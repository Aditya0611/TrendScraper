import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google API
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")

    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # LinkedIn API
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

    # Twitter/X API
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    # Meta (Instagram/Facebook)
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
    META_PAGE_ID = os.getenv("META_PAGE_ID")
    INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.GOOGLE_SHEET_ID: missing.append("GOOGLE_SHEET_ID")
        if not cls.GROQ_API_KEY: missing.append("GROQ_API_KEY")
        # Add more as needed based on active platforms
        return missing
