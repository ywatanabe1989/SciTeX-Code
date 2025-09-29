#!/usr/bin/env python3
"""
Phase 2: Download PDFs using saved authentication from Phase 1.
No login required - uses cookies from previous session.
"""

import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader, find_chrome_profile
from scitex.io import load


class CookieBasedPDFDownloader(AuthenticatedPDFDownloader):
    """PDF downloader that relies on saved cookies."""
    
    def download_with_saved_auth(self, doi: str, filename: Optional[str] = None) -> Optional[Path]:
        """Download using saved authentication - no login handling."""
        if not filename:
            filename = doi.replace('/', '_').replace(':', '_') + '.pdf'
        
        filepath = self.output_dir / filename
        
        # Check if already exists
        if filepath.exists():
            print(f"  → Already exists: {filename}")
            return filepath
        
        # Setup driver if needed
        if not self.driver:
            self._setup_driver()
        
        try:
            # Clear download directory
            for f in Path(self.download_dir).glob("*"):
                f.unlink()
            
            # Navigate to DOI
            doi_url = f"https://doi.org/{doi}"
            self.driver.get(doi_url)
            time.sleep(3)  # Let page load
            
            # Check if we hit a login page (shouldn't happen with saved cookies)
            current_url = self.driver.current_url
            if any(indicator in current_url.lower() for indicator in ['login', 'sso', 'auth']):
                print(f"  ⚠ Login required - cookies may have expired")
                return None
            
            # Try to download
            print(f"  → Page loaded: {self.driver.title[:50]}...")
            
            # Try clicking PDF button
            pdf_clicked = self._click_pdf_download()
            if pdf_clicked:
                print(f"  → Clicked PDF download button")
                downloaded = self._wait_for_download(timeout=20)
                if downloaded:
                    import shutil
                    shutil.move(str(downloaded), str(filepath))
                    return filepath
            
            # Try finding PDF URL
            pdf_url = self._find_pdf_url()
            if pdf_url:
                print(f"  → Found PDF URL, downloading...")
                self.driver.get(pdf_url)
                downloaded = self._wait_for_download(timeout=20)
                if downloaded:
                    import shutil
                    shutil.move(str(downloaded), str(filepath))
                    return filepath
            
            print(f"  ✗ Could not find PDF download option")
            return None
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None


def main():
    """Phase 2: Download PDFs with saved authentication."""
    
    print("PHASE 2: PDF DOWNLOAD WITH SAVED AUTHENTICATION")
    print("="*60)
    
    # Check for Chrome profile
    profile_path = find_chrome_profile()
    if not profile_path:
        print("\n⚠ No Chrome profile found!")
        print("Please run phase1_login_setup.py first to save your logins.")
        return
    
    print(f"\n✓ Using saved authentication from: {profile_path}")
    
    # Load BibTeX
    bibtex_file = "./process_remaining_semantic_out/papers_enhanced_final_v2.bib"
    if not Path(bibtex_file).exists():
        print(f"\n⚠ BibTeX file not found: {bibtex_file}")
        return
        
    entries = load(bibtex_file)
    
    # Get all papers with DOIs
    papers = []
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi:
            papers.append({
                'doi': doi,
                'title': fields.get('title', 'Unknown'),
                'journal': fields.get('journal', 'Unknown'),
                'year': fields.get('year')
            })
    
    print(f"\nFound {len(papers)} papers with DOIs")
    
    # Options for what to download
    print("\nWhat would you like to download?")
    print("1. Test with 5 paywalled papers")
    print("2. First 10 papers")
    print("3. All papers")
    print("4. Custom range")
    
    try:
        choice = input("\nChoice (1-4) [default=1]: ").strip() or "1"
    except:
        choice = "1"
    
    if choice == "1":
        # Test papers from different publishers
        test_dois = [
            "10.1016/j.neubiorev.2020.07.005",  # Elsevier
            "10.1002/hbm.26190",                # Wiley
            "10.1038/s41598-019-48870-2",       # Nature (might be open)
            "10.1016/j.neuroimage.2021.118403", # Elsevier
            "10.3389/fnins.2019.00573",         # Frontiers (open)
        ]
        selected_papers = [p for p in papers if p['doi'] in test_dois]
        
    elif choice == "2":
        selected_papers = papers[:10]
        
    elif choice == "3":
        selected_papers = papers
        
    else:
        try:
            start = int(input("Start index (1-based): ")) - 1
            end = int(input("End index (1-based): "))
            selected_papers = papers[start:end]
        except:
            print("Invalid input, using first 5 papers")
            selected_papers = papers[:5]
    
    if not selected_papers:
        print("No papers selected.")
        return
    
    print(f"\nWill download {len(selected_papers)} papers:")
    for i, p in enumerate(selected_papers[:5], 1):
        print(f"{i}. {p['title'][:50]}... ({p['journal']})")
    if len(selected_papers) > 5:
        print(f"... and {len(selected_papers) - 5} more")
    
    print("\nStarting downloads in 3 seconds...")
    time.sleep(3)
    
    # Create downloader
    downloader = CookieBasedPDFDownloader(
        output_dir="authenticated_pdfs_batch",
        chrome_profile_path=profile_path,
        headless=False  # Show browser so you can see what's happening
    )
    
    # Download each paper
    results = []
    print("\n" + "="*60)
    print("Downloading PDFs...")
    print("="*60 + "\n")
    
    for i, paper in enumerate(selected_papers, 1):
        doi = paper['doi']
        title = paper['title']
        
        print(f"[{i}/{len(selected_papers)}] {title[:50]}...")
        print(f"  DOI: {doi}")
        
        # Clean filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        filename = safe_title[:80].strip().replace(' ', '_') + '.pdf'
        
        # Download
        path = downloader.download_with_saved_auth(doi, filename)
        
        if path:
            print(f"  ✓ Success: {path.name}\n")
            results.append((paper, path))
        else:
            print(f"  ✗ Failed\n")
        
        # Small delay between downloads
        if i < len(selected_papers):
            time.sleep(2)
    
    # Cleanup
    del downloader
    
    # Summary
    print("="*60)
    print("DOWNLOAD COMPLETE")
    print("="*60)
    
    print(f"\nSuccessfully downloaded: {len(results)}/{len(selected_papers)} PDFs")
    print(f"PDFs saved to: authenticated_pdfs_batch/")
    
    if results:
        print("\n✓ Downloaded papers:")
        for paper, path in results[:10]:
            print(f"  • {paper['title'][:50]}...")
            print(f"    → {path.name}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")
    
    failed = len(selected_papers) - len(results)
    if failed > 0:
        print(f"\n✗ Failed to download {failed} papers")
        print("\nPossible reasons:")
        print("- Authentication cookies expired (run phase1_login_setup.py again)")
        print("- Paper not accessible with your subscription")
        print("- Publisher website changed")


if __name__ == "__main__":
    main()