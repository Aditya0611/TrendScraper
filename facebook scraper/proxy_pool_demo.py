#!/usr/bin/env python3
"""
Proxy Pool Demo
===============

Demonstrates the advanced proxy pool features:
- Rotation strategies
- Health scoring
- Retry/backoff
- Circuit breaker
- Metrics and monitoring
"""

import time
import random
from proxy_pool import (
    ProxyPool,
    RotationStrategy,
    RetryConfig,
    CircuitBreakerConfig,
    HealthCheckConfig
)


def demo_basic_usage():
    """Demonstrate basic proxy pool usage"""
    print("=" * 60)
    print("DEMO 1: Basic Proxy Pool Usage")
    print("=" * 60)
    
    # Create proxy pool with sample proxies
    pool = ProxyPool(
        proxies=[
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ],
        rotation_strategy=RotationStrategy.ROUND_ROBIN
    )
    
    # Get proxies
    print("\nGetting proxies (round-robin):")
    for i in range(5):
        proxy = pool.get_proxy()
        print(f"  Request {i+1}: {proxy}")
    
    pool.cleanup()
    print()


def demo_rotation_strategies():
    """Demonstrate different rotation strategies"""
    print("=" * 60)
    print("DEMO 2: Rotation Strategies")
    print("=" * 60)
    
    proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080'
    ]
    
    strategies = [
        RotationStrategy.ROUND_ROBIN,
        RotationStrategy.WEIGHTED,
        RotationStrategy.RANDOM,
        RotationStrategy.LEAST_USED
    ]
    
    for strategy in strategies:
        print(f"\n{strategy.value.upper()} strategy:")
        pool = ProxyPool(proxies=proxies.copy(), rotation_strategy=strategy)
        
        selected = []
        for i in range(6):
            proxy = pool.get_proxy()
            selected.append(proxy.split('/')[-1].split(':')[0])  # Extract name
        
        print(f"  Selected: {' -> '.join(selected)}")
        pool.cleanup()


def demo_health_scoring():
    """Demonstrate health scoring system"""
    print("=" * 60)
    print("DEMO 3: Health Scoring")
    print("=" * 60)
    
    pool = ProxyPool(
        proxies=[
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ],
        rotation_strategy=RotationStrategy.WEIGHTED
    )
    
    # Simulate different proxy performances
    print("\nSimulating proxy performance...")
    
    # Proxy 1: Good performance
    proxy1 = pool.proxies[0]
    for i in range(10):
        pool.mark_success(proxy1, response_time=0.3 + random.uniform(0, 0.2))
    
    # Proxy 2: Mixed performance
    proxy2 = pool.proxies[1]
    for i in range(8):
        if i % 3 == 0:
            pool.mark_failure(proxy2, error="timeout")
        else:
            pool.mark_success(proxy2, response_time=0.5 + random.uniform(0, 0.3))
    
    # Proxy 3: Poor performance
    proxy3 = pool.proxies[2]
    for i in range(10):
        if i < 3:
            pool.mark_success(proxy3, response_time=1.0 + random.uniform(0, 0.5))
        else:
            pool.mark_failure(proxy3, error="connection failed")
    
    # Show metrics
    print("\nProxy Metrics:")
    print("-" * 60)
    for proxy in pool.proxies:
        metrics = pool.get_metrics(proxy)
        print(f"\n{proxy}:")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Health Score: {metrics['health_score']:.2%}")
        print(f"  Avg Response Time: {metrics['avg_response_time']:.2f}s")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Circuit State: {metrics['circuit_state']}")
    
    # Weighted selection should prefer proxy1 (best health)
    print("\nNext proxy (weighted selection - should prefer healthy):")
    next_proxy = pool.get_proxy()
    print(f"  Selected: {next_proxy}")
    
    pool.cleanup()
    print()


