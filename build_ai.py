import yfinance as yf
import feedparser
from textblob import TextBlob
from jinja2 import Template
import json
import numpy as np
from datetime import datetime
import pytz

# --- CONFIGURATION ---
MAG_7 = ['NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'TSLA', 'AAPL']

def get_valuation_index():
    print("Fetching Valuation Data...")
    try:
        mag7_pes = []
        for ticker in MAG_7:
            try:
                stock = yf.Ticker(ticker)
                pe = stock.info.get('forwardPE', 0)
                if pe > 0: mag7_pes.append(pe)
            except: continue
        
        if not mag7_pes: return 50, 0.0
        
        avg_mag7_pe = np.mean(mag7_pes)
        # Linear mapping: 20 PE = 0 Score, 60 PE = 100 Score
        score = (avg_mag7_pe - 20) * 2.5
        return int(max(0, min(100, score))), round(avg_mag7_pe, 1)
    except:
        return 50, 0.0

def get_capex_momentum():
    print("Fetching Capex/Volume Data...")
    try:
        nvda = yf.Ticker("NVDA").history(period="3mo")
        avg_vol = nvda['Volume'].mean()
        current_vol = nvda['Volume'].iloc[-1]
        ratio = current_vol / avg_vol
        score = ratio * 50
        return int(max(0, min(100, score)))
    except:
        return 50

def get_sentiment_score():
    print("Analysing Media Sentiment...")
    try:
        rss_url = "https://news.google.com/rss/search?q=AI+Bubble+Stock+Market&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        bubble_mentions = sum(1 for entry in feed.entries[:15] if "bubble" in entry.title.lower() or "crash" in entry.title.lower())
        score = (bubble_mentions / 15) * 100 * 2
        return int(max(0, min(100, score)))
    except:
        return 50

def get_adoption_velocity():
    return 65 # V1 Placeholder for Enterprise Stability

def build_index():
    print("ASSEMBLING AI BUBBLE INDEX...")
    
    v_score, avg_pe = get_valuation_index()
    c_score = get_capex_momentum()
    s_score = get_sentiment_score()
    a_score = get_adoption_velocity()
    
    # Get Strait Risk
    try:
        with open('history.json', 'r') as f:
            strait_history = json.load(f)
            strait_risk = strait_history[-1]['score']
    except:
        strait_risk = 30
        
    # Calculate Base Score
    base_score = (v_score * 0.4) + (c_score * 0.3) + (s_score * 0.2) + (a_score * 0.1)
    
    # Apply Volatility Multiplier
    multiplier = 1 + (strait_risk / 200)
    final_score = int(max(0, min(100, base_score * multiplier)))
    
    if final_score < 40: status = "HEALTHY GROWTH"
    elif final_score < 65: status = "ELEVATED VALUATION"
    elif final_score < 85: status = "SPECULATIVE MANIA"
    else: status = "CRITICAL INSTABILITY"
    
    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M')

    # Render the HTML Template
    with open('ai_template.html', 'r', encoding='utf-8') as f:
        template = Template(f.read())

    rendered_html = template.render(
        bubble_score=final_score,
        status_text=status,
        multiplier=round(multiplier, 2),
        strait_risk=strait_risk,
        v_score=v_score,
        c_score=c_score,
        s_score=s_score,
        a_score=a_score,
        avg_pe=avg_pe,
        last_updated=update_time
    )

    with open('ai_bubble.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    print("Success: ai_bubble.html generated.")

if __name__ == "__main__":
    build_index()
