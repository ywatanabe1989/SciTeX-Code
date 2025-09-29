#!/usr/bin/env python3
"""
Enhanced PDF downloader that opens multiple tabs and handles login with retry.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.scitex.scholar.authenticated_pdf_downloader import AuthenticatedPDFDownloader, find_chrome_profile
from scitex.io import load

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TabBasedPDFDownloader(AuthenticatedPDFDownloader):
    """Enhanced downloader that manages multiple tabs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doi_to_tab = {}  # Map DOI to tab handle
        self.login_checked = False
    
    def open_dois_in_tabs(self, dois: List[str], batch_size: int = 5):
        """
        Open multiple DOIs in separate tabs.
        
        Args:
            dois: List of DOIs to open
            batch_size: Number of tabs to open at once
        """
        print(f"\nOpening {len(dois)} papers in tabs (batch size: {batch_size})...")
        
        # Setup driver if needed
        if not self.driver:
            self._setup_driver()
        
        # Process in batches
        for i in range(0, len(dois), batch_size):
            batch = dois[i:i+batch_size]
            print(f"\nBatch {i//batch_size + 1}: Opening {len(batch)} tabs...")
            
            for j, doi in enumerate(batch):
                doi_url = f"https://doi.org/{doi}"
                
                if j == 0 and i == 0:
                    # First DOI - navigate in current tab
                    self.driver.get(doi_url)
                    self.doi_to_tab[doi] = self.driver.current_window_handle
                else:
                    # Open new tab
                    self.driver.execute_script("window.open('');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.get(doi_url)
                    self.doi_to_tab[doi] = self.driver.current_window_handle
                
                time.sleep(1)  # Small delay between tabs
            
            # Check for login on first batch
            if i == 0 and not self.login_checked:
                time.sleep(3)  # Let redirects happen
                if self._check_and_handle_login():
                    # Refresh all tabs after login
                    print("\nRefreshing tabs after login...")
                    for handle in self.driver.window_handles:
                        self.driver.switch_to.window(handle)
                        self.driver.refresh()
                        time.sleep(0.5)
            
            if i + batch_size < len(dois):
                print(f"\nWaiting before next batch...")
                time.sleep(2)
    
    def _check_and_handle_login(self) -> bool:
        """Check if login is needed and handle it."""
        # Check each tab for login pages
        login_needed = False
        
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            current_url = self.driver.current_url
            
            if any(login_indicator in current_url.lower() for login_indicator in 
                   ['login', 'sso', 'auth', 'signin', 'ezproxy', 'shibboleth']):
                login_needed = True
                break
        
        if login_needed:
            print("\n" + "="*60)
            print("⚠️  LOGIN REQUIRED!")
            print("="*60)
            print("\nPlease complete the login in any of the browser tabs.")
            print("The script will detect when you're logged in and continue.")
            
            # Wait for login completion
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            while time.time() - start_time < timeout:
                # Check if we're still on login page
                all_logged_in = True
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    current_url = self.driver.current_url
                    if any(login_indicator in current_url.lower() for login_indicator in 
                           ['login', 'sso', 'auth', 'signin']):
                        all_logged_in = False
                        break
                
                if all_logged_in:
                    print("\n✓ Login successful! Continuing...")
                    self.login_checked = True
                    time.sleep(2)
                    return True
                
                time.sleep(2)
            
            print("\n⚠️  Login timeout. Some papers may not download.")
        
        self.login_checked = True
        return login_needed
    
    def download_from_tab(self, doi: str, filename: Optional[str] = None) -> Optional[Path]:
        """Download PDF from an already open tab."""
        if doi not in self.doi_to_tab:
            return self.download_from_doi(doi, filename)
        
        # Switch to the tab
        try:
            self.driver.switch_to.window(self.doi_to_tab[doi])
        except:
            # Tab might be closed, try normal download
            return self.download_from_doi(doi, filename)
        
        if not filename:
            filename = doi.replace('/', '_').replace(':', '_') + '.pdf'
        
        filepath = self.output_dir / filename
        
        # Check if already exists
        if filepath.exists():
            logger.info(f"Already exists: {filename}")
            return filepath
        
        # Clear download directory
        for f in Path(self.download_dir).glob("*"):
            f.unlink()
        
        # Try download methods
        current_url = self.driver.current_url
        
        # Check if we need to retry due to login
        if any(login_indicator in current_url.lower() for login_indicator in 
               ['login', 'sso', 'auth', 'signin']):
            print(f"\n⚠️  Login page detected for {doi}")
            print("Please login in this tab, then press Enter...")
            input()
            self.driver.refresh()
            time.sleep(3)
        
        # Try download
        pdf_downloaded = self._click_pdf_download()
        
        if pdf_downloaded:
            downloaded_file = self._wait_for_download()
            if downloaded_file:
                # Move to final location
                import shutil
                shutil.move(str(downloaded_file), str(filepath))
                return filepath
        
        # Try other methods
        pdf_url = self._find_pdf_url()
        if pdf_url:
            self.driver.get(pdf_url)
            downloaded_file = self._wait_for_download()
            if downloaded_file:
                import shutil
                shutil.move(str(downloaded_file), str(filepath))
                return filepath
        
        return None
    
    def download_batch_with_tabs(
        self, 
        dois: List[str], 
        titles: Optional[Dict[str, str]] = None,
        batch_size: int = 5
    ) -> Dict[str, Path]:
        """Download PDFs using tab-based approach."""
        results = {}
        titles = titles or {}
        
        # Open tabs first
        self.open_dois_in_tabs(dois, batch_size)
        
        print(f"\n{'='*60}")
        print("Starting downloads from open tabs...")
        print(f"{'='*60}\n")
        
        # Download from each tab
        for i, doi in enumerate(dois, 1):
            print(f"[{i}/{len(dois)}] Downloading: {doi}")
            
            # Generate filename
            title = titles.get(doi)
            if title:
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
                filename = safe_title[:80].strip().replace(' ', '_') + '.pdf'
            else:
                filename = None
            
            # Download
            path = self.download_from_tab(doi, filename)
            
            if path:
                results[doi] = path
                print(f"  ✓ Success! Saved as: {path.name}")
                self.download_log.append({
                    'doi': doi,
                    'filename': path.name,
                    'status': 'success'
                })
            else:
                print(f"  ✗ Failed to download")
                
                # Offer retry
                retry = input("  Retry this paper? (y/n): ").lower()
                if retry == 'y':
                    # Switch to tab and refresh
                    if doi in self.doi_to_tab:
                        self.driver.switch_to.window(self.doi_to_tab[doi])
                        self.driver.refresh()
                        time.sleep(3)
                    
                    path = self.download_from_tab(doi, filename)
                    if path:
                        results[doi] = path
                        print(f"  ✓ Success on retry!")
                    else:
                        print(f"  ✗ Still failed")
                
                self.download_log.append({
                    'doi': doi,
                    'filename': filename or f"{doi.replace('/', '_')}.pdf",
                    'status': 'failed'
                })
        
        # Save log
        import json
        log_path = self.output_dir / "tab_download_log.json"
        with open(log_path, 'w') as f:
            json.dump(self.download_log, f, indent=2)
        
        return results


def main():
    """Main function for tab-based downloads."""
    
    # Get BibTeX file
    bibtex_file = "./process_remaining_semantic_out/papers_enhanced_final_v2.bib"
    
    print("TAB-BASED PDF DOWNLOADER")
    print("="*60)
    print("\nThis will:")
    print("1. Open multiple papers in Chrome tabs")
    print("2. Detect if login is needed")
    print("3. Let you login once for all tabs")
    print("4. Download PDFs with retry option")
    
    # Load entries
    entries = load(bibtex_file)
    
    # Get DOIs
    all_papers = []
    for entry in entries:
        fields = entry.get('fields', {})
        doi = fields.get('doi')
        if doi:
            all_papers.append({
                'doi': doi,
                'title': fields.get('title', 'Unknown'),
                'journal': fields.get('journal', 'Unknown'),
                'year': fields.get('year')
            })
    
    print(f"\nFound {len(all_papers)} papers with DOIs")
    
    # Select papers to download
    print("\nOptions:")
    print("1. Download specific paywalled papers (recommended for testing)")
    print("2. Download all papers")
    print("3. Download custom range")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        # Specific paywalled papers
        target_dois = [
            "10.1016/j.neubiorev.2020.07.005",  # Neuroscience & Biobehavioral Reviews
            "10.1016/j.neuroimage.2021.118403", # NeuroImage
            "10.1016/j.neuroimage.2021.118573", # NeuroImage
            "10.1002/hbm.26190",                # Human Brain Mapping
            "10.3390/e23081070",                # Entropy (might be open)
        ]
        papers = [p for p in all_papers if p['doi'] in target_dois]
        
    elif choice == '2':
        papers = all_papers
        
    else:
        start = int(input("Start index (1-based): ")) - 1
        end = int(input("End index (1-based): "))
        papers = all_papers[start:end]
    
    if not papers:
        print("No papers selected.")
        return
    
    print(f"\nWill download {len(papers)} papers:")
    for p in papers[:5]:
        print(f"  • {p['title'][:60]}...")
    if len(papers) > 5:
        print(f"  ... and {len(papers) - 5} more")
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"\n✓ Found Chrome profile: {profile_path}")
    
    input("\nPress Enter to start...")
    
    # Create downloader
    downloader = TabBasedPDFDownloader(
        output_dir="tab_downloaded_pdfs",
        chrome_profile_path=profile_path,
        headless=False
    )
    
    # Download
    dois = [p['doi'] for p in papers]
    doi_to_title = {p['doi']: p['title'] for p in papers}
    
    results = downloader.download_batch_with_tabs(
        dois,
        titles=doi_to_title,
        batch_size=5  # Open 5 tabs at a time
    )
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("="*60)
    print(f"Successfully downloaded: {len(results)}/{len(papers)} PDFs")
    print(f"PDFs saved to: tab_downloaded_pdfs/")
    
    # Show results
    if results:
        print("\nSuccessful downloads:")
        for doi, path in list(results.items())[:10]:
            p = next(p for p in papers if p['doi'] == doi)
            print(f"  ✓ {p['title'][:50]}... → {path.name}")
    
    # Cleanup
    del downloader


if __name__ == "__main__":
    main()