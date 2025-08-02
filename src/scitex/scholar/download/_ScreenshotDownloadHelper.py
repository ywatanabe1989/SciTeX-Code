#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/_ScreenshotDownloadHelper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/_ScreenshotDownloadHelper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Download helper with screenshot capture for debugging.

Captures screenshots during download attempts to help diagnose:
- Authentication pages
- Captchas
- Access denied errors
- Successful downloads
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scitex import logging
from ..storage import EnhancedStorageManager
from ..lookup import get_default_lookup

logger = logging.getLogger(__name__)

# Try to import browser automation tools
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.debug("Playwright not available - screenshot capture disabled")


class ScreenshotDownloadHelper:
    """Download helper with screenshot capture capabilities."""
    
    def __init__(self, storage_manager: Optional[EnhancedStorageManager] = None):
        """Initialize download helper.
        
        Args:
            storage_manager: Storage manager instance
        """
        self.storage = storage_manager or EnhancedStorageManager()
        self.lookup = get_default_lookup()
        
    async def download_with_screenshots(self, storage_key: str, urls: List[str],
                                      headless: bool = False) -> Dict:
        """Attempt to download PDF with screenshot capture.
        
        Args:
            storage_key: Storage key for the paper
            urls: List of URLs to try
            headless: Run browser in headless mode
            
        Returns:
            Download result with screenshot paths
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "success": False,
                "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"
            }
            
        result = {
            "storage_key": storage_key,
            "success": False,
            "pdf_path": None,
            "screenshots": [],
            "errors": []
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Set download directory
            download_dir = Path.home() / ".scitex" / "downloads" / storage_key
            download_dir.mkdir(parents=True, exist_ok=True)
            
            page = await context.new_page()
            
            # Listen for downloads
            download_path = None
            
            async def handle_download(download):
                nonlocal download_path
                suggested_filename = download.suggested_filename
                download_path = download_dir / suggested_filename
                await download.save_as(download_path)
                logger.info(f"Downloaded: {suggested_filename}")
                
            page.on("download", handle_download)
            
            # Try each URL
            for idx, url in enumerate(urls):
                try:
                    logger.info(f"Trying URL {idx+1}/{len(urls)}: {url}")
                    
                    # Navigate to URL
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(2000)  # Let page stabilize
                    
                    # Capture initial screenshot
                    screenshot_path = await self._capture_screenshot(
                        page, storage_key, f"attempt-{idx+1}-initial"
                    )
                    result["screenshots"].append(str(screenshot_path))
                    
                    # Check for common authentication/access patterns
                    page_content = await page.content()
                    page_title = await page.title()
                    
                    # Check for login forms
                    if await self._check_for_login(page):
                        screenshot_path = await self._capture_screenshot(
                            page, storage_key, f"attempt-{idx+1}-login-required"
                        )
                        result["screenshots"].append(str(screenshot_path))
                        result["errors"].append(f"Login required at {url}")
                        continue
                        
                    # Check for captcha
                    if await self._check_for_captcha(page):
                        screenshot_path = await self._capture_screenshot(
                            page, storage_key, f"attempt-{idx+1}-captcha"
                        )
                        result["screenshots"].append(str(screenshot_path))
                        result["errors"].append(f"Captcha detected at {url}")
                        continue
                        
                    # Look for PDF viewer or download button
                    if "pdf" in page_content.lower() or "download" in page_content.lower():
                        # Try clicking download button
                        download_clicked = await self._try_download_button(page)
                        
                        if download_clicked:
                            # Wait for download
                            await page.wait_for_timeout(5000)
                            
                            if download_path and download_path.exists():
                                # Success!
                                screenshot_path = await self._capture_screenshot(
                                    page, storage_key, f"attempt-{idx+1}-success"
                                )
                                result["screenshots"].append(str(screenshot_path))
                                
                                # Store the PDF
                                stored_path = self.storage.store_pdf(
                                    storage_key=storage_key,
                                    pdf_path=download_path,
                                    original_filename=download_path.name,
                                    pdf_url=url
                                )
                                
                                result["success"] = True
                                result["pdf_path"] = str(stored_path)
                                logger.info(f"Successfully downloaded from {url}")
                                break
                                
                    # Capture final state
                    screenshot_path = await self._capture_screenshot(
                        page, storage_key, f"attempt-{idx+1}-final"
                    )
                    result["screenshots"].append(str(screenshot_path))
                    
                except Exception as e:
                    logger.error(f"Error with URL {url}: {e}")
                    result["errors"].append(str(e))
                    
                    # Capture error screenshot
                    try:
                        screenshot_path = await self._capture_screenshot(
                            page, storage_key, f"attempt-{idx+1}-error"
                        )
                        result["screenshots"].append(str(screenshot_path))
                    except:
                        pass
                        
            await browser.close()
            
        # Clean up download directory
        if download_dir.exists():
            for f in download_dir.iterdir():
                if f != download_path:
                    f.unlink()
            if not any(download_dir.iterdir()):
                download_dir.rmdir()
                
        return result
        
    async def _capture_screenshot(self, page: Page, storage_key: str, 
                                 description: str) -> Path:
        """Capture and store screenshot.
        
        Args:
            page: Playwright page object
            storage_key: Storage key
            description: Screenshot description
            
        Returns:
            Path to stored screenshot
        """
        # Capture screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = Path.home() / ".scitex" / "temp" / f"{timestamp}-{storage_key}.png"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        await page.screenshot(path=temp_path, full_page=True)
        
        # Store with storage manager
        stored_path = self.storage.store_screenshot(
            storage_key=storage_key,
            screenshot_path=temp_path,
            description=description,
            convert_to_jpg=True,
            quality=85
        )
        
        # Clean up temp file
        temp_path.unlink()
        
        return stored_path
        
    async def _check_for_login(self, page: Page) -> bool:
        """Check if page requires login."""
        login_indicators = [
            "input[type='password']",
            "button:has-text('Login')",
            "button:has-text('Sign in')",
            "a:has-text('Login')",
            "form[action*='login']",
            "div:has-text('Please log in')"
        ]
        
        for selector in login_indicators:
            try:
                if await page.locator(selector).count() > 0:
                    return True
            except:
                pass
                
        return False
        
    async def _check_for_captcha(self, page: Page) -> bool:
        """Check if page has captcha."""
        captcha_indicators = [
            "iframe[src*='recaptcha']",
            "div[class*='captcha']",
            "img[alt*='captcha']",
            "div:has-text('I am not a robot')",
            "div:has-text('Verify you are human')"
        ]
        
        for selector in captcha_indicators:
            try:
                if await page.locator(selector).count() > 0:
                    return True
            except:
                pass
                
        return False
        
    async def _try_download_button(self, page: Page) -> bool:
        """Try to click download button."""
        download_selectors = [
            "a[href$='.pdf']",
            "button:has-text('Download PDF')",
            "a:has-text('Download PDF')",
            "button:has-text('Download')",
            "a:has-text('Download')",
            "a[download]",
            "button[aria-label*='download']"
        ]
        
        for selector in download_selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    await elements[0].click()
                    return True
            except:
                pass
                
        return False


def create_download_report(storage_key: str) -> Dict:
    """Create a report of download attempts for a paper.
    
    Args:
        storage_key: Storage key
        
    Returns:
        Report dictionary
    """
    storage = EnhancedStorageManager()
    
    # Get screenshots
    screenshots = storage.list_screenshots(storage_key)
    
    # Get PDF info
    pdfs = storage.list_pdfs(storage_key)
    pdf_info = storage.get_pdf_info(storage_key) if pdfs else None
    
    report = {
        "storage_key": storage_key,
        "has_pdf": len(pdfs) > 0,
        "pdf_info": pdf_info,
        "download_attempts": len([s for s in screenshots if "attempt" in s["description"]]),
        "screenshots": screenshots,
        "latest_screenshot": None
    }
    
    # Get latest screenshot path
    latest = storage.get_latest_screenshot(storage_key)
    if latest:
        report["latest_screenshot"] = str(latest)
        
    return report


if __name__ == "__main__":
    print("Screenshot Download Helper")
    print("=" * 60)
    
    print("\nFeatures:")
    print("- Captures screenshots during download attempts")
    print("- Converts PNG to JPG to save space")
    print("- Organized storage: storage/KEY/screenshots/")
    print("- Tracks login pages, captchas, errors")
    print("- Keeps download history for debugging")
    
    print("\nUsage:")
    print("""
    # With playwright installed
    helper = ScreenshotDownloadHelper()
    
    result = await helper.download_with_screenshots(
        storage_key="ABCD1234",
        urls=[
            "https://doi.org/10.1038/example",
            "https://openurl.unimelb.edu.au/...",
            "https://arxiv.org/pdf/..."
        ],
        headless=False  # Show browser for debugging
    )
    
    # Check results
    if result["success"]:
        print(f"PDF saved at: {result['pdf_path']}")
    else:
        print(f"Failed. Screenshots: {result['screenshots']}")
        print(f"Errors: {result['errors']}")
    """)

# EOF