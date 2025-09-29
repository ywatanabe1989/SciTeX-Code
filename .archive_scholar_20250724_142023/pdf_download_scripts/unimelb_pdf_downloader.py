#!/usr/bin/env python3
"""
UniMelb authenticated PDF downloader using Selenium
Simplified version that downloads PDFs directly without Zotero
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import shutil
import tempfile


class UniMelbPDFDownloader:
    def __init__(self, output_dir="./unimelb_pdfs"):
        # Use EZProxy login directly - this gives access to publishers
        self.ezproxy_login_url = "https://ezproxy.lib.unimelb.edu.au/login"
        self.ezproxy_base = "https://ezproxy.lib.unimelb.edu.au/login?url="
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        self.download_dir = None
        
    def setup_driver(self, profile_path=None):
        """Setup Chrome with download preferences"""
        # Create temp download directory
        self.download_dir = tempfile.mkdtemp(prefix="unimelb_pdfs_")
        
        options = Options()
        if profile_path:
            options.add_argument(f"user-data-dir={profile_path}")
        
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
        
    def authenticate_unimelb(self, username=None, password=None):
        """Login to UniMelb library system"""
        print("🔐 Authenticating with UniMelb EZProxy...")
        
        # Go to EZProxy login
        self.driver.get(self.ezproxy_login_url)
        time.sleep(2)
        
        if username and password:
            try:
                # Try automated login
                user_field = self.driver.find_element(By.NAME, "code")
                pass_field = self.driver.find_element(By.NAME, "pin")
                
                user_field.send_keys(username)
                pass_field.send_keys(password)
                
                # Submit form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                submit_btn.click()
                
                time.sleep(3)
                print("✓ Automated login attempted")
            except Exception as e:
                print(f"⚠ Automated login failed: {e}")
        else:
            print("\n👤 Please login manually in the browser window:")
            print("   1. Enter your student ID/email")
            print("   2. Enter your PIN/password")
            print("   3. Complete any 2FA if required")
            input("\nPress Enter when login is complete...")
        
        # Verify we're logged in
        current_url = self.driver.current_url
        print(f"Current URL after login: {current_url}")
        
        # Check for successful login indicators
        # EZProxy shows menu or redirects after successful login
        if "ezproxy.lib.unimelb.edu.au/menu" in current_url.lower():
            print("✓ Authentication successful - EZProxy menu reached")
            return True
        elif "ezproxy.lib.unimelb.edu.au" in current_url.lower() and "login" not in current_url.lower():
            print("✓ Authentication successful")
            return True
        elif "error" in current_url.lower():
            print("❌ Authentication failed - login error")
            return False
        else:
            # Assume success if we're past the login
            print("✓ Authentication appears successful")
            return True
    
    def download_doi(self, doi, title=None):
        """Download a single DOI through EZProxy"""
        filename = (title or doi).replace('/', '_').replace(':', '_')[:80] + '.pdf'
        filepath = self.output_dir / filename
        
        if filepath.exists():
            print(f"  → Already exists: {filename}")
            return filepath
        
        # Clear download directory
        for f in Path(self.download_dir).glob("*"):
            f.unlink()
        
        # Try EZProxy URL first
        ezproxy_url = f"{self.ezproxy_base}https://doi.org/{doi}"
        print(f"  → Accessing via EZProxy: {doi}")
        
        try:
            self.driver.get(ezproxy_url)
            time.sleep(3)  # Wait for redirects
            
            # Look for PDF download button
            pdf_found = self._find_and_click_pdf()
            
            if pdf_found:
                # Wait for download
                downloaded = self._wait_for_download()
                if downloaded:
                    shutil.move(str(downloaded), str(filepath))
                    print(f"  ✓ Downloaded: {filename}")
                    return filepath
            
            print(f"  ✗ No PDF found for {doi}")
            return None
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def _find_and_click_pdf(self):
        """Find and click PDF download button"""
        # Common PDF download selectors
        selectors = [
            "a[href*='.pdf']",
            "a[href*='/pdf/']",
            "button:contains('PDF')",
            ".pdf-download",
            "a[data-track-action='download pdf']",
            ".article-tools a[href*='pdf']",
            "a.download-pdf",
            "a:contains('Download PDF')",
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
                    elements[0].click()
                    time.sleep(2)
                    return True
            except:
                continue
        
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
            self.setup_driver()
        
        # First authenticate
        if not self.authenticate_unimelb():
            print("Authentication failed, aborting")
            return []
        
        results = []
        titles = titles or {}
        
        print(f"\nDownloading {len(doi_list)} papers...")
        for i, doi in enumerate(doi_list, 1):
            print(f"\n[{i}/{len(doi_list)}] {doi}")
            
            title = titles.get(doi)
            path = self.download_doi(doi, title)
            
            if path:
                results.append((doi, path))
            
            # Rate limiting
            if i < len(doi_list):
                time.sleep(3)
        
        return results
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if self.download_dir and os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
    
    def __del__(self):
        self.cleanup()


# Simple usage function
def download_unimelb_pdfs(dois, output_dir="./unimelb_pdfs"):
    """
    Download PDFs using UniMelb authentication
    
    Args:
        dois: List of DOI strings
        output_dir: Where to save PDFs
    
    Returns:
        List of (doi, filepath) tuples for successful downloads
    """
    downloader = UniMelbPDFDownloader(output_dir)
    
    try:
        # Find Chrome profile
        from pathlib import Path
        import platform
        
        home = Path.home()
        if platform.system() == "Linux":
            profile_path = home / ".config" / "google-chrome"
            if profile_path.exists():
                downloader.setup_driver(str(profile_path))
            else:
                downloader.setup_driver()
        else:
            downloader.setup_driver()
        
        # Download PDFs
        results = downloader.download_batch(dois)
        
        print(f"\n{'='*60}")
        print(f"Downloaded {len(results)}/{len(dois)} PDFs")
        print(f"Saved to: {output_dir}")
        
        return results
        
    finally:
        downloader.cleanup()


if __name__ == "__main__":
    # Test with some DOIs
    test_dois = [
        "10.1038/s41586-024-07992-y",
        "10.1016/j.cell.2024.01.001",
        "10.1126/science.abcd1234",
    ]
    
    results = download_unimelb_pdfs(test_dois)
    
    print("\nSuccessfully downloaded:")
    for doi, path in results:
        print(f"  {doi} -> {path.name}")