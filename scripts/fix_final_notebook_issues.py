#!/usr/bin/env python3
"""Fix final issues in notebooks - decorators and web."""

import json
from pathlib import Path


def fix_web_notebook():
    """Fix the web notebook import issue."""
    notebook_path = Path("/home/ywatanabe/proj/SciTeX-Code/examples/23_scitex_web.ipynb")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    # Fix the first code cell with concatenated imports
    if nb['cells'] and nb['cells'][1]['cell_type'] == 'code':
        # The imports are all concatenated together
        concatenated = nb['cells'][1]['source'][0]
        
        # Split and properly format the imports
        proper_imports = """import sys
sys.path.insert(0, '../src')
import scitex
import pandas as pd
import numpy as np
from pathlib import Path
import json
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# Create output directory for web examples
web_output = Path('./web_examples')
web_output.mkdir(exist_ok=True)

print("SciTeX Web Operations Tutorial - Ready to begin!")
print("Note: This tutorial requires internet connection for demonstration")"""
        
        nb['cells'][1]['source'] = proper_imports.split('\n')
    
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print("✓ Fixed 23_scitex_web.ipynb")


def fix_decorators_notebook():
    """Fix the decorators notebook comment issue."""
    notebook_path = Path("/home/ywatanabe/proj/SciTeX-Code/examples/21_scitex_decorators.ipynb")
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    # Find and fix the specific cell
    for cell in nb['cells']:
        if cell.get('cell_type') == 'code':
            for i, line in enumerate(cell.get('source', [])):
                # Fix the specific line that was uncommented
                if 'print(f"\\n2. Pandas Series input (name: {series_data.name})")' in line and not line.strip().startswith('#'):
                    # This line should be commented as originally intended
                    cell['source'][i] = '# print(f"\\n2. Pandas Series input (name: {series_data.name})")\n'
                    print("Fixed decorators notebook comment")
    
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print("✓ Fixed 21_scitex_decorators.ipynb")


def main():
    """Fix final notebook issues."""
    print("Fixing final notebook issues...")
    print("=" * 60)
    
    fix_web_notebook()
    fix_decorators_notebook()
    
    print("=" * 60)
    print("All notebooks fixed!")


if __name__ == "__main__":
    main()