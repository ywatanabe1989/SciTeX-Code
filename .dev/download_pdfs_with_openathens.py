#!/usr/bin/env python3
"""Download PDFs using OpenAthens authentication with BrowserManager."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.auth._OpenAthensAuthenticator import OpenAthensAuthenticator
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.browser._BrowserConfig import BrowserConfiguration, BrowserMode
from scitex import logging

logger = logging.getLogger(__name__)


async def download_pdf_with_openathens(doi: str, storage_dir: Path, browser_manager: BrowserManager) -> bool:
    """Download a PDF using OpenAthens authenticated browser."""
    print(f"\n  Attempting to download PDF for DOI: {doi}")
    
    try:
        # Navigate to DOI
        url = f"https://doi.org/{doi}"
        page = await browser_manager.navigate(url)
        
        if not page:
            print("    ✗ Failed to navigate to URL")
            return False
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        # Take screenshot for debugging
        screenshot_dir = storage_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_doi_page.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"    📸 Screenshot saved: {screenshot_path.name}")
        
        # Look for PDF download links
        pdf_selectors = [
            'a[href*=".pdf"]',
            'a:has-text("PDF")',
            'a:has-text("Download PDF")',
            'button:has-text("PDF")',
            'button:has-text("Download")',
            'a[href*="/pdf/"]',
            'a[href*="full.pdf"]',
            'a.pdf-link',
            'a.download-pdf'
        ]
        
        pdf_link = None
        for selector in pdf_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    # Filter for visible elements
                    for elem in elements:
                        if await elem.is_visible():
                            pdf_link = elem
                            print(f"    Found PDF link with selector: {selector}")
                            break
                if pdf_link:
                    break
            except:
                continue
        
        if not pdf_link:
            print("    ✗ No PDF download link found")
            # Take screenshot of what we see
            await page.screenshot(path=str(screenshot_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_no_pdf_link.png"))
            return False
        
        # Get the PDF URL
        pdf_url = await pdf_link.get_attribute('href')
        if pdf_url and not pdf_url.startswith('http'):
            # Relative URL
            base_url = page.url.split('?')[0].rsplit('/', 1)[0]
            pdf_url = f"{base_url}/{pdf_url.lstrip('/')}"
        
        print(f"    PDF URL: {pdf_url}")
        
        # Download the PDF
        async with page.context.expect_download() as download_info:
            await pdf_link.click()
            download = await download_info.value
            
            # Save to storage directory
            filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
            pdf_path = storage_dir / filename
            await download.save_as(str(pdf_path))
            
            print(f"    ✓ SUCCESS! Downloaded {filename} to {pdf_path}")
            return True
            
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        # Take error screenshot
        try:
            screenshot_path = storage_dir / "screenshots" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_error.png"
            await page.screenshot(path=str(screenshot_path))
        except:
            pass
        return False


async def main():
    """Main function to download PDFs with OpenAthens."""
    print("=" * 80)
    print("PDF DOWNLOAD WITH OPENATHENS AUTHENTICATION")
    print("=" * 80)
    
    # Initialize OpenAthens authenticator
    auth = OpenAthensAuthenticator()
    
    # Check if authenticated
    if not await auth.is_authenticated(verify_live=False):
        print("\nNot authenticated with OpenAthens. Authenticating...")
        auth_result = await auth.authenticate()
        if not auth_result:
            print("Authentication failed!")
            return
    else:
        print("\n✓ Already authenticated with OpenAthens")
    
    # Load papers that need OpenAthens
    openathens_csv = Path(".dev/papers_for_openathens_download.csv")
    if not openathens_csv.exists():
        print("Run create_csv_summary_fixed.py first to generate download list!")
        return
    
    import pandas as pd
    papers_df = pd.read_csv(openathens_csv)
    print(f"\nFound {len(papers_df)} papers needing OpenAthens download")
    
    # Initialize browser with auth
    config = BrowserConfiguration(
        mode=BrowserMode.DEBUG,
        headless=False,  # Show browser for debugging
        viewport_size=(1280, 800),
        capture_screenshots=True
    )
    
    browser_manager = BrowserManager(
        auth_manager=auth,
        config=config
    )
    
    # Process papers
    successful = 0
    failed = []
    
    # Start browser
    await browser_manager.start()
    
    try:
        # Apply authentication cookies
        if hasattr(auth, '_full_cookies') and auth._full_cookies:
            await browser_manager.context.add_cookies(auth._full_cookies)
            print(f"Applied {len(auth._full_cookies)} authentication cookies")
        
        # Process first 5 papers as test
        for idx, row in papers_df.head(5).iterrows():
            storage_key = row['storage_key']
            doi = row['doi']
            title = row['title']
            
            print(f"\n[{idx+1}/5] {storage_key}: {title[:60]}...")
            
            # Get storage directory
            storage_dir = Path(f"/home/ywatanabe/.scitex/scholar/library/pac_research/{storage_key}")
            
            # Try to download
            success = await download_pdf_with_openathens(doi, storage_dir, browser_manager)
            
            if success:
                successful += 1
            else:
                failed.append({
                    'storage_key': storage_key,
                    'doi': doi,
                    'title': title
                })
            
            # Small delay between downloads
            await asyncio.sleep(2)
    
    finally:
        await browser_manager.stop()
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Successfully downloaded: {successful}/5")
    if failed:
        print(f"\nFailed downloads:")
        for f in failed:
            print(f"  - {f['doi']}: {f['title'][:50]}...")


if __name__ == "__main__":
    asyncio.run(main())