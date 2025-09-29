#!/usr/bin/env python3
"""
Non-interactive version of the PDF downloader for testing.
Automatically downloads PDFs without prompts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader, find_chrome_profile
from src.scitex.scholar.smart_pdf_downloader import SmartPDFDownloader
from scitex.io import load


def main():
    """Download PDFs automatically without prompts."""
    
    # Get BibTeX file
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
    else:
        # Find the enhanced file
        bibtex_file = "./process_remaining_semantic_out/papers_enhanced_final_v2.bib"
        if not Path(bibtex_file).exists():
            print(f"BibTeX file not found: {bibtex_file}")
            return
    
    print(f"Loading BibTeX file: {bibtex_file}")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Extract papers with DOIs
    papers_with_doi = []
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi:
            papers_with_doi.append({
                'doi': doi,
                'title': fields.get('title', 'Unknown'),
                'year': fields.get('year'),
                'journal': fields.get('journal')
            })
    
    print(f"\nFound {len(entries)} total papers")
    print(f"Papers with DOIs: {len(papers_with_doi)}")
    
    if not papers_with_doi:
        print("No papers with DOIs found.")
        return
    
    # Show first few
    print("\nFirst 5 papers:")
    for i, p in enumerate(papers_with_doi[:5], 1):
        print(f"{i}. {p['title'][:70]}...")
        print(f"   DOI: {p['doi']}")
    
    # Prepare DOI lists
    all_dois = [p['doi'] for p in papers_with_doi]
    doi_to_title = {p['doi']: p['title'] for p in papers_with_doi}
    
    # Stage 1: Try open access first (quick test with first 10)
    print("\n" + "="*60)
    print("STAGE 1: Testing open access downloads...")
    print("="*60)
    
    test_dois = all_dois[:10]  # Test with first 10
    
    open_access_dir = Path("test_open_access_pdfs")
    smart_downloader = SmartPDFDownloader(
        output_dir=str(open_access_dir),
        email="research@example.com"
    )
    
    print(f"\nTesting with first {len(test_dois)} papers...")
    open_access_results = smart_downloader.download_batch(
        test_dois,
        max_workers=3,
    )
    
    print(f"\nOpen access results: {len(open_access_results)}/{len(test_dois)} downloaded")
    
    # Find remaining
    remaining_dois = [doi for doi in test_dois if doi not in open_access_results]
    
    if not remaining_dois:
        print("\nAll test papers were available via open access!")
        return
    
    # Stage 2: Test authenticated download with first 3 remaining
    print("\n" + "="*60)
    print(f"STAGE 2: Testing authenticated download...")
    print("="*60)
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"\nUsing Chrome profile: {profile_path}")
    else:
        print("\nNo Chrome profile found. Browser will open without saved logins.")
    
    # Test with first 3 remaining papers
    test_remaining = remaining_dois[:3]
    print(f"\nTesting authenticated download with {len(test_remaining)} papers...")
    
    auth_dir = Path("test_authenticated_pdfs")
    
    try:
        auth_downloader = AuthenticatedPDFDownloader(
            output_dir=str(auth_dir),
            chrome_profile_path=profile_path,
            headless=False  # Show browser
        )
        
        auth_results = auth_downloader.download_batch(
            test_remaining,
            delay_between=2,
            titles={doi: doi_to_title[doi] for doi in test_remaining}
        )
        
        print(f"\nAuthenticated results: {len(auth_results)}/{len(test_remaining)} downloaded")
        
    except Exception as e:
        print(f"\nError during authenticated download: {e}")
        auth_results = {}
    
    # Summary
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)
    
    total_tested = len(test_dois)
    total_downloaded = len(open_access_results) + len(auth_results)
    
    print(f"\nTotal tested: {total_tested} papers")
    print(f"Successfully downloaded: {total_downloaded}")
    print(f"  - Open access: {len(open_access_results)}")
    print(f"  - Via authentication: {len(auth_results)}")
    print(f"  - Failed: {total_tested - total_downloaded}")
    
    # Show what we got
    all_results = {**open_access_results, **auth_results}
    if all_results:
        print("\nDownloaded papers:")
        for doi, path in list(all_results.items())[:5]:
            title = doi_to_title.get(doi, "Unknown")[:60]
            print(f"  ✓ {title}...")
            print(f"    → {path.name}")
    
    print(f"\nPDFs saved in:")
    if open_access_dir.exists():
        print(f"  - {open_access_dir}/")
    if auth_dir.exists():
        print(f"  - {auth_dir}/")
    
    print("\nTo download ALL papers, use:")
    print(f"  python download_all_pdfs.py {bibtex_file}")


if __name__ == "__main__":
    main()