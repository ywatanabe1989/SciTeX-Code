#!/usr/bin/env python3
"""
Quick PDF downloader - downloads a few papers at a time to avoid timeouts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.smart_pdf_downloader import SmartPDFDownloader
from scitex.io import load


def main():
    """Quick download of PDFs."""
    
    # Get BibTeX file
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
    else:
        bibtex_file = "./process_remaining_semantic_out/papers_enhanced_final_v2.bib"
    
    # Optional: number of papers to download
    if len(sys.argv) > 2:
        max_papers = int(sys.argv[2])
    else:
        max_papers = 20  # Default to first 20
    
    print(f"Loading BibTeX file: {bibtex_file}")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Extract DOIs
    dois = []
    doi_to_info = {}
    
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi:
            dois.append(doi)
            doi_to_info[doi] = {
                'title': fields.get('title', 'Unknown'),
                'year': fields.get('year'),
                'journal': fields.get('journal')
            }
    
    print(f"\nFound {len(dois)} papers with DOIs")
    
    if not dois:
        print("No papers with DOIs found.")
        return
    
    # Limit to max_papers
    dois_to_download = dois[:max_papers]
    
    print(f"Downloading first {len(dois_to_download)} papers...")
    
    # Download with smart downloader (open access only)
    downloader = SmartPDFDownloader(
        output_dir="quick_pdfs",
        email="research@example.com"
    )
    
    results = downloader.download_batch(
        dois_to_download,
        max_workers=3
    )
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Downloaded: {len(results)}/{len(dois_to_download)} PDFs")
    print(f"PDFs saved to: quick_pdfs/")
    
    # Show what we got
    if results:
        print("\nSuccessfully downloaded:")
        for doi in results:
            info = doi_to_info[doi]
            print(f"  ✓ {info['title'][:60]}...")
    
    # Show failures
    failed = [doi for doi in dois_to_download if doi not in results]
    if failed:
        print(f"\nFailed to download {len(failed)} papers (likely paywalled):")
        for doi in failed[:5]:
            info = doi_to_info[doi]
            print(f"  ✗ {info['title'][:60]}...")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more")
    
    print("\nTo download paywalled papers, use:")
    print("  python download_with_unimelb.py " + bibtex_file)


if __name__ == "__main__":
    main()