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
import time
from html2image import Html2Image

# --- CONFIG ---
MARKET_WEIGHT = 0.5
CONFLICT_WEIGHT = 0.5

# --- 1. DATA GATHERING ---

def get_market_risk():
    try:
        tsm = yf.Ticker("TSM").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        
        if len(tsm) < 2 or len(spy) < 2: 
            return {"score": 30, "desc": "Market Closed"}
            
        tsm_change = (tsm['Close'].iloc[-1] - tsm['Open'].iloc[-1]) / tsm['Open'].iloc[-1]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[-1]) / spy['Open'].iloc[-1]
        
        divergence = spy_change - tsm_change
        score = 30 + (divergence * 400)
        final_score = int(max(0, min(100, score)))

        if abs(divergence) > 0.015:
            evidence = "High Divergence (TSMC/SPY)"
        else:
            evidence = "Market Volatility Normal"
        
        return {"score": final_score, "desc": evidence}

    except Exception as e:
        print(f"Market Error: {e}")
        return {"score": 30, "desc": "Data unavailable"}

def get_conflict_risk():
    try:
        rss_url = "https://news.google.com/rss/search?q=Taiwan+China+conflict+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        entries = feed.entries[:20]
        
        if not entries: 
            return {"score": 30, "headlines": [], "top_phrase": "No Signals"}
        
        sentiment_score = 0
        keyword_hits = 0
        # Ordered from "Scary" to "Standard"
        warning_words = ["missile", "blockade", "live-fire", "invasion", "jets", "incursion", "drill", "exercise"]
        triggered_headlines = []
        
        for entry in entries:
            title = entry.title
            title_lower = title.lower()
            hit = False
            for word in warning_words:
                if word in title_lower:
                    keyword_hits += 1
                    hit = True
            
            blob = TextBlob(title)
            sentiment_score += blob.sentiment.polarity
            
            if hit and len(triggered_headlines) < 3:
                triggered_headlines.append(title)
            
        avg_sentiment = sentiment_score / len(entries)
        sentiment_risk = 50 - (avg_sentiment * 50) 
        keyword_risk = keyword_hits * 5
        total = (sentiment_risk * 0.6) + (keyword_risk * 0.4)
        final_score = int(max(0, min(100, total)))
        
        # --- SMART SIGNAL LABELING ---
        top_phrase = "Sector Calm"
        
        if triggered_headlines:
            if final_score < 60:
                 top_phrase = "Signal: NEWS FLOW"
            else:
                for word in warning_words:
                    if any(word in h.lower() for h in triggered_headlines):
                        top_phrase = f"Signal: {word.upper()}"
                        break

        return {
            "score": final_score,
            "headlines": triggered_headlines,
            "top_phrase": top_phrase
        }
        
    except Exception as e:
        print(f"News Error: {e}")
        return {"score": 30, "headlines": [], "top_phrase": "Data Error"}

# --- 2. VISUALS GENERATION ---

