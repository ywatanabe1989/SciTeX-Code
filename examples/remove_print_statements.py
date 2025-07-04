#!/usr/bin/env python3
"""Remove unnecessary print statements from notebooks according to CLAUDE.md guidelines."""

import json
import re
from pathlib import Path

def should_keep_print(line):
    """Determine if a print statement should be kept."""
    # Keep prints that are part of function definitions or examples
    if 'def ' in line and 'print(' in line:
        return True
    # Keep prints in docstrings or comments
    if '"""' in line or "'''" in line or line.strip().startswith('#'):
        return True
    # Keep prints that show example usage
    if 'example' in line.lower() or 'demo' in line.lower():
        return True
    return False

def remove_print_statements(notebook_path):
    """Remove print statements from a notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    changes_made = False
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code' and 'source' in cell:
            source = cell['source']
            if isinstance(source, list):
                source_text = ''.join(source)
            else:
                source_text = source
            
            original_source = source_text
            lines = source_text.split('\n')
            new_lines = []
            
            for line in lines:
                # Skip print statements unless they should be kept
                if 'print(' in line and not should_keep_print(line):
                    # Check if it's a standalone print statement
                    if re.match(r'^\s*print\(', line):
                        continue  # Skip this line
                new_lines.append(line)
            
            new_source = '\n'.join(new_lines)
            
            if new_source != original_source:
                changes_made = True
                if isinstance(cell['source'], list):
                    cell['source'] = new_source.split('\n')
                    # Ensure newlines
                    for i in range(len(cell['source']) - 1):
                        if not cell['source'][i].endswith('\n'):
                            cell['source'][i] += '\n'
                else:
                    cell['source'] = new_source
    
    return notebook, changes_made

def main():
    """Process all notebooks."""
    notebooks = list(Path('.').glob('*.ipynb'))
    
    print(f"Processing {len(notebooks)} notebooks...")
    
    modified_count = 0
    
    for notebook_path in notebooks:
        try:
            notebook, changed = remove_print_statements(notebook_path)
            
            if changed:
                with open(notebook_path, 'w') as f:
                    json.dump(notebook, f, indent=1)
                modified_count += 1
                print(f"  ✓ {notebook_path.name} - removed print statements")
            else:
                print(f"  - {notebook_path.name} - no changes needed")
                
        except Exception as e:
            print(f"  ✗ {notebook_path.name} - error: {e}")
    
    print(f"\nModified {modified_count} notebooks")

if __name__ == '__main__':
    main()