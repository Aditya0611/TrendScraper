import scrapy
import re
import json
import time
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from scrapy.http import HtmlResponse
import undetected_chromedriver as uc
from dotenv import load_dotenv
import os

from ..items import HashtagItem

load_dotenv()


class LinkedinHashtagsSpider(scrapy.Spider):
    name = 'linkedin_hashtags'
    allowed_domains = ['linkedin.com']
    start_urls = ['https://www.linkedin.com/feed/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
    }
    
    def __init__(self, *args, **kwargs):
        super(LinkedinHashtagsSpider, self).__init__(*args, **kwargs)
        self.driver = None
        self.hashtag_counts = {}
        self.hashtag_contexts = {}
        self.hashtag_original_case = {}
        self.cookies_file = Path("../linkedin_cookies.json")
        self.email = os.getenv("LINKEDIN_EMAIL", "").strip()
        self.password = os.getenv("LINKEDIN_PASSWORD", "").strip()
        
    def start_requests(self):
        """Initialize the spider with authentication"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_with_selenium,
                meta={'dont_cache': True}
            )
    
    def _setup_driver(self):
        """Set up Chrome driver with proper configuration"""
        if self.driver:
            return
            
        try:
            # Configure Chrome options for LinkedIn scraping
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Use desktop user agent
            desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={desktop_ua}")
            
            # Try different approaches for driver initialization
            attempts = [
                lambda: uc.Chrome(options=options, use_subprocess=True),
                lambda: uc.Chrome(use_subprocess=True),
                lambda: uc.Chrome()
            ]
            
            driver_created = False
            for i, attempt in enumerate(attempts):
                try:
                    self.logger.info(f"Attempting driver setup method {i+1}...")
                    self.driver = attempt()
                    driver_created = True
                    break
                except Exception as e:
                    self.logger.warning(f"Method {i+1} failed: {e}")
                    continue
            
            if not driver_created:
                raise Exception("All driver setup methods failed")
            
            # Configure driver after successful creation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            self.logger.info("✅ Chrome driver setup successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup driver: {e}")
            raise
    
    def _load_cookies(self):
        """Load saved LinkedIn cookies"""
        if not self.cookies_file.exists():
            self.logger.info("No cookie file found")
            return False
            
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            self.driver.delete_all_cookies()
            for cookie in cookies:
                try:
                    if all(k in cookie for k in ['name', 'value']):
                        clean_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.linkedin.com'),
                            'path': cookie.get('path', '/'),
                            'secure': cookie.get('secure', True),
                            'httpOnly': cookie.get('httpOnly', False)
                        }
                        if 'expiry' in cookie:
                            clean_cookie['expiry'] = int(cookie['expiry'])
                        self.driver.add_cookie(clean_cookie)
                except:
                    continue
                    
            self.logger.info(f"✅ Loaded {len(cookies)} cookies")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    def _save_cookies(self):
        """Save current session cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            self.logger.info(f"💾 Saved {len(cookies)} cookies")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to save cookies: {e}")
            return False
    
    def _check_login_status(self):
        """Check if successfully logged into LinkedIn"""
        try:
            current_url = self.driver.current_url.lower()
            
            # Check for login failure indicators
            if any(fail in current_url for fail in ['login', 'challenge', 'checkpoint']):
                return False
                
            # Check for success indicators
            if any(success in current_url for success in ['feed', 'mynetwork', 'jobs']):
                return True
                
            # Check for navigation elements
            nav_selectors = [
                "nav#global-nav",
                "#global-nav-search",
                ".global-nav__me",
                "[data-control-name='nav.settings']"
            ]
            
            for selector in nav_selectors:
                try:
                    if self.driver.find_element(By.CSS_SELECTOR, selector).is_displayed():
                        return True
                except:
                    continue
                    
            return False
            
        except:
            return False
    
    def _authenticate_with_cookies(self):
        """Try to authenticate using saved cookies"""
        self.logger.info("🍪 Attempting cookie authentication...")
        
        self.driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        if not self._load_cookies():
            return False
            
        self.driver.refresh()
        time.sleep(5)
        
        if self._check_login_status():
            self.logger.info("✅ Cookie authentication successful!")
            return True
        else:
            self.logger.warning("❌ Cookie authentication failed")
            return False
    
    def _authenticate_with_credentials(self):
        """Authenticate using email and password"""
        if not self.email or not self.password:
            self.logger.error("❌ LinkedIn credentials not found in .env file")
            return False
            
        self.logger.info("🔐 Attempting credential authentication...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Fill email
            email_field = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "username"))
            )
            email_field.clear()
            for char in self.email:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            for char in self.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(8)
            
            # Handle potential security challenges
            current_url = self.driver.current_url.lower()
            if any(challenge in current_url for challenge in ['challenge', 'captcha', 'security']):
                self.logger.warning("🚨 Security challenge detected - please solve manually")
                input("Press Enter after completing the security challenge...")
            
            # Navigate to feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(5)
            
            if self._check_login_status():
                self.logger.info("✅ Credential authentication successful!")
                self._save_cookies()
                return True
            else:
                self.logger.error("❌ Credential authentication failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return False
    
    def parse_with_selenium(self, response):
        """Use Selenium to handle LinkedIn's dynamic content and authentication"""
        self._setup_driver()
        
        # Try cookie authentication first, then credentials
        authenticated = (
            self._authenticate_with_cookies() or 
            self._authenticate_with_credentials()
        )
        
        if not authenticated:
            self.logger.error("❌ All authentication methods failed")
            return
        
        # Navigate to feed if not already there
        if 'feed' not in self.driver.current_url:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(5)
        
        # Scroll through the feed to load more content
        self._scroll_feed()
        
        # Get the page source and create Scrapy response
        html_content = self.driver.page_source
        
        # Save debug HTML
        debug_file = f"debug_scrapy_feed_{int(time.time())}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"💾 Saved debug HTML to {debug_file}")
        
        # Create Scrapy response from Selenium page source
        selenium_response = HtmlResponse(
            url=self.driver.current_url,
            body=html_content,
            encoding='utf-8'
        )
        
        # Parse the content for hashtags
        return self.parse_hashtags(selenium_response)
    
    def _scroll_feed(self, max_scrolls=15):
        """Scroll through LinkedIn feed to load more posts"""
        self.logger.info("📜 Scrolling through LinkedIn feed...")
        
        for i in range(max_scrolls):
            try:
                # Random scroll distance
                scroll_distance = random.randint(700, 1200)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                
                self.logger.info(f"📜 Scroll {i+1}/{max_scrolls}")
                
                # Occasional reverse scroll for more natural behavior
                if i > 0 and i % 4 == 0:
                    reverse_distance = random.randint(100, 400)
                    self.driver.execute_script(f"window.scrollBy(0, -{reverse_distance});")
                    time.sleep(random.uniform(1, 3))
                
                # Random delay between scrolls
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                self.logger.warning(f"Error during scroll {i+1}: {e}")
                continue
        
        self.logger.info("✅ Feed scrolling completed")
    
    def parse_hashtags(self, response):
        """Parse hashtags from the LinkedIn feed"""
        self.logger.info("🔍 Parsing hashtags from LinkedIn feed...")
        
        # Find post containers using multiple selectors
        post_selectors = [
            "div.feed-shared-update-v2",
            "div[data-id]",
            "article",
            "div.update-components-update-v2",
        ]
        
        posts = []
        for selector in post_selectors:
            posts = response.css(selector)
            if posts:
                self.logger.info(f"📊 Found {len(posts)} posts using '{selector}' selector")
                break
        
        if not posts:
            self.logger.warning("⚠️ No post containers found, trying direct hashtag extraction")
            return self._extract_hashtags_directly(response)
        
        # Extract hashtags from posts
        for post in posts:
            self._extract_hashtags_from_post(post)
        
        # Also try direct hashtag extraction as backup
        direct_hashtags = self._extract_hashtags_directly(response)
        
        # Generate final results
        return self._generate_hashtag_items()
    
    def _extract_hashtags_from_post(self, post):
        """Extract hashtags from a single post"""
        # Get post text content
        text_selectors = [
            ".update-components-text",
            ".feed-shared-update-v2__commentary",
            ".update-components-update-v2__commentary",
            ".feed-shared-text",
            ".feed-shared-update-v2__description",
        ]
        
        post_text = ""
        for selector in text_selectors:
            text_element = post.css(selector)
            if text_element:
                post_text = text_element.get()
                break
        
        if not post_text:
            post_text = post.get()
        
        # Extract hashtags using regex
        hashtag_pattern = r'#([A-Za-z0-9_]+)'
        matches = re.findall(hashtag_pattern, post_text)
        
        for hashtag in matches:
            if 2 <= len(hashtag) <= 50:
                tag_lower = hashtag.lower()
                self.hashtag_counts[tag_lower] = self.hashtag_counts.get(tag_lower, 0) + 1
                
                if tag_lower not in self.hashtag_contexts:
                    self.hashtag_contexts[tag_lower] = []
                if len(self.hashtag_contexts[tag_lower]) < 3:
                    clean_text = re.sub(r'<[^>]+>', '', post_text)
                    self.hashtag_contexts[tag_lower].append(clean_text[:300])
                
                if tag_lower not in self.hashtag_original_case:
                    self.hashtag_original_case[tag_lower] = hashtag
    
    def _extract_hashtags_directly(self, response):
        """Direct hashtag extraction from hashtag links"""
        self.logger.info("🔗 Attempting direct hashtag extraction...")
        
        # Find hashtag links with expanded selectors
        hashtag_links = response.css(
            'a[href*="/feed/hashtag/"], '
            'a[href*="/hashtag/"], '
            'a[href*="keywords=%23"]'
        )
        
        self.logger.info(f"Found {len(hashtag_links)} potential hashtag links")
        
        for link in hashtag_links:
            # Extract hashtag from link
            href = link.attrib.get('href', '')
            text = link.css('::text').get('')
            
            hashtag = None
            
            # Method 1: From text content
            if text.startswith('#'):
                hashtag = text[1:]
            
            # Method 2: From URL parameters
            elif 'keywords=%23' in href:
                hashtag = href.split('keywords=%23')[1].split('&')[0]
            
            # Method 3: From hashtag path
            elif '/hashtag/' in href:
                hashtag = href.split('/hashtag/')[1].split('?')[0].split('/')[0]
            
            if hashtag and 2 <= len(hashtag) <= 50:
                tag_lower = hashtag.lower()
                self.hashtag_counts[tag_lower] = self.hashtag_counts.get(tag_lower, 0) + 1
                
                if tag_lower not in self.hashtag_original_case:
                    self.hashtag_original_case[tag_lower] = hashtag
                
                # Get context from parent elements
                if tag_lower not in self.hashtag_contexts:
                    self.hashtag_contexts[tag_lower] = []
                if len(self.hashtag_contexts[tag_lower]) < 3:
                    parent_text = link.xpath('./parent::*/text()').get('')
                    if parent_text:
                        self.hashtag_contexts[tag_lower].append(parent_text[:300])
        
        return []
    
    def _generate_hashtag_items(self):
        """Generate HashtagItem objects from collected data"""
        self.logger.info(f"📝 Generating items for {len(self.hashtag_counts)} hashtags...")
        
        items = []
        
        for hashtag, count in sorted(self.hashtag_counts.items(), key=lambda x: x[1], reverse=True):
            item = HashtagItem()
            item['name'] = hashtag
            item['original_case'] = self.hashtag_original_case.get(hashtag, hashtag)
            item['url'] = f"https://www.linkedin.com/feed/hashtag/{hashtag}/"
            item['mentions'] = count
            item['context'] = ' | '.join(self.hashtag_contexts.get(hashtag, [])[:3])
            item['sentiment_score'] = 0.0  # Can be enhanced with sentiment analysis
            item['sentiment_polarity'] = 'neutral'
            item['scraped_at'] = datetime.now().isoformat()
            item['post_text'] = self.hashtag_contexts.get(hashtag, [''])[0]
            item['author'] = 'various'
            
            items.append(item)
            yield item
        
        self.logger.info(f"✅ Generated {len(items)} hashtag items")
    
    def closed(self, reason):
        """Clean up when spider closes"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
        self.logger.info(f"🕷️ Spider closed: {reason}")
