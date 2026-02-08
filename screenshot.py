from html2image import Html2Image
import time

# Initialize
hti = Html2Image(output_path='public') # Save directly to your public/build folder

# Define the HTML for the card specifically (or load your index.html)
# For best results, I recommend generating a dedicated 'card.html' 
# that contains ONLY your Risk Card with inline CSS, 
# ensuring it looks perfect at 1200x600px (Twitter's preferred size).

html_content = """
<html>
  <head>
    <style>
      body { width: 1200px; height: 628px; background: #f4f4f9; display: flex; align-items: center; justify-content: center; font-family: sans-serif; }
      .card { /* Copy your CSS classes from your main site here */ 
          background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;
      }
      .score { font-size: 120px; font-weight: bold; color: #d9534f; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Taiwan Strait Risk Index</h1>
      <div class="score">30</div> <p>Status: STABLE</p>
    </div>
  </body>
</html>
"""

# Snapshot
hti.screenshot(html_str=html_content, save_as='twitter_card.png', size=(1200, 628))
print("Screenshot generated: public/twitter_card.png")
