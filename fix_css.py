import glob
import re

def nuke_css_blocks():
    # Find all HTML files in the current folder AND all subfolders
    html_files = glob.glob('**/*.html', recursive=True)
    
    # Regex specifically targets <style> to </style> across multiple lines
    pattern = re.compile(r'<style.*?>.*?</style>', re.DOTALL)
    
    modified_count = 0
    
    for filepath in html_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Only rewrite the file if it actually contains a <style> block
            if '<style' in content:
                # Replace the entire style block with nothing
                new_content = pattern.sub('', content)
                
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                    
                print(f"Nuked style block in: {filepath}")
                modified_count += 1
        except Exception as e:
            print(f"Skipped {filepath} due to error: {e}")
            
    print(f"\nDone. Successfully blew away CSS in {modified_count} files across all folders.")

if __name__ == "__main__":
    nuke_css_blocks()