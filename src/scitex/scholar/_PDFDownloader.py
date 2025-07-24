#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 19:24:57 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_PDFDownloader.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_PDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Union

"""
PDF downloader for SciTeX Scholar.

This module provides comprehensive PDF download functionality:
1. Direct publisher patterns (fastest)
2. Zotero translator support (most reliable)
3. Sci-Hub fallback (for paywalled content)
4. Web scraping with Playwright (last resort)
"""

import asyncio
import hashlib
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import quote, urljoin, urlparse

import aiohttp
from playwright.async_api import async_playwright

from ..errors import PDFDownloadError, ScholarError, warn_performance
from ._ethical_usage import ETHICAL_USAGE_MESSAGE, check_ethical_usage
from ._ProgressTracker import create_progress_tracker
from ._utils import normalize_filename
from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner
from ._LeanLibraryAuthenticator import LeanLibraryAuthenticator
# BrowserAutomation removed - using direct playwright calls
# OpenAthensURLTransformer removed - not needed for basic functionality

logger = logging.getLogger(__name__)


class PDFDownloader:
    """
    PDF downloader with multiple strategies.

    Download priority:
    1. Check local cache
    2. Try direct publisher patterns
    3. Use Zotero translators if available
    4. Try Sci-Hub (with ethical acknowledgment)
    5. Use Playwright for JavaScript sites

    Features:
    - Concurrent downloads with progress tracking
    - Smart caching and deduplication
    - Automatic retry with exponential backoff
    - Publisher-specific optimizations
    - Ethical usage acknowledgment for Sci-Hub
    """

    # Sci-Hub mirrors (updated regularly)
    SCIHUB_MIRRORS = [
        "https://sci-hub.se",
        "https://sci-hub.st",
        "https://sci-hub.ru",
        "https://sci-hub.ren",
        "https://sci-hub.tw",
        "https://sci-hub.ee",
    ]

    # Class-level authenticator cache for multiprocessing
    _openathens_authenticator_cache = {}

    def __init__(
        self,
        download_dir: Optional[Path] = None,
        use_translators: bool = True,
        use_scihub: bool = True,
        use_playwright: bool = True,
        use_openathens: bool = False,
        openathens_config: Optional[Dict[str, Any]] = None,
        use_lean_library: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
        max_concurrent: int = 3,
        acknowledge_ethical_usage: Optional[bool] = None,
        debug_mode: bool = False,
    ):
        """
        Initialize PDF downloader.

        Args:
            download_dir: Default download directory
            use_translators: Enable Zotero translator support
            use_scihub: Enable Sci-Hub fallback
            use_playwright: Enable Playwright for JS sites
            use_openathens: Enable OpenAthens authentication
            openathens_config: OpenAthens configuration dict
            timeout: Download timeout in seconds
            max_retries: Maximum retry attempts
            max_concurrent: Maximum concurrent downloads
            acknowledge_ethical_usage: Acknowledge ethical usage for Sci-Hub
        """
        self.download_dir = Path(download_dir or "./pdfs")
        self.use_translators = use_translators
        self.use_scihub = use_scihub
        self.use_playwright = use_playwright
        self.use_openathens = use_openathens
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        self.debug_mode = debug_mode

        # Initialize components
        if use_translators:
            try:
                self.zotero_translator_runner = ZoteroTranslatorRunner()
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Zotero translator runner: {e}"
                )
                self.zotero_translator_runner = None
                self.use_translators = False
        else:
            self.zotero_translator_runner = None

        # Initialize OpenAthens authenticator with singleton pattern for multiprocessing
        # TODO: Future authentication methods (EZProxy, Lean Library, Shibboleth)
        # will be added here following the same pattern
        self.openathens_authenticator = None
        if use_openathens and openathens_config:
            try:
                from ._OpenAthensAuthenticator import OpenAthensAuthenticator

                # Use email as cache key (or 'default' if no email)
                cache_key = openathens_config.get("email", "default")

                # Check if we already have an authenticator for this email
                if cache_key in PDFDownloader._openathens_authenticator_cache:
                    self.openathens_authenticator = (
                        PDFDownloader._openathens_authenticator_cache[
                            cache_key
                        ]
                    )
                    logger.debug(
                        f"Reusing OpenAthens authenticator for {cache_key}"
                    )
                else:
                    # Create new authenticator
                    self.openathens_authenticator = OpenAthensAuthenticator(
                        email=openathens_config.get("email"),
                        timeout=timeout,
                        debug_mode=openathens_config.get("debug_mode", self.debug_mode),
                    )
                    # Initialize will be done on first use
                    PDFDownloader._openathens_authenticator_cache[
                        cache_key
                    ] = self.openathens_authenticator
                    logger.debug(
                        f"Created new OpenAthens authenticator for {cache_key}"
                    )
                
                # Initialize URL transformer for OpenAthens
                # URL transformer removed - not needed
                self.url_transformer = None

            except Exception as e:
                logger.warning(f"Failed to initialize OpenAthens: {e}")
                self.use_openathens = False
                self.url_transformer = None
        else:
            self.url_transformer = None

        # Lean Library browser extension support
        self.use_lean_library = use_lean_library
        self.lean_library_authenticator = None
        if self.use_lean_library:
            try:
                self.lean_library_authenticator = LeanLibraryAuthenticator()
                logger.info("Lean Library authenticator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Lean Library: {e}")
                self.use_lean_library = False

        # Track downloads to avoid duplicates
        self._active_downloads: Set[str] = set()
        self._download_cache: Dict[str, Path] = {}
        self._download_methods: Dict[str, str] = (
            {}
        )  # Track which method succeeded

        # Ethical usage for Sci-Hub
        self._ethical_acknowledged = acknowledge_ethical_usage

    async def download_pdf_async(
        self,
        identifier: str,
        output_dir: Optional[Path] = None,
        filename: Optional[str] = None,
        force: bool = False,
        progress_callback: Optional[callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        """
        Download PDF using best available method.

        Args:
            identifier: DOI, URL, or other identifier
            output_dir: Output directory (uses default if None)
            filename: Custom filename (auto-generated if None)
            force: Force re-download even if exists
            metadata: Additional metadata for filename generation

        Returns:
            Path to downloaded PDF or None
        """
        # Normalize identifier
        identifier = identifier.strip()

        # Check if already downloading
        if identifier in self._active_downloads:
            logger.info(f"Already downloading: {identifier}")
            # Wait for existing download
            while identifier in self._active_downloads:
                await asyncio.sleep(0.5)
            return self._download_cache.get(identifier)

        # Mark as active
        self._active_downloads.add(identifier)

        try:
            # Determine output path
            output_dir = output_dir or self.download_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            if not filename:
                filename = self._generate_filename(identifier, metadata)
            output_path = output_dir / filename

            # Check cache
            if (
                not force
                and output_path.exists()
                and output_path.stat().st_size > 1000
            ):
                logger.info(f"PDF already exists: {output_path}")
                self._download_cache[identifier] = output_path
                return output_path

            # Try download strategies in order
            pdf_path = None

            # Strategy 1: Direct download if URL
            if identifier.startswith("http"):
                pdf_path = await self._try_direct_url_download_async(
                    identifier, output_path
                )

            # Strategy 2: DOI resolution and patterns
            elif self._is_doi(identifier):
                pdf_path = await self._download_from_doi_async(
                    identifier, output_path, progress_callback
                )

            # Strategy 3: Try as URL even without http
            else:
                # Maybe it's a partial URL
                for prefix in ["https://", "http://"]:
                    test_url = prefix + identifier
                    if await self._is_valid_url_async(test_url):
                        pdf_path = await self._try_direct_url_download_async(
                            test_url, output_path
                        )
                        if pdf_path:
                            break

            # Cache result
            if pdf_path:
                self._download_cache[identifier] = pdf_path

            return pdf_path

        finally:
            # Remove from active downloads
            self._active_downloads.discard(identifier)

    async def _download_from_doi_async(
        self,
        doi: str,
        output_path: Path,
        progress_callback: Optional[callable] = None,
    ) -> Optional[Path]:
        """Download PDF from DOI using multiple strategies with authentication as a layer."""
        # Resolve DOI to URL
        resolved_url = await self._resolve_doi_async(doi)
        if not resolved_url:
            logger.error(f"Failed to resolve DOI: {doi}")
            return None

        logger.info(f"Resolved {doi} to {resolved_url}")
        
        # Transform URL for OpenAthens if needed
        url = resolved_url
        logger.debug(f"Checking URL transformation: use_openathens={self.use_openathens}, has_transformer={self.url_transformer is not None}")
        
        if self.use_openathens and self.url_transformer:
            needs_transform = self.url_transformer.needs_transformation(url)
            logger.info(f"URL {url} needs transformation: {needs_transform}")
            
            if needs_transform:
                transformed_url = self.url_transformer.transform_url_for_openathens(url, method='redirector')
                logger.info(f"Transformed URL: {resolved_url} → {transformed_url}")
                url = transformed_url
            else:
                logger.warning(f"URL doesn't need transformation according to transformer: {url}")
        else:
            logger.warning(f"URL transformation skipped: use_openathens={self.use_openathens}, url_transformer={self.url_transformer}")

        # Step 1: Get authenticated session (if available)
        auth_session = await self._get_authenticated_session_async()
        if auth_session:
            provider = auth_session.get('context', {}).get('provider', 'Unknown')
            logger.info(f"Using authenticated session from {provider}")
        else:
            logger.info("No authentication available, proceeding without auth")

        # Step 2: Try discovery strategies WITH authentication
        # If we have OpenAthens authentication, use it as the primary strategy
        if auth_session and self.use_openathens and self.openathens_authenticator:
            strategies = [
                ("Lean Library", self._try_lean_library_async),  # Primary - browser extension
                ("OpenAthens", self._try_openathens_async),  # Use OpenAthens authenticator's method
                ("Direct patterns", self._try_direct_patterns_async),  # Fallback
                ("Sci-Hub", self._try_scihub_async),  # Last resort
            ]
        else:
            strategies = [
                ("Lean Library", self._try_lean_library_async),  # Primary - browser extension
                ("Zotero translators", self._try_zotero_translator_async),  # Most reliable for non-auth
                ("Direct patterns", self._try_direct_patterns_async),
                ("Playwright", self._try_playwright_async),
                ("Sci-Hub", self._try_scihub_async),  # Last resort
            ]

        for name, strategy in strategies:
            if not self._should_use_strategy(name):
                continue

            logger.info(f"Trying {name} for {doi}")

            # Report progress - trying method
            if progress_callback:
                progress_callback(None, None, doi, method=name, status=None)

            try:
                # Pass auth_session to strategies that can use it
                if name in ["Zotero translators", "Direct patterns", "Playwright", "OpenAthens"]:
                    pdf_path = await strategy(doi, url, output_path, auth_session)
                else:
                    # Sci-Hub doesn't need auth
                    pdf_path = await strategy(doi, url, output_path)
                    
                if pdf_path:
                    logger.info(f"Success with {name}: {pdf_path}")
                    self._download_methods[doi] = name  # Track successful method
                    return pdf_path
            except Exception as e:
                logger.debug(f"{name} failed for {doi}: {e}")

        logger.error(f"All strategies failed for {doi}")
        return None
    
    async def _get_authenticated_session_async(self) -> Optional[Dict[str, Any]]:
        """
        Get authenticated session from available authentication providers.
        
        Returns session data with cookies/headers if authenticated,
        None otherwise.
        """
        # Check OpenAthens if available
        if self.use_openathens and self.openathens_authenticator:
            try:
                # Reload session cache in case another process authenticated
                await self.openathens_authenticator._load_session_cache()
                
                if await self.openathens_authenticator.is_authenticated_async():
                    # Get cookies from authenticator
                    cookies = []
                    if hasattr(self.openathens_authenticator, '_full_cookies') and self.openathens_authenticator._full_cookies:
                        cookies = self.openathens_authenticator._full_cookies
                    elif hasattr(self.openathens_authenticator, '_cookies') and self.openathens_authenticator._cookies:
                        # Convert simple cookies to full format
                        cookies = [
                            {
                                'name': name,
                                'value': value,
                                'domain': '.openathens.net',
                                'path': '/'
                            }
                            for name, value in self.openathens_authenticator._cookies.items()
                        ]
                    
                    return {
                        'cookies': cookies,
                        'headers': {},
                        'context': {
                            'provider': 'OpenAthens',
                            'email': getattr(self.openathens_authenticator, 'email', None)
                        }
                    }
            except Exception as e:
                logger.debug(f"Failed to get OpenAthens session: {e}")
        
        # Future: Check other authentication providers here
        # if self.use_ezproxy and self.ezproxy_authenticator:
        #     ...
        
        return None

    def _should_use_strategy(self, strategy: str) -> bool:
        """Check if strategy should be used."""
        if strategy == "OpenAthens":
            return (
                self.use_openathens
                and self.openathens_authenticator is not None
            )
        elif strategy == "Zotero translators":
            return (
                self.use_translators
                and self.zotero_translator_runner is not None
            )
        elif strategy == "Sci-Hub":
            return self.use_scihub
        elif strategy == "Playwright":
            return self.use_playwright
        return True

    async def _try_direct_patterns_async(
        self, doi: str, url: str, output_path: Path, auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Try direct download using publisher patterns with optional authentication."""
        pdf_urls = self._get_publisher_pdf_urls(url, doi)

        for pdf_url in pdf_urls:
            logger.debug(f"Trying direct download: {pdf_url}")
            # If we have auth session, use it for download
            if auth_session and auth_session.get('cookies'):
                if await self._download_file_with_auth_async(pdf_url, output_path, auth_session, referer=url):
                    return output_path
            else:
                if await self._download_file_async(pdf_url, output_path, referer=url):
                    return output_path

        return None

    async def _try_lean_library_async(
        self, identifier: str, url: str, output_path: Path
    ) -> Optional[Path]:
        """Try downloading using Lean Library browser extension."""
        if not self.lean_library_authenticator:
            return None
            
        try:
            logger.info("Attempting download with Lean Library...")
            
            # Check if Lean Library is available
            if not await self.lean_library_authenticator.is_available_async():
                logger.warning("Lean Library not available (no browser profile found)")
                return None
            
            # Try to download with extension
            result = await self.lean_library_authenticator.download_with_extension_async(
                url, output_path, timeout=self.timeout * 1000
            )
            
            if result:
                logger.info(f"Successfully downloaded with Lean Library: {output_path}")
                return output_path
            else:
                logger.warning("Lean Library could not access the PDF")
                return None
                
        except Exception as e:
            logger.error(f"Lean Library download failed: {e}")
            return None

    async def _try_openathens_async(
        self, doi: str, url: str, output_path: Path, auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Try download using OpenAthens authenticator's download_with_auth method."""
        if not self.openathens_authenticator:
            return None
            
        try:
            logger.info(f"Using OpenAthens authenticated download for {url}")
            # Use the authenticator's download method which handles publisher-specific flows
            result = await self.openathens_authenticator.download_with_auth_async(
                url=url,
                output_path=output_path
            )
            return result
        except Exception as e:
            logger.error(f"OpenAthens download failed: {e}")
            return None

    async def _try_zotero_translator_async(
        self, doi: str, url: str, output_path: Path, auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Try download using Zotero translator with optional authentication."""
        if not self.zotero_translator_runner:
            return None

        # Find translator
        translator = self.zotero_translator_runner.find_translator_for_url(url)
        if not translator:
            return None
            
        logger.info(f"Using Zotero translator: {translator['label']}")

        # If we have auth session, run translator with authenticated browser
        if auth_session and auth_session.get('cookies'):
            return await self._run_translator_with_auth_async(translator, url, output_path, auth_session)
        else:
            # No auth - use standard translator
            pdf_urls = await self.zotero_translator_runner.extract_pdf_urls(url)
            for pdf_url in pdf_urls:
                logger.info(f"Trying translator PDF: {pdf_url}")
                if await self._download_file_async(pdf_url, output_path, referer=url):
                    return output_path

        return None

    async def _try_scihub_async(
        self, doi: str, url: str, output_path: Path
    ) -> Optional[Path]:
        """Try download using Sci-Hub."""
        # Check ethical acknowledgment
        if not self._ethical_acknowledged:
            self._ethical_acknowledged = check_ethical_usage(
                self._ethical_acknowledged
            )
            if not self._ethical_acknowledged:
                logger.info(
                    "Sci-Hub download skipped (ethical usage not acknowledged)"
                )
                return None

        # Try each Sci-Hub mirror
        for mirror in self.SCIHUB_MIRRORS:
            try:
                # Sci-Hub accepts DOIs directly
                scihub_url = f"{mirror}/{doi}"

                # Get the PDF URL from Sci-Hub
                pdf_url = await self._get_scihub_pdf_url_async(scihub_url)
                if pdf_url:
                    logger.info(f"Found PDF on Sci-Hub: {mirror}")
                    if await self._download_file_async(pdf_url, output_path):
                        return output_path

            except Exception as e:
                logger.debug(f"Sci-Hub mirror {mirror} failed: {e}")
                continue

        return None

    async def _get_scihub_pdf_url_async(self, scihub_url: str) -> Optional[str]:
        """Extract PDF URL from Sci-Hub page."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    scihub_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={"User-Agent": "Mozilla/5.0"},
                ) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()

                    # Look for PDF embed/iframe
                    patterns = [
                        r'<iframe.*?src=["\']([^"\']*\.pdf[^"\']*)["\']',
                        r'<embed.*?src=["\']([^"\']*\.pdf[^"\']*)["\']',
                        r'<iframe.*?src=["\']([^"\']*)["\'].*?pdf',
                        r'window\.location\.href\s*=\s*["\']([^"\']*\.pdf[^"\']*)["\']',
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, html, re.IGNORECASE)
                        if match:
                            pdf_url = match.group(1)
                            # Make absolute URL
                            if not pdf_url.startswith("http"):
                                if pdf_url.startswith("//"):
                                    pdf_url = "https:" + pdf_url
                                else:
                                    pdf_url = urljoin(scihub_url, pdf_url)
                            return pdf_url

        except Exception as e:
            logger.debug(f"Failed to get Sci-Hub PDF URL: {e}")

        return None

    async def _handle_cookie_consent_async(self, page) -> None:
        """Handle cookie consent popups that block content."""
        try:
            # Common cookie consent button selectors
            cookie_selectors = [
                # Nature specific
                'button:has-text("Accept cookies")',
                'button:has-text("Accept Cookies")',
                # Generic patterns
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
                'button:has-text("OK")',
                'button:has-text("Got it")',
                # ID/class based
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button[class*="consent"]',
                'button[class*="cookie"] button[class*="accept"]',
                # Links
                'a:has-text("Accept")',
                'a:has-text("Accept cookies")',
            ]
            
            for selector in cookie_selectors:
                try:
                    # Wait up to 1 second for each selector
                    button = await page.wait_for_selector(selector, timeout=1000)
                    if button and await button.is_visible():
                        logger.info(f"Found cookie consent button: {selector}")
                        await button.click()
                        # Wait a bit for the popup to disappear
                        await page.wait_for_timeout(1000)
                        logger.info("Accepted cookie consent")
                        return
                except:
                    # Selector not found, try next
                    continue
                    
        except Exception as e:
            logger.debug(f"Cookie consent handling error (non-critical): {e}")

    async def _try_playwright_async(
        self, doi: str, url: str, output_path: Path, auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Try download using Playwright for JS-heavy sites with optional authentication."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=not self.debug_mode)
            context = await browser.new_context()
            
            # Set up context with user agent
            await context.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Add auth cookies if available
            if auth_session and auth_session.get('cookies'):
                await context.add_cookies(auth_session['cookies'])
                logger.debug(f"Added {len(auth_session['cookies'])} auth cookies to Playwright")
            
            page = await context.new_page()
            
            # Simple page setup - just wait for it to be ready
            await page.wait_for_load_state('domcontentloaded')

            try:
                # Log navigation
                logger.info(f"Navigating to: {url}")
                
                # Navigate and wait for content
                response = await page.goto(url, wait_until="domcontentloaded")
                
                # Log any redirects
                current_url = page.url
                if current_url != url:
                    logger.info(f"Redirected to: {current_url}")
                
                # Simple wait for page to stabilize
                await page.wait_for_timeout(3000)
                
                # Handle cookie consent popups
                try:
                    await self._handle_cookie_consent_async(page)
                    
                    # Wait a bit more after handling cookies for content to load
                    await page.wait_for_timeout(2000)
                except Exception as e:
                    logger.warning(f"Error during popup handling: {e}")
                    # Continue anyway - the page might still work
                
                # Check if current page is already a PDF
                if response:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        logger.info(f"Current page is a PDF: {current_url}")
                        pdf_content = await response.body()
                        if pdf_content and pdf_content.startswith(b'%PDF'):
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            output_path.write_bytes(pdf_content)
                            logger.info(f"Saved PDF from current page to {output_path}")
                            return output_path
                
                # Also check if we're in a PDF viewer (URL often contains .pdf)
                final_url = page.url
                if '.pdf' in final_url or '/pdf/' in final_url:
                    logger.info(f"URL suggests PDF content: {final_url}")
                    # Try to get the PDF content from the page
                    try:
                        # Wait a bit more for PDF to load
                        await page.wait_for_timeout(2000)
                        
                        # For embedded PDF viewers, we might need to find the actual PDF URL
                        pdf_frame = await page.evaluate('''
                            () => {
                                // Check for PDF in iframe
                                const iframe = document.querySelector('iframe[src*=".pdf"], iframe[src*="/pdf/"]');
                                if (iframe) return iframe.src;
                                
                                // Check for embed/object tags
                                const embed = document.querySelector('embed[src*=".pdf"], object[data*=".pdf"]');
                                if (embed) return embed.src || embed.data;
                                
                                return null;
                            }
                        ''')
                        
                        if pdf_frame:
                            logger.info(f"Found embedded PDF: {pdf_frame}")
                            # Download the embedded PDF
                            if await self._download_file_async(pdf_frame, output_path, referer=final_url):
                                return output_path
                    except Exception as e:
                        logger.debug(f"Failed to extract embedded PDF: {e}")

                # Look for PDF links (enhanced for authenticated pages)
                pdf_urls = await page.evaluate(
                    """
                    () => {
                        const urls = new Set();

                        // Standard selectors
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            if (href && (href.includes('.pdf') ||
                                        href.includes('/pdf/') ||
                                        a.textContent.match(/PDF|Download/i))) {
                                urls.add(href);
                            }
                        });
                        
                        // Enhanced selectors for authenticated pages
                        const authSelectors = [
                            'a[data-track-action="download pdf"]',
                            '.pdf-download-btn',
                            'a.pdf-download',
                            'a:has-text("Access PDF")',
                            'button:has-text("Download PDF")',
                            // Nature specific
                            'a[data-track-action="download-pdf"]',
                            'a.c-pdf-download__link',
                            'a[href*="/articles/"][href$=".pdf"]',
                            'a[data-article-pdf]',
                            // More generic patterns
                            'a[aria-label*="Download PDF"]',
                            'a[title*="Download PDF"]'
                        ];
                        
                        authSelectors.forEach(selector => {
                            try {
                                document.querySelectorAll(selector).forEach(el => {
                                    if (el.href) urls.add(el.href);
                                });
                            } catch (e) {}
                        });

                        // Check iframes
                        document.querySelectorAll('iframe').forEach(iframe => {
                            if (iframe.src && iframe.src.includes('pdf')) {
                                urls.add(iframe.src);
                            }
                        });

                        return Array.from(urls);
                    }
                """
                )

                # Log found PDF URLs
                logger.info(f"Found {len(pdf_urls)} potential PDF URLs")
                for url in pdf_urls[:3]:  # Log first 3
                    logger.debug(f"  - {url}")
                
                # Try downloading PDFs
                for pdf_url in pdf_urls:
                    if auth_session and auth_session.get('cookies'):
                        if await self._download_file_with_auth_async(pdf_url, output_path, auth_session, referer=url):
                            return output_path
                    else:
                        if await self._download_file_async(pdf_url, output_path, referer=url):
                            return output_path

            finally:
                await browser.close()

        return None

    def _get_publisher_pdf_urls(self, url: str, doi: str) -> List[str]:
        """Generate PDF URLs based on publisher patterns."""
        domain = urlparse(url).netloc
        pdf_urls = []

        # Comprehensive publisher patterns
        patterns = {
            # Nature Publishing Group
            "nature.com": [
                lambda: url.replace("/articles/", "/articles/") + ".pdf",
                lambda: re.sub(r"(/articles/[^/]+).*", r"\1.pdf", url),
            ],
            # Science/AAAS
            "science.org": [
                lambda: url.replace("/doi/", "/doi/pdf/"),
                lambda: url.replace("/content/", "/content/") + ".full.pdf",
            ],
            # Cell Press/Elsevier
            "cell.com": [
                lambda: url.replace("/fulltext/", "/pdf/"),
                lambda: url.replace("/article/", "/action/showPdf?pii="),
            ],
            "sciencedirect.com": [
                lambda: self._sciencedirect_pdf_url(url),
            ],
            # Springer
            "springer.com": [
                lambda: url.replace("/article/", "/content/pdf/") + ".pdf",
                lambda: url.replace("/chapter/", "/content/pdf/") + ".pdf",
            ],
            "link.springer.com": [
                lambda: url.replace("/article/", "/content/pdf/") + ".pdf",
                lambda: url.replace("/chapter/", "/content/pdf/") + ".pdf",
            ],
            # Wiley
            "wiley.com": [
                lambda: url.replace("/abs/", "/pdf/"),
                lambda: url.replace("/full/", "/pdfdirect/"),
                lambda: url.replace("/doi/", "/doi/pdf/"),
                lambda: re.sub(
                    r"/doi/([^/]+)/([^/]+)/(.+)", r"/doi/pdf/\1/\2/\3", url
                ),
            ],
            # IEEE
            "ieee.org": [
                lambda: self._ieee_pdf_url(url),
                lambda: url.replace(
                    "/document/", "/stamp/stamp.jsp?tp=&arnumber="
                ),
            ],
            # ACS Publications
            "acs.org": [
                lambda: url.replace("/doi/", "/doi/pdf/"),
                lambda: url.replace("/abs/", "/pdf/"),
            ],
            # RSC Publishing
            "rsc.org": [
                lambda: url.replace("/en/content/", "/en/content/articlepdf/"),
                lambda: url + "/pdf",
            ],
            # IOP Science
            "iop.org": [
                lambda: url.replace("/article/", "/article/") + "/pdf",
                lambda: url.replace("/meta", "/pdf"),
            ],
            # Taylor & Francis
            "tandfonline.com": [
                lambda: url.replace("/doi/full/", "/doi/pdf/"),
                lambda: url.replace("/doi/abs/", "/doi/pdf/"),
            ],
            # PLOS
            "plos.org": [
                lambda: self._plos_pdf_url(url),
                lambda: url.replace("/article?", "/article/file?")
                + "&type=printable",
            ],
            # PNAS
            "pnas.org": [
                lambda: url.replace("/content/", "/content/") + ".full.pdf",
                lambda: url.replace("/doi/", "/doi/pdf/"),
            ],
            # Oxford Academic
            "oup.com": [
                lambda: url.replace("/article/", "/article-pdf/"),
                lambda: url + "/pdf",
            ],
            "academic.oup.com": [
                lambda: url.replace("/article/", "/article-pdf/"),
            ],
            # BMJ
            "bmj.com": [
                lambda: url.replace("/content/", "/content/") + ".full.pdf",
                lambda: url + ".full.pdf",
            ],
            # Frontiers
            "frontiersin.org": [
                lambda: url.replace("/articles/", "/articles/") + "/pdf",
                lambda: url.replace("/full", "/pdf"),
            ],
            # MDPI
            "mdpi.com": [
                lambda: url.replace("/htm", "/pdf"),
                lambda: url + "/pdf",
            ],
            # arXiv
            "arxiv.org": [
                lambda: url.replace("/abs/", "/pdf/") + ".pdf",
                lambda: url.replace("arxiv.org", "export.arxiv.org").replace(
                    "/abs/", "/pdf/"
                )
                + ".pdf",
            ],
            # bioRxiv/medRxiv
            "biorxiv.org": [
                lambda: url + ".full.pdf",
                lambda: url.replace("/content/", "/content/") + ".full.pdf",
            ],
            "medrxiv.org": [
                lambda: url + ".full.pdf",
                lambda: url.replace("/content/", "/content/") + ".full.pdf",
            ],
            # SSRN
            "ssrn.com": [
                lambda: self._ssrn_pdf_url(url),
            ],
            # JSTOR
            "jstor.org": [
                lambda: url.replace("/stable/", "/stable/pdf/") + ".pdf",
            ],
            # Project MUSE
            "muse.jhu.edu": [
                lambda: url.replace("/article/", "/article/") + "/pdf",
            ],
            # APS Physics
            "aps.org": [
                lambda: url.replace("/abstract/", "/pdf/"),
            ],
            "physics.aps.org": [
                lambda: url.replace("/abstract/", "/pdf/"),
            ],
        }

        # Try all matching patterns
        for domain_pattern, url_generators in patterns.items():
            if domain_pattern in domain:
                for generator in url_generators:
                    try:
                        pdf_url = generator()
                        if pdf_url:
                            pdf_urls.append(pdf_url)
                    except:
                        continue

        # Add generic DOI resolver
        pdf_urls.append(f"https://doi.org/{doi}?format=pdf")

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in pdf_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def _sciencedirect_pdf_url(self, url: str) -> Optional[str]:
        """Generate ScienceDirect PDF URL."""
        # Extract PII (Publication Item Identifier)
        pii_match = re.search(r"/pii/([A-Z0-9]+)", url)
        if pii_match:
            pii = pii_match.group(1)
            return f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"

        # Try article pattern
        article_match = re.search(r"/article/abs/pii/([A-Z0-9]+)", url)
        if article_match:
            pii = article_match.group(1)
            return f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"

        return None

    def _ieee_pdf_url(self, url: str) -> Optional[str]:
        """Generate IEEE PDF URL."""
        # Extract document number
        doc_match = re.search(r"/document/(\d+)", url)
        if doc_match:
            doc_num = doc_match.group(1)
            return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_num}"

        # Try arnumber pattern
        arn_match = re.search(r"arnumber=(\d+)", url)
        if arn_match:
            doc_num = arn_match.group(1)
            return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_num}"

        return None

    def _plos_pdf_url(self, url: str) -> Optional[str]:
        """Generate PLOS PDF URL."""
        # Extract article ID
        id_match = re.search(r"id=([^&]+)", url)
        if id_match:
            article_id = id_match.group(1)
            return f"https://journals.plos.org/plosone/article/file?id={article_id}&type=printable"

        # Try DOI pattern
        doi_match = re.search(r"journal\.p[^.]+\.(\d+)", url)
        if doi_match:
            return (
                url.replace("/article?", "/article/file?") + "&type=printable"
            )

        return None

    def _ssrn_pdf_url(self, url: str) -> Optional[str]:
        """Generate SSRN PDF URL."""
        # Extract abstract ID
        abstract_match = re.search(r"abstract=(\d+)", url)
        if abstract_match:
            abstract_id = abstract_match.group(1)
            return f"https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{abstract_id}_code.pdf?abstractid={abstract_id}"

        return None

    async def _resolve_doi_async(self, doi: str) -> Optional[str]:
        """Resolve DOI to publisher URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; SciTeX/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            }

            # Clean DOI
            doi = doi.strip()
            if not doi.startswith("10."):
                doi = "10." + doi.split("10.")[-1]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://doi.org/{doi}",
                    headers=headers,
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return str(response.url)

        except Exception as e:
            logger.error(f"DOI resolution failed for {doi}: {e}")
            return None

    async def _download_file_async(
        self, url: str, output_path: Path, referer: Optional[str] = None
    ) -> bool:
        """Download file with retry logic."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/pdf,*/*",
        }

        if referer:
            headers["Referer"] = referer

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        allow_redirects=True,
                    ) as response:
                        if response.status == 200:
                            content = await response.read()

                            # Verify it's a PDF
                            if content.startswith(b"%PDF"):
                                output_path.parent.mkdir(
                                    parents=True, exist_ok=True
                                )
                                output_path.write_bytes(content)
                                logger.info(f"Downloaded PDF to {output_path}")
                                return True
                            else:
                                logger.debug(f"Content is not PDF from {url}")

                        elif response.status == 404:
                            logger.debug(f"404 Not Found: {url}")
                            return False
                        else:
                            logger.debug(f"HTTP {response.status} from {url}")

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except Exception as e:
                logger.debug(f"Download error on attempt {attempt + 1}: {e}")

            # Exponential backoff
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2**attempt)

        return False

    async def _try_direct_url_download_async(
        self, url: str, output_path: Path
    ) -> Optional[Path]:
        """Try downloading directly from URL."""
        # Check if it's already a PDF URL
        if ".pdf" in url.lower() or "/pdf/" in url:
            if await self._download_file_async(url, output_path):
                return output_path

        # Try appending .pdf
        if not url.endswith(".pdf"):
            pdf_url = url + ".pdf"
            if await self._download_file_async(pdf_url, output_path):
                return output_path

        return None

    def _is_doi(self, identifier: str) -> bool:
        """Check if identifier is a DOI."""
        # DOI regex pattern
        doi_pattern = r"^10\.\d{4,}/[-._;()/:\w]+$"
        return bool(re.match(doi_pattern, identifier))

    async def _is_valid_url_async(self, url: str) -> bool:
        """Check if URL is valid and accessible."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    def _generate_filename(
        self, identifier: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate descriptive filename."""
        if metadata:
            parts = []

            # Add first author
            if "authors" in metadata and metadata["authors"]:
                first_author = metadata["authors"][0].split(",")[0].strip()
                first_author = re.sub(r"[^\w\s-]", "", first_author)
                parts.append(first_author.replace(" ", "_"))

            # Add year
            if "year" in metadata:
                parts.append(str(metadata["year"]))

            # Add short title
            if "title" in metadata:
                title_words = metadata["title"].split()[:5]
                short_title = "_".join(title_words)
                short_title = re.sub(r"[^\w\s-]", "", short_title)
                parts.append(short_title)

            if parts:
                filename = "_".join(parts) + ".pdf"
                # Limit length
                if len(filename) > 100:
                    filename = filename[:96] + ".pdf"
                return filename

        # Fallback: use identifier
        clean_id = re.sub(r"[^\w.-]", "_", identifier)
        return clean_id + ".pdf"

    async def batch_download_async(
        self,
        identifiers: List[str],
        output_dir: Optional[Path] = None,
        organize_by_year: bool = False,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        progress_callback: Optional[callable] = None,
        show_progress: bool = True,
        return_detailed: bool = False,
    ) -> Union[Dict[str, Optional[Path]], Dict[str, Dict[str, Any]]]:
        """
        Download multiple PDFs concurrently.

        Args:
            identifiers: List of DOIs/URLs
            output_dir: Output directory
            organize_by_year: Create year subdirectories
            metadata_list: Metadata for each identifier
            progress_callback: Callback(completed, total, identifier)
            return_detailed: If True, return detailed results with download methods

        Returns:
            If return_detailed is False: Dictionary mapping identifier to downloaded path
            If return_detailed is True: Dictionary mapping identifier to {path, method}
        """
        if len(identifiers) > 10:
            warn_performance(
                "PDF Download",
                f"Downloading {len(identifiers)} PDFs. This may take time.",
            )

        output_dir = output_dir or self.download_dir
        results = {}
        completed = 0
        total = len(identifiers)

        # Create progress tracker
        if progress_callback is None and show_progress:
            progress_tracker = create_progress_tracker(
                total, show_progress=True
            )

            # Create a new callback that uses the tracker
            def _progress_callback(
                completed, total, identifier, method=None, status=None
            ):
                progress_tracker.update(
                    identifier=identifier,
                    method=method,
                    status=status,
                    completed=completed,
                )

            progress_callback = _progress_callback
        elif not show_progress:
            progress_callback = None

        # Prepare download tasks
        tasks = []
        for i, identifier in enumerate(identifiers):
            metadata = metadata_list[i] if metadata_list else None

            # Determine output directory
            if organize_by_year and metadata and "year" in metadata:
                item_dir = output_dir / str(metadata["year"])
            else:
                item_dir = output_dir

            tasks.append(
                {
                    "identifier": identifier,
                    "output_dir": item_dir,
                    "metadata": metadata,
                }
            )

        # Download with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def download_with_limit_async(
            task: Dict,
        ) -> Tuple[str, Optional[Path]]:
            nonlocal completed

            async with semaphore:
                path = await self.download_pdf_async(
                    identifier=task["identifier"],
                    output_dir=task["output_dir"],
                    metadata=task["metadata"],
                    progress_callback=progress_callback,
                )

                completed += 1
                # Report success or failure
                if progress_callback:
                    status = "success" if path else "failed"
                    progress_callback(
                        completed, total, task["identifier"], status=status
                    )

                return task["identifier"], path

        # Execute downloads
        download_results = await asyncio.gather(
            *[download_with_limit_async(task) for task in tasks],
            return_exceptions=True,
        )

        # Process results
        for result in download_results:
            if isinstance(result, Exception):
                logger.error(f"Download failed: {result}")
            else:
                identifier, path = result
                results[identifier] = path

        # Summary
        success_count = sum(1 for p in results.values() if p is not None)
        logger.info(f"Downloaded {success_count}/{total} PDFs successfully")

        # Finish progress tracking
        if "progress_tracker" in locals():
            progress_tracker.finish()

        # Return detailed results if requested
        if return_detailed:
            detailed_results = {}
            for identifier, path in results.items():
                if path:
                    detailed_results[identifier] = {
                        "path": path,
                        "method": self._download_methods.get(
                            identifier, "Unknown"
                        ),
                    }
                else:
                    detailed_results[identifier] = None
            return detailed_results
        else:
            return results
    
    async def _download_file_with_auth_async(
        self,
        url: str,
        output_path: Path,
        auth_session: Dict[str, Any],
        referer: Optional[str] = None
    ) -> bool:
        """Download file using authenticated session."""
        # If we have cookies, use Playwright to maintain session
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=not self.debug_mode)
            context = await browser.new_context()
            
            # Set up context with user agent
            await context.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Add auth cookies
            if auth_session.get('cookies'):
                await context.add_cookies(auth_session['cookies'])
            
            try:
                page = await context.new_page()
                
                # Simple page setup - just wait for it to be ready
                await page.wait_for_load_state('domcontentloaded')
                
                if referer:
                    await page.set_extra_http_headers({'Referer': referer})
                
                # Navigate to download URL
                response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Simple wait for page to stabilize
                await page.wait_for_timeout(1000)
                
                if response and response.status == 200:
                    # Check if it's a PDF
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        # Get content
                        content = await response.body()
                        if content.startswith(b'%PDF'):
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            output_path.write_bytes(content)
                            logger.info(f"Downloaded PDF with auth to {output_path}")
                            return True
                
                # Try download button if not direct PDF
                try:
                    # Wait for download
                    async with page.expect_download(timeout=15000) as download_info:
                        # Click download button if present
                        await page.click('a:has-text("Download PDF")', timeout=5000)
                    
                    download = await download_info.value
                    await download.save_as(output_path)
                    return True
                except:
                    pass
                    
            except Exception as e:
                logger.debug(f"Auth download failed: {e}")
            finally:
                await browser.close()
                
        return False
    
    async def _run_translator_with_auth_async(
        self,
        translator: Dict,
        url: str,
        output_path: Path,
        auth_session: Dict[str, Any]
    ) -> Optional[Path]:
        """Run Zotero translator with authenticated browser context."""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not getattr(self, 'debug_mode', False),
                args=['--disable-blink-features=AutomationControlled']
            )
            
            try:
                context = await browser.new_context()
                
                # Set up context with user agent
                await context.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Add authentication cookies
                await context.add_cookies(auth_session['cookies'])
                logger.info(f"Added {len(auth_session['cookies'])} auth cookies to Zotero translator")
                
                page = await context.new_page()
                
                # Simple page setup - just wait for it to be ready
                await page.wait_for_load_state('domcontentloaded')
                
                # Inject Zotero shim
                await page.add_init_script(self.zotero_translator_runner._zotero_shim)
                
                # Navigate with auth
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Simple wait for page to stabilize
                await page.wait_for_timeout(2000)
                
                # Run translator
                translator_code = translator['content']
                result = await page.evaluate('''
                    async (translatorCode) => {
                        try {
                            window._zoteroItems = [];
                            eval(translatorCode);
                            
                            if (typeof detectWeb === 'function') {
                                const itemType = detectWeb(document, window.location.href);
                                if (itemType && typeof doWeb === 'function') {
                                    await doWeb(document, window.location.href);
                                    await new Promise(resolve => setTimeout(resolve, 2000));
                                }
                            }
                            
                            return {
                                success: true,
                                items: window._zoteroItems
                            };
                        } catch (error) {
                            return {
                                success: false,
                                error: error.toString()
                            };
                        }
                    }
                ''', translator_code)
                
                if not result.get('success'):
                    logger.debug(f"Translator execution failed: {result.get('error')}")
                    return None
                
                # Extract PDF URLs from translator results
                pdf_urls = []
                for item in result.get('items', []):
                    for attachment in item.get('attachments', []):
                        if attachment.get('mimeType') == 'application/pdf' and attachment.get('url'):
                            pdf_urls.append(attachment['url'])
                
                # Also look for PDF links on authenticated page
                auth_pdf_urls = await page.evaluate('''
                    () => {
                        const urls = new Set();
                        
                        // Enhanced selectors for authenticated pages
                        const authSelectors = [
                            'a[data-track-action="download pdf"]',
                            '.pdf-download-btn',
                            'a.pdf-download',
                            '.c-pdf-download__link',
                            'a[data-article-pdf]',
                            'a:has-text("Download PDF")',
                            'a:has-text("Access PDF")',
                            'button:has-text("Download PDF")',
                            'a[href*=".pdf"][class*="download"]'
                        ];
                        
                        authSelectors.forEach(selector => {
                            try {
                                document.querySelectorAll(selector).forEach(el => {
                                    const href = el.href || el.getAttribute('data-href');
                                    if (href && !href.includes('javascript:')) {
                                        urls.add(href);
                                    }
                                });
                            } catch (e) {}
                        });
                        
                        return Array.from(urls);
                    }
                ''')
                
                pdf_urls.extend(auth_pdf_urls)
                
                # Remove duplicates
                seen = set()
                unique_urls = []
                for url in pdf_urls:
                    if url not in seen:
                        seen.add(url)
                        unique_urls.append(url)
                
                logger.info(f"Zotero translator found {len(unique_urls)} PDF URLs on authenticated page")
                
                # Try downloading PDFs with auth
                for pdf_url in unique_urls:
                    logger.info(f"Trying Zotero-discovered PDF: {pdf_url}")
                    if await self._download_file_with_auth_async(
                        pdf_url, output_path, auth_session, referer=url
                    ):
                        return output_path
                        
            finally:
                await browser.close()
        
        return None


