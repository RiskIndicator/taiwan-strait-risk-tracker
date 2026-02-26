import yfinance as yf
from jinja2 import Template
from datetime import datetime
import pytz
import json

def build_fiat_confidence():
    print("CALCULATING FIAT SOVEREIGNTY...")
    try:
        raw_data = yf.download(['GLD', 'BTC-USD', 'TLT', 'UUP'], period="3mo")['Close']
        
        data = raw_data.ffill().dropna()
        
        normalized = data / data.iloc[0]
        
        hard_assets = (normalized['GLD'].iloc[-1] + normalized['BTC-USD'].iloc[-1]) / 2
        fiat_assets = (normalized['TLT'].iloc[-1] + normalized['UUP'].iloc[-1]) / 2
        
        divergence = (hard_assets - fiat_assets) * 100
        score = int(max(0, min(100, 50 + (divergence * 1.5))))
        
        status = "CAPITAL FLIGHT" if score > 75 else "EROSION OF TRUST" if score > 55 else "SYSTEM CONFIDENCE HIGH"
        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        # Jinja2 Rendering for your existing fiat page
        with open('fiat_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            score=score,
            status_text=status,
            hard_trend=round((hard_assets-1)*100, 1),
            fiat_trend=round((fiat_assets-1)*100, 1),
            last_updated=update_time
        )
        
        with open('fiat.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print(f"Success: fiat.html generated.")

        # --- NEW EXPORT FOR MACRO PAGE ---
        color = "#ef4444" if score > 75 else "#f59e0b" if score > 55 else "#10b981"
        macro_data = {
            "score": score,
            "desc": status,
            "color": color,
            "ratio": round(float(divergence), 2)
        }
        with open('fiat_data.json', 'w') as f:
            json.dump(macro_data, f)
        print("Success: fiat_data.json exported for Macro dashboard.")
        # ---------------------------------

    except Exception as e:
        print(f"Error: {e}")
        # Create fallback data if the API fails
        fallback = {"score": 50, "desc": "Data Error", "color": "#64748b", "ratio": 0}
        with open('fiat_data.json', 'w') as f:
            json.dump(fallback, f)

if __name__ == "__main__":
    build_fiat_confidence()