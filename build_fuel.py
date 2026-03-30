import os
import requests
import feedparser
from jinja2 import Template
from datetime import datetime
import pytz
import json
import time

EIA_API_KEY = os.environ.get("EIA_API_KEY", "")
CACHE_FILE = "fuel_cache.json"

def fetch_eia_data(series_id, max_retries=3):
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={EIA_API_KEY}&frequency=weekly&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json().get("response", {}).get("data", [])
                if data:
                    return data[0]['value']
            print(f"EIA API attempt {attempt + 1} failed with status {response.status_code}.")
        except requests.exceptions.RequestException as e:
            print(f"EIA API connection attempt {attempt + 1} failed: {e}")
        
        time.sleep(5 * (attempt + 1))
        
    return None

def build_fuel_index():
    print("Calculating Days of Supply...")
    
    daily_consumption = 16.0 
    comm_val, spr_val = None, None
    top_headline = "Awaiting OSINT data."
    is_cached = False

    if EIA_API_KEY:
        comm_val = fetch_eia_data("WCESTUS1")
        spr_val = fetch_eia_data("WCSSTUS1")

    if comm_val is None or spr_val is None:
        print("API failed. Attempting to load from cache...")
        is_cached = True
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                comm_val = cache.get("comm_val", 350000)
                spr_val = cache.get("spr_val", 350000)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No cache found. Using hardcoded baselines.")
            comm_val = 350000
            spr_val = 350000
    else:
        with open(CACHE_FILE, 'w') as f:
            json.dump({"comm_val": comm_val, "spr_val": spr_val}, f)

    comm_m = float(comm_val) / 1000.0
    spr_m = float(spr_val) / 1000.0
    
    comm_days = round(comm_m / daily_consumption, 1)
    spr_days = round(spr_m / daily_consumption, 1)
    total_days = round(comm_days + spr_days, 1)

    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=oil+supply+OR+crude+inventory+when:1d&hl=en-US&gl=US&ceid=US:en")
        if feed.entries:
            top_headline = feed.entries[0].title
    except Exception:
        pass

    if total_days < 35:
        status, color = "CRITICAL DEPLETION", "#ef4444"
    elif total_days < 50:
        status, color = "VULNERABLE", "#f59e0b"
    else:
        status, color = "SUPPLY SECURE", "#10b981"
        
    iea_mandate_pct = min(100, int((total_days / 90) * 100))

    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M AEST')
    if is_cached:
        update_time += " (Cached Data)"

    try:
        with open('fuel_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            days_buffer=total_days,
            status_text=status,
            color_code=color,
            comm_days=comm_days,
            comm_m=int(comm_m),
            spr_days=spr_days,
            spr_m=int(spr_m),
            iea_pct=iea_mandate_pct,
            top_headline=top_headline,
            last_updated=update_time
        )
        
        with open('fuel-reserves.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print("Fuel Reserve Countdown Generated successfully.")
    except Exception as e:
        print(f"Template Error: {e}")

if __name__ == "__main__":
    build_fuel_index()