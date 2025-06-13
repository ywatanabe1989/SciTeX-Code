#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Script to update all formatter files to use tracked_dict instead of args

import os
import re
import glob

# Find all formatter files
formatters_dir = "src/scitex/plt/_subplots/_export_as_csv_formatters"
formatter_files = glob.glob(f"{formatters_dir}/_format_*.py")

print(f"Found {len(formatter_files)} formatter files to process")

# Pattern to replace in function definition
pattern = r"def (_format_[a-zA-Z0-9_]+)\(id, args, kwargs\):"
replacement = r"def \1(id, tracked_dict, kwargs):"

# Pattern to replace in docstring args section
doc_pattern = r"(        args \(dict\):)"
doc_replacement = r"        tracked_dict (dict):"

# Pattern for internal references to args
internal_pattern = r"args\.get\("
internal_replacement = r"tracked_dict.get("

# Pattern for checking args
check_pattern = r"if not args or not isinstance\(args, dict\):"
check_replacement = r"if not tracked_dict or not isinstance(tracked_dict, dict):"

# Count of files successfully updated
updated_count = 0

for filepath in formatter_files:
    with open(filepath, 'r') as file:
        content = file.read()
    
    # Skip files that already use tracked_dict
    if "def _format_" in content and "tracked_dict" in content:
        print(f"Skipping {filepath} (already updated)")
        continue
    
    # Replace function signature
    updated_content = re.sub(pattern, replacement, content)
    
    # Replace docstring
    updated_content = re.sub(doc_pattern, doc_replacement, updated_content)
    
    # Replace internal references to args
    updated_content = re.sub(internal_pattern, internal_replacement, updated_content)
    
    # Replace check for args
    updated_content = re.sub(check_pattern, check_replacement, updated_content)
    
    # Write the updated content back to the file
    with open(filepath, 'w') as file:
        file.write(updated_content)
    
    updated_count += 1
    print(f"Updated {filepath}")

print(f"\nCompleted: {updated_count} files updated")