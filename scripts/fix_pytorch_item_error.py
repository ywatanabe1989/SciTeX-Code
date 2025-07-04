#!/usr/bin/env python3
"""Fix PyTorch .item() AttributeError in stats notebooks."""

import json
import re
from pathlib import Path

def fix_pytorch_item_cell(cell_source):
    """Fix the .item() method call on float objects."""
    if isinstance(cell_source, list):
        source = ''.join(cell_source)
    else:
        source = cell_source
    
    fixed = source
    modified = False
    
    # Fix pattern: something.item() where something might be a float
    # Common patterns in stats calculations
    patterns_to_fix = [
        # Fix kurtosis.item() and similar
        (r'(\w+)\.item\(\)', r'\1.item() if hasattr(\1, "item") else \1'),
        # More specific fixes for known variables
        ('skewness.item()', 'skewness.item() if hasattr(skewness, "item") else skewness'),
        ('kurtosis.item()', 'kurtosis.item() if hasattr(kurtosis, "item") else kurtosis'),
        ('std.item()', 'std.item() if hasattr(std, "item") else std'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        if pattern in source:
            fixed = fixed.replace(pattern, replacement)
            modified = True
    
    # Alternative approach: wrap the entire moments calculation
    if 'moments.update({' in source and '.item()' in source:
        # Replace all .item() calls within the update block
        lines = fixed.split('\n')
        new_lines = []
        in_update_block = False
        
        for line in lines:
            if 'moments.update({' in line:
                in_update_block = True
            
            if in_update_block and '.item()' in line:
                # Replace .item() with a safe version
                line = re.sub(
                    r'(\w+)\.item\(\)',
                    r'(\1.item() if hasattr(\1, "item") else float(\1))',
                    line
                )
                modified = True
            
            if '})' in line and in_update_block:
                in_update_block = False
            
            new_lines.append(line)
        
        if modified:
            fixed = '\n'.join(new_lines)
    
    return fixed, modified

def fix_notebook(notebook_path):
    """Fix PyTorch .item() errors in a notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    modified = False
    cells_fixed = 0
    
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'code':
            source = cell['source']
            
            # Check if this cell has PyTorch moment calculations
            source_text = ''.join(source) if isinstance(source, list) else source
            
            if '.item()' in source_text and ('torch' in source_text or 'moment' in source_text):
                fixed_source, was_fixed = fix_pytorch_item_cell(source)
                
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
    """Fix PyTorch .item() errors in stats notebooks."""
    notebooks_to_fix = [
        "./examples/11_scitex_stats.ipynb",
        "./examples/11_scitex_stats_test_complete.ipynb", 
        "./examples/11_scitex_stats_test_fixed.ipynb",
        "./examples/11_scitex_stats_executed.ipynb",
        "./examples/11_scitex_stats_test_complete_executed.ipynb"
    ]
    
    print("Fixing PyTorch .item() AttributeError in stats notebooks...")
    print("=" * 60)
    
    fixed_count = 0
    
    for notebook_path in notebooks_to_fix:
        path = Path(notebook_path)
        
        if not path.exists():
            continue
            
        try:
            # Create backup
            backup_path = path.with_suffix('.ipynb.bak2')
            if not backup_path.exists():
                import shutil
                shutil.copy2(path, backup_path)
            
            # Fix notebook
            notebook, modified, cells_fixed = fix_notebook(path)
            
            if modified:
                # Save fixed notebook
                with open(path, 'w') as f:
                    json.dump(notebook, f, indent=1)
                
                fixed_count += 1
                print(f"✓ {path.name} - Fixed {cells_fixed} cells")
            else:
                print(f"○ {path.name} - No changes needed")
                
        except Exception as e:
            print(f"✗ {path.name} - Error: {e}")
    
    print(f"\nFixed {fixed_count} notebooks")
    print("Backups saved with .bak2 extension")

if __name__ == "__main__":
    main()