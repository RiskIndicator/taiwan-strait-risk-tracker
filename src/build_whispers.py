import feedparser
import json
import os
import re
import html # NEW: to fix the weird &#8217; characters

# ==========================================
# GSN CONTEXT NODES (KOL ROSTER)
# ==========================================
FEEDS = {
    "Peter Zeihan (Geopolitics & Supply Chain)": "https://zeihan.com/feed/",
    "Doomberg (Energy & Industrial Macro)": "https://doomberg.substack.com/feed"
}

def clean_html(raw_html, title):
    # Replace HTML tags with spaces (so words don't get smashed together)
    text = re.sub('<[^<]+>', ' ', raw_html)
    # Fix weird apostrophes and quotes
    text = html.unescape(text)
    # Remove extra spaces/newlines
    text = " ".join(text.split())
    # Strip out Zeihan's annoying boilerplate
    boilerplate = f"The post {title} appeared first on Zeihan on Geopolitics."
    text = text.replace(boilerplate, "")
    
    return text[:800].strip() + "..." # Increased to 800 chars for better context

def fetch_whispers():
    print("GSN TERMINAL: Initiating Deep Context Node Scraping...")
    whispers = []
    
    for author, url in FEEDS.items():
        try:
            print(f"📡 Intercepting {author}...")
            feed = feedparser.parse(url)
            
            if feed.entries:
                latest = feed.entries[0]
                title = latest.get('title', 'No Title')
                
                # Hunt for the actual body content first, fallback to summary
                if 'content' in latest:
                    raw_text = latest.content[0].value
                else:
                    raw_text = latest.get('summary', '') or latest.get('description', '')
                
                # Scrub the data clean
                summary_clean = clean_html(raw_text, title)
                
                whispers.append({
                    "author": author,
                    "title": title,
                    "snippet": summary_clean
                })
                print(f"✅ Secured: {title}")
            else:
                print(f"⚠️ No entries found for {author}.")
                
        except Exception as e:
            print(f"❌ Target offline - {author}: {e}")
            
    # ==========================================
    # EXPORT TO ORCHESTRATOR
    # ==========================================
    os.makedirs('data', exist_ok=True)
    with open('data/whispers.json', 'w', encoding='utf-8') as f:
        json.dump({"whispers": whispers}, f, indent=4)
        
    print(f"GSN TERMINAL: {len(whispers)} Context Nodes successfully compiled to whispers.json.")

if __name__ == "__main__":
    fetch_whispers()