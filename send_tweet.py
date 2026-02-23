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

    # 2. Authenticate using OAuth 1.0a (Required for Free Tier Posting)
    try:
        # This is the 'V1' handler which is more reliable for checking 401 errors
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
        api_v1 = tweepy.API(auth)
        
        # This line will confirm if X actually likes your keys
        user = api_v1.verify_credentials()
        print(f"✅ Authenticated successfully as: @{user.screen_name}")
        
    except Exception as e:
        print(f"❌ Authentication Failed: {e}")
        print("💡 This means your keys are invalid or OAuth 1.0a isn't enabled in the portal.")
        sys.exit(1)

    # 3. Use the V2 Client to post the Tweet
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    report_url = "https://taiwanstraittracker.com"
    message = f"🚨 Taiwan Strait Risk Update\n\nToday's Risk Index: {risk_score}/100\n\nView full intelligence briefing and live radar: {report_url}"

    try:
        # user_auth=True forces it to use the OAuth 1.0a we just verified
        response = client.create_tweet(text=message, user_auth=True)
        print(f"✅ Tweet posted successfully! ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Post Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()