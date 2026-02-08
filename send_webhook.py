import requests
import os
import sys
import time

def check_image_availability(url, timeout=300):
    print(f"Waiting for image to go live: {url}")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, stream=True, timeout=10)
            content_type = response.headers.get("Content-Type", "")
            
            if response.status_code == 200 and content_type.startswith("image/"):
                print(f"✅ Image is live ({content_type})")
                return True
            else:
                print(f"⏳ Not ready yet (status={response.status_code}, type={content_type})")

        except Exception as e:
            print(f"⚠️ Network check failed: {e}")

        time.sleep(10)

    print("❌ Timeout: Image did not appear within 5 minutes.")
    return False

def send_to_ifttt():
    key = os.environ.get("IFTTT_KEY")
    tweet_text = os.environ.get("TWEET_TEXT")
    image_url = os.environ.get("IMAGE_URL")

    if not key:
        print("Error: IFTTT Key is missing.")
        sys.exit(1)

    if not tweet_text:
        print("Error: Tweet text is missing.")
        sys.exit(1)
        
    if not image_url:
        print("Error: Image URL is missing.")
        sys.exit(1)

    # --- Run the Smart Check ---
    if not check_image_availability(image_url):
        print("Aborting tweet to prevent error.")
        sys.exit(1)
    # ---------------------------

    url = f"https://maker.ifttt.com/trigger/post_tweet/with/key/{key}"
    payload = {
        "value1": tweet_text,
        "value2": image_url
    }

    print(f"Sending to IFTTT...")
    print(f"Text: {tweet_text}")
    print(f"Image: {image_url}")

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
