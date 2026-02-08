import requests
import os
import sys
import time

def check_image_availability(url, timeout=300):
    """
    Polls the image URL to see if it is live.
    Uses Browser Headers to avoid false negatives.
    """
    print(f"Waiting for image to go live: {url}")
    start_time = time.time()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while time.time() - start_time < timeout:
        try:
            # Use stream=True to check headers quickly
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            content_type = response.headers.get("Content-Type", "")
            
            # Success Condition: 200 OK AND it's an image
            if response.status_code == 200 and content_type.startswith("image/"):
                print(f"✅ Image is live! (Type: {content_type})")
                return True
            else:
                print(f"⏳ Waiting... (Status: {response.status_code})")

        except Exception as e:
            print(f"⚠️ Network check failed: {e}")
            
        time.sleep(10)
        
    print("❌ Timeout: Image did not appear within 5 minutes.")
    return False

def send_to_ifttt():
    key = os.environ.get("IFTTT_KEY")
    tweet_text = os.environ.get("TWEET_TEXT")
    image_url = os.environ.get("IMAGE_URL")

    if not key or not tweet_text or not image_url:
        print("Error: Missing environment variables.")
        sys.exit(1)

    # 1. WAIT FOR AVAILABILITY
    if not check_image_availability(image_url):
        print("Aborting tweet because image check failed.")
        sys.exit(1)

    # 2. SEND TO IFTTT
    url = f"https://maker.ifttt.com/trigger/post_tweet/with/key/{key}"
    payload = {
        "value1": tweet_text,
        "value2": image_url
    }

    print(f"Sending to IFTTT...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("SUCCESS: Webhook sent.")
        else:
            print(f"ERROR: IFTTT rejected request: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Network Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_to_ifttt()
