#!/usr/bin/env python3
"""Download PDFs using Puppeteer MCP to navigate OpenURL resolver."""

import json
import time
from pathlib import Path

# Load download status
with open('.dev/download_status_report.json') as f:
    report = json.load(f)

print(f"Total papers: {report['total_papers']}")
print(f"Already downloaded: {report['already_downloaded']}")
print(f"Papers to download: {report['papers_to_download']}")
print()

# Function to download PDFs using shell commands
def download_pdf_with_puppeteer(paper_info):
    """Download a PDF by navigating to OpenURL and finding PDF link."""
    
    print(f"\n{'='*60}")
    print(f"Downloading Paper {paper_info['index']}: {paper_info['title'][:50]}...")
    print(f"DOI: {paper_info['doi']}")
    
    # Create a Python script that will use the MCP tools
    # Since we can't directly use MCP from within Python, we'll output instructions
    
    instructions = f"""
# Instructions for downloading {paper_info['filename']}:

1. Navigate to OpenURL:
   URL: {paper_info['openurl']}

2. Wait for page to load and look for:
   - "Full Text" or "PDF" links
   - Download buttons
   - Direct PDF viewer

3. Save PDF as: downloaded_papers/{paper_info['filename']}

4. If authentication is required:
   - The browser should have stored OpenAthens cookies
   - Look for institutional login options
"""
    
    return instructions

# Generate download instructions for first 5 papers
output_dir = Path('downloaded_papers')
output_dir.mkdir(exist_ok=True)

all_instructions = []

for paper in report['download_urls'][:5]:
    # Check if already downloaded
    pdf_path = output_dir / paper['filename']
    if pdf_path.exists():
        print(f"\n✓ Already exists: {paper['filename']}")
        continue
    
    instructions = download_pdf_with_puppeteer(paper)
    all_instructions.append(instructions)

# Save all instructions
with open('.dev/puppeteer_download_instructions.txt', 'w') as f:
    f.write('\n'.join(all_instructions))

print(f"\n{'='*60}")
print("Download instructions saved to: .dev/puppeteer_download_instructions.txt")
print("\nTo download PDFs manually:")
print("1. Run: ./.dev/open_papers_in_browser.sh")
print("2. Use browser extensions (Zotero Connector) to save PDFs")
print("3. Or use the Puppeteer MCP to navigate and download")

# Create a summary of what needs to be downloaded
summary = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'total_papers': report['total_papers'],
    'downloaded': report['already_downloaded'],
    'remaining': report['papers_to_download'],
    'next_papers': [
        {
            'index': p['index'],
            'title': p['title'],
            'doi': p['doi'],
            'filename': p['filename'],
            'openurl': p['openurl']
        }
        for p in report['download_urls'][:10]
        if not (output_dir / p['filename']).exists()
    ]
}

with open('.dev/download_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nDownload summary saved to: .dev/download_summary.json")