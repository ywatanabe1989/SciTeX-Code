#!/usr/bin/env python3
# Find and fix indentation error in notebook

import json
from pathlib import Path

notebook_path = Path("examples/notebooks/02_scitex_gen.ipynb")

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Check each code cell for indentation issues
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        
        # Look for "else:" followed by "except" pattern
        if 'else:' in source and 'except Exception as e:' in source:
            lines = source.split('\n')
            for j, line in enumerate(lines):
                if line.strip() == 'else:' and j + 1 < len(lines):
                    next_line = lines[j + 1]
                    # Check if next line needs indentation
                    if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t'):
                        print(f"Found indentation issue in cell {i}")
                        print(f"Line {j+1}: {line}")
                        print(f"Line {j+2}: {next_line}")
                        print("First 100 chars of cell:")
                        print(source[:100] + "...")
                        print("-" * 60)

# The problematic cell appears to be cell 18
# Let's fix it properly
if len(notebook['cells']) > 18 and notebook['cells'][18]['cell_type'] == 'code':
    source_lines = notebook['cells'][18]['source']
    
    # Check if it's a list of lines or a single string
    if isinstance(source_lines, list):
        source = ''.join(source_lines)
    else:
        source = source_lines
    
    # Fix the indentation issue
    fixed_source = source.replace(
        "else:\nexcept Exception as e:",
        "else:\n    pass\nexcept Exception as e:"
    )
    
    # Convert back to list format
    notebook['cells'][18]['source'] = fixed_source.split('\n')
    
    # Save the fixed notebook
    with open(notebook_path, 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"\nFixed indentation in cell 18")
    print("The notebook should now run without indentation errors.")