#!/usr/bin/env python3
"""
Download ALL PDFs from your BibTeX file, including paywalled content.
Uses your browser's saved logins (university account, etc.) to access paywalled papers.
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader, find_chrome_profile
from src.scitex.scholar.smart_pdf_downloader import SmartPDFDownloader
from scitex.io import load


def main():
    """Download all PDFs with a two-stage approach."""
    
    # Get BibTeX file
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
    else:
        # Try to find enhanced file
        possible_files = [
            "papers_enhanced_final_v2.bib",
            "papers_with_all_dois.bib",
            "/home/ywatanabe/win/downloads/papers.bib",
        ]
        
        bibtex_file = None
        for f in possible_files:
            if Path(f).exists():
                bibtex_file = f
                break
        
        if not bibtex_file:
            print("Usage: python download_all_pdfs.py <bibtex_file>")
            return
    
    print(f"Loading BibTeX file: {bibtex_file}")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Extract papers with DOIs
    papers_with_doi = []
    papers_without_doi = []
    
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        title = fields.get('title', 'Unknown')
        
        paper_info = {
            'title': title,
            'year': fields.get('year'),
            'journal': fields.get('journal'),
            'authors': fields.get('author', ''),
            'entry': entry
        }
        
        if doi:
            paper_info['doi'] = doi
            papers_with_doi.append(paper_info)
        else:
            papers_without_doi.append(paper_info)
    
    print(f"\nFound {len(entries)} total papers:")
    print(f"  ✓ {len(papers_with_doi)} with DOIs")
    print(f"  ✗ {len(papers_without_doi)} without DOIs")
    
    if not papers_with_doi:
        print("\nNo papers with DOIs found.")
        return
    
    # Show summary
    print(f"\nWill download PDFs for {len(papers_with_doi)} papers")
    print("\nThis process will:")
    print("1. First try open access sources (fast, no login needed)")
    print("2. Then use your browser with saved logins for paywalled content")
    print("   (will open Chrome and use your university credentials)")
    
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Prepare DOI lists
    all_dois = [p['doi'] for p in papers_with_doi]
    doi_to_title = {p['doi']: p['title'] for p in papers_with_doi}
    
    # Stage 1: Try open access sources first
    print("\n" + "="*60)
    print("STAGE 1: Checking open access sources...")
    print("="*60)
    
    open_access_dir = Path("pdfs_open_access")
    smart_downloader = SmartPDFDownloader(
        output_dir=str(open_access_dir),
        email="research@example.com"
    )
    
    open_access_results = smart_downloader.download_batch(
        all_dois,
        max_workers=5,  # Faster for open access
    )
    
    # Find remaining DOIs
    remaining_dois = [doi for doi in all_dois if doi not in open_access_results]
    
    if not remaining_dois:
        print("\nAll papers were available via open access!")
        return
    
    # Stage 2: Use authenticated browser for remaining papers
    print("\n" + "="*60)
    print(f"STAGE 2: Downloading {len(remaining_dois)} paywalled papers...")
    print("="*60)
    print("\nThis will open Chrome and use your saved logins.")
    print("Make sure you're logged into your university library/journal sites in Chrome.")
    
    response = input("\nReady to open browser? (y/n): ")
    if response.lower() != 'y':
        print("Skipping paywalled downloads.")
        return
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"\nUsing Chrome profile: {profile_path}")
    else:
        print("\nWarning: No Chrome profile found. You may need to login manually.")
    
    # Download with authentication
    auth_dir = Path("pdfs_authenticated")
    auth_downloader = AuthenticatedPDFDownloader(
        output_dir=str(auth_dir),
        chrome_profile_path=profile_path,
        headless=False  # Show browser so user can see what's happening
    )
    
    auth_results = auth_downloader.download_batch(
        remaining_dois,
        delay_between=3,  # Be polite to servers
        titles={doi: doi_to_title[doi] for doi in remaining_dois}
    )
    
    # Final summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    
    total_downloaded = len(open_access_results) + len(auth_results)
    print(f"\nTotal downloaded: {total_downloaded}/{len(all_dois)} PDFs")
    print(f"  Open access: {len(open_access_results)}")
    print(f"  Via authentication: {len(auth_results)}")
    print(f"  Failed: {len(all_dois) - total_downloaded}")
    
    print(f"\nPDFs saved in:")
    print(f"  {open_access_dir}/ - Open access papers")
    print(f"  {auth_dir}/ - Paywalled papers")
    
    # Merge all PDFs to one directory
    response = input("\nMerge all PDFs to a single directory? (y/n): ")
    if response.lower() == 'y':
        merged_dir = Path("all_pdfs")
        merged_dir.mkdir(exist_ok=True)
        
        # Copy all PDFs
        copied = 0
        for source_dir in [open_access_dir, auth_dir]:
            if source_dir.exists():
                for pdf in source_dir.glob("*.pdf"):
                    target = merged_dir / pdf.name
                    if not target.exists():
                        import shutil
                        shutil.copy2(pdf, target)
                        copied += 1
        
        print(f"\nCopied {copied} PDFs to: {merged_dir}/")
    
    # Show failed papers
    all_results = {**open_access_results, **auth_results}
    failed_dois = [doi for doi in all_dois if doi not in all_results]
    
    if failed_dois:
        print(f"\nFailed to download {len(failed_dois)} papers:")
        for doi in failed_dois[:5]:
            paper = next(p for p in papers_with_doi if p['doi'] == doi)
            print(f"  - {paper['title'][:60]}...")
            print(f"    DOI: {doi}")
        if len(failed_dois) > 5:
            print(f"  ... and {len(failed_dois) - 5} more")
        
        # Save failed list
        with open("failed_downloads.txt", "w") as f:
            f.write("Failed to download these papers:\n\n")
            for doi in failed_dois:
                paper = next(p for p in papers_with_doi if p['doi'] == doi)
                f.write(f"Title: {paper['title']}\n")
                f.write(f"DOI: {doi}\n")
                f.write(f"Year: {paper.get('year', 'Unknown')}\n")
                f.write(f"Journal: {paper.get('journal', 'Unknown')}\n")
                f.write("-" * 80 + "\n\n")
        print("\nFailed papers saved to: failed_downloads.txt")


if __name__ == "__main__":
    main()