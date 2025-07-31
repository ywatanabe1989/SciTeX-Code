#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-31 23:55:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/_Crawl4AIDownloadStrategy.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/scholar/download/_Crawl4AIDownloadStrategy.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Crawl4AI-based download strategy for PDF retrieval with advanced anti-bot bypass."""

import asyncio
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import re

from scitex import logging
from scitex.errors import PDFDownloadError
from ._BaseDownloadStrategy import BaseDownloadStrategy

logger = logging.getLogger(__name__)

# Optional import - Crawl4AI might not be installed
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.debug("Crawl4AI not installed - strategy will be skipped")


class Crawl4AIDownloadStrategy(BaseDownloadStrategy):
    """Download strategy using Crawl4AI for advanced stealth and anti-bot bypass.
    
    Crawl4AI provides:
    - Built-in stealth mode to avoid bot detection
    - Persistent browser profiles for maintaining auth
    - JavaScript execution for dynamic content
    - Human-like behavior simulation
    - Multiple browser engine support
    
    This strategy is particularly effective for:
    - Sites with aggressive anti-bot measures
    - Dynamic JavaScript-rendered content
    - Multi-step authentication flows
    - Sites requiring persistent sessions
    """
    
    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        profile_name: str = "scitex_academic",
        use_proxy: bool = False,
        simulate_user: bool = True
    ):
        """Initialize Crawl4AI download strategy.
        
        Args:
            browser_type: Browser to use (chromium, firefox, webkit)
            headless: Run browser in headless mode
            profile_name: Browser profile name for persistent auth
            use_proxy: Use proxy if configured
            simulate_user: Simulate human-like behavior
        """
        super().__init__()
        self.browser_type = browser_type
        self.headless = headless
        self.profile_name = profile_name
        self.use_proxy = use_proxy
        self.simulate_user = simulate_user
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning(
                "Crawl4AI not installed. Install with: pip install crawl4ai[all]"
            )
    
    def can_handle(self, paper: Any) -> bool:
        """Check if this strategy can handle the paper."""
        if not CRAWL4AI_AVAILABLE:
            return False
        
        # Can handle any paper with DOI or URL
        return bool(paper.doi or getattr(paper, 'url', None))
    
    async def download_async(
        self,
        paper: Any,
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """Download PDF using Crawl4AI with stealth features."""
        if not CRAWL4AI_AVAILABLE:
            logger.error("Crawl4AI not installed")
            return None
        
        # Prepare output path
        safe_filename = self._sanitize_filename(
            paper.bibtex_key or f"{paper.first_author}_{paper.year}" or "unknown"
        )
        output_path = os.path.join(output_dir, f"{safe_filename}.pdf")
        
        # Skip if already exists
        if os.path.exists(output_path):
            logger.info(f"PDF already exists: {output_path}")
            if progress_callback:
                await progress_callback(
                    method="Crawl4AI",
                    status="exists",
                    path=output_path
                )
            return output_path
        
        # Configure browser
        browser_config = BrowserConfig(
            browser_type=self.browser_type,
            headless=self.headless,
            viewport_width=1920,
            viewport_height=1080,
            use_persistent_context=True,
            profile_name=self.profile_name,
            accept_languages=["en-US", "en"],
            ignore_https_errors=True,
            java_script_enabled=True,
            
            # Anti-detection settings
            extra_args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ] if self.headless else []
        )
        
        # Add proxy if configured
        if self.use_proxy and os.getenv("PROXY_URL"):
            browser_config.proxy = {
                "server": os.getenv("PROXY_URL"),
                "username": os.getenv("PROXY_USERNAME"),
                "password": os.getenv("PROXY_PASSWORD")
            }
        
        # Try different URL strategies
        urls_to_try = []
        
        # 1. OpenURL resolver (institutional access)
        if paper.doi:
            openurl_base = os.getenv(
                "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
                "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
            )
            openurl = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{paper.doi}&svc_id=fulltext"
            urls_to_try.append(("OpenURL", openurl))
        
        # 2. Direct DOI
        if paper.doi:
            urls_to_try.append(("DOI", f"https://doi.org/{paper.doi}"))
        
        # 3. Publisher URL if available
        if hasattr(paper, 'url') and paper.url:
            urls_to_try.append(("Publisher", paper.url))
        
        # Crawler configuration
        crawler_config = CrawlerRunConfig(
            # Content settings
            exclude_external_links=False,
            exclude_social_media_links=True,
            
            # Anti-bot bypass
            simulate_user=self.simulate_user,
            random_user_agent=True,
            
            # Wait strategies
            wait_until="networkidle",
            delay_before_return=3.0,
            
            # JavaScript to find PDF
            js_code="""
            // Check for PDF viewer
            const pdfEmbed = document.querySelector('embed[type="application/pdf"]');
            if (pdfEmbed) return pdfEmbed.src;
            
            const pdfIframe = document.querySelector('iframe[src*=".pdf"]');
            if (pdfIframe) return pdfIframe.src;
            
            // Look for download links
            const links = document.querySelectorAll('a');
            for (const link of links) {
                const href = link.href || '';
                const text = link.textContent.toLowerCase();
                if (href.endsWith('.pdf') || 
                    (href.includes('pdf') && (text.includes('download') || text.includes('full text')))) {
                    return href;
                }
            }
            
            return null;
            """,
            
            # Headers for academic sites
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Referer": "https://scholar.google.com/"
            }
        )
        
        for method, url in urls_to_try:
            logger.info(f"Trying {method}: {url}")
            
            if progress_callback:
                await progress_callback(
                    method=f"Crawl4AI-{method}",
                    status="downloading"
                )
            
            try:
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    # Crawl the page
                    result = await crawler.arun(
                        url=url,
                        config=crawler_config
                    )
                    
                    if result.success:
                        # Check if we found a PDF URL
                        if result.js_result:
                            pdf_url = result.js_result
                            logger.info(f"Found PDF URL: {pdf_url}")
                            
                            # Download the PDF
                            pdf_result = await crawler.arun(
                                url=pdf_url,
                                config=CrawlerRunConfig(
                                    bypass_cache=True,
                                    screenshot=False,
                                    js_code=None
                                )
                            )
                            
                            if pdf_result.success and pdf_result.raw_content:
                                # Verify it's a PDF
                                if pdf_result.raw_content.startswith(b'%PDF'):
                                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                                    with open(output_path, 'wb') as f:
                                        f.write(pdf_result.raw_content)
                                    
                                    logger.success(f"Downloaded via Crawl4AI: {output_path}")
                                    
                                    if progress_callback:
                                        await progress_callback(
                                            method=f"Crawl4AI-{method}",
                                            status="success",
                                            path=output_path
                                        )
                                    
                                    return output_path
                        
                        # Try to extract PDF URLs from HTML
                        if result.html:
                            pdf_urls = re.findall(
                                r'href="([^"]*\.pdf[^"]*)"',
                                result.html,
                                re.IGNORECASE
                            )
                            
                            if pdf_urls:
                                logger.info(f"Found {len(pdf_urls)} PDF links")
                                # Could implement logic to try downloading these
                                # For now, just log them
                                for pdf_url in pdf_urls[:3]:
                                    logger.debug(f"  PDF link: {pdf_url}")
            
            except Exception as e:
                logger.error(f"Crawl4AI error with {method}: {e}")
                continue
        
        # All attempts failed
        if progress_callback:
            await progress_callback(
                method="Crawl4AI",
                status="failed"
            )
        
        return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem."""
        # Remove/replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename