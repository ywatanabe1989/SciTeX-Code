#!/usr/bin/env python3
"""Simple OpenURL resolution script using module command."""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Load paper data
merged_data_file = Path("papers_merged_download_data.json")
with open(merged_data_file) as f:
    papers = json.load(f)

# Load DOI resolution data
doi_map = {}
for doi_file in Path('.').glob('doi_resolution_*.json'):
    try:
        with open(doi_file) as f:
            data = json.load(f)
            if 'papers' in data:
                for key, info in data['papers'].items():
                    if info.get('status') == 'resolved' and 'doi' in info:
                        doi_map[info['title'].lower()] = info['doi']
    except:
        pass

print(f"Found {len(papers)} papers total")
print(f"Found {len(doi_map)} resolved DOIs")

# Collect DOIs
dois_to_resolve = []
for paper in papers[:20]:  # First 20 papers
    doi = paper.get('doi')
    if not doi and paper['title'].lower() in doi_map:
        doi = doi_map[paper['title'].lower()]
    
    if doi:
        dois_to_resolve.append(doi)
        print(f"  {paper['index']:3d}. {doi} - {paper['title'][:50]}...")

print(f"\nWill resolve {len(dois_to_resolve)} DOIs")

# Save DOIs to temp file
dois_file = Path('.dev/dois_to_resolve.txt')
with open(dois_file, 'w') as f:
    for doi in dois_to_resolve:
        f.write(f"{doi}\n")

print(f"DOIs saved to: {dois_file}")

# Create Python script to run
script_content = '''
import sys
import os
sys.path.insert(0, 'src')

from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url._ResumableOpenURLResolver import ResumableOpenURLResolver

# Read DOIs
with open('.dev/dois_to_resolve.txt') as f:
    dois = [line.strip() for line in f if line.strip()]

print(f"Resolving {len(dois)} DOIs...")

# Initialize
auth_manager = AuthenticationManager()
resolver = ResumableOpenURLResolver(
    auth_manager=auth_manager,
    progress_file=".dev/openurl_resolution_progress.json",
    concurrency=2
)

# Resolve
results = resolver.resolve_from_dois(dois)

# Save results
import json
with open('.dev/openurl_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: .dev/openurl_results.json")
'''

# Save and run script
script_path = Path('.dev/run_openurl_resolver.py')
with open(script_path, 'w') as f:
    f.write(script_content)

print(f"\nCreated script: {script_path}")
print("Running OpenURL resolver...")

# Run the script
result = subprocess.run(['python', str(script_path)], capture_output=True, text=True)
print("\nOutput:")
print(result.stdout)
if result.stderr:
    print("\nErrors:")
    print(result.stderr)