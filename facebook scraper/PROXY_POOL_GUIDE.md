# Advanced Proxy Pool Guide

## Overview

The `proxy_pool.py` module provides a comprehensive proxy pool abstraction with:

- ✅ **Multiple Rotation Strategies** - Round-robin, weighted, random, least-used
- ✅ **Health Scoring System** - Based on success rate, response time, recency, consistency
- ✅ **Exponential Backoff with Jitter** - Automatic retry mechanism
- ✅ **Circuit Breaker Pattern** - Prevents using failing proxies
- ✅ **Thread-Safe Operations** - Safe for concurrent use
- ✅ **Automatic Health Checks** - Background monitoring
- ✅ **Proxy Recovery** - Automatic reactivation of recovered proxies

## Features

### 1. Rotation Strategies

The proxy pool supports multiple rotation strategies:

- **WEIGHTED** (default): Selects proxy based on health score (recommended)
- **ROUND_ROBIN**: Cycles through proxies sequentially
- **RANDOM**: Randomly selects from available proxies
- **LEAST_USED**: Prefers proxies with fewer uses

### 2. Health Scoring

Each proxy is assigned a health score (0.0 to 1.0) based on:

- **50%** Success rate (successful requests / total requests)
- **25%** Response time (faster = better)
- **15%** Recency (recent success = better)
- **10%** Consistency (consecutive successes)

### 3. Retry/Backoff

Automatic retry mechanism with exponential backoff:

- Configurable max retries
- Exponential delay increase
- Jitter to prevent thundering herd
- Automatic proxy rotation on failure

### 4. Circuit Breaker

Prevents using failing proxies:

- **CLOSED**: Normal operation
- **OPEN**: Too many failures, reject requests
- **HALF_OPEN**: Testing if proxy recovered

Transitions:
- CLOSED → OPEN: After N consecutive failures
- OPEN → HALF_OPEN: After timeout period
- HALF_OPEN → CLOSED: After N consecutive successes
- HALF_OPEN → OPEN: On any failure

## Basic Usage

### Simple Example

```python
from proxy_pool import ProxyPool, RotationStrategy

# Create proxy pool
pool = ProxyPool(
    proxies=[
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080'
    ],
    rotation_strategy=RotationStrategy.WEIGHTED
)

# Get next proxy
proxy = pool.get_proxy()
print(f"Using proxy: {proxy}")

# Use proxy for request
try:
    # Make your request with proxy
    result = make_request(proxy)
    pool.mark_success(proxy, response_time=0.5)
except Exception as e:
    pool.mark_failure(proxy, error=str(e))
```

### From Environment Variable

```python
from proxy_pool import ProxyPool

# Load from PROXIES environment variable
# Format: PROXIES=http://proxy1:8080,http://proxy2:8080
pool = ProxyPool.from_env()

proxy = pool.get_proxy()
```

### With Automatic Retry/Backoff

```python
from proxy_pool import ProxyPool, RetryConfig

pool = ProxyPool(
    proxies=['http://proxy1:8080', 'http://proxy2:8080'],
    retry_config=RetryConfig(
        max_retries=3,
        initial_delay=1.0,
        max_delay=60.0
    )
)

def make_request(proxy):
    # Your request logic here
    import requests
    proxies = {'http': proxy, 'https': proxy}
    response = requests.get('https://example.com', proxies=proxies)
    return response

# Execute with automatic retry
try:
    result = pool.execute_with_retry(make_request)
    print("Success!")
except Exception as e:
    print(f"All retries failed: {e}")
```

## Advanced Configuration

### Custom Retry Configuration

```python
from proxy_pool import ProxyPool, RetryConfig

retry_config = RetryConfig(
    max_retries=5,              # Maximum retry attempts
    initial_delay=2.0,          # Initial delay in seconds
    max_delay=120.0,            # Maximum delay cap
    exponential_base=2.0,       # Exponential multiplier
    jitter=True,                # Enable random jitter
    jitter_range=(0.1, 0.5)    # Jitter multiplier range
)

pool = ProxyPool(proxies=[...], retry_config=retry_config)
```

### Custom Circuit Breaker Configuration

```python
from proxy_pool import ProxyPool, CircuitBreakerConfig

circuit_config = CircuitBreakerConfig(
    failure_threshold=5,        # Open circuit after N failures
    success_threshold=2,        # Close circuit after N successes
    timeout=60.0,              # Wait time before half-open
    half_open_max_attempts=3   # Max attempts in half-open
)

pool = ProxyPool(proxies=[...], circuit_config=circuit_config)
```

### Custom Health Check Configuration

