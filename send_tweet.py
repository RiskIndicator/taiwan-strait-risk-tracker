import os
import sys

def main():
    # 1. Pull secrets
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')

    # 2. DIAGNOSTIC CHECK
    # This identifies which secret is missing without printing the secret itself
    keys = {
        "TWITTER_API_KEY": api_key,
        "TWITTER_API_SECRET": api_secret,
        "TWITTER_ACCESS_TOKEN": access_token,
        "TWITTER_ACCESS_SECRET": access_secret
    }
    
    missing_any = False
    for name, value in keys.items():
        if not value or value.strip() == "":
            print(f"❌ MISSING: {name}")
            missing_any = True
        else:
            # Check length to ensure it's not just a single character or empty space
            print(f"✅ FOUND: {name} (Length: {len(value)})")

    if missing_any:
        print("\nError: One or more environment variables are empty. Check your GitHub Secrets naming.")
        sys.exit(1)

    print("🚀 All secrets found. Proceeding to tweet...")

    # 3. Import tweepy only after we know we have keys (to avoid import errors if pip failed)
    try:
        import tweepy
    except ImportError:
        print("❌ Error: Tweepy is not installed.")
        sys.exit(1)

    # 4. Authenticate and Post
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )

    report_url = "https://taiwanstraittracker.com"
    risk_score = os.getenv('RISK_SCORE', 'Checked')
    message = f"🚨 Taiwan Strait Risk Update\n\nToday's Risk Index: {risk_score}/100\n\nFull intelligence briefing and radar: {report_url}"

    try:
        response = client.create_tweet(text=message)
        print(f"✅ Tweet posted! ID: {response.data['id']}")
    except Exception as e:
        print(f"❌ Twitter API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()