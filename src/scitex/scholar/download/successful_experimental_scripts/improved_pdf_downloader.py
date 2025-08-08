#!/usr/bin/env python3
"""Improved PDF downloader that gets actual PDF binaries."""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.browser.local import BrowserManager
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.download.run_zotero_translators import find_translator_for_url, execute_translator
from scitex import logging

logger = logging.getLogger(__name__)


class ImprovedPDFDownloader:
    """PDF downloader that successfully gets actual PDF binaries from publishers."""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.browser_manager = BrowserManager(
            chrome_profile_name="system",
            browser_mode="stealth",
            auth_manager=self.auth_manager,
        )
    
    async def download_pdf(self, article_url: str, output_dir: Path = None) -> Dict:
        """
        Download PDF from article URL using the most reliable method.
        
        Args:
            article_url: URL of the article page
            output_dir: Directory to save PDF (default: .dev/)
            
        Returns:
            Dict with download results
        """
        if output_dir is None:
            output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/.dev")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get authenticated browser
        browser, context = await self.browser_manager.get_authenticated_browser_and_context_async()
        page = await context.new_page()
        
        result = {
            'article_url': article_url,
            'pdf_path': None,
            'metadata': {},
            'success': False,
            'method': None,
            'error': None
        }
        
        try:
            # Navigate to article page first
            logger.info(f"Loading article page: {article_url}")
            await page.goto(article_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            
            # Extract metadata using Zotero translator
            metadata = await self._extract_metadata(page, article_url)
            result['metadata'] = metadata
            
            # Determine PDF URL
            pdf_url = await self._find_pdf_url(page, article_url)
            if not pdf_url:
                logger.error("Could not find PDF URL")
                result['error'] = "PDF URL not found"
                return result
            
            logger.info(f"PDF URL: {pdf_url}")
            
            # Method 1: Direct request using Playwright's request context
            # This is the most reliable method that gets the actual PDF binary
            pdf_content = await self._download_with_request_context(context, pdf_url)
            
            if pdf_content and pdf_content.startswith(b'%PDF'):
                # Generate filename from metadata or URL
                filename = self._generate_filename(metadata, article_url)
                pdf_path = output_dir / filename
                
                pdf_path.write_bytes(pdf_content)
                logger.success(f"✅ Downloaded actual PDF: {pdf_path}")
                logger.info(f"File size: {len(pdf_content):,} bytes")
                
                result['pdf_path'] = str(pdf_path)
                result['success'] = True
                result['method'] = 'request_context'
                
                # Verify it's the actual paper content
                if self._verify_pdf_content(pdf_content):
                    logger.success("✅ Verified: This is the actual paper PDF!")
                else:
                    logger.warning("⚠️ This might be a wrapper or incomplete PDF")
            else:
                logger.error("Failed to download PDF or invalid PDF content")
                result['error'] = "Invalid PDF content"
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            result['error'] = str(e)
        finally:
            await page.close()
        
        return result
    
    async def _extract_metadata(self, page, url: str) -> Dict:
        """Extract metadata using Zotero translator."""
        try:
            translator_path = find_translator_for_url(url)
            if translator_path:
                logger.info(f"Using translator: {Path(translator_path).name}")
                await execute_translator(page, translator_path)
                
                # Get Zotero items
                items = await page.evaluate("() => window._zoteroItems || []")
                if items and len(items) > 0:
                    item = items[0]
                    return {
                        'title': item.get('title', ''),
                        'authors': item.get('creators', []),
                        'journal': item.get('publicationTitle', ''),
                        'year': item.get('date', ''),
                        'doi': item.get('DOI', ''),
                    }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
        return {}
    
    async def _find_pdf_url(self, page, article_url: str) -> Optional[str]:
        """Find the PDF URL from the article page."""
        
        # Common patterns for PDF URLs
        if '.pdf' in article_url:
            return article_url
        
        # Check for Nature pattern
        if 'nature.com' in article_url:
            # Nature PDFs are typically at article_url + '.pdf'
            return article_url.rstrip('/') + '.pdf'
        
        # Try to find PDF link on page
        pdf_links = await page.evaluate("""
            () => {
                // Look for PDF links
                const links = Array.from(document.querySelectorAll('a[href*=".pdf"]'));
                const pdfLinks = links.map(l => l.href).filter(h => h.includes('.pdf'));
                
                // Also check for download buttons that might have PDF URLs
                const downloadButtons = Array.from(document.querySelectorAll('[data-track-action*="download"]'));
                downloadButtons.forEach(btn => {
                    const href = btn.getAttribute('href');
                    if (href && href.includes('pdf')) {
                        pdfLinks.push(new URL(href, window.location.href).href);
                    }
                });
                
                return pdfLinks;
            }
        """)
        
        if pdf_links and len(pdf_links) > 0:
            # Return the first PDF link that looks like the main article
            for link in pdf_links:
                if 'supplement' not in link.lower():
                    return link
            return pdf_links[0]
        
        # Default: try adding .pdf to the URL
        return article_url.rstrip('/') + '.pdf'
    
    async def _download_with_request_context(self, context, pdf_url: str) -> Optional[bytes]:
        """Download PDF using Playwright's request context."""
        try:
            # Use the authenticated context's request object
            request_context = context.request
            
            # Make direct request for PDF
            response = await request_context.get(pdf_url)
            
            if response.status == 200:
                pdf_content = await response.body()
                
                if pdf_content and pdf_content.startswith(b'%PDF'):
                    return pdf_content
                else:
                    logger.warning(f"Response is not a PDF. First 100 bytes: {pdf_content[:100]}")
            else:
                logger.error(f"Request failed with status: {response.status}")
                
        except Exception as e:
            logger.error(f"Request context download failed: {e}")
        
        return None
    
    def _generate_filename(self, metadata: Dict, url: str) -> str:
        """Generate a meaningful filename for the PDF."""
        if metadata and metadata.get('title'):
            # Use title for filename
            title = metadata['title'][:50].replace(' ', '_').replace('/', '_')
            return f"{title}.pdf"
        else:
            # Use URL parts
            from urllib.parse import urlparse
            parts = urlparse(url).path.strip('/').split('/')
            return f"{'_'.join(parts[-2:])}.pdf"
    
    def _verify_pdf_content(self, pdf_content: bytes) -> bool:
        """Verify that the PDF contains actual paper content."""
        # Check for typical PDF document structures
        indicators = [
            b'/Type /Page',
            b'/Contents',
            b'/Resources',
            b'/Font',
            b'/Text'
        ]
        
        for indicator in indicators:
            if indicator in pdf_content[:100000]:  # Check first 100KB
                return True
        
        return False
    
    async def close(self):
        """Close the browser manager."""
        # BrowserManager doesn't have close_async, just let it clean up on exit
        pass


async def test_improved_downloader():
    """Test the improved PDF downloader."""
    downloader = ImprovedPDFDownloader()
    
    # Test URLs
    test_urls = [
        "https://www.nature.com/articles/s41593-025-01990-7",  # Nature article
        # "https://www.frontiersin.org/articles/10.3389/fnins.2023.1234567/full",  # Frontiers
        # Add more test URLs as needed
    ]
    
    for url in test_urls:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {url}")
        logger.info('='*60)
        
        result = await downloader.download_pdf(url)
        
        if result['success']:
            logger.success(f"✅ Success: {result['pdf_path']}")
            logger.info(f"Method: {result['method']}")
            if result['metadata']:
                logger.info(f"Title: {result['metadata'].get('title', 'N/A')}")
                logger.info(f"DOI: {result['metadata'].get('doi', 'N/A')}")
        else:
            logger.error(f"❌ Failed: {result['error']}")
    
    await downloader.close()


if __name__ == "__main__":
    asyncio.run(test_improved_downloader())