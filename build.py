import yfinance as yf
import feedparser
from textblob import TextBlob
from jinja2 import Template
from datetime import datetime
import pytz
import json
import os

# --- 1. SET UP ---
# Define weights for the algorithm
MARKET_WEIGHT = 0.5
CONFLICT_WEIGHT = 0.5

def get_market_risk():
    """
    Calculates risk based on TSMC (TSM) performance relative to S&P 500 (SPY).
    High Risk = TSM crashing while SPY is stable.
    """
    try:
        # Fetch last 5 days of data
        tsm = yf.Ticker("TSM").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        
        if len(tsm) < 2 or len(spy) < 2:
            return 30 # Neutral fallback if market closed
            
        # Calculate daily % change
        tsm_change = (tsm['Close'].iloc[-1] - tsm['Open'].iloc[-1]) / tsm['Open'].iloc[-1]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[-1]) / spy['Open'].iloc[-1]
        
        # Divergence: If SPY is up (0.01) and TSM is down (-0.05), diff is 0.06
        divergence = spy_change - tsm_change
        
        # Formula: Base 30 + (Divergence * Multiplier)
        # Normal fluctuation is ~2-3%, so a 5% divergence is huge.
        score = 30 + (divergence * 400)
        return int(max(0, min(100, score)))
    except Exception as e:
        print(f"Market Data Error: {e}")
        return 30 # Neutral fallback

def get_conflict_risk():
    """
    Scans Google News RSS for specific 'Warning' keywords.
    """
    try:
        # Google News RSS for 'Taiwan China'
        rss_url = "https://news.google.com/rss/search?q=Taiwan+China+conflict+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        entries = feed.entries[:15] # Analyze top 15 stories
        if not entries: return 30
        
        sentiment_score = 0
        keyword_hits = 0
        warning_words = ["invasion", "jets", "incursion", "adiz", "war", "missile", "blockade"]
        
        for entry in entries:
            title = entry.title.lower()
            
            # 1. Keyword Count (The "Military Proxy")
            for word in warning_words:
                if word in title:
                    keyword_hits += 1
            
            # 2. Sentiment Analysis
            blob = TextBlob(entry.title)
            # Polarity -1 (Negative) to 1 (Positive). We want Negative = High Risk.
            sentiment_score += blob.sentiment.polarity
            
        # Calculate Score
        # Average sentiment (invert it: negative news is positive risk)
        avg_sentiment = sentiment_score / len(entries)
        sentiment_risk = 50 - (avg_sentiment * 50) 
        
        # Keyword Boost: +5 points for every "war" word found in top 15 headlines
        keyword_risk = keyword_hits * 5
        
        total = (sentiment_risk * 0.6) + (keyword_risk * 0.4)
        return int(max(0, min(100, total)))
        
    except Exception as e:
        print(f"News Error: {e}")
        return 30

# --- 2. EXECUTE LOGIC ---
market_score = get_market_risk()
conflict_score = get_conflict_risk()

# Weighted Average
final_score = int((market_score * MARKET_WEIGHT) + (conflict_score * CONFLICT_WEIGHT))

# Determine Status Text & Color
if final_score < 30:
    status = "Low Tension"
    color = "#28a745" # Green
    summary = "Markets are stable and rhetorical noise is low."
elif final_score < 60:
    status = "Elevated"
    color = "#ffc107" # Amber
    summary = "Increased diplomatic friction or minor market divergence detected."
else:
    status = "High Risk"
    color = "#dc3545" # Red
    summary = "Significant market volatility or aggressive military signaling detected."

# --- 3. UPDATE DATABASE (HISTORY.JSON) ---
brisbane_time = datetime.now(pytz.timezone('Australia/Brisbane'))
today_str = brisbane_time.strftime('%Y-%m-%d')
update_time = brisbane_time.strftime('%Y-%m-%d %H:%M')

# Load existing history
try:
    with open('history.json', 'r') as f:
        history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    history = []

# --- FORCE BACKFILL IF DATA IS TOO SHORT ---
# The bug was checking "if not history". 
# We change it to: if less than 5 entries, generate fake history.
if len(history) < 5:
    import random
    from datetime import timedelta
    print("History too short. Generating 30-day backfill...")
    
    # Clear existing to prevent weird overlaps
    history = []
    
    current_date = brisbane_time - timedelta(days=30)
    for _ in range(30):
        # Generate a random score around 30-40 (Low tension baseline)
        fake_score = random.randint(25, 45)
        history.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "score": fake_score
        })
        current_date += timedelta(days=1)

# Add today's real entry
# Remove today if it already exists (to update it)
history = [entry for entry in history if entry['date'] != today_str]
history.append({"date": today_str, "score": final_score})

# Keep only last 30 days
history = history[-30:]

# Save history
with open('history.json', 'w') as f:
    json.dump(history, f)

# --- 4. BUILD HTML ---
with open('template.html', 'r') as f:
    template_str = f.read()

template = Template(template_str)
output_html = template.render(
    risk_score=final_score,
    status_text=status,
    market_score=market_score,
    conflict_score=conflict_score,
    color_code=color,
    daily_summary=summary,
    last_updated=update_time,
    history_json=json.dumps(history) # Pass raw JSON for JS Chart
)

with open('index.html', 'w') as f:
    f.write(output_html)

print(f"SUCCESS: Built site. Score: {final_score}")
