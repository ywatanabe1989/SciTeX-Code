#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:05:00"
# Author: Yusuke Watanabe
# File: _ShibbolethDownloadStrategy.py

"""
Shibboleth-based download strategy for PDFs.

This strategy uses Shibboleth authentication to download PDFs
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
from ..auth import ShibbolethAuthenticator
from ._BaseDownloadStrategy import BaseDownloadStrategy

logger = logging.getLogger(__name__)


class ShibbolethDownloadStrategy(BaseDownloadStrategy):
    """Download PDFs using Shibboleth authentication."""
    
    def __init__(
        self,
        shibboleth_authenticator: Optional[ShibbolethAuthenticator] = None,
        institution: Optional[str] = None,
        idp_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize Shibboleth download strategy.
        
        Args:
            shibboleth_authenticator: Pre-configured authenticator
            institution: Institution name if creating new authenticator
            idp_url: Identity Provider URL
            username: Username for authentication
            password: Password for authentication
            timeout: Download timeout in seconds
        """
        super().__init__(**kwargs)
        
        # Use provided authenticator or create new one
        if shibboleth_authenticator:
            self.authenticator = shibboleth_authenticator
        else:
            self.authenticator = ShibbolethAuthenticator(
                institution=institution,
                idp_url=idp_url,
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
            True if Shibboleth is configured and authenticate_async
        """
        # Check if Shibboleth is configured
        if not self.authenticator:
            return False
            
        # Check if URL is from a Shibboleth-protected site
        sp_info = self.authenticator.detect_shibboleth_sp(url)
        if not sp_info:
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
        Download PDF using Shibboleth authentication.
        
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
                logger.info("Authenticating with Shibboleth...")
                await self.authenticator.authenticate_async(resource_url=url)
            
            logger.info(f"Downloading via Shibboleth: {url}")
            
            # Create authenticate_async browser
            browser, context = await self.authenticator.create_authenticate_async_browser()
            
            try:
                page = await context.new_page()
                
                # Set up download handling
                download_path = output_path.parent
                download_path.mkdir(parents=True, exist_ok=True)
                
                # Navigate to the URL
                response = await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                
                if not response:
                    logger.warning("No response from server")
                    return False
                
                # Check if we got a PDF directly
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    # Direct PDF response
                    content = await response.body()
                    output_path.write_bytes(content)
                    logger.info(f"Downloaded PDF directly: {output_path}")
                    return True
                
                # Check if we need to handle institutional login again
                if await self._needs_institutional_login_async(page):
                    # Click institutional login
                    login_link = await self._find_institutional_login_async(page)
                    if login_link:
                        await login_link.click()
                        await page.wait_for_load_state("networkidle")
                
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
            logger.error(f"Shibboleth download failed: {e}")
            return False
    
    async def _needs_institutional_login_async(self, page: Page) -> bool:
        """Check if page requires institutional login."""
        indicators = [
            "institutional login",
            "access through your institution",
            "shibboleth",
            "wayf",
            "where are you from",
        ]
        
        page_text = (await page.text_content() or "").lower()
        return any(ind in page_text for ind in indicators)
    
    async def _find_institutional_login_async(self, page: Page) -> Optional[Any]:
        """Find institutional login link."""
        selectors = [
            "a:has-text('Institutional')",
            "a:has-text('Institution')",
            "a:has-text('Shibboleth')",
            "a:has-text('Access through your institution')",
            "button:has-text('Institutional')",
        ]
        
        for selector in selectors:
            element = await page.query_selector(selector)
            if element and await element.is_visible():
                return element
                
        return None
    
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
            # JSTOR specific
            'a.pdfLink',
            'a[data-qa="download-pdf"]',
            # Project MUSE specific
            'a.download-link',
            # IEEE specific
            'a[aria-label*="PDF"]',
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
            "institution": self.authenticator.institution,
            "saml_attributes": self.authenticator._saml_attributes,
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"ShibbolethDownloadStrategy(institution={self.authenticator.institution})"

# EOF