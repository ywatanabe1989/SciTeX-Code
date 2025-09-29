#!/usr/bin/env python3
"""
Download PDFs using UniMelb authentication.
This script handles the university login flow automatically.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader
from scitex.io import load

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniMelbPDFDownloader(AuthenticatedPDFDownloader):
    """Extended downloader with UniMelb SSO support."""
    
    def _handle_unimelb_login(self):
        """Handle UniMelb SSO login if redirected to login page."""
        current_url = self.driver.current_url
        
        # Check if we're on UniMelb login page
        if 'login.unimelb.edu.au' in current_url or 'sso' in current_url:
            logger.info("Detected UniMelb login page")
            
            # Wait for user to complete login
            print("\n" + "="*60)
            print("UNIMELB LOGIN REQUIRED")
            print("="*60)
            print("Please complete the login in the browser window.")
            print("The script will continue automatically after login.")
            print("Waiting for login completion...")
            
            # Wait until we're redirected away from login page
            timeout = 120  # 2 minutes to login
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                current = self.driver.current_url
                if 'login.unimelb.edu.au' not in current and 'sso' not in current:
                    logger.info("Login completed, continuing...")
                    time.sleep(2)  # Let page stabilize
                    return True
                time.sleep(1)
            
            logger.warning("Login timeout")
            return False
        
        return True
    
    def _try_download_methods(self, doi: str, doi_url: str):
        """Override to handle UniMelb login."""
        # Navigate to DOI
        logger.info(f"Navigating to: {doi_url}")
        self.driver.get(doi_url)
        time.sleep(3)
        
        # Check for UniMelb login
        if not self._handle_unimelb_login():
            return None
        
        # Continue with normal download methods
        return super()._try_download_methods(doi, doi_url)


def main():
    """Main function for UniMelb PDF downloads."""
    
    # Get BibTeX file
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
    else:
        print("Usage: python download_with_unimelb.py <bibtex_file>")
        print("\nThis script will:")
        print("1. Open Chrome with your saved logins")
        print("2. Navigate to each paper's DOI")
        print("3. Handle UniMelb SSO login if needed")
        print("4. Download PDFs you have access to")
        return
    
    print(f"Loading BibTeX file: {bibtex_file}")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Extract DOIs
    papers = []
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi:
            papers.append({
                'doi': doi,
                'title': fields.get('title', 'Unknown'),
                'year': fields.get('year'),
                'journal': fields.get('journal')
            })
    
    print(f"\nFound {len(papers)} papers with DOIs")
    
    if not papers:
        print("No papers with DOIs found.")
        return
    
    # Show what we'll download
    print("\nFirst few papers:")
    for p in papers[:5]:
        print(f"  - {p['title'][:60]}...")
    if len(papers) > 5:
        print(f"  ... and {len(papers) - 5} more")
    
    print("\n" + "="*60)
    print("IMPORTANT:")
    print("- Chrome will open and navigate to each paper")
    print("- If prompted, login with your UniMelb credentials")
    print("- The script will handle the rest automatically")
    print("="*60)
    
    response = input("\nReady to start? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Find Chrome profile
    from src.scitex.scholar.authenticated_pdf_downloader import find_chrome_profile
    profile_path = find_chrome_profile()
    
    if profile_path:
        print(f"\nUsing Chrome profile: {profile_path}")
        print("This should have your saved UniMelb login")
    else:
        print("\nNo Chrome profile found.")
        print("You'll need to login manually when prompted.")
    
    # Create downloader
    downloader = UniMelbPDFDownloader(
        output_dir="unimelb_pdfs",
        chrome_profile_path=profile_path,
        headless=False  # Must show browser for login
    )
    
    # Download PDFs
    dois = [p['doi'] for p in papers]
    doi_to_title = {p['doi']: p['title'] for p in papers}
    
    print(f"\nStarting downloads...")
    results = downloader.download_batch(
        dois,
        delay_between=2,  # Shorter delay since we handle login
        titles=doi_to_title
    )
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"Successfully downloaded: {len(results)}/{len(papers)} PDFs")
    print(f"PDFs saved to: unimelb_pdfs/")
    
    # Show what we got
    if results:
        print("\nDownloaded papers:")
        for doi, path in list(results.items())[:10]:
            print(f"  ✓ {path.name}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")
    
    # Show failures
    failed = [p for p in papers if p['doi'] not in results]
    if failed:
        print(f"\nFailed to download {len(failed)} papers:")
        for p in failed[:5]:
            print(f"  ✗ {p['title'][:60]}...")
        if len(failed) > 5:
            print(f"  ... and {len(failed) - 5} more")


if __name__ == "__main__":
    main()