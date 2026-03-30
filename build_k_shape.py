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
        # Download data and forward-fill any missing daily values
        data = yf.download(ASSETS + ESSENTIALS, period="6mo")['Close']
        data = data.ffill().dropna()
        
        normalized = data / data.iloc[0]
        
        asset_series = normalized[ASSETS].mean(axis=1)
        survival_series = normalized[ESSENTIALS].mean(axis=1)
        
        asset_perf = asset_series.iloc[-1]
        survival_perf = survival_series.iloc[-1]
        
        gap = (asset_perf - survival_perf) * 100
        
        # Prepare historical data for the chart (converted to % growth)
        dates = [d.strftime('%b %d') for d in asset_series.index]
        asset_chart_data = [round((val - 1) * 100, 2) for val in asset_series]
        survival_chart_data = [round((val - 1) * 100, 2) for val in survival_series]

        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        with open('inequality_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            fracture_score=round(gap, 1),
            asset_growth=round((asset_perf-1)*100, 1),
            survival_inflation=round((survival_perf-1)*100, 1),
            last_updated=update_time,
            chart_dates=json.dumps(dates),
            chart_assets=json.dumps(asset_chart_data),
            chart_survival=json.dumps(survival_chart_data)
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