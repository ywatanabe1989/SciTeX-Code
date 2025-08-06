#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 22:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/_ZenRowsDownloadStrategy.py
# ----------------------------------------
"""ZenRows-based download strategy for bypassing bot detection and CAPTCHAs.

This strategy uses the ZenRows API to download PDFs that are protected by:
- Bot detection systems (Cloudflare, PerimeterX, etc.)
- CAPTCHA challenges
- JavaScript-heavy sites
- Rate limiting

It can also transfer authentication cookies from OpenAthens or other auth providers.
"""

import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urljoin, urlparse

from scitex import logging
from ...errors import PDFDownloadError
from ._BaseDownloadStrategy import BaseDownloadStrategy

logger = logging.getLogger(__name__)


class ZenRowsDownloadStrategy(BaseDownloadStrategy):
    """Download strategy using ZenRows API for anti-bot bypass."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize ZenRows strategy.
        
        Args:
            api_key: ZenRows API key (uses env var if not provided)
        """
        super().__init__()
        self.api_key = api_key or os.environ.get(
            "ZENROWS_API_KEY",
            os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        )
        
        if not self.api_key:
            logger.warning("No ZenRows API key found - strategy will be disabled")
            
        # Session management for maintaining same IP
        self.session_id = None
        self.cookies: Dict[str, str] = {}
        
    def _generate_session_id(self) -> str:
        """Generate numeric session ID for ZenRows."""
        import random
        # ZenRows expects smaller session IDs (1-9999 based on error)
        return str(random.randint(1, 9999))
        
    async def can_download(self, url: str, metadata: Dict[str, Any]) -> bool:
        """Check if this strategy can download from the URL.
        
        ZenRows can handle any URL, but we prioritize it for:
        - Known problematic publishers (Elsevier, Springer, Wiley, etc.)
        - URLs that failed with other strategies
        - Sites with known bot protection
        """
        if not self.api_key:
            return False
            
        # Always available as a fallback
        return True
        
    async def download(
        self,
        url: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        session_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Download PDF using ZenRows API.
        
        Args:
            url: URL to download
            output_path: Where to save the PDF
            metadata: Paper metadata (title, authors, etc.)
            session_data: Authentication session data (cookies)
            
        Returns:
            Path to download PDF or None if failed
        """
        if not self.api_key:
            logger.error("ZenRows API key not configured")
            return None
            
        # Generate session ID if needed
        if not self.session_id:
            self.session_id = self._generate_session_id()
            logger.info(f"Created ZenRows session: {self.session_id}")
            
        # Build request parameters
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",  # Enable JavaScript rendering
            "premium_proxy": "true",  # Use premium proxies
            "session_id": self.session_id,  # Maintain same IP
            "wait": "5000"  # Wait 5 seconds for page to load
        }
        
        # Add custom headers if we have session cookies
        headers = {}
        if session_data and session_data.get("cookies"):
            # Merge session cookies with any existing cookies
            self.cookies.update(session_data["cookies"])
            
        if self.cookies:
            # Send cookies as HTTP headers
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            logger.info(f"Using {len(self.cookies)} cookies for authentication")
            
        try:
            async with aiohttp.ClientSession() as session:
                # Make request through ZenRows
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"ZenRows request failed: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error response: {error_text[:500]}")
                        logger.debug(f"Request URL: {url}")
                        logger.debug(f"Request params: {params}")
                        return None
                        
                    # Check content type
                    content_type = response.headers.get('Content-Type', '')
                    
                    # Update cookies from response
                    zr_cookies = response.headers.get('Zr-Cookies', '')
                    if zr_cookies:
                        new_cookies = self._parse_cookie_header(zr_cookies)
                        self.cookies.update(new_cookies)
                        logger.info(f"Updated cookies, total: {len(self.cookies)}")
                        
                    # Get final URL (after redirects)
                    final_url = response.headers.get('Zr-Final-Url', url)
                    logger.info(f"Final URL: {final_url}")
                    
                    # Check if it's a PDF
                    if 'application/pdf' in content_type:
                        # Direct PDF download
                        content = await response.read()
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_bytes(content)
                        logger.info(f"Downloaded PDF directly: {output_path}")
                        return output_path
                        
                    else:
                        # HTML response - need to look for PDF link
                        html_content = await response.text()
                        
                        # Try to find PDF link in the page
                        pdf_url = await self._find_pdf_url_async(html_content, final_url)
                        
                        if pdf_url:
                            logger.info(f"Found PDF URL: {pdf_url}")
                            # Download the PDF
                            return await self._download_pdf_async_url(pdf_url, output_path)
                        else:
                            logger.warning("No PDF link found in page")
                            # Save HTML for debugging
                            debug_path = output_path.with_suffix('.debug.html')
                            debug_path.write_text(html_content)
                            logger.debug(f"Saved debug HTML: {debug_path}")
                            return None
                            
        except Exception as e:
            logger.error(f"ZenRows download error: {e}")
            return None
            
    def _parse_cookie_header(self, cookie_header: str) -> Dict[str, str]:
        """Parse cookie header string into dictionary."""
        cookies = {}
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name.strip()] = value.strip()
        return cookies
        
    async def _find_pdf_url_async(self, html_content: str, base_url: str) -> Optional[str]:
        """Find PDF download URL in HTML content."""
        import re
        
        # First check meta tags (most reliable for academic publishers)
        meta_patterns = [
            r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"',
            r'<meta\s+property="citation_pdf_url"\s+content="([^"]+)"',
            r'<meta\s+name="dc.identifier"\s+content="([^"]+\.pdf[^"]*)"',
        ]
        
        for pattern in meta_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                pdf_url = matches[0]
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(base_url, pdf_url)
                logger.info(f"Found PDF URL in meta tag: {pdf_url}")
                return pdf_url
        
        # Common PDF link patterns
        pdf_patterns = [
            r'href="([^"]+\.pdf[^"]*)"',  # Direct .pdf links
            r'href="([^"]+/pdf/[^"]+)"',  # /pdf/ path
            r'href="([^"]+[?&]download=true[^"]*)"',  # Download parameter
            r'data-pdf-url="([^"]+)"',  # Data attribute
            r'window\.location\.href\s*=\s*["\']([^"\']+\.pdf[^"\']*)["\']',  # JavaScript redirect
            r'"pdfUrl"\s*:\s*"([^"]+)"',  # JSON data
            r'<a[^>]+class="[^"]*download[^"]*"[^>]+href="([^"]+)"',  # Download button
        ]
        
        for pattern in pdf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Convert relative URLs to absolute
                pdf_url = urljoin(base_url, match)
                if 'pdf' in pdf_url.lower() or 'download' in pdf_url.lower():
                    logger.info(f"Found PDF URL in content: {pdf_url}")
                    return pdf_url
                    
        return None
        
    async def _download_pdf_async_url(self, pdf_url: str, output_path: Path) -> Optional[Path]:
        """Download PDF from a specific URL using ZenRows."""
        # Use ZenRows again for the PDF URL
        params = {
            "url": pdf_url,
            "apikey": self.api_key,
            "premium_proxy": "true",
            "session_id": self.session_id
        }
        
        headers = {}
        if self.cookies:
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        content = await response.read()
                        
                        # Verify it's a PDF
                        if content.startswith(b'%PDF'):
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            output_path.write_bytes(content)
                            logger.info(f"Downloaded PDF: {output_path}")
                            return output_path
                        else:
                            logger.warning("Downloaded content is not a PDF")
                            return None
                    else:
                        logger.error(f"Failed to download PDF: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"PDF download error: {e}")
            return None
            
    def reset_session(self):
        """Reset ZenRows session (new IP and clear cookies)."""
        self.session_id = None
        self.cookies = {}
        logger.info("ZenRows session reset")