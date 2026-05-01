import os
from datetime import datetime

# GSN Terminal: Sitemap Generator Calibration
# Target: Technical SEO Optimisation & Full Directory Coverage

BASE_URL = "https://taiwanstraittracker.com"
ROOT_DIR = "."
ARTICLES_DIR = "articles"
PUBLIC_DIR = "public"

def generate_sitemap():
    print("GSN TERMINAL: Initialising sitemap recalibration...")
    
    pages = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Process Root Directory
    for file in os.listdir(ROOT_DIR):
        if file.endswith(".html"):
            # Exclusion Logic: Skip templates, index, WMP frontend, and raw partials
            if "template" in file or file == "index.html" or file == "test.html":
                continue
                
            # Calculate dynamic last modified time
            mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d")
            
            pages.append({
                "loc": f"{BASE_URL}/{file}", 
                "priority": "0.9", 
                "freq": "daily",
                "lastmod": mod_time
            })

    # 2. Add Index explicitly
    pages.append({
        "loc": f"{BASE_URL}/", 
        "priority": "1.0", 
        "freq": "daily",
        "lastmod": today
    })

    # 3. Process Articles Directory (The Evergreen Pillars)
    if os.path.exists(ARTICLES_DIR):
        for file in os.listdir(ARTICLES_DIR):
            if file.endswith(".html"):
                file_path = os.path.join(ARTICLES_DIR, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
                
                pages.append({
                    "loc": f"{BASE_URL}/{ARTICLES_DIR}/{file}", 
                    "priority": "0.8", 
                    "freq": "weekly",
                    "lastmod": mod_time
                })

    # 4. Process Public Directory (Static Info Pages)
    if os.path.exists(PUBLIC_DIR):
        for file in os.listdir(PUBLIC_DIR):
            if file.endswith(".html"):
                file_path = os.path.join(PUBLIC_DIR, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d")
                
                pages.append({
                    "loc": f"{BASE_URL}/{PUBLIC_DIR}/{file}", 
                    "priority": "0.5", 
                    "freq": "monthly",
                    "lastmod": mod_time
                })

    # ==========================================
    # XML CONSTRUCTION
    # ==========================================
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_content += "    <url>\n"
        sitemap_content += f"        <loc>{page['loc']}</loc>\n"
        sitemap_content += f"        <lastmod>{page['lastmod']}</lastmod>\n"
        sitemap_content += f"        <changefreq>{page['freq']}</changefreq>\n"
        sitemap_content += f"        <priority>{page['priority']}</priority>\n"
        sitemap_content += "    </url>\n"

    sitemap_content += "</urlset>"

    # Execute strict UTF-8 write protocol
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print(f"GSN TERMINAL: Sitemap recalibrated. {len(pages)} nodes indexed.")

if __name__ == "__main__":
    generate_sitemap()