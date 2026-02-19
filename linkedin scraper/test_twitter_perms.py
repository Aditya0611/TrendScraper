import tweepy
from config import Config

def test_twitter():
    print("Testing Twitter Credentials...")
    try:
        # Try V1 Authentication for verification
        auth = tweepy.OAuth1UserHandler(
            Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET,
            Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        user = api.verify_credentials()
        print(f"Authentication successful! Authenticated as: @{user.screen_name}")
        
        # Check permissions by attempting a dry-run or just seeing what error comes back
        print("Self-check passed. Attempting V2 tweet (real)...")
        client = tweepy.Client(
            consumer_key=Config.TWITTER_API_KEY,
            consumer_secret=Config.TWITTER_API_SECRET,
            access_token=Config.TWITTER_ACCESS_TOKEN,
            access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text="Test tweet from automation agent.")
        print(f"Post successful! Tweet ID: {response.data['id']}")
        
    except tweepy.TweepyException as e:
        print(f"Tweepy Error (Twitter API Error): {e}")
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_twitter()
