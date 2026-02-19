import yfinance as yf
from jinja2 import Template
from datetime import datetime
import pytz

def build_fiat_confidence():
    print("CALCULATING FIAT SOVEREIGNTY...")
    try:
        data = yf.download(['GLD', 'BTC-USD', 'TLT', 'UUP'], period="3mo")['Close']
        normalized = data / data.iloc[0]
        
        hard_assets = (normalized['GLD'].iloc[-1] + normalized['BTC-USD'].iloc[-1]) / 2
        fiat_assets = (normalized['TLT'].iloc[-1] + normalized['UUP'].iloc[-1]) / 2
        
        divergence = (hard_assets - fiat_assets) * 100
        score = int(max(0, min(100, 50 + (divergence * 1.5))))
        
        status = "CAPITAL FLIGHT" if score > 75 else "EROSION OF TRUST" if score > 55 else "SYSTEM CONFIDENCE HIGH"
        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        # Jinja2 Rendering
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
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_fiat_confidence()
