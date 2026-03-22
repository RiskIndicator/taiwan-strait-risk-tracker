import os
import requests
import feedparser
from jinja2 import Template
from datetime import datetime
import pytz
import json

EIA_API_KEY = os.environ.get("EIA_API_KEY", "")

def fetch_eia_data(series_id):
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={EIA_API_KEY}&frequency=weekly&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json().get("response", {}).get("data", [])
            return data
    except Exception as e:
        print(f"EIA API Error for {series_id}: {e}")
    return None

def build_fuel_index():
    print("Calculating Fuel Reserve Risk...")
    
    spr_score, comm_score, osint_score = 50, 50, 50
    spr_val, comm_val = 0, 0
    spr_desc, comm_desc = "Data unavailable.", "Data unavailable."
    top_headline = "Awaiting OSINT data."

    # 1. SPR Buffer (WCSSTUS1)
    spr_data = fetch_eia_data("WCSSTUS1")
    if spr_data and len(spr_data) > 0:
        current_spr = spr_data[0]['value'] 
        spr_val = round(current_spr / 1000, 1) 
        spr_risk = 100 - ((current_spr - 200000) / 4000) 
        spr_score = int(max(0, min(100, spr_risk)))
        spr_desc = f"SPR at {spr_val}M barrels. " + ("CRITICAL DEPLETION." if spr_score > 75 else "Stable emergency buffer.")

    # 2. Commercial Stocks (WCESTUS1)
    comm_data = fetch_eia_data("WCESTUS1")
    if comm_data and len(comm_data) > 0:
        current_comm = comm_data[0]['value']
        comm_val = round(current_comm / 1000, 1)
        comm_risk = 100 - ((current_comm - 350000) / 1000)
        comm_score = int(max(0, min(100, comm_risk)))
        comm_desc = f"{comm_val}M commercial barrels. " + ("INVENTORY SHORTAGE." if comm_score > 75 else "Standard inventory levels.")

    # 3. OSINT Supply Shock
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=oil+supply+shortage+OPEC+embargo+SPR+release+when:1d&hl=en-US&gl=US&ceid=US:en")
        threat_keywords = ['shortage', 'embargo', 'cut', 'opec', 'halt', 'reserves', 'crisis']
        hit_count = sum(1 for entry in feed.entries[:25] if any(k in entry.title.lower() for k in threat_keywords))
        if feed.entries:
            top_headline = feed.entries[0].title
        osint_score = int(max(0, min(100, hit_count * 5)))
    except Exception:
        pass

    master_score = int((spr_score * 0.4) + (comm_score * 0.4) + (osint_score * 0.2))
    
    if comm_score > 90:
        master_score = max(master_score, comm_score)

    if master_score > 75:
        status, color = "CRITICAL SHORTAGE", "#ef4444"
    elif master_score > 55:
        status, color = "VULNERABLE INVENTORY", "#f59e0b"
    else:
        status, color = "SUPPLY SECURE", "#10b981"

    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M AEST')

    try:
        with open('fuel_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            score=master_score,
            status_text=status,
            color_code=color,
            spr_score=spr_score,
            spr_desc=spr_desc,
            comm_score=comm_score,
            comm_desc=comm_desc,
            osint_score=osint_score,
            top_headline=top_headline,
            update_time=update_time
        )
        
        with open('fuel-reserves.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print("Fuel Reserve Index Generated successfully.")
    except Exception as e:
        print(f"Template Error: {e}")

if __name__ == "__main__":
    build_fuel_index()