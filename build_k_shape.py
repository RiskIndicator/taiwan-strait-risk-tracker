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
        
        # Every 1% of gap results in a 15px vertical shift
        # Negative gap (Survival > Assets) pushes the bottom card down
        displacement = int(gap * 15) 

        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        with open('inequality_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            fracture_score=round(gap, 1),
            displacement=displacement,
            asset_growth=round((asset_perf-1)*100, 1),
            survival_inflation=round((survival_perf-1)*100, 1),
            last_updated=update_time
        )
        
        with open('inequality.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        # Export for Orchestrator
        kshape_export = {"fracture_score": round(gap, 1), "wealth_gap": float(gap)}
        with open('kshape_data.json', 'w') as f: json.dump(kshape_export, f)
        print("Success: inequality.html generated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_k_shape()