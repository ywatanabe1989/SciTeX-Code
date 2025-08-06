#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 12:35:00"
# Author: Yusuke Watanabe
# File: _EZProxyDownloadStrategy.py

"""
EZProxy-based download strategy for PDFs.

This strategy uses EZProxy authentication to download PDFs
through institutional subscriptions.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

from scitex import logging

try:
    from playwright.async_api import Page, Browser
except ImportError:
    Page = None
    Browser = None

from ...errors import PDFDownloadError
from ..auth import EZProxyAuthenticator
from ._BaseDownloadStrategy import BaseDownloadStrategy

logger = logging.getLogger(__name__)


class EZProxyDownloadStrategy(BaseDownloadStrategy):
    """Download PDFs using EZProxy authentication."""
    
    def __init__(
        self,
        ezproxy_authenticator: Optional[EZProxyAuthenticator] = None,
        proxy_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize EZProxy download strategy.
        
        Args:
            ezproxy_authenticator: Pre-configured authenticator
            proxy_url: EZProxy server URL if creating new authenticator
            username: Username for authentication
            password: Password for authentication
            timeout: Download timeout in seconds
        """
        super().__init__(**kwargs)
        
        # Use provided authenticator or create new one
        if ezproxy_authenticator:
            self.authenticator = ezproxy_authenticator
        else:
            self.authenticator = EZProxyAuthenticator(
                proxy_url=proxy_url,
                username=username,
                password=password,
                timeout=timeout
            )
        
        self.timeout = timeout
    
    async def can_download(self, url: str, paper: Optional[Any] = None) -> bool:
        """
        Check if this strategy can download from the given URL.
        
        Args:
            url: URL to check
            paper: Paper object (optional)
            
        Returns:
            True if EZProxy is configured and authenticate_async
        """
        # Check if EZProxy is configured
        if not self.authenticator or not self.authenticator.proxy_url:
            return False
            
        # Check if authenticate_async
        try:
            return await self.authenticator.is_authenticate_async()
        except Exception:
            return False
    
    async def download(
        self,
        url: str,
        output_path: Path,
        paper: Optional[Any] = None,
        progress_callback: Optional[Any] = None
    ) -> bool:
        """
        Download PDF using EZProxy authentication.
        
        Args:
            url: URL to download
            output_path: Where to save the PDF
            paper: Paper object (optional)
            progress_callback: Progress callback function
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure authenticate_async
            if not await self.authenticator.is_authenticate_async():
                logger.info("Authenticating with EZProxy...")
                await self.authenticator.authenticate_async()
            
            # Transform URL through EZProxy
            proxied_url = self.authenticator.transform_url(url)
            logger.info(f"Downloading through EZProxy: {proxied_url}")
            
            # Create authenticate_async browser
            browser, context = await self.authenticator.create_authenticate_async_browser()
            
            try:
                page = await context.new_page()
                
                # Set up download handling
                download_path = output_path.parent
                download_path.mkdir(parents=True, exist_ok=True)
                
                # Navigate to the proxied URL
                response = await page.goto(proxied_url, wait_until="networkidle", timeout=self.timeout * 1000)
                
                if not response:
                    logger.warning("No response from EZProxy")
                    return False
                
                # Check if we got a PDF directly
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    # Direct PDF response
                    content = await response.body()
                    output_path.write_bytes(content)
                    logger.info(f"Downloaded PDF directly: {output_path}")
                    return True
                
                # Look for PDF download link on the page
                pdf_link = await self._find_pdf_link_async(page)
                
                if pdf_link:
                    # Download the PDF
                    async with page.expect_download(timeout=self.timeout * 1000) as download_info:
                        await page.click(pdf_link)
                    
                    download = await download_info.value
                    
                    # Save to specified path
                    await download.save_as(output_path)
                    logger.info(f"Downloaded PDF: {output_path}")
                    return True
                else:
                    logger.warning("No PDF link found on page")
                    return False
                    
            finally:
                await browser.close()
                
        except Exception as e:
            logger.error(f"EZProxy download failed: {e}")
            return False
    
    async def _find_pdf_link_async(self, page: Page) -> Optional[str]:
        """
        Find PDF download link on the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            CSS selector for PDF link or None
        """
        # Common PDF link patterns
        pdf_selectors = [
            'a[href$=".pdf"]',
            'a[href*="/pdf/"]',
            'a:has-text("Download PDF")',
            'a:has-text("Full Text PDF")',
            'a:has-text("View PDF")',
            'button:has-text("Download PDF")',
            'a[class*="pdf-link"]',
            'a[class*="download-pdf"]',
            'a[data-track-action="download pdf"]',
            # Publisher-specific
            'a[data-article-pdf]',  # Nature
            'a.article-pdf-download',  # Various publishers
            'a[rel="alternate"][type="application/pdf"]',
        ]
        
        for selector in pdf_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # Check if visible
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.debug(f"Found PDF link with selector: {selector}")
                        return selector
            except Exception:
                continue
                
        return None
    
    async def get_authenticate_async_session(self) -> Dict[str, Any]:
        """Get authenticate_async session information."""
        if not await self.authenticator.is_authenticate_async():
            await self.authenticator.authenticate_async()
            
        return {
            "cookies": await self.authenticator.get_auth_cookies_async(),
            "headers": await self.authenticator.get_auth_headers_async(),
            "proxy_url": self.authenticator.proxy_url,
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"EZProxyDownloadStrategy(proxy_url={self.authenticator.proxy_url})"

# EOF