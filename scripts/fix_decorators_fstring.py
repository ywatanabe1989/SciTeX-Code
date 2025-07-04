#!/usr/bin/env python3
"""Fix specific f-string issue in decorators notebook."""

import json
from pathlib import Path


def fix_decorators_notebook():
    notebook_path = Path("/home/ywatanabe/proj/SciTeX-Code/examples/21_scitex_decorators.ipynb")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    fixed = False
    
    # Find and fix the problematic line
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            for i, line in enumerate(source):
                # Fix the specific problematic line
                if '# print(f"\\n2. Pandas Series input(name: {series_data.name})")' in line:
                    source[i] = 'print(f"\\n2. Pandas Series input (name: {series_data.name})")\n'
                    fixed = True
                    print(f"Fixed line: {source[i].strip()}")
    
    if fixed:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)
        print("✓ Fixed 21_scitex_decorators.ipynb")
    else:
        print("No changes needed")


if __name__ == "__main__":
    fix_decorators_notebook()