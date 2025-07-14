#!/usr/bin/env python3
"""
Fix the indentation error in 02_scitex_gen.ipynb caused by the kernel death fix.
"""

import json
from pathlib import Path

def fix_indentation_error():
    notebook_path = Path("examples/02_scitex_gen.ipynb")
    
    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Find and fix the problematic cell
    for cell in notebook.get('cells', []):
        if cell.get('id') == '1b564718':
            # Restore the original correct code
            correct_source = '''# Path compatibility helper
import os
from pathlib import Path

def ensure_output_dir(subdir: str, notebook_name: str = "02_scitex_gen"):
    """Ensure output directory exists with backward compatibility."""
    expected_dir = Path(subdir)
    actual_dir = Path(f"{notebook_name}_out") / subdir
    
    if not expected_dir.exists() and actual_dir.exists():
        # Create symlink for backward compatibility
        try:
            os.symlink(str(actual_dir.resolve()), str(expected_dir))
            print(f"Created symlink: {expected_dir} -> {actual_dir}")
        except (OSError, FileExistsError):
            pass
    
    return expected_dir
'''
            cell['source'] = correct_source.strip().split('\n')
            # Add newlines to all lines except the last
            for i in range(len(cell['source']) - 1):
                cell['source'][i] += '\n'
            
            print("Fixed indentation error in cell 1b564718")
            break
    
    # Write fixed notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)
    
    print("✓ Fixed indentation error in 02_scitex_gen.ipynb")

if __name__ == "__main__":
    fix_indentation_error()