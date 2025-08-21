#!/usr/bin/env python3
"""Debug the Zotero translator loading and JavaScript generation."""

import sys
import json
sys.path.insert(0, 'src')

from pathlib import Path

# Load the ScienceDirect translator
translator_file = Path("src/scitex/scholar/url/helpers/finders/zotero_translators/ScienceDirect.js")
with open(translator_file, "r", encoding="utf-8") as f:
    content = f.read()

# Extract metadata and code
lines = content.split("\n")
json_end_idx = -1
brace_count = 0

for i, line in enumerate(lines):
    if line.strip() == "{":
        brace_count = 1
    elif brace_count > 0:
        brace_count += line.count("{") - line.count("}")
        if brace_count == 0:
            json_end_idx = i
            break

if json_end_idx != -1:
    # Extract JavaScript code (after metadata)
    js_code = "\n".join(lines[json_end_idx + 1:]).lstrip()
    
    # Remove test cases section
    test_idx = js_code.find("/** BEGIN TEST CASES **/")
    if test_idx > 0:
        js_code = js_code[:test_idx]
    
    # Try to JSON encode it
    translator_code_json = json.dumps(js_code)
    
    print(f"Original JS code length: {len(js_code)}")
    print(f"JSON encoded length: {len(translator_code_json)}")
    print(f"First 200 chars of JS: {js_code[:200]}")
    print(f"First 200 chars of JSON: {translator_code_json[:200]}")
    
    # Check if there are any problematic characters
    if "<" in js_code[:1000]:
        print("\nWARNING: Found '<' in first 1000 chars")
        idx = js_code.index("<")
        print(f"Context around '<' at position {idx}:")
        print(js_code[max(0, idx-50):idx+50])