import requests
import os
import sys
import time

def run_diagnostics(url):
    print("\n--- 🔍 DIAGNOSTICS START ---")
    print(f"Testing URL: {url}")
    
    # TEST 1: The "IFTTT Simulation" (No Headers)
    # This mimics exactly what IFTTT sees.
    print("\n1. Simulation: IFTTT (No Headers)")
    try:
        r = requests.get(url, timeout=5)
        print(f"   Status: {r.status_code}")
        print(f"   Headers: {r.headers}")
        content_type = r.headers.get('Content-Type', 'None')
        print(f"   👉 Content-Type: {content_type}")
        
        if 'image' not in content_type:
            print("   ❌ CRITICAL FAIL: Server is NOT returning an image to bots.")
            print("      (This explains why IFTTT fails while Python succeeds)")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")

    # TEST 2: The "Browser Simulation" (With Headers)
    # This confirms if the file exists for humans.
    print("\n2. Simulation: Real Browser (Chrome)")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        content_type = r.headers.get('Content-Type', 'None')
        print(f"   👉 Content-Type: {content_type}")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")
        
    print("--- 🔍 DIAGNOSTICS END ---\n")

def check_image_availability(url, timeout=300):
    print(f"Waiting for image to go live: {url}")
    start_time = time.time()
    
    # We use the browser header here to ensure WE can see it, 
    # even if IFTTT might struggle.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            content_type = response.headers.get("Content-Type", "")
            
            if response.status_code == 200 and content_type.startswith("image/"):
                print(f"✅ Image is live! (Type: {content_type})")
                return True
            else:
                print(f"⏳ Waiting... (Status: {response.status_code}, Type: {content_type})")

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

    # 1. RUN DIAGNOSTICS FIRST
    run_diagnostics(image_url)

    # 2. WAIT FOR AVAILABILITY
    if not check_image_availability(image_url):
        print("Aborting tweet.")
        sys.exit(1)

    # 3. SEND TO IFTTT
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
