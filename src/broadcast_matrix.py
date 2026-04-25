import tweepy
import requests
import os
import sys
import json
import re
import time
from google import genai 
from atproto import Client 

# ==========================================
# PLATFORM POSTING FUNCTIONS
# ==========================================

def post_to_twitter(main_msg, reply_msg, keys):
    try:
        print("▶️ Initiating X (Twitter) Broadcast...")
        client = tweepy.Client(
            consumer_key=keys['api_key'],
            consumer_secret=keys['api_secret'],
            access_token=keys['access_token'],
            access_token_secret=keys['access_secret']
        )
        main_response = client.create_tweet(text=main_msg, user_auth=True)
        main_tweet_id = main_response.data['id']
        print(f"✅ X Main Post Live! ID: {main_tweet_id}")

        reply_response = client.create_tweet(
            text=reply_msg, 
            in_reply_to_tweet_id=main_tweet_id, 
            user_auth=True
        )
        print(f"✅ X Thread Linked! ID: {reply_response.data['id']}")
    except Exception as e:
        print(f"❌ X (Twitter) Broadcast Failed: {e}")

def post_to_bluesky(message, handle, app_password):
    try:
        print("▶️ Initiating Bluesky Broadcast...")
        client = Client()
        client.login(handle, app_password)
        post = client.send_post(message)
        print(f"✅ Bluesky Broadcast Live! URI: {post.uri}")
    except Exception as e:
        print(f"❌ Bluesky Broadcast Failed: {e}")

def post_to_telegram(message, token, chat_id):
    try:
        print("▶️ Initiating Telegram Broadcast...")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Telegram Broadcast Live!")
    except Exception as e:
        print(f"❌ Telegram Broadcast Failed: {e}")

def post_to_linkedin(message, token, author_urn):
    try:
        print("▶️ Initiating LinkedIn Broadcast...")
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        payload = {
            "author": f"urn:li:person:{author_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": message},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ LinkedIn Broadcast Live!")
    except Exception as e:
        print(f"❌ LinkedIn Broadcast Failed: {e}")

# ==========================================
# MAIN ORCHESTRATOR
# ==========================================

