import os
from datetime import datetime

# GSN Terminal: Sitemap Generator Calibration
# Target: Technical SEO Optimisation

BASE_URL = "https://taiwanstraittracker.com"
ROOT_DIR = "."
ARTICLES_DIR = "articles"

def generate_sitemap():
    print("GSN TERMINAL: Initialising sitemap recalibration...")
    
    pages = []
    
    # 1. Process Root Directory
    for file in os.listdir(ROOT_DIR):
        if file.endswith(".html"):
            # Exclusion Logic: Skip templates and internal blueprints
            if "template" in file or file == "index.html":
                continue
            pages.append({"loc": f"{BASE_URL}/{file}", "priority": "0.9", "freq": "daily"})

    # 2. Add Index explicitly
    pages.append({"loc": f"{BASE_URL}/", "priority": "1.0", "freq": "daily"})

    # 3. Process Articles Directory
    if os.path.exists(ARTICLES_DIR):
        for file in os.listdir(ARTICLES_DIR):
            if file.endswith(".html"):
                pages.append({"loc": f"{BASE_URL}/articles/{file}", "priority": "0.8", "freq": "weekly"})

    # XML Construction
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_content += f"""    <url>
        <loc>{page['loc']}</loc>
        <changefreq>{page['freq']}</changefreq>
        <priority>{page['priority']}</priority>
    </url>\n"""

    sitemap_content += "</urlset>"

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print(f"GSN TERMINAL: Sitemap recalibrated. {len(pages)} nodes indexed. Templates purged.")

if __name__ == "__main__":
    generate_sitemap()