# Convenience functions


async def download_pdf_async(
    identifier: str,
    output_dir: Optional[Path] = None,
    use_scihub: bool = True,
    acknowledge_ethical_usage: Optional[bool] = None,
) -> Optional[Path]:
    """
    Simple function to download a single PDF.

    Args:
        identifier: DOI or URL
        output_dir: Output directory
        use_scihub: Enable Sci-Hub fallback
        acknowledge_ethical_usage: Acknowledge ethical usage

    Returns:
        Path to downloaded PDF or None
    """
    downloader = PDFDownloader(
        use_scihub=use_scihub,
        acknowledge_ethical_usage=acknowledge_ethical_usage,
    )
    return await downloader.download_pdf_async(identifier, output_dir)


async def download_pdfs_async(
    identifiers: List[str],
    output_dir: Optional[Path] = None,
    max_concurrent: int = 3,
    use_scihub: bool = True,
    acknowledge_ethical_usage: Optional[bool] = None,
    progress_callback: Optional[callable] = None,
) -> Dict[str, Optional[Path]]:
    """
    Download multiple PDFs concurrently.

    Args:
        identifiers: List of DOIs/URLs
        output_dir: Output directory
        max_concurrent: Maximum concurrent downloads
        use_scihub: Enable Sci-Hub fallback
        acknowledge_ethical_usage: Acknowledge ethical usage
        progress_callback: Optional progress callback

    Returns:
        Dictionary mapping identifier to path
    """
    downloader = PDFDownloader(
        max_concurrent=max_concurrent,
        use_scihub=use_scihub,
        acknowledge_ethical_usage=acknowledge_ethical_usage,
    )
    return await downloader.batch_download_async(
        identifiers, output_dir, progress_callback=progress_callback
    )


