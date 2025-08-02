#!/usr/bin/env python3
"""
Direct DOI to PDF downloader
Works with existing browser authentication (no proxy required)
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import tempfile


class DirectDOIDownloader:
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
        
        # Disable images for faster loading (optional)
        # prefs["profile.managed_default_content_settings.images"] = 2
        
        self.driver = webdriver.Chrome(options=options)
        
        # Enable downloads
        params = {"behavior": "allow", "downloadPath": self.download_dir}
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        
    def check_authentication_status(self):
        """Check if we have access by testing a known paywalled paper"""
        print("\n🔍 Checking authentication status...")
        
        # Test with a Nature paper
        test_doi = "10.1038/s41586-020-2649-2"
        test_url = f"https://doi.org/{test_doi}"
        
        self.driver.get(test_url)
        time.sleep(3)
        
        current_url = self.driver.current_url
        page_source = self.driver.page_source.lower()
        
        # Check for access indicators
        if any(indicator in page_source for indicator in ["download pdf", "full text pdf", "view pdf"]):
            print("✓ You appear to have journal access")
            return True
        elif any(indicator in page_source for indicator in ["access through your institution", "get access", "purchase"]):
            print("⚠ Limited access detected - you may need to login to publishers")
            return False
        else:
            print("? Access status unclear - will attempt downloads anyway")
            return None
    
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
            domain = current_url.split('/')[2] if '/' in current_url else ""
            
            print(f"  → Publisher: {domain}")
            
            # Check if we hit a paywall
            page_source = self.driver.page_source.lower()
            if any(paywall in page_source for paywall in ["access through your institution", "get access", "purchase article"]):
                print(f"  ⚠ Paywall detected")
                
                # Try to find institutional login
                if self._try_institutional_login():
                    time.sleep(3)
                    # Retry PDF search after login
                    pass
            
            # Look for PDF download options
            pdf_found = self._find_and_click_pdf()
            
            if pdf_found:
                # Wait for download
                downloaded = self._wait_for_download()
                if downloaded:
                    shutil.move(str(downloaded), str(filepath))
                    print(f"  ✓ Downloaded: {filename}")
                    return filepath
                else:
                    print(f"  ✗ Download did not complete")
            else:
                print(f"  ✗ No PDF download option found")
            
            return None
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def _try_institutional_login(self):
        """Try to find and use institutional login"""
        print("  → Looking for institutional login...")
        
        # Common institutional login selectors
        inst_selectors = [
            "a:contains('institutional')",
            "a:contains('Institution')",
            "button:contains('institutional')",
            "a:contains('Shibboleth')",
            "a:contains('Athens')",
            "a:contains('university')",
            ".institution-login",
            "#institution-login",
        ]
        
        for selector in inst_selectors:
            try:
                if ":contains(" in selector:
                    text = selector.split("'")[1]
                    elements = self.driver.find_elements(
                        By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    )
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"  → Found institutional login option")
                    elements[0].click()
                    time.sleep(2)
                    
                    # You might need to search for University of Melbourne here
                    # For now, just return True to indicate we tried
                    return True
            except:
                continue
        
        return False
    
    def _find_and_click_pdf(self):
        """Find and click PDF download button - comprehensive search"""
        print("  → Searching for PDF download option...")
        
        # Wait a bit for dynamic content to load
        time.sleep(2)
        
        # Try multiple strategies
        strategies = [
            self._try_pdf_by_selector,
            self._try_pdf_by_link_text,
            self._try_pdf_by_href,
            self._try_pdf_by_meta_tag
        ]
        
        for strategy in strategies:
            if strategy():
                return True
        
        return False
    
    def _try_pdf_by_selector(self):
        """Try common PDF button selectors"""
        selectors = [
            # Generic
            ".pdf-download", "a.download-pdf", ".download-pdf-link",
            "#pdf-download", ".pdf-link", "a.pdf",
            
            # Nature
            "a[data-track-action='download pdf']",
            ".c-pdf-download__link",
            "a.c-pdf-download",
            
            # Elsevier/ScienceDirect
            "a.accessbar-utility-link[title*='PDF']",
            ".PdfLink", "a.pdfLink",
            ".download-pdf-popover",
            
            # Wiley
            ".article-tools__item--pdf a",
            "a.pdf-download-btn",
            
            # Springer
            "a.c-pdf-download",
            ".test-pdf-link",
            "a.download-article",
            
            # IEEE
            "a[ng-click*='pdf']",
            ".stats-document-lh-action-downloadPdf_2",
            "xpl-article-details a[href*='pdf']",
            
            # Taylor & Francis
            "a.show-pdf",
            ".download-options a[href*='pdf']",
            
            # SAGE
            ".sage-pdf-link",
            "a[data-item-name='download-PDF']",
            
            # Oxford Academic
            "a.al-link.pdf",
            ".pdf-link",
            
            # MDPI
            "a.UD_ArticlePDF",
            
            # Frontiers
            "a.download-files-pdf",
            
            # PLOS
            "a#downloadPdf",
            
            # Cell Press
            ".article-tools a.article-tools__pdf",
            
            # PNAS
            "a.article-pdf-download"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"  → Found PDF button: {selector}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        element.click()
                        time.sleep(2)
                        return True
            except:
                continue
        
        return False
    
    def _try_pdf_by_link_text(self):
        """Try finding PDF by link text"""
        pdf_texts = [
            "Download PDF", "Full Text PDF", "View PDF", "Get PDF",
            "PDF", "Download", "Full Text", "Download full text",
            "Download article", "Article PDF", "Full article"
        ]
        
        for text in pdf_texts:
            try:
                # Case insensitive partial link text
                links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, text)
                for link in links:
                    if link.is_displayed() and link.is_enabled():
                        href = link.get_attribute("href") or ""
                        if "pdf" in href.lower() or "download" in href.lower():
                            print(f"  → Found PDF link: '{text}'")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(1)
                            link.click()
                            time.sleep(2)
                            return True
            except:
                continue
        
        return False
    
    def _try_pdf_by_href(self):
        """Try finding PDF by href attribute"""
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href") or ""
                if (".pdf" in href.lower() or "/pdf/" in href.lower()) and link.is_displayed():
                    text = link.text or link.get_attribute("title") or ""
                    if any(term in text.lower() for term in ["download", "pdf", "full", "text"]):
                        print(f"  → Found PDF link by href")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(1)
                        link.click()
                        time.sleep(2)
                        return True
        except:
            pass
        
        return False
    
    def _try_pdf_by_meta_tag(self):
        """Try finding PDF URL in meta tags"""
        meta_names = ["citation_pdf_url", "citation_fulltext_url", "DC.Identifier"]
        
        for name in meta_names:
            try:
                meta = self.driver.find_element(By.CSS_SELECTOR, f"meta[name='{name}']")
                content = meta.get_attribute("content")
                if content and (".pdf" in content or "/pdf/" in content):
                    print(f"  → Found PDF URL in meta tag: {name}")
                    self.driver.get(content)
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
            temp_files.extend(list(Path(self.download_dir).glob("*.tmp")))
            temp_files.extend(list(Path(self.download_dir).glob("*.download")))
            
            if files and not temp_files:
                # Ensure file is not empty
                if files[0].stat().st_size > 1000:  # At least 1KB
                    return files[0]
            
            time.sleep(0.5)
        
        # Check if any file was partially downloaded
        all_files = list(Path(self.download_dir).glob("*"))
        if all_files:
            print(f"  ⚠ Download incomplete. Files in directory: {[f.name for f in all_files]}")
        
        return None
    
    def download_batch(self, doi_list, titles=None, check_auth=True):
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
        
        # Optional: Check authentication status
        if check_auth:
            self.check_authentication_status()
        
        results = []
        titles = titles or {}
        
        print(f"\nAttempting to download {len(doi_list)} papers...")
        print("=" * 60)
        
        for i, doi in enumerate(doi_list, 1):
            print(f"\n[{i}/{len(doi_list)}] DOI: {doi}")
            
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
    # Test DOIs - mix of open access and paywalled
    test_dois = [
        "10.1371/journal.pone.0261631",  # PLOS ONE - open access
        "10.3389/fnins.2019.00573",      # Frontiers - open access
        "10.1186/s12859-020-03839-1",    # BMC - open access
        "10.1038/s41586-020-2649-2",     # Nature - usually paywalled
        "10.1016/j.cell.2021.02.029",    # Cell - usually paywalled
    ]
    
    print("Direct DOI to PDF Downloader")
    print("=" * 60)
    print("\nThis will attempt to download PDFs directly from publishers.")
    print("Success depends on your browser's existing authentication.\n")
    
    downloader = DirectDOIDownloader(output_dir="./direct_doi_pdfs")
    
    try:
        results = downloader.download_batch(test_dois)
        
        print(f"\n{'='*60}")
        print(f"Downloaded {len(results)}/{len(test_dois)} PDFs")
        
        if results:
            print("\nSuccessful downloads:")
            for doi, path in results:
                print(f"  ✓ {doi}")
                print(f"    → {path.name}")
        
        # Show which ones failed
        failed_dois = set(test_dois) - set(doi for doi, _ in results)
        if failed_dois:
            print("\nFailed downloads:")
            for doi in failed_dois:
                print(f"  ✗ {doi}")
        
    finally:
        downloader.cleanup()