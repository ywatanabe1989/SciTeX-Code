#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 23:55:00 (assistant)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/download/SmartPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/SmartPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Smart PDF Downloader with Zotero Translator Integration

This module provides intelligent PDF downloading with:
1. Zotero translator support for metadata extraction
2. Multiple download strategies with fallbacks
3. Periodic screenshots for debugging
4. Authentication support via BrowserManager
5. Publisher-specific handling
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import httpx
from playwright.async_api import Page, Response

from scitex import logging

# Handle both module and script execution
try:
    from scitex.scholar.browser import BrowserManager
    from scitex.scholar.auth import AuthenticationManager
    from scitex.scholar.config import ScholarConfig
    from .run_zotero_translators import find_translator_for_url, execute_translator
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from scitex.scholar.browser import BrowserManager
    from scitex.scholar.auth import AuthenticationManager
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.download.run_zotero_translators import find_translator_for_url, execute_translator

logger = logging.getLogger(__name__)


class SmartPDFDownloader:
    """
    Advanced PDF downloader with Zotero translator support.
    
    Features:
    - Automatic publisher detection via Zotero translators
    - Multiple download strategies with intelligent fallbacks
    - Periodic screenshot documentation
    - Full authentication support
    - Metadata extraction alongside PDF download
    """
    
    def __init__(self, browser_manager: BrowserManager = None):
        """Initialize the Smart PDF Downloader."""
        self.config = ScholarConfig()
        self.downloads_dir = self.config.get_downloads_dir()
        
        # Initialize browser manager if not provided
        if browser_manager:
            self.browser_manager = browser_manager
        else:
            auth_manager = AuthenticationManager()
            self.browser_manager = BrowserManager(
                browser_mode="interactive",  # Use interactive for debugging
                auth_manager=auth_manager,
                chrome_profile_name="system",  # Use system profile
            )
        
        # Track download statistics
        self.stats = {
            'total_attempts': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'methods_used': {}
        }
        
        # Publisher-specific strategies
        self.publisher_strategies = {
            'nature.com': self._nature_strategy,
            'science.org': self._science_strategy,
            'sciencedirect.com': self._generic_strategy,  # Use generic for now
            'springer.com': self._generic_strategy,  # Use generic for now
            'frontiersin.org': self._frontiers_strategy,
            'plos.org': self._generic_strategy,  # Use generic for now
            'mdpi.com': self._generic_strategy,  # Use generic for now
            'ieee.org': self._generic_strategy,  # Use generic for now
        }
    
    async def download_with_metadata(
        self,
        url: str,
        output_dir: Path = None,
        use_screenshots: bool = True
    ) -> Dict:
        """
        Download PDF with metadata extraction using Zotero translators.
        
        Args:
            url: URL of the article or PDF
            output_dir: Directory to save files (auto-created if needed)
            use_screenshots: Whether to take periodic screenshots
            
        Returns:
            Dictionary with download results and metadata
        """
        self.stats['total_attempts'] += 1
        
        # Setup output directory
        if output_dir is None:
            article_id = self._generate_article_id(url)
            output_dir = self.downloads_dir / article_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"=== Smart PDF Download ===")
        logger.info(f"URL: {url}")
        logger.info(f"Output: {output_dir}")
        
        # Get authenticated browser
        browser, context = await self.browser_manager.get_authenticated_browser_and_context_async()
        page = await context.new_page()
        
        # Store browser manager reference in context for screenshot functionality
        context._browser_manager = self.browser_manager
        
        result = {
            'url': url,
            'output_dir': str(output_dir),
            'metadata': {},
            'pdf_path': None,
            'supplementary': [],
            'screenshots': [],
            'method_used': None,
            'success': False,
            'error': None
        }
        
        try:
            # Navigate to article page
            logger.info("Step 1: Loading article page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # Start periodic screenshots if requested
            screenshot_task = None
            if use_screenshots:
                screenshot_task = await self.browser_manager.start_periodic_screenshots_async(
                    page,
                    prefix=f"smart_download_{self._generate_article_id(url)}",
                    interval_seconds=2,
                    duration_seconds=30,
                    verbose=False
                )
            
            # Step 2: Run Zotero translator for metadata
            logger.info("Step 2: Extracting metadata with Zotero translator...")
            metadata = await self._extract_metadata_with_translator(page, url)
            result['metadata'] = metadata
            
            # Step 3: Detect publisher and apply strategy
            logger.info("Step 3: Detecting publisher and download strategy...")
            publisher = self._detect_publisher(url, page)
            
            # Step 4: Download PDF with appropriate strategy
            pdf_info = await self._download_pdf_smart(
                page,
                url,
                output_dir,
                publisher,
                metadata
            )
            
            if pdf_info['success']:
                result['pdf_path'] = pdf_info['path']
                result['method_used'] = pdf_info['method']
                result['success'] = True
                self.stats['successful_downloads'] += 1
                self.stats['methods_used'][pdf_info['method']] = \
                    self.stats['methods_used'].get(pdf_info['method'], 0) + 1
                logger.success(f"✅ PDF downloaded: {pdf_info['path']}")
            else:
                result['error'] = pdf_info.get('error', 'Unknown error')
                self.stats['failed_downloads'] += 1
                logger.error(f"❌ Download failed: {result['error']}")
            
            # Step 5: Download supplementary materials
            logger.info("Step 5: Checking for supplementary materials...")
            supplementary = await self._download_supplementary(page, output_dir)
            result['supplementary'] = supplementary
            
            # Stop screenshots
            if screenshot_task:
                await self.browser_manager.stop_periodic_screenshots_async(screenshot_task)
            
            # Save metadata to file
            metadata_path = output_dir / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Metadata saved: {metadata_path}")
            
        except Exception as e:
            logger.error(f"Download failed with exception: {e}")
            result['error'] = str(e)
            self.stats['failed_downloads'] += 1
        finally:
            await page.close()
        
        return result
    
    async def _extract_metadata_with_translator(self, page: Page, url: str) -> Dict:
        """Extract metadata using Zotero translator."""
        try:
            # Find appropriate translator
            translator_path = find_translator_for_url(url)
            if not translator_path:
                logger.warning("No Zotero translator found for URL")
                return {}
            
            # Execute translator
            translator_result = await execute_translator(page, translator_path)
            
            # Extract metadata from Zotero items
            metadata = {}
            if translator_result and isinstance(translator_result, dict):
                # Handle window._zoteroItems if present
                items = await page.evaluate("() => window._zoteroItems || []")
                if items and len(items) > 0:
                    item = items[0]  # Use first item
                    metadata = {
                        'title': item.get('title', ''),
                        'authors': item.get('creators', []),
                        'journal': item.get('publicationTitle', ''),
                        'year': item.get('date', ''),
                        'doi': item.get('DOI', ''),
                        'abstract': item.get('abstractNote', ''),
                        'volume': item.get('volume', ''),
                        'issue': item.get('issue', ''),
                        'pages': item.get('pages', ''),
                        'url': item.get('url', url),
                        'attachments': item.get('attachments', []),
                        'tags': item.get('tags', []),
                    }
                    logger.success(f"Extracted metadata: {metadata.get('title', 'Unknown')[:50]}...")
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {}
    
    def _detect_publisher(self, url: str, page: Page) -> str:
        """Detect publisher from URL or page content."""
        domain = urlparse(url).netloc.lower()
        
        for publisher_domain in self.publisher_strategies.keys():
            if publisher_domain in domain:
                logger.info(f"Detected publisher: {publisher_domain}")
                return publisher_domain
        
        logger.info("Publisher not detected, using generic strategy")
        return 'generic'
    
    async def _download_pdf_smart(
        self,
        page: Page,
        url: str,
        output_dir: Path,
        publisher: str,
        metadata: Dict
    ) -> Dict:
        """Download PDF using smart strategy selection."""
        
        # Try publisher-specific strategy first
        if publisher in self.publisher_strategies:
            logger.info(f"Using {publisher} specific strategy...")
            result = await self.publisher_strategies[publisher](page, url, output_dir, metadata)
            if result['success']:
                return result
        
        # Fallback to generic strategies
        logger.info("Trying generic download strategies...")
        
        # Strategy 1: Direct download button
        result = await self._try_download_button(page, output_dir)
        if result['success']:
            return result
        
        # Strategy 2: PDF link navigation
        result = await self._try_pdf_navigation(page, output_dir)
        if result['success']:
            return result
        
        # Strategy 3: Response interception
        result = await self._try_response_interception(page, url, output_dir)
        if result['success']:
            return result
        
        # Strategy 4: Print to PDF (last resort)
        result = await self._try_print_to_pdf(page, output_dir)
        return result
    
    async def _nature_strategy(self, page: Page, url: str, output_dir: Path, metadata: Dict) -> Dict:
        """Nature-specific download strategy."""
        logger.info("Applying Nature publishing group strategy...")
        
        # Nature serves PDFs through Chrome viewer
        pdf_url = url if '.pdf' in url else url + '.pdf'
        
        # Create new page for PDF
        new_page = await page.context.new_page()
        
        try:
            # Navigate to PDF URL
            await new_page.goto(pdf_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(5)
            
            # Try blob extraction first
            pdf_data = await self._extract_pdf_from_blob(new_page)
            if pdf_data:
                pdf_path = output_dir / 'main_article.pdf'
                pdf_path.write_bytes(pdf_data)
                return {
                    'success': True,
                    'path': str(pdf_path),
                    'method': 'nature_blob_extraction'
                }
            
            # Fallback to print
            return await self._try_print_to_pdf(new_page, output_dir)
            
        finally:
            await new_page.close()
    
    async def _science_strategy(self, page: Page, url: str, output_dir: Path, metadata: Dict) -> Dict:
        """Science.org specific strategy."""
        logger.info("Applying Science.org strategy...")
        
        # Science has reliable download buttons
        download_selectors = [
            'a[data-track-action*="download"]',
            'a[href*="/doi/pdf/"]',
            '.article-pdf-link'
        ]
        
        for selector in download_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible():
                    async with page.expect_download(timeout=10000) as download_info:
                        await element.click()
                    
                    download = await download_info.value
                    pdf_path = output_dir / 'main_article.pdf'
                    await download.save_as(str(pdf_path))
                    
                    return {
                        'success': True,
                        'path': str(pdf_path),
                        'method': 'science_direct_download'
                    }
            except:
                continue
        
        return {'success': False, 'error': 'Science download failed'}
    
    async def _generic_strategy(self, page: Page, url: str, output_dir: Path, metadata: Dict) -> Dict:
        """Generic strategy for any publisher."""
        logger.info("Applying generic download strategy...")
        
        # Try standard download methods in order
        strategies = [
            self._try_download_button,
            self._try_pdf_navigation,
            self._try_response_interception,
            self._try_print_to_pdf
        ]
        
        for strategy in strategies:
            if strategy == self._try_response_interception:
                result = await strategy(page, url, output_dir)
            else:
                result = await strategy(page, output_dir)
            
            if result.get('success'):
                return result
        
        return {'success': False, 'error': 'Generic strategy failed'}
    
    async def _frontiers_strategy(self, page: Page, url: str, output_dir: Path, metadata: Dict) -> Dict:
        """Frontiers specific strategy."""
        logger.info("Applying Frontiers strategy...")
        
        # Frontiers has straightforward PDF links
        pdf_link = await page.locator('a:has-text("Download PDF")').first.get_attribute('href')
        if pdf_link:
            full_url = urljoin(url, pdf_link)
            
            # Download with httpx
            cookies = await page.context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(full_url, cookies=cookie_dict)
                if response.status_code == 200 and response.content.startswith(b'%PDF'):
                    pdf_path = output_dir / 'main_article.pdf'
                    pdf_path.write_bytes(response.content)
                    return {
                        'success': True,
                        'path': str(pdf_path),
                        'method': 'frontiers_direct'
                    }
        
        return {'success': False, 'error': 'Frontiers download failed'}
    
    async def _extract_pdf_from_blob(self, page: Page) -> Optional[bytes]:
        """Extract PDF content from blob URL in Chrome viewer."""
        try:
            pdf_src = await page.evaluate("""
                () => {
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    return embed ? embed.src : null;
                }
            """)
            
            if pdf_src and pdf_src.startswith('blob:'):
                logger.info(f"Extracting from blob URL: {pdf_src}")
                
                pdf_blob = await page.evaluate("""
                    async (blobUrl) => {
                        try {
                            const response = await fetch(blobUrl);
                            const blob = await response.blob();
                            const buffer = await blob.arrayBuffer();
                            const bytes = new Uint8Array(buffer);
                            return Array.from(bytes);
                        } catch (e) {
                            return null;
                        }
                    }
                """, pdf_src)
                
                if pdf_blob:
                    pdf_bytes = bytes(pdf_blob)
                    if pdf_bytes.startswith(b'%PDF'):
                        logger.success(f"Extracted {len(pdf_bytes)} bytes from blob")
                        return pdf_bytes
        except Exception as e:
            logger.debug(f"Blob extraction failed: {e}")
        
        return None
    
    async def _try_download_button(self, page: Page, output_dir: Path) -> Dict:
        """Try to download via download button using Playwright's Download API."""
        download_selectors = [
            'button:has-text("Download PDF")',
            'a:has-text("Download PDF")',
            'a[download][href$=".pdf"]',
            '.pdf-download-btn',
            '[data-track-action*="download"]',
            'a[href*="/pdf/"][class*="download"]',
            'button[aria-label*="Download"]'
        ]
        
        for selector in download_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements[:3]:  # Try first 3 matches
                    if await element.is_visible():
                        logger.info(f"Clicking download element: {selector}")
                        
                        try:
                            # Use Playwright's Download API
                            async with page.expect_download(timeout=5000) as download_info:
                                await element.click(force=True)  # Force click to bypass overlays
                            
                            download = await download_info.value
                            
                            # Log download details
                            logger.info(f"Download triggered: {download.suggested_filename}")
                            
                            # Save the file
                            pdf_path = output_dir / (download.suggested_filename or 'main_article.pdf')
                            await download.save_as(str(pdf_path))
                            
                            # Get download failure reason if any
                            failure = await download.failure()
                            if failure:
                                logger.warning(f"Download failed: {failure}")
                                if pdf_path.exists():
                                    pdf_path.unlink()
                                continue
                            
                            # Verify it's a PDF
                            if pdf_path.exists() and pdf_path.read_bytes().startswith(b'%PDF'):
                                return {
                                    'success': True,
                                    'path': str(pdf_path),
                                    'method': 'download_button',
                                    'filename': download.suggested_filename
                                }
                            else:
                                if pdf_path.exists():
                                    pdf_path.unlink()
                        except asyncio.TimeoutError:
                            logger.debug(f"No download triggered for {selector}")
                        except Exception as e:
                            logger.debug(f"Download error: {e}")
            except Exception as e:
                logger.debug(f"Selector error for {selector}: {e}")
                continue
        
        return {'success': False}
    
    async def _try_pdf_navigation(self, page: Page, output_dir: Path) -> Dict:
        """Try navigating to PDF URL."""
        pdf_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href*=".pdf"]'));
                return links.map(l => l.href).filter(h => h.includes('.pdf'));
            }
        """)
        
        for pdf_url in pdf_links[:3]:  # Try first 3 PDF links
            try:
                new_page = await page.context.new_page()
                
                # Set up response capture
                pdf_content = None
                
                async def capture_pdf(response: Response):
                    nonlocal pdf_content
                    if response.status == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                        try:
                            body = await response.body()
                            if body and body.startswith(b'%PDF'):
                                pdf_content = body
                        except:
                            pass
                
                new_page.on('response', capture_pdf)
                
                await new_page.goto(pdf_url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(3)
                
                if pdf_content:
                    pdf_path = output_dir / 'main_article.pdf'
                    pdf_path.write_bytes(pdf_content)
                    await new_page.close()
                    return {
                        'success': True,
                        'path': str(pdf_path),
                        'method': 'pdf_navigation'
                    }
                
                # Try blob extraction
                pdf_data = await self._extract_pdf_from_blob(new_page)
                if pdf_data:
                    pdf_path = output_dir / 'main_article.pdf'
                    pdf_path.write_bytes(pdf_data)
                    await new_page.close()
                    return {
                        'success': True,
                        'path': str(pdf_path),
                        'method': 'blob_extraction'
                    }
                
                await new_page.close()
            except:
                continue
        
        return {'success': False}
    
    async def _try_response_interception(self, page: Page, url: str, output_dir: Path) -> Dict:
        """Try intercepting PDF response."""
        pdf_content = None
        
        async def intercept_pdf(response: Response):
            nonlocal pdf_content
            try:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or '.pdf' in response.url.lower():
                    body = await response.body()
                    if body and body.startswith(b'%PDF'):
                        pdf_content = body
            except:
                pass
        
        page.on('response', intercept_pdf)
        
        # Reload page to capture responses
        await page.reload()
        await asyncio.sleep(5)
        
        if pdf_content:
            pdf_path = output_dir / 'main_article.pdf'
            pdf_path.write_bytes(pdf_content)
            return {
                'success': True,
                'path': str(pdf_path),
                'method': 'response_interception'
            }
        
        return {'success': False}
    
    async def _try_print_to_pdf(self, page: Page, output_dir: Path) -> Dict:
        """Last resort: print page to PDF."""
        try:
            logger.warning("Using print-to-PDF (visual capture only)")
            
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True,
                margin={'top': '10mm', 'right': '10mm', 'bottom': '10mm', 'left': '10mm'}
            )
            
            if pdf_bytes and len(pdf_bytes) > 50000:
                pdf_path = output_dir / 'main_article_printed.pdf'
                pdf_path.write_bytes(pdf_bytes)
                return {
                    'success': True,
                    'path': str(pdf_path),
                    'method': 'print_to_pdf',
                    'warning': 'Visual capture only - not original PDF'
                }
        except Exception as e:
            logger.error(f"Print to PDF failed: {e}")
        
        return {'success': False, 'error': 'All download methods failed'}
    
    async def _download_supplementary(self, page: Page, output_dir: Path) -> List[Dict]:
        """Download supplementary materials."""
        supplementary = []
        
        try:
            # Find supplementary links
            supp_links = await page.evaluate("""
                () => {
                    const links = [];
                    // Common supplementary selectors
                    const selectors = [
                        'a[href*="supplementary"]',
                        'a[href*="supplement"]',
                        'a[href*="additional"]',
                        'a[href*="supporting"]',
                        'a[href*="SI"]',
                        'a[href*="ESM"]'  // Electronic Supplementary Material
                    ];
                    
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(link => {
                            if (link.href) {
                                links.push({
                                    url: link.href,
                                    text: link.textContent.trim()
                                });
                            }
                        });
                    });
                    
                    return links;
                }
            """)
            
            for i, link in enumerate(supp_links[:10]):  # Limit to 10 files
                if any(ext in link['url'].lower() for ext in ['.pdf', '.xlsx', '.docx', '.zip']):
                    logger.info(f"Downloading supplementary: {link['text'][:50]}...")
                    
                    # Determine file extension
                    ext = Path(link['url']).suffix or '.pdf'
                    filename = f"supplementary_{i+1}{ext}"
                    file_path = output_dir / filename
                    
                    # Download with httpx
                    cookies = await page.context.cookies()
                    cookie_dict = {c['name']: c['value'] for c in cookies}
                    
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        try:
                            response = await client.get(link['url'], cookies=cookie_dict, timeout=30)
                            if response.status_code == 200:
                                file_path.write_bytes(response.content)
                                supplementary.append({
                                    'filename': filename,
                                    'path': str(file_path),
                                    'description': link['text'],
                                    'size': len(response.content)
                                })
                                logger.success(f"Downloaded: {filename}")
                        except:
                            logger.warning(f"Failed to download: {link['text'][:30]}...")
        
        except Exception as e:
            logger.warning(f"Supplementary download error: {e}")
        
        return supplementary
    
    def _generate_article_id(self, url: str) -> str:
        """Generate unique article ID from URL."""
        # Extract meaningful parts from URL
        parts = re.findall(r'[a-zA-Z0-9]+', url)
        # Use last few meaningful parts
        article_id = '_'.join(parts[-3:]) if len(parts) >= 3 else '_'.join(parts)
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{article_id}_{timestamp}"
    
    async def download_batch(self, urls: List[str], use_screenshots: bool = False) -> List[Dict]:
        """Download multiple PDFs in sequence."""
        results = []
        
        logger.info(f"=== Batch Download: {len(urls)} articles ===")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            try:
                result = await self.download_with_metadata(url, use_screenshots=use_screenshots)
                results.append(result)
                
                if result['success']:
                    logger.success(f"✅ [{i}/{len(urls)}] Success")
                else:
                    logger.warning(f"⚠️ [{i}/{len(urls)}] Failed: {result.get('error', 'Unknown')}")
                
                # Brief pause between downloads
                if i < len(urls):
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"❌ [{i}/{len(urls)}] Exception: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
        
        # Print summary
        logger.info("\n=== Download Summary ===")
        logger.info(f"Total: {len(urls)}")
        logger.info(f"Success: {sum(1 for r in results if r.get('success', False))}")
        logger.info(f"Failed: {sum(1 for r in results if not r.get('success', False))}")
        
        if self.stats['methods_used']:
            logger.info("\nMethods used:")
            for method, count in self.stats['methods_used'].items():
                logger.info(f"  {method}: {count}")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get download statistics."""
        return self.stats.copy()


async def test_smart_downloader():
    """Test the Smart PDF Downloader."""
    downloader = SmartPDFDownloader()
    
    # Test URLs
    test_urls = [
        "https://www.nature.com/articles/s41593-025-01990-7",  # Nature
        # "https://www.science.org/doi/10.1126/science.aao0702",  # Science
        # "https://www.frontiersin.org/articles/10.3389/fnins.2023.1234567/full",  # Frontiers
    ]
    
    results = await downloader.download_batch(test_urls, use_screenshots=True)
    
    # Save results
    results_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/smart_download_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nResults saved to: {results_file}")
    
    # Print statistics
    stats = downloader.get_statistics()
    logger.info(f"\nFinal Statistics:")
    logger.info(f"  Total attempts: {stats['total_attempts']}")
    logger.info(f"  Successful: {stats['successful_downloads']}")
    logger.info(f"  Failed: {stats['failed_downloads']}")


if __name__ == "__main__":
    asyncio.run(test_smart_downloader())