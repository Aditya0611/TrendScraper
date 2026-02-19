#!/usr/bin/env python3
"""
Advanced Proxy Pool Abstraction
================================

A comprehensive proxy pool implementation with:
- Multiple rotation strategies (round-robin, weighted, random, least-used)
- Health scoring system (based on success rate, response time, uptime)
- Exponential backoff with jitter for retries
- Circuit breaker pattern to prevent using failing proxies
- Thread-safe operations
- Automatic health checks
- Proxy recovery mechanisms

Usage:
------
    from proxy_pool import ProxyPool, RotationStrategy
    
    pool = ProxyPool(
        proxies=['http://proxy1:8080', 'http://proxy2:8080'],
        rotation_strategy=RotationStrategy.WEIGHTED
    )
    
    # Get next proxy with automatic retry/backoff
    proxy = pool.get_proxy()
    
    try:
        # Use proxy for request
        result = make_request(proxy)
        pool.mark_success(proxy, response_time=0.5)
    except Exception as e:
        pool.mark_failure(proxy, error=str(e))
"""

import os
import time
import random
import math
import threading
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from threading import Lock, RLock
from datetime import datetime, timedelta


class RotationStrategy(Enum):
    """Proxy rotation strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    RANDOM = "random"
    LEAST_USED = "least_used"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class ProxyMetrics:
    """Metrics for a single proxy"""
    # Request counts
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Response times (in seconds)
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # Timing
    first_used: Optional[float] = None
    last_used: Optional[float] = None
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    
    # Failure tracking
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    # Circuit breaker
    circuit_state: CircuitState = CircuitState.CLOSED
    circuit_opened_at: Optional[float] = None
    
    # Usage tracking
    times_used: int = 0
    
    def get_success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)"""
        if self.total_requests == 0:
            return 1.0
        return self.success_count / self.total_requests
    
    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if self.success_count == 0:
            return 0.0
        return self.total_response_time / self.success_count
    
    def get_health_score(self) -> float:
        """Calculate health score (0.0 to 1.0)"""
        if self.total_requests == 0:
            return 1.0  # Unused proxy gets perfect score
        
        success_rate = self.get_success_rate()
        
        # Response time score (faster = better, normalized)
        avg_time = self.get_avg_response_time()
        time_score = 1.0 / (1.0 + avg_time)  # Max score = 1.0 for 0s, decays
        
        # Recency score (recent success = better)
        recency_score = 1.0
        if self.last_success:
            hours_since_success = (time.time() - self.last_success) / 3600
            recency_score = 1.0 / (1.0 + hours_since_success)
        
        # Consistency score (based on consecutive successes)
        consistency_score = min(self.consecutive_successes / 10.0, 1.0)
        
        # Combined score with weights
        health_score = (
            0.50 * success_rate +        # 50% weight on success rate
            0.25 * time_score +          # 25% weight on response time
            0.15 * recency_score +       # 15% weight on recency
            0.10 * consistency_score     # 10% weight on consistency
        )
        
        return max(0.0, min(1.0, health_score))


@dataclass
class RetryConfig:
    """Configuration for retry/backoff mechanism"""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0     # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: Tuple[float, float] = (0.1, 0.5)  # (min, max) multiplier


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Open circuit after N consecutive failures
    success_threshold: int = 2  # Close circuit after N consecutive successes
    timeout: float = 60.0  # Seconds to wait before attempting half-open
    half_open_max_attempts: int = 3  # Max attempts in half-open state


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    enabled: bool = True
    interval: float = 300.0  # Seconds between health checks
    timeout: float = 5.0     # Timeout for health check request
    url: str = "http://httpbin.org/ip"  # URL to test proxy


