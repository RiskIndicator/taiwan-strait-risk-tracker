import tweepy
import os
import sys
from datetime import datetime
import pytz

def main():
    # 1. Pull secrets from GitHub
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')
    
    risk_score = os.getenv('RISK_SCORE', 'Checked')

    # 2. Use the V2 Client directly (Bypassing the deprecated v1.1 API)
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # 3. Add a timestamp to prevent 403 Duplicate Tweet filters
    current_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y, %H:%M')
    
    report_url = "https://taiwanstraittracker.com"
    message = f"🚨 Taiwan Strait Risk Update ({current_time})\n\nToday's Risk Index: {risk_score}/100"

    # 4. Post the Tweet
    try:
        # user_auth=True forces it to use the OAuth 1.0a keys for posting
        response = client.create_tweet(text=message, user_auth=True)
        print(f"✅ Tweet posted successfully! ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Post Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()