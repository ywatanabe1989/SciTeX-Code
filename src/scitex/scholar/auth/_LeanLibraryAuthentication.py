#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 03:00:00 (ywatanabe)"
# File: ./src/scitex/scholar/auth/_LeanLibraryAuthentication.py
# ----------------------------------------

"""
Lean Library browser extension integration for institutional PDF access.

This authenticator leverages the Lean Library browser extension to access
papers through institutional subscriptions. It requires the extension to be
installed in the user's Chrome browser.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import platform

from playwright.async_api import async_playwright, Page, BrowserContext

from ...errors import ScholarError

logger = logging.getLogger(__name__)


class LeanLibraryError(ScholarError):
    """Raised when Lean Library operations fail."""
    pass


class LeanLibraryAuthenticator:
    """
    Authenticator that uses Lean Library browser extension for institutional access.
    
    Lean Library is a browser extension that automatically provides institutional
    access to academic papers. It's used by many universities including Harvard,
    Stanford, Yale, and others.
    
    Advantages over OpenAthens:
    - Automatic authentication (no manual login needed after initial setup)
    - Works with all major publishers
    - Provides visual indicators when access is available
    - Falls back to open access versions automatically
    """
    
    def __init__(self, config=None):
        """
        Initialize Lean Library authenticator.
        
        Args:
            config: Scholar configuration object
        """
        self.config = config
        self.debug_mode = getattr(config, 'debug_mode', False)
        self._user_data_dir = None
        self._browser_channel = "chrome"  # or "msedge", "chromium"
        
    def _find_browser_profile(self) -> Optional[Path]:
        """Find the user's browser profile directory."""
        home = Path.home()
        system = platform.system()
        
        # Potential profile locations by OS
        profile_paths = []
        
        if system == "Darwin":  # macOS
            profile_paths = [
                home / "Library/Application Support/Google/Chrome",
                home / "Library/Application Support/Microsoft Edge",
            ]
        elif system == "Linux":
            profile_paths = [
                home / ".config/google-chrome",
                home / ".config/chromium",
                home / ".config/microsoft-edge",
            ]
        elif system == "Windows":
            profile_paths = [
                home / "AppData/Local/Google/Chrome/User Data",
                home / "AppData/Local/Microsoft/Edge/User Data",
            ]
        
        # Find first existing profile
        for path in profile_paths:
            if path.exists():
                logger.info(f"Found browser profile at: {path}")
                # Detect browser type
                if "Chrome" in str(path) or "google-chrome" in str(path):
                    self._browser_channel = "chrome"
                elif "Edge" in str(path) or "microsoft-edge" in str(path):
                    self._browser_channel = "msedge"
                elif "chromium" in str(path):
                    self._browser_channel = "chromium"
                return path
        
        return None
    
    async def is_available_async(self) -> bool:
        """
        Check if Lean Library can be used.
        
        Returns:
            True if browser profile exists and can be used
        """
        if self._user_data_dir is None:
            profile_path = self._find_browser_profile()
            if profile_path:
                self._user_data_dir = str(profile_path)
                return True
        return self._user_data_dir is not None
    
    async def check_extension_async(self, page: Page) -> bool:
        """
        Check if Lean Library extension is active on the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if Lean Library is detected
        """
        # Wait for potential Lean Library activation
        await page.wait_for_timeout(2000)
        
        # Look for Lean Library indicators
        indicators = [
            # Lean Library elements
            'div[class*="lean-library"]',
            'div[id*="lean-library"]',
            '[class*="leanlibrary"]',
            '[id*="leanlibrary"]',
            # Modified elements
            'button[class*="lean"]',
            'a[class*="lean"]',
            # Lean Library banner
            '.lean-library-banner',
            '#lean-library-banner',
        ]
        
        for selector in indicators:
            try:
                element = await page.query_selector(selector)
                if element:
                    logger.info(f"Detected Lean Library element: {selector}")
                    return True
            except:
                continue
        
        # Also check for modified page title or meta tags
        try:
            # Lean Library sometimes adds meta tags
            meta = await page.query_selector('meta[name*="lean"]')
            if meta:
                return True
        except:
            pass
        
        return False
    
    async def download_with_extension_async(
        self,
        url: str,
        output_path: Path,
        timeout: int = 30000
    ) -> Optional[Path]:
        """
        Download PDF using browser with Lean Library extension.
        
        Args:
            url: URL of the paper
            output_path: Where to save the PDF
            timeout: Maximum time to wait for download
            
        Returns:
            Path to downloaded file or None
        """
        if not await self.is_available_async():
            raise LeanLibraryError("Browser profile not found. Cannot use Lean Library.")
        
        async with async_playwright() as p:
            # Launch browser with user profile
            logger.info(f"Launching {self._browser_channel} with user profile...")
            
            try:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self._user_data_dir,
                    headless=False,  # Extensions don't work in headless mode
                    channel=self._browser_channel,
                    slow_mo=100 if self.debug_mode else 0,
                    downloads_path=str(output_path.parent),
                    accept_downloads=True,
                    args=[
                        "--profile-directory=Default",
                    ]
                )
                
                # Use existing page or create new one
                page = context.pages[0] if context.pages else await context.new_page()
                
                # Navigate to paper
                logger.info(f"Navigating to: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                
                # Check if Lean Library is active
                has_extension = await self.check_extension_async(page)
                if not has_extension:
                    logger.warning("Lean Library extension not detected on page")
                
                # Wait for any authentication redirects
                await page.wait_for_timeout(3000)
                
                # Look for PDF download options
                pdf_found = await self._download_pdf_from_page_async(page, output_path, timeout)
                
                if pdf_found:
                    logger.info(f"Successfully downloaded PDF to: {output_path}")
                    return output_path
                else:
                    logger.warning("Could not find PDF download option")
                    return None
                    
            except Exception as e:
                logger.error(f"Lean Library download failed: {e}")
                raise LeanLibraryError(f"Download failed: {str(e)}")
            finally:
                await context.close()
    
    async def _download_pdf_from_page_async(
        self,
        page: Page,
        output_path: Path,
        timeout: int
    ) -> bool:
        """
        Try to download PDF from the current page.
        
        Args:
            page: Playwright page object
            output_path: Where to save the PDF
            timeout: Maximum time to wait
            
        Returns:
            True if download succeeded
        """
        # Common PDF link selectors
        pdf_selectors = [
            # Direct PDF links
            'a[href$=".pdf"]',
            'a[href*=".pdf?"]',
            'a[href*="/pdf/"]',
            # Download buttons
            'button:has-text("Download PDF")',
            'button:has-text("PDF")',
            'a:has-text("Download PDF")',
            'a:has-text("Full Text PDF")',
            'a:has-text("View PDF")',
            # Publisher-specific
            '[class*="pdf-download"]',
            '[class*="download-pdf"]',
            '[id*="pdf-download"]',
            '.pdf-link',
            # Nature specific
            'a[data-track-action="download pdf"]',
            # Elsevier specific
            'a.download-pdf-link',
            # Wiley specific
            'a.pdf-download-btn',
        ]
        
        for selector in pdf_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000)
                if element:
                    logger.info(f"Found PDF link with selector: {selector}")
                    
                    # Check if it's actually visible
                    is_visible = await element.is_visible()
                    if not is_visible:
                        continue
                    
                    # Get href to check if it's a real PDF link
                    href = await element.get_attribute('href')
                    if href and ('.pdf' in href or '/pdf/' in href):
                        logger.info(f"PDF URL: {href[:100]}...")
                        
                        # Set up download handling
                        async with page.expect_download(timeout=timeout) as download_info:
                            await element.click()
                            download = await download_info.value
                            
                            # Save the file
                            await download.save_as(output_path)
                            return True
                    else:
                        # Try clicking anyway (might trigger download)
                        try:
                            async with page.expect_download(timeout=10000) as download_info:
                                await element.click()
                                download = await download_info.value
                                await download.save_as(output_path)
                                return True
                        except:
                            continue
                            
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        return False
    
    async def test_access_async(self, test_url: str = None) -> Dict[str, Any]:
        """
        Test if Lean Library is working properly.
        
        Args:
            test_url: URL to test (defaults to Nature paper)
            
        Returns:
            Dictionary with test results
        """
        if test_url is None:
            test_url = "https://doi.org/10.1038/s41586-020-2832-5"  # Nature paper
        
        results = {
            "browser_profile_found": False,
            "browser_type": None,
            "extension_detected": False,
            "pdf_accessible": False,
            "error": None
        }
        
        try:
            # Check profile
            if await self.is_available_async():
                results["browser_profile_found"] = True
                results["browser_type"] = self._browser_channel
            else:
                results["error"] = "No browser profile found"
                return results
            
            # Test extension
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self._user_data_dir,
                    headless=False,
                    channel=self._browser_channel,
                )
                
                page = context.pages[0] if context.pages else await context.new_page()
                
                await page.goto(test_url, wait_until='domcontentloaded')
                
                # Check extension
                results["extension_detected"] = await self.check_extension_async(page)
                
                # Check PDF access
                pdf_selectors = ['a[href*=".pdf"]', 'button:has-text("PDF")']
                for selector in pdf_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            results["pdf_accessible"] = True
                            break
                    except:
                        pass
                
                await context.close()
                
        except Exception as e:
            results["error"] = str(e)
        
        return results


# Module-level function for convenience
async def download_with_lean_library(
    url: str,
    output_path: Path,
    config=None
) -> Optional[Path]:
    """
    Download a PDF using Lean Library browser extension.
    
    Args:
        url: URL of the paper
        output_path: Where to save the PDF
        config: Optional Scholar configuration
        
    Returns:
        Path to downloaded file or None
    """
    authenticator = LeanLibraryAuthenticator(config)
    
    if not await authenticator.is_available_async():
        logger.warning("Lean Library not available (no browser profile found)")
        return None
    
    try:
        return await authenticator.download_with_extension_async(url, output_path)
    except Exception as e:
        logger.error(f"Lean Library download failed: {e}")
        return None