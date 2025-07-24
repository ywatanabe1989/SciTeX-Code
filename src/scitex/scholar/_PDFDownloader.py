#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 08:50:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_PDFDownloader.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_PDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import quote, urljoin, urlparse

import aiohttp
import requests
from playwright.async_api import async_playwright

from ..errors import PDFDownloadError, ScholarError, warn_performance
from ._ethical_usage import check_ethical_usage, ETHICAL_USAGE_MESSAGE
from ._utils import normalize_filename
from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner

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
    
    def __init__(
        self,
        download_dir: Optional[Path] = None,
        use_translators: bool = True,
        use_scihub: bool = True,
        use_playwright: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
        max_concurrent: int = 3,
        acknowledge_ethical_usage: Optional[bool] = None,
    ):
        """
        Initialize PDF downloader.
        
        Args:
            download_dir: Default download directory
            use_translators: Enable Zotero translator support
            use_scihub: Enable Sci-Hub fallback
            use_playwright: Enable Playwright for JS sites
            timeout: Download timeout in seconds
            max_retries: Maximum retry attempts
            max_concurrent: Maximum concurrent downloads
            acknowledge_ethical_usage: Acknowledge ethical usage for Sci-Hub
        """
        self.download_dir = Path(download_dir or "./pdfs")
        self.use_translators = use_translators
        self.use_scihub = use_scihub
        self.use_playwright = use_playwright
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        
        # Initialize components
        if use_translators:
            try:
                self.zotero_translator_runner = ZoteroTranslatorRunner()
            except Exception as e:
                logger.warning(f"Failed to initialize Zotero translator runner: {e}")
                self.zotero_translator_runner = None
                self.use_translators = False
        else:
            self.zotero_translator_runner = None
            
        # Track downloads to avoid duplicates
        self._active_downloads: Set[str] = set()
        self._download_cache: Dict[str, Path] = {}
        
        # Ethical usage for Sci-Hub
        self._ethical_acknowledged = acknowledge_ethical_usage
        
    async def download_pdf(
        self,
        identifier: str,
        output_dir: Optional[Path] = None,
        filename: Optional[str] = None,
        force: bool = False,
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
            if not force and output_path.exists() and output_path.stat().st_size > 1000:
                logger.info(f"PDF already exists: {output_path}")
                self._download_cache[identifier] = output_path
                return output_path
                
            # Try download strategies in order
            pdf_path = None
            
            # Strategy 1: Direct download if URL
            if identifier.startswith('http'):
                pdf_path = await self._try_direct_url_download(
                    identifier, output_path
                )
                
            # Strategy 2: DOI resolution and patterns
            elif self._is_doi(identifier):
                pdf_path = await self._download_from_doi(
                    identifier, output_path
                )
                
            # Strategy 3: Try as URL even without http
            else:
                # Maybe it's a partial URL
                for prefix in ['https://', 'http://']:
                    test_url = prefix + identifier
                    if await self._is_valid_url(test_url):
                        pdf_path = await self._try_direct_url_download(
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
            
    async def _download_from_doi(
        self,
        doi: str,
        output_path: Path
    ) -> Optional[Path]:
        """Download PDF from DOI using multiple strategies."""
        # Resolve DOI to URL
        resolved_url = await self._resolve_doi(doi)
        if not resolved_url:
            logger.error(f"Failed to resolve DOI: {doi}")
            return None
            
        logger.info(f"Resolved {doi} to {resolved_url}")
        
        # Try strategies in order
        strategies = [
            ("Direct patterns", self._try_direct_patterns),
            ("Zotero translators", self._try_zotero_translator),
            ("Sci-Hub", self._try_scihub),
            ("Playwright", self._try_playwright),
        ]
        
        for name, strategy in strategies:
            if not self._should_use_strategy(name):
                continue
                
            logger.info(f"Trying {name} for {doi}")
            
            try:
                pdf_path = await strategy(doi, resolved_url, output_path)
                if pdf_path:
                    logger.info(f"Success with {name}: {pdf_path}")
                    return pdf_path
            except Exception as e:
                logger.debug(f"{name} failed for {doi}: {e}")
                
        logger.error(f"All strategies failed for {doi}")
        return None
        
    def _should_use_strategy(self, strategy: str) -> bool:
        """Check if strategy should be used."""
        if strategy == "Zotero translators":
            return self.use_translators and self.zotero_translator_runner is not None
        elif strategy == "Sci-Hub":
            return self.use_scihub
        elif strategy == "Playwright":
            return self.use_playwright
        return True
        
    async def _try_direct_patterns(
        self,
        doi: str,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """Try direct download using publisher patterns."""
        pdf_urls = self._get_publisher_pdf_urls(url, doi)
        
        for pdf_url in pdf_urls:
            logger.debug(f"Trying direct download: {pdf_url}")
            if await self._download_file(pdf_url, output_path, referer=url):
                return output_path
                
        return None
        
    async def _try_zotero_translator(
        self,
        doi: str,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """Try download using Zotero translator."""
        if not self.zotero_translator_runner:
            return None
            
        # Find and run translator
        translator = self.zotero_translator_runner.find_translator_for_url(url)
        if not translator:
            return None
            
        # Extract PDF URLs using translator
        pdf_urls = await self.zotero_translator_runner.extract_pdf_urls(url)
        
        for pdf_url in pdf_urls:
            logger.info(f"Trying translator PDF: {pdf_url}")
            if await self._download_file(pdf_url, output_path, referer=url):
                return output_path
                
        return None
        
    async def _try_scihub(
        self,
        doi: str,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """Try download using Sci-Hub."""
        # Check ethical acknowledgment
        if not self._ethical_acknowledged:
            self._ethical_acknowledged = check_ethical_usage(
                self._ethical_acknowledged
            )
            if not self._ethical_acknowledged:
                logger.info("Sci-Hub download skipped (ethical usage not acknowledged)")
                return None
                
        # Try each Sci-Hub mirror
        for mirror in self.SCIHUB_MIRRORS:
            try:
                # Sci-Hub accepts DOIs directly
                scihub_url = f"{mirror}/{doi}"
                
                # Get the PDF URL from Sci-Hub
                pdf_url = await self._get_scihub_pdf_url(scihub_url)
                if pdf_url:
                    logger.info(f"Found PDF on Sci-Hub: {mirror}")
                    if await self._download_file(pdf_url, output_path):
                        return output_path
                        
            except Exception as e:
                logger.debug(f"Sci-Hub mirror {mirror} failed: {e}")
                continue
                
        return None
        
    async def _get_scihub_pdf_url(self, scihub_url: str) -> Optional[str]:
        """Extract PDF URL from Sci-Hub page."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    scihub_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={'User-Agent': 'Mozilla/5.0'}
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
                            if not pdf_url.startswith('http'):
                                if pdf_url.startswith('//'):
                                    pdf_url = 'https:' + pdf_url
                                else:
                                    pdf_url = urljoin(scihub_url, pdf_url)
                            return pdf_url
                            
        except Exception as e:
            logger.debug(f"Failed to get Sci-Hub PDF URL: {e}")
            
        return None
        
    async def _try_playwright(
        self,
        doi: str,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """Try download using Playwright for JS-heavy sites."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate and wait for content
                await page.goto(url, wait_until='networkidle')
                await page.wait_for_timeout(3000)
                
                # Look for PDF links
                pdf_urls = await page.evaluate('''
                    () => {
                        const urls = new Set();
                        
                        // Check all links
                        document.querySelectorAll('a').forEach(a => {
                            const href = a.href;
                            if (href && (href.includes('.pdf') || 
                                        href.includes('/pdf/') ||
                                        a.textContent.match(/PDF|Download/i))) {
                                urls.add(href);
                            }
                        });
                        
                        // Check iframes
                        document.querySelectorAll('iframe').forEach(iframe => {
                            if (iframe.src && iframe.src.includes('pdf')) {
                                urls.add(iframe.src);
                            }
                        });
                        
                        return Array.from(urls);
                    }
                ''')
                
                # Try downloading PDFs
                for pdf_url in pdf_urls:
                    if await self._download_file(pdf_url, output_path, referer=url):
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
            'nature.com': [
                lambda: url.replace('/articles/', '/articles/') + '.pdf',
                lambda: re.sub(r'(/articles/[^/]+).*', r'\1.pdf', url),
            ],
            
            # Science/AAAS
            'science.org': [
                lambda: url.replace('/doi/', '/doi/pdf/'),
                lambda: url.replace('/content/', '/content/') + '.full.pdf',
            ],
            
            # Cell Press/Elsevier
            'cell.com': [
                lambda: url.replace('/fulltext/', '/pdf/'),
                lambda: url.replace('/article/', '/action/showPdf?pii='),
            ],
            'sciencedirect.com': [
                lambda: self._sciencedirect_pdf_url(url),
            ],
            
            # Springer
            'springer.com': [
                lambda: url.replace('/article/', '/content/pdf/') + '.pdf',
                lambda: url.replace('/chapter/', '/content/pdf/') + '.pdf',
            ],
            'link.springer.com': [
                lambda: url.replace('/article/', '/content/pdf/') + '.pdf',
                lambda: url.replace('/chapter/', '/content/pdf/') + '.pdf',
            ],
            
            # Wiley
            'wiley.com': [
                lambda: url.replace('/abs/', '/pdf/'),
                lambda: url.replace('/full/', '/pdfdirect/'),
                lambda: url.replace('/doi/', '/doi/pdf/'),
                lambda: re.sub(r'/doi/([^/]+)/([^/]+)/(.+)', r'/doi/pdf/\1/\2/\3', url),
            ],
            
            # IEEE
            'ieee.org': [
                lambda: self._ieee_pdf_url(url),
                lambda: url.replace('/document/', '/stamp/stamp.jsp?tp=&arnumber='),
            ],
            
            # ACS Publications
            'acs.org': [
                lambda: url.replace('/doi/', '/doi/pdf/'),
                lambda: url.replace('/abs/', '/pdf/'),
            ],
            
            # RSC Publishing
            'rsc.org': [
                lambda: url.replace('/en/content/', '/en/content/articlepdf/'),
                lambda: url + '/pdf',
            ],
            
            # IOP Science
            'iop.org': [
                lambda: url.replace('/article/', '/article/') + '/pdf',
                lambda: url.replace('/meta', '/pdf'),
            ],
            
            # Taylor & Francis
            'tandfonline.com': [
                lambda: url.replace('/doi/full/', '/doi/pdf/'),
                lambda: url.replace('/doi/abs/', '/doi/pdf/'),
            ],
            
            # PLOS
            'plos.org': [
                lambda: self._plos_pdf_url(url),
                lambda: url.replace('/article?', '/article/file?') + '&type=printable',
            ],
            
            # PNAS
            'pnas.org': [
                lambda: url.replace('/content/', '/content/') + '.full.pdf',
                lambda: url.replace('/doi/', '/doi/pdf/'),
            ],
            
            # Oxford Academic
            'oup.com': [
                lambda: url.replace('/article/', '/article-pdf/'),
                lambda: url + '/pdf',
            ],
            'academic.oup.com': [
                lambda: url.replace('/article/', '/article-pdf/'),
            ],
            
            # BMJ
            'bmj.com': [
                lambda: url.replace('/content/', '/content/') + '.full.pdf',
                lambda: url + '.full.pdf',
            ],
            
            # Frontiers
            'frontiersin.org': [
                lambda: url.replace('/articles/', '/articles/') + '/pdf',
                lambda: url.replace('/full', '/pdf'),
            ],
            
            # MDPI
            'mdpi.com': [
                lambda: url.replace('/htm', '/pdf'),
                lambda: url + '/pdf',
            ],
            
            # arXiv
            'arxiv.org': [
                lambda: url.replace('/abs/', '/pdf/') + '.pdf',
                lambda: url.replace('arxiv.org', 'export.arxiv.org').replace('/abs/', '/pdf/') + '.pdf',
            ],
            
            # bioRxiv/medRxiv
            'biorxiv.org': [
                lambda: url + '.full.pdf',
                lambda: url.replace('/content/', '/content/') + '.full.pdf',
            ],
            'medrxiv.org': [
                lambda: url + '.full.pdf',
                lambda: url.replace('/content/', '/content/') + '.full.pdf',
            ],
            
            # SSRN
            'ssrn.com': [
                lambda: self._ssrn_pdf_url(url),
            ],
            
            # JSTOR
            'jstor.org': [
                lambda: url.replace('/stable/', '/stable/pdf/') + '.pdf',
            ],
            
            # Project MUSE
            'muse.jhu.edu': [
                lambda: url.replace('/article/', '/article/') + '/pdf',
            ],
            
            # APS Physics
            'aps.org': [
                lambda: url.replace('/abstract/', '/pdf/'),
            ],
            'physics.aps.org': [
                lambda: url.replace('/abstract/', '/pdf/'),
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
        pii_match = re.search(r'/pii/([A-Z0-9]+)', url)
        if pii_match:
            pii = pii_match.group(1)
            return f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
            
        # Try article pattern
        article_match = re.search(r'/article/abs/pii/([A-Z0-9]+)', url)
        if article_match:
            pii = article_match.group(1)
            return f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
            
        return None
        
    def _ieee_pdf_url(self, url: str) -> Optional[str]:
        """Generate IEEE PDF URL."""
        # Extract document number
        doc_match = re.search(r'/document/(\d+)', url)
        if doc_match:
            doc_num = doc_match.group(1)
            return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_num}"
            
        # Try arnumber pattern
        arn_match = re.search(r'arnumber=(\d+)', url)
        if arn_match:
            doc_num = arn_match.group(1)
            return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_num}"
            
        return None
        
    def _plos_pdf_url(self, url: str) -> Optional[str]:
        """Generate PLOS PDF URL."""
        # Extract article ID
        id_match = re.search(r'id=([^&]+)', url)
        if id_match:
            article_id = id_match.group(1)
            return f"https://journals.plos.org/plosone/article/file?id={article_id}&type=printable"
            
        # Try DOI pattern
        doi_match = re.search(r'journal\.p[^.]+\.(\d+)', url)
        if doi_match:
            return url.replace('/article?', '/article/file?') + '&type=printable'
            
        return None
        
    def _ssrn_pdf_url(self, url: str) -> Optional[str]:
        """Generate SSRN PDF URL."""
        # Extract abstract ID
        abstract_match = re.search(r'abstract=(\d+)', url)
        if abstract_match:
            abstract_id = abstract_match.group(1)
            return f"https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{abstract_id}_code.pdf?abstractid={abstract_id}"
            
        return None
        
    async def _resolve_doi(self, doi: str) -> Optional[str]:
        """Resolve DOI to publisher URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; SciTeX/1.0)',
                'Accept': 'text/html,application/xhtml+xml',
            }
            
            # Clean DOI
            doi = doi.strip()
            if not doi.startswith('10.'):
                doi = '10.' + doi.split('10.')[-1]
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://doi.org/{doi}",
                    headers=headers,
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return str(response.url)
                    
        except Exception as e:
            logger.error(f"DOI resolution failed for {doi}: {e}")
            return None
            
    async def _download_file(
        self,
        url: str,
        output_path: Path,
        referer: Optional[str] = None
    ) -> bool:
        """Download file with retry logic."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*',
        }
        
        if referer:
            headers['Referer'] = referer
            
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        allow_redirects=True
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # Verify it's a PDF
                            if content.startswith(b'%PDF'):
                                output_path.parent.mkdir(parents=True, exist_ok=True)
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
                await asyncio.sleep(2 ** attempt)
                
        return False
        
    async def _try_direct_url_download(
        self,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """Try downloading directly from URL."""
        # Check if it's already a PDF URL
        if '.pdf' in url.lower() or '/pdf/' in url:
            if await self._download_file(url, output_path):
                return output_path
                
        # Try appending .pdf
        if not url.endswith('.pdf'):
            pdf_url = url + '.pdf'
            if await self._download_file(pdf_url, output_path):
                return output_path
                
        return None
        
    def _is_doi(self, identifier: str) -> bool:
        """Check if identifier is a DOI."""
        # DOI regex pattern
        doi_pattern = r'^10\.\d{4,}/[-._;()/:\w]+$'
        return bool(re.match(doi_pattern, identifier))
        
    async def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
            
    def _generate_filename(
        self,
        identifier: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate descriptive filename."""
        if metadata:
            parts = []
            
            # Add first author
            if 'authors' in metadata and metadata['authors']:
                first_author = metadata['authors'][0].split(',')[0].strip()
                first_author = re.sub(r'[^\w\s-]', '', first_author)
                parts.append(first_author.replace(' ', '_'))
                
            # Add year
            if 'year' in metadata:
                parts.append(str(metadata['year']))
                
            # Add short title
            if 'title' in metadata:
                title_words = metadata['title'].split()[:5]
                short_title = '_'.join(title_words)
                short_title = re.sub(r'[^\w\s-]', '', short_title)
                parts.append(short_title)
                
            if parts:
                filename = '_'.join(parts) + '.pdf'
                # Limit length
                if len(filename) > 100:
                    filename = filename[:96] + '.pdf'
                return filename
                
        # Fallback: use identifier
        clean_id = re.sub(r'[^\w.-]', '_', identifier)
        return clean_id + '.pdf'
        
    async def batch_download(
        self,
        identifiers: List[str],
        output_dir: Optional[Path] = None,
        organize_by_year: bool = False,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Optional[Path]]:
        """
        Download multiple PDFs concurrently.
        
        Args:
            identifiers: List of DOIs/URLs
            output_dir: Output directory
            organize_by_year: Create year subdirectories
            metadata_list: Metadata for each identifier
            progress_callback: Callback(completed, total, identifier)
            
        Returns:
            Dictionary mapping identifier to downloaded path
        """
        if len(identifiers) > 10:
            warn_performance(
                "PDF Download",
                f"Downloading {len(identifiers)} PDFs. This may take time."
            )
            
        output_dir = output_dir or self.download_dir
        results = {}
        completed = 0
        total = len(identifiers)
        
        # Prepare download tasks
        tasks = []
        for i, identifier in enumerate(identifiers):
            metadata = metadata_list[i] if metadata_list else None
            
            # Determine output directory
            if organize_by_year and metadata and 'year' in metadata:
                item_dir = output_dir / str(metadata['year'])
            else:
                item_dir = output_dir
                
            tasks.append({
                'identifier': identifier,
                'output_dir': item_dir,
                'metadata': metadata
            })
            
        # Download with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_limit(task: Dict) -> Tuple[str, Optional[Path]]:
            nonlocal completed
            
            async with semaphore:
                path = await self.download_pdf(
                    identifier=task['identifier'],
                    output_dir=task['output_dir'],
                    metadata=task['metadata']
                )
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, task['identifier'])
                    
                return task['identifier'], path
                
        # Execute downloads
        download_results = await asyncio.gather(
            *[download_with_limit(task) for task in tasks],
            return_exceptions=True
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
        
        return results


# Convenience functions

async def download_pdf(
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
        acknowledge_ethical_usage=acknowledge_ethical_usage
    )
    return await downloader.download_pdf(identifier, output_dir)


async def download_pdfs(
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
        acknowledge_ethical_usage=acknowledge_ethical_usage
    )
    return await downloader.batch_download(
        identifiers,
        output_dir,
        progress_callback=progress_callback
    )


if __name__ == "__main__":
    # Example usage
    import sys
    
    async def test_unified_downloader():
        # Test identifiers
        test_cases = [
            # DOIs
            "10.1038/s41586-021-03819-2",  # Nature
            "10.1126/science.abg5298",      # Science
            "10.1016/j.cell.2021.07.015",   # Cell
            "10.1103/PhysRevLett.127.067401",  # APS
            "10.1021/acs.nanolett.1c02400",    # ACS
            
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
                acknowledge_ethical_usage=True
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
                progress_callback=progress
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
            print(f"\nSuccess rate: {success}/{len(test_cases)} ({success/len(test_cases)*100:.0f}%)")
            
    asyncio.run(test_unified_downloader())

# EOF