def demo_retry_backoff():
    """Demonstrate retry/backoff mechanism"""
    print("=" * 60)
    print("DEMO 4: Retry with Exponential Backoff")
    print("=" * 60)
    
    pool = ProxyPool(
        proxies=['http://proxy1.example.com:8080'],
        retry_config=RetryConfig(
            max_retries=3,
            initial_delay=0.5,  # Short delay for demo
            max_delay=5.0,
            exponential_base=2.0,
            jitter=True
        )
    )
    
    attempt_count = [0]
    
    def failing_request(proxy=None):
        """Request that fails first 2 times, succeeds on 3rd"""
        attempt_count[0] += 1
        attempt = attempt_count[0]
        
        print(f"  Attempt {attempt}: ", end="")
        if attempt < 3:
            print("FAILED")
            raise Exception(f"Simulated failure on attempt {attempt}")
        else:
            print("SUCCESS")
            return f"Success on attempt {attempt}"
    
    print("\nExecuting request with automatic retry:")
    print("(Will fail 2 times, succeed on 3rd attempt)")
    
    start_time = time.time()
    try:
        result = pool.execute_with_retry(failing_request)
        elapsed = time.time() - start_time
        print(f"\n  Result: {result}")
        print(f"  Total time: {elapsed:.2f}s (includes backoff delays)")
    except Exception as e:
        print(f"\n  All retries exhausted: {e}")
    
    pool.cleanup()
    print()


def demo_circuit_breaker():
    """Demonstrate circuit breaker pattern"""
    print("=" * 60)
    print("DEMO 5: Circuit Breaker Pattern")
    print("=" * 60)
    
    pool = ProxyPool(
        proxies=['http://proxy1.example.com:8080'],
        circuit_config=CircuitBreakerConfig(
            failure_threshold=3,  # Open after 3 failures
            success_threshold=2,   # Close after 2 successes
            timeout=5.0           # Short timeout for demo
        )
    )
    
    proxy = pool.proxies[0]
    
    print("\nSimulating failures (circuit should open after 3):")
    for i in range(5):
        pool.mark_failure(proxy, error=f"Failure {i+1}")
        metrics = pool.get_metrics(proxy)
        print(f"  Failure {i+1}: Circuit state = {metrics['circuit_state']}")
        print(f"    Consecutive failures: {metrics['consecutive_failures']}")
    
    print("\n  Trying to get proxy (should be blocked by circuit breaker):")
    available = pool.get_proxy()
    if available is None:
        print("    ✓ Proxy unavailable (circuit is OPEN)")
    else:
        print(f"    ✗ Got proxy: {available}")
    
    print("\n  Waiting for timeout (5 seconds)...")
    time.sleep(5.1)
    
    print("  Circuit should move to HALF_OPEN state")
    metrics = pool.get_metrics(proxy)
    print(f"    Circuit state: {metrics['circuit_state']}")
    
    print("\n  Testing recovery (2 successes should close circuit):")
    for i in range(2):
        pool.mark_success(proxy, response_time=0.5)
        metrics = pool.get_metrics(proxy)
        print(f"    Success {i+1}: Circuit state = {metrics['circuit_state']}")
    
    print("\n  Trying to get proxy again (should work now):")
    available = pool.get_proxy()
    if available:
        print(f"    ✓ Proxy available: {available}")
    
    pool.cleanup()
    print()


