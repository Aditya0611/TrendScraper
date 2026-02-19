import os
import time
import random
import json
import logging
import re
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from textblob import TextBlob
from supabase import create_client, Client

# Selenium (undetected)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class ScrapingConfig:
    """Configuration class for scraping parameters"""
    email: str = os.getenv("LINKEDIN_EMAIL", "").strip()
    password: str = os.getenv("LINKEDIN_PASSWORD", "").strip()
    hashtag: str = os.getenv("HASHTAG", "ai").strip()
    max_scrolls: int = int(os.getenv("MAX_SCROLLS", "5"))
    max_posts: int = int(os.getenv("MAX_POSTS", "50"))
    proxy_host: str = os.getenv("PROXY_HOST", "").strip()
    proxy_port: str = os.getenv("PROXY_PORT", "").strip()
    cookies_file: Path = Path("linkedin_cookies.json")
    output_dir: Path = Path("output")
    supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
    supabase_key: str = os.getenv("SUPABASE_KEY", "").strip()
    
    def __post_init__(self):
        self.output_dir.mkdir(exist_ok=True)

@dataclass
class LinkedInPost:
    """Data class for LinkedIn post information"""
    author: str
    time: str
    text: str
    link: str
    engagement_stats: Dict[str, int] = None
    sentiment_score: float = 0.0
    sentiment_polarity: str = "neutral"
    hashtag_engagement_score: float = 0.0
    
    def __post_init__(self):
        if self.engagement_stats is None:
            self.engagement_stats = {}

