import requests
import os
import sys
import time

def send_to_ifttt():
    # 1. Get Settings
    key = os.environ.get("IFTTT_KEY")
    tweet_text = os.environ.get("TWEET_TEXT")
    event_name = "post_tweet"
    
    # We construct the image URL manually.
    # We add a timestamp (?v=...) to force IFTTT to download the new version every day.
    image_url = f"https://taiwanstraittracker.com/public/twitter_card.png?v={int(time.time())}"

    if not key:
        print("Error: IFTTT Key is missing.")
        sys.exit(1)

    if not tweet_text:
        print("Error: Tweet text is missing.")
        sys.exit(1)

    # 2. Prepare the Payload
    # Value1 = The text of the tweet
    # Value2 = The URL of the image for IFTTT to download and upload to X
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{key}"
    payload = {
        "value1": tweet_text,
        "value2": image_url
    }

    print(f"Sending to IFTTT...")
    print(f"Text: {tweet_text}")
    print(f"Image Source: {image_url}")

    # 3. Fire the Request
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("SUCCESS: Webhook sent. IFTTT will now upload the image to X.")
        else:
            print(f"ERROR: IFTTT rejected the request. Code: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Network Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_to_ifttt()
