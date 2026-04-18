import feedparser
import json
import os
import re
import html
from datetime import datetime

# ==========================================
# GSN CONTEXT NODES (KOL ROSTER)
# ==========================================
FEEDS = {
    "Mainstream Consensus (CNBC Macro)": "https://search.cnbc.com/rs/search/combinedcms/view.xml?id=10000664", # NEW: Mainstream Finance News
    "Peter Zeihan (Geopolitics & Supply Chain)": "https://zeihan.com/feed/",
    "Doomberg (Energy & Industrial Macro)": "https://doomberg.substack.com/feed",
    "Gary's Economics (Inequality & Policy)": "https://garyseconomics.substack.com/feed",
    "Ray Dalio (Macro Debt Cycles)": "https://raydalio.substack.com/feed",
    "Michael Pettis (Global Trade Imbalances)": "https://carnegieendowment.org/rss/experts/414",
    "Lyn Alden (Macro & Energy)": "https://www.lynalden.com/feed/",
    "Arthur Hayes (Crypto & Fiat Debasement)": "https://cryptohayes.substack.com/feed"
}

def clean_html(raw_html, title):
    text = re.sub('<[^<]+>', ' ', raw_html)
    text = html.unescape(text)
    text = " ".join(text.split())
    boilerplate = f"The post {title} appeared first on Zeihan on Geopolitics."
    text = text.replace(boilerplate, "")
    return text[:800].strip() + "..."

def fetch_whispers():
    print("GSN TERMINAL: Initiating Deep Context Node Scraping...")
    
    ledger_path = 'data/whisper_ledger.json'
    os.makedirs('data', exist_ok=True)
    
    # 1. Load the existing memory bank (or start a new one)
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                ledger = json.load(f)
        except Exception:
            ledger = {"whispers": []}
    else:
        ledger = {"whispers": []}
        
    # Get a list of titles we already have so we don't duplicate them
    existing_titles = [w['title'] for w in ledger.get('whispers', [])]
    new_count = 0
    
    for author, url in FEEDS.items():
        try:
            print(f"📡 Intercepting {author}...")
            feed = feedparser.parse(url)
            
            if feed.entries:
                latest = feed.entries[0]
                title = latest.get('title', 'No Title')
                
                # Check for duplicates
                if title in existing_titles:
                    print(f"   ⏭️ Already logged: {title}")
                    continue
                
                if 'content' in latest:
                    raw_text = latest.content[0].value
                else:
                    raw_text = latest.get('summary', '') or latest.get('description', '')
                
                summary_clean = clean_html(raw_text, title)
                
                # Add new intelligence to the ledger
                ledger['whispers'].append({
                    "author": author,
                    "title": title,
                    "snippet": summary_clean,
                    "status": "UNPUBLISHED",
                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                new_count += 1
                print(f"   ✅ Secured New Intel: {title}")
            else:
                print(f"⚠️ No entries found for {author}.")
                
        except Exception as e:
            print(f"❌ Target offline - {author}: {e}")
            
    # ==========================================
    # SAVE THE LEDGER
    # ==========================================
    with open(ledger_path, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=4)
        
    print(f"GSN TERMINAL: System memory updated. Added {new_count} new context nodes.")

if __name__ == "__main__":
    fetch_whispers()