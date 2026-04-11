import tweepy
import os
import sys
import json
from google import genai 

def main():
    # 1. Pull secrets from GitHub
    twitter_api_key = os.getenv('TWITTER_API_KEY')
    twitter_api_secret = os.getenv('TWITTER_API_SECRET')
    twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        print("❌ Missing GEMINI_API_KEY.")
        sys.exit(1)

    # 2. Load the Full Network Intelligence
    print("Loading GSN Orchestrator Telemetry...")
    try:
        with open('data/agentic_briefing.json', 'r', encoding='utf-8') as f:
            briefing = json.load(f)
        with open('data/active_alerts.json', 'r', encoding='utf-8') as f:
            alerts_data = json.load(f)
            
        exec_summary = briefing.get('executive_summary', 'Nominal variance across all nodes.')
        correlations = briefing.get('correlations', 'None detected.')
        alerts = alerts_data.get('alerts', [])
        
        # Format alerts for the AI prompt
        alert_text = "\n".join([f"- {a['severity']} [{a['type']}]: {a['headline']}" for a in alerts]) if alerts else "No critical anomalies."
        
    except Exception as e:
        print(f"⚠️ Error loading orchestrated data: {e}")
        exec_summary = "System baseline nominal."
        correlations = "None."
        alert_text = "No critical anomalies."

    # 3. Generate Unique Tweet Copy using Google GenAI SDK
    try:
        print("Generating unique macro-geopolitical copy via Google AI...")
        ai_client = genai.Client(api_key=gemini_api_key)
        
        prompt = f"""
        You are the automated intelligence broadcaster for the Global Shift Network (GSN).
        Your task is to write a single, urgent, highly professional Twitter post (under 280 characters) summarizing today's global macro risk.
        
        Current Executive Summary: {exec_summary}
        Cross-Node Correlations: {correlations}
        Active Anomalies/Alerts: {alert_text}
        
        Instructions:
        - If there are ACTIVE ALERTS, focus the tweet entirely on the most severe alert.
        - If there are NO alerts, provide a clinical, macro-level summary of the correlations.
        - Tone: Institutional, data-driven, objective, OSINT analyst (FinTwit). 
        - Do not use hashtags in the main body. Add 2-3 relevant hashtags at the very end.
        - Do NOT include a URL or link (that will be in the reply thread).
        """

        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        main_message = response.text.strip()
    except Exception as e:
        print(f"❌ AI Generation Failed: {e}")
        sys.exit(1)

    # 4. Authenticate Twitter V2 Client
    client = tweepy.Client(
        consumer_key=twitter_api_key,
        consumer_secret=twitter_api_secret,
        access_token=twitter_access_token,
        access_token_secret=twitter_access_secret
    )

    # 5. Prepare Reply Message (Driving traffic to the terminal)
    report_url = "https://taiwanstraittracker.com"
    reply_message = f"Dive into the full institutional data, capital flight metrics, and cross-node correlations on the GSN Terminal:\n\n{report_url}"

    # 6. Execute the Thread
    try:
        print("Posting main AI generated text update...")
        main_response = client.create_tweet(text=main_message, user_auth=True)
        main_tweet_id = main_response.data['id']
        print(f"✅ Main tweet posted! ID: {main_tweet_id}")

        print("Posting URL as a threaded reply...")
        reply_response = client.create_tweet(
            text=reply_message, 
            in_reply_to_tweet_id=main_tweet_id, 
            user_auth=True
        )
        print(f"✅ Reply posted! ID: {reply_response.data['id']}")
        
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")

if __name__ == "__main__":
    main()