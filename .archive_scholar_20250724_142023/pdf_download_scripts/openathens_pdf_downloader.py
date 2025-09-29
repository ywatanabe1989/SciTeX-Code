#!/usr/bin/env python3
"""
UniMelb OpenAthens authenticated PDF downloader
Uses University of Melbourne's OpenAthens SSO for journal access
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


class OpenAthensPDFDownloader:
    def __init__(self, output_dir="./openathens_pdfs"):
        # OpenAthens login URL for UniMelb
        self.openathens_login = "https://login.openathens.net/auth/unimelb.edu.au"
        self.unimelb_sso = "https://okta.unimelb.edu.au"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        self.download_dir = None
        self.authenticated = False
        
    def setup_driver(self, profile_path=None):
        """Setup Chrome with download preferences"""
        # Create temp download directory
        self.download_dir = tempfile.mkdtemp(prefix="openathens_pdfs_")
        
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
        
    def authenticate_openathens(self, username=None, password=None):
        """Login through OpenAthens/UniMelb SSO"""
        if self.authenticated:
            return True
            
        print("🔐 Authenticating with UniMelb OpenAthens...")
        
        # First, try accessing a known publisher through OpenAthens
        # This will trigger the login flow if not authenticated
        test_url = "https://www-nature-com.openathens-sp.com/nature"
        
        print("  → Testing OpenAthens access...")
        self.driver.get(test_url)
        time.sleep(3)
        
        current_url = self.driver.current_url
        
        # Check if we need to login
        if "login.openathens.net" in current_url or "okta.unimelb.edu.au" in current_url:
            print("  → Login required...")
            
            if username and password:
                # Try automated login
                try:
                    # Wait for username field
                    username_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "username"))
                    )
                    username_field.send_keys(username)
                    
                    # Click next/continue
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    next_button.click()
                    
                    # Wait for password field
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "password"))
                    )
                    password_field.send_keys(password)
                    
                    # Submit
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    submit_button.click()
                    
                    print("  → Automated login submitted")
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"  ⚠ Automated login failed: {e}")
                    print("\n👤 Please complete login manually in the browser window...")
                    input("Press Enter when login is complete...")
            else:
                print("\n👤 Please login manually in the browser window:")
                print("   1. Enter your UniMelb username/email")
                print("   2. Enter your password")
                print("   3. Complete any 2FA if required")
                input("\nPress Enter when login is complete...")
        
        # Verify authentication
        time.sleep(2)
        current_url = self.driver.current_url
        
        if "openathens-sp.com" in current_url or any(pub in current_url for pub in ["nature.com", "sciencedirect.com", "wiley.com"]):
            print("✓ OpenAthens authentication successful!")
            self.authenticated = True
            return True
        else:
            print("❌ Authentication may have failed")
            return False
    
    def download_doi_openathens(self, doi, title=None):
        """Download a DOI using OpenAthens authentication"""
        filename = (title or doi).replace('/', '_').replace(':', '_')[:80] + '.pdf'
        filepath = self.output_dir / filename
        
        if filepath.exists():
            print(f"  → Already exists: {filename}")
            return filepath
        
        # Clear download directory
        for f in Path(self.download_dir).glob("*"):
            f.unlink()
        
        # For OpenAthens, we need to construct the proxied URL
        # Different publishers have different OpenAthens domains
        doi_url = f"https://doi.org/{doi}"
        
        print(f"  → Resolving DOI: {doi}")
        
        try:
            # First go to DOI to see where it redirects
            self.driver.get(doi_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            domain = current_url.split('/')[2]
            
            # Convert to OpenAthens URL if not already
            if "openathens-sp.com" not in current_url:
                # Map common publishers to their OpenAthens domains
                openathens_domains = {
                    "nature.com": "www-nature-com.openathens-sp.com",
                    "sciencedirect.com": "www-sciencedirect-com.openathens-sp.com",
                    "onlinelibrary.wiley.com": "onlinelibrary-wiley-com.openathens-sp.com",
                    "link.springer.com": "link-springer-com.openathens-sp.com",
                    "ieeexplore.ieee.org": "ieeexplore-ieee-org.openathens-sp.com",
                    "journals.sagepub.com": "journals-sagepub-com.openathens-sp.com",
                    "academic.oup.com": "academic-oup-com.openathens-sp.com",
                    "www.tandfonline.com": "www-tandfonline-com.openathens-sp.com"
                }
                
                # Check if we can proxy this domain
                for original, proxied in openathens_domains.items():
                    if original in domain:
                        # Construct OpenAthens URL
                        openathens_url = current_url.replace(original, proxied)
                        print(f"  → Using OpenAthens proxy: {proxied}")
                        self.driver.get(openathens_url)
                        time.sleep(3)
                        break
            
            print(f"  → On publisher page: {self.driver.current_url[:60]}...")
            
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
                
                if elements and elements[0].is_displayed():
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
                if link.is_displayed():
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
        
        # Authenticate first
        if not self.authenticate_openathens():
            print("Authentication failed, aborting")
            return []
        
        results = []
        titles = titles or {}
        
        print(f"\nDownloading {len(doi_list)} papers via OpenAthens...")
        
        for i, doi in enumerate(doi_list, 1):
            print(f"\n[{i}/{len(doi_list)}] DOI: {doi}")
            
            title = titles.get(doi)
            path = self.download_doi_openathens(doi, title)
            
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
    # Test DOIs - mix of publishers
    test_dois = [
        "10.1038/s41586-020-2649-2",     # Nature
        "10.1016/j.cell.2021.02.029",    # Cell/Elsevier
        "10.1002/adma.202001537",        # Wiley
        "10.1371/journal.pone.0261631",  # PLOS (open access)
    ]
    
    print("UniMelb OpenAthens PDF Download Test")
    print("=" * 60)
    print("\nThis will:")
    print("1. Open Chrome and test OpenAthens authentication")
    print("2. Prompt for UniMelb login if needed")
    print("3. Download PDFs through OpenAthens proxy")
    print("\nNote: You need to be connected to UniMelb network or VPN")
    
    downloader = OpenAthensPDFDownloader(output_dir="./openathens_test_pdfs")
    
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