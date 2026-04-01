import os
import shutil
import json
import time
from google import genai

# Initialise the GSN Architect
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.0-flash"
CACHE_FILE = "gsn_migration_state.log"

def load_completed_files():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

def mark_completed(filepath):
    with open(CACHE_FILE, 'a') as f:
        f.write(f"{filepath}\n")

def execute_migration():
    print("GSN TERMINAL: Initialising architectural refactor...")
    
    # 1. Define Target Directories
    dirs_to_create = ['src', 'data', 'public', 'templates']
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        
    # 2. Deterministic File Mapping
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    mapping = {}
    
    ignore_list = ['index.html', 'requirements.txt', 'README.md', 'CNAME', 'sitemap.xml', 'gsn_migration.py', 'folder_structure.txt']
    
    for f in files:
        if f in ignore_list:
            continue
        elif f.endswith('.py'):
            mapping[f] = f"src/{f}"
        elif f.endswith('.json'):
            mapping[f] = f"data/{f}"
        elif f.endswith(('.css', '.png', '.jpg', '.jpeg')):
            mapping[f] = f"public/{f}"
        elif f.endswith('.html'):
            mapping[f] = f"templates/{f}"
            
    # 3. Execute Physical Repositioning
    for old_path, new_path in mapping.items():
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"RELOCATED: {old_path} -> {new_path}")

    # 4. Agentic Content Refactoring
    print("GSN TERMINAL: Commencing deep code refactor with State Caching. Please hold...")
    
    completed_files = load_completed_files()
    target_folders = ['.', 'src', 'templates', 'articles', '.github/workflows']
    
    for folder in target_folders:
        if not os.path.exists(folder):
            continue
            
        for root, dirs, filenames in os.walk(folder):
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
                
            for filename in filenames:
                file_path = os.path.normpath(os.path.join(root, filename))
                
                if file_path in completed_files:
                    print(f"SKIPPED (Already Refactored): {file_path}")
                    continue
                
                if filename.endswith(('.png', '.jpg', '.jpeg', '.json', '.css', '.xml', '.zip', '.log', '.txt')) or filename == 'gsn_migration.py':
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        original_code = file.read()
                except UnicodeDecodeError:
                    print(f"SKIPPED (Binary Quarantine): {file_path}")
                    continue
                
                prompt = f"""
                You are the Lead Systems Architect for Global Shift Network.
                The repository has been restructured. Python scripts are in /src. JSON data is in /data. CSS and Images are in /public. HTML templates are in /templates.
                
                Current File: {file_path}
                
                Task: Rewrite the following code to correct all file path references.
                - HTML/JS: Update fetch() calls to point to 'data/filename.json'.
                - HTML: Update link hrefs and img srcs to point to 'public/filename.ext' (or '../public/filename.ext' if the file is in a subdirectory).
                - Python: Scripts in /src are executed from the root directory by GitHub Actions. Ensure open() calls point to 'data/filename.json' or 'templates/filename.html'.
                - GitHub Actions YAML: Update run commands to 'python src/filename.py'.
                
                Return ONLY the raw, updated code. Do not include markdown formatting blocks like ```python.
                
                Code:
                {original_code}
                """
                
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                updated_code = response.text.strip()
                
                if updated_code.startswith("```"):
                    updated_code = "\n".join(updated_code.split('\n')[1:-1])
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_code)
                
                mark_completed(file_path)
                print(f"REFACTORED: {file_path}")
                
                # Heavy throttle to clear the Token bucket
                time.sleep(15)

    print("GSN TERMINAL: Migration complete. Awaiting manual verification.")

if __name__ == "__main__":
    execute_migration()