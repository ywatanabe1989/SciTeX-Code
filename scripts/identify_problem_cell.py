#!/usr/bin/env python3
"""
Identify the problematic cell #18 that's causing kernel death.
"""

import json
from pathlib import Path

def identify_cell_18():
    notebook_path = Path("examples/02_scitex_gen.ipynb")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    
    # Count only code cells (papermill only counts code cells)
    code_cell_count = 0
    
    for i, cell in enumerate(cells):
        if cell.get('cell_type') == 'code':
            code_cell_count += 1
            if code_cell_count == 18:
                print(f"Cell #18 (index {i}) content:")
                print("=" * 60)
                source = ''.join(cell.get('source', []))
                print(source)
                print("=" * 60)
                
                # Check for potentially problematic operations
                if 'plt.show()' in source:
                    print("⚠️  Contains matplotlib plotting")
                if 'for' in source and 'range' in source:
                    print("⚠️  Contains loops")
                if 'np.random' in source:
                    print("⚠️  Contains random array generation")
                if 'shell' in source or 'subprocess' in source:
                    print("⚠️  Contains shell execution")
                if 'var_info' in source:
                    print("⚠️  Contains var_info calls")
                if 'print_config' in source:
                    print("⚠️  Contains config printing")
                
                # Also check surrounding cells
                print(f"\nCell #17 preview:")
                if code_cell_count > 1:
                    for j in range(i-1, -1, -1):
                        if cells[j].get('cell_type') == 'code':
                            preview = ''.join(cells[j].get('source', []))[:100]
                            print(preview + "...")
                            break
                
                print(f"\nCell #19 preview:")
                next_code_found = False
                for j in range(i+1, len(cells)):
                    if cells[j].get('cell_type') == 'code':
                        preview = ''.join(cells[j].get('source', []))[:100]
                        print(preview + "...")
                        break
                
                break
    
    print(f"\nTotal code cells: {code_cell_count}")

if __name__ == "__main__":
    identify_cell_18()