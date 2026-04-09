import yfinance as yf
import feedparser
from jinja2 import Template
from datetime import datetime
import pytz
import json

def build_middle_east_index():
    print("CALCULATING MIDDLE EAST WAR RISK...")
    
    try:
        # 1. Energy Shock Index (Brent Crude)
        oil = yf.Ticker("BZ=F").history(period="1mo")
        current_oil = oil['Close'].iloc[-1]
        avg_oil = oil['Close'].mean()
        oil_spike = ((current_oil - avg_oil) / avg_oil) * 100
        
        # GSN Patch: Negative oil spikes mean baseline nominal risk (50), not "peace" (0).
        if oil_spike < 0:
            energy_score = 50
            energy_desc = f"Oil markets absorbing kinetic action (Premium: {round(oil_spike, 1)}%)."
        else:
            energy_score = int(min(100, 50 + (oil_spike * 5)))
            energy_desc = f"Brent Crude diverging +{round(oil_spike, 1)}% from 30 day average." if oil_spike > 2 else "Oil markets absorbing kinetic action."
    except Exception:
        energy_score = 50
        oil_spike = 0.0
        energy_desc = "Energy data unavailable."

    try:
        # 2. Defense Sector Premium (War Pricing)
        ita = yf.Ticker("ITA").history(period="5d")
        spy = yf.Ticker("SPY").history(period="5d")
        ita_change = (ita['Close'].iloc[-1] - ita['Open'].iloc[0]) / ita['Open'].iloc[0]
        spy_change = (spy['Close'].iloc[-1] - spy['Open'].iloc[0]) / spy['Open'].iloc[0]
        
        defense_divergence = (ita_change - spy_change) * 100
        
        # GSN Patch: Negative divergence stays at baseline 50
        if defense_divergence < 0:
            defense_score = 50
        else:
            defense_score = int(min(100, 50 + (defense_divergence * 10)))
            
        defense_desc = "Capital rotating into defense contractors." if defense_divergence > 1 else "Normal sector variance."
    except Exception:
        defense_score = 50
        defense_desc = "Defense data unavailable."

    try:
        # 3. Regional Contagion OSINT (Expanded Dragnet)
        # GSN Patch: Added Lebanon, Syria, Iraq, Saudi, Yemen
        rss_url = "https://news.google.com/rss/search?q=Iran+OR+Israel+OR+Lebanon+OR+Syria+OR+Saudi+OR+Yemen+OR+Iraq+missile+OR+strike+OR+attack+when:1d&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        threat_keywords = ['strike', 'missile', 'bomb', 'base', 'retaliation', 'hezbollah', 'houthi', 'lebanon', 'syria', 'iraq', 'saudi', 'yemen', 'idf', 'irgc']
        hit_count = 0
        top_headline = "Awaiting regional OSINT data."
        
        if feed.entries:
            top_headline = feed.entries[0].title
            for entry in feed.entries[:25]:
                title = entry.title.lower()
                if any(k in title for k in threat_keywords):
                    hit_count += 1
        
        # 25 hits * 4 = max score of 100
        osint_score = int(max(0, min(100, hit_count * 4)))
    except Exception:
        osint_score = 50
        top_headline = "News feed unavailable."

    # Calculate Base Master Score
    master_score = int((energy_score * 0.4) + (defense_score * 0.3) + (osint_score * 0.3))
    
    # GSN Systemic Overrides
    if energy_score > 90:
        master_score = max(master_score, energy_score)
    elif energy_score > 80:
        master_score = max(master_score, 85)
        
    # NEW OVERRIDE: If kinetic war is raging but markets ignore it, force the score up.
    if osint_score > 80:
        master_score = max(master_score, osint_score)
        
    if master_score > 70:
        status = "CRITICAL ESCALATION"
        color = "#ef4444"
    elif master_score > 55:
        status = "ELEVATED CONTAGION"
        color = "#f59e0b"
    else:
        status = "CONTAINED CONFLICT"
        color = "#10b981"

    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M AEST')

    try:
        with open('templates/middle_east_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            risk_index=master_score,
            status_text=status,
            color_code=color,
            energy_spike=round(oil_spike, 1),
            defense_rotation=defense_score,
            gulf_contagion=osint_score,
            top_headline=top_headline,
            last_updated=update_time
        )
        
        with open('middle-east.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print(f"✅ Middle East Index Generated: middle-east.html (Score: {master_score})")
        
        me_export = {
            "risk_index": master_score,
            "energy_spike": float(oil_spike)
        }
        with open('data/me_data.json', 'w') as f: json.dump(me_export, f)

    except Exception as e:
        print(f"❌ Template Error: {e}")

if __name__ == "__main__":
    build_middle_east_index()