#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:10:00 (ywatanabe)"
# File: ./scripts/fix_notebook_paths_directly.py

"""
Fix notebook paths by updating specific problematic patterns.
"""

import json
import nbformat
from pathlib import Path


def fix_io_notebook():
    """Fix the specific path issue in 01_scitex_io.ipynb."""
    nb_path = Path("examples/01_scitex_io.ipynb")
    
    with open(nb_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Find and fix the compression example cell
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'code' and 'file_sizes[' in cell.source:
            # This is the problematic cell
            lines = cell.source.split('\n')
            new_lines = []
            
            for line in lines:
                if "file_sizes['uncompressed'] = uncompressed_file.stat().st_size" in line:
                    # Add a check before accessing the file
                    new_lines.extend([
                        "# Wait for file to be written and get actual path",
                        "import time",
                        "time.sleep(0.1)  # Brief pause to ensure file is written",
                        "# The file is saved to notebook_out directory",
                        "actual_path = Path(f'{Path().name}_out') / uncompressed_file",
                        "if actual_path.exists():",
                        "    file_sizes['uncompressed'] = actual_path.stat().st_size",
                        "else:",
                        "    # Fallback: check if it's in current directory",
                        "    if uncompressed_file.exists():",
                        "        file_sizes['uncompressed'] = uncompressed_file.stat().st_size",
                        "    else:",
                        "        print(f'Warning: Could not find {uncompressed_file}')",
                        "        file_sizes['uncompressed'] = 0"
                    ])
                elif "compressed_file.stat().st_size" in line:
                    # Similar fix for compressed files
                    new_lines.extend([
                        "            actual_path = Path(f'{Path().name}_out') / compressed_file",
                        "            if actual_path.exists():",
                        "                file_sizes[compression] = actual_path.stat().st_size",
                        "            elif compressed_file.exists():",
                        "                file_sizes[compression] = compressed_file.stat().st_size",
                        "            else:",
                        "                file_sizes[compression] = 0"
                    ])
                else:
                    new_lines.append(line)
            
            cell.source = '\n'.join(new_lines)
            break
    
    # Save the fixed notebook
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"✓ Fixed path issues in {nb_path}")


def add_notebook_name_detection():
    """Add notebook name detection to all notebooks."""
    examples_dir = Path("examples")
    
    for nb_path in sorted(examples_dir.glob("*.ipynb")):
        if "test" in nb_path.name or "output" in nb_path.name:
            continue
            
        try:
            with open(nb_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)
            
            # Check if already has notebook name detection
            has_detection = any(
                "notebook_name =" in cell.source and "Path(__file__)" not in cell.source
                for cell in nb.cells
                if cell.cell_type == 'code'
            )
            
            if not has_detection and len(nb.cells) > 1:
                # Add notebook name detection after imports
                detection_code = f"""# Detect notebook name for output directory
import os
from pathlib import Path

# Get notebook name (for papermill compatibility)
notebook_name = "{nb_path.stem}"
if 'PAPERMILL_NOTEBOOK_NAME' in os.environ:
    notebook_name = Path(os.environ['PAPERMILL_NOTEBOOK_NAME']).stem
"""
                
                # Insert after first cell (usually imports)
                detection_cell = nbformat.v4.new_code_cell(detection_code)
                nb.cells.insert(1, detection_cell)
                
                with open(nb_path, 'w') as f:
                    nbformat.write(nb, f)
                    
                print(f"✓ Added notebook detection to {nb_path.name}")
                
        except Exception as e:
            print(f"✗ Error processing {nb_path.name}: {e}")


if __name__ == "__main__":
    print("Fixing notebook path issues...")
    fix_io_notebook()
    add_notebook_name_detection()
    print("\nDone!")

# EOF