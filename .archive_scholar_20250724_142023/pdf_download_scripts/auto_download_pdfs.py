#!/usr/bin/env python3
"""
Fully automated PDF downloader for your BibTeX files.
No manual intervention required!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.pdf_auto_downloader import AutoPDFDownloader
from scitex.io import load


def main():
    """Download PDFs automatically from BibTeX file."""
    
    # Get BibTeX file from command line or use default
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
    else:
        # Try to find your enhanced file
        possible_files = [
            "papers_enhanced_final_v2.bib",
            "papers_with_all_dois.bib",
            "process_remaining_dois_batch_out/papers_enhanced_final_batch.bib",
        ]
        
        bibtex_file = None
        for f in possible_files:
            if Path(f).exists():
                bibtex_file = f
                break
        
        if not bibtex_file:
            print("Usage: python auto_download_pdfs.py <bibtex_file>")
            print("\nNo BibTeX file found. Please specify one.")
            return
    
    print(f"Using BibTeX file: {bibtex_file}")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Extract DOIs and titles
    papers = []
    no_doi_count = 0
    
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        title = fields.get('title', 'Unknown')
        
        if doi:
            papers.append({
                'doi': doi,
                'title': title,
                'year': fields.get('year'),
                'journal': fields.get('journal')
            })
        else:
            no_doi_count += 1
    
    print(f"\nFound {len(entries)} total papers:")
    print(f"  ✓ {len(papers)} with DOIs")
    print(f"  ✗ {no_doi_count} without DOIs")
    
    if not papers:
        print("\nNo papers with DOIs found.")
        return
    
    # Show what we'll download
    print(f"\nWill attempt to download PDFs for {len(papers)} papers")
    print("This will ONLY download open access papers (no login required)")
    print("\nFirst few papers:")
    for p in papers[:3]:
        print(f"  - {p['title'][:60]}... [{p['doi']}]")
    if len(papers) > 3:
        print(f"  ... and {len(papers) - 3} more")
    
    # Confirm
    response = input("\nProceed with automatic download? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Create downloader
    output_dir = Path("downloaded_pdfs")
    downloader = AutoPDFDownloader(
        output_dir=str(output_dir),
        email="your.email@example.com"  # Change this to your email
    )
    
    # Extract DOIs and titles for download
    dois = [p['doi'] for p in papers]
    doi_to_title = {p['doi']: p['title'] for p in papers}
    
    # Download!
    print(f"\nStarting automatic download to: {output_dir}/")
    results = downloader.download_batch(
        dois,
        max_workers=3,  # Download 3 at a time
        titles=doi_to_title
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("DOWNLOAD COMPLETE!")
    print(f"{'='*60}")
    print(f"Successfully downloaded: {len(results)} PDFs")
    print(f"Failed/Not available: {len(papers) - len(results)}")
    print(f"PDFs saved to: {output_dir}/")
    
    # Show what was downloaded
    if results:
        print("\nDownloaded papers:")
        for doi, path in list(results.items())[:10]:
            print(f"  ✓ {path.name}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")


if __name__ == "__main__":
    main()