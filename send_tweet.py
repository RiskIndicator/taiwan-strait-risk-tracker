import tweepy
import os
import sys
import google.generativeai as genai

def main():
    # 1. Pull secrets from GitHub
    twitter_api_key = os.getenv('TWITTER_API_KEY')
    twitter_api_secret = os.getenv('TWITTER_API_SECRET')
    twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    risk_score = os.getenv('RISK_SCORE', 'Unchanged')
    top_headline = os.getenv('TOP_HEADLINE', 'Standard market variance detected.')

    if not gemini_api_key:
        print("❌ Missing GEMINI_API_KEY.")
        sys.exit(1)

    # 2. Generate Unique Tweet Copy using Google AI Studio
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a professional open-source intelligence (OSINT) analyst. 
    Write a single, urgent Twitter post announcing today's Taiwan Strait Risk Score is {risk_score}/100. 
    The primary escalation driver is this headline: "{top_headline}".
    Keep it highly professional, analytical, and strictly under 200 characters. 
    Do not use any hashtags. End the tweet by telling the reader to view the full report below.
    """
    
    try:
        print("Generating unique copy via Google AI...")
        response = model.generate_content(prompt)
        main_message = response.text.strip()
    except Exception as e:
        print(f"❌ AI Generation Failed: {e}")
        sys.exit(1)

    # 3. Authenticate Twitter V2 Client
    client = tweepy.Client(
        consumer_key=twitter_api_key,
        consumer_secret=twitter_api_secret,
        access_token=twitter_access_token,
        access_token_secret=twitter_access_secret
    )

    # 4. Prepare Reply Message (Keeping the link out of the main tweet boosts algorithmic reach)
    report_url = "https://taiwanstraittracker.com"
    reply_message = f"Dive into the institutional data, capital flight metrics, and full market impact here:\n{report_url}"

    # 5. Execute the Thread
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
        print(f"✅ Reply posted successfully! ID: {reply_response.data['id']}")
        
    except Exception as e:
        print(f"❌ Post Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()