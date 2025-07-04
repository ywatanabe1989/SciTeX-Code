#!/usr/bin/env python3
"""
Fix incomplete code blocks in notebooks (else, except, etc.).
"""

import json
import re
from pathlib import Path

def fix_incomplete_blocks(source_lines):
    """Fix incomplete blocks by adding pass statements."""
    fixed_lines = []
    i = 0
    
    while i < len(source_lines):
        line = source_lines[i]
        
        # Check if this is a block-starting line (else:, except:, finally:, elif:)
        block_match = re.match(r'^(\s*)(else|except\s+.*|finally|elif\s+.*):\s*$', line)
        
        if block_match:
            indent = block_match.group(1)
            fixed_lines.append(line)
            
            # Check if the next line exists and has proper indentation
            has_body = False
            if i + 1 < len(source_lines):
                next_line = source_lines[i + 1]
                # Check if next line is properly indented
                if next_line.strip() and re.match(rf'^{indent}\s+\S', next_line):
                    has_body = True
            
            # If no body, add pass
            if not has_body:
                fixed_lines.append(f"{indent}    pass  # Fixed incomplete block\n")
                
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return fixed_lines

def fix_notebook_blocks(notebook_path):
    """Fix incomplete blocks in a notebook."""
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
                # Ensure newlines are preserved
                source_lines = [line + '\n' if i < len(source_lines)-1 or line else line 
                               for i, line in enumerate(source_lines)]
            else:
                source_lines = source
            
            # Fix incomplete blocks
            fixed_lines = fix_incomplete_blocks(source_lines)
            
            if fixed_lines != source_lines:
                cell['source'] = fixed_lines
                modified = True
                
                # Count what was fixed
                for line in fixed_lines:
                    if "# Fixed incomplete block" in line:
                        fixes_made.append(f"  - Fixed incomplete block in cell {cell_idx + 1}")
                        break
    
    if modified:
        # Save the fixed notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print(f"✓ Fixed {notebook_path.name}:")
        for fix in fixes_made:
            print(fix)
    else:
        print(f"✓ No incomplete blocks found")
    
    return modified

def main():
    """Fix incomplete blocks in all example notebooks."""
    examples_dir = Path('./examples')
    
    # Get all numbered notebooks
    notebooks = sorted([
        f for f in examples_dir.glob('*.ipynb')
        if f.name[0:2].isdigit() and f.name[2] == '_'
    ])
    
    print(f"Checking {len(notebooks)} notebooks for incomplete blocks...\n")
    
    fixed_count = 0
    
    for notebook_path in notebooks:
        if fix_notebook_blocks(notebook_path):
            fixed_count += 1
        print()
    
    print(f"Summary: Fixed incomplete blocks in {fixed_count} notebooks")

if __name__ == '__main__':
    main()