#!/usr/bin/env python3
"""Fix common API issues in notebooks based on the analysis."""

import json
import re
from pathlib import Path
import shutil
from datetime import datetime

def fix_notebook(notebook_path):
    """Fix API issues in a single notebook."""
    
    # Read notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    modified = False
    fixes_applied = []
    
    # Process each cell
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'code':
            source = cell['source']
            
            # Join source if it's a list
            if isinstance(source, list):
                original_source = ''.join(source)
            else:
                original_source = source
            
            new_source = original_source
            
            # Fix 1: ansi_escape usage
            if 'ansi_escape(' in new_source:
                # Replace function call with proper regex usage
                new_source = re.sub(
                    r'scitex\.utils\.ansi_escape\((.*?)\)',
                    r'scitex.utils.ansi_escape.sub("", \1)',
                    new_source
                )
                if new_source != original_source:
                    fixes_applied.append("Fixed ansi_escape usage")
            
            # Fix 2: notify() level parameter
            if 'notify(' in new_source and 'level=' in new_source:
                # Remove level parameter
                new_source = re.sub(
                    r',?\s*level\s*=\s*[\'"][^\'\"]+[\'"]',
                    '',
                    new_source
                )
                if new_source != original_source:
                    fixes_applied.append("Removed level parameter from notify()")
            
            # Fix 3: gen_footer() missing arguments
            if 'gen_footer()' in new_source:
                # Add required arguments
                new_source = re.sub(
                    r'scitex\.utils\.gen_footer\(\)',
                    r'scitex.utils.gen_footer("user@host", "notebook.ipynb", scitex, "main")',
                    new_source
                )
                if new_source != original_source:
                    fixes_applied.append("Added required arguments to gen_footer()")
            
            # Fix 4: search() pattern vs patterns
            if 'search(' in new_source and 'pattern=' in new_source:
                # Change pattern to patterns
                new_source = re.sub(
                    r'pattern=',
                    r'patterns=',
                    new_source
                )
                if new_source != original_source:
                    fixes_applied.append("Changed 'pattern' to 'patterns' in search()")
            
            # Fix 5: get_git_branch() path vs module
            if 'get_git_branch(' in new_source:
                # Replace path with module
                new_source = re.sub(
                    r'get_git_branch\([\'"][^\'"]+[\'"]\)',
                    r'get_git_branch(scitex)',
                    new_source
                )
                if new_source != original_source:
                    fixes_applied.append("Fixed get_git_branch() to use module instead of path")
            
            # Fix 6: undefined cleanup variable
            if 'if cleanup:' in new_source:
                # Check if cleanup is defined (even in comments)
                if 'cleanup =' not in new_source.replace('# cleanup =', ''):
                    # Define cleanup variable at the beginning of the cell
                    new_source = 'cleanup = False  # Set to True to remove example files\n' + new_source
                    if new_source != original_source:
                        fixes_applied.append("Added cleanup variable definition")
            
            # Update cell source if changed
            if new_source != original_source:
                modified = True
                # Split back into lines if original was a list
                if isinstance(source, list):
                    cell['source'] = new_source.splitlines(True)
                else:
                    cell['source'] = new_source
    
    return notebook, modified, fixes_applied


def main():
    """Fix API issues in all notebooks."""
    examples_dir = Path("./examples")
    
    # Notebooks to fix (excluding already working ones and test files)
    notebooks_to_fix = [
        "03_scitex_utils.ipynb",
        "04_scitex_str.ipynb", 
        "05_scitex_path.ipynb",
        "06_scitex_context.ipynb",
        "07_scitex_dict.ipynb",
        "08_scitex_types.ipynb",
        "10_scitex_parallel.ipynb",
        "11_scitex_stats.ipynb",
        "12_scitex_linalg.ipynb",
        "13_scitex_dsp.ipynb",
        "14_scitex_plt.ipynb",
        "15_scitex_pd.ipynb",
        "16_scitex_ai.ipynb",
        "16_scitex_scholar.ipynb",
        "19_scitex_db.ipynb",
        "21_scitex_decorators.ipynb",
        "23_scitex_web.ipynb"
    ]
    
    print("Fixing notebook API issues...")
    print("=" * 80)
    
    fixed_count = 0
    
    for notebook_name in notebooks_to_fix:
        notebook_path = examples_dir / notebook_name
        
        if not notebook_path.exists():
            print(f"✗ {notebook_name} not found")
            continue
        
        # Backup original
        backup_path = notebook_path.with_suffix('.ipynb.bak')
        if not backup_path.exists():
            shutil.copy2(notebook_path, backup_path)
        
        # Fix notebook
        try:
            notebook, modified, fixes = fix_notebook(notebook_path)
            
            if modified:
                # Save fixed notebook
                with open(notebook_path, 'w') as f:
                    json.dump(notebook, f, indent=1)
                
                fixed_count += 1
                print(f"✓ {notebook_name}")
                for fix in fixes:
                    print(f"  - {fix}")
            else:
                print(f"○ {notebook_name} (no changes needed)")
                
        except Exception as e:
            print(f"✗ {notebook_name}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Fixed {fixed_count} notebooks")
    print(f"Backups saved with .bak extension")
    
    # Save fix report
    report = {
        'timestamp': datetime.now().isoformat(),
        'notebooks_fixed': fixed_count,
        'notebooks_processed': len(notebooks_to_fix)
    }
    
    with open(examples_dir / 'notebook_api_fixes.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: notebook_api_fixes.json")


if __name__ == "__main__":
    main()
