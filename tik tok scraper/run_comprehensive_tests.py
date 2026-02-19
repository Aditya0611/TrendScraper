#!/usr/bin/env python3
"""
Comprehensive Test Suite for TikTok Scraper
Tests all modules to ensure production readiness
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestSuite")

# Test results tracking
test_results = {
    'passed': [],
    'failed': [],
    'skipped': []
}

def test_result(test_name, passed, message=""):
    """Record test result."""
    if passed:
        test_results['passed'].append(test_name)
        logger.info(f"✅ PASS: {test_name}")
    else:
        test_results['failed'].append((test_name, message))
        logger.error(f"❌ FAIL: {test_name} - {message}")

def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⏭️  Skipped: {len(test_results['skipped'])}")
    
    if test_results['failed']:
        print("\nFailed Tests:")
        for test_name, message in test_results['failed']:
            print(f"  - {test_name}: {message}")
    
    print("="*60)
    
    # Return exit code
    return 0 if len(test_results['failed']) == 0 else 1

# ============================================================================
# TEST 1: Environment Configuration
# ============================================================================

def test_environment():
    """Test environment variables are set."""
    logger.info("Testing environment configuration...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            test_result(f"ENV: {var}", True)
        else:
            test_result(f"ENV: {var}", False, "Not set")

# ============================================================================
# TEST 2: Module Imports
# ============================================================================

def test_imports():
    """Test all modules can be imported."""
    logger.info("Testing module imports...")
    
    modules = [
        'base',
        'job_queue',
        'worker_apscheduler',
        'odoo_sync',
        'cache_manager',
        'proxy_pool',
        'logging_metrics'
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
            test_result(f"IMPORT: {module_name}", True)
        except ImportError as e:
            test_result(f"IMPORT: {module_name}", False, str(e))

# ============================================================================
# TEST 3: Database Connection
# ============================================================================

def test_database():
    """Test Supabase database connection."""
    logger.info("Testing database connection...")
    
    try:
        from base import init_supabase
        supabase = init_supabase()
        
        if supabase:
            test_result("DB: Connection", True)
            
            # Test table access
            try:
                result = supabase.table('tiktok').select('id').limit(1).execute()
                test_result("DB: Table Access", True)
                
                # Test record count
                result_all = supabase.table('tiktok').select('id').execute()
                count = len(result_all.data)
                test_result("DB: Record Count", count > 0, f"Found {count} records")
                
            except Exception as e:
                test_result("DB: Table Access", False, str(e))
        else:
            test_result("DB: Connection", False, "Failed to initialize")
            
    except Exception as e:
        test_result("DB: Connection", False, str(e))

# ============================================================================
# TEST 4: Job Queue
# ============================================================================

def test_job_queue():
    """Test job queue functionality."""
    logger.info("Testing job queue...")
    
    try:
        from job_queue import JobQueue
        from base import init_supabase
        
        supabase = init_supabase()
        if not supabase:
            test_result("QUEUE: Initialization", False, "No Supabase connection")
            return
        
        queue = JobQueue(supabase)
        test_result("QUEUE: Initialization", True)
        
        # Test add job
        try:
            job_id = queue.add_job(
                job_type="test",
                payload={"test": "data"},
                max_attempts=3
            )
            test_result("QUEUE: Add Job", job_id is not None)
            
            # Test fetch jobs
            jobs = queue.fetch_pending_jobs(limit=1)
            test_result("QUEUE: Fetch Jobs", True)
            
            # Cleanup test job
            if job_id:
                queue.mark_completed(job_id)
                
        except Exception as e:
            test_result("QUEUE: Operations", False, str(e))
            
    except Exception as e:
        test_result("QUEUE: Module", False, str(e))

# ============================================================================
# TEST 5: Odoo Sync
# ============================================================================

def test_odoo_sync():
    """Test Odoo sync module."""
    logger.info("Testing Odoo sync...")
    
    try:
        from odoo_sync import OdooSync
        
        syncer = OdooSync()
        test_result("ODOO: Initialization", True)
        
        # Check if Odoo is configured
        if syncer.uid:
            test_result("ODOO: Connection", True)
        else:
            test_result("ODOO: Connection", False, "Not configured (expected if no Odoo)")
            
    except Exception as e:
        test_result("ODOO: Module", False, str(e))

# ============================================================================
# TEST 6: Cache Manager
# ============================================================================

def test_cache():
    """Test cache manager."""
    logger.info("Testing cache manager...")
    
    try:
        from cache_manager import LocalCache
        
        cache = LocalCache()
        test_result("CACHE: Initialization", True)
        
        # Test write/read
        test_data = [{"topic": "test", "score": 100}]
        cache.set_trend_data("test_topic", test_data, platform="TikTok")
        
        cached = cache.get_trend_data("test_topic", platform="TikTok")
        test_result("CACHE: Read/Write", cached is not None)
        
    except Exception as e:
        test_result("CACHE: Module", False, str(e))

# ============================================================================
# TEST 7: Proxy Pool
# ============================================================================

def test_proxy_pool():
    """Test proxy pool."""
    logger.info("Testing proxy pool...")
    
    try:
        from proxy_pool import ProxyPool, ProxyConfig
        
        # Test with empty pool (no proxies configured)
        pool = ProxyPool(proxies=[])
        test_result("PROXY: Initialization", True)
        
    except Exception as e:
        test_result("PROXY: Module", False, str(e))

# ============================================================================
# TEST 8: Worker Scheduler
# ============================================================================

def test_worker():
    """Test worker scheduler."""
    logger.info("Testing worker scheduler...")
    
    try:
        from worker_apscheduler import APSchedulerWorker
        
        # Initialize worker (don't start)
        worker = APSchedulerWorker()
        test_result("WORKER: Initialization", True)
        
        # Test config loading
        configs = worker.load_platform_configs()
        test_result("WORKER: Load Configs", len(configs) > 0)
        
    except Exception as e:
        test_result("WORKER: Module", False, str(e))

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests."""
    print("="*60)
    print("COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now()}")
    print("="*60)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded .env file")
    except:
        logger.warning("Could not load .env file")
    
    # Run tests
    test_environment()
    test_imports()
    test_database()
    test_job_queue()
    test_odoo_sync()
    test_cache()
    test_proxy_pool()
    test_worker()
    
    # Print summary
    exit_code = print_summary()
    
    print(f"\nCompleted at: {datetime.now()}")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
