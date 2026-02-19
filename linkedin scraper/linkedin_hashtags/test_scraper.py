#!/usr/bin/env python3
"""
Test script to run the LinkedIn hashtag scraper directly
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Scrapy
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'linkedin_hashtags.settings')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from linkedin_hashtags.spiders.linkedin_hashtags import LinkedinHashtagsSpider

def run_scraper():
    """Run the LinkedIn hashtag scraper"""
    print("🚀 Starting LinkedIn Hashtag Scraper (Scrapy Version)")
    print("="*60)
    
    # Get project settings
    settings = get_project_settings()
    
    # Override some settings for testing
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('LOG_FILE', None)  # Log to console
    
    # Create and configure the crawler process
    process = CrawlerProcess(settings)
    
    # Add our spider
    process.crawl(LinkedinHashtagsSpider)
    
    # Start the crawling process
    print("📡 Starting crawler...")
    process.start()  # This will block until crawling is finished

if __name__ == "__main__":
    try:
        run_scraper()
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error running scraper: {e}")
        import traceback
        traceback.print_exc()
