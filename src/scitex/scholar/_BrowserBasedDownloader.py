#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 21:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_BrowserBasedDownloader.py
# ----------------------------------------
import os
__FILE__ = "./src/scitex/scholar/_BrowserBasedDownloader.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Browser-based PDF downloader that keeps the authenticated session alive.

This approach:
1. Opens browser for OpenAthens login (minimal automation)
2. Keeps the browser session alive
3. Downloads PDFs by navigating to papers in the same session
4. Avoids cookie domain issues entirely
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, Download

logger = logging.getLogger(__name__)


class BrowserBasedDownloader:
    """Download PDFs using an authenticated browser session."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize browser-based downloader.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._authenticated = False
        
    async def authenticate_openathens(self, email: Optional[str] = None) -> bool:
        """
        Open browser for OpenAthens authentication.
        
        Minimal automation - just opens browser and waits for user to login.
        """
        try:
            # Launch browser
            async with async_playwright() as p:
                self._browser = await p.chromium.launch(headless=self.headless)
                self._page = await self._browser.new_page()
                
                # Navigate to OpenAthens
                logger.info("Opening OpenAthens login page")
                await self._page.goto("https://my.openathens.net", wait_until='domcontentloaded')
                
                # Show instructions
                print("\n" + "="*60)
                print("Browser-Based Authentication")
                print("="*60)
                if email:
                    print(f"Account: {email}")
                print("\nPlease complete the login process in the browser:")
                print("1. Enter your email")
                print("2. Select your institution")
                print("3. Complete institution login")
                print("4. Return to OpenAthens")
                print("\n⚠️  Minimal automation for reliability")
                print("="*60 + "\n")
                
                # Wait for successful login (check every 5 seconds)
                max_wait = 300  # 5 minutes
                elapsed = 0
                
                while elapsed < max_wait:
                    try:
                        current_url = self._page.url
                        
                        # Simple success check - we're back at OpenAthens and logged in
                        if ('my.openathens.net/account' in current_url or 
                            'my.openathens.net/app' in current_url):
                            print("\n✅ Authentication successful!")
                            self._authenticated = True
                            return True
                            
                    except:
                        # Ignore navigation errors
                        pass
                    
                    await asyncio.sleep(5)
                    elapsed += 5
                    
                    if elapsed % 30 == 0:
                        print(f"Still waiting for login... ({elapsed}s)")
                
                print("\n❌ Authentication timeout")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def download_pdf(self, url: str, output_path: Path) -> bool:
        """
        Download PDF by navigating to it in the authenticated browser.
        
        Args:
            url: URL of the paper (can be DOI URL)
            output_path: Where to save the PDF
            
        Returns:
            True if download successful
        """
        if not self._authenticated or not self._page:
            logger.error("Not authenticated. Please authenticate first.")
            return False
            
        try:
            logger.info(f"Navigating to: {url}")
            
            # Set up download handling
            download_promise = None
            
            async def handle_download(download: Download):
                nonlocal download_promise
                download_promise = download
            
            self._page.on("download", handle_download)
            
            # Navigate to paper
            await self._page.goto(url, wait_until='domcontentloaded')
            await self._page.wait_for_timeout(3000)  # Let page settle
            
            # Look for PDF download button/link
            pdf_selectors = [
                # Nature
                'a[data-track-action="download pdf"]',
                '.c-pdf-download__link',
                
                # Science/AAAS
                '.btn-pdf-download',
                'a[data-article-pdf]',
                
                # Elsevier/ScienceDirect
                '.pdf-download-btn',
                '.pdfLink',
                'a[role="button"]:has-text("Download PDF")',
                
                # Wiley
                'a.pdf-download',
                '.article-tools__item--pdf a',
                
                # Springer
                'a.c-pdf-download',
                'a[data-track-label="download-pdf"]',
                
                # Generic
                'a:has-text("Download PDF")',
                'a:has-text("PDF")',
                'button:has-text("Download PDF")',
                'a[href$=".pdf"]'
            ]
            
            # Try to find and click PDF download
            pdf_found = False
            for selector in pdf_selectors:
                try:
                    element = await self._page.query_selector(selector)
                    if element and await element.is_visible():
                        logger.info(f"Found PDF element with selector: {selector}")
                        
                        # Click and wait for download
                        await element.click()
                        pdf_found = True
                        
                        # Wait for download to start
                        await asyncio.sleep(2)
                        
                        if download_promise:
                            # Save the download
                            await download_promise.save_as(output_path)
                            logger.info(f"PDF saved to: {output_path}")
                            return True
                        
                        break
                        
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not pdf_found:
                logger.error("Could not find PDF download button")
                
                # Try direct PDF link
                pdf_links = await self._page.query_selector_all('a[href$=".pdf"]')
                if pdf_links:
                    logger.info(f"Found {len(pdf_links)} direct PDF links")
                    # Try first link
                    href = await pdf_links[0].get_attribute('href')
                    if href:
                        # Navigate to PDF directly
                        response = await self._page.goto(href)
                        if response and 'application/pdf' in response.headers.get('content-type', ''):
                            # Save PDF content
                            content = await response.body()
                            output_path.write_bytes(content)
                            logger.info(f"PDF saved directly to: {output_path}")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    async def download_papers(self, paper_urls: List[str], output_dir: Path) -> Dict[str, Any]:
        """
        Download multiple papers.
        
        Args:
            paper_urls: List of paper URLs
            output_dir: Directory to save PDFs
            
        Returns:
            Results dictionary
        """
        if not self._authenticated:
            logger.error("Not authenticated. Please authenticate first.")
            return {"success": 0, "failed": len(paper_urls)}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "success": 0,
            "failed": 0,
            "papers": []
        }
        
        for i, url in enumerate(paper_urls, 1):
            print(f"\n[{i}/{len(paper_urls)}] Downloading: {url}")
            
            # Generate filename from URL
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1] or f"paper_{i}"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            output_path = output_dir / filename
            
            success = await self.download_pdf(url, output_path)
            
            if success:
                results["success"] += 1
                results["papers"].append({
                    "url": url,
                    "path": str(output_path),
                    "success": True
                })
                print(f"   ✅ Success: {output_path.name}")
            else:
                results["failed"] += 1
                results["papers"].append({
                    "url": url,
                    "success": False
                })
                print(f"   ❌ Failed")
            
            # Small delay between downloads
            if i < len(paper_urls):
                await asyncio.sleep(2)
        
        return results
    
    async def close(self):
        """Close the browser."""
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        self._authenticated = False


# Example usage
async def example():
    """Example of using browser-based downloader."""
    
    downloader = BrowserBasedDownloader(headless=False)
    
    # Authenticate
    success = await downloader.authenticate_openathens(email="user@university.edu")
    
    if success:
        # Download papers
        paper_urls = [
            "https://doi.org/10.1038/s41586-021-03819-2",
            "https://doi.org/10.1126/science.abe9868"
        ]
        
        results = await downloader.download_papers(
            paper_urls,
            Path("./downloads")
        )
        
        print(f"\nResults: {results['success']}/{len(paper_urls)} successful")
    
    await downloader.close()


if __name__ == "__main__":
    asyncio.run(example())