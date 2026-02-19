#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perfect_scraper import PerfectFacebookScraper
from free_api_scraper import FreeAPIFacebookScraper

class TestMultiScraperEnforcement(unittest.TestCase):
    
    def setUp(self):
        # Clear environment for clean tests
        if 'PROXIES' in os.environ: del os.environ['PROXIES']
        if 'PROXY_URL' in os.environ: del os.environ['PROXY_URL']
        os.environ['PROXY_STRICT_MODE'] = 'true'

    @patch('sys.exit')
    def test_perfect_scraper_enforcement(self, mock_exit):
        print("\nTesting PerfectFacebookScraper Strict Enforcement...")
        # Should call sys.exit(1) because PROXIES is empty and STRICT_MODE is true
        try:
            scraper = PerfectFacebookScraper()
        except Exception as e:
            print(f"Caught exception: {e}")
        
        mock_exit.assert_called_with(1)
        print("SUCCESS: Perfect Scraper exited as expected.")

    @patch('sys.exit')
    def test_free_api_scraper_enforcement(self, mock_exit):
        print("\nTesting FreeAPIFacebookScraper Strict Enforcement...")
        # Should call sys.exit(1) because PROXIES is empty and STRICT_MODE is true
        try:
            scraper = FreeAPIFacebookScraper(api_type='facebook_scraper')
        except Exception as e:
            print(f"Caught exception: {e}")
        
        mock_exit.assert_called_with(1)
        print("SUCCESS: Free API Scraper exited as expected.")

if __name__ == '__main__':
    unittest.main()
