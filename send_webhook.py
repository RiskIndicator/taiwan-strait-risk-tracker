import requests
import os
import sys

def send_to_ifttt():
    key = os.environ.get("IFTTT_KEY")
    tweet_text = os.environ.get("TWEET_TEXT")
    image_url = os.environ.get("IMAGE_URL") # Received directly from build.py

    if not key:
        print("Error: IFTTT Key is missing.")
        sys.exit(1)

    if not tweet_text:
        print("Error: Tweet text is missing.")
        sys.exit(1)
        
    if not image_url:
        print("Error: Image URL is missing.")
        sys.exit(1)

    # IFTTT "Post a tweet with image" action
    # Value1 = Text
    # Value2 = Clean Image URL (e.g. .../card_2026-02-08.png)
    url = f"https://maker.ifttt.com/trigger/post_tweet/with/key/{key}"
    payload = {
        "value1": tweet_text,
        "value2": image_url
    }

    print(f"Sending to IFTTT...")
    print(f"Text: {tweet_text}")
    print(f"Image Source: {image_url}")

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("SUCCESS: Webhook sent.")
        else:
            print(f"ERROR: IFTTT rejected the request. Code: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Network Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_to_ifttt()
