import glob

def fix_article_layouts():
    # Targets ONLY the files inside the articles subfolder
    article_files = glob.glob('articles/*.html')
    count = 0
    
    override_style = """
    <style>
        /* Override the global dashboard grid for readable text */
        .container { 
            display: block !important; 
            max-width: 800px; 
            margin: 0 auto; 
            padding-top: 40px; 
        }
        .container p, .container ul, .container li { 
            font-size: 1.15rem; 
            color: var(--text-sub); 
            line-height: 1.8; 
            margin-bottom: 24px; 
        }
        .container h1 { font-size: 2.5rem; margin-bottom: 20px; color: var(--text-main); letter-spacing: -0.5px; line-height: 1.2;}
        .container h2, .container h3 { color: var(--text-main); margin-top: 40px; margin-bottom: 15px; }
        .container img { max-width: 100%; height: auto; border-radius: 8px; margin: 20px 0; border: 1px solid var(--border); }
        .container a { color: var(--accent); text-decoration: none; }
        .container a:hover { text-decoration: underline; }
    </style>
</head>"""

    for filepath in article_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Only inject if we haven't already fixed this page
            if '/* Override the global dashboard grid' not in content and '</head>' in content:
                # Replace the closing head tag with our override styles
                new_content = content.replace('</head>', override_style)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                
        except Exception as e:
            print(f"Skipped {filepath}: {e}")

    print(f"\nDone! Fixed layout on {count} articles.")

if __name__ == "__main__":
    fix_article_layouts()