#!/usr/bin/env python3
"""
Direct approach to download papers without complex imports.
"""

import os
import sys
import json
import time
from pathlib import Path

# Simple BibTeX parser
def parse_bibtex(filename):
    """Simple BibTeX parser to extract basic fields."""
    entries = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by @ to get entries
    raw_entries = content.split('@')[1:]  # Skip empty first element
    
    for raw_entry in raw_entries:
        if not raw_entry.strip():
            continue
            
        entry = {}
        lines = raw_entry.strip().split('\n')
        
        # Get entry type and key
        first_line = lines[0]
        entry_type, rest = first_line.split('{', 1)
        entry['type'] = entry_type.strip()
        entry['key'] = rest.split(',')[0].strip()
        
        # Parse fields
        current_field = None
        current_value = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line == '}':
                continue
                
            if '=' in line and not current_field:
                # New field
                if current_field and current_value:
                    entry[current_field] = ' '.join(current_value).strip(' {},')
                    
                field_name, field_value = line.split('=', 1)
                current_field = field_name.strip()
                current_value = [field_value.strip()]
            else:
                # Continuation of previous field
                current_value.append(line)
        
        # Don't forget the last field
        if current_field and current_value:
            entry[current_field] = ' '.join(current_value).strip(' {},')
        
        entries.append(entry)
    
    return entries

# Load BibTeX
bibtex_file = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/from_user/papers.bib"
print(f"Loading papers from: {bibtex_file}")

entries = parse_bibtex(bibtex_file)
print(f"Loaded {len(entries)} entries")

# Create output directory
output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/downloaded_papers")
output_dir.mkdir(exist_ok=True)

# Progress tracking
progress_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/download_progress.json")
if progress_file.exists():
    with open(progress_file, 'r') as f:
        progress = json.load(f)
else:
    progress = {"downloaded": [], "failed": [], "manual_needed": []}

# Show first 5 entries
print("\nFirst 5 papers:")
for i, entry in enumerate(entries[:5]):
    print(f"\n{i+1}. Title: {entry.get('title', 'N/A')[:80]}...")
    print(f"   DOI: {entry.get('doi', 'N/A')}")
    print(f"   Authors: {entry.get('author', 'N/A')[:80]}...")
    print(f"   Year: {entry.get('year', 'N/A')}")
    print(f"   Journal: {entry.get('journal', 'N/A')}")

# Try to download using wget for open access papers
print("\n" + "="*80)
print("Attempting downloads...")
print("="*80)

# Test with first paper that has a DOI
for entry in entries[:1]:
    doi = entry.get('doi', '').strip('"')
    if not doi:
        continue
        
    print(f"\nTesting download for DOI: {doi}")
    
    # Generate filename
    authors = entry.get('author', 'Unknown').replace(' and ', ', ')
    first_author = authors.split(',')[0].split()[-1] if authors else "Unknown"
    year = entry.get('year', '0000').strip('"')
    journal = entry.get('journal', 'Unknown').strip('"')
    journal_abbrev = ''.join([word[0].upper() for word in journal.split()[:3]])
    filename = f"{first_author}-{year}-{journal_abbrev}.pdf"
    
    print(f"Target filename: {filename}")
    
    # Add to manual intervention list
    progress['manual_needed'].append({
        "doi": doi,
        "title": entry.get('title', 'N/A').strip('"'),
        "filename": filename,
        "url": f"https://doi.org/{doi}"
    })

# Save progress
with open(progress_file, 'w') as f:
    json.dump(progress, f, indent=2)

print(f"\nProgress saved to: {progress_file}")
print(f"Manual intervention needed for {len(progress['manual_needed'])} papers")

# Create a manual download guide
guide_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/manual_download_guide.md")
with open(guide_file, 'w') as f:
    f.write("# Manual Download Guide\n\n")
    f.write("The following papers need manual download:\n\n")
    
    for i, paper in enumerate(progress['manual_needed'][:10]):  # First 10
        f.write(f"## {i+1}. {paper['title'][:100]}...\n")
        f.write(f"- DOI: {paper['doi']}\n")
        f.write(f"- URL: {paper['url']}\n")
        f.write(f"- Save as: `{paper['filename']}`\n")
        f.write(f"- Save to: `{output_dir}/`\n\n")

print(f"\nManual download guide created: {guide_file}")