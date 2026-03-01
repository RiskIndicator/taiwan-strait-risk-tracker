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

    # 2. Authenticate the V2 Client
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # 3. Prepare the payload
    current_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y, %H:%M')
    
    # Tweet 1: Safe text only
    main_message = f"🚨 Taiwan Strait Risk Update ({current_time})\n\nToday's Risk Index: {risk_score}/100"
    
    # Tweet 2: The flagged URL
    report_url = "https://taiwanstraittracker.com"
    reply_message = f"View the full intelligence briefing and live radar here:\n{report_url}"

    # 4. Execute the Thread
    try:
        # Post the main tweet
        print("Posting main text update...")
        main_response = client.create_tweet(text=main_message, user_auth=True)
        main_tweet_id = main_response.data['id']
        print(f"✅ Main tweet posted! ID: {main_tweet_id}")

        # Post the reply using the ID from the main tweet
        print("Posting URL as a threaded reply...")
        reply_response = client.create_tweet(
            text=reply_message, 
            in_reply_to_tweet_id=main_tweet_id, 
            user_auth=True
        )
        print(f"✅ Reply posted successfully! ID: {reply_response.data['id']}")
        
    except Exception as e:
        print(f"❌ Post Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()