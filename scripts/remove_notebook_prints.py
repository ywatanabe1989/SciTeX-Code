#!/usr/bin/env python3
"""
Remove print statements from Jupyter notebooks.
As per CLAUDE.md: "No print needed. As scitex is designed to print necessary outputs automatically"
"""

import json
import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def remove_prints_from_cell(cell_source):
    """Remove print statements from a cell's source code."""
    if isinstance(cell_source, list):
        lines = cell_source
    else:
        lines = cell_source.split('\n')
    
    modified_lines = []
    for line in lines:
        # Skip lines that are print statements
        if re.match(r'^\s*print\s*\(', line):
            continue
        # Keep the line
        modified_lines.append(line)
    
    # Remove empty lines at the end
    while modified_lines and modified_lines[-1].strip() == '':
        modified_lines.pop()
    
    return modified_lines

def process_notebook(notebook_path):
    """Process a single notebook to remove print statements."""
    print(f"Processing: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    print_count = 0
    modified = False
    
    # Process each cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            original_source = cell.get('source', [])
            # Count prints
            source_text = ''.join(original_source) if isinstance(original_source, list) else original_source
            print_count += len(re.findall(r'print\s*\(', source_text))
            
            # Remove prints
            new_source = remove_prints_from_cell(original_source)
            
            if new_source != original_source:
                cell['source'] = new_source
                modified = True
    
    if modified:
        # Create backup
        backup_path = notebook_path.with_suffix('.ipynb.bak')
        shutil.copy2(notebook_path, backup_path)
        
        # Save modified notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print(f"  ✓ Removed {print_count} print statements")
        print(f"  ✓ Backup saved to {backup_path}")
    else:
        print(f"  ✓ No print statements found")
    
    return print_count, modified

def main():
    """Main function to process all notebooks."""
    examples_dir = Path('./examples')
    
    # Get all numbered notebooks (00_ through 23_)
    notebooks = sorted([
        f for f in examples_dir.glob('*.ipynb')
        if f.name[0:2].isdigit() and f.name[2] == '_'
    ])
    
    print(f"Found {len(notebooks)} notebooks to process\n")
    
    total_prints = 0
    modified_count = 0
    
    for notebook_path in notebooks:
        prints, modified = process_notebook(notebook_path)
        total_prints += prints
        if modified:
            modified_count += 1
        print()
    
    print(f"\nSummary:")
    print(f"- Total notebooks processed: {len(notebooks)}")
    print(f"- Notebooks modified: {modified_count}")
    print(f"- Total print statements removed: {total_prints}")
    print(f"\nBackup files created with .bak extension")

if __name__ == '__main__':
    main()