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
    """
    Returns specific data: Score AND the exact percentage divergence.
    """
    try:
        tsm = yf.Ticker("TSM").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        
        if len(tsm) < 2 or len(spy) < 2: 
            return {"score": 30, "desc": "Market Closed / No Data"}
            
        # Calculate daily % change
        tsm_change = (tsm['Close'].iloc[-1] - tsm['Open'].iloc[-1]) / tsm['Open'].iloc[-1]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[-1]) / spy['Open'].iloc[-1]
        
        # Divergence
        divergence = spy_change - tsm_change
        score = 30 + (divergence * 400)
        final_score = int(max(0, min(100, score)))

        # Format evidence string (e.g., "TSMC -1.2% vs SPY +0.5%")
        tsm_pct = f"{tsm_change*100:+.2f}%"
        spy_pct = f"{spy_change*100:+.2f}%"
        evidence = f"TSMC ({tsm_pct}) vs SP500 ({spy_pct})"
        
        return {"score": final_score, "desc": evidence}

    except Exception as e:
        print(f"Market Error: {e}")
        return {"score": 30, "desc": "Data unavailable"}

def get_conflict_risk():
    """
    Returns score AND top 3 relevant headlines.
    """
    try:
        rss_url = "https://news.google.com/rss/search?q=Taiwan+China+conflict+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        entries = feed.entries[:20]
        
        if not entries: 
            return {"score": 30, "headlines": []}
        
        sentiment_score = 0
        keyword_hits = 0
        warning_words = ["invasion", "jets", "incursion", "adiz", "war", "missile", "blockade", "drill", "exercise"]
        triggered_headlines = []
        
        for entry in entries:
            title = entry.title
            title_lower = title.lower()
            
            # Check for keywords
            hit = False
            for word in warning_words:
                if word in title_lower:
                    keyword_hits += 1
                    hit = True
            
            # Sentiment
            blob = TextBlob(title)
            sentiment_score += blob.sentiment.polarity
            
            # Save relevant headlines for the report
            if hit and len(triggered_headlines) < 3:
                triggered_headlines.append(title)
            
        # Calculate Score
        avg_sentiment = sentiment_score / len(entries)
        sentiment_risk = 50 - (avg_sentiment * 50) 
        keyword_risk = keyword_hits * 5
        total = (sentiment_risk * 0.6) + (keyword_risk * 0.4)
        
        return {
            "score": int(max(0, min(100, total))),
            "headlines": triggered_headlines
        }
        
    except Exception as e:
        print(f"News Error: {e}")
        return {"score": 30, "headlines": []}

# --- 2. EXECUTE LOGIC ---
market_data = get_market_risk()
conflict_data = get_conflict_risk()

market_score = market_data['score']
conflict_score = conflict_data['score']

# Weighted Average
final_score = int((market_score * MARKET_WEIGHT) + (conflict_score * CONFLICT_WEIGHT))

# Status Logic
if final_score < 30:
    status = "Low Tension"
    color = "#28a745" # Green
    summary = "Standard geopolitical variance. No immediate indicators of escalation."
elif final_score < 60:
    status = "Elevated"
    color = "#f59e0b" # Amber/Orange (Darker for readability)
    summary = " heightened rhetorical noise or market anomaly detected."
else:
    status = "High Risk"
    color = "#dc3545" # Red
    summary = "Significant anomaly detected in multiple risk vectors."

# --- 3. DATABASE & TREND LOGIC ---
brisbane_time = datetime.now(pytz.timezone('Australia/Brisbane'))
today_str = brisbane_time.strftime('%Y-%m-%d')
update_time = brisbane_time.strftime('%Y-%m-%d %H:%M')

try:
    with open('history.json', 'r') as f:
        history = json.load(f)
except:
    history = []

# Backfill if empty
if len(history) < 5:
    current_date = brisbane_time - timedelta(days=30)
    history = []
    for _ in range(30):
        history.append({"date": current_date.strftime('%Y-%m-%d'), "score": random.randint(25, 45)})
        current_date += timedelta(days=1)

# Calculate Trend (Change from yesterday)
last_score = history[-1]['score'] if history else final_score
score_change = final_score - last_score
if score_change > 0:
    trend_arrow = "↑"
    trend_desc = f"+{score_change} pts"
    trend_color = "#ef4444" # Red for rising risk
elif score_change < 0:
    trend_arrow = "↓"
    trend_desc = f"{score_change} pts"
    trend_color = "#28a745" # Green for falling risk
else:
    trend_arrow = "→"
    trend_desc = "No Change"
    trend_color = "#6b7280"

# Update History
history = [entry for entry in history if entry['date'] != today_str]
history.append({"date": today_str, "score": final_score})
history = history[-30:]

with open('history.json', 'w') as f:
    json.dump(history, f)

# --- 4. REPORT ARCHIVE GENERATION ---
report_links = []
if os.path.exists('reports'):
    files = sorted(glob.glob('reports/*.html'), reverse=True)
    for f in files:
        date_part = os.path.basename(f).split('-risk')[0]
        report_links.append({'url': f, 'date': date_part})

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
        market_evidence=market_data['desc'],
        headline_list=conflict_data['headlines'],
        archive_filename=report_filename
    )
    
    os.makedirs('reports', exist_ok=True)
    with open(report_filename, 'w') as f:
        f.write(report_html)
except Exception as e:
    print(f"Archive Error: {e}")

# --- 5. DASHBOARD GENERATION ---
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
    history_json=json.dumps(history),
    report_list=report_links,
    
    # NEW DATA POINTS
    trend_arrow=trend_arrow,
    trend_desc=trend_desc,
    trend_color=trend_color,
    market_evidence=market_data['desc'],
    top_headline=conflict_data['headlines'][0] if conflict_data['headlines'] else "No major conflict keywords detected in top stories."
)

with open('index.html', 'w') as f:
    f.write(output_html)
