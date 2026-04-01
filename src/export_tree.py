import os

def export_folder_tree(start_path, output_filename):
    # Folders to ignore so your output stays clean
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'env'}
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"Folder Structure for: {os.path.abspath(start_path)}\n")
        f.write("=" * 50 + "\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Modify dirs in-place to skip the ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Calculate the current depth for indentation
            level = root.replace(start_path, '').count(os.sep)
            indent = '    ' * level
            
            # Write the current directory
            folder_name = os.path.basename(root)
            if level == 0:
                folder_name = "root"
                
            f.write(f"{indent}📁 {folder_name}/\n")
            
            # Write the files within the directory
            sub_indent = '    ' * (level + 1)
            for file in files:
                # Ignore the script itself and its output file
                if file not in ['export_tree.py', os.path.basename(output_filename)]:
                    f.write(f"{sub_indent}📄 {file}\n")

if __name__ == "__main__":
    # '.' means it will scan the directory the script is located in
    target_directory = '.' 
    output_file = 'data/folder_structure.txt'
    
    print(f"Scanning directory: {os.path.abspath(target_directory)}")
    export_folder_tree(target_directory, output_file)
    print(f"✅ Success! Folder structure exported to {output_file}")