import os
import glob
import re

# GSN & WMP: Unified Context Aggregator
# Target: Compiles core architecture into gsn_context.md for AI initialisation

def generate_context_file():
    print("GSN TERMINAL: Initialising unified context aggregator...")
    
    output_file = "gsn_context.md"
    
    # 1. Dynamic Targets: Sweep core logic and templates
    dynamic_targets = [
        {"path": "src/*.py", "type": "python"},
        {"path": "templates/*.html", "type": "html"},
        {"path": ".github/workflows/*.yml", "type": "yaml"}
    ]
    
    # 2. Explicit Root Files: Core pages for both GSN & WMP
    explicit_root_files = [
        # GSN Terminal Core
        "index.html",
        "taiwan.html",
        "ai-disruption.html",
        "middle-east.html",
        "supply-chain.html",
        "fuel-reserves.html",
        "inequality.html",
        "macro.html",
        # WMP Core
        "test.html",
        "guides.html",
        "chart.html"
    ]
    
    try:
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write("# GSN Terminal & WMP Unified Codebase Context\n")
            out_f.write("> This file contains the core operational logic, templates, and explicit root HTML files for the Global Shift Network and What's My Politics platforms.\n\n")
            
            # Process dynamic directories
            for target in dynamic_targets:
                files = glob.glob(target["path"])
                for file_path in sorted(files):
                    append_file_content(out_f, file_path, target["type"])
                    
            # Process explicit root files
            for file_path in explicit_root_files:
                if os.path.exists(file_path):
                    append_file_content(out_f, file_path, "html")
                else:
                    print(f"⚠️ Warning: {file_path} not found in root.")
                    
        print(f"✅ Context successfully compiled to {output_file}")
        
    except Exception as e:
        print(f"❌ Critical Error generating context: {e}")

def append_file_content(out_file, file_path, lang_type):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Detect and warn about Git merge conflicts without failing the build
        if re.search(r'<<<<<<< HEAD', content):
            print(f"   ⚠️ WARNING: Git merge conflict markers detected in {file_path}")
            
        out_file.write(f"## {file_path}\n")
        out_file.write(f"```{lang_type}\n")
        out_file.write(content)
        if not content.endswith('\n'):
            out_file.write("\n")
        out_file.write("```\n\n")
        
        print(f"   + Ingested: {file_path}")
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

if __name__ == "__main__":
    generate_context_file()