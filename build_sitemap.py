import os

BASE_URL = "https://taiwanstraittracker.com"

# High-priority evergreen pages
EVERGREEN_PAGES = [
    {"loc": "/", "priority": "1.0", "changefreq": "daily"},
    {"loc": "/about.html", "priority": "0.8", "changefreq": "monthly"},
    {"loc": "/articles.html", "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/dual-chokepoint.html", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/quantitative-signal.html", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/macro-big-cycle.html", "priority": "0.9", "changefreq": "monthly"},
]

def generate_sitemap():
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n'

    # 1. Add evergreen pages
    for page in EVERGREEN_PAGES:
        xml_content += "    <url>\n"
        xml_content += f"        <loc>{BASE_URL}{page['loc']}</loc>\n"
        xml_content += f"        <changefreq>{page['changefreq']}</changefreq>\n"
        xml_content += f"        <priority>{page['priority']}</priority>\n"
        xml_content += "    </url>\n"

    # 2. Dynamically find daily reports
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        # Get all html files and sort them (newest first)
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
        report_files.sort(reverse=True)

        for report in report_files:
            # Extract date from filename (e.g., 2026-02-04)
            date_str = report[:10]
            
            xml_content += "    <url>\n"
            xml_content += f"        <loc>{BASE_URL}/reports/{report}</loc>\n"
            xml_content += f"        <lastmod>{date_str}</lastmod>\n"
            xml_content += "        <changefreq>never</changefreq>\n"
            xml_content += "    </url>\n"

    xml_content += "</urlset>"

    # 3. Save the file
    with open("sitemap.xml", "w") as f:
        f.write(xml_content)
        
    print("✅ sitemap.xml generated successfully!")

if __name__ == "__main__":
    generate_sitemap()