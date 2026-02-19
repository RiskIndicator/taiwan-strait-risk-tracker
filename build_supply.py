import yfinance as yf
import json
from datetime import datetime
import pytz

def build_supply_chain():
    print("CALCULATING SUPPLY CHAIN STRESS...")
    try:
        # BDRY (Dry Bulk Shipping Freight), USO (Crude Oil)
        data = yf.download(['BDRY', 'USO'], period="3mo")['Close']
        normalized = data / data.iloc[0]
        
        # If shipping and oil are spiking, the supply chain is fracturing
        shipping_stress = (normalized['BDRY'].iloc[-1] - 1) * 100
        energy_stress = (normalized['USO'].iloc[-1] - 1) * 100
        
        base_score = 50 + (shipping_stress * 0.6) + (energy_stress * 0.4)
        score = int(max(0, min(100, base_score)))
        
        if score > 70: status = "SEVERE BOTTLENECKS"
        elif score > 55: status = "ELEVATED FRICTION"
        else: status = "SUPPLY FLOWING"

        output = {
            "score": score,
            "status": status,
            "shipping_trend": round(shipping_stress, 1),
            "updated": datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')
        }
        
        with open('supply_chain.json', 'w') as f:
            json.dump(output, f)
        print(f"Success: Supply Chain Score {score}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_supply_chain()
