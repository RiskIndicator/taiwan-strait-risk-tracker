import json
import os
from datetime import datetime
import pytz

DATA_FILES = {
    "taiwan": "taiwan_data.json",
    "ai_bubble": "ai_bubble_data.json",
    "fuel": "fuel_cache.json",
    "middle_east": "me_data.json",
    "fiat": "fiat_data.json",
    "supply": "supply_data.json",
    "inequality": "kshape_data.json"
}

ALERTS_OUTPUT_FILE = "active_alerts.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None

def run_orchestrator():
    print("Initializing Master Orchestrator...")
    active_alerts = []
    
    # 1. INGEST ALL DATA
    tw_data = load_json(DATA_FILES["taiwan"]) or {}
    ai_data = load_json(DATA_FILES["ai_bubble"]) or {}
    fuel_data = load_json(DATA_FILES["fuel"]) or {}
    me_data = load_json(DATA_FILES["middle_east"]) or {}
    fiat_data = load_json(DATA_FILES["fiat"]) or {}
    supply_data = load_json(DATA_FILES["supply"]) or {}
    kshape_data = load_json(DATA_FILES["inequality"]) or {}

    # Extract metrics safely
    tw_media_panic = tw_data.get("media_noise", 30)
    tw_physical_change = tw_data.get("daily_change", 0)
    
    ai_score = ai_data.get("bubble_index", 50)
    
    fuel_comm_val = fuel_data.get("comm_val", 350000)
    fuel_days = round((float(fuel_comm_val) / 1000.0) / 16.0, 1) 
    
    me_energy_spike = me_data.get("energy_spike", 0.0)
    
    fiat_score = fiat_data.get("score", 50)
    supply_score = supply_data.get("stress_score", 50)
    kshape_score = kshape_data.get("fracture_score", 50)

    # 2. RUN FULL SYSTEM TRIGGER LOGIC

    # Trigger A: Divergence (Media panic vs physical reality)
    if tw_media_panic >= 80 and abs(tw_physical_change) <= 2:
        active_alerts.append({
            "type": "DIVERGENCE",
            "severity": "ELEVATED",
            "headline": "Taiwan Strait: Media hysteria diverging from physical supply data.",
            "link": "/taiwan.html"
        })

    # Trigger B: Creeping Baseline (Fuel drops below safe threshold)
    if fuel_days < 35:
        active_alerts.append({
            "type": "CREEPING BASELINE",
            "severity": "CRITICAL",
            "headline": f"Global Fuel Reserves Vulnerable: Commercial Buffer at {fuel_days} Days.",
            "link": "/fuel-reserves.html"
        })

    # Trigger C: Macro Cross-Correlation (Supply Chain Stress + Energy Spike)
    if supply_score > 65 and me_energy_spike > 5.0:
        active_alerts.append({
            "type": "CROSS-CORRELATION",
            "severity": "SEVERE",
            "headline": "Systemic Shock: Energy sector volatility compounding global shipping bottlenecks.",
            "link": "/supply-chain.html"
        })
        
    # Trigger D: Societal Fracture (High Wealth Inequality + Capital Flight from Fiat)
    if kshape_score > 70 and fiat_score > 70:
        active_alerts.append({
            "type": "CROSS-CORRELATION",
            "severity": "SEVERE",
            "headline": "Macro Fracture: Extreme wealth compression aligning with fiat capital flight.",
            "link": "/macro.html"
        })

    # Trigger E: Fiat Capital Flight (Sovereign Debt/Currency Crisis)
    if fiat_score > 75:
        active_alerts.append({
            "type": "SYSTEMIC SHOCK",
            "severity": "CRITICAL",
            "headline": "Capital Flight: Severe divergence detected between hard assets and fiat instruments.",
            "link": "/fiat.html"
        })

    # 3. EXPORT TERMINAL FEED
    update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y %H:%M AEST')
    
    output_data = {
        "last_updated": update_time,
        "alert_count": len(active_alerts),
        "alerts": active_alerts
    }

    with open(ALERTS_OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Orchestrator Complete. {len(active_alerts)} active systemic anomalies detected.")

if __name__ == "__main__":
    run_orchestrator()