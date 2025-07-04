#!/usr/bin/env python3
"""Fix specific indentation error in notebook."""

import json

# Fix 07_scitex_dict.ipynb
with open('07_scitex_dict.ipynb', 'r') as f:
    notebook = json.load(f)

# Find and fix the problematic cell
for cell in notebook['cells']:
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
            
        if 'try:\nselected_features = scitex.dict.pop_keys' in source_text:
            # Fix the indentation
            source_text = source_text.replace(
                'try:\nselected_features = scitex.dict.pop_keys',
                'try:\n    selected_features = scitex.dict.pop_keys'
            )
            
            # Update cell source
            if isinstance(cell['source'], list):
                cell['source'] = source_text.split('\n')
                for i in range(len(cell['source']) - 1):
                    if not cell['source'][i].endswith('\n'):
                        cell['source'][i] += '\n'
            else:
                cell['source'] = source_text
            
            print("Fixed indentation in 07_scitex_dict.ipynb")
            break

# Save the fixed notebook
with open('07_scitex_dict.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

# Fix 05_scitex_path.ipynb - missing datetime import
with open('05_scitex_path.ipynb', 'r') as f:
    notebook = json.load(f)

# Find cell with BackupManager class and add datetime import
for i, cell in enumerate(notebook['cells']):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
            
        if 'class BackupManager:' in source_text and 'import datetime' not in source_text:
            # Add import at the beginning
            source_text = 'import datetime\n\n' + source_text
            
            # Update cell source
            if isinstance(cell['source'], list):
                cell['source'] = source_text.split('\n')
                for j in range(len(cell['source']) - 1):
                    if not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
            else:
                cell['source'] = source_text
            
            print("Added datetime import to 05_scitex_path.ipynb")
            break

# Save the fixed notebook
with open('05_scitex_path.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("Fixes applied!")