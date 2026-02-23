import tweepy
import os
import sys

def main():
    # 1. Pull secrets from GitHub Actions environment
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')

    # 2. Basic check to ensure keys aren't empty
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ Error: One or more Twitter API secrets are missing.")
        sys.exit(1)

    # 3. Authenticate with X API v2
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # 4. Generate the Tweet content
    # Note: We include the URL so Twitter's crawler displays the Card image automatically
    report_url = "https://taiwanstraittracker.com"
    
    # You can customize this message - keep it under 280 chars
    tweet_text = f"🚨 Taiwan Strait Risk Update\n\nToday's Risk Index: {os.getenv('RISK_SCORE', 'Checked')}/100\n\nView full intelligence briefing and live radar: {report_url}"

    try:
        response = client.create_tweet(text=tweet_text)
        print(f"✅ Tweet posted successfully! Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Failed to post tweet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()