def demo_metrics():
    """Demonstrate comprehensive metrics"""
    print("=" * 60)
    print("DEMO 6: Comprehensive Metrics")
    print("=" * 60)
    
    pool = ProxyPool(
        proxies=[
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ]
    )
    
    # Simulate various scenarios
    proxy1, proxy2, proxy3 = pool.proxies
    
    # Proxy 1: Excellent
    for _ in range(20):
        pool.mark_success(proxy1, response_time=0.2 + random.uniform(0, 0.1))
    
    # Proxy 2: Good but slow
    for _ in range(15):
        pool.mark_success(proxy2, response_time=1.0 + random.uniform(0, 0.5))
        if random.random() < 0.1:  # 10% failure rate
            pool.mark_failure(proxy2, error="timeout")
    
    # Proxy 3: Poor
    for _ in range(10):
        if random.random() < 0.6:  # 60% failure rate
            pool.mark_failure(proxy3, error="connection failed")
        else:
            pool.mark_success(proxy3, response_time=2.0 + random.uniform(0, 1.0))
    
    # Get all metrics
    all_metrics = pool.get_metrics()
    
    print(f"\nPool Summary:")
    print(f"  Total Proxies: {all_metrics['total_proxies']}")
    print(f"  Available Proxies: {all_metrics['available_proxies']}")
    print(f"  Rotation Strategy: {all_metrics['rotation_strategy']}")
    
    print("\nDetailed Proxy Metrics:")
    print("-" * 60)
    for proxy_url, metrics in all_metrics['proxies'].items():
        proxy_name = proxy_url.split('/')[-1].split(':')[0]
        print(f"\n{proxy_name}:")
        print(f"  Success Rate:     {metrics['success_rate']:>6.2%}")
        print(f"  Health Score:     {metrics['health_score']:>6.2%}")
        print(f"  Avg Response Time: {metrics['avg_response_time']:>5.2f}s")
        print(f"  Min Response Time: {metrics['min_response_time']:>5.2f}s")
        print(f"  Max Response Time: {metrics['max_response_time']:>5.2f}s")
        print(f"  Total Requests:   {metrics['total_requests']:>6}")
        print(f"  Success Count:    {metrics['success_count']:>6}")
        print(f"  Failure Count:    {metrics['failure_count']:>6}")
        print(f"  Consecutive Failures: {metrics['consecutive_failures']:>3}")
        print(f"  Consecutive Successes: {metrics['consecutive_successes']:>3}")
        print(f"  Circuit State:    {metrics['circuit_state']:>10}")
        print(f"  Times Used:       {metrics['times_used']:>6}")
    
    pool.cleanup()
    print()


def demo_proxy_management():
    """Demonstrate adding/removing proxies"""
    print("=" * 60)
    print("DEMO 7: Dynamic Proxy Management")
    print("=" * 60)
    
    pool = ProxyPool(
        proxies=['http://proxy1.example.com:8080']
    )
    
    print(f"\nInitial proxies: {len(pool.proxies)}")
    for proxy in pool.proxies:
        print(f"  - {proxy}")
    
    print("\nAdding new proxies...")
    pool.add_proxy('http://proxy2.example.com:8080')
    pool.add_proxy('http://proxy3.example.com:8080')
    print(f"\nAfter adding: {len(pool.proxies)} proxies")
    
    print("\nRemoving a proxy...")
    pool.remove_proxy('http://proxy2.example.com:8080')
    print(f"After removing: {len(pool.proxies)} proxies")
    for proxy in pool.proxies:
        print(f"  - {proxy}")
    
    print("\nResetting proxy metrics...")
    proxy = pool.proxies[0]
    pool.mark_success(proxy, response_time=0.5)
    pool.mark_failure(proxy, error="test")
    
    before = pool.get_metrics(proxy)
    print(f"  Before reset - Total requests: {before['total_requests']}")
    
    pool.reset_proxy(proxy)
    after = pool.get_metrics(proxy)
    print(f"  After reset - Total requests: {after['total_requests']}")
    
    pool.cleanup()
    print()


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("PROXY POOL DEMONSTRATIONS")
    print("=" * 60)
    print("\nThis demo showcases the advanced proxy pool features:")
    print("  1. Basic usage")
    print("  2. Rotation strategies")
    print("  3. Health scoring")
    print("  4. Retry/backoff")
    print("  5. Circuit breaker")
    print("  6. Metrics")
    print("  7. Dynamic proxy management")
    print()
    
    try:
        demo_basic_usage()
        demo_rotation_strategies()
        demo_health_scoring()
        demo_retry_backoff()
        demo_circuit_breaker()
        demo_metrics()
        demo_proxy_management()
        
        print("=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nFor more information, see PROXY_POOL_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

