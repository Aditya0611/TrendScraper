import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch
from base import BaseScraper, ProxyManager

class TestFinalCompliance(unittest.TestCase):
    
    def setUp(self):
        # Mock env vars to prevent actual DB/Proxy noise during unit logic test
        self.env_patcher = patch.dict(os.environ, {
            'PROXIES': '',
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-key'
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_no_bypass_mandate(self):
        """Verify that BaseScraper hard-fails (sys.exit) when no proxies are available"""
        print("\n[TEST] Verifying 'No Bypass' Mandate...")
        
        # Mock ProxyManager to return no proxies
        with patch('base.ProxyManager.from_env') as mock_from_env:
            mock_pm = MagicMock(spec=ProxyManager)
            mock_pm.get_next_proxy.return_value = None
            mock_pm.proxies = []
            mock_from_env.return_value = mock_pm
            
            scraper = BaseScraper()
            
            # Should call sys.exit(1) inside setup_browser because proxy_config is None
            with self.assertRaises(SystemExit) as cm:
                scraper.setup_browser()
            
            self.assertEqual(cm.exception.code, 1)
            print("PASS: Scraper hard-failed with sys.exit(1) on missing proxy.")

    def test_run_tracking_initialization(self):
        """Verify that run tracking is initialized during browser setup"""
        print("\n[TEST] Verifying Run Tracking Initialization...")
        
        with patch('base.sync_playwright'):
            with patch('base.create_client') as mock_supabase_client:
                scraper = BaseScraper()
                scraper.logger = MagicMock()
                
                # Mock a successful proxy so it proceeds to run initialization
                mock_proxy = {'server': 'http://proxy:8080'}
                scraper.proxy_manager.get_next_proxy = MagicMock(return_value=mock_proxy)
                
                # Mock browser/context/page
                scraper.playwright = MagicMock()
                scraper.browser = MagicMock()
                
                scraper.setup_browser()
                
                # check if _start_scrape_run was triggered
                # it's called inside setup_browser if proxy_config exists
                self.assertTrue(scraper._run_started)
                mock_supabase_client.return_value.table.assert_any_call('scrape_runs')
                print("PASS: Run tracking initialized in Supabase.")

    def test_fatal_db_failure(self):
        """Verify that DB insertion failure is fatal (sys.exit)"""
        print("\n[TEST] Verifying Fatal DB Insertion...")
        
        scraper = BaseScraper()
        scraper.logger = MagicMock()
        
        # Mock _save_to_supabase_normalized to raise an error
        with patch.object(BaseScraper, '_save_to_supabase_normalized', side_effect=Exception("DB Connection Lost")):
            with self.assertRaises(SystemExit) as cm:
                scraper.save_results([], "test_category", "test_version_id")
            
            self.assertEqual(cm.exception.code, 1)
            print("PASS: DB failure triggered fatal exit.")

if __name__ == "__main__":
    unittest.main()