```python
from proxy_pool import ProxyPool, HealthCheckConfig

health_config = HealthCheckConfig(
    enabled=True,               # Enable automatic health checks
    interval=300.0,            # Check every 5 minutes
    timeout=5.0,               # Request timeout
    url="http://httpbin.org/ip"  # Test URL
)

pool = ProxyPool(proxies=[...], health_check_config=health_config)
```

## Monitoring and Metrics

### Get Proxy Metrics

```python
# Get metrics for all proxies
all_metrics = pool.get_metrics()
print(f"Total proxies: {all_metrics['total_proxies']}")
print(f"Available proxies: {all_metrics['available_proxies']}")

# Get metrics for specific proxy
proxy_metrics = pool.get_metrics(proxy='http://proxy1:8080')
print(f"Success rate: {proxy_metrics['success_rate']:.2%}")
print(f"Health score: {proxy_metrics['health_score']:.2%}")
print(f"Avg response time: {proxy_metrics['avg_response_time']:.2f}s")
print(f"Circuit state: {proxy_metrics['circuit_state']}")
```

### Example Metrics Output

```python
{
    'proxy': 'http://proxy1:8080',
    'success_rate': 0.95,
    'health_score': 0.92,
    'avg_response_time': 0.45,
    'min_response_time': 0.12,
    'max_response_time': 2.34,
    'total_requests': 100,
    'success_count': 95,
    'failure_count': 5,
    'consecutive_failures': 0,
    'consecutive_successes': 15,
    'circuit_state': 'closed',
    'times_used': 150,
    'last_used': '2025-01-15T10:30:00',
    'last_success': '2025-01-15T10:30:00',
    'last_failure': '2025-01-15T09:15:00'
}
```

## Integration Examples

### Integration with Playwright

```python
from proxy_pool import ProxyPool
from playwright.sync_api import sync_playwright

pool = ProxyPool.from_env()

with sync_playwright() as p:
    proxy = pool.get_proxy()
    
    if proxy:
        browser = p.chromium.launch()
        context = browser.new_context(
            proxy={'server': proxy}
        )
        page = context.new_page()
        
        try:
            page.goto('https://example.com')
            pool.mark_success(proxy, response_time=2.5)
        except Exception as e:
            pool.mark_failure(proxy, error=str(e))
        finally:
            context.close()
            browser.close()
```

### Integration with Requests

```python
from proxy_pool import ProxyPool
import requests

pool = ProxyPool.from_env()

def make_request(url):
    proxy = pool.get_proxy()
    if not proxy:
        raise RuntimeError("No available proxies")
    
    proxies = {'http': proxy, 'https': proxy}
    
    start_time = time.time()
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            pool.mark_success(proxy, response_time=response_time)
            return response
        else:
            pool.mark_failure(proxy, error=f"HTTP {response.status_code}")
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        pool.mark_failure(proxy, error=str(e))
        raise

# Use with retry
try:
    response = pool.execute_with_retry(
        make_request,
        url='https://example.com'
    )
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Integration with Existing Scrapers

The proxy pool can be used as a drop-in replacement for existing proxy managers:

```python
from proxy_pool import ProxyPool
from base import BaseScraper

# Create advanced proxy pool
pool = ProxyPool.from_env(
    rotation_strategy=RotationStrategy.WEIGHTED
)

# Create adapter wrapper to match existing interface
class ProxyPoolAdapter:
    def __init__(self, pool):
        self.pool = pool
    
    @property
    def proxies(self):
        return self.pool.proxies
    
    def get_next_proxy(self):
        proxy = self.pool.get_proxy()
        if proxy:
            return {'server': proxy}
        return None
    
    def mark_failed(self, proxy_url):
        # Extract URL from dict if needed
        if isinstance(proxy_url, dict):
            proxy_url = proxy_url.get('server', '')
        self.pool.mark_failure(proxy_url)

# Use with existing scraper
adapter = ProxyPoolAdapter(pool)
scraper = BaseScraper(proxy_manager=adapter)
```

## Best Practices

### 1. Choose Appropriate Rotation Strategy

- **WEIGHTED**: Best for production (recommended)
- **ROUND_ROBIN**: Good for uniform load distribution
- **RANDOM**: Good for testing or avoiding patterns
- **LEAST_USED**: Good for equalizing proxy usage

### 2. Configure Circuit Breaker Appropriately

- Lower `failure_threshold` (3-5) for strict quality control
- Higher `failure_threshold` (10+) for more tolerance
- Adjust `timeout` based on expected recovery time

### 3. Monitor Health Metrics

- Regularly check `get_metrics()` output
- Remove consistently failing proxies
- Add new proxies dynamically as needed

### 4. Handle Proxy Failures Gracefully

```python
proxy = pool.get_proxy()
if not proxy:
    # Handle no proxies available
    raise RuntimeError("No proxies available")

