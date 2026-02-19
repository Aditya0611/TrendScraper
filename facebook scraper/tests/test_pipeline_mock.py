
import sys
import logging
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from unittest.mock import MagicMock
from perfect_scraper import PerfectFacebookScraper
from datetime import datetime

# Setup logging to console
logging.basicConfig(level=logging.INFO)

def run_verification():
    print("starting verification...")
    # Initialize scraper
    scraper = PerfectFacebookScraper(debug=True)
    
    # Mock the actual scraping part to avoid network/cookie issues during verification
    # We want to test the DB insertion pipeline specifically
    scraper._get_posts_safe = MagicMock(return_value=[
        {
            'text': "This is a test post about #technology and #AI!",
            'post_id': '123456789',
            'time': datetime.now(),
            'likes': 100,
            'comments': 20,
            'shares': 5,
            'post_url': 'http://facebook.com/123',
            'reactions': {'like': 100}
        },
         {
            'text': "Another amazing #tech post with #innovation",
            'post_id': '987654321',
            'time': datetime.now(),
            'likes': 50,
            'comments': 10,
            'shares': 2,
            'post_url': 'http://facebook.com/987',
            'reactions': {'like': 50}
        }
    ])
    
    # Run the pipeline
    print("Running scraper pipeline (mocked network)...")
    results = scraper.get_trending_hashtags('technology', max_posts=10)
    
    if not results:
        print("❌ No results found (unexpected for mocked data)")
        return
        
    print(f"Generated {len(results)} trending topics.")
    
    # Save results - this triggers Supabase insertion
    print("\nTriggering Save...")
    scraper.save_results(results, 'technology')
    
    print("\nVerification complete.")

if __name__ == "__main__":
    run_verification()