def main():
    # 1. Pull API Secrets
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    twitter_keys = {
        'api_key': os.getenv('TWITTER_API_KEY'),
        'api_secret': os.getenv('TWITTER_API_SECRET'),
        'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
        'access_secret': os.getenv('TWITTER_ACCESS_SECRET')
    }
    
    bluesky_handle = os.getenv('BLUESKY_HANDLE')
    bluesky_password = os.getenv('BLUESKY_PASSWORD')

    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    
    linkedin_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    linkedin_urn = os.getenv('LINKEDIN_PERSON_URN') 

    if not gemini_key:
        print("❌ Missing GEMINI_API_KEY. System halting.")
        sys.exit(1)

    ai_client = genai.Client(api_key=gemini_key)

    # 2. Load Telemetry & The Intelligence Backlog
    print("Loading GSN Orchestrator Telemetry and the Intelligence Backlog...")
    try:
        with open('data/agentic_briefing.json', 'r', encoding='utf-8') as f:
            briefing = json.load(f)
        with open('data/active_alerts.json', 'r', encoding='utf-8') as f:
            alerts_data = json.load(f)
            
        with open('data/whisper_ledger.json', 'r', encoding='utf-8') as f:
            ledger_data = json.load(f)
            
        exec_summary = briefing.get('executive_summary', 'Nominal variance.')
        alerts = alerts_data.get('alerts', [])
        alert_text = "\n".join([f"- {a['severity']} [{a['type']}]: {a['headline']}" for a in alerts]) if alerts else "No critical anomalies."
        
        unpublished_whispers = [w for w in ledger_data.get('whispers', []) if w.get('status') == 'UNPUBLISHED']
        
        whisper_text = ""
        for idx, w in enumerate(unpublished_whispers):
            whisper_text += f"ID: {idx}\nKOL: {w['author']}\nContext: {w['snippet']}\n\n"
            
        if not whisper_text:
            whisper_text = "No new KOL insights available today."
            
    except Exception as e:
        print(f"⚠️ Telemetry load error: {e}")
        exec_summary, alert_text, whisper_text, alerts, unpublished_whispers, ledger_data = "Baseline nominal.", "None.", "None.", [], [], {"whispers": []}

    is_alert_day = len(alerts) > 0

    # 3. Construct Divergence Engine Prompt
    prompt = f"""
    You are the Lead Macro-Intelligence Analyst for the Global Shift Network (GSN).
    Draft a concise, clinical social media broadcast. 
    Strict Rules: Use Australian English spelling. Do NOT use en-dashes or em-dashes; use standard hyphens or commas.

    Current GSN Telemetry:
    {exec_summary}

    Active Node Alerts:
    {alert_text}

    Unpublished Context Nodes:
    {whisper_text}

    Instructions:
    Select ONE context node to base today's narrative on. Look for contrarian alpha.
    You MUST begin your response with the exact string [ID: X] where X is the integer ID of the context node you selected.
    Following the ID tag, provide the broadcast copy. Do not include hashtags.
    """

    # 4. Generate Bifurcated Copy via Gemini with Exponential Backoff
    max_retries = 3
    raw_ai_message = ""
    
    for attempt in range(max_retries):
        try:
            response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            raw_ai_message = response.text.strip()
            break  # Exit the retry loop on success
        except Exception as api_err:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5  # Waits 5 seconds, then 10 seconds
                print(f"⚠️ Gemini API Overloaded (503). Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ AI Generation Failed after {max_retries} attempts: {api_err}")
                sys.exit(1)
    
    # 4.5 THE BURN PROTOCOL: Robust ID Detection and Removal
    match = re.search(r'\[ID:\s*(\d+)\]', raw_ai_message)
    
    if match:
        chosen_id = int(match.group(1))
        # Strip the exact tag out of the final message for broadcast
        ai_message = re.sub(r'\[ID:\s*\d+\]\s*', '', raw_ai_message).strip()
        
        # Find the whisper in the ledger and burn it
        if 0 <= chosen_id < len(unpublished_whispers):
            chosen_whisper = unpublished_whispers[chosen_id]
            print(f"🔥 Burning Whisper: '{chosen_whisper['title']}' by {chosen_whisper['author']}")
            
            # Update the main ledger data
            for w in ledger_data['whispers']:
                if w['title'] == chosen_whisper['title'] and w['author'] == chosen_whisper['author']:
                    w['status'] = 'PUBLISHED'
                    break
                    
            # Save the ledger back to disk
            with open('data/whisper_ledger.json', 'w', encoding='utf-8') as f:
                json.dump(ledger_data, f, indent=4)
    else:
        ai_message = raw_ai_message
        if not is_alert_day:
            print("⚠️ Could not detect Whisper ID in AI response. No whispers burned today.")

    # ==========================================
    # 5. CONTENT ANALYSIS & ROUTING (SMART LINKER)
    # ==========================================
    report_url = "https://taiwanstraittracker.com"
    politics_url = "https://whatsmypolitics.com"
    
    # The is_political check occurs safely here, after ai_message is fully defined.
    political_keywords = ['policy', 'government', 'inequality', 'wealth', 'tax', 'labor', 'politics', 'gary', 'stevenson']
    is_political = any(keyword in ai_message.lower() for keyword in political_keywords)

    if is_political and not is_alert_day:
        print("🏛️ Political context detected. Injecting whatsmypolitics.com cross-promotion.")
        twitter_reply = f"Where do you stand on the economic divide? Test your alignment at {politics_url}\n\nDive into the hard data on the GSN Terminal: {report_url}"
        unified_full_message = f"{ai_message}\n\nWhere do you stand? {politics_url}\nLive Telemetry: {report_url}"
    else:
        twitter_reply = f"Dive into the full institutional data, capital flight metrics, and cross-node correlations on the GSN Terminal:\n\n{report_url}"
        unified_full_message = f"{ai_message}\n\nLive Telemetry: {report_url}"

    # 6. EXECUTE BROADCAST MATRIX
    print("\n--- INITIATING MODULAR BROADCAST MATRIX ---")
    
    run_twitter = os.getenv('RUN_TWITTER') == 'true'
    run_bluesky = os.getenv('RUN_BLUESKY') == 'true'
    run_telegram = os.getenv('RUN_TELEGRAM') == 'true'
    run_linkedin = os.getenv('RUN_LINKEDIN') == 'true'
    
    if run_twitter and all(twitter_keys.values()):
        post_to_twitter(ai_message, twitter_reply, twitter_keys)
    else:
        print("⏭️ Skipping X (Twitter): Disabled by user or missing keys.")

    if run_bluesky and bluesky_handle and bluesky_password:
        post_to_bluesky(unified_full_message, bluesky_handle, bluesky_password)
    else:
        print("⏭️ Skipping Bluesky: Disabled by user or missing keys.")

    if run_telegram and telegram_token and telegram_chat:
        post_to_telegram(unified_full_message, telegram_token, telegram_chat)
    else:
        print("⏭️ Skipping Telegram: Disabled by user or missing keys.")

    if run_linkedin and linkedin_token and linkedin_urn:
        post_to_linkedin(unified_full_message, linkedin_token, linkedin_urn)
    else:
        print("⏭️ Skipping LinkedIn: Disabled by user or missing keys.")

    print("--- MATRIX BROADCAST COMPLETE ---")

if __name__ == "__main__":
    main()