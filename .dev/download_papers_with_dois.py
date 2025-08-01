#!/usr/bin/env python3
"""Download papers using DOIs from enhanced instructions."""

import os
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

def extract_dois_from_instructions():
    """Extract DOIs from enhanced download instructions."""
    instructions_file = Path("enhanced_download_instructions.md")
    
    with open(instructions_file, 'r') as f:
        content = f.read()
    
    # Pattern to extract DOI and filename
    papers = []
    sections = content.split('### ')
    
    for section in sections[1:]:  # Skip first empty section
        lines = section.strip().split('\n')
        
        # Extract paper info
        paper_info = {}
        
        # Get title (first line)
        paper_info['title'] = lines[0].split('. ')[1].strip('...')
        
        # Extract details from lines
        for line in lines:
            if line.startswith('- **DOI**:'):
                doi = line.split(':', 1)[1].strip()
                if doi and doi != '':
                    paper_info['doi'] = doi
            elif line.startswith('- **Save as**:'):
                filename = line.split('`')[1]
                paper_info['filename'] = filename
        
        # Only add papers with DOIs
        if 'doi' in paper_info:
            papers.append(paper_info)
    
    return papers

def download_papers_with_dois():
    """Download papers that have DOIs."""
    from src.scitex.scholar import Scholar
    
    # Extract papers with DOIs
    papers_with_dois = extract_dois_from_instructions()
    print(f"Found {len(papers_with_dois)} papers with DOIs")
    
    # Create Scholar instance
    scholar = Scholar()
    
    # Download directory
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    
    # Extract just the DOIs
    dois = [p['doi'] for p in papers_with_dois]
    
    print(f"\nDOIs to download:")
    for i, paper in enumerate(papers_with_dois):
        print(f"{i+1}. {paper['doi']} -> {paper['filename']}")
    
    # Download PDFs
    print(f"\nDownloading PDFs to {download_dir.absolute()}")
    results = scholar.download_pdfs(
        dois,
        download_dir=download_dir,
        show_progress=True,
        acknowledge_ethical_usage=True
    )
    
    return results, papers_with_dois

if __name__ == "__main__":
    results, papers = download_papers_with_dois()
    
    # Report results
    if results and 'successful' in results:
        print(f"\n✓ Downloaded {results['successful']} PDFs successfully")
        print(f"✗ Failed: {results['failed']}")
        
        # Show which files were downloaded
        if 'downloaded_files' in results:
            print("\nDownloaded files:")
            for doi, filepath in results['downloaded_files'].items():
                print(f"  {doi} -> {filepath}")
    else:
        print("\nNo results returned")