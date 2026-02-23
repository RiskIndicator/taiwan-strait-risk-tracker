import tweepy
import os
import sys

def main():
    # 1. Pull secrets from GitHub
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')
    
    risk_score = os.getenv('RISK_SCORE', 'Checked')

    # 2. Authenticate using the V2 Client
    # We must provide all 4 keys to enable User Auth (Write access)
    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        print("🚀 Authentication successful. Preparing tweet...")
    except Exception as e:
        print(f"❌ Authentication Setup Error: {e}")
        sys.exit(1)

    # 3. Format the message
    report_url = "https://taiwanstraittracker.com"
    message = f"🚨 Taiwan Strait Risk Update\n\nToday's Risk Index: {risk_score}/100\n\nFull intelligence briefing and radar: {report_url}"

    # 4. Post with 'user_auth=True' (The Fix)
    try:
        # user_auth=True is required to use the Access Tokens for Write access
        response = client.create_tweet(text=message, user_auth=True)
        print(f"✅ Tweet posted successfully! ID: {response.data['id']}")
    except tweepy.errors.Unauthorized as e:
        print(f"❌ 401 Unauthorized: Double check that your Access Tokens were regenerated AFTER you set permissions to Read/Write.")
        print(f"Error Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()