class LinkedInScraper:
    """Enhanced LinkedIn scraper with better error handling and structure"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.driver = None
        
        # Updated selectors based on LinkedIn's current HTML structure (2025)
        self.selectors = {
            'post_containers': [
                "article.main-feed-activity-card",
                "div.feed-shared-update-v2",
            ],
            'author': [
                "a[data-tracking-control-name='feed_main-feed-card_feed-actor-name']",
                "a[data-tracking-control-name='feed_main-feed-card_reshare_feed-actor-name']",
                ".base-main-feed-card__entity-lockup a span[aria-hidden='true']",
                "span.feed-shared-actor__name",
                "[data-test-id='main-feed-card__actor-lockup-title']"
            ],
            'time': [
                "span.text-sm.text-color-text-low-emphasis",
                ".base-main-feed-card__entity-lockup span",
                "span.feed-shared-actor__sub-description"
            ],
            'text': [
                "p.attributed-text-segment-list__content",
                "div.papabear-text-view",
                "div.update-components-text",
                "div.feed-shared-update-v2__description-wrapper",
                "span.break-words",
                "div.feed-shared-text"
            ],
            'engagement': {
                'likes': [
                    "span[data-test-id='social-actions__reaction-count']",
                    "span.social-details-social-counts__reactions-count"
                ],
                'comments': [
                    "li.social-details-social-counts__item--with-social-proof button",
                    "span.social-action-bar__button-text"
                ],
            }
        }

    def rand_sleep(self, min_time: float = 1.0, max_time: float = 3.0):
        time.sleep(random.uniform(min_time, max_time))

    def build_driver(self, use_proxy: bool = False) -> uc.Chrome:
        ua = UserAgent()
        options = uc.ChromeOptions()
        
        # Headless mode to avoid renderer issues
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-agent={ua.random}")
        
        if use_proxy and self.config.proxy_host and self.config.proxy_port:
            options.add_argument(f"--proxy-server=http://{self.config.proxy_host}:{self.config.proxy_port}")
            logger.info(f"Using proxy: {self.config.proxy_host}:{self.config.proxy_port}")
        
        try:
            driver = uc.Chrome(options=options, version_main=139)
            driver.set_page_load_timeout(90)
            driver.implicitly_wait(30)
            return driver
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise

    def build_driver_with_gui(self) -> uc.Chrome:
        """Build driver without headless mode for manual verification"""
        ua = UserAgent()
        options = uc.ChromeOptions()
        
        # Non-headless mode for manual verification
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={ua.random}")
        
        try:
            driver = uc.Chrome(options=options, version_main=139)
            driver.set_page_load_timeout(90)
            driver.implicitly_wait(30)
            return driver
        except Exception as e:
            logger.error(f"Failed to create GUI driver: {e}")
            raise

    def save_cookies(self) -> bool:
        try:
            cookies = self.driver.get_cookies()
            with open(self.config.cookies_file, "w", encoding="utf-8") as f: json.dump(cookies, f, indent=2)
            logger.info(f"Saved cookies to {self.config.cookies_file}")
            return True
        except Exception as e:
            logger.warning(f"Failed to save cookies: {e}"); return False

    def load_cookies(self) -> bool:
        if not self.config.cookies_file.exists(): return False
        try:
            with open(self.config.cookies_file, "r", encoding="utf-8") as f: cookies = json.load(f)
            self.driver.delete_all_cookies()
            for cookie in cookies:
                if "expiry" in cookie and cookie["expiry"] is not None:
                    try: cookie["expiry"] = int(cookie["expiry"])
                    except (ValueError, TypeError): cookie.pop("expiry", None)
                try: self.driver.add_cookie(cookie)
                except Exception: continue
            logger.info(f"Loaded cookies from {self.config.cookies_file}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load cookies: {e}"); return False

    def login(self) -> bool:
        try:
            self.driver.get("https://www.linkedin.com/login")
            try:
                wait = WebDriverWait(self.driver, 10)
                username_field = wait.until(EC.element_to_be_clickable((By.NAME, "session_key")))
                logger.info("Standard login page detected. Entering email.")
                username_field.clear()
                username_field.send_keys(self.config.email)
            except TimeoutException:
                logger.info("Email field not found, assuming 'Welcome back' page.")
                pass
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.config.password)
            password_field.send_keys(Keys.RETURN)
            self.rand_sleep(4, 7)
            
            current_url = self.driver.current_url.lower()
            if "feed" in current_url: 
                logger.info("Login successful")
                return True
            elif "checkpoint" in current_url or "challenge" in current_url: 
                logger.warning("Login requires verification - switching to non-headless mode for manual verification")
                # Switch to non-headless mode for manual verification
                self.cleanup()
                self.driver = self.build_driver_with_gui()
                return self.manual_verification_login()
            else: 
                logger.error(f"Login failed. URL: {current_url}")
                return False
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return False

    def manual_verification_login(self) -> bool:
        """Handle manual verification with user interaction"""
        try:
            logger.info("Loading LinkedIn login page for manual verification...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Fill in credentials
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "session_key"))
                )
                username_field.clear()
                username_field.send_keys(self.config.email)
                
                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(self.config.password)
                password_field.send_keys(Keys.RETURN)
            except Exception as e:
                logger.error(f"Error filling credentials: {e}")
                return False
            
            # Wait for user to complete verification manually
            logger.info("Please complete the verification challenge manually in the browser window.")
            logger.info("Press Enter in this terminal once you have successfully logged in...")
            input("Waiting for manual verification completion...")
            
            # Check if login was successful
            current_url = self.driver.current_url.lower()
            if "feed" in current_url:
                logger.info("Manual verification successful!")
                self.save_cookies()
                # Switch back to headless mode
                self.cleanup()
                self.driver = self.build_driver(False)
                self.load_cookies()
                return True
            else:
                logger.error("Manual verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Manual verification exception: {e}")
            return False

    def human_like_browsing(self):
        logger.info("Performing human-like navigation...")
        self.driver.get("https://www.linkedin.com/feed/")
        self.rand_sleep(3, 6)
        for _ in range(random.randint(1, 2)):
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(300, 600)});")
            self.rand_sleep(1, 3)

    def fetch_trending_hashtags(self) -> List[Dict[str, str]]:
        """Scrape trending hashtags from LinkedIn feed posts"""
        hashtags = []
        
        try:
            # Navigate to main feed and ensure we're logged in
            logger.info("Extracting hashtags from LinkedIn feed posts...")
            self.driver.get("https://www.linkedin.com/feed/")
            self.rand_sleep(4, 6)
            
            # Check if we're actually on the feed (not redirected to login)
            current_url = self.driver.current_url.lower()
            if "login" in current_url or "checkpoint" in current_url:
                logger.error("Not properly authenticated - redirected to login page")
                return hashtags
            
            # Scroll through feed to load more posts
            for i in range(8):  # Increased scrolls to get more posts
                self.driver.execute_script("window.scrollBy(0, 800);")
                self.rand_sleep(2, 3)
                logger.info(f"Feed scroll progress: {i+1}/8")
            
            # Get hashtags from current feed
            html_source = self.driver.page_source
            hashtags = self.parse_hashtags(html_source)
            
            # Save debug HTML
            debug_file = self.config.output_dir / "debug_hashtags_page.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(html_source)
            logger.info(f"Saved hashtag debug HTML to {debug_file}")
            
        except Exception as e:
            logger.error(f"Error extracting hashtags from feed: {e}")
        
        return hashtags

    def parse_hashtags(self, html: str) -> List[Dict[str, str]]:
        """Parse hashtags from LinkedIn HTML and count their frequency"""
        soup = BeautifulSoup(html, "html.parser")
        hashtag_counts = {}
        hashtag_contexts = {}  # Store context text for sentiment analysis
        
        # Extract hashtags from post content using regex
        hashtag_pattern = r'#(\w+)'
        post_elements = soup.select('.attributed-text-segment-list__content')
        
        logger.info(f"Analyzing {len(post_elements)} posts for hashtags...")
        
        for post in post_elements:
            text = post.get_text()
            found_hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
            for tag in found_hashtags:
                tag_lower = tag.lower()
                hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
                # Store context for sentiment analysis
                if tag_lower not in hashtag_contexts:
                    hashtag_contexts[tag_lower] = []
                hashtag_contexts[tag_lower].append(text)
        
        # Also check for hashtag links in the page
        hashtag_links = soup.select('a[href*="/hashtag/"]')
        for link in hashtag_links:
            try:
                href = link.get('href', '')
                if '/hashtag/' in href:
                    hashtag_name = href.split('/hashtag/')[-1].split('/')[0].lower()
                    hashtag_counts[hashtag_name] = hashtag_counts.get(hashtag_name, 0) + 1
            except Exception as e:
                continue
        
        # Convert to list and sort by frequency
        hashtags = []
        for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True):
            # Calculate sentiment for this hashtag based on context
            context_texts = hashtag_contexts.get(tag, [])
            combined_context = ' '.join(context_texts[:5])  # Use first 5 contexts
            sentiment_score, sentiment_polarity = self.calculate_sentiment(combined_context) if combined_context else (0.0, "neutral")
            
            hashtags.append({
                'name': tag,
                'url': f"https://www.linkedin.com/feed/hashtag/{tag}/",
                'followers': f"Mentioned {count} times",
                'count': count,
                'sentiment_score': sentiment_score,
                'sentiment_polarity': sentiment_polarity,
                'context_sample': combined_context[:200] + "..." if len(combined_context) > 200 else combined_context
            })
        
        logger.info(f"Successfully extracted {len(hashtags)} unique hashtags with sentiment analysis")
        return hashtags

    def extract_element_text(self, container, selectors: List[str]) -> Optional[str]:
        for selector in selectors:
            if (element := container.select_one(selector)) and (text := element.get_text(strip=True)): return text
        return None

    def extract_engagement_stats(self, container) -> Dict[str, int]:
        stats = {}
        for stat_type, selectors in self.selectors['engagement'].items():
            for selector in selectors:
                if element := container.select_one(selector):
                    import re
                    text = element.get_text(strip=True)
                    numbers = re.findall(r'\d+', text)
                    if numbers: 
                        stats[stat_type] = int(numbers[0])
                        break
                    # Also check for common engagement text patterns
                    if stat_type == 'likes' and any(word in text.lower() for word in ['like', 'reaction']):
                        # Try to extract from aria-label or title attributes
                        for attr in ['aria-label', 'title']:
                            if attr_text := element.get(attr):
                                numbers = re.findall(r'\d+', attr_text)
                                if numbers:
                                    stats[stat_type] = int(numbers[0])
                                    break
        return stats

    def parse_posts(self, html: str) -> List[LinkedInPost]:
        soup = BeautifulSoup(html, "html.parser")
        posts, containers = [], []
        for selector in self.selectors['post_containers']:
            if found_containers := soup.select(selector):
                containers = found_containers
                logger.info(f"Found {len(containers)} posts using selector: '{selector}'"); break
        if not containers: logger.warning("No post containers found."); return posts
        for container in containers:
            try:
                data_urn = next((container.get(attr) for attr in ['data-urn', 'data-activity-urn'] if container.get(attr)), None)
                if not data_urn: continue
                if not (text := self.extract_element_text(container, self.selectors['text'])): continue
                author = self.extract_element_text(container, self.selectors['author']) or "Unknown Author"
                time_text = self.extract_element_text(container, self.selectors['time'])
                engagement_stats = self.extract_engagement_stats(container)
                link = f"https://www.linkedin.com/feed/update/{data_urn}"
                
                # Calculate sentiment analysis
                sentiment_score, sentiment_polarity = self.calculate_sentiment(text)
                
                # Calculate hashtag engagement score
                hashtag_engagement_score = self.calculate_hashtag_engagement_score(text, engagement_stats)
                
                posts.append(LinkedInPost(
                    author=author,
                    time=time_text or "Unknown",
                    text=text,
                    link=link,
                    engagement_stats=engagement_stats,
                    sentiment_score=sentiment_score,
                    sentiment_polarity=sentiment_polarity,
                    hashtag_engagement_score=hashtag_engagement_score
                ))
                if len(posts) >= self.config.max_posts: break
            except Exception as e:
                logger.warning(f"Error parsing a post: {e}"); continue
        logger.info(f"Successfully parsed {len(posts)} posts")
        return posts

    def save_results(self, posts: List[LinkedInPost]) -> Path:
        output_file = self.config.output_dir / f"linkedin_{self.config.hashtag}_posts.json"
        with open(output_file, "w", encoding="utf-8") as f: json.dump([asdict(p) for p in posts], f, indent=2)
        logger.info(f"Saved {len(posts)} posts to {output_file}")
        return output_file

    def upload_posts_to_supabase(self, posts: List[LinkedInPost]) -> bool:
        """Upload scraped posts to Supabase database"""
        if not self.config.supabase_url or not self.config.supabase_key:
            logger.warning("Supabase credentials not configured. Skipping upload.")
            return False
        
        try:
            # Remove quotes from URL and key if present
            url = self.config.supabase_url.strip('"')
            key = self.config.supabase_key.strip('"')
            
            # Initialize Supabase client with clean parameters
            supabase: Client = create_client(url, key)
            
            # Convert posts to dictionary format with metadata
            posts_data = []
            for post in posts:
                post_dict = asdict(post)
                # Add metadata
                post_dict['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                post_dict['hashtag'] = self.config.hashtag
                posts_data.append(post_dict)
            
            # Upload to Supabase table (assuming table name is 'linkedin_posts')
            response = supabase.table('linkedin_posts').insert(posts_data).execute()
            
            if response.data:
                logger.info(f"Successfully uploaded {len(posts_data)} posts to Supabase")
                return True
            else:
                logger.error("Failed to upload posts to Supabase - no data returned")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading posts to Supabase: {e}")
            return False

    def save_hashtags(self, hashtags: List[Dict[str, str]]) -> Path:
        output_file = self.config.output_dir / "linkedin_trending_hashtags.json"
        with open(output_file, "w", encoding="utf-8") as f: json.dump(hashtags, f, indent=2)
        logger.info(f"Saved {len(hashtags)} hashtags to {output_file}")
        return output_file

    def upload_hashtags_to_supabase(self, hashtags: List[Dict[str, str]]) -> bool:
        """Upload scraped hashtags to Supabase database"""
        if not self.config.supabase_url or not self.config.supabase_key:
            logger.warning("Supabase credentials not configured. Skipping upload.")
            return False
        
        try:
            # Remove quotes from URL and key if present
            url = self.config.supabase_url.strip('"')
            key = self.config.supabase_key.strip('"')
            
            # Initialize Supabase client with clean parameters
            supabase: Client = create_client(url, key)
            
            # Convert hashtags to dictionary format with metadata
            hashtags_data = []
            for hashtag in hashtags:
                hashtag_dict = hashtag.copy()
                # Clean hashtag name (remove tracking parameters)
                clean_name = hashtag_dict['name'].split('?')[0].strip()
                hashtag_dict['name'] = clean_name
                # Add metadata
                hashtag_dict['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                hashtag_dict['source'] = 'linkedin_feed'
                hashtags_data.append(hashtag_dict)
            
            # Upload to Supabase table (assuming table name is 'linkedin_hashtags')
            response = supabase.table('linkedin_hashtags').insert(hashtags_data).execute()
            
            if response.data:
                logger.info(f"Successfully uploaded {len(hashtags_data)} hashtags to Supabase")
                return True
            else:
                logger.error("Failed to upload hashtags to Supabase - no data returned")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading hashtags to Supabase: {e}")
            return False

    def calculate_sentiment(self, text: str) -> tuple[float, str]:
        """Calculate sentiment score and polarity using TextBlob"""
        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.1:
                polarity = "positive"
            elif sentiment_score < -0.1:
                polarity = "negative"
            else:
                polarity = "neutral"
                
            return sentiment_score, polarity
        except Exception as e:
            logger.warning(f"Error calculating sentiment: {e}")
            return 0.0, "neutral"

    def calculate_hashtag_engagement_score(self, text: str, engagement_stats: Dict[str, int]) -> float:
        """Calculate engagement score based on hashtags and engagement metrics"""
        try:
            # Extract hashtags from text
            hashtags = re.findall(r'#(\w+)', text, re.IGNORECASE)
            hashtag_count = len(hashtags)
            
            # Get engagement metrics
            likes = engagement_stats.get('likes', 0)
            comments = engagement_stats.get('comments', 0)
            
            # Calculate engagement score: (likes + comments*2) / max(hashtag_count, 1)
            # Comments weighted more as they indicate higher engagement
            total_engagement = likes + (comments * 2)
            hashtag_engagement_score = total_engagement / max(hashtag_count, 1)
            
            return round(hashtag_engagement_score, 2)
        except Exception as e:
            logger.warning(f"Error calculating hashtag engagement score: {e}")
            return 0.0

    def fetch_hashtag_page(self) -> str:
        """Fetch and scroll through a specific hashtag page to load posts"""
        url = f"https://www.linkedin.com/feed/hashtag/{self.config.hashtag}/"
        logger.info(f"Navigating to hashtag page: {url}")
        self.driver.get(url)
        self.rand_sleep(4, 6)
        
        last_height, scroll_count, stagnant_scrolls = 0, 0, 0
        while scroll_count < self.config.max_scrolls:
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {random.uniform(0.8, 1.0)});")
            self.rand_sleep(2.5, 4.0)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                stagnant_scrolls += 1
                if stagnant_scrolls >= 2: 
                    logger.info("No new content, stopping scroll.")
                    break
            else: 
                stagnant_scrolls = 0
            last_height = new_height
            scroll_count += 1
            logger.info(f"Scroll progress: {scroll_count}/{self.config.max_scrolls}")
        
        # Save debug HTML
        debug_file = self.config.output_dir / f"debug_{self.config.hashtag}_page.html"
        html_source = self.driver.page_source
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(html_source)
        logger.info(f"Saved debug HTML to {debug_file}")
        return html_source

    def cleanup(self):
        if self.driver:
            try: self.driver.quit(); logger.info("Driver cleanup completed")
            except OSError: pass
            except Exception as e: logger.warning(f"Driver cleanup warning: {e}")

    def run_hashtag_scraping(self) -> List[Dict[str, str]]:
        """Run hashtag scraping to get trending hashtags"""
        if not self.config.email or not self.config.password: raise ValueError("LinkedIn credentials not set")
        try:
            self.driver = self.build_driver(bool(self.config.proxy_host))
            self.driver.get("https://www.linkedin.com")
            login_successful = False
            if self.config.cookies_file.exists() and self.load_cookies():
                self.driver.get("https://www.linkedin.com/feed/")
                if "login" not in self.driver.current_url.lower() and "checkpoint" not in self.driver.current_url.lower():
                    logger.info("Cookie authentication successful")
                    login_successful = True
                else: logger.info("Cookie auth failed, trying credentials")
            if not login_successful:
                if self.login(): self.save_cookies(); login_successful = True
                else: raise Exception("Login failed")
            self.human_like_browsing()
            hashtags = self.fetch_trending_hashtags()
            if hashtags:
                self.save_hashtags(hashtags)
                self.upload_hashtags_to_supabase(hashtags)
                logger.info("Sample of trending hashtags:")
                for i, hashtag in enumerate(hashtags[:10]):
                    logger.info(f"[{i+1}] #{hashtag['name']} - {hashtag['followers']}")
            else: logger.warning("No hashtags were scraped")
            return hashtags
        except Exception as e:
            logger.error(f"Hashtag scraping failed: {e}"); raise
        finally:
            self.cleanup()

    def run(self) -> List[LinkedInPost]:
        if not self.config.email or not self.config.password: raise ValueError("LinkedIn credentials not set")
        try:
            self.driver = self.build_driver(bool(self.config.proxy_host))
            self.driver.get("https://www.linkedin.com")
            login_successful = False
            if self.config.cookies_file.exists() and self.load_cookies():
                self.driver.get("https://www.linkedin.com/feed/")
                if "login" not in self.driver.current_url.lower() and "checkpoint" not in self.driver.current_url.lower():
                    logger.info("Cookie authentication successful")
                    login_successful = True
                else: logger.info("Cookie auth failed, trying credentials")
            if not login_successful:
                if self.login(): self.save_cookies(); login_successful = True
                else: raise Exception("Login failed")
            self.human_like_browsing()
            html = self.fetch_hashtag_page()
            posts = self.parse_posts(html)
            if posts:
                self.save_results(posts)
                self.upload_posts_to_supabase(posts)
                logger.info("Sample of results:")
                for i, post in enumerate(posts[:3]):
                    logger.info(f"\n[{i+1}] Author: {post.author}\nEngagement: {post.engagement_stats}\nText: {post.text[:150]}...")
            else: logger.warning("No posts were scraped")
            return posts
        except Exception as e:
            logger.error(f"Scraping run failed: {e}"); raise
        finally:
            self.cleanup()

def main():
    import sys
    try:
        config = ScrapingConfig()
        scraper = LinkedInScraper(config)
        
        # Check if user wants to scrape hashtags
        if len(sys.argv) > 1 and sys.argv[1].lower() in ['hashtags', 'trending', '--hashtags']:
            hashtags = scraper.run_hashtag_scraping()
            print(f"\n🏷️ Success! Scraped {len(hashtags)} trending hashtags")
            if hashtags:
                print("📈 Top trending hashtags:")
                for i, hashtag in enumerate(hashtags[:10]):
                    print(f"  {i+1}. #{hashtag['name']} - {hashtag['followers']}")
        else:
            posts = scraper.run()
            print(f"\n🎉 Success! Scraped {len(posts)} posts for '#{config.hashtag}'")
            if posts:
                total_likes = sum(p.engagement_stats.get('likes', 0) for p in posts)
                total_comments = sum(p.engagement_stats.get('comments', 0) for p in posts)
                print(f"📊 Engagement: {total_likes} likes, {total_comments} comments.")
    except Exception:
        logger.error("Script execution failed."); return 1
    return 0

if __name__ == "__main__":
    exit(main())