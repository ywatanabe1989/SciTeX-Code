#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:15:00 (ywatanabe)"
# File: ./src/scitex/scholar/download/_SciHubDownloadStrategy.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/download/_SciHubDownloadStrategy.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Sci-Hub download strategy for PDFs.

This module implements downloads through Sci-Hub for paywalled content.
Note: Use of Sci-Hub may have legal and ethical implications.
"""

"""Imports"""
from scitex import logging
import asyncio
from pathlib import Path
from typing import Optional, Callable, List
import aiohttp
from playwright.async_api import async_playwright
import re

from ._BaseDownloadStrategy import BaseDownloadStrategy
from ...errors import PDFDownloadError, ScholarError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class SciHubDownloadStrategy(BaseDownloadStrategy):
    """Sci-Hub download strategy implementation."""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize Sci-Hub download strategy.
        
        Args:
            config: Configuration options including ethical acknowledgment
        """
        super().__init__(config)
        self.mirrors = [
            "https://sci-hub.se",
            "https://sci-hub.st",
            "https://sci-hub.ru"
        ]
        self.timeout = config.get('timeout', 30) if config else 30
        self.ethical_acknowledged = config.get('acknowledge_ethical_usage', False) if config else False
        
    async def can_handle(self, url: str) -> bool:
        """
        Sci-Hub can potentially handle any academic paper URL/DOI.
        
        Args:
            url: URL or DOI to check
            
        Returns:
            True if ethical usage acknowledged
        """
        return self.ethical_acknowledged
        
    async def download(
        self,
        url: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
        **kwargs
    ) -> bool:
        """
        Download PDF through Sci-Hub.
        
        Args:
            url: URL or DOI to download
            save_path: Path to save the PDF
            progress_callback: Optional progress callback
            **kwargs: Additional parameters
            
        Returns:
            True if successful
            
        Raises:
            PDFDownloadError: If download fails
            ScholarError: If ethical usage not acknowledged
        """
        if not self.ethical_acknowledged:
            raise ScholarError(
                "Sci-Hub usage requires explicit ethical acknowledgment. "
                "Please set acknowledge_ethical_usage=True in configuration."
            )
            
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try each mirror
        for mirror in self.mirrors:
            try:
                logger.info(f"Trying Sci-Hub mirror: {mirror}")
                success = await self._download_from_mirror(
                    mirror, url, save_path, progress_callback
                )
                if success:
                    return True
            except Exception as e:
                logger.warning(f"Failed with mirror {mirror}: {e}")
                continue
                
        raise PDFDownloadError("All Sci-Hub mirrors failed")
        
    async def _download_from_mirror(
        self,
        mirror: str,
        identifier: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Download from a specific Sci-Hub mirror."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to Sci-Hub
                sci_hub_url = f"{mirror}/{identifier}"
                await page.goto(sci_hub_url, wait_until='domcontentloaded')
                
                # Wait for content to load
                await page.wait_for_timeout(2000)
                
                # Find PDF URL
                pdf_url = await self._extract_pdf_url(page, mirror)
                if not pdf_url:
                    raise PDFDownloadError("Could not find PDF URL on Sci-Hub page")
                    
                # Download PDF
                return await self._download_pdf(pdf_url, save_path, progress_callback)
                
            finally:
                await browser.close()
                
    async def _extract_pdf_url(self, page, mirror: str) -> Optional[str]:
        """Extract PDF URL from Sci-Hub page."""
        # Try different selectors
        selectors = [
            'iframe#pdf',
            'embed[type="application/pdf"]',
            'iframe[src*=".pdf"]',
            'a[onclick*="download"]',
            '#article > embed'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    src = await element.get_attribute('src')
                    if src:
                        # Make URL absolute
                        if src.startswith('//'):
                            return 'https:' + src
                        elif src.startswith('/'):
                            return mirror + src
                        else:
                            return src
            except Exception:
                continue
                
        # Try to find direct PDF link
        try:
            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                if href and '.pdf' in href:
                    if href.startswith('//'):
                        return 'https:' + href
                    elif href.startswith('/'):
                        return mirror + href
                    else:
                        return href
        except Exception:
            pass
            
        return None
        
    async def _download_pdf(
        self,
        pdf_url: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Download PDF from URL."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://sci-hub.se/'
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(pdf_url, headers=headers) as response:
                if response.status != 200:
                    raise PDFDownloadError(f"HTTP {response.status}")
                    
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded / total_size)
                            
        return await self.validate_pdf(save_path)
        
    async def validate_pdf(self, file_path: Path) -> bool:
        """Validate PDF file."""
        if not file_path.exists():
            return False
            
        # Check file size
        if file_path.stat().st_size < 1024:
            return False
            
        # Check PDF header
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                return header == b'%PDF-'
        except Exception:
            return False
            
    def get_priority(self) -> int:
        """Sci-Hub has low priority due to ethical considerations."""
        return 20

# EOF