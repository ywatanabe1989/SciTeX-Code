#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:08:00 (ywatanabe)"
# File: ./scripts/update_notebook_paths.py

"""
Update notebook code to use new path conventions.

This script updates notebooks to expect files in the current directory
while scitex saves to {notebook_name}_out/ directories.
"""

import json
import re
from pathlib import Path
import nbformat
from typing import List, Dict, Any


def update_cell_paths(cell_source: str, notebook_name: str) -> str:
    """Update paths in a cell to use new convention."""
    # Pattern to match file operations that expect files in subdirectories
    patterns = [
        # Match Path("subdir/file") patterns
        (r'Path\("([\w_]+)/([\w_.-]+)"\)', r'Path("\1/\2")'),
        # Match .stat() calls on saved files
        (r'(\w+_file)\.stat\(\)', r'scitex.io.get_path(\1).stat()'),
        # Match direct file access after save
        (r'([\w_]+)/([\w_.-]+)\.(\w+)', r'\1/\2.\3'),
    ]
    
    updated = cell_source
    
    # Special handling for io notebook compression example
    if "io_examples" in cell_source and notebook_name == "01_scitex_io":
        # Add a cell to check if file exists and create symlink if needed
        check_code = """# Ensure output directory exists
import os
output_dir = Path("io_examples")
actual_dir = Path("01_scitex_io_out/io_examples")

if actual_dir.exists() and not output_dir.exists():
    # Create symlink for backward compatibility
    os.symlink(str(actual_dir), str(output_dir))
    print(f"Created symlink: {output_dir} -> {actual_dir}")
"""
        if "data_dir = Path" in cell_source and check_code not in cell_source:
            # Insert after data_dir definition
            lines = cell_source.split('\n')
            for i, line in enumerate(lines):
                if "data_dir = Path" in line:
                    lines.insert(i + 1, check_code)
                    break
            updated = '\n'.join(lines)
    
    return updated


def update_notebook(notebook_path: Path) -> bool:
    """Update a single notebook with new path handling."""
    try:
        # Read notebook
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        notebook_name = notebook_path.stem
        modified = False
        
        # Update code cells
        for cell in nb.cells:
            if cell.cell_type == 'code':
                original = cell.source
                updated = update_cell_paths(original, notebook_name)
                
                if updated != original:
                    cell.source = updated
                    modified = True
        
        # Write back if modified
        if modified:
            with open(notebook_path, 'w') as f:
                nbformat.write(nb, f)
            print(f"✓ Updated: {notebook_path.name}")
            return True
        else:
            print(f"  No changes: {notebook_path.name}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {notebook_path.name}: {e}")
        return False


def add_path_helper_cells(notebook_path: Path) -> bool:
    """Add helper cells to handle path compatibility."""
    try:
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        notebook_name = notebook_path.stem
        
        # Create helper cell
        helper_code = f"""# Path compatibility helper
import os
from pathlib import Path

def ensure_output_dir(subdir: str, notebook_name: str = "{notebook_name}"):
    \"\"\"Ensure output directory exists with backward compatibility.\"\"\"
    expected_dir = Path(subdir)
    actual_dir = Path(f"{{notebook_name}}_out") / subdir
    
    if not expected_dir.exists() and actual_dir.exists():
        # Create symlink for backward compatibility
        try:
            os.symlink(str(actual_dir.resolve()), str(expected_dir))
            print(f"Created symlink: {{expected_dir}} -> {{actual_dir}}")
        except (OSError, FileExistsError):
            pass
    
    return expected_dir
"""
        
        # Check if helper already exists
        has_helper = any(
            "ensure_output_dir" in cell.source 
            for cell in nb.cells 
            if cell.cell_type == 'code'
        )
        
        if not has_helper:
            # Insert helper after imports (usually cell 1)
            helper_cell = nbformat.v4.new_code_cell(helper_code)
            nb.cells.insert(2, helper_cell)
            
            with open(notebook_path, 'w') as f:
                nbformat.write(nb, f)
            print(f"✓ Added helper to: {notebook_path.name}")
            return True
            
    except Exception as e:
        print(f"✗ Error adding helper to {notebook_path.name}: {e}")
    
    return False


def main():
    """Update notebooks with path handling fixes."""
    examples_dir = Path("examples")
    
    # Priority notebooks that need fixes
    priority_notebooks = [
        "01_scitex_io.ipynb",
        "02_scitex_gen.ipynb",
        "11_scitex_stats.ipynb",
        "14_scitex_plt.ipynb",
    ]
    
    print("Updating notebook paths for new convention...")
    print("=" * 60)
    
    # First add helpers to priority notebooks
    print("\nAdding path helpers to priority notebooks:")
    for nb_name in priority_notebooks:
        nb_path = examples_dir / nb_name
        if nb_path.exists():
            add_path_helper_cells(nb_path)
    
    print("\nUpdating path references:")
    # Update all notebooks
    updated_count = 0
    for notebook_path in sorted(examples_dir.glob("*.ipynb")):
        if "test" not in notebook_path.name and "output" not in notebook_path.name:
            if update_notebook(notebook_path):
                updated_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Updated {updated_count} notebooks")
    
    # Test one notebook
    print("\nTesting updated notebook...")
    test_nb = examples_dir / "01_scitex_io.ipynb"
    if test_nb.exists():
        import subprocess
        result = subprocess.run(
            ["../.env/bin/python", "-m", "papermill", 
             str(test_nb), "test_updated_io.ipynb", 
             "-k", "scitex", "--progress-bar"],
            cwd=str(examples_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Test notebook executed successfully!")
        else:
            print("✗ Test notebook still has issues")
            print(f"  Error: {result.stderr[-500:]}")  # Last 500 chars


if __name__ == "__main__":
    main()

# EOF