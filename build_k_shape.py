import yfinance as yf
from jinja2 import Template
import json
from datetime import datetime
import pytz

ASSETS = ['SPY', 'VNQ'] 
ESSENTIALS = ['DBA', 'XLP'] 

def build_k_shape():
    print("CALCULATING WEALTH FRACTURE...")
    try:
        data = yf.download(ASSETS + ESSENTIALS, period="6mo")['Close']
        normalized = data / data.iloc[0]
        
        asset_perf = normalized[ASSETS].mean(axis=1).iloc[-1]
        survival_perf = normalized[ESSENTIALS].mean(axis=1).iloc[-1]
        
        gap = (asset_perf - survival_perf) * 100
        score = int(max(0, min(100, 50 + (gap * 2.5))))
        
        if score > 65: status = "WIDENING GAP"
        elif score < 35: status = "WEALTH COMPRESSION"
        else: status = "STABLE TREND"

        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        # Jinja2 Rendering
        with open('inequality_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            fracture_score=round(gap, 1),
            status_text=status,
            asset_growth=round((asset_perf-1)*100, 1),
            survival_inflation=round((survival_perf-1)*100, 1),
            last_updated=update_time
        )
        
        with open('inequality.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print(f"Success: inequality.html generated.")
        
        # --- EXPORT FOR ORCHESTRATOR (Now correctly inside the Try block) ---
        kshape_export = {
            "fracture_score": score,
            "wealth_gap": float(gap)
        }
        with open('kshape_data.json', 'w') as f: json.dump(kshape_export, f)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_k_shape()