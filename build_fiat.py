import yfinance as yf
import json
from datetime import datetime
import pytz

def build_fiat_confidence():
    print("CALCULATING FIAT SOVEREIGNTY...")
    try:
        # GLD (Gold), BTC-USD (Bitcoin), TLT (20+ Yr Treasury Bonds), UUP (US Dollar Index)
        tickers = ['GLD', 'BTC-USD', 'TLT', 'UUP']
        data = yf.download(tickers, period="3mo")['Close']
        normalized = data / data.iloc[0]
        
        # Hard Assets (Fleeing the system)
        hard_assets = (normalized['GLD'].iloc[-1] + normalized['BTC-USD'].iloc[-1]) / 2
        # Fiat Assets (Trusting the system)
        fiat_assets = (normalized['TLT'].iloc[-1] + normalized['UUP'].iloc[-1]) / 2
        
        # If Hard Assets outpace Fiat Assets, confidence is dropping.
        # Note: A high score here means HIGH risk/low confidence in fiat.
        divergence = (hard_assets - fiat_assets) * 100
        score = int(max(0, min(100, 50 + (divergence * 1.5))))
        
        if score > 75: status = "CAPITAL FLIGHT (DEBASEMENT)"
        elif score > 55: status = "EROSION OF TRUST"
        else: status = "SYSTEM CONFIDENCE HIGH"

        output = {
            "score": score,
            "status": status,
            "updated": datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')
        }
        
        with open('fiat_sovereignty.json', 'w') as f:
            json.dump(output, f)
        print(f"Success: Fiat Sovereignty Score {score}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_fiat_confidence()
