#!/usr/bin/env python3
"""
Download PDFs for all papers in your enhanced BibTeX file using Zotero.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.io import load
from doi_to_pdf_simple import download_pdfs_with_zotero


def main():
    """Main function to download PDFs from BibTeX."""
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python download_pdfs_from_bibtex.py <bibtex_file>")
        print("\nExample:")
        print("  python download_pdfs_from_bibtex.py papers_enhanced_final_v2.bib")
        return
    
    bibtex_file = sys.argv[1]
    
    if not Path(bibtex_file).exists():
        print(f"Error: File not found: {bibtex_file}")
        return
    
    print(f"Loading BibTeX file: {bibtex_file}")
    entries = load(bibtex_file)
    
    # Extract papers with DOIs
    papers_with_doi = []
    papers_without_doi = []
    
    for entry in entries:
        fields = entry.get('fields', {})
        title = fields.get('title', 'Unknown')
        doi = fields.get('doi')
        
        if doi:
            papers_with_doi.append({
                'doi': doi,
                'title': title,
                'year': fields.get('year'),
                'journal': fields.get('journal')
            })
        else:
            papers_without_doi.append(title)
    
    print(f"\nFound {len(entries)} total papers:")
    print(f"  ✓ {len(papers_with_doi)} with DOIs (ready to download)")
    print(f"  ✗ {len(papers_without_doi)} without DOIs (cannot download)")
    
    if papers_without_doi and len(papers_without_doi) <= 10:
        print("\nPapers without DOIs:")
        for title in papers_without_doi[:10]:
            print(f"  - {title[:60]}...")
    
    if not papers_with_doi:
        print("\nNo papers with DOIs found. Nothing to download.")
        return
    
    # Show some examples
    print(f"\nFirst few papers to download:")
    for paper in papers_with_doi[:5]:
        print(f"  - {paper['title'][:60]}... ({paper['doi']})")
    
    if len(papers_with_doi) > 5:
        print(f"  ... and {len(papers_with_doi) - 5} more")
    
    # Confirm
    response = input(f"\nDownload PDFs for {len(papers_with_doi)} papers? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Extract just DOIs for download
    dois = [p['doi'] for p in papers_with_doi]
    
    # Create progress file with same base name as BibTeX
    progress_file = Path(bibtex_file).stem + "_pdf_progress.json"
    
    # Start download
    print(f"\nProgress will be saved to: {progress_file}")
    download_pdfs_with_zotero(dois, progress_file)


if __name__ == "__main__":
    main()