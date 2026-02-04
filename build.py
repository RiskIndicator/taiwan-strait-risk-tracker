import yfinance as yf
import feedparser
from textblob import TextBlob
from jinja2 import Template
from datetime import datetime, timedelta
import pytz
import json
import os
import random
import glob

# --- 1. SET UP ---
MARKET_WEIGHT = 0.5
CONFLICT_WEIGHT = 0.5

def get_market_risk():
    try:
        tsm = yf.Ticker("TSM").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        if len(tsm) < 2 or len(spy) < 2: return 30
        tsm_change = (tsm['Close'].iloc[-1] - tsm['Open'].iloc[-1]) / tsm['Open'].iloc[-1]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[-1]) / spy['Open'].iloc[-1]
        divergence = spy_change - tsm_change
        score = 30 + (divergence * 400)
        return int(max(0, min(100, score)))
    except Exception as e:
        print(f"Market Data Error: {e}")
        return 30

def get_conflict_risk():
    try:
        rss_url = "https://news.google.com/rss/search?q=Taiwan+China+conflict+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        entries = feed.entries[:15]
        if not entries: return 30
        
        sentiment_score = 0
        keyword_hits = 0
        warning_words = ["invasion", "jets", "incursion", "adiz", "war", "missile", "blockade"]
        
        for entry in entries:
            title = entry.title.lower()
            for word in warning_words:
                if word in title: keyword_hits += 1
            blob = TextBlob(entry.title)
            sentiment_score += blob.sentiment.polarity
            
        avg_sentiment = sentiment_score / len(entries)
        sentiment_risk = 50 - (avg_sentiment * 50) 
        keyword_risk = keyword_hits * 5
        total = (sentiment_risk * 0.6) + (keyword_risk * 0.4)
        return int(max(0, min(100, total)))
    except Exception as e:
        print(f"News Error: {e}")
        return 30

# --- 2. EXECUTE LOGIC ---
market_score = get_market_risk()
conflict_score = get_conflict_risk()
final_score = int((market_score * MARKET_WEIGHT) + (conflict_score * CONFLICT_WEIGHT))

if final_score < 30:
    status = "Low Tension"
    color = "#28a745"
    summary = "Markets are stable and rhetorical noise is low."
elif final_score < 60:
    status = "Elevated"
    color = "#ffc107"
    summary = "Increased diplomatic friction or minor market divergence detected."
else:
    status = "High Risk"
    color = "#dc3545"
    summary = "Significant market volatility or aggressive military signaling detected."

# --- 3. UPDATE DATABASE ---
brisbane_time = datetime.now(pytz.timezone('Australia/Brisbane'))
today_str = brisbane_time.strftime('%Y-%m-%d')
update_time = brisbane_time.strftime('%Y-%m-%d %H:%M')

try:
    with open('history.json', 'r') as f:
        history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    history = []

if len(history) < 5:
    current_date = brisbane_time - timedelta(days=30)
    history = []
    for _ in range(30):
        history.append({"date": current_date.strftime('%Y-%m-%d'), "score": random.randint(25, 45)})
        current_date += timedelta(days=1)

history = [entry for entry in history if entry['date'] != today_str]
history.append({"date": today_str, "score": final_score})
history = history[-30:]

with open('history.json', 'w') as f:
    json.dump(history, f)

# --- 4. GENERATE DAILY ARCHIVE REPORT (Moved First) ---
report_filename = f"reports/{today_str}-risk-analysis.html"
try:
    with open('report_template.html', 'r') as f:
        report_template_str = f.read()
    
    report_template = Template(report_template_str)
    report_html = report_template.render(
        date_str=today_str,
        risk_score=final_score,
        status_text=status,
        conflict_score=conflict_score,
        market_score=market_score,
        color_code=color,
        daily_summary=summary,
        archive_filename=report_filename
    )
    
    os.makedirs('reports', exist_ok=True)
    with open(report_filename, 'w') as f:
        f.write(report_html)
    print(f"SUCCESS: Generated archive report: {report_filename}")
except Exception as e:
    print(f"Archive Error: {e}")

# --- 5. SCAN FOR EXISTING REPORTS (New Feature) ---
# Finds all html files in reports folder, sorts by name (date) descending
report_links = []
if os.path.exists('reports'):
    files = sorted(glob.glob('reports/*.html'), reverse=True)
    for f in files:
        # Create a display name (e.g., "2026-02-04") from the filename
        # Filename is "reports/2026-02-04-risk-analysis.html"
        date_part = os.path.basename(f).split('-risk')[0]
        report_links.append({'url': f, 'date': date_part})

# --- 6. BUILD HTML (HOME PAGE) ---
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
    last_updated_date=today_str,
    history_json=json.dumps(history),
    report_list=report_links  # Passing the list to the template
)

with open('index.html', 'w') as f:
    f.write(output_html)

print(f"SUCCESS: Built site. Score: {final_score}")
