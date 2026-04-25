import requests
import json
from config.config import cfg

def debug_api():
    url = f"https://{cfg.HOST}/matches/v1/live"
    headers = {
        "x-rapidapi-key": cfg.RAPID_KEY,
        "x-rapidapi-host": cfg.HOST
    }
    
    print(f"Testing URL: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        print(f"Response Headers: {r.headers}")
        print(f"Raw Response Body (first 500 chars):")
        print(r.text[:500])
        
        try:
            data = r.json()
            print("Successfully parsed JSON")
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    debug_api()
