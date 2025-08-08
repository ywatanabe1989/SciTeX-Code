#!/usr/bin/env python3
"""
Download ALL PDFs using Selenium with authenticated Chrome Profile 1.
This properly handles IEEE, Elsevier, and other paywalled content.
"""

import json
import time
from pathlib import Path
from datetime import datetime
import shutil

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not installed. Install with: pip install selenium")


def setup_chrome_with_profile():
    """Setup Chrome with authenticated Profile 1."""
    options = Options()
    
    # Use the authenticated Profile 1
    profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument('--profile-directory=Profile 1')
    
    # Disable automation flags to avoid detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Set download directory
    download_dir = Path.home() / '.scitex' / 'scholar' / 'downloads'
    download_dir.mkdir(parents=True, exist_ok=True)
    
    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    options.add_experimental_option("prefs", prefs)
    
    # Window size
    options.add_argument('--window-size=1920,1080')
    
    return webdriver.Chrome(options=options), download_dir


def find_and_click_pdf_link(driver, wait_time=10):
    """Find and click PDF download link on the page."""
    try:
        # Wait for page to load
        time.sleep(3)
        
        # Common PDF link patterns
        pdf_selectors = [
            "a[href*='.pdf']",
            "a[href*='/pdf']",
            "button:contains('PDF')",
            "a:contains('Download PDF')",
            "a:contains('Full Text PDF')",
            "a:contains('Get PDF')",
            ".pdf-link",
            "[data-pdf-url]",
            "a[title*='PDF']",
            # IEEE specific
            "a[href*='stamp.jsp']",
            "xpl-pdf-btn",
            # Elsevier specific
            "a.download-pdf-link",
            ".pdf-download-btn",
            # Nature specific
            "a.c-pdf-download__link",
            # Frontiers specific
            "a.download-files-pdf",
        ]
        
        for selector in pdf_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Click the first visible element
                    for element in elements:
                        if element.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView();", element)
                            time.sleep(1)
                            element.click()
                            return True
            except:
                continue
        
        # Try JavaScript approach
        js_script = """
        var links = document.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            var link = links[i];
            if (link.href && (link.href.includes('.pdf') || 
                link.href.includes('/pdf') ||
                link.textContent.toLowerCase().includes('pdf'))) {
                link.click();
                return true;
            }
        }
        return false;
        """
        
        result = driver.execute_script(js_script)
        if result:
            return True
        
    except Exception as e:
        print(f"    Error finding PDF link: {e}")
    
    return False


def wait_for_download(download_dir: Path, timeout: int = 30) -> Path:
    """Wait for a PDF to appear in download directory."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check for PDF files
        pdf_files = list(download_dir.glob("*.pdf"))
        
        # Exclude partial downloads
        complete_pdfs = [f for f in pdf_files if not f.name.endswith('.crdownload')]
        
        if complete_pdfs:
            # Get the most recent PDF
            latest_pdf = max(complete_pdfs, key=lambda x: x.stat().st_mtime)
            
            # Check if it's recent (downloaded in last minute)
            if time.time() - latest_pdf.stat().st_mtime < 60:
                return latest_pdf
        
        time.sleep(1)
    
    return None


def download_all_pac_pdfs_selenium():
    """Download all PAC PDFs using Selenium with authentication."""
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available. Install with: pip install selenium")
        return
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    print("PAC Collection Selenium PDF Downloader (with OpenAthens)")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Setup Chrome with authenticated profile
    try:
        driver, download_dir = setup_chrome_with_profile()
        print(f"✅ Chrome launched with authenticated Profile 1")
        print(f"📁 Download directory: {download_dir}")
    except Exception as e:
        print(f"❌ Failed to launch Chrome: {e}")
        return
    
    # Get papers needing PDFs
    papers_to_download = []
    
    for item in sorted(pac_dir.iterdir()):
        if not item.is_symlink() or item.name.startswith('.') or item.name == 'info':
            continue
        
        target = item.readlink()
        if target.parts[0] != '..':
            continue
            
        unique_id = target.parts[-1]
        master_path = master_dir / unique_id
        
        if not master_path.exists():
            continue
        
        # Check if PDF already exists
        pdf_files = list(master_path.glob('*.pdf'))
        if pdf_files:
            continue
        
        # Load metadata
        metadata_file = master_path / 'metadata.json'
        if not metadata_file.exists():
            continue
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        doi = metadata.get('doi', '')
        if not doi:
            continue
        
        papers_to_download.append({
            'name': item.name,
            'unique_id': unique_id,
            'master_path': master_path,
            'metadata': metadata,
            'doi': doi,
            'url': f"https://doi.org/{doi}" if not doi.startswith('http') else doi
        })
    
    print(f"Found {len(papers_to_download)} papers needing PDFs")
    print()
    
    # Statistics
    successful = 0
    failed = []
    
    # Process each paper
    for i, paper in enumerate(papers_to_download, 1):
        print(f"[{i}/{len(papers_to_download)}] {paper['name'][:50]}")
        print(f"  Journal: {paper['metadata'].get('journal', 'Unknown')}")
        print(f"  DOI: {paper['doi']}")
        
        try:
            # Clear download directory
            for old_file in download_dir.glob("*.pdf"):
                old_file.unlink()
            
            # Navigate to DOI
            driver.get(paper['url'])
            time.sleep(5)  # Wait for redirects and page load
            
            # Get final URL after redirects
            final_url = driver.current_url
            print(f"  Final URL: {final_url[:80]}...")
            
            # Try to find and click PDF link
            pdf_clicked = find_and_click_pdf_link(driver)
            
            if pdf_clicked:
                print(f"  📥 PDF link clicked, waiting for download...")
                
                # Wait for download
                downloaded_pdf = wait_for_download(download_dir)
                
                if downloaded_pdf:
                    # Generate filename
                    authors = paper['metadata'].get('authors', [])
                    year = paper['metadata'].get('year', '')
                    if authors and year:
                        first_author = str(authors[0]).split(',')[0].split()[-1]
                        import re
                        first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
                        filename = f"{first_author}-{year}.pdf"
                    else:
                        filename = f"{paper['name']}.pdf"
                    
                    # Move to paper directory
                    target_path = paper['master_path'] / filename
                    shutil.move(str(downloaded_pdf), str(target_path))
                    
                    print(f"  ✅ Downloaded: {filename} ({target_path.stat().st_size / 1024 / 1024:.1f} MB)")
                    
                    # Update metadata
                    with open(paper['master_path'] / 'metadata.json', 'r') as f:
                        metadata = json.load(f)
                    metadata['pdf_downloaded'] = True
                    metadata['pdf_filename'] = filename
                    metadata['pdf_download_url'] = final_url
                    metadata['pdf_download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open(paper['master_path'] / 'metadata.json', 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    successful += 1
                else:
                    print(f"  ⚠️  PDF download timeout")
                    failed.append(paper['name'])
            else:
                print(f"  ⚠️  Could not find PDF link")
                failed.append(paper['name'])
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed.append(paper['name'])
        
        # Small delay between papers
        time.sleep(2)
    
    # Close browser
    driver.quit()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Successfully downloaded: {successful}/{len(papers_to_download)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed papers:")
        for name in failed[:10]:
            print(f"  - {name}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")
    
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    download_all_pac_pdfs_selenium()