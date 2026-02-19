
import os
import json
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client

load_dotenv()

def fetch_samples():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("Error: Supabase credentials missing.")
        return

    print(f"Connecting to Supabase: {url}")
    supabase = create_client(url, key)
    
    try:
        response = supabase.table('facebook').select('*').order('scraped_at', desc=True).limit(5).execute()
        data = response.data
        
        if not data:
            print("No data found in 'facebook' table.")
            return

        print(f"\nFound {len(data)} rows. Here are the most recent 5:")
        print("-" * 80)
        
        # Display as a formatted JSON or simpler text
        for row in data:
            print(f"ID: {row.get('id')}")
            print(f"Hashtag: {row.get('topic_hashtag')}")
            print(f"Engagement Score: {row.get('engagement_score')}")
            print(f"Scraped At: {row.get('scraped_at')}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_samples()
