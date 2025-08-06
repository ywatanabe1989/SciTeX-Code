#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:45:00"
# Author: Claude
# File: _SmartPDFDownloader.py

"""
Smart PDF downloader using AI agents and multiple strategies.

This module implements Critical Task #7: Download PDFs using AI agents
with intelligent retry, authentication handling, and quality verification.
"""

import asyncio
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page, Browser, Download
import aiohttp

from scitex import logging
from ..auth import AuthenticationManager
from ..browser.local import BrowserManager
from ..config import ScholarConfig
from ..open_url import DOIToURLResolver
from ..utils._screenshot_capturer import ScreenshotCapturer
from ._PDFDownloader import PDFDownloader
from .._Paper import Paper

logger = logging.getLogger(__name__)


class DownloadAgent:
    """Base class for download agents with different strategies."""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.success_count = 0
        self.failure_count = 0
        
    async def can_handle_async(self, paper: Paper, url: str) -> bool:
        """Check if this agent can handle the download."""
        return True
        
    async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
        """Attempt to download the PDF."""
        raise NotImplementedError
        
    def adjust_priority(self, success: bool):
        """Adjust agent priority based on success/failure."""
        if success:
            self.success_count += 1
            self.priority += 1
        else:
            self.failure_count += 1
            self.priority -= 1


