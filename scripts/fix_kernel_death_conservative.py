#!/usr/bin/env python3
"""
Conservative fix for kernel death issues - only modifies the most problematic parts.
"""

import json
from pathlib import Path
import shutil

def apply_conservative_fixes(notebook_path):
    """Apply minimal fixes to prevent kernel death."""
    
    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    modifications = []
    
    # Add a global memory management cell at the beginning
    memory_mgmt_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Memory management for automated execution\n",
            "import gc\n",
            "import matplotlib\n",
            "matplotlib.use('Agg')  # Non-interactive backend\n",
            "import matplotlib.pyplot as plt\n",
            "plt.ioff()  # Turn off interactive mode\n",
            "\n",
            "# Function to clean up matplotlib\n",
            "def cleanup_plt():\n",
            "    plt.close('all')\n",
            "    gc.collect()\n"
        ]
    }
    
    # Insert after the first import cell
    inserted = False
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code' and not inserted:
            source = ''.join(cell.get('source', []))
            if 'import' in source and 'scitex' in source:
                notebook['cells'].insert(i + 1, memory_mgmt_cell)
                modifications.append("Added memory management cell")
                inserted = True
                break
    
    # Fix specific problematic cells
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            original_source = source
            
            # Add cleanup after matplotlib plots
            if 'plt.show()' in source:
                source = source.replace('plt.show()', 'plt.show()\ncleanup_plt()  # Free memory')
                
            # Limit the caching demonstration
            if 'cached_computation' in source and 'time.time()' in source:
                # Replace the computation with a simpler version
                source = source.replace('cached_computation(100)', 'cached_computation(10)')
                source = source.replace('min(n, 100)', 'min(n, 10)')
                
            # Skip shell command execution entirely
            if 'scitex.gen.shell' in source or 'subprocess' in source:
                lines = source.split('\n')
                new_lines = []
                for line in lines:
                    if 'shell' in line or 'subprocess' in line:
                        new_lines.append('# ' + line + '  # Skipped for safety')
                    else:
                        new_lines.append(line)
                source = '\n'.join(new_lines)
            
            # Update cell if modified
            if source != original_source:
                cell['source'] = source.split('\n')
                for i in range(len(cell['source']) - 1):
                    if not cell['source'][i].endswith('\n'):
                        cell['source'][i] += '\n'
                modifications.append(f"Modified cell with: {source[:50]}...")
    
    return notebook, modifications

def main():
    # Restore from backup first
    notebook_path = Path("examples/02_scitex_gen.ipynb")
    backup_path = Path("examples/02_scitex_gen.ipynb.bak")
    
    if backup_path.exists():
        print("Restoring from original backup...")
        shutil.copy(backup_path, notebook_path)
    
    # Apply conservative fixes
    fixed_notebook, modifications = apply_conservative_fixes(notebook_path)
    
    if modifications:
        # Write fixed notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_notebook, f, indent=2)
        
        print(f"✓ Applied conservative fixes to {notebook_path.name}:")
        for mod in modifications:
            print(f"  - {mod}")
    
    print("\nConservative fixes complete!")

if __name__ == "__main__":
    main()