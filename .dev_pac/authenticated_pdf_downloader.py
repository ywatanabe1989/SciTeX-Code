#!/usr/bin/env python3
"""
Authenticated PDF downloader using Chrome Profile 1 with stored cookies and extensions.
This uses the manually created browser profile with authentication data.
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright, Page, Browser
from scitex import logging

logger = logging.getLogger(__name__)


class AuthenticatedPDFDownloader:
    """PDF downloader using authenticated Chrome profile with extensions."""
    
    def __init__(self):
        # Use Profile 1 which has manual authentication
        self.profile_dir = Path.home() / ".scitex" / "scholar" / "cache" / "chrome" / "Profile 1"
        self.extension_profile_dir = Path.home() / ".scitex" / "scholar" / "cache" / "chrome" / "_extension"
        
        # Extension IDs
        self.EXTENSIONS = {
            "lean_library": "hghakoefmnkhamdhenpbogkeopjlkpoa",
            "popup_blocker": "bkkbcggnhapdmkeljlodobbkopceiche", 
            "accept_cookies": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
            "captcha_solver_2captcha": "ifibfemgeogfhoebkmokieepdoobkbpo",
            "captcha_solver_hcaptcha": "hlifkpholllijblknnmbfagnkjneagid",
        }
        
        logger.info(f"Using authenticated profile: {self.profile_dir}")
        
    def get_papers_needing_pdfs(self, limit: int = 5) -> List[Dict]:
        """Get papers from pac collection that need PDFs."""
        library_dir = Path.home() / ".scitex" / "scholar" / "library"
        pac_dir = library_dir / "pac"
        master_dir = library_dir / "MASTER"
        
        if not pac_dir.exists():
            logger.error(f"Collection directory not found: {pac_dir}")
            return []
        
        papers = []
        count = 0
        
        logger.info(f"Scanning pac collection for papers without PDFs...")
        
        for item in sorted(pac_dir.iterdir()):
            if count >= limit:
                break
                
            if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
                target = item.readlink()
                if target.parts[0] == '..':
                    unique_id = target.parts[-1]
                    master_path = master_dir / unique_id
                    
                    if master_path.exists():
                        metadata_file = master_path / "metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                
                                # Check if PDF already exists
                                pdf_files = list(master_path.glob("*.pdf"))
                                if len(pdf_files) == 0:  # No PDF yet
                                    paper = {
                                        'human_name': item.name,
                                        'unique_id': unique_id,
                                        'master_path': master_path,
                                        'metadata': metadata,
                                    }
                                    papers.append(paper)
                                    count += 1
                                    logger.info(f"  {count}. {item.name}")
                                    
                            except Exception as e:
                                logger.error(f"Error reading {unique_id}: {e}")
                                continue
        
        logger.success(f"Found {len(papers)} papers needing PDFs")
        return papers
    
    def get_paper_url(self, metadata: Dict) -> Optional[str]:
        """Get the best URL for downloading from paper metadata."""
        if 'doi' in metadata and metadata['doi']:
            doi = metadata['doi']
            if not doi.startswith('http'):
                return f"https://doi.org/{doi}"
            return doi
        
        url_fields = ['url', 'publisher_url', 'journal_url', 'source_url']
        for field in url_fields:
            if field in metadata and metadata[field]:
                return metadata[field]
        
        return None
    
    def get_extension_paths(self) -> List[str]:
        """Get paths to installed extensions."""
        extension_paths = []
        extensions_dir = self.extension_profile_dir / "Default" / "Extensions"
        
        if extensions_dir.exists():
            for ext_id in self.EXTENSIONS.values():
                ext_dir = extensions_dir / ext_id
                if ext_dir.exists():
                    version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                    if version_dirs:
                        latest_version = max(version_dirs, key=lambda x: x.name)
                        manifest_file = latest_version / "manifest.json"
                        if manifest_file.exists():
                            extension_paths.append(str(latest_version))
                            logger.info(f"Extension found: {ext_id} -> {latest_version.name}")
        
        return extension_paths
    
    async def launch_authenticated_browser(self):
        """Launch browser with authenticated profile and extensions."""
        playwright = await async_playwright().start()
        
        # Get extension paths
        extension_paths = self.get_extension_paths()
        
        # Chrome launch arguments
        chrome_args = [
            f"--user-data-dir={self.profile_dir.parent}",
            f"--profile-directory={self.profile_dir.name}",
            "--enable-extensions",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
        ]
        
        # Add extensions if found
        if extension_paths:
            extensions_list = ",".join(extension_paths)
            chrome_args.extend([
                f"--load-extension={extensions_list}",
                f"--disable-extensions-except={extensions_list}",
            ])
            logger.success(f"Loading {len(extension_paths)} extensions")
        
        # Launch browser
        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir.parent),
            headless=False,  # Must be False for extensions
            args=chrome_args,
            viewport={'width': 1200, 'height': 800},
            ignore_https_errors=True,
        )
        
        logger.success("Launched authenticated browser with extensions")
        return playwright, browser
    
    async def extract_pdf_links_from_page(self, page: Page) -> List[str]:
        """Extract PDF links from the current page."""
        try:
            # Wait for page to stabilize
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Look for PDF links
            pdf_urls = await page.evaluate("""
                () => {
                    const urls = new Set();
                    
                    // Find all links
                    const links = document.querySelectorAll('a');
                    for (const link of links) {
                        const href = link.href || '';
                        const text = link.textContent || '';
                        
                        // Check if it's a PDF link
                        if (href.includes('.pdf') || 
                            href.includes('/pdf') ||
                            text.toLowerCase().includes('pdf') ||
                            text.toLowerCase().includes('download')) {
                            urls.add(href);
                        }
                    }
                    
                    // Look for data attributes
                    const dataElements = document.querySelectorAll('[data-pdf-url], [data-download-url]');
                    for (const elem of dataElements) {
                        const url = elem.getAttribute('data-pdf-url') || elem.getAttribute('data-download-url');
                        if (url) urls.add(url);
                    }
                    
                    // Check for Lean Library elements
                    const leanLibrary = document.querySelectorAll('[data-lean-library], .lean-library-pdf, .ll-pdf-button');
                    for (const elem of leanLibrary) {
                        const href = elem.href || elem.getAttribute('data-url');
                        if (href) urls.add(href);
                    }
                    
                    return Array.from(urls);
                }
            """)
            
            if pdf_urls:
                logger.success(f"Found {len(pdf_urls)} potential PDF URLs")
            
            return pdf_urls
            
        except Exception as e:
            logger.error(f"Error extracting PDF links: {e}")
            return []
    
    async def wait_for_lean_library(self, page: Page, timeout: int = 5):
        """Wait for Lean Library to activate and provide access."""
        try:
            logger.info(f"Waiting {timeout}s for Lean Library...")
            await page.wait_for_timeout(timeout * 1000)
            
            # Check for Lean Library elements
            lean_library_found = await page.evaluate("""
                () => {
                    const selectors = [
                        '[data-lean-library]',
                        '.lean-library-pdf',
                        '.ll-pdf-button',
                        '.lean-library-access',
                        'button:has-text("Get PDF")',
                        'a:has-text("Get PDF")'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const elem = document.querySelector(selector);
                            if (elem) return true;
                        } catch (e) {}
                    }
                    return false;
                }
            """)
            
            if lean_library_found:
                logger.success("Lean Library activated!")
                return True
            else:
                logger.warning("Lean Library not detected")
                return False
                
        except Exception as e:
            logger.error(f"Error waiting for Lean Library: {e}")
            return False
    
    async def download_pdf_with_browser(self, page: Page, pdf_url: str, output_path: Path) -> bool:
        """Download PDF using browser download capability."""
        try:
            # Set up download handler
            download_promise = page.wait_for_event('download', timeout=30000)
            
            # Navigate to PDF URL
            logger.info(f"Navigating to PDF: {pdf_url}")
            await page.goto(pdf_url)
            
            # Wait for download to start
            download = await download_promise
            
            # Save the download
            await download.save_as(output_path)
            
            # Verify it's a PDF
            if output_path.exists():
                with open(output_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        file_size = output_path.stat().st_size
                        logger.success(f"Downloaded PDF: {file_size / 1024 / 1024:.1f} MB")
                        return True
                    else:
                        logger.error(f"Not a valid PDF (header: {header})")
                        output_path.unlink()
                        return False
            
        except Exception as e:
            logger.error(f"Browser download failed: {e}")
            return False
    
    def generate_filename(self, paper: Dict) -> str:
        """Generate filename for downloaded PDF."""
        metadata = paper['metadata']
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        
        if authors and year:
            first_author = str(authors[0]) if authors else 'Unknown'
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            
            # Clean for filename
            first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
            return f"{first_author}-{year}.pdf"
        else:
            return f"{paper['human_name']}.pdf"
    
    def update_metadata(self, paper: Dict, filename: str, download_url: str):
        """Update paper metadata with download information."""
        try:
            metadata_file = paper['master_path'] / "metadata.json"
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['pdf_downloaded'] = True
            metadata['pdf_filename'] = filename
            metadata['pdf_download_url'] = download_url
            metadata['pdf_download_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.success("Updated metadata")
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
    
    async def download_paper_pdf(self, browser, paper: Dict) -> bool:
        """Download PDF for a single paper using authenticated browser."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {paper['human_name']}")
        logger.info(f"{'='*80}")
        
        metadata = paper['metadata']
        logger.info(f"Title: {metadata.get('title', 'N/A')[:70]}...")
        logger.info(f"Year: {metadata.get('year', 'N/A')}")
        logger.info(f"Journal: {metadata.get('journal', 'N/A')}")
        
        # Get URL
        url = self.get_paper_url(metadata)
        if not url:
            logger.error("No suitable URL found in metadata")
            return False
        
        logger.info(f"URL: {url}")
        
        # Generate output path
        filename = self.generate_filename(paper)
        output_path = paper['master_path'] / filename
        
        try:
            # Create new page
            page = await browser.new_page()
            
            # Navigate to the paper URL
            logger.info("Navigating to paper URL...")
            await page.goto(url, wait_until='networkidle')
            
            # Wait for Lean Library to activate
            await self.wait_for_lean_library(page)
            
            # Accept cookies if prompted
            try:
                cookie_button = await page.query_selector('button:has-text("Accept")')
                if cookie_button:
                    await cookie_button.click()
                    logger.info("Accepted cookies")
            except:
                pass
            
            # Take screenshot for debugging
            screenshot_path = paper['master_path'] / f"screenshot_{int(time.time())}.png"
            await page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path.name}")
            
            # Extract PDF links
            pdf_urls = await self.extract_pdf_links_from_page(page)
            
            if pdf_urls:
                logger.info(f"Found {len(pdf_urls)} PDF candidates")
                
                # Try each PDF URL
                for pdf_url in pdf_urls[:3]:  # Try first 3
                    logger.info(f"Trying: {pdf_url}")
                    
                    # Try browser download
                    if await self.download_pdf_with_browser(page, pdf_url, output_path):
                        self.update_metadata(paper, filename, pdf_url)
                        await page.close()
                        return True
            else:
                logger.warning("No PDF links found")
            
            # Try clicking download buttons
            logger.info("Looking for download buttons...")
            download_clicked = await page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button, a');
                    for (const btn of buttons) {
                        const text = btn.textContent || '';
                        if (text.toLowerCase().includes('download') && 
                            (text.toLowerCase().includes('pdf') || text.toLowerCase().includes('article'))) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            if download_clicked:
                logger.info("Clicked download button")
                await page.wait_for_timeout(5000)
                
                # Check for downloads
                # Note: This would need proper download handling
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error processing paper: {e}")
            return False
        
        logger.error(f"Failed to download PDF for {paper['human_name']}")
        return False


async def main():
    """Main function to download PDFs with authentication."""
    logger.info("🚀 Authenticated PDF Downloader")
    logger.info("=" * 60)
    
    downloader = AuthenticatedPDFDownloader()
    
    # Get papers needing PDFs
    papers = downloader.get_papers_needing_pdfs(limit=3)
    
    if not papers:
        logger.success("No papers need PDFs!")
        return
    
    logger.info(f"\nWill attempt to download {len(papers)} PDFs:")
    for i, paper in enumerate(papers, 1):
        metadata = paper['metadata']
        logger.info(f"  {i}. {paper['human_name']}")
        logger.info(f"     Journal: {metadata.get('journal', 'N/A')}")
        logger.info(f"     Year: {metadata.get('year', 'N/A')}")
    
    # Launch authenticated browser
    logger.info("\nLaunching authenticated browser...")
    playwright, browser = await downloader.launch_authenticated_browser()
    
    # Download PDFs
    successful = 0
    
    try:
        for paper in papers:
            try:
                success = await downloader.download_paper_pdf(browser, paper)
                
                if success:
                    successful += 1
                    logger.success(f"SUCCESS: {paper['human_name']}")
                else:
                    logger.error(f"FAILED: {paper['human_name']}")
                
                # Wait between downloads
                if paper != papers[-1]:
                    logger.info("Waiting 3 seconds...")
                    await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error processing {paper['human_name']}: {e}")
        
    finally:
        await browser.close()
        await playwright.stop()
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.success(f"Download Session Complete!")
    logger.info(f"Successful downloads: {successful}/{len(papers)}")
    
    if successful > 0:
        logger.success(f"Downloaded {successful} PDFs successfully!")
    else:
        logger.warning("No PDFs downloaded this session")


if __name__ == "__main__":
    asyncio.run(main())