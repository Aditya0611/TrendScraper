#!/usr/bin/env python3
"""
Simple Test Suite for TikTok Scraper (Windows Compatible)
Tests all modules to ensure production readiness
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestSuite")

# Test counters
passed = 0
failed = 0
failed_tests = []

def test(name, condition, error_msg=""):
    """Record test result."""
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        failed_tests.append((name, error_msg))
        print(f"[FAIL] {name}: {error_msg}")

print("="*60)
print("COMPREHENSIVE TEST SUITE")
print("="*60)
print(f"Started: {datetime.now()}")
print("="*60)

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded .env file")
except:
    print("[WARN] Could not load .env file")

# TEST 1: Environment
print("\n[TEST 1] Environment Configuration")
test("ENV: SUPABASE_URL", bool(os.environ.get('SUPABASE_URL')))
test("ENV: SUPABASE_KEY", bool(os.environ.get('SUPABASE_KEY')))

# TEST 2: Imports
print("\n[TEST 2] Module Imports")
modules = ['base', 'job_queue', 'odoo_sync', 'cache_manager']
for mod in modules:
    try:
        __import__(mod)
        test(f"IMPORT: {mod}", True)
    except ImportError as e:
        test(f"IMPORT: {mod}", False, str(e))

# TEST 3: Database
print("\n[TEST 3] Database Connection")
try:
    from base import init_supabase
    supabase = init_supabase()
    test("DB: Connection", supabase is not None)
    
    if supabase:
        try:
            result = supabase.table('tiktok').select('id').limit(1).execute()
            test("DB: Table Access", True)
            
            result_all = supabase.table('tiktok').select('id').execute()
            count = len(result_all.data)
            test("DB: Has Records", count > 0)
            print(f"      Found {count} records in database")
        except Exception as e:
            test("DB: Table Access", False, str(e))
except Exception as e:
    test("DB: Connection", False, str(e))

# TEST 4: Job Queue
print("\n[TEST 4] Job Queue")
try:
    from job_queue import JobQueue
    from base import init_supabase
    
    supabase = init_supabase()
    if supabase:
        queue = JobQueue(supabase)
        test("QUEUE: Initialization", True)
        
        # Test operations
        try:
            job_id = queue.add_job("test", {"data": "test"}, 3)
            test("QUEUE: Add Job", job_id is not None)
            
            jobs = queue.fetch_pending_jobs(1)
            test("QUEUE: Fetch Jobs", True)
            
            if job_id:
                queue.mark_completed(job_id)
        except Exception as e:
            test("QUEUE: Operations", False, str(e))
    else:
        test("QUEUE: Initialization", False, "No DB connection")
except Exception as e:
    test("QUEUE: Module", False, str(e))

# TEST 5: Worker (Deprecated in favor of Odoo Cron)
print("\n[TEST 5] Worker Scheduler")
print("SKIPPED: APScheduler deprecated. Using Odoo ir.cron.")


# TEST 6: Cache
print("\n[TEST 6] Cache Manager")
try:
    from cache_manager import LocalCache
    cache = LocalCache()
    test("CACHE: Initialization", True)
    
    test_data = [{"topic": "test", "score": 100}]
    cache.set_trend_data("test", test_data, "TikTok")
    cached = cache.get_trend_data("test", "TikTok")
    test("CACHE: Read/Write", cached is not None)
except Exception as e:
    test("CACHE: Module", False, str(e))

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")

if failed_tests:
    print("\nFailed Tests:")
    for name, msg in failed_tests:
        print(f"  - {name}: {msg}")

print("="*60)
print(f"Completed: {datetime.now()}")
print("="*60)

# Exit code
sys.exit(0 if failed == 0 else 1)
