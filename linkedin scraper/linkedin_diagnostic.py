import requests
import json
import os
from dotenv import load_dotenv

def test_linkedin():
    load_dotenv()
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not token:
        print("Error: LINKEDIN_ACCESS_TOKEN not found in .env")
        return

    endpoints = [
        ("v2/userinfo (No Version)", "https://api.linkedin.com/v2/userinfo", False, False),
        ("v2/userinfo (LinkedIn-Version: 202511)", "https://api.linkedin.com/v2/userinfo", "LinkedIn-Version", "202511"),
        ("v2/userinfo (X-LinkedIn-Version: 202511)", "https://api.linkedin.com/v2/userinfo", "X-LinkedIn-Version", "202511"),
        ("rest/me (LinkedIn-Version: 202511)", "https://api.linkedin.com/rest/me", "LinkedIn-Version", "202511"),
        ("v2/me (No Version)", "https://api.linkedin.com/v2/me", False, False),
    ]

    print(f"Testing LinkedIn Token: {token[:10]}...")
    
    for name, url, header_name, version in endpoints:
        print(f"\n--- Testing {name} ---")
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        if header_name and version:
            headers[header_name] = version
            
        try:
            res = requests.get(url, headers=headers)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                print("Success!")
                print(json.dumps(res.json(), indent=2))
            else:
                print(f"Error: {res.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_linkedin()
