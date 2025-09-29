#!/usr/bin/env python3
"""
Open remaining papers in Chrome with Zotero proxy support.
Zotero WSL ProxyServer is running on http://ywata-note-win.local:23119
"""

import os
import json
import subprocess
import time
from pathlib import Path

def check_pdf_status():
    """Check which papers have PDFs and which don't."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    
    papers_with_pdf = []
    papers_without_pdf = []
    
    # Iterate through all symlinks in pac directory
    for item in pac_dir.iterdir():
        if item.is_symlink():
            # Follow symlink to actual directory in MASTER
            target_dir = item.resolve()
            if target_dir.exists():
                # Check for PDF in the actual MASTER directory
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        
                    paper_info = {
                        'id': target_dir.name,  # Use target ID, not symlink name
                        'symlink_name': item.name,  # Keep symlink name for reference
                        'title': metadata.get('title', 'Unknown'),
                        'doi': metadata.get('doi', ''),
                        'journal': metadata.get('journal', ''),
                        'year': metadata.get('year', ''),
                        'has_pdf': len(pdf_files) > 0
                    }
                    
                    if pdf_files:
                        papers_with_pdf.append(paper_info)
                    else:
                        papers_without_pdf.append(paper_info)
    
    return papers_with_pdf, papers_without_pdf

def open_papers_for_zotero(papers, limit=10):
    """Open papers in Chrome for Zotero capture."""
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Skip IEEE papers (not subscribed)
    filtered_papers = []
    for paper in papers:
        if 'IEEE' not in paper.get('journal', ''):
            filtered_papers.append(paper)
    
    print(f"Opening {min(limit, len(filtered_papers))} papers in Chrome for Zotero capture...")
    print("=" * 60)
    
    urls_to_open = []
    for i, paper in enumerate(filtered_papers[:limit]):
        doi = paper.get('doi', '')
        if doi:
            url = f'https://doi.org/{doi}'
            urls_to_open.append(url)
            print(f"{i+1}. {paper['title'][:50]}...")
            print(f"   Journal: {paper['journal']}")
            print(f"   DOI: {doi}")
    
    if urls_to_open:
        # Open all URLs in Chrome
        args = [
            'google-chrome',
            f'--user-data-dir={profile_dir}',
            '--profile-directory=Profile 1',
        ] + urls_to_open
        
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("\n" + "=" * 60)
        print("ZOTERO CAPTURE INSTRUCTIONS:")
        print("1. Chrome is opening with authenticated papers")
        print("2. Zotero WSL Proxy is running at http://ywata-note-win.local:23119")
        print("3. Click the Zotero Connector icon in Chrome")
        print("4. Papers will be saved to your Zotero library")
        print("5. PDFs will download with institutional access")
        print("\nZotero is now connected via WSL proxy!")

def main():
    print("PAC Collection - Zotero Capture Helper")
    print("=" * 60)
    
    # Check status
    papers_with_pdf, papers_without_pdf = check_pdf_status()
    
    print(f"Papers WITH PDF: {len(papers_with_pdf)}")
    print(f"Papers WITHOUT PDF: {len(papers_without_pdf)}")
    print()
    
    if papers_without_pdf:
        print("Opening papers without PDFs for Zotero capture...")
        open_papers_for_zotero(papers_without_pdf, limit=15)
    else:
        print("All papers have PDFs!")

if __name__ == "__main__":
    main()