if __name__ == "__main__":
    # Example usage
    import sys

    async def test_unified_downloader_async():
        # Test identifiers
        test_cases = [
            # DOIs
            "10.1038/s41586-021-03819-2",  # Nature
            "10.1126/science.abg5298",  # Science
            "10.1016/j.cell.2021.07.015",  # Cell
            "10.1103/PhysRevLett.127.067401",  # APS
            "10.1021/acs.nanolett.1c02400",  # ACS
            # Direct URLs
            "https://arxiv.org/abs/2103.14030",
            "https://www.biorxiv.org/content/10.1101/2021.07.15.452479v1",
            # Paywalled (will try Sci-Hub)
            "10.1038/s41586-020-2649-2",
        ]

        if len(sys.argv) > 1:
            test_cases = [sys.argv[1]]

        output_dir = Path("./test_unified_pdfs")
        output_dir.mkdir(exist_ok=True)

        print("Testing PDF Downloader")
        print("=" * 50)

        # Test single download
        if len(test_cases) == 1:
            identifier = test_cases[0]
            print(f"\nDownloading: {identifier}")

            path = await download_pdf(
                identifier,
                output_dir,
                use_scihub=True,
                acknowledge_ethical_usage=True,
            )

            if path:
                print(f"✓ Success: {path}")
                print(f"  Size: {path.stat().st_size / 1024:.1f} KB")
            else:
                print(f"✗ Failed to download {identifier}")

        else:
            # Test batch download
            print(f"\nBatch downloading {len(test_cases)} PDFs...")

            def progress(completed, total, identifier):
                print(f"Progress: {completed}/{total} - {identifier}")

            results = await download_pdfs(
                test_cases,
                output_dir,
                max_concurrent=2,
                use_scihub=True,
                acknowledge_ethical_usage=True,
                progress_callback=progress,
            )

            print("\n\nResults:")
            print("-" * 50)

            for identifier, path in results.items():
                if path:
                    size_kb = path.stat().st_size / 1024
                    print(f"✓ {identifier}")
                    print(f"  → {path.name} ({size_kb:.1f} KB)")
                else:
                    print(f"✗ {identifier} - Failed")

            # Summary
            success = sum(1 for p in results.values() if p)
            print(
                f"\nSuccess rate: {success}/{len(test_cases)} ({success/len(test_cases)*100:.0f}%)"
            )

    asyncio.run(test_unified_downloader())

# EOF