try:
    # Use proxy
    result = make_request(proxy)
    pool.mark_success(proxy, response_time=0.5)
except Exception as e:
    # Mark failure (circuit breaker will handle it)
    pool.mark_failure(proxy, error=str(e))
    
    # Optionally try another proxy
    proxy = pool.get_proxy(exclude=[proxy])
    if proxy:
        # Retry with new proxy
        result = make_request(proxy)
```

### 5. Use Context Manager for Cleanup

```python
with ProxyPool.from_env() as pool:
    proxy = pool.get_proxy()
    # Use proxy...
    # Cleanup automatically called on exit
```

## Troubleshooting

### No Proxies Available

**Problem**: `get_proxy()` returns `None`

**Solutions**:
- Check if proxies are configured: `pool.proxies`
- Check circuit breaker state: `pool.get_metrics()`
- Reset failed proxies: `pool.reset_proxy(proxy)`
- Verify proxy URLs are correct

### Circuit Breaker Always Open

**Problem**: Proxies stay in OPEN state

**Solutions**:
- Increase `failure_threshold` in circuit config
- Decrease `timeout` to retry sooner
- Check if proxies are actually working
- Reset circuit: `pool.reset_proxy(proxy)`

### Health Checks Not Working

**Problem**: Health checks don't run

**Solutions**:
- Verify `health_check_config.enabled = True`
- Check if health check thread is running
- Verify test URL is accessible
- Check logs for health check errors

## API Reference

### ProxyPool Class

```python
class ProxyPool:
    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        rotation_strategy: RotationStrategy = RotationStrategy.WEIGHTED,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        health_check_config: Optional[HealthCheckConfig] = None,
        logger: Optional[Any] = None
    )
    
    def get_proxy(self, exclude: Optional[List[str]] = None) -> Optional[str]
    def mark_success(self, proxy: str, response_time: Optional[float] = None)
    def mark_failure(self, proxy: str, error: Optional[str] = None)
    def execute_with_retry(self, func: Callable, *args, proxy: Optional[str] = None, **kwargs) -> Any
    def get_proxy_dict(self, proxy: str) -> Dict[str, str]
    def get_metrics(self, proxy: Optional[str] = None) -> Dict
    def reset_proxy(self, proxy: str)
    def add_proxy(self, proxy: str)
    def remove_proxy(self, proxy: str)
    def cleanup(self)
    
    @staticmethod
    def from_env(env_var: str = "PROXIES", **kwargs) -> 'ProxyPool'
```

### Enums

```python
class RotationStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    RANDOM = "random"
    LEAST_USED = "least_used"

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
```

### Configuration Classes

```python
@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_range: Tuple[float, float] = (0.1, 0.5)

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    half_open_max_attempts: int = 3

@dataclass
class HealthCheckConfig:
    enabled: bool = True
    interval: float = 300.0
    timeout: float = 5.0
    url: str = "http://httpbin.org/ip"
```

## Example: Complete Integration

```python
#!/usr/bin/env python3
"""Example: Using ProxyPool with requests"""

from proxy_pool import ProxyPool, RotationStrategy, RetryConfig, CircuitBreakerConfig
import requests
import time

def main():
    # Initialize proxy pool
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
    
    def make_request(url, proxy=None):
        """Make HTTP request with proxy"""
        proxies = {}
        if proxy:
            proxies = {'http': proxy, 'https': proxy}
        
        response = requests.get(url, proxies=proxies, timeout=10)
        return response
    
    # Make requests with automatic retry
    urls = [
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/get'
    ]
    
    for url in urls:
        try:
            print(f"\nRequesting: {url}")
            response = pool.execute_with_retry(make_request, url=url)
            print(f"Success: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Failed: {e}")
    
    # Show metrics
    print("\n=== Proxy Metrics ===")
    metrics = pool.get_metrics()
    for proxy_url, proxy_metrics in metrics['proxies'].items():
        print(f"\nProxy: {proxy_url}")
        print(f"  Success Rate: {proxy_metrics['success_rate']:.2%}")
        print(f"  Health Score: {proxy_metrics['health_score']:.2%}")
        print(f"  Circuit State: {proxy_metrics['circuit_state']}")
    
    # Cleanup
    pool.cleanup()

if __name__ == "__main__":
    main()
```

## Summary

The `proxy_pool.py` module provides a production-ready proxy pool implementation with:

1. **Smart Rotation**: Choose from multiple strategies
2. **Health Monitoring**: Automatic scoring and tracking
3. **Resilience**: Retry/backoff and circuit breaker patterns
4. **Thread-Safe**: Safe for concurrent operations
5. **Automatic Recovery**: Health checks and circuit breaker recovery

Use it as a standalone module or integrate with existing scrapers through an adapter pattern.

