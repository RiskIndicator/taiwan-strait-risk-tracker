from html2image import Html2Image
import os

def generate_card():
    # 1. Initialize
    # We set a specific size to match Twitter's "Large Card" format
    hti = Html2Image(output_path='public', size=(1200, 628))

    # Ensure public directory exists
    os.makedirs('public', exist_ok=True)

    # 2. Define the CSS/HTML for the card
    # (This reconstructs the visual card for the screenshot)
    html_str = """
    <div class="card">
        <div class="header">TAIWAN STRAIT RISK INDEX</div>
        <div class="score">30</div>
        <div class="status">STATUS: STABLE</div>
        <div class="footer">taiwanstraittracker.com</div>
    </div>
    """

    css_str = """
    body { background: white; width: 1200px; height: 628px; display: flex; justify-content: center; align-items: center; font-family: sans-serif; }
    .card { background: #f8f9fa; padding: 40px; border-radius: 20px; text-align: center; border: 2px solid #e9ecef; width: 80%; }
    .header { font-size: 30px; color: #666; font-weight: bold; letter-spacing: 2px; margin-bottom: 20px; }
    .score { font-size: 180px; font-weight: 900; color: #2c3e50; line-height: 1; margin: 20px 0; }
    .status { font-size: 40px; color: #27ae60; font-weight: bold; text-transform: uppercase; }
    .footer { margin-top: 30px; font-size: 20px; color: #999; }
    """

    # 3. Take the screenshot
    print("Generating screenshot...")
    hti.screenshot(html_str=html_str, css_str=css_str, save_as='twitter_card.png')
    print("Screenshot generated: public/twitter_card.png")

if __name__ == "__main__":
    generate_card()