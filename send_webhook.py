import requests
import os
import sys

def send_to_ifttt():
    # 1. Get Settings
    key = os.environ.get("IFTTT_KEY")
    tweet_text = os.environ.get("TWEET_TEXT")
    event_name = "post_tweet"

    if not key:
        print("Error: IFTTT Key is missing (Check GitHub Secrets).")
        sys.exit(1)

    if not tweet_text:
        print("Error: Tweet text is missing (Check build.py output).")
        sys.exit(1)

    # 2. Prepare the Payload
    # IFTTT takes the tweet text as "value1"
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{key}"
    payload = {"value1": tweet_text}

    print(f"Sending to IFTTT... (Length: {len(tweet_text)})")

    # 3. Fire the Request
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("SUCCESS: Webhook sent to IFTTT. The tweet should appear shortly.")
        else:
            print(f"ERROR: IFTTT rejected the request. Code: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Network Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_to_ifttt()
