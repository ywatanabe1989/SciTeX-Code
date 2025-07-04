#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 18:41:00 (ywatanabe)"
# File: ./scripts/fix_specific_notebooks.py

"""
Fix specific issues in problematic notebooks.
"""

import nbformat
from pathlib import Path


def fix_str_notebook():
    """Fix the specific f-string issue in 04_scitex_str.ipynb."""
    nb_path = Path("examples/04_scitex_str.ipynb")
    
    with open(nb_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Find and fix the problematic cell
    for cell in nb.cells:
        if cell.cell_type == 'code' and "Step {i}:" in cell.source:
            # Fix the nested f-string issue
            cell.source = cell.source.replace(
                "print(f\"\\n{scitex.str.ct(f'Step {i}: {entry['step']}', 'green')}\")",
                "print(f\"\\n{scitex.str.ct(f'Step {i}: ' + entry['step'], 'green')}\")"
            )
    
    # Save the fixed notebook
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"✓ Fixed f-string issue in {nb_path}")


def fix_io_notebook():
    """Fix the compression ratio issue in 01_scitex_io.ipynb."""
    nb_path = Path("examples/01_scitex_io.ipynb")
    
    with open(nb_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Find and fix the division by zero issue
    for cell in nb.cells:
        if cell.cell_type == 'code' and "compression_ratio = file_sizes" in cell.source:
            # Add zero check
            cell.source = cell.source.replace(
                "compression_ratio = file_sizes['uncompressed'] / size",
                "compression_ratio = file_sizes['uncompressed'] / size if size > 0 else 1.0"
            )
            # Also fix the file size access
            if "file_sizes['uncompressed'] = uncompressed_file.stat().st_size" in cell.source:
                # Already fixed by previous script, but ensure it's correct
                pass
    
    # Save the fixed notebook
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"✓ Fixed compression issue in {nb_path}")


def fix_utils_notebook():
    """Fix the get_git_branch issue in 03_scitex_utils.ipynb."""
    nb_path = Path("examples/03_scitex_utils.ipynb")
    
    with open(nb_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Fix all get_git_branch calls
    for cell in nb.cells:
        if cell.cell_type == 'code' and "get_git_branch()" in cell.source:
            cell.source = cell.source.replace(
                "scitex.utils.get_git_branch()",
                "scitex.utils.get_git_branch('.')"
            )
    
    # Save the fixed notebook
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"✓ Fixed get_git_branch calls in {nb_path}")


def fix_path_notebook():
    """Fix potential issues in 05_scitex_path.ipynb."""
    nb_path = Path("examples/05_scitex_path.ipynb")
    
    with open(nb_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Fix any f-string issues with nested brackets
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # Fix nested dictionary access in f-strings
            if '["' in cell.source and '"]' in cell.source and 'f"' in cell.source:
                # Replace ["key"] with ['key'] in f-strings
                import re
                cell.source = re.sub(
                    r'f"([^"]*)\[\"([^"]+)\"\]([^"]*)"',
                    r'f"\1[\'\2\']\3"',
                    cell.source
                )
    
    # Save the fixed notebook
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"✓ Fixed potential f-string issues in {nb_path}")


def main():
    """Fix specific notebook issues."""
    print("Fixing Specific Notebook Issues")
    print("=" * 60)
    
    fix_str_notebook()
    fix_io_notebook()
    fix_utils_notebook()
    fix_path_notebook()
    
    print("\nDone! Run test_notebooks_status.py to verify fixes.")


if __name__ == "__main__":
    main()

# EOF