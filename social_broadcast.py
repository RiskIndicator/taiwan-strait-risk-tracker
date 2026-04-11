import json
import os
import tweepy
import random
from datetime import datetime

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                pass
    return None

def broadcast_status():
    print("INITIALIZING GSN SOCIAL BROADCAST MATRIX...")
    
    # 1. Load the latest telemetry from our JSON files
    tw_data = load_json("data/taiwan_data.json") or {}
    me_data = load_json("data/me_data.json") or {}
    ai_data = load_json("data/ai_bubble_data.json") or {}

    # Extract metrics (falling back to nominal 30/50 if missing)
    tw_score = tw_data.get("current_risk_score", 30)
    tw_status = tw_data.get("status_text", "NOMINAL")
    tw_headline = tw_data.get("top_headline", "Standard market variance detected.")
    
    me_score = me_data.get("risk_index", 50)
    me_status = me_data.get("status_text", "CONTAINED")
    
    ai_score = ai_data.get("bubble_index", 50)

    # 2. Logic Engine: Decide what to Tweet
    tweet_text = ""
    
    # TRIGGER A: Taiwan Flash Alert (High Risk)
    if tw_score >= 60:
        tweet_text = (
            f"🚨 GSN FLASH ALERT: TAIWAN STRAIT 🚨\n\n"
            f"📊 Risk Index: {tw_score}/100 ({tw_status})\n\n"
            f"📡 Primary Catalyst:\n\"{tw_headline}\"\n\n"
            f"Capital flight detected in regional logistics/tech.\n"
            f"Live telemetry: taiwanstraittracker.com\n"
            f"#OSINT #Taiwan #Geopolitics #TSMC"
        )
        
    # TRIGGER B: Middle East Flash Alert (High Risk)
    elif me_score >= 70:
        tweet_text = (
            f"🚨 GSN FLASH ALERT: MIDDLE EAST 🚨\n\n"
            f"📊 Gulf Contagion Index: {me_score}/100 ({me_status})\n\n"
            f"🛢️ Energy markets and defense sectors rotating rapidly.\n"
            f"Live telemetry: taiwanstraittracker.com/middle-east\n"
            f"#OSINT #MiddleEast #EnergyMarkets"
        )
        
    # TRIGGER C: The Morning Macro Rollup (If things are relatively calm)
    else:
        hooks = [
            "🌐 GSN TERMINAL: MORNING MACRO BRIEFING",
            "📊 GLOBAL SHIFT NETWORK: DAILY TELEMETRY",
            "📡 OSINT TERMINAL: BASELINE UPDATE"
        ]
        tweet_text = (
            f"{random.choice(hooks)}\n\n"
            f"🇹🇼 Strait Risk: {tw_score} ({tw_status})\n"
            f"🛢️ Gulf Contagion: {me_score}\n"
            f"🤖 AI Bubble: {ai_score}\n\n"
            f"Current Primary Signal: \"{tw_headline}\"\n\n"
            f"Access the full intelligence dashboard:\n"
            f"taiwanstraittracker.com\n"
            f"#OSINT #Macro #Geopolitics #SupplyChain"
        )

    print("-" * 40)
    print("DRAFTED BROADCAST:")
    print(tweet_text)
    print("-" * 40)

    # 3. Authenticate with X (Twitter) API
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_SECRET")

    # Safety check for local testing (so it doesn't crash if you don't have keys locally)
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("⚠️ API Keys missing from environment. Dry run successful. Broadcast aborted.")
        return

    # 4. Fire the Payload
    try:
        client = tweepy.Client(
            consumer_key=api_key, 
            consumer_secret=api_secret,
            access_token=access_token, 
            access_token_secret=access_token_secret
        )
        response = client.create_tweet(text=tweet_text)
        print(f"✅ Broadcast Live! Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Broadcast Failed: {e}")

if __name__ == "__main__":
    broadcast_status()