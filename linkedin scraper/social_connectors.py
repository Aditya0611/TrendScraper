import requests
import tweepy
from config import Config

class SocialConnector:
    def post(self, content):
        raise NotImplementedError("Subclasses must implement post()")

class LinkedInConnector(SocialConnector):
    def post(self, content):
        if not Config.LINKEDIN_ACCESS_TOKEN:
            return False, "Missing LinkedIn Token"
        
        # LinkedIn API v2 (Simplified post)
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {Config.LINKEDIN_ACCESS_TOKEN}",
            "LinkedIn-Version": "202511",  # Updated to a confirmed active version
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        
        # Note: LinkedIn requires author URN. For this automation, we assume it's linked to the token owner.
        # This part often requires a precursor call to /me to get the URN.
        try:
            # First, get author URN (using /v2/userinfo for OpenID Connect)
            me_res = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if me_res.status_code != 200:
                return False, f"LinkedIn userinfo error ({me_res.status_code}): {me_res.text}"
            
            user_info = me_res.json()
            author_urn = f"urn:li:person:{user_info['sub']}"
            
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code in [201, 200]:
                return True, "Posted"
            return False, f"Error: {res.text}"
        except Exception as e:
            return False, str(e)

class TwitterConnector(SocialConnector):
    def post(self, content):
        if not all([Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET, 
                    Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_TOKEN_SECRET]):
            return False, "Missing Twitter Credentials"
        
        try:
            client = tweepy.Client(
                consumer_key=Config.TWITTER_API_KEY,
                consumer_secret=Config.TWITTER_API_SECRET,
                access_token=Config.TWITTER_ACCESS_TOKEN,
                access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET
            )
            response = client.create_tweet(text=content)
            return True, "Posted"
        except Exception as e:
            return False, str(e)

class MetaConnector(SocialConnector):
    """Instagram and Facebook Connector using Graph API."""
    def post_facebook(self, content):
        if not Config.META_PAGE_ID or not Config.META_ACCESS_TOKEN:
            return False, "Missing FB Credentials"
        
        url = f"https://graph.facebook.com/v21.0/{Config.META_PAGE_ID}/feed"
        params = {
            "message": content,
            "access_token": Config.META_ACCESS_TOKEN
        }
        try:
            res = requests.post(url, params=params)
            if res.status_code == 200:
                return True, "Posted to FB"
            return False, f"FB Error: {res.text}"
        except Exception as e:
            return False, str(e)

    def post_instagram(self, content):
        if not Config.INSTAGRAM_BUSINESS_ID or not Config.META_ACCESS_TOKEN:
            return False, "Missing IG Credentials"
        
        # Step 1: Create Container
        # Step 2: Publish Container (Simplified logic)
        return False, "Instagram direct text post requires media via Graph API."
