import json
import os
from datetime import datetime
import pytz
import google.generativeai as genai

# Configure your API Key here. 
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

DATA_FILES = {
    "taiwan": "taiwan_data.json",
    "ai_bubble": "ai_bubble_data.json",
    "fuel": "fuel_cache.json",
    "middle_east": "me_data.json",
    "supply": "supply_data.json",
    "inequality": "kshape_data.json" # Fiat replaced with Inequality
}

ALERTS_OUTPUT_FILE = "active_alerts.json"
BRIEFING_OUTPUT_FILE = "agentic_briefing.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None

def generate_agentic_briefing(metrics):
    """
    Sends the raw metrics to the LLM to generate a synthesised system health report.
    """
    print("Engaging Agentic Model for Synthesis...")
    
    if API_KEY == "PASTE_YOUR_API_KEY_HERE_IF_TESTING" or not API_KEY:
        print("WARNING: No API Key found. Skipping dynamic synthesis.")
        return "AGENT OFFLINE. Awaiting valid API credentials for dynamic synthesis."
    
    prompt = f"""
    You are the central intelligence node of the Global Shift Network, a dashboard monitoring real-time global macro risk.
    Review the following live telemetry and identify any critical cross-correlations or systemic risks.
    Provide a clinical, highly analytical 2-3 sentence executive briefing. Do not use pleasantries.
    
    Current Telemetry:
    - Taiwan Media Panic vs Physical Change: {metrics['tw_media_panic']} vs {metrics['tw_physical_change']}
    - AI Bubble Index: {metrics['ai_score']} / 100
    - Global Fuel Reserves: {metrics['fuel_days']} Days of commercial buffer
    - Middle East Energy Spike: +{metrics['me_energy_spike']}%
    - Supply Chain Stress Score: {metrics['supply_score']} / 100
    - Wealth Inequality Fracture Gap: {metrics['kshape_score']}%
    """
    
    try:
        # Using Gemini 1.5 Flash for fast, cheap, and reliable text synthesis
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Agentic Synthesis Failed: {e}")
        return "AGENT OFFLINE. Synthesis pipeline encountered an error."

def run_orchestrator():
    print("Initializing Agentic Master Orchestrator...")
    active_alerts = []
    
    # 1. INGEST ALL DATA
    tw_data = load_json(DATA_FILES["taiwan"]) or {}
    ai_data = load_json(DATA_FILES["ai_bubble"]) or {}
    fuel_data = load_json(DATA_FILES["fuel"]) or {}
    me_data = load_json(DATA_FILES["middle_east"]) or {}
    supply_data = load_json(DATA_FILES["supply"]) or {}
    kshape_data = load_json(DATA_FILES["inequality"]) or {}

    # Extract metrics safely
    metrics = {
        "tw_media_panic": tw_data.get("media_noise", 30),
        "tw_physical_change": tw_data.get("daily_change", 0),
        "ai_score": ai_data.get("bubble_index", 50),
        "fuel_days": round((float(fuel_data.get("comm_val", 350000)) / 1000.0) / 16.0, 1) if fuel_data else 0,
        "me_energy_spike": me_data.get("energy_spike", 0.0),
        "supply_score": supply_data.get("stress_score", 50),
        "kshape_score": kshape_data.get("fracture_score", 50)
    }

    # 2. ENGAGE AGENT FOR SYNTHESIS
    agent_briefing = generate_agentic_briefing(metrics)
    
    with open(BRIEFING_OUTPUT_FILE, 'w') as f:
        json.dump({"agent_briefing": agent_briefing}, f)
        print("Agentic briefing saved.")

    # 3. RUN FULL SYSTEM TRIGGER LOGIC
    # Trigger A: Divergence (Media panic vs physical reality)
    if metrics["tw_media_panic"] >= 80 and abs(metrics["tw_physical_change"]) <= 2:
        active_alerts.append({
            "type": "DIVERGENCE",
            "severity": "ELEVATED",
            "headline": "Taiwan Strait: Media hysteria diverging from physical supply data.",
            "link": "/taiwan.html"
        })

    # Trigger B: Creeping Baseline (Fuel drops below safe threshold)
    if metrics["fuel_days"] > 0 and metrics["fuel_days"] < 35:
        active_alerts.append({
            "type": "CREEPING BASELINE",
            "severity": "CRITICAL",
            "headline": f"Global Fuel Reserves Vulnerable: Commercial Buffer at {metrics['fuel_days']} Days.",
            "link": "/fuel-reserves.html"
        })

    # Trigger C: Macro Cross-Correlation (Supply Chain Stress + Energy Spike)
    if metrics["supply_score"] > 65 and metrics["me_energy_spike"] > 5.0:
        active_alerts.append({
            "type": "CROSS-CORRELATION",
            "severity": "SEVERE",
            "headline": "Systemic Shock: Energy sector volatility compounding global shipping bottlenecks.",
            "link": "/supply-chain.html"
        })
        
    # Trigger D: Societal Fracture (High Wealth Inequality) - Updated for new metric
    if metrics["kshape_score"] > 15.0: # Adjust this threshold based on what constitutes a "critical" gap
        active_alerts.append({
            "type": "SYSTEMIC FRACTURE",
            "severity": "SEVERE",
            "headline": f"Wealth Compression: Cost of survival outpacing asset growth by {metrics['kshape_score']}%.",
            "link": "/inequality.html"
        })

    # 4. EXPORT TERMINAL FEED
    brisbane_tz = pytz.timezone('Australia/Brisbane')
    update_time = datetime.now(brisbane_tz).strftime('%d %b %Y %H:%M AEST')
    
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