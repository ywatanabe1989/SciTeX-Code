#!/usr/bin/env python3
"""
Fix syntax errors in notebooks, particularly incomplete except blocks.
"""

import json
import re
from pathlib import Path

def fix_incomplete_except_blocks(source_lines):
    """Fix incomplete except blocks by adding a pass statement."""
    fixed_lines = []
    i = 0
    
    while i < len(source_lines):
        line = source_lines[i]
        
        # Check if this is an except line
        if re.match(r'^\s*except\s+.*:\s*$', line):
            fixed_lines.append(line)
            
            # Check if the next line exists and has content
            if i + 1 < len(source_lines):
                next_line = source_lines[i + 1]
                # If next line is empty or has no indentation, add pass
                if not next_line.strip() or not re.match(r'^\s+', next_line):
                    # Add appropriate indentation
                    indent = re.match(r'^(\s*)', line).group(1)
                    fixed_lines.append(f"{indent}    pass  # Fixed incomplete except block\n")
            else:
                # At end of cell, add pass
                indent = re.match(r'^(\s*)', line).group(1)
                fixed_lines.append(f"{indent}    pass  # Fixed incomplete except block\n")
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return fixed_lines

def fix_notebook_syntax(notebook_path):
    """Fix syntax errors in a notebook."""
    print(f"Checking: {notebook_path.name}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    modified = False
    fixes_made = []
    
    for cell_idx, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            
            # Convert to list if string
            if isinstance(source, str):
                source_lines = source.split('\n')
            else:
                source_lines = source
            
            # Fix incomplete except blocks
            fixed_lines = fix_incomplete_except_blocks(source_lines)
            
            if fixed_lines != source_lines:
                cell['source'] = fixed_lines
                modified = True
                fixes_made.append(f"  - Fixed incomplete except block in cell {cell_idx + 1}")
    
    if modified:
        # Save the fixed notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print(f"✓ Fixed {notebook_path.name}:")
        for fix in fixes_made:
            print(fix)
    else:
        print(f"✓ No syntax errors found")
    
    return modified

def main():
    """Fix syntax errors in all example notebooks."""
    examples_dir = Path('./examples')
    
    # Get all numbered notebooks
    notebooks = sorted([
        f for f in examples_dir.glob('*.ipynb')
        if f.name[0:2].isdigit() and f.name[2] == '_'
    ])
    
    print(f"Checking {len(notebooks)} notebooks for syntax errors...\n")
    
    fixed_count = 0
    
    for notebook_path in notebooks:
        if fix_notebook_syntax(notebook_path):
            fixed_count += 1
        print()
    
    print(f"Summary: Fixed syntax errors in {fixed_count} notebooks")

if __name__ == '__main__':
    main()