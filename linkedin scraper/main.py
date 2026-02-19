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
from dataclasses import dataclass
import argparse

# Selenium (undetected) and Human-like Actions
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Optional dependencies
try:
    from supabase import create_client, Client
    SUPABASE_ENABLED = True
except ImportError:
    SUPABASE_ENABLED = False
    print("⚠️  Supabase not installed. Database features disabled.")

try:
    from textblob import TextBlob
    TEXTBLOB_ENABLED = True
except ImportError:
    TEXTBLOB_ENABLED = False
    print("⚠️  TextBlob not installed. Sentiment analysis disabled.")

# Enhanced Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
load_dotenv()

@dataclass
class ScrapingConfig:
    """Enhanced configuration with validation and defaults."""
    email: str = os.getenv("LINKEDIN_EMAIL", "").strip()
    password: str = os.getenv("LINKEDIN_PASSWORD", "").strip()
    cookies_file: Path = Path("linkedin_cookies.json")
    output_dir: Path = Path("output")
    supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
    supabase_key: str = os.getenv("SUPABASE_KEY", "").strip()
    max_scroll_iterations: int = 15
    scroll_pause_time: tuple = (3, 7)
    request_timeout: int = 90
    max_retries: int = 3

    def __post_init__(self):
        self.output_dir.mkdir(exist_ok=True)
        self._validate_config()

    def _validate_config(self):
        if not self.email or not self.password:
            logger.warning("⚠️  LinkedIn credentials not found in .env file. Manual login will be required.")
        if self.supabase_url and not self.supabase_key:
            logger.warning("⚠️  Supabase URL provided but key missing")

