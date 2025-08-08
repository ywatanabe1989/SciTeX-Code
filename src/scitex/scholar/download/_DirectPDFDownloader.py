#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 00:50:00 (assistant)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/_DirectPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/_DirectPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Direct PDF Downloader

This module downloads PDFs using pre-discovered URLs.
It doesn't search for URLs - it just downloads from provided URLs.
Uses the reliable request context method that bypasses Chrome's PDF viewer.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from playwright.async_api import Browser, BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)


class DirectPDFDownloader:
    """
    Direct PDF downloader that uses authenticated browser context.
    
    This downloader:
    1. Takes PDF URLs as input (no URL discovery)
    2. Uses authenticated browser context for access
    3. Downloads using request context (bypasses Chrome viewer)
    4. Validates downloaded PDFs
    5. Reports success/failure for each URL
    """
    
    def __init__(self, context: BrowserContext = None):
        """
        Initialize the Direct PDF Downloader.
        
        Args:
            context: Authenticated browser context (from BrowserManager)
        """
        self.context = context
        self.stats = {
            'total_attempts': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_bytes': 0
        }
    
    async def download_pdf(
        self,
        pdf_url: str,
        output_path: Path,
        timeout: int = 30000
    ) -> Dict:
        """
        Download a PDF from a URL.
        
        Args:
            pdf_url: Direct PDF URL to download
            output_path: Path to save the PDF
            timeout: Download timeout in milliseconds
            
        Returns:
            Dict with download results:
                - success: Whether download succeeded
                - path: Path to downloaded file (if successful)
                - size: File size in bytes
                - error: Error message (if failed)
                - method: Download method used
        """
        self.stats['total_attempts'] += 1
        
        result = {
            'url': pdf_url,
            'success': False,
            'path': None,
            'size': 0,
            'error': None,
            'method': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try primary method: Request context
        logger.info(f"Downloading PDF: {pdf_url}")
        pdf_content = await self._download_with_request_context(pdf_url, timeout)
        
        if pdf_content and self._validate_pdf(pdf_content):
            # Save PDF
            output_path.write_bytes(pdf_content)
            
            result['success'] = True
            result['path'] = str(output_path)
            result['size'] = len(pdf_content)
            result['method'] = 'request_context'
            
            self.stats['successful_downloads'] += 1
            self.stats['total_bytes'] += len(pdf_content)
            
            logger.success(f"✅ Downloaded PDF: {output_path.name} ({len(pdf_content):,} bytes)")
        else:
            # Try fallback method if primary fails
            pdf_content = await self._download_with_page_navigation(pdf_url, timeout)
            
            if pdf_content and self._validate_pdf(pdf_content):
                output_path.write_bytes(pdf_content)
                
                result['success'] = True
                result['path'] = str(output_path)
                result['size'] = len(pdf_content)
                result['method'] = 'page_navigation'
                
                self.stats['successful_downloads'] += 1
                self.stats['total_bytes'] += len(pdf_content)
                
                logger.success(f"✅ Downloaded PDF via navigation: {output_path.name}")
            else:
                result['error'] = 'Failed to download valid PDF'
                self.stats['failed_downloads'] += 1
                logger.error(f"❌ Failed to download: {pdf_url}")
        
        return result
    
    async def download_multiple_pdfs(
        self,
        pdf_urls: List[str],
        output_dir: Path,
        name_prefix: str = "document"
    ) -> List[Dict]:
        """
        Download multiple PDFs.
        
        Args:
            pdf_urls: List of PDF URLs to try
            output_dir: Directory to save PDFs
            name_prefix: Prefix for generated filenames
            
        Returns:
            List of download results
        """
        results = []
        
        for i, url in enumerate(pdf_urls, 1):
            output_path = output_dir / f"{name_prefix}_{i}.pdf"
            
            logger.info(f"Attempting download {i}/{len(pdf_urls)}")
            result = await self.download_pdf(url, output_path)
            results.append(result)
            
            # Stop on first success
            if result['success']:
                logger.success(f"Successfully downloaded from URL {i}")
                break
            
            # Brief pause between attempts
            if i < len(pdf_urls):
                await asyncio.sleep(2)
        
        return results
    
    async def download_with_fallback(
        self,
        urls: Dict[str, str],
        output_path: Path
    ) -> Dict:
        """
        Try downloading from multiple URL types with fallback.
        
        Args:
            urls: Dictionary of URL types (final_pdf_url, openurl_resolved_url, etc.)
            output_path: Path to save the PDF
            
        Returns:
            Download result
        """
        # Priority order for URLs
        url_priority = [
            'final_pdf_url',
            'openurl_resolved_url',
            'publisher_url',
            'doi_url'
        ]
        
        # Add .pdf to URLs if needed
        for url_type in url_priority:
            if url_type in urls and urls[url_type]:
                url = urls[url_type]
                
                # Try original URL
                logger.info(f"Trying {url_type}: {url}")
                result = await self.download_pdf(url, output_path)
                
                if result['success']:
                    result['url_type'] = url_type
                    return result
                
                # Try with .pdf extension if not present
                if not url.endswith('.pdf'):
                    pdf_url = url.rstrip('/') + '.pdf'
                    logger.info(f"Trying {url_type} with .pdf: {pdf_url}")
                    result = await self.download_pdf(pdf_url, output_path)
                    
                    if result['success']:
                        result['url_type'] = url_type + '_pdf'
                        return result
        
        # All attempts failed
        return {
            'success': False,
            'error': 'All URL types failed',
            'attempted_urls': [urls.get(t) for t in url_priority if urls.get(t)]
        }
    
    async def _download_with_request_context(
        self,
        pdf_url: str,
        timeout: int = 30000
    ) -> Optional[bytes]:
        """
        Download PDF using browser context's request API.
        This bypasses Chrome's PDF viewer.
        """
        if not self.context:
            logger.error("No browser context available")
            return None
        
        try:
            # Use the authenticated context's request object
            request_context = self.context.request
            
            # Make direct request for PDF
            response = await request_context.get(pdf_url, timeout=timeout)
            
            if response.status == 200:
                pdf_content = await response.body()
                
                if pdf_content and pdf_content.startswith(b'%PDF'):
                    return pdf_content
                else:
                    logger.debug(f"Response is not a PDF. First bytes: {pdf_content[:10] if pdf_content else 'None'}")
            else:
                logger.warning(f"Request failed with status: {response.status}")
                
        except asyncio.TimeoutError:
            logger.error(f"Download timeout after {timeout/1000}s")
        except Exception as e:
            logger.error(f"Request context download failed: {e}")
        
        return None
    
    async def _download_with_page_navigation(
        self,
        pdf_url: str,
        timeout: int = 30000
    ) -> Optional[bytes]:
        """
        Fallback method: Navigate to PDF and intercept response.
        """
        if not self.context:
            return None
        
        page = None
        try:
            page = await self.context.new_page()
            pdf_content = None
            
            async def capture_pdf(response):
                nonlocal pdf_content
                try:
                    if response.status == 200 and '.pdf' in response.url.lower():
                        body = await response.body()
                        if body and body.startswith(b'%PDF'):
                            pdf_content = body
                            logger.debug(f"Captured PDF: {len(body)} bytes")
                except:
                    pass
            
            page.on('response', capture_pdf)
            
            # Navigate to PDF URL
            await page.goto(pdf_url, wait_until='networkidle', timeout=timeout)
            
            # Wait a bit for response capture
            await asyncio.sleep(3)
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Page navigation download failed: {e}")
            return None
        finally:
            if page:
                await page.close()
    
    def _validate_pdf(self, content: bytes) -> bool:
        """
        Validate that content is a real PDF.
        
        Args:
            content: File content to validate
            
        Returns:
            True if valid PDF
        """
        if not content:
            return False
        
        # Check PDF header
        if not content.startswith(b'%PDF'):
            return False
        
        # Check minimum size (at least 10KB for a real paper)
        if len(content) < 10000:
            logger.warning(f"PDF too small: {len(content)} bytes")
            return False
        
        # Check for PDF structure markers
        pdf_markers = [b'/Type', b'/Page', b'/Contents']
        has_structure = any(marker in content[:50000] for marker in pdf_markers)
        
        if not has_structure:
            logger.warning("PDF lacks expected structure markers")
            return False
        
        return True
    
    def get_statistics(self) -> Dict:
        """Get download statistics."""
        stats = self.stats.copy()
        if stats['total_attempts'] > 0:
            stats['success_rate'] = stats['successful_downloads'] / stats['total_attempts']
        else:
            stats['success_rate'] = 0
        
        if stats['total_bytes'] > 0:
            stats['total_mb'] = stats['total_bytes'] / (1024 * 1024)
        
        return stats


async def download_pdf_simple(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path
) -> bool:
    """
    Simple function to download a PDF.
    
    Args:
        context: Authenticated browser context
        pdf_url: URL of the PDF
        output_path: Where to save the PDF
        
    Returns:
        True if successful
    """
    downloader = DirectPDFDownloader(context)
    result = await downloader.download_pdf(pdf_url, output_path)
    return result['success']


# EOF