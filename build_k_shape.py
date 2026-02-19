import yfinance as yf
import json
from datetime import datetime
import pytz

# Assets (The "Haves") vs Essentials (The "Have Nots")
ASSETS = ['SPY', 'VNQ'] # S&P 500, Real Estate
ESSENTIALS = ['DBA', 'XLP'] # Agriculture/Food, Consumer Staples

def build_k_shape():
    print("CALCULATING WEALTH FRACTURE...")
    try:
        data = yf.download(ASSETS + ESSENTIALS, period="6mo")['Close']
        normalized = data / data.iloc[0]
        
        asset_perf = normalized[ASSETS].mean(axis=1).iloc[-1]
        survival_perf = normalized[ESSENTIALS].mean(axis=1).iloc[-1]
        
        # Calculate the divergence gap
        gap = (asset_perf - survival_perf) * 100
        score = int(max(0, min(100, 50 + (gap * 2.5))))
        
        if score > 65: status = "WIDENING GAP"
        elif score < 35: status = "WEALTH COMPRESSION"
        else: status = "STABLE TREND"

        output = {
            "score": score,
            "status": status,
            "gap_percentage": round(gap, 1),
            "updated": datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')
        }
        
        with open('inequality.json', 'w') as f:
            json.dump(output, f)
        print(f"Success: K-Shape Score {score}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_k_shape()
