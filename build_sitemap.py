import os

BASE_URL = "https://taiwanstraittracker.com"

# Specific settings for your core navigational pages
CORE_PAGES = {
    "index.html": {"loc": "/", "priority": "1.0", "changefreq": "daily"},
    "macro.html": {"loc": "/macro.html", "priority": "0.9", "changefreq": "daily"},
    "ai-bubble.html": {"loc": "/ai-bubble.html", "priority": "0.9", "changefreq": "daily"},
    "middle-east.html": {"loc": "/middle-east.html", "priority": "0.9", "changefreq": "daily"},
    "fuel-reserves.html": {"loc": "/fuel-reserves.html", "priority": "0.9", "changefreq": "daily"},
    "supply-chain.html": {"loc": "/supply-chain.html", "priority": "0.9", "changefreq": "daily"},
    "inequality.html": {"loc": "/inequality.html", "priority": "0.9", "changefreq": "daily"},
    "fiat.html": {"loc": "/fiat.html", "priority": "0.9", "changefreq": "daily"},
    "about.html": {"loc": "/about.html", "priority": "0.8", "changefreq": "monthly"},
    "articles.html": {"loc": "/articles.html", "priority": "0.8", "changefreq": "weekly"}
}

def generate_sitemap():
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'

    # 1. Dynamically scan the main folder for ALL articles and pages
    root_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for file in root_files:
        if file in CORE_PAGES:
            # Apply specific priority for core pages
            page = CORE_PAGES[file]
            xml_content += "    <url>\n"
            xml_content += f"        <loc>{BASE_URL}{page['loc']}</loc>\n"
            xml_content += f"        <changefreq>{page['changefreq']}</changefreq>\n"
            xml_content += f"        <priority>{page['priority']}</priority>\n"
            xml_content += "    </url>\n"
        else:
            # Treat any other HTML file (like your articles) as high priority
            xml_content += "    <url>\n"
            xml_content += f"        <loc>{BASE_URL}/{file}</loc>\n"
            xml_content += "        <changefreq>monthly</changefreq>\n"
            xml_content += "        <priority>0.9</priority>\n"
            xml_content += "    </url>\n"

    # 2. Dynamically scan the daily reports folder
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
        report_files.sort(reverse=True)

        for report in report_files:
            date_str = report[:10]
            xml_content += "    <url>\n"
            xml_content += f"        <loc>{BASE_URL}/reports/{report}</loc>\n"
            xml_content += f"        <lastmod>{date_str}</lastmod>\n"
            xml_content += "        <changefreq>never</changefreq>\n"
            xml_content += "    </url>\n"

    xml_content += "</urlset>"

    with open("sitemap.xml", "w") as f:
        f.write(xml_content)
        
    print("✅ sitemap.xml generated successfully with all root articles included!")

if __name__ == "__main__":
    generate_sitemap()