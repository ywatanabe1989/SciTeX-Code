#!/usr/bin/env python3
"""
Download paywalled papers with clear login instructions.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader, find_chrome_profile
from scitex.io import load


def main():
    """Download paywalled papers with authentication."""
    
    # Get BibTeX file
    bibtex_file = "./process_remaining_semantic_out/papers_enhanced_final_v2.bib"
    
    print("AUTHENTICATED PDF DOWNLOADER")
    print("="*60)
    print("\nThis will download paywalled papers using your browser.")
    print("\nBEFORE STARTING:")
    print("1. Open Chrome manually")
    print("2. Go to a journal site (e.g., sciencedirect.com)")
    print("3. Login with your UniMelb account if needed")
    print("4. Make sure you can access papers")
    print("5. Close Chrome")
    print("\nThe script will then use your saved login session.")
    
    input("\nPress Enter when ready...")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Get specific paywalled papers
    paywalled_dois = [
        "10.1016/j.neubiorev.2020.07.005",  # Neuroscience & Biobehavioral Reviews
        "10.3389/fnins.2019.00573",         # Frontiers (should work)
        "10.1016/j.neuroimage.2021.118403", # NeuroImage
        "10.1016/j.neuroimage.2021.118573", # NeuroImage
        "10.1002/hbm.26190",                # Human Brain Mapping
    ]
    
    # Get paper info
    doi_to_info = {}
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi in paywalled_dois:
            doi_to_info[doi] = {
                'title': fields.get('title', 'Unknown'),
                'journal': fields.get('journal', 'Unknown')
            }
    
    print(f"\nWill download {len(paywalled_dois)} specific papers:")
    for doi in paywalled_dois:
        info = doi_to_info.get(doi, {'title': 'Unknown', 'journal': 'Unknown'})
        print(f"\n  • {info['title'][:60]}...")
        print(f"    Journal: {info['journal']}")
        print(f"    DOI: {doi}")
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"\n✓ Found Chrome profile: {profile_path}")
    else:
        print("\n⚠ No Chrome profile found. You'll need to login manually.")
    
    input("\nPress Enter to start downloading...")
    
    # Create downloader
    print("\nOpening Chrome...")
    downloader = AuthenticatedPDFDownloader(
        output_dir="authenticated_pdfs",
        chrome_profile_path=profile_path,
        headless=False  # Show browser
    )
    
    # Download each paper
    results = {}
    for i, doi in enumerate(paywalled_dois, 1):
        print(f"\n[{i}/{len(paywalled_dois)}] Downloading: {doi}")
        
        info = doi_to_info.get(doi, {})
        title = info.get('title', 'Unknown')
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        filename = safe_title[:80].strip().replace(' ', '_') + '.pdf'
        
        try:
            # Navigate and wait
            print("  Navigating to paper...")
            path = downloader.download_from_doi(doi, filename)
            
            if path:
                results[doi] = path
                print(f"  ✓ Success! Saved as: {path.name}")
            else:
                print(f"  ✗ Failed - may need login or not accessible")
                
                # Check if we need login
                current_url = downloader.driver.current_url
                if 'login' in current_url or 'sso' in current_url:
                    print("\n  ⚠ LOGIN REQUIRED!")
                    print("  Please login in the browser window.")
                    input("  Press Enter after logging in...")
                    
                    # Try again
                    print("  Retrying download...")
                    path = downloader.download_from_doi(doi, filename)
                    if path:
                        results[doi] = path
                        print(f"  ✓ Success after login!")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Small delay between papers
        if i < len(paywalled_dois):
            time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print(f"Downloaded: {len(results)}/{len(paywalled_dois)} papers")
    
    if results:
        print("\nSuccessfully downloaded:")
        for doi, path in results.items():
            info = doi_to_info.get(doi, {'title': 'Unknown'})
            print(f"  ✓ {info['title'][:60]}...")
    
    failed = [doi for doi in paywalled_dois if doi not in results]
    if failed:
        print(f"\nFailed to download:")
        for doi in failed:
            info = doi_to_info.get(doi, {'title': 'Unknown'})
            print(f"  ✗ {info['title'][:60]}...")
    
    print(f"\nPDFs saved to: authenticated_pdfs/")


if __name__ == "__main__":
    main()