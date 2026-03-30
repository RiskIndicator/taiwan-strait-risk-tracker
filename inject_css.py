import glob

def brute_force_css_fix():
    html_files = glob.glob('**/*.html', recursive=True)
    count = 0
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 1. Wipe the slate clean: Remove ALL existing references to the CSS file
            # This destroys the parasitic tags attached to your Google Fonts
            content = content.replace(' href="/gsn-core.css"', '')
            content = content.replace('href="/gsn-core.css"', '')
            
            # 2. Inject ONE perfect, clean tag right before the closing head tag
            if '</head>' in content:
                content = content.replace('</head>', '    <link rel="stylesheet" href="/gsn-core.css">\n</head>')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
                print(f"✅ Purged & Fixed: {filepath}")
                
        except Exception as e:
            print(f"Error on {filepath}: {e}")

    print(f"\nDone. Brute-forced {count} files. Your network is now completely unified.")

if __name__ == "__main__":
    brute_force_css_fix()