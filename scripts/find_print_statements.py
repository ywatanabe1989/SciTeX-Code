#!/usr/bin/env python3
"""Find print statements in Jupyter notebooks."""

import json
import re
import sys
from pathlib import Path

def find_print_in_notebook(notebook_path):
    """Find print statements in a notebook."""
    try:
        with open(notebook_path, 'r') as f:
            notebook = json.load(f)
    except Exception as e:
        return f"Error reading {notebook_path}: {e}", 0
    
    print_count = 0
    print_locations = []
    
    # Check all cells
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            if isinstance(source, list):
                source = ''.join(source)
            
            # Look for print statements (not in comments)
            lines = source.split('\n')
            for line_num, line in enumerate(lines):
                # Skip commented lines
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                
                # Look for print( pattern
                if re.search(r'\bprint\s*\(', line):
                    print_count += 1
                    print_locations.append(f"Cell {i+1}, Line {line_num+1}: {line.strip()}")
    
    return print_locations, print_count

def main():
    # Get all numbered notebooks
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    notebooks = sorted([f for f in examples_dir.glob("*.ipynb") 
                       if f.name[:2].isdigit() and '_' in f.name])
    
    total_prints = 0
    notebooks_with_prints = []
    
    print("Searching for print statements in example notebooks...\n")
    
    for notebook in notebooks:
        locations, count = find_print_in_notebook(notebook)
        
        if isinstance(locations, str):  # Error case
            print(f"{notebook.name}: {locations}")
            continue
            
        if count > 0:
            notebooks_with_prints.append((notebook.name, count))
            total_prints += count
            print(f"\n{notebook.name}: {count} print statement(s)")
            for loc in locations[:5]:  # Show first 5
                print(f"  - {loc}")
            if len(locations) > 5:
                print(f"  ... and {len(locations) - 5} more")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"Total notebooks examined: {len(notebooks)}")
    print(f"Notebooks with print statements: {len(notebooks_with_prints)}")
    print(f"Total print statements found: {total_prints}")
    
    if notebooks_with_prints:
        print(f"\nNotebooks with print statements:")
        for name, count in sorted(notebooks_with_prints, key=lambda x: x[1], reverse=True):
            print(f"  - {name}: {count} print(s)")

if __name__ == "__main__":
    main()