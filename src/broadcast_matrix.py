import tweepy
import requests
import os
import sys
import json
from google import genai 
from atproto import Client # NEW: Bluesky AT Protocol Library

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

    # 2. Load Telemetry
    print("Loading GSN Orchestrator Telemetry...")
    try:
        with open('data/agentic_briefing.json', 'r', encoding='utf-8') as f:
            briefing = json.load(f)
        with open('data/active_alerts.json', 'r', encoding='utf-8') as f:
            alerts_data = json.load(f)
            
        exec_summary = briefing.get('executive_summary', 'Nominal variance.')
        correlations = briefing.get('correlations', 'None detected.')
        alerts = alerts_data.get('alerts', [])
        alert_text = "\n".join([f"- {a['severity']} [{a['type']}]: {a['headline']}" for a in alerts]) if alerts else "No critical anomalies."
        
    except Exception as e:
        print(f"⚠️ Telemetry load error: {e}")
        exec_summary, correlations, alert_text = "Baseline nominal.", "None.", "None."

    # 3. Generate Unified Copy via Gemini
    try:
        print("Generating macro-geopolitical copy via Gemini 2.5 Flash...")
        ai_client = genai.Client(api_key=gemini_key)
        
        prompt = f"""
        You are the automated intelligence broadcaster for the Global Shift Network (GSN).
        Write a single, urgent, highly professional OSINT alert (under 280 characters).
        
        Summary: {exec_summary}
        Correlations: {correlations}
        Alerts: {alert_text}
        
        Instructions:
        - Focus on the most severe alert, or macro correlations if no alerts exist.
        - Tone: Institutional, data-driven, objective.
        - Do not use hashtags in the main body. Add 2-3 at the end.
        - NEVER include a URL.
        """

        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        ai_message = response.text.strip()
    except Exception as e:
        print(f"❌ AI Generation Failed: {e}")
        sys.exit(1)

    # 4. Prepare URLs and Final Text
    report_url = "https://taiwanstraittracker.com"
    twitter_reply = f"Dive into the full institutional data, capital flight metrics, and cross-node correlations on the GSN Terminal:\n\n{report_url}"
    
    # LinkedIn, Telegram, and Bluesky logic: append the link to the bottom.
    unified_full_message = f"{ai_message}\n\nLive Telemetry: {report_url}"

    # 5. EXECUTE BROADCAST MATRIX
    print("\n--- INITIATING MODULAR BROADCAST MATRIX ---")
    
    # Check environment toggles (Defaults to False if not found)
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