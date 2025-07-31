#!/usr/bin/env python3
"""
Generate download URLs and instructions for manual PDF downloads.
Workaround for blocked automated downloads.
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Simple BibTeX parser
def parse_bibtex_simple(content):
    """Extract basic fields from BibTeX content."""
    entries = []
    
    # Split by @ to get entries
    raw_entries = content.split('@')[1:]
    
    for raw_entry in raw_entries:
        if not raw_entry.strip():
            continue
            
        entry = {}
        
        # Extract fields using simple regex-like parsing
        for field in ['title', 'author', 'year', 'journal', 'doi', 'url']:
            # Look for field = {value} or field = "value"
            start_idx = raw_entry.find(f'{field} =')
            if start_idx == -1:
                start_idx = raw_entry.find(f'{field}=')
            
            if start_idx != -1:
                # Find the start of the value
                value_start = raw_entry.find('{', start_idx)
                if value_start == -1:
                    value_start = raw_entry.find('"', start_idx)
                
                if value_start != -1:
                    # Find the end of the value
                    if raw_entry[value_start] == '{':
                        value_end = raw_entry.find('}', value_start)
                    else:
                        value_end = raw_entry.find('"', value_start + 1)
                    
                    if value_end != -1:
                        value = raw_entry[value_start+1:value_end]
                        entry[field] = value.strip()
        
        if entry:
            entries.append(entry)
    
    return entries

# Load BibTeX file
bibtex_file = "src/scitex/scholar/docs/from_user/papers.bib"
print(f"Loading papers from: {bibtex_file}")

with open(bibtex_file, 'r', encoding='utf-8') as f:
    content = f.read()

entries = parse_bibtex_simple(content)
print(f"Parsed {len(entries)} entries")

# Create output directory
output_dir = Path("downloaded_papers")
output_dir.mkdir(exist_ok=True)

# Generate download instructions
instructions_file = Path("manual_download_instructions.md")
urls_file = Path("download_urls.json")

download_data = []

with open(instructions_file, 'w') as f:
    f.write("# Manual PDF Download Instructions\n\n")
    f.write(f"Please download the following papers and save them to: `{output_dir.absolute()}/`\n\n")
    f.write("## Papers to Download\n\n")
    
    for i, entry in enumerate(entries[:20]):  # First 20 papers
        title = entry.get('title', 'Unknown Title')[:100]
        authors = entry.get('author', 'Unknown Authors')
        year = entry.get('year', '0000')
        journal = entry.get('journal', 'Unknown Journal')
        doi = entry.get('doi', '')
        url = entry.get('url', '')
        
        # Generate filename
        if authors and authors != 'Unknown Authors':
            # Extract first author's last name
            first_author = authors.split(' and ')[0]
            last_name = first_author.split()[-1] if first_author else "Unknown"
        else:
            last_name = "Unknown"
        
        # Create journal abbreviation
        journal_words = journal.split()[:3]
        journal_abbrev = ''.join([w[0].upper() for w in journal_words if w])
        if not journal_abbrev:
            journal_abbrev = "UNK"
        
        filename = f"{last_name}-{year}-{journal_abbrev}.pdf"
        
        # Write instructions
        f.write(f"### {i+1}. {title}...\n\n")
        f.write(f"- **Authors**: {authors[:100]}...\n")
        f.write(f"- **Year**: {year}\n")
        f.write(f"- **Journal**: {journal}\n")
        
        if doi:
            doi_url = f"https://doi.org/{doi}"
            f.write(f"- **DOI URL**: [{doi_url}]({doi_url})\n")
        elif url:
            f.write(f"- **URL**: [{url}]({url})\n")
        else:
            f.write(f"- **URL**: No DOI or URL available - search manually\n")
        
        f.write(f"- **Save as**: `{filename}`\n\n")
        
        # Store data for JSON
        download_data.append({
            "index": i + 1,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "doi": doi,
            "url": url or doi_url if doi else None,
            "filename": filename
        })

# Save URLs as JSON
with open(urls_file, 'w') as f:
    json.dump(download_data, f, indent=2)

print(f"\n✓ Generated download instructions: {instructions_file}")
print(f"✓ Generated URLs JSON: {urls_file}")
print(f"\nNext steps:")
print(f"1. Open {instructions_file} and follow the manual download instructions")
print(f"2. Save all PDFs to: {output_dir.absolute()}/")
print(f"3. Use University of Melbourne credentials when prompted")
print(f"4. For difficult papers, note them for alternative access methods")