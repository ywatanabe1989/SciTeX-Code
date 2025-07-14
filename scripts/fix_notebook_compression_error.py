#!/usr/bin/env python3
"""Fix division by zero error in utils notebooks compression tests."""

import json
import re
from pathlib import Path

def fix_compression_cell(cell_source):
    """Fix the division by zero error in compression ratio calculation."""
    if isinstance(cell_source, list):
        source = ''.join(cell_source)
    else:
        source = cell_source
    
    # Look for the problematic compression ratio calculation
    if 'compression_ratio = uncompressed_size / compressed_size' in source:
        # Add zero check
        fixed = source.replace(
            'compression_ratio = uncompressed_size / compressed_size',
            'compression_ratio = uncompressed_size / compressed_size if compressed_size > 0 else 1.0'
        )
        
        # Also fix the similar issue in the loop
        fixed = fixed.replace(
            "compression_ratio = file_sizes['uncompressed'] / size",
            "compression_ratio = file_sizes['uncompressed'] / size if size > 0 else 1.0"
        )
        
        return fixed, True
    
    # Also check for the loop version
    if "file_sizes['uncompressed'] / size" in source:
        fixed = source.replace(
            "compression_ratio = file_sizes['uncompressed'] / size",
            "compression_ratio = file_sizes['uncompressed'] / size if size > 0 else 1.0"
        )
        return fixed, True
    
    return source, False

def fix_notebook(notebook_path):
    """Fix division by zero errors in a notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    modified = False
    cells_fixed = 0
    
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'code':
            source = cell['source']
            
            # Fix compression ratio calculation
            fixed_source, was_fixed = fix_compression_cell(source)
            
            if was_fixed:
                modified = True
                cells_fixed += 1
                
                # Update cell source
                if isinstance(source, list):
                    cell['source'] = fixed_source.splitlines(True)
                else:
                    cell['source'] = fixed_source
                    
    return notebook, modified, cells_fixed

def main():
    """Fix division by zero errors in utils notebooks."""
    notebooks_to_fix = [
        "./examples/03_scitex_utils.ipynb",
        "./examples/03_scitex_utils_test_fix.ipynb",
        "./examples/03_scitex_utils_test_output.ipynb"
    ]
    
    print("Fixing division by zero errors in compression tests...")
    print("=" * 60)
    
    for notebook_path in notebooks_to_fix:
        path = Path(notebook_path)
        
        if not path.exists():
            print(f"✗ {path.name} not found")
            continue
            
        try:
            # Create backup
            backup_path = path.with_suffix('.ipynb.bak')
            if not backup_path.exists():
                import shutil
                shutil.copy2(path, backup_path)
            
            # Fix notebook
            notebook, modified, cells_fixed = fix_notebook(path)
            
            if modified:
                # Save fixed notebook
                with open(path, 'w') as f:
                    json.dump(notebook, f, indent=1)
                
                print(f"✓ {path.name} - Fixed {cells_fixed} cells")
            else:
                print(f"○ {path.name} - No changes needed")
                
        except Exception as e:
            print(f"✗ {path.name} - Error: {e}")
    
    print("\nDone! Backups saved with .bak extension")

if __name__ == "__main__":
    main()