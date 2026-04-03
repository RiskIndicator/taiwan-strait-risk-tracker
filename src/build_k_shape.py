import yfinance as yf
import pandas as pd
from jinja2 import Template
import json
from datetime import datetime
import pytz

ASSETS = ['SPY', 'VNQ'] 
ESSENTIALS = ['DBA', 'XLP'] 

def build_k_shape():
    print("CALCULATING MULTI-TIMEFRAME WEALTH FRACTURE...")
    try:
        # Pull 10 years of data
        data = yf.download(ASSETS + ESSENTIALS, period="10y")['Close']
        data = data.ffill().dropna()
        
        # --- 10-Year Data (Monthly) ---
        data_10y = data.resample('ME').last()
        norm_10y = data_10y / data_10y.iloc[0]
        assets_10y = norm_10y[ASSETS].mean(axis=1)
        survival_10y = norm_10y[ESSENTIALS].mean(axis=1)
        
        # --- 1-Year Data (Weekly) ---
        cutoff_1y = data.index.max() - pd.DateOffset(years=1)
        data_1y = data[data.index >= cutoff_1y].resample('W-FRI').last()
        norm_1y = data_1y / data_1y.iloc[0]
        assets_1y = norm_1y[ASSETS].mean(axis=1)
        survival_1y = norm_1y[ESSENTIALS].mean(axis=1)
        
        # Calculate headline metrics
        asset_perf_1y = assets_1y.iloc[-1]
        survival_perf_1y = survival_1y.iloc[-1]
        gap_1y = (asset_perf_1y - survival_perf_1y) * 100
        
        # GSN Normalisation: 25% Gap = 100 Systemic Stress
        max_threshold = 25.0
        stress_score = min(max((gap_1y / max_threshold) * 100, 0), 100.0)

        # Prepare chart JSON
        dates_10y_json = [d.strftime('%b %Y') for d in assets_10y.index]
        chart_assets_10y = [round((val - 1) * 100, 2) for val in assets_10y]
        chart_survival_10y = [round((val - 1) * 100, 2) for val in survival_10y]

        dates_1y_json = [d.strftime('%d %b %Y') for d in assets_1y.index]
        chart_assets_1y = [round((val - 1) * 100, 2) for val in assets_1y]
        chart_survival_1y = [round((val - 1) * 100, 2) for val in survival_1y]

        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        with open('templates/inequality_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            fracture_score=round(gap_1y, 1),
            asset_growth=round((asset_perf_1y-1)*100, 1),
            survival_inflation=round((survival_perf_1y-1)*100, 1),
            last_updated=update_time,
            dates_10y=json.dumps(dates_10y_json),
            assets_10y=json.dumps(chart_assets_10y),
            survival_10y=json.dumps(chart_survival_10y),
            dates_1y=json.dumps(dates_1y_json),
            assets_1y=json.dumps(chart_assets_1y),
            survival_1y=json.dumps(chart_survival_1y)
        )
        
        with open('inequality.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        # Export for Orchestrator and Macro Dashboard
        kshape_export = {
            "fracture_score": round(gap_1y, 1), 
            "stress_score": round(stress_score, 1)
        }
        with open('data/kshape_data.json', 'w') as f: 
            json.dump(kshape_export, f)
            
        print("Success: inequality.html generated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_k_shape()