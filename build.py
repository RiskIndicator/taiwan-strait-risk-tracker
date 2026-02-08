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
from screenshot import generate_card

# --- 1. SET UP ---
MARKET_WEIGHT = 0.5
CONFLICT_WEIGHT = 0.5

# --- FUNCTIONS ---
def update_sitemap(new_report_filename):
    sitemap_path = 'sitemap.xml'
    base_url = "https://taiwanstraittracker.com/"
    new_entry = f"""
    <url>
        <loc>{base_url}{new_report_filename}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>never</changefreq>
    </url>
    """
    if not os.path.exists(sitemap_path):
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>')
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if new_report_filename in content:
        return
    content = content.replace('</urlset>', new_entry + '</urlset>')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_market_risk():
    try:
        tsm = yf.Ticker("TSM").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        if len(tsm) < 2 or len(spy) < 2: 
            return {"score": 30, "desc": "Market Closed / No Data"}
        tsm_change = (tsm['Close'].iloc[-1] - tsm['Open'].iloc[-1]) / tsm['Open'].iloc[-1]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[-1]) / spy['Open'].iloc[-1]
        divergence = spy_change - tsm_change
        score = 30 + (divergence * 400)
        final_score = int(max(0, min(100, score)))
        tsm_pct = f"{tsm_change*100:+.2f}%"
        spy_pct = f"{spy_change*100:+.2f}%"
        evidence = f"TSMC ({tsm_pct}) vs SP500 ({spy_pct})"
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
            return {"score": 30, "headlines": []}
        sentiment_score = 0
        keyword_hits = 0
        warning_words = ["invasion", "jets", "incursion", "adiz", "war", "missile", "blockade", "drill", "exercise"]
        triggered_headlines = []
        for entry in entries:
            title = entry.title
            title_lower = title.lower()
            hit = False
            for word in warning_words:
                if word in title_lower:
                    keyword_hits += 1
                    hit = True
            blob = TextBlob(entry.title)
            sentiment_score += blob.sentiment.polarity
            if hit and len(triggered_headlines) < 3:
                triggered_headlines.append(title)
        avg_sentiment = sentiment_score / len(entries)
        sentiment_risk = 50 - (avg_sentiment * 50) 
        keyword_risk = keyword_hits * 5
        total = (sentiment_risk * 0.6) + (keyword_risk * 0.4)
        return {"score": int(max(0, min(100, total))), "headlines": triggered_headlines}
    except Exception as e:
        print(f"News Error: {e}")
        return {"score": 30, "headlines": []}

def prepare_tweet_text(status, score, summary):
    base_url = "https://taiwanstraittracker.com"
    hashtags = "#Taiwan #OSINT"
    prefix = f"Daily Risk Update: {status} (Score: {score})."
    safe_limit = 280 - 23 - len(hashtags) - len(prefix) - 5
    if len(summary) > safe_limit:
        safe_summary = summary[:safe_limit] + "..."
    else:
        safe_summary = summary
    final_tweet = f"{prefix} {safe_summary}\n\n{base_url} {hashtags}"
    return final_tweet

