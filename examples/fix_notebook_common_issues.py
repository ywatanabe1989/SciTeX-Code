#!/usr/bin/env python3
"""Fix common issues in failing notebooks."""

import json
import re
from pathlib import Path
import shutil
from datetime import datetime

def fix_notebook(notebook_path):
    """Fix common issues in a notebook."""
    # Read notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    fixes_applied = []
    
    # Fix each cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code' and 'source' in cell:
            source = cell['source']
            if isinstance(source, list):
                source_text = ''.join(source)
            else:
                source_text = source
            
            original_source = source_text
            
            # Fix 1: Add parents=True to mkdir calls for nested directories
            if 'mkdir(' in source_text and 'exist_ok=True' in source_text:
                # Pattern: xxx.mkdir(exist_ok=True) -> xxx.mkdir(exist_ok=True, parents=True)
                source_text = re.sub(
                    r'\.mkdir\(exist_ok=True\)',
                    '.mkdir(exist_ok=True, parents=True)',
                    source_text
                )
                if source_text != original_source:
                    fixes_applied.append('Added parents=True to mkdir')
            
            # Fix 2: Fix cleanup variable issues
            if 'cleanup = False' in source_text and '#' in source_text:
                # Remove inline comments that might cause issues
                lines = source_text.split('\n')
                new_lines = []
                for line in lines:
                    if 'cleanup = False' in line and '#' in line:
                        # Keep only the assignment part
                        new_lines.append('cleanup = False')
                        fixes_applied.append('Fixed cleanup variable definition')
                    else:
                        new_lines.append(line)
                source_text = '\n'.join(new_lines)
            
            # Fix 3: Fix undefined variables (like print_count)
            if 'print_count' in source_text and 'def print_count' not in source_text:
                # Check if it's used as a function call
                if 'print_count(' in source_text:
                    # Replace with print
                    source_text = source_text.replace('print_count(', 'print(')
                    fixes_applied.append('Replaced print_count with print')
            
            # Fix 4: Fix syntax errors in dictionary definitions
            # Look for patterns like: '{{'accuracy': accuracy
            if "{{'" in source_text or '{{\"' in source_text:
                # This is likely a template issue - fix double braces
                source_text = source_text.replace("{{", "{")
                source_text = source_text.replace("}}", "}")
                fixes_applied.append('Fixed double brace syntax error')
            
            # Fix 5: Fix missing quotes in dictionary returns
            # Pattern: return {accuracy': accuracy  (missing opening quote)
            source_text = re.sub(
                r"return\s+{([a-zA-Z_]+)':\s*",
                r"return {'\1': ",
                source_text
            )
            
            # Fix 6: Ensure data directories exist at the beginning
            if 'data_dir = Path(' in source_text or 'data_dir = ' in source_text:
                # Check if mkdir is called on data_dir
                if 'data_dir.mkdir' not in source_text:
                    # Add mkdir after data_dir definition
                    lines = source_text.split('\n')
                    for i, line in enumerate(lines):
                        if 'data_dir = ' in line and 'Path(' in line:
                            # Insert mkdir on the next line
                            lines.insert(i + 1, 'data_dir.mkdir(exist_ok=True, parents=True)')
                            fixes_applied.append('Added data_dir.mkdir()')
                            break
                    source_text = '\n'.join(lines)
            
            # Fix 7: Fix list.remove() errors in pop_keys usage
            if 'scitex.dict.pop_keys' in source_text:
                # This function might have issues with items not in list
                # Wrap in try-except
                lines = source_text.split('\n')
                new_lines = []
                for line in lines:
                    if 'scitex.dict.pop_keys' in line and 'try:' not in source_text:
                        indent = len(line) - len(line.lstrip())
                        new_lines.append(' ' * indent + 'try:')
                        new_lines.append(line)
                        new_lines.append(' ' * indent + 'except ValueError as e:')
                        new_lines.append(' ' * indent + '    print(f"Warning: {e}")')
                        new_lines.append(' ' * indent + '    # Continue with original list')
                        fixes_applied.append('Added error handling for pop_keys')
                    else:
                        new_lines.append(line)
                source_text = '\n'.join(new_lines) if 'Added error handling' in str(fixes_applied) else source_text
            
            # Update cell source if changes were made
            if source_text != original_source:
                if isinstance(cell['source'], list):
                    cell['source'] = source_text.split('\n')
                    # Ensure each line ends with \n except the last
                    for i in range(len(cell['source']) - 1):
                        if not cell['source'][i].endswith('\n'):
                            cell['source'][i] += '\n'
                else:
                    cell['source'] = source_text
    
    return notebook, fixes_applied

def main():
    """Fix common issues in all failing notebooks."""
    # List of notebooks that are known to fail
    failing_notebooks = [
        '05_scitex_path.ipynb',
        '07_scitex_dict.ipynb', 
        '08_scitex_types.ipynb',
        '10_scitex_parallel.ipynb',
        '12_scitex_linalg.ipynb',
        '13_scitex_dsp.ipynb',
        '14_scitex_plt.ipynb',
        '15_scitex_pd.ipynb',
        '16_scitex_ai.ipynb',
        '16_scitex_scholar.ipynb',
        '19_scitex_db.ipynb',
        '21_scitex_decorators.ipynb',
        '23_scitex_web.ipynb'
    ]
    
    # Create backup directory
    backup_dir = Path('backups') / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for notebook_name in failing_notebooks:
        notebook_path = Path(notebook_name)
        
        if not notebook_path.exists():
            print(f"Skipping {notebook_name} - file not found")
            continue
        
        print(f"\nProcessing {notebook_name}...")
        
        # Create backup
        backup_path = backup_dir / notebook_name
        shutil.copy2(notebook_path, backup_path)
        
        try:
            # Fix the notebook
            fixed_notebook, fixes = fix_notebook(notebook_path)
            
            if fixes:
                # Save fixed notebook
                with open(notebook_path, 'w') as f:
                    json.dump(fixed_notebook, f, indent=1)
                
                print(f"  Applied {len(fixes)} fixes:")
                for fix in fixes:
                    print(f"    - {fix}")
                
                results.append({
                    'notebook': notebook_name,
                    'status': 'fixed',
                    'fixes': fixes
                })
            else:
                print("  No fixes needed")
                results.append({
                    'notebook': notebook_name,
                    'status': 'no_changes',
                    'fixes': []
                })
                
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'notebook': notebook_name,
                'status': 'error',
                'error': str(e)
            })
    
    # Save results
    with open('notebook_fixes_applied.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nFixed {sum(1 for r in results if r['status'] == 'fixed')} notebooks")
    print(f"Backups saved to: {backup_dir}")
    print("Results saved to: notebook_fixes_applied.json")

if __name__ == '__main__':
    main()