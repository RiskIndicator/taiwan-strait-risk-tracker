import json
from jinja2 import Template

def main():
    # 1. Load the new Fiat Data from build_fiat.py
    try:
        with open('fiat_data.json', 'r') as f:
            fiat_data = json.load(f)
    except Exception:
        fiat_data = {"score": 50, "desc": "Unknown", "color": "#64748b", "ratio": 0}

    # 2. Load the main history to get the latest Strait Risk score
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
        latest_risk = history[-1]['score'] if history else 30
    except Exception:
        latest_risk = 30

    # 3. Calculate Cycle Positions (0% to 100% across the screen)
    # USA starts past the peak (65%) and gets pushed further right by debt stress
    us_base = 65
    us_shift = (fiat_data['score'] - 50) * 0.4
    us_pos = min(95, max(60, us_base + us_shift))

    # China starts low (20%) and gets pushed up the curve by global conflict scores
    china_base = 20
    china_shift = (latest_risk - 30) * 0.3
    china_pos = min(50, max(15, china_base + china_shift))

    # 4. Render the HTML
    try:
        with open('macro_template.html', 'r', encoding='utf-8') as f:
            template = Template(f.read())

        rendered = template.render(
            us_pos=round(us_pos, 1),
            china_pos=round(china_pos, 1),
            fiat_desc=fiat_data['desc'],
            fiat_color=fiat_data['color'],
            fiat_ratio=fiat_data['ratio']
        )

        with open('macro.html', 'w', encoding='utf-8') as f:
            f.write(rendered)
            
        print("✅ Macro Page Generated: macro.html")
    except Exception as e:
        print(f"❌ Template Error: {e}")

if __name__ == "__main__":
    main()