def main():
    print("Starting Build Process...")
    market_data = get_market_risk()
    conflict_data = get_conflict_risk()
    market_score = market_data['score']
    conflict_score = conflict_data['score']
    final_score = int((market_score * MARKET_WEIGHT) + (conflict_score * CONFLICT_WEIGHT))

    if final_score < 30:
        status = "Low Tension"
        color = "#28a745"
        summary = "Standard geopolitical variance. No immediate indicators of escalation."
    elif final_score < 60:
        status = "Elevated"
        color = "#f59e0b"
        summary = "Heightened rhetorical noise or market anomaly detected."
    else:
        status = "High Risk"
        color = "#dc3545"
        summary = "Significant anomaly detected in multiple risk vectors."

    brisbane_time = datetime.now(pytz.timezone('Australia/Brisbane'))
    today_str = brisbane_time.strftime('%Y-%m-%d')
    update_time = brisbane_time.strftime('%Y-%m-%d %H:%M')

    try:
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []

    if len(history) < 5:
        current_date = brisbane_time - timedelta(days=30)
        history = []
        for _ in range(30):
            history.append({"date": current_date.strftime('%Y-%m-%d'), "score": random.randint(25, 45)})
            current_date += timedelta(days=1)

    last_score = history[-1]['score'] if history else final_score
    score_change = final_score - last_score
    if score_change > 0:
        trend_arrow = "↑"
        trend_desc = f"+{score_change} pts"
        trend_color = "#ef4444"
    elif score_change < 0:
        trend_arrow = "↓"
        trend_desc = f"{score_change} pts"
        trend_color = "#28a745"
    else:
        trend_arrow = "→"
        trend_desc = "No Change"
        trend_color = "#6b7280"

    history = [entry for entry in history if entry['date'] != today_str]
    history.append({"date": today_str, "score": final_score})
    history = history[-30:]

    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history, f)

    report_links = []
    if os.path.exists('reports'):
        files = sorted(glob.glob('reports/*.html'), reverse=True)
        for f in files:
            date_part = os.path.basename(f).split('-risk')[0]
            report_links.append({'url': f, 'date': date_part})

    report_filename = f"reports/{today_str}-risk-analysis.html"
    try:
        with open('report_template.html', 'r', encoding='utf-8') as f:
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
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_html)
        update_sitemap(report_filename)
    except Exception as e:
        print(f"Archive Error: {e}")

    # --- 4. GENERATE CARD (NEW LOGIC) ---
    final_image_url = ""
    try:
        generate_card() # Generates 'public/twitter_card.png'
        
        # RENAME FILE TO INCLUDE DATE
        # This solves the IFTTT caching issue AND the query string issue
        old_path = "public/twitter_card.png"
        new_filename = f"card_{today_str}.png"
        new_path = f"public/{new_filename}"
        
        # Safety check: ensure public folder exists
        os.makedirs("public", exist_ok=True)
        
        if os.path.exists(old_path):
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(old_path, new_path)
            
            # This is the CLEAN URL (No ?v= parameter needed!)
            final_image_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
            print(f"Twitter Card Renamed to: {new_filename}")
        else:
            print("Error: twitter_card.png was not generated.")
            
    except Exception as e:
        print(f"Screenshot Error: {e}")

    # 5. GENERATE INDEX.HTML
    nuclear_image_url = f"https://raw.githubusercontent.com/RiskIndicator/taiwan-strait-risk-tracker/main/public/{new_filename}"
    
    # 2. Update the HTML Template with this specific URL
    # We force the 'twitter:image' tag to use the nuclear link.
    with open('template.html', 'r', encoding='utf-8') as f:
        template_str = f.read()

    template = Template(template_str)
    rendered_html = template.render(
        # ... your existing variables ...
        risk_score=final_score,
        status_text=status,
        market_score=market_score,
        conflict_score=conflict_score,
        color_code=color,
        daily_summary=summary,
        last_updated=update_time,
        history_json=json.dumps(history),
        report_list=report_links,
        trend_arrow=trend_arrow,
        trend_desc=trend_desc,
        trend_color=trend_color,
        market_evidence=market_data['desc'],
        top_headline=conflict_data['headlines'][0] if conflict_data['headlines'] else "No major conflict keywords detected."
    )

    # 3. FORCE THE META TAG
    # We manually inject the twitter:image tag with the nuclear URL.
    # This ensures the "Big Card" works every time.
    meta_tag = f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{nuclear_image_url}">'
    
    if "</head>" not in rendered_html:
        raise ValueError("No </head> tag found in HTML")
        
    final_html_with_meta = rendered_html.replace("</head>", f"{meta_tag}\n</head>")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html_with_meta)
        
    print(f"Build Complete. Index updated.")

    # 6. OUTPUT FOR GITHUB ACTIONS
    tweet_content = prepare_tweet_text(status, final_score, summary)
    
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
            # 1. Output the Tweet Text
            print("tweet<<EOF", file=fh)
            print(tweet_content, file=fh)
            print("EOF", file=fh)
            # 2. Output the specific Image URL for this run
            print(f"image_url={final_image_url}", file=fh)
    else:
        print(f"\n[LOCAL TEST] Tweet: {tweet_content}")
        print(f"[LOCAL TEST] Image: {final_image_url}")

if __name__ == "__main__":
    main()
