import tweepy
import os
import sys

def send_tweet():
    # 1. Get credentials from GitHub Secrets
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    # 2. Get the tweet text (passed from the YAML file)
    tweet_text = os.environ.get("TWEET_TEXT")

    if not tweet_text:
        print("Error: No tweet text found!")
        sys.exit(1)

    print(f"Attempting to tweet length: {len(tweet_text)}")

    # 3. Authenticate using API v2 (Client)
    # This is the "Magic Fix" - Client uses the v2 endpoint which is allowed on Free Tier.
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # 4. Post the Tweet
    try:
        response = client.create_tweet(text=tweet_text)
        print(f"SUCCESS! Tweet sent. ID: {response.data['id']}")
    except Exception as e:
        print(f"Error sending tweet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_tweet()
