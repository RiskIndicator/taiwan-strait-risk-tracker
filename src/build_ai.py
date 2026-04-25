import yfinance as yf
import feedparser
from textblob import TextBlob
from jinja2 import Template
import json
import numpy as np
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
MAG_7 = ['NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'TSLA', 'AAPL']

def get_capital_frenzy():
    print("Fetching Mag 7 Valuation Data...")
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
        # Linear mapping: 20 PE = 0 Threat, 60 PE = 100 Threat
        score = (avg_mag7_pe - 20) * 2.5
        return int(max(0, min(100, score))), round(avg_mag7_pe, 1)
    except:
        return 50, 0.0

def get_compute_bottleneck():
    print("Calculating Physical Compute & Energy Constraints...")
    try:
        fuel_stress = 50
        supply_stress = 50
        
        # Cross-reference existing GSN Terminal Data!
        if os.path.exists('data/fuel_cache.json'):
            with open('data/fuel_cache.json', 'r') as f:
                fuel_data = json.load(f)
                fuel_stress = fuel_data.get('fuel_stress_score', 50)
                
        if os.path.exists('data/supply_data.json'):
            with open('data/supply_data.json', 'r') as f:
                supply_data = json.load(f)
                supply_stress = supply_data.get('stress_score', 50)
                
        # If the physical world is stressed, AI scaling is threatened
        bottleneck_score = (fuel_stress * 0.5) + (supply_stress * 0.5)
        return int(max(0, min(100, bottleneck_score)))
    except:
        return 55

def get_agi_timeline():
    print("Analysing AGI Breakthrough Velocity...")
    try:
        # Scrape news for AGI timeline shifts
        rss_url = "https://news.google.com/rss/search?q=AGI+Artificial+General+Intelligence+timeline&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        # Look for acceleration trigger words in the headlines
        urgency_words = ['sooner', 'breakthrough', 'close', 'imminent', 'fast', 'achieve', 'accelerate', 'ahead']
        urgency_mentions = sum(1 for entry in feed.entries[:20] if any(w in entry.title.lower() for w in urgency_words))
        
        # Base AGI consensus is roughly 5.0 years out. High urgency drops the timeline.
        base_years = 5.0
        adjusted_years = max(0.5, base_years - (urgency_mentions * 0.3))
        
        # Threat Math: 10 years out = 0 Threat. 0 years out = 100 Threat.
        score = max(0, min(100, (10 - adjusted_years) * 10))
        return int(score), round(adjusted_years, 1)
    except:
        return 60, 4.0

def get_color_code(score):
    if score < 40: return "#10b981" # Green
    elif score < 65: return "#f59e0b" # Yellow
    else: return "#ef4444" # Red

def build_index():
    print("ASSEMBLING AI DISRUPTION INDEX...")
    
    capital_score, avg_pe = get_capital_frenzy()
    compute_score = get_compute_bottleneck()
    agi_score, agi_years = get_agi_timeline()
    
    # Calculate Disruption Score (Weighted)
    final_score = int((agi_score * 0.4) + (compute_score * 0.3) + (capital_score * 0.3))
    
    if final_score < 40: status = "LINEAR PROGRESSION"
    elif final_score < 65: status = "ACCELERATING DISRUPTION"
    elif final_score < 85: status = "STRUCTURAL STRAIN"
    else: status = "SINGULARITY THRESHOLD"
    
    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M')

    # EXPORT 1: The JSON payload for the Terminal UI
    ai_export = {
        "disruption_index": final_score,
        "agi_countdown": f"{agi_years} Years",
        "capital_score": capital_score,
        "compute_score": compute_score
    }
    
    # Save with the NEW name the frontend is looking for
    with open('data/ai_disruption_data.json', 'w') as f: 
        json.dump(ai_export, f)
    print("Success: ai_disruption_data.json generated.")

    # EXPORT 2: The HTML Page
    try:
        with open('templates/ai_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered_html = template.render(
            final_score=final_score,
            status_text=status,
            agi_years=agi_years,
            agi_score=agi_score,
            compute_score=compute_score,
            capital_score=capital_score,
            avg_pe=avg_pe,
            last_updated=update_time,
            color_code=get_color_code(final_score)
        )

        # Output to the NEW HTML filename
        with open('ai-disruption.html', 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        print("Success: ai-disruption.html generated.")
    except Exception as e:
        print(f"Note: HTML not generated. Awaiting template update. Error: {e}")

if __name__ == "__main__":
    build_index()