import yfinance as yf
from jinja2 import Template
from datetime import datetime
import pytz

def build_supply_chain():
    print("CALCULATING SUPPLY CHAIN STRESS...")
    try:
        data = yf.download(['BDRY', 'USO'], period="3mo")['Close']
        normalized = data / data.iloc[0]
        
        shipping_stress = (normalized['BDRY'].iloc[-1] - 1) * 100
        energy_stress = (normalized['USO'].iloc[-1] - 1) * 100
        
        score = int(max(0, min(100, 50 + (shipping_stress * 0.6) + (energy_stress * 0.4))))
        status = "SEVERE BOTTLENECKS" if score > 70 else "ELEVATED FRICTION" if score > 55 else "SUPPLY FLOWING"
        update_time = datetime.now(pytz.timezone('Australia/Brisbane')).strftime('%d %b %Y')

        # Jinja2 Rendering
        with open('supply_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            score=score,
            status_text=status,
            shipping=round(shipping_stress, 1),
            energy=round(energy_stress, 1),
            last_updated=update_time
        )
        
        with open('supply-chain.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print(f"Success: supply-chain.html generated.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_supply_chain()