class ProxyPool:
    """
    Advanced proxy pool with rotation, health scoring, retry/backoff, and circuit breaker.
    
    Features:
    - Multiple rotation strategies
    - Health scoring based on success rate, response time, recency
    - Exponential backoff with jitter for retries
    - Circuit breaker to prevent using failing proxies
    - Thread-safe operations
    - Automatic health checks
    """
    
    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        rotation_strategy: RotationStrategy = RotationStrategy.WEIGHTED,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        health_check_config: Optional[HealthCheckConfig] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize proxy pool.
        
        Args:
            proxies: List of proxy URLs (e.g., ['http://proxy1:8080', 'http://proxy2:8080'])
            rotation_strategy: Strategy for selecting next proxy
            retry_config: Configuration for retry/backoff mechanism
            circuit_config: Configuration for circuit breaker
            health_check_config: Configuration for automatic health checks
            logger: Optional logger instance
        """
        self.proxies = proxies or []
        self.rotation_strategy = rotation_strategy
        self.retry_config = retry_config or RetryConfig()
        self.circuit_config = circuit_config or CircuitBreakerConfig()
        self.health_check_config = health_check_config or HealthCheckConfig()
        self.logger = logger
        
        # Thread safety
        self._lock = RLock()
        
        # Proxy metrics storage
        self._metrics: Dict[str, ProxyMetrics] = {}
        for proxy in self.proxies:
            self._metrics[proxy] = ProxyMetrics()
        
        # Rotation state
        self._current_index = 0
        
        # Health check thread
        self._health_check_thread: Optional[threading.Thread] = None
        self._health_check_stop_event = threading.Event()
        
        # Start health checks if enabled
        if self.health_check_config.enabled and self.proxies:
            self._start_health_checks()
    
    def _start_health_checks(self):
        """Start background thread for periodic health checks"""
        def health_check_worker():
            while not self._health_check_stop_event.is_set():
                try:
                    self._perform_health_checks()
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Health check error: {e}")
                
                # Wait for interval or stop event
                if self._health_check_stop_event.wait(self.health_check_config.interval):
                    break
        
        self._health_check_thread = threading.Thread(
            target=health_check_worker,
            daemon=True,
            name="ProxyPoolHealthCheck"
        )
        self._health_check_thread.start()
    
    def _perform_health_checks(self):
        """Perform health checks on all proxies"""
        try:
            import requests
        except ImportError:
            if self.logger:
                self.logger.warning("requests library not available, skipping health checks")
            return
        
        for proxy in self.proxies:
            metrics = self._metrics[proxy]
            
            # Skip if circuit is open (wait for timeout)
            if metrics.circuit_state == CircuitState.OPEN:
                if metrics.circuit_opened_at:
                    elapsed = time.time() - metrics.circuit_opened_at
                    if elapsed >= self.circuit_config.timeout:
                        # Move to half-open
                        metrics.circuit_state = CircuitState.HALF_OPEN
                        if self.logger:
                            self.logger.info(f"Proxy {proxy} moved to HALF_OPEN state")
                continue
            
            # Perform health check
            try:
                start_time = time.time()
                proxies = {'http': proxy, 'https': proxy}
                response = requests.get(
                    self.health_check_config.url,
                    proxies=proxies,
                    timeout=self.health_check_config.timeout
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.mark_success(proxy, response_time=response_time)
                    if self.logger:
                        self.logger.debug(f"Health check passed for {proxy}")
                else:
                    self.mark_failure(proxy, error=f"HTTP {response.status_code}")
            except ImportError:
                # requests not available
                if self.logger:
                    self.logger.warning("requests library not available for health checks")
                break
            except Exception as e:
                self.mark_failure(proxy, error=str(e))
                if self.logger:
                    self.logger.debug(f"Health check failed for {proxy}: {e}")
    
    def get_proxy(self, exclude: Optional[List[str]] = None) -> Optional[str]:
        """
        Get next available proxy based on rotation strategy.
        
        Args:
            exclude: List of proxy URLs to exclude from selection
        
        Returns:
            Proxy URL or None if no healthy proxy available
        """
        exclude = exclude or []
        
        with self._lock:
            # Filter available proxies
            available = [
                p for p in self.proxies
                if p not in exclude
                and self._is_proxy_available(p)
            ]
            
            if not available:
                # Try all proxies if none available
                available = [p for p in self.proxies if p not in exclude]
            
            if not available:
                return None
            
            # Select proxy based on strategy
            if self.rotation_strategy == RotationStrategy.ROUND_ROBIN:
                proxy = self._round_robin_select(available)
            elif self.rotation_strategy == RotationStrategy.WEIGHTED:
                proxy = self._weighted_select(available)
            elif self.rotation_strategy == RotationStrategy.RANDOM:
                proxy = self._random_select(available)
            elif self.rotation_strategy == RotationStrategy.LEAST_USED:
                proxy = self._least_used_select(available)
            else:
                proxy = available[0]
            
            # Update usage tracking
            metrics = self._metrics[proxy]
            metrics.times_used += 1
            metrics.last_used = time.time()
            if metrics.first_used is None:
                metrics.first_used = time.time()
            
            return proxy
    
    def _is_proxy_available(self, proxy: str) -> bool:
        """Check if proxy is available (circuit not open)"""
        metrics = self._metrics.get(proxy)
        if not metrics:
            return True
        
        # Circuit breaker check
        if metrics.circuit_state == CircuitState.OPEN:
            # Check if timeout has passed
            if metrics.circuit_opened_at:
                elapsed = time.time() - metrics.circuit_opened_at
                if elapsed >= self.circuit_config.timeout:
                    # Move to half-open
                    metrics.circuit_state = CircuitState.HALF_OPEN
                    metrics.circuit_opened_at = None
                    return True
            return False
        
        return True
    
    def _round_robin_select(self, available: List[str]) -> str:
        """Round-robin selection"""
        # Find current proxy in available list
        if self._current_index >= len(available):
            self._current_index = 0
        
        proxy = available[self._current_index]
        self._current_index = (self._current_index + 1) % len(available)
        return proxy
    
    def _weighted_select(self, available: List[str]) -> str:
        """Weighted selection based on health scores"""
        if not available:
            return None
        
        # Calculate weights (health scores)
        weights = []
        for proxy in available:
            metrics = self._metrics.get(proxy, ProxyMetrics())
            score = metrics.get_health_score()
            weights.append(max(0.01, score))  # Minimum weight to avoid zero
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(available)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return available[i]
        
        return available[-1]
    
    def _random_select(self, available: List[str]) -> str:
        """Random selection"""
        return random.choice(available)
    
    def _least_used_select(self, available: List[str]) -> str:
        """Select least used proxy"""
        if not available:
            return None
        
        least_used = min(
            available,
            key=lambda p: self._metrics.get(p, ProxyMetrics()).times_used
        )
        return least_used
    
    def mark_success(self, proxy: str, response_time: Optional[float] = None):
        """
        Mark proxy request as successful.
        
        Args:
            proxy: Proxy URL
            response_time: Response time in seconds
        """
        with self._lock:
            if proxy not in self._metrics:
                self._metrics[proxy] = ProxyMetrics()
            
            metrics = self._metrics[proxy]
            metrics.total_requests += 1
            metrics.success_count += 1
            metrics.last_success = time.time()
            metrics.consecutive_successes += 1
            metrics.consecutive_failures = 0
            
            if response_time is not None:
                metrics.total_response_time += response_time
                metrics.min_response_time = min(metrics.min_response_time, response_time)
                metrics.max_response_time = max(metrics.max_response_time, response_time)
            
            # Circuit breaker: Close circuit if in half-open state
            if metrics.circuit_state == CircuitState.HALF_OPEN:
                if metrics.consecutive_successes >= self.circuit_config.success_threshold:
                    metrics.circuit_state = CircuitState.CLOSED
                    if self.logger:
                        self.logger.info(f"Proxy {proxy} circuit CLOSED after recovery")
    
    def mark_failure(self, proxy: str, error: Optional[str] = None):
        """
        Mark proxy request as failed.
        
        Args:
            proxy: Proxy URL
            error: Error message (optional)
        """
        with self._lock:
            if proxy not in self._metrics:
                self._metrics[proxy] = ProxyMetrics()
            
            metrics = self._metrics[proxy]
            metrics.total_requests += 1
            metrics.failure_count += 1
            metrics.last_failure = time.time()
            metrics.consecutive_failures += 1
            metrics.consecutive_successes = 0
            
            # Circuit breaker: Open circuit if threshold reached
            if metrics.circuit_state == CircuitState.CLOSED:
                if metrics.consecutive_failures >= self.circuit_config.failure_threshold:
                    metrics.circuit_state = CircuitState.OPEN
                    metrics.circuit_opened_at = time.time()
                    if self.logger:
                        self.logger.warning(
                            f"Proxy {proxy} circuit OPENED after {metrics.consecutive_failures} failures"
                        )
            elif metrics.circuit_state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                metrics.circuit_state = CircuitState.OPEN
                metrics.circuit_opened_at = time.time()
                if self.logger:
                    self.logger.warning(f"Proxy {proxy} circuit OPENED from HALF_OPEN state")
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        proxy: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with automatic proxy retry/backoff.
        
        Args:
            func: Function to execute (should accept proxy as keyword argument)
            *args: Positional arguments for func
            proxy: Optional proxy to use (if None, will select from pool)
            **kwargs: Keyword arguments for func
        
        Returns:
            Result from func
        
        Raises:
            Exception: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Get proxy if not provided
                if proxy is None:
                    proxy = self.get_proxy()
                    if proxy is None:
                        raise RuntimeError("No available proxies in pool")
                
                # Execute function with proxy
                if 'proxy' in kwargs:
                    kwargs['proxy'] = proxy
                else:
                    kwargs.setdefault('proxy', proxy)
                
                start_time = time.time()
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Mark success
                self.mark_success(proxy, response_time=response_time)
                return result
                
            except Exception as e:
                last_exception = e
                
                # Mark failure
                if proxy:
                    self.mark_failure(proxy, error=str(e))
                
                # Don't retry on last attempt
                if attempt < self.retry_config.max_retries:
                    # Calculate backoff delay
                    delay = self._calculate_backoff_delay(attempt)
                    
                    if self.logger:
                        self.logger.debug(
                            f"Retry attempt {attempt + 1}/{self.retry_config.max_retries} "
                            f"after {delay:.2f}s (proxy: {proxy}, error: {str(e)[:50]})"
                        )
                    
                    time.sleep(delay)
                    
                    # Get new proxy for next attempt (exclude failed one)
                    if proxy:
                        proxy = self.get_proxy(exclude=[proxy])
                    else:
                        proxy = self.get_proxy()
                else:
                    if self.logger:
                        self.logger.error(
                            f"All retries exhausted for proxy {proxy}: {str(e)}"
                        )
        
        # All retries failed
        raise last_exception or RuntimeError("All retries exhausted")
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""
        delay = min(
            self.retry_config.initial_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            jitter_factor = random.uniform(*self.retry_config.jitter_range)
            delay *= (1.0 + jitter_factor)
        
        return delay
    
    def get_proxy_dict(self, proxy: str) -> Dict[str, str]:
        """
        Convert proxy URL to dictionary format for requests/playwright.
        
        Args:
            proxy: Proxy URL
        
        Returns:
            Dictionary with proxy configuration
        """
        if not proxy:
            return {}
        
        return {'server': proxy}
    
    def get_metrics(self, proxy: Optional[str] = None) -> Dict:
        """
        Get metrics for proxy or all proxies.
        
        Args:
            proxy: Optional proxy URL (if None, returns all)
        
        Returns:
            Dictionary with metrics
        """
        with self._lock:
            if proxy:
                metrics = self._metrics.get(proxy)
                if not metrics:
                    return {}
                
                return {
                    'proxy': proxy,
                    'success_rate': metrics.get_success_rate(),
                    'health_score': metrics.get_health_score(),
                    'avg_response_time': metrics.get_avg_response_time(),
                    'min_response_time': metrics.min_response_time if metrics.min_response_time != float('inf') else 0.0,
                    'max_response_time': metrics.max_response_time,
                    'total_requests': metrics.total_requests,
                    'success_count': metrics.success_count,
                    'failure_count': metrics.failure_count,
                    'consecutive_failures': metrics.consecutive_failures,
                    'consecutive_successes': metrics.consecutive_successes,
                    'circuit_state': metrics.circuit_state.value,
                    'times_used': metrics.times_used,
                    'last_used': datetime.fromtimestamp(metrics.last_used).isoformat() if metrics.last_used else None,
                    'last_success': datetime.fromtimestamp(metrics.last_success).isoformat() if metrics.last_success else None,
                    'last_failure': datetime.fromtimestamp(metrics.last_failure).isoformat() if metrics.last_failure else None,
                }
            else:
                # All proxies summary
                total_proxies = len(self.proxies)
                available_count = sum(1 for p in self.proxies if self._is_proxy_available(p))
                
                return {
                    'total_proxies': total_proxies,
                    'available_proxies': available_count,
                    'rotation_strategy': self.rotation_strategy.value,
                    'proxies': {
                        p: self.get_metrics(p)
                        for p in self.proxies
                    }
                }
    
    def reset_proxy(self, proxy: str):
        """Reset metrics and circuit breaker for a proxy"""
        with self._lock:
            if proxy in self._metrics:
                self._metrics[proxy] = ProxyMetrics()
                if self.logger:
                    self.logger.info(f"Reset metrics for proxy {proxy}")
    
    def add_proxy(self, proxy: str):
        """Add a new proxy to the pool"""
        with self._lock:
            if proxy not in self.proxies:
                self.proxies.append(proxy)
                self._metrics[proxy] = ProxyMetrics()
                if self.logger:
                    self.logger.info(f"Added proxy {proxy} to pool")
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool"""
        with self._lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                self._metrics.pop(proxy, None)
                if self.logger:
                    self.logger.info(f"Removed proxy {proxy} from pool")
    
    def cleanup(self):
        """Cleanup resources (stop health check thread)"""
        if self._health_check_stop_event:
            self._health_check_stop_event.set()
        
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5.0)
    
    @staticmethod
    def from_env(
        env_var: str = "PROXIES",
        **kwargs
    ) -> 'ProxyPool':
        """
        Create ProxyPool from environment variable.
        
        Args:
            env_var: Environment variable name
            **kwargs: Additional arguments for ProxyPool constructor
        
        Returns:
            ProxyPool instance
        """
        proxy_string = os.getenv(env_var, '')
        proxy_list = [p.strip() for p in proxy_string.split(',') if p.strip()]
        return ProxyPool(proxies=proxy_list, **kwargs)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Example usage and testing
if __name__ == "__main__":
    # Example: Create proxy pool
    pool = ProxyPool(
        proxies=[
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ],
        rotation_strategy=RotationStrategy.WEIGHTED,
        retry_config=RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=60.0
        ),
        circuit_config=CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=60.0
        )
    )
    
    # Get next proxy
    proxy = pool.get_proxy()
    print(f"Selected proxy: {proxy}")
    
    # Get metrics
    metrics = pool.get_metrics()
    print(f"\nPool metrics:\n{metrics}")
    
    # Cleanup
    pool.cleanup()

