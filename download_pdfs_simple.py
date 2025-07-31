#!/usr/bin/env python3
"""
Simple PDF download script for papers with DOIs.
Uses the existing test_papers_enriched_final.bib as a starting point.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scitex.scholar import Scholar, Papers

# Output directory
output_dir = Path("downloaded_papers")
output_dir.mkdir(exist_ok=True)

# Load the enriched test papers (5 papers with DOIs)
test_file = ".dev/test_papers_enriched_final.bib"
print(f"Loading enriched papers from: {test_file}")

papers = Papers.from_bibtex(test_file)
print(f"Loaded {len(papers)} papers with DOIs")

# Initialize Scholar
scholar = Scholar()

# Download PDFs one by one
for i, paper in enumerate(papers):
    print(f"\n[{i+1}/{len(papers)}] Processing: {paper.title[:60]}...")
    print(f"  DOI: {paper.doi}")
    
    if not paper.doi:
        print("  ✗ No DOI, skipping")
        continue
    
    # Generate filename
    first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
    year = paper.year or "0000"
    journal_abbrev = ''.join([word[0].upper() for word in (paper.journal or "Unknown").split()[:3]])
    filename = f"{first_author}-{year}-{journal_abbrev}.pdf"
    filepath = output_dir / filename
    
    if filepath.exists():
        print(f"  ✓ Already downloaded: {filename}")
        continue
    
    try:
        # Try to download
        print(f"  → Attempting download...")
        downloaded = scholar.download_pdfs(
            [paper.doi],
            output_dir=str(output_dir),
            acknowledge_ethical_usage=True
        )
        
        if downloaded and downloaded[0].pdf_path:
            # Rename to our format
            original_path = Path(downloaded[0].pdf_path)
            if original_path.exists():
                original_path.rename(filepath)
                print(f"  ✓ Downloaded: {filename}")
            else:
                print(f"  ✗ Download failed: file not found")
        else:
            print(f"  ✗ Download failed: no PDF returned")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Be respectful
    if i < len(papers) - 1:
        time.sleep(2)

print(f"\n\nDownloaded PDFs are in: {output_dir}/")
print("Next step: Run enrichment on the full 75-paper BibTeX file")