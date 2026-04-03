import json
import os
from datetime import datetime
import pytz
from google import genai

# ==============================
# GSN Configuration
# ==============================
API_KEY = os.environ.get("GEMINI_API_KEY")
print("GSN TERMINAL: Gemini key verification:", bool(API_KEY))

client = genai.Client(api_key=API_KEY) if API_KEY else None

DATA_FILES = {
    "taiwan": "data/taiwan_data.json",
    "ai_bubble": "data/ai_bubble_data.json",
    "fuel": "data/fuel_cache.json",
    "middle_east": "data/me_data.json",
    "supply": "data/supply_data.json",
    "inequality": "data/kshape_data.json",
}

ALERTS_OUTPUT_FILE = "data/active_alerts.json"
BRIEFING_OUTPUT_FILE = "data/agentic_briefing.json"

# ==============================
# Utility Functions
# ==============================
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"GSN TERMINAL: WARNING - Failed to decode JSON from {filepath}")
                return None
    return None

# ==============================
# Gemini Agentic Synthesis
# ==============================
def generate_agentic_briefing(metrics):
    print("GSN TERMINAL: Initialising Agentic Synthesis...")

    if not client:
        print("GSN TERMINAL: WARNING - API Key absent. Synthesis suspended.")
        return {
            "risk_score": 5,
            "executive_summary": "AGENT OFFLINE. Awaiting valid API credentials for dynamic synthesis.",
            "correlations": "None - Pipeline Offline."
        }

    prompt = f"""
    You are the central intelligence node of the Global Shift Network.
    Review the following live telemetry. Identify critical cross-correlations.
    
    Current Telemetry:
    - Taiwan Media Panic vs Physical Change: {metrics['tw_media_panic']} vs {metrics['tw_physical_change']}
    - AI Bubble Index: {metrics['ai_score']} / 100
    - Global Fuel Reserves: {metrics['fuel_days']} Days (Stress: {metrics['fuel_stress']}/100)
    - Middle East Energy Spike: +{metrics['me_energy_spike']}%
    - Supply Chain Stress Score: {metrics['supply_score']} / 100
    - Wealth Inequality Fracture Gap: {metrics['kshape_raw_gap']}% (Stress: {metrics['kshape_stress']}/100)

    Response Requirements (Strictly follow this format):
    RISK_SCORE: [1-10 integer]
    SUMMARY: [Clinical, analytical 2-3 sentence executive briefing. Australian English. No dashes.]
    CORRELATIONS: [Brief note on systemic linkage between two metrics.]
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()
        
        lines = raw_text.split('\n')
        score = 5
        summary = "Synthesis failed to parse."
        correlations = "No correlations identified."

        for line in lines:
            if line.startswith("RISK_SCORE:"):
                score = int(''.join(filter(str.isdigit, line)))
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("CORRELATIONS:"):
                correlations = line.replace("CORRELATIONS:", "").strip()

        return {
            "risk_score": score,
            "executive_summary": summary,
            "correlations": correlations
        }

    except Exception as e:
        print(f"GSN TERMINAL: ERROR - Gemini synthesis failed: {e}")
        return {
            "risk_score": 0,
            "executive_summary": "AGENT OFFLINE. Synthesis pipeline encountered a network error.",
            "correlations": "Error State."
        }

# ==============================
# Main Orchestrator
# ==============================
def run_orchestrator():
    print("GSN TERMINAL: Initialising Agentic Master Orchestrator...")
    active_alerts = []

    tw_data = load_json(DATA_FILES["taiwan"]) or {}
    ai_data = load_json(DATA_FILES["ai_bubble"]) or {}
    fuel_data = load_json(DATA_FILES["fuel"]) or {}
    me_data = load_json(DATA_FILES["middle_east"]) or {}
    supply_data = load_json(DATA_FILES["supply"]) or {}
    kshape_data = load_json(DATA_FILES["inequality"]) or {}

    metrics = {
        "tw_media_panic": tw_data.get("media_noise", 30),
        "tw_physical_change": tw_data.get("daily_change", 0),
        "ai_score": ai_data.get("bubble_index", 50),
        "fuel_days": fuel_data.get("comm_days", 35.0), # Direct from Single Source of Truth
        "fuel_stress": fuel_data.get("fuel_stress_score", 0.0),
        "me_energy_spike": me_data.get("energy_spike", 0.0),
        "supply_score": supply_data.get("stress_score", 50),
        "kshape_raw_gap": kshape_data.get("fracture_score", 0.0),
        "kshape_stress": kshape_data.get("stress_score", 0.0),
    }

    intelligence = generate_agentic_briefing(metrics)

    update_time = datetime.now(pytz.timezone("Australia/Brisbane")).strftime("%Y-%m-%d %H:%M:%S")
    
    briefing_payload = {
        "status": "LIVE_INTELLIGENCE",
        "timestamp": update_time,
        "risk_score": intelligence["risk_score"],
        "executive_summary": intelligence["executive_summary"],
        "correlations": intelligence["correlations"]
    }

    with open(BRIEFING_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(briefing_payload, f, indent=4)

    print("GSN TERMINAL: Agentic briefing saved with status LIVE_INTELLIGENCE.")

    if metrics["tw_media_panic"] >= 80 and abs(metrics["tw_physical_change"]) <= 2:
        active_alerts.append({
            "type": "DIVERGENCE",
            "severity": "ELEVATED",
            "headline": "Taiwan Strait: Media hysteria diverging from physical supply data.",
            "link": "taiwan.html",
        })

    if 0 < metrics["fuel_days"] < 25:
        active_alerts.append({
            "type": "CREEPING BASELINE",
            "severity": "CRITICAL",
            "headline": f"Global Fuel Reserves Vulnerable: Commercial Buffer at {metrics['fuel_days']} Days.",
            "link": "fuel-reserves.html",
        })

    if metrics["supply_score"] > 65 and metrics["me_energy_spike"] > 5.0:
        active_alerts.append({
            "type": "CROSS-CORRELATION",
            "severity": "SEVERE",
            "headline": "Systemic Shock: Energy sector volatility compounding global shipping bottlenecks.",
            "link": "supply-chain.html",
        })

    if metrics["kshape_stress"] > 75.0:
        active_alerts.append({
            "type": "SYSTEMIC FRACTURE",
            "severity": "SEVERE",
            "headline": f"Wealth Compression: Cost of survival outpacing asset growth by {metrics['kshape_raw_gap']}%.",
            "link": "inequality.html",
        })

    display_time = datetime.now(pytz.timezone("Australia/Brisbane")).strftime("%d %b %Y %H:%M AEST")
    
    output_data = {
        "last_updated": display_time,
        "alert_count": len(active_alerts),
        "alerts": active_alerts,
    }

    with open(ALERTS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"GSN TERMINAL: Orchestrator Complete. {len(active_alerts)} systemic anomalies identified.")

if __name__ == "__main__":
    run_orchestrator()