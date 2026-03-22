import os
import requests
import feedparser
from jinja2 import Template
from datetime import datetime
import pytz

EIA_API_KEY = os.environ.get("EIA_API_KEY", "")

def fetch_eia_data(series_id):
    url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={EIA_API_KEY}&frequency=weekly&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", {}).get("data", [])
    except Exception as e:
        print(f"API Error for {series_id}: {e}")
    return None

def build_fuel_index():
    print("Calculating Days of Supply...")
    
    # Fallbacks to prevent Exit Code 1 crashes
    comm_days, spr_days, total_days = 0.0, 0.0, 0.0
    comm_m, spr_m = 0.0, 0.0
    top_headline = "Awaiting OSINT data."
    
    # Approx daily benchmark refinery input in millions of barrels
    daily_consumption = 16.0 

    comm_data = fetch_eia_data("WCESTUS1")
    if comm_data and len(comm_data) > 0:
        comm_m = comm_data[0]['value'] / 1000
        comm_days = round(comm_m / daily_consumption, 1)

    spr_data = fetch_eia_data("WCSSTUS1")
    if spr_data and len(spr_data) > 0:
        spr_m = spr_data[0]['value'] / 1000
        spr_days = round(spr_m / daily_consumption, 1)
        
    total_days = round(comm_days + spr_days, 1)

    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=oil+supply+shortage+OPEC+embargo+SPR+release+when:1d&hl=en-US&gl=US&ceid=US:en")
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

    try:
        with open('fuel_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            total_days=total_days,
            status_text=status,
            color_code=color,
            comm_days=comm_days,
            comm_m=int(comm_m),
            spr_days=spr_days,
            spr_m=int(spr_m),
            iea_pct=iea_mandate_pct,
            top_headline=top_headline,
            update_time=update_time
        )
        
        with open('fuel-reserves.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print("Fuel Reserve Countdown Generated successfully.")
    except Exception as e:
        print(f"Template Error: {e}")

if __name__ == "__main__":
    build_fuel_index()