class DirectDownloadAgent(DownloadAgent):
    """Direct HTTP download without browser."""
    
    def __init__(self, downloader=None):
        super().__init__("DirectDownload", priority=10)
        self.downloader = downloader
        
    async def can_handle_async(self, paper: Paper, url: str) -> bool:
        """Check if URL is directly downloadable."""
        return url.endswith('.pdf') or '/pdf/' in url
        
    async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
        """Download PDF directly via HTTP."""
        try:
            http_timeout = self.downloader.timeouts['http_request'] if self.downloader else 30
            timeout = aiohttp.ClientTimeout(total=http_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Verify it's a PDF
                        if content.startswith(b'%PDF'):
                            output_path.write_bytes(content)
                            logger.success(f"Direct download successful: {output_path.name}")
                            return True
                            
        except Exception as e:
            logger.debug(f"Direct download failed: {e}")
            
        return False


class BrowserDownloadAgent(DownloadAgent):
    """Browser-based download with JavaScript handling."""
    
    def __init__(self, browser_manager: BrowserManager, screenshot_capturer=None, downloader=None):
        super().__init__("BrowserDownload", priority=8)
        self.browser_manager = browser_manager
        self.screenshot_capturer = screenshot_capturer
        self.downloader = downloader
        
    async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
        """Download PDF using browser automation."""
        browser = None
        try:
            browser = await self.browser_manager.get_browser_async()
            context = await browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Set download behavior
            await page.route('**/*.pdf', lambda route: route.continue_())
            
            # Navigate to URL with configurable timeout
            page_timeout = self.downloader.timeouts['page_load'] if self.downloader else 60000
            await page.goto(url, wait_until='networkidle', timeout=page_timeout)
            
            # Capture initial page screenshot
            if self.screenshot_capturer:
                await self.screenshot_capturer(paper, url, "initial_page", page)
            
            # Wait for page to stabilize with configurable timeout
            stabilization_wait = self.downloader.timeouts['stabilization'] if self.downloader else 3000
            await page.wait_for_timeout(stabilization_wait)
            
            # Capture page after stabilization
            if self.screenshot_capturer:
                await self.screenshot_capturer(paper, url, "after_stabilization", page)
            
            # Try to find and click PDF download button
            download_selectors = [
                'a[href$=".pdf"]',
                'a[href*="/pdf/"]',
                'button:has-text("Download PDF")',
                'a:has-text("Download PDF")',
                'a:has-text("View PDF")',
                'a:has-text("Full Text PDF")',
                '.pdf-download',
                '[aria-label*="Download"]',
                'a[title*="PDF"]'
            ]
            
            for selector in download_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        # Start waiting for download
                        async with page.expect_download() as download_info:
                            await elements[0].click()
                            download = await download_info.value
                            
                        # Save the download
                        await download.save_as(output_path)
                        
                        # Capture screenshot after download attempt
                        if self.screenshot_capturer:
                            await self.screenshot_capturer(paper, url, "after_download_attempt", page)
                        
                        # Verify it's a PDF
                        if output_path.exists() and output_path.read_bytes().startswith(b'%PDF'):
                            # Capture success screenshot
                            if self.screenshot_capturer:
                                await self.screenshot_capturer(paper, url, "download_successful", page)
                            logger.success(f"Browser download successful: {output_path.name}")
                            return True
                            
                except Exception as e:
                    logger.debug(f"Failed with selector {selector}: {e}")
                    continue
                    
            # Check for embedded PDF
            pdf_frames = await page.query_selector_all('iframe[src*="pdf"], embed[type="application/pdf"]')
            if pdf_frames:
                # Capture screenshot when PDF frame detected
                if self.screenshot_capturer:
                    await self.screenshot_capturer(paper, url, "pdf_frame_detected", page)
                
                frame_src = await pdf_frames[0].get_attribute('src')
                if frame_src:
                    # Try direct download of embedded PDF
                    if frame_src.startswith('/'):
                        frame_src = f"{urlparse(url).scheme}://{urlparse(url).netloc}{frame_src}"
                    
                    return await DirectDownloadAgent().download(paper, frame_src, output_path)
            
            # If no PDF found, capture final state
            if self.screenshot_capturer:
                await self.screenshot_capturer(paper, url, "no_pdf_found", page)
                    
        except Exception as e:
            logger.error(f"Browser download error: {e}")
            
        finally:
            if browser:
                await browser.close()
                
        return False


class AuthenticatedDownloadAgent(DownloadAgent):
    """Download with institutional authentication."""
    
    def __init__(self, auth_manager: AuthenticationManager, config: ScholarConfig):
        super().__init__("AuthenticatedDownload", priority=9)
        self.auth_manager = auth_manager
        self.config = config
        
    async def can_handle_async(self, paper: Paper, url: str) -> bool:
        """Check if authentication might help."""
        # Check for common paywall indicators
        return any(domain in url for domain in [
            'sciencedirect', 'springer', 'wiley', 'ieee',
            'nature', 'science', 'cell', 'elsevier'
        ])
        
    async def download(self, paper: Paper, url: str, output_path: Path) -> bool:
        """Download using authenticate_async session."""
        try:
            # Get authenticate_async browser
            browser = await self.auth_manager.get_authenticate_async_browser()
            
            if browser:
                page = await browser.new_page()
                
                # Use browser agent with authenticate_async session
                agent = BrowserDownloadAgent(None)
                agent.browser_manager = type('obj', (object,), {'get_browser_async': lambda: browser})()
                
                return await agent.download(paper, url, output_path)
                
        except Exception as e:
            logger.error(f"Authenticated download error: {e}")
            
        return False


class SmartPDFDownloader:
    """Intelligent PDF downloader using multiple AI agents."""
    
    def __init__(self, config: Optional[ScholarConfig] = None):
        """
        Initialize smart PDF downloader.
        
        Args:
            config: Scholar configuration
        """
        self.config = config or ScholarConfig()
        
        # Initialize components with config
        self.browser_manager = BrowserManager(headless=True, scholar_config=self.config)
        self.auth_manager = AuthenticationManager(config=self.config)
        self.url_resolver = DOIToURLResolver(config=self.config)
        # Initialize with path manager for proper directory structure
        self.path_manager = self.config.path_manager
        
        # Performance optimization: Configurable timeouts
        self.timeouts = {
            'page_load': self.config.resolve('pdf_download_page_load_timeout', default=30000, type=int),
            'screenshot': self.config.resolve('pdf_download_screenshot_timeout', default=10000, type=int),
            'stabilization': self.config.resolve('pdf_download_stabilization_wait', default=2000, type=int),
            'http_request': self.config.resolve('pdf_download_http_timeout', default=30, type=int),
            'download_wait': self.config.resolve('pdf_download_wait', default=2, type=int)
        }
        
        # Initialize download agents with screenshot capability and downloader reference
        self.agents = [
            DirectDownloadAgent(downloader=self),
            BrowserDownloadAgent(self.browser_manager, self.capture_systematic_screenshot_async, downloader=self),
            AuthenticatedDownloadAgent(self.auth_manager, self.config)
        ]
        
        # Simplified tracking: Use organized directory structure
        # No need for centralized JSON progress files - each paper's directory contains its status
        
    def is_paper_download(self, paper: Paper) -> Tuple[bool, Optional[Path]]:
        """
        Check if a paper is already download using directory-based lookup.
        
        Args:
            paper: Paper object
            
        Returns:
            Tuple of (is_download, pdf_path)
        """
        paper_info = {
            'title': paper.title,
            'authors': getattr(paper, 'authors', []),
            'year': getattr(paper, 'year', None),
            'doi': getattr(paper, 'doi', None),
            'journal': getattr(paper, 'journal', None)
        }
        
        storage_paths = self.path_manager.get_paper_storage_paths(paper_info, "papers")
        existing_pdfs = list(storage_paths["storage_path"].glob("*.pdf"))
        
        if existing_pdfs:
            return True, existing_pdfs[0]
        return False, None
        
    async def capture_systematic_screenshot_async(self, paper: Paper, url: str, description: str, page: Optional[Page] = None):
        """
        Capture systematic screenshots during download process.
        
        Args:
            paper: Paper object
            url: Current URL
            description: Stage description (e.g., "initial_page", "after_auth", "pdf_found", "captcha_detected")
            page: Existing page object (if None, creates new browser)
        """
        try:
            # Get paper storage paths
            paper_info = {
                'title': paper.title,
                'authors': getattr(paper, 'authors', []),
                'year': getattr(paper, 'year', None),
                'doi': getattr(paper, 'doi', None),
                'journal': getattr(paper, 'journal', None),
                'url': url
            }
            
            storage_paths = self.path_manager.get_paper_storage_paths(paper_info, "papers")
            screenshots_dir = storage_paths["storage_path"] / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp and filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}-{description}.png"
            screenshot_path = screenshots_dir / filename
            
            if page:
                # Use existing page with configurable timeout
                screenshot_timeout = self.timeouts['screenshot']
                await page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                    timeout=screenshot_timeout
                )
                logger.info(f"Screenshot captured: {description} -> {screenshot_path}")
            else:
                # Create new browser for screenshot
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    new_page = await browser.new_page()
                    
                    try:
                        page_timeout = self.timeouts['page_load']
                        screenshot_timeout = self.timeouts['screenshot']
                        await new_page.goto(url, wait_until='networkidle', timeout=page_timeout)
                        await new_page.screenshot(
                            path=str(screenshot_path),
                            full_page=True,
                            timeout=screenshot_timeout
                        )
                        logger.info(f"Screenshot captured: {description} -> {screenshot_path}")
                    finally:
                        await browser.close()
                        
        except Exception as e:
            logger.debug(f"Failed to capture systematic screenshot for {description}: {e}")

    async def download_single(self, paper: Paper) -> Tuple[bool, Optional[Path]]:
        """
        Download a single paper using multiple strategies.
        
        Args:
            paper: Paper object with metadata
            
        Returns:
            Tuple of (success, pdf_path)
        """
        # Check if already download using directory-based lookup
        paper_info = {
            'title': paper.title,
            'authors': getattr(paper, 'authors', []),
            'year': getattr(paper, 'year', None),
            'doi': getattr(paper, 'doi', None),
            'journal': getattr(paper, 'journal', None)
        }
        
        # Use PathManager to check if PDF already exists
        storage_paths = self.path_manager.get_paper_storage_paths(paper_info, "papers")
        existing_pdfs = list(storage_paths["storage_path"].glob("*.pdf"))
        
        if existing_pdfs:
            pdf_path = existing_pdfs[0]  # Take the first PDF found
            logger.info(f"Already download: {pdf_path.name}")
            return True, pdf_path
                
        # Get URLs to try
        urls = []
        
        # Add URL from paper
        if paper.url:
            urls.append(paper.url)
            
        # Resolve URL from DOI
        if paper.doi:
            logger.info(f"Resolving URL for DOI: {paper.doi}")
            result = await self.url_resolver.resolve_single_async(paper.doi)
            if result and result.get('url'):
                urls.append(result['url'])
                
        # Add direct DOI URL
        if paper.doi:
            urls.append(f"https://doi.org/{paper.doi}")
            
        if not urls:
            logger.warning(f"No URLs found for: {paper.title}")
            return False, None
            
        # Use organized directory structure for PDF storage
        storage_paths = self.path_manager.get_paper_storage_paths(paper_info, "papers")
        storage_paths["storage_path"].mkdir(parents=True, exist_ok=True)
        
        # Create proper filename
        journal = paper_info.get('journal') or 'Unknown'
        year = paper_info.get('year') or '0000'
        authors = paper_info.get('authors', [])
        first_author = authors[0].split(',')[0].strip() if authors else 'Unknown'
        first_author = first_author.split()[-1] if first_author else 'Unknown'
        
        # Clean and format filename
        journal_clean = ''.join(c for c in journal if c.isalnum())[:20]
        filename = f"{first_author}-{year}-{journal_clean}.pdf"
        output_path = storage_paths["storage_path"] / filename
        
        for url in urls:
            logger.info(f"Trying URL: {url}")
            
            # Sort agents by priority
            agents = sorted(self.agents, key=lambda a: a.priority, reverse=True)
            
            for agent in agents:
                if await agent.can_handle_async(paper, url):
                    logger.info(f"Trying {agent.name} agent...")
                    
                    success = await agent.download(paper, url, output_path)
                    agent.adjust_priority(success)
                    
                    if success and output_path.exists():
                        # Verify PDF
                        content = output_path.read_bytes()
                        if len(content) > 1000 and content.startswith(b'%PDF'):
                            # Save simple download metadata alongside PDF
                            metadata_file = output_path.with_suffix('.download.json')
                            download_metadata = {
                                'url': url,
                                'agent': agent.name,
                                'timestamp': datetime.now().isoformat(),
                                'size': len(content),
                                'md5': hashlib.md5(content).hexdigest(),
                                'doi': paper_info.get('doi'),
                                'title': paper_info.get('title')
                            }
                            
                            try:
                                with open(metadata_file, 'w') as f:
                                    json.dump(download_metadata, f, indent=2)
                            except Exception as e:
                                logger.warning(f"Failed to save download metadata: {e}")
                            
                            logger.success(f"Downloaded: {output_path.name} ({len(content)/1024:.1f} KB)")
                            return True, output_path
                        else:
                            # Invalid PDF
                            output_path.unlink()
                            logger.warning("Downloaded file is not a valid PDF")
                            
        # All attempts failed - save failure info in organized directory
        failure_file = storage_paths["storage_path"] / "download_failed.json"
        failure_metadata = {
            'urls_tried': urls,
            'timestamp': datetime.now().isoformat(),
            'title': paper_info.get('title'),
            'doi': paper_info.get('doi'),
            'last_error': 'All download agents failed'
        }
        
        try:
            with open(failure_file, 'w') as f:
                json.dump(failure_metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save failure metadata: {e}")
        
        # Capture screenshot for debugging using proper directory structure
        if urls:
            await self._capture_failure_screenshot_async(paper, urls[0], "download_failed")
                    
        return False, None
    
    async def _capture_failure_screenshot_async(self, paper: Paper, url: str, description: str):
        """
        Capture screenshot for failed download using proper directory structure.
        
        Args:
            paper: Paper object
            url: URL that failed
            description: Description of the failure (e.g., "download_failed", "auth_required")
        """
        try:
            # Get paper storage paths for screenshots
            paper_info = {
                'title': paper.title,
                'authors': getattr(paper, 'authors', []),
                'year': getattr(paper, 'year', None),
                'doi': getattr(paper, 'doi', None),
                'journal': getattr(paper, 'journal', None),
                'url': url
            }
            
            # Use "screenshots" as collection name for failed downloads
            storage_paths = self.path_manager.get_paper_storage_paths(paper_info, "screenshots")
            screenshots_dir = storage_paths["storage_path"] / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp and filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}-{description}.png"
            screenshot_path = screenshots_dir / filename
            
            # Capture screenshot using browser
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    logger.info(f"Capturing screenshot for failed download: {url}")
                    page_timeout = self.timeouts['page_load']
                    await page.goto(url, wait_until='networkidle', timeout=page_timeout)
                    
                    # Take full page screenshot with configurable timeout
                    screenshot_timeout = self.timeouts['screenshot']
                    await page.screenshot(
                        path=str(screenshot_path),
                        full_page=True,
                        timeout=screenshot_timeout
                    )
                    
                    # Save page info alongside screenshot
                    info_file = screenshot_path.with_suffix(".txt")
                    page_info = {
                        'url': url,
                        'paper_title': paper.title,
                        'paper_doi': getattr(paper, 'doi', None),
                        'timestamp': timestamp,
                        'description': description,
                        'page_title': await page.title(),
                        'page_url': page.url,
                        'user_agent': await page.evaluate('navigator.userAgent')
                    }
                    
                    with open(info_file, 'w', encoding='utf-8') as f:
                        for key, value in page_info.items():
                            f.write(f"{key}: {value}\n")
                    
                    logger.success(f"Screenshot saved: {screenshot_path}")
                    logger.info(f"Page info saved: {info_file}")
                    
                except Exception as e:
                    logger.warning(f"Failed to capture screenshot: {e}")
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Error in screenshot capture system: {e}")
        
    async def download_batch(
        self,
        papers: List[Paper],
        max_concurrent: int = 3,
        progress_callback = None
    ) -> Dict[str, Tuple[bool, Optional[Path]]]:
        """
        Download multiple papers concurrently.
        
        Args:
            papers: List of Paper objects
            max_concurrent: Maximum concurrent downloads
            progress_callback: Optional progress callback
            
        Returns:
            Dict mapping paper IDs to (success, path) tuples
        """
        if not self.progress.get('started_at'):
            self.progress['started_at'] = datetime.now().isoformat()
            
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_limit(paper: Paper, index: int):
            async with semaphore:
                if progress_callback:
                    progress_callback(index, len(papers), f"Downloading: {paper.title[:50]}...")
                    
                success, path = await self.download_single(paper)
                paper_id = paper.doi or paper.title
                results[paper_id] = (success, path)
                
                # Add configurable delay to avoid rate limiting
                download_wait = self.timeouts['download_wait']
                await asyncio.sleep(download_wait)
                
                return success, path
                
        # Create tasks
        tasks = [
            download_with_limit(paper, i)
            for i, paper in enumerate(papers)
        ]
        
        # Process all papers
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Summary
        success_count = sum(1 for s, _ in results.values() if s)
        logger.info(f"Downloaded {success_count}/{len(papers)} PDFs")
        
        return results
        
    def download_from_bibtex(
        self,
        bibtex_path: Path,
        max_concurrent: int = 3
    ) -> Dict[str, Tuple[bool, Optional[Path]]]:
        """
        Download PDFs for all entries in a BibTeX file.
        
        Args:
            bibtex_path: Path to BibTeX file
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            Dict mapping paper IDs to (success, path) tuples
        """
        import bibtexparser
        
        # Load BibTeX
        with open(bibtex_path, 'r', encoding='utf-8') as f:
            bib_db = bibtexparser.load(f)
            
        # Convert to Paper objects
        papers = []
        for entry in bib_db.entries:
            paper = Paper(
                title=entry.get('title', '').strip('{}'),
                authors=entry.get('author', '').split(' and '),
                year=int(entry.get('year', 0)) if entry.get('year', '').isdigit() else None,
                journal=entry.get('journal'),
                venue=entry.get('booktitle'),
                doi=entry.get('doi'),
                url=entry.get('url'),
                abstract=entry.get('abstract')
            )
            papers.append(paper)
            
        logger.info(f"Loaded {len(papers)} papers from {bibtex_path}")
        
        # Download PDFs
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self.download_batch(papers, max_concurrent)
            )
        finally:
            loop.close()