class LinkedInScraper:
    """
    Definitive LinkedIn scraper with a "warm-up" routine to trigger lazy-loaded content.
    """
    POST_CONTAINER_SELECTORS = ["div[data-urn*=':share:']", "div[data-urn*=':activity:']"]
    TEXT_CONTENT_SELECTORS = [".update-components-text", "[class*='commentary']"]

    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.driver = None
        self.session_active = False

    def _rand_sleep(self, min_time: float = 2.5, max_time: float = 5.0):
        time.sleep(random.uniform(min_time, max_time))

    def _human_type(self, element, text: str):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        self._rand_sleep(0.5, 1)

    def _build_driver(self, headless: bool = True, retries: int = 3) -> uc.Chrome:
        for attempt in range(retries):
            try:
                options = uc.ChromeOptions()
                if headless: options.add_argument("--headless=new")
                options.add_argument("--start-maximized")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument(f"--user-agent={UserAgent().random}")
                
                logger.info("🔧 Forcing ChromeDriver version 139 to match your installed browser.")
                driver = uc.Chrome(options=options, version_main=139)
                
                driver.set_page_load_timeout(self.config.request_timeout)
                driver.implicitly_wait(10)
                logger.info(f"✅ Chrome driver created successfully (attempt {attempt + 1})")
                return driver
            except Exception as e:
                logger.warning(f"⚠️  Driver creation attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1: raise
                time.sleep(5)

    def _save_cookies(self) -> bool:
        try:
            cookies = self.driver.get_cookies()
            if not cookies: logger.warning("⚠️  No cookies to save"); return False
            with open(self.config.cookies_file, "w", encoding="utf-8") as f: json.dump(cookies, f, indent=2)
            logger.info(f"✅ Saved {len(cookies)} cookies to {self.config.cookies_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save cookies: {e}"); return False

    def _load_cookies(self) -> bool:
        if not self.config.cookies_file.exists(): return False
        try:
            with open(self.config.cookies_file, "r", encoding="utf-8") as f: cookies = json.load(f)
            if not cookies: return False
            self.driver.get("https://www.linkedin.com")
            for cookie in cookies: self.driver.add_cookie(cookie)
            logger.info(f"✅ Loaded {len(cookies)} cookies from file.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {e}"); return False

    def _check_login_status(self) -> bool:
        """Checks for elements that only appear when logged in. More robust version."""
        try:
            self._wait_for_page_load(15)
            login_selectors = [
                ".global-nav__me-photo",
                ".feed-identity-module",
                "#global-nav-search",
                "[data-test-id='global-nav-me-dropdown-trigger']"
            ]
            combined_selector = ", ".join(login_selectors)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, combined_selector))
            )
            logger.info("✅ Login status confirmed: Found a valid session element.")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.warning("❌ Login status check failed: Could not find any valid session elements.")
            return False

    def _wait_for_page_load(self, timeout: int = 30):
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            logger.warning("⚠️  Page load timed out.")

    def _login_with_credentials(self) -> bool:
        logger.info("🔐 Attempting automated login with credentials...")
        if not self.config.email or not self.config.password:
            logger.error("❌ LinkedIn credentials not configured in .env file"); return False

        self.driver = self._build_driver(headless=False)
        try:
            self.driver.get("https://www.linkedin.com/login"); self._wait_for_page_load()
            wait = WebDriverWait(self.driver, 20)
            
            logger.info("🤖 Filling in credentials...")
            email_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
            self._human_type(email_field, self.config.email)
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
            self._human_type(password_field, self.config.password)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            
            logger.info("⏳ Waiting for page transition after login...")
            self._rand_sleep(5, 8) 
            
            # --- NEW, MORE ROBUST CHECKING LOGIC ---
            current_url = self.driver.current_url.lower()
            if "checkpoint" in current_url or "challenge" in current_url:
                print("\n" + "="*70)
                print("🚨 SECURITY CHALLENGE DETECTED")
                print("Your account requires verification (e.g., CAPTCHA, 2FA, email code).")
                print("Please complete the steps in the browser window to continue.")
                print("="*70)
                input("⏳ Press Enter here ONLY after you have landed on the main LinkedIn feed...")
                self.driver.get("https://www.linkedin.com/feed/")

            if "/feed/" not in self.driver.current_url.lower():
                 logger.info(f"Redirected to unexpected page: {self.driver.current_url}. Navigating to feed manually.")
                 self.driver.get("https://www.linkedin.com/feed/")

            if self._check_login_status():
                logger.info("✅ Automated login successful!")
                self.session_active = True
                return True
            else:
                logger.error(f"❌ Login verification failed on page: {self.driver.current_url}. Please check credentials and solve any CAPTCHAs.")
                return False

        except Exception as e:
            logger.error(f"❌ An error occurred during login: {e}", exc_info=True); return False

    def _initialize_session(self) -> bool:
        logger.info("🚀 Initializing LinkedIn session...")
        if self._try_cookie_authentication(): return True
        logger.info("🔄 Cookie auth failed, trying credential login...")
        self.cleanup()
        if self._login_with_credentials():
            if self._save_cookies(): logger.info("💾 New session cookies saved.")
            return True
        logger.error("❌ All authentication methods failed."); return False

    def _try_cookie_authentication(self) -> bool:
        if not self.config.cookies_file.exists(): return False
        logger.info("🍪 Attempting cookie-based authentication...")
        self.driver = self._build_driver(headless=True)
        try:
            if not self._load_cookies(): return False
            self.driver.get("https://www.linkedin.com/feed/")
            if self._check_login_status():
                logger.info("✅ Cookie authentication successful!")
                self.session_active = True
                return True
            else:
                logger.warning("❌ Cookies seem to be invalid or expired.")
                self.config.cookies_file.unlink()
                logger.info("🗑️ Removed expired cookies file.")
                return False
        except Exception as e:
            logger.error(f"❌ An error occurred during cookie authentication: {e}"); return False

    def fetch_trending_hashtags(self) -> List[Dict]:
        """Scrapes hashtags with an improved warm-up and updated selectors."""
        try:
            logger.info("🎯 Starting hashtag extraction...")
            if not self.session_active: logger.error("❌ No active session."); return []

            logger.info("🔥 Performing page warm-up...")
            self.driver.get("https://www.linkedin.com/feed/")
            self._rand_sleep(4, 7)
            self.driver.execute_script("window.scrollBy(0, 500);")
            self._rand_sleep(3, 5)

            try:
                post_selector_css = ", ".join(self.POST_CONTAINER_SELECTORS)
                WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, post_selector_css)))
                logger.info("✅ Feed content loaded successfully after warm-up!")
            except TimeoutException:
                logger.warning("⚠️ Feed content did not load after warm-up. Attempting to scroll anyway.")

            self._scroll_feed()
            html_source = self.driver.page_source
            debug_file = self.config.output_dir / f"debug_feed_{int(time.time())}.html"
            with open(debug_file, "w", encoding="utf-8") as f: f.write(html_source)
            logger.info(f"💾 Saved feed HTML to {debug_file}")

            return self.parse_hashtags(html_source)
        except Exception as e:
            logger.error(f"❌ Fatal error in hashtag extraction: {e}", exc_info=True); return []

    def _scroll_feed(self):
        logger.info("📜 Starting intelligent feed scrolling...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for i in range(self.config.max_scroll_iterations):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight - {random.randint(0, 200)});")
            logger.info(f"📜 Feed scroll {i + 1}/{self.config.max_scroll_iterations}")
            self._rand_sleep(*self.config.scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("✅ Reached end of feed or no new content loaded.")
                break
            last_height = new_height
        logger.info("✅ Completed scrolling.")

    def parse_hashtags(self, html: str) -> List[Dict]:
        logger.info("🔍 Parsing hashtags from extracted HTML...")
        soup = BeautifulSoup(html, "html.parser")
        hashtag_counts, hashtag_contexts, hashtag_original_case = {}, {}, {}
        hashtag_pattern = r'#([A-Za-z0-9_]+)'
        post_selector_css = ", ".join(self.POST_CONTAINER_SELECTORS)
        posts = soup.select(post_selector_css)
        logger.info(f"📊 Found {len(posts)} potential post containers.")
        if not posts: logger.warning("⚠️ No post containers found."); return []

        text_content_selector_css = ", ".join(self.TEXT_CONTENT_SELECTORS)
        for post in posts:
            text_element = post.select_one(text_content_selector_css)
            if not text_element: continue
            text_content = text_element.get_text(" ", strip=True)
            if not text_content: continue
            for tag in re.findall(hashtag_pattern, text_content):
                if not (2 <= len(tag) <= 50): continue
                tag_lower = tag.lower()
                hashtag_counts[tag_lower] = hashtag_counts.get(tag_lower, 0) + 1
                if tag_lower not in hashtag_contexts or len(hashtag_contexts.get(tag_lower, [])) < 5:
                    hashtag_contexts.setdefault(tag_lower, []).append(text_content[:500])
                if tag_lower not in hashtag_original_case:
                    hashtag_original_case[tag_lower] = tag
        if not hashtag_counts: logger.warning("❌ Could not find any hashtags in the posts."); return []

        processed_hashtags = []
        for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True):
            contexts = hashtag_contexts.get(tag, [])[:3]
            combined_context = ' | '.join(contexts)
            sentiment_score, sentiment_polarity = self.calculate_sentiment(combined_context)
            original_case = hashtag_original_case.get(tag, tag)
            processed_hashtags.append({
                'name': tag, 'original_case': original_case,
                'url': f"https://www.linkedin.com/feed/hashtag/{tag}/", 'mentions': count,
                'sentiment_score': round(sentiment_score, 3), 'sentiment_polarity': sentiment_polarity,
                'context_sample': combined_context[:400]
            })
        logger.info(f"✅ Successfully extracted {len(processed_hashtags)} unique hashtags.")
        return processed_hashtags

    def calculate_sentiment(self, text: str) -> tuple[float, str]:
        if not text or not TEXTBLOB_ENABLED: return 0.0, "neutral"
        try:
            blob = TextBlob(text)
            score = blob.sentiment.polarity
            if score > 0.1: return score, "positive"
            if score < -0.1: return score, "negative"
            return score, "neutral"
        except Exception: return 0.0, "neutral"

    def upload_to_supabase(self, data: List[Dict]) -> bool:
        if not all([SUPABASE_ENABLED, self.config.supabase_url, self.config.supabase_key, data]):
            logger.info("ℹ️  Supabase upload skipped."); return False
        try:
            logger.info(f"☁️  Uploading {len(data)} records to Supabase...")
            supabase: Client = create_client(self.config.supabase_url, self.config.supabase_key)
            batch_id = f"batch_{int(time.time())}"
            enriched_data = [{**item, 'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'batch_id': batch_id} for item in data]
            supabase.table('linkedin_hashtags').insert(enriched_data).execute()
            logger.info(f"✅ Successfully uploaded {len(enriched_data)} records to Supabase.")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase upload error: {e}"); return False

    def generate_report(self, hashtags: List[Dict]) -> str:
        if not hashtags: return "📄 No hashtags were extracted."
        report = [f"🏷️  LinkedIn Hashtags Report ({time.strftime('%Y-%m-%d %H:%M:%S')})", "="*60, f"📊 Unique hashtags found: {len(hashtags)}", "", "🔥 Top 15 Trending Hashtags:", "-"*40]
        for i, tag in enumerate(hashtags[:15], 1):
            emoji = '😊' if tag['sentiment_polarity'] == 'positive' else '😞' if tag['sentiment_polarity'] == 'negative' else '😐'
            report.append(f"{i:2d}. #{tag['original_case']} ({tag['mentions']} mentions) {emoji}")
        return "\n".join(report)

    def cleanup(self):
        if self.driver:
            try: self.driver.quit()
            except Exception: pass
            finally: self.driver = None; self.session_active = False

    def run_hashtag_scraping(self) -> List[Dict]:
        start_time = time.time()
        try:
            print("\n🎯 LinkedIn Hashtag Scraper v2.0\n" + "="*50)
            print("🔐 Step 1: Authenticating with LinkedIn...")
            if not self._initialize_session(): raise Exception("Failed to establish a session.")
            print("✅ Authentication successful!")
            print("\n🎯 Step 2: Extracting hashtags from feed...")
            hashtags = self.fetch_trending_hashtags()
            if not hashtags: print("❌ No hashtags found."); return []
            print(f"✅ Found {len(hashtags)} unique hashtags!")
            print("\n💾 Step 3: Saving results...")
            output_file = self.config.output_dir / f"linkedin_hashtags_{int(time.time())}.json"
            with open(output_file, "w", encoding="utf-8") as f: json.dump(hashtags, f, indent=2)
            print(f"💾 Results saved to: {output_file}")
            self.upload_to_supabase(hashtags)
            print(f"\n{self.generate_report(hashtags)}")
            print("\n" + "="*60 + f"\n⏱️  Total time: {time.time() - start_time:.1f}s\n🎉 Done!\n" + "="*60)
            return hashtags
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Hashtag Scraper v2.0')
    parser.add_argument('--get-cookies', action='store_true', help='Run interactive mode to save a session cookie file.')
    parser.add_argument('--max-scrolls', type=int, default=15, help='Set the max number of scroll actions.')
    args = parser.parse_args()
    scraper = None
    try:
        config = ScrapingConfig(max_scroll_iterations=args.max_scrolls)
        scraper = LinkedInScraper(config)
        if args.get_cookies:
            # Simplified manual cookie generation
            scraper.run_manual_cookie_generator()
        else:
            if not config.cookies_file.exists() and not (config.email and config.password):
                print("\n⚠️  Credentials or cookies not found! Run with `--get-cookies` to generate a session file first.")
                return 1
            scraper.run_hashtag_scraping()
    except Exception:
        logger.critical("💥 FATAL ERROR: The script encountered an unrecoverable error.")
        return 1
    finally:
        if scraper: scraper.cleanup()
    return 0

if __name__ == "__main__":
    exit(main())