def generate_dark_mode_card(score, status, color, market_desc, conflict_phrase, trend_arrow):
    html_str = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
        body {{ margin: 0; padding: 0; width: 1200px; height: 628px; background-color: #0f172a; color: #e2e8f0; font-family: 'JetBrains Mono', monospace; display: flex; justify-content: center; align-items: center; }}
        .container {{ width: 1100px; height: 550px; background: #1e293b; border: 2px solid #334155; border-radius: 16px; position: relative; overflow: hidden; display: grid; grid-template-columns: 1fr 1fr; }}
        .grid {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px); background-size: 40px 40px; opacity: 0.1; z-index: 0; }}
        .left-panel {{ padding: 50px; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; z-index: 1; border-right: 2px solid #334155; }}
        .label {{ font-size: 20px; color: #94a3b8; letter-spacing: 2px; margin-bottom: 10px; }}
        .score-wrap {{ display: flex; align-items: center; gap: 20px; }}
        .score {{ font-size: 160px; font-weight: 800; line-height: 1; color: {color}; text-shadow: 0 0 40px {color}40; }}
        .trend {{ font-size: 80px; color: #64748b; }}
        .status-badge {{ margin-top: 20px; padding: 10px 24px; background: {color}20; color: {color}; border: 1px solid {color}; font-size: 32px; font-weight: 700; border-radius: 8px; text-transform: uppercase; letter-spacing: 3px; }}
        .right-panel {{ padding: 50px; display: flex; flex-direction: column; justify-content: center; z-index: 1; }}
        .intel-row {{ margin-bottom: 40px; }}
        .intel-label {{ color: #64748b; font-size: 18px; margin-bottom: 8px; text-transform: uppercase; }}
        .intel-value {{ font-size: 28px; color: #f8fafc; font-weight: 700; border-left: 4px solid {color}; padding-left: 15px; }}
        .footer {{ position: absolute; bottom: 20px; right: 30px; color: #475569; font-size: 16px; letter-spacing: 1px; }}
    </style>
    <link rel="icon" type="image/png" href="/public/gsn-logo-mono.png">
</head>
    <body>
        <div class="container">
            <div class="grid"></div>
            <div class="left-panel">
                <div class="label">TAIWAN STRAIT RISK INDEX</div>
                <div class="score-wrap"><div class="score">{score}</div><div class="trend">{trend_arrow}</div></div>
                <div class="status-badge">{status}</div>
            </div>
            <div class="right-panel">
                <div class="intel-row"><div class="intel-label">CONFLICT SIGNALS</div><div class="intel-value">{conflict_phrase}</div></div>
                <div class="intel-row"><div class="intel-label">MARKET SENTIMENT</div><div class="intel-value">{market_desc}</div></div>
                <div class="intel-row"><div class="intel-label">DATE</div><div class="intel-value">{datetime.now().strftime('%Y-%m-%d')}</div></div>
            </div>
            <div class="footer">TAIWANSTRAITTRACKER.COM // OSINT AUTOMATION</div>
        </div>
    </body>
    </html>
    """
    return html_str

def prepare_clickbait_tweet(status, score, summary, headlines, market_desc):
    base_url = "https://taiwanstraittracker.com"
    
    if score < 40:
        hooks = [f"🌊 CALM: Taiwan Strait Risk Index stable at {score}.", f"📉 REPORT: No major anomalies detected. Score: {score}.", f"🛡️ STATUS: Geopolitical indicators nominal ({score})."]
    elif score < 60:
        hooks = [f"⚠️ WATCH: Risk Index rising to {score}. {market_desc}.", f"👀 EYES ON: Activity detected in the Strait (Score {score}).", f"📈 TREND: Risk score hits {score}. Rhetoric heating up."]
    else:
        hooks = [f"🚨 ALERT: Risk Index spikes to {score}. Full briefing 👇", f"‼️ CRITICAL: Multiple risk vectors flashing red (Score {score}).", f"🔔 URGENT: Divergence + Conflict keywords detected. Score: {score}."]
        
    hook = random.choice(hooks)
    
    reason = ""
    if headlines:
        top_story = headlines[0].split('-')[0].strip()[:50]
        reason = f"\n\n🔍 INTEL: {top_story}..."
    elif "Divergence" in market_desc:
        reason = f"\n\n📉 MARKET: Unusual TSMC movements detected."

    tags = "\n\n#Taiwan #China #OSINT #Geopolitics #TSMC"
    return f"{hook}{reason}{tags}\n{base_url}"

# --- 3. MAIN EXECUTION ---

def main():
    print("Starting Build Process...")

    market_data = get_market_risk()
    conflict_data = get_conflict_risk()
    market_score = market_data['score']
    conflict_score = conflict_data['score']
    final_score = int((market_score * MARKET_WEIGHT) + (conflict_score * CONFLICT_WEIGHT))

    if final_score < 40:
        status = "NOMINAL"; color = "#10b981"; summary = "Standard variance. No indicators."
    elif final_score < 60:
        status = "ELEVATED"; color = "#f59e0b"; summary = "Heightened rhetorical noise detected."
    else:
        status = "HIGH RISK"; color = "#ef4444"; summary = "Significant anomaly detected."

    today_str = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%Y-%m-%d')
    try:
        with open('history.json', 'r', encoding='utf-8') as f: history = json.load(f)
    except: history = []

    last_score = history[-1]['score'] if history else final_score
    score_change = final_score - last_score
    if score_change > 0: trend_arrow = "▲"; trend_desc = f"+{score_change}"
    elif score_change < 0: trend_arrow = "▼"; trend_desc = f"{score_change}"
    else: trend_arrow = "■"; trend_desc = "-"

    history = [entry for entry in history if entry['date'] != today_str]
    history.append({"date": today_str, "score": final_score})
    history = history[-30:]
    with open('history.json', 'w', encoding='utf-8') as f: json.dump(history, f)

    print("Generating Situation Room Card...")
    card_html = generate_dark_mode_card(final_score, status, color, market_data['desc'], conflict_data['top_phrase'], trend_arrow)
    
    final_image_url = ""
    try:
        hti = Html2Image(output_path='public', size=(1200, 628), custom_flags=['--no-sandbox', '--disable-gpu', '--hide-scrollbars'])
        os.makedirs('public', exist_ok=True)
        new_filename = f"card_{today_str}_s{final_score}.png"
        for f in glob.glob(f"public/card_{today_str}*.png"): os.remove(f)
        hti.screenshot(html_str=card_html, save_as=new_filename)
        final_image_url = f"https://raw.githubusercontent.com/RiskIndicator/taiwan-strait-risk-tracker/main/public/{new_filename}"
        print(f"✅ Card Generated: {new_filename}")
    except Exception as e:
        print(f"❌ Screenshot Error: {e}")

    tweet_content = prepare_clickbait_tweet(status, final_score, summary, conflict_data['headlines'], market_data['desc'])

    # --- THE FIX STARTS HERE ---
    
    # 1. Generate Daily Report first
    os.makedirs('reports', exist_ok=True)
    report_filename = f"report_{today_str}.html"
    report_filepath = os.path.join('reports', report_filename)
    
    try:
        with open('report_template.html', 'r', encoding='utf-8') as f:
            report_template = Template(f.read())
            
        rendered_report = report_template.render(
            date_str=today_str,
            risk_score=final_score,
            status_text=status,
            market_score=market_score,
            conflict_score=conflict_score,
            color_code=color,
            daily_summary=summary,
            market_evidence=market_data['desc'],
            headline_list=conflict_data['headlines']
        )
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_report)
        print(f"✅ Report Generated: {report_filepath}")
    except Exception as e:
        print(f"❌ Report Generation Error: {e}")

    # 2. Build the Archive List
    report_files = sorted(glob.glob('reports/report_*.html'), reverse=True)[:5]
    recent_reports = []
    for file_path in report_files:
        filename = os.path.basename(file_path)
        date_part = filename.replace('report_', '').replace('.html', '')
        recent_reports.append({
            'url': f"reports/{filename}",
            'date': date_part
        })

    # 3. Update the Homepage (index.html)
    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%Y-%m-%d %H:%M')
    
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            main_template = Template(f.read())

        rendered_html = main_template.render(
            risk_score=final_score,
            status_text=status,
            market_score=market_score,
            conflict_score=conflict_score,
            color_code=color,
            daily_summary=summary,
            last_updated=update_time,
            history_json=json.dumps(history),
            report_list=recent_reports, 
            trend_arrow=trend_arrow,
            trend_desc=trend_desc,
            market_evidence=market_data['desc'],
            top_headline=conflict_data['headlines'][0] if conflict_data['headlines'] else "No news flow",
            latest_report_url=f"reports/{report_filename}" 
        )

# --- CLEANED UP SECTION ---
        meta_tags = f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{final_image_url}">'
        
        # Remove the old static meta tags
        final_html = rendered_html.replace('<meta name="twitter:card" content="summary_large_image">', '').replace('<meta name="twitter:image" content="https://taiwanstraittracker.com/public/card_2026-02-09.png">', '')
        
        # Inject the new dynamic meta tags right before the closing </head> tag
        final_html = final_html.replace("</head>", f"{meta_tags}\n</head>")

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(final_html)
        print("✅ Homepage Updated")
        # --------------------------

    except Exception as e:
        print(f"❌ Homepage Update Error: {e}")

    # F. GITHUB ACTIONS OUTPUT
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
            print("tweet<<EOF", file=fh)
            print(tweet_content, file=fh)
            print("EOF", file=fh)
            print(f"image_url={final_image_url}", file=fh)
            print(f"risk_score={final_score}", file=fh)

if __name__ == "__main__":
    main()