async def main():
    """Command-line interface for smart PDF downloads."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download PDFs intelligently using multiple strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download PDFs from BibTeX file
  python -m scitex.scholar.download.smart --bibtex papers.bib
  
  # Use more concurrent downloads
  python -m scitex.scholar.download.smart --bibtex papers.bib --worker_asyncs 5
  
  # Download to specific directory
  python -m scitex.scholar.download.smart --bibtex papers.bib --output-dir ./pdfs
        """
    )
    
    parser.add_argument(
        "--bibtex", "-b",
        type=str,
        required=True,
        help="BibTeX file containing papers to download"
    )
    
    parser.add_argument(
        "--worker_asyncs", "-w",
        type=int,
        default=3,
        help="Maximum concurrent downloads (default: 3)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        help="Output directory for PDFs"
    )
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = SmartPDFDownloader()
    
    if args.output_dir:
        downloader.download_dir = Path(args.output_dir)
        downloader.download_dir.mkdir(parents=True, exist_ok=True)
        
    # Download PDFs
    try:
        results = downloader.download_from_bibtex(
            Path(args.bibtex),
            max_concurrent=args.worker_asyncs
        )
        
        # Print summary
        success_count = sum(1 for s, _ in results.values() if s)
        print(f"\nDownload Summary:")
        print(f"  Total papers: {len(results)}")
        print(f"  Downloaded: {success_count}")
        print(f"  Failed: {len(results) - success_count}")
        print(f"\nPDFs saved to: {downloader.download_dir}")
        
    except KeyboardInterrupt:
        print("\nInterrupted! Progress has been saved.")
        return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))