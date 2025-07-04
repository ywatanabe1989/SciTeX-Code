#!/usr/bin/env python3
"""Fix recursive autosummary references in API docs."""

import glob
import re

api_files = glob.glob("docs/RTD/api/scitex.*.rst")

for filepath in api_files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove the recursive module reference
    pattern = r'(.. autosummary::\s*\n\s*:toctree: generated\s*\n\s*:recursive:\s*\n\s*\n\s*scitex\.\w+)'
    replacement = r'.. autosummary::\n   :toctree: generated'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Also fix simpler patterns
    pattern2 = r'(.. autosummary::\s*\n\s*:toctree: generated\s*\n\s*\n\s*scitex\.\w+)'
    new_content = re.sub(pattern2, replacement, new_content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed: {filepath}")

print("Done!")