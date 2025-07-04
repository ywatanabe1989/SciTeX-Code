#!/usr/bin/env python3
"""
Fix Jupyter notebook format issues.
Removes invalid properties like 'id' and 'outputs' from markdown cells.
"""

import json
import os
from pathlib import Path

def fix_notebook_format(notebook_path):
    """Fix format issues in a single notebook."""
    print(f"Fixing: {notebook_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    modified = False
    
    # Process each cell
    for cell in notebook.get('cells', []):
        # Remove 'id' from cells if present (not valid in notebook format v4.2)
        if 'id' in cell:
            del cell['id']
            modified = True
        
        # For markdown cells, remove 'outputs' if present
        if cell.get('cell_type') == 'markdown' and 'outputs' in cell:
            del cell['outputs']
            modified = True
        
        # Ensure code cells have outputs array
        if cell.get('cell_type') == 'code' and 'outputs' not in cell:
            cell['outputs'] = []
            modified = True
        
        # Ensure code cells have execution_count
        if cell.get('cell_type') == 'code' and 'execution_count' not in cell:
            cell['execution_count'] = None
            modified = True
    
    if modified:
        # Save fixed notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print(f"  ✓ Fixed format issues")
    else:
        print(f"  ✓ No format issues found")
    
    return modified

def main():
    """Fix all notebooks in examples directory."""
    examples_dir = Path('./examples')
    
    # Get all numbered notebooks
    notebooks = sorted([
        f for f in examples_dir.glob('*.ipynb')
        if f.name[0:2].isdigit() and f.name[2] == '_'
    ])
    
    print(f"Checking {len(notebooks)} notebooks for format issues\n")
    
    fixed_count = 0
    
    for notebook_path in notebooks:
        if fix_notebook_format(notebook_path):
            fixed_count += 1
    
    print(f"\nSummary:")
    print(f"- Total notebooks processed: {len(notebooks)}")
    print(f"- Notebooks fixed: {fixed_count}")

if __name__ == '__main__':
    main()