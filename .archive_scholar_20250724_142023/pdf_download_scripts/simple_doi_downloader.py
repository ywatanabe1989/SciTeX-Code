#!/usr/bin/env python3
"""
Simple DOI to PDF downloader using existing Chrome profile
Relies on saved authentication cookies from previous logins
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import shutil
import tempfile


class SimpleDOIDownloader:
    def __init__(self, output_dir="./doi_pdfs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        self.download_dir = None
        
    def setup_driver(self, profile_path=None):
        """Setup Chrome with download preferences"""
        # Create temp download directory
        self.download_dir = tempfile.mkdtemp(prefix="doi_pdfs_")
        
        options = Options()
        if profile_path:
            options.add_argument(f"user-data-dir={profile_path}")
            print(f"✓ Using Chrome profile: {profile_path}")
        
        # Download settings
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Enable downloads
        params = {"behavior": "allow", "downloadPath": self.download_dir}
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        
    def download_doi(self, doi, title=None):
        """Download a single DOI"""
        filename = (title or doi).replace('/', '_').replace(':', '_')[:80] + '.pdf'
        filepath = self.output_dir / filename
        
        if filepath.exists():
            print(f"  → Already exists: {filename}")
            return filepath
        
        # Clear download directory
        for f in Path(self.download_dir).glob("*"):
            f.unlink()
        
        # Go directly to DOI
        doi_url = f"https://doi.org/{doi}"
        print(f"  → Navigating to: {doi_url}")
        
        try:
            self.driver.get(doi_url)
            time.sleep(3)  # Wait for redirects
            
            current_url = self.driver.current_url
            print(f"  → Redirected to: {current_url[:60]}...")
            
            # Look for PDF download button
            pdf_found = self._find_and_click_pdf()
            
            if pdf_found:
                # Wait for download
                downloaded = self._wait_for_download()
                if downloaded:
                    shutil.move(str(downloaded), str(filepath))
                    print(f"  ✓ Downloaded: {filename}")
                    return filepath
            
            print(f"  ✗ No PDF download option found")
            return None
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def _find_and_click_pdf(self):
        """Find and click PDF download button"""
        # Common PDF download selectors
        selectors = [
            # Generic
            "a[href*='.pdf']",
            "a[href*='/pdf/']",
            "button:contains('PDF')",
            ".pdf-download",
            "a.download-pdf",
            
            # Publisher specific
            "a[data-track-action='download pdf']",  # Nature
            ".c-pdf-download__link",  # Nature
            ".article-tools a[href*='pdf']",  # Science
            ".article-tools__item--pdf a",  # Wiley
            "a.accessbar-utility-link[title*='PDF']",  # Elsevier
            ".PdfLink",  # Elsevier
            "a.c-pdf-download",  # Springer
            ".test-pdf-link",  # Springer
            "a[ng-click*='pdf']",  # IEEE
            ".stats-document-lh-action-downloadPdf_2",  # IEEE
            "a.article-pdf-download",  # PNAS
            ".article-tools a.article-tools__pdf",  # Cell Press
            "a.al-link.pdf",  # Oxford
            "a.show-pdf",  # Taylor & Francis
            "a.UD_ArticlePDF",  # MDPI
            "a.download-files-pdf",  # Frontiers
            "a#downloadPdf"  # PLOS
        ]
        
        for selector in selectors:
            try:
                if ":contains(" in selector:
                    # Handle text-based selectors
                    text = selector.split("'")[1]
                    elements = self.driver.find_elements(
                        By.XPATH, f"//*[contains(text(), '{text}')]"
                    )
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"  → Found PDF button: {selector}")
                    elements[0].click()
                    time.sleep(2)
                    return True
            except:
                continue
        
        # Also try looking for PDF links by text
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.lower()
                if any(term in link_text for term in ["download pdf", "full text pdf", "view pdf", "get pdf"]):
                    print(f"  → Found PDF link: {link.text}")
                    link.click()
                    time.sleep(2)
                    return True
        except:
            pass
        
        return False
    
    def _wait_for_download(self, timeout=30):
        """Wait for PDF download to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            files = list(Path(self.download_dir).glob("*.pdf"))
            temp_files = list(Path(self.download_dir).glob("*.crdownload"))
            
            if files and not temp_files:
                return files[0]
            
            time.sleep(0.5)
        
        return None
    
    def download_batch(self, doi_list, titles=None):
        """Download multiple DOIs"""
        if not self.driver:
            # Find Chrome profile
            from pathlib import Path
            import platform
            
            home = Path.home()
            profile_path = None
            
            if platform.system() == "Linux":
                chrome_profile = home / ".config" / "google-chrome"
                if chrome_profile.exists():
                    profile_path = str(chrome_profile)
            
            self.setup_driver(profile_path)
        
        results = []
        titles = titles or {}
        
        print(f"\nAttempting to download {len(doi_list)} papers...")
        print("Note: This relies on your existing browser authentication\n")
        
        for i, doi in enumerate(doi_list, 1):
            print(f"[{i}/{len(doi_list)}] DOI: {doi}")
            
            title = titles.get(doi)
            path = self.download_doi(doi, title)
            
            if path:
                results.append((doi, path))
            
            # Rate limiting
            if i < len(doi_list):
                time.sleep(2)
        
        return results
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if self.download_dir and os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
    
    def __del__(self):
        self.cleanup()


# Test function
if __name__ == "__main__":
    # Test DOIs
    test_dois = [
        "10.1371/journal.pone.0261631",  # PLOS ONE - open access
        "10.3389/fnins.2019.00573",      # Frontiers - open access
        "10.1038/s41586-020-2649-2",     # Nature - might need auth
    ]
    
    downloader = SimpleDOIDownloader(output_dir="./test_simple_pdfs")
    
    try:
        results = downloader.download_batch(test_dois)
        
        print(f"\n{'='*60}")
        print(f"Downloaded {len(results)}/{len(test_dois)} PDFs")
        
        if results:
            print("\nSuccessful downloads:")
            for doi, path in results:
                print(f"  ✓ {doi}")
                print(f"    → {path.name}")
        
    finally:
        downloader.cleanup()