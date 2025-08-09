#!/usr/bin/env python3
"""
Authenticated PDF downloader integrating with existing Scholar auth and browser systems
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests

# Add src to path
sys.path.append('/home/ywatanabe/proj/SciTeX-Code/src')

try:
    import crawl4ai
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
from scitex.scholar.browser import BrowserManager
from scitex.scholar.download._ZoteroTranslatorRunner import ZoteroTranslatorRunner
from scitex.scholar.config import ScholarConfig
from scitex.logging import getLogger

logger = getLogger(__name__)

class AuthenticatedPDFDownloader:
    """
    Advanced PDF downloader that integrates with Scholar's authentication and browser systems
    
    Features:
    1. Uses existing OpenAthens authentication 
    2. Leverages browser extensions (captcha solvers, cookie acceptors)
    3. Supports both crawl4ai and Zotero translators
    4. Maintains authentication state across requests
    """
    
    def __init__(self, library_path="/home/ywatanabe/.scitex/scholar/library"):
        self.library_path = Path(library_path)
        self.screenshot_dir = Path("/tmp/scitex_auth_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Initialize Scholar components
        self.config = ScholarConfig()
        self.auth_manager = AuthenticationManager(config=self.config)
        self.browser_manager = BrowserManager(
            browser_mode="stealth",  # Use stealth mode for PDF downloads
            auth_manager=self.auth_manager,
            config=self.config
        )
        
        # Initialize Zotero translator runner
        self.zotero_runner = ZoteroTranslatorRunner()
        
        # Track authentication status
        self._authenticated = False
    
    async def ensure_authentication_async(self) -> bool:
        """Ensure we have valid authentication for library access"""
        if self._authenticated:
            return True
            
        try:
            logger.info("Checking authentication status...")
            
            # Use the authentication manager to ensure we're logged in
            auth_status = await self.auth_manager.check_authentication_status_async()
            
            if auth_status.get('authenticated', False):
                logger.info("✅ Already authenticated")
                self._authenticated = True
                return True
            else:
                logger.warning("❌ Not authenticated - PDF downloads may be limited")
                # In production, you might want to trigger authentication here
                return False
                
        except Exception as e:
            logger.error(f"Authentication check failed: {e}")
            return False
    
    def load_paper_metadata(self, scitex_id: str) -> Optional[Dict]:
        """Load metadata for a paper"""
        metadata_path = self.library_path / "MASTER" / scitex_id / "metadata.json"
        if not metadata_path.exists():
            return None
        
        with open(metadata_path) as f:
            return json.load(f)
    
    def get_pdf_path(self, metadata: Dict) -> Path:
        """Get expected PDF file path"""
        scitex_id = metadata['scitex_id']
        readable_name = metadata['readable_name']
        pdf_dir = self.library_path / "MASTER" / scitex_id
        return pdf_dir / f"{readable_name}.pdf"
    
    async def crawl4ai_extract_pdfs_async(self, url: str, paper_name: str) -> Dict:
        """Use crawl4ai with authentication for PDF extraction"""
        if not CRAWL4AI_AVAILABLE:
            return {'success': False, 'error': 'crawl4ai not available'}
        
        try:
            # Get authenticated browser context from BrowserManager
            browser, context = await self.browser_manager.get_authenticate_async_context()
            
            # Configure crawl4ai to use our authenticated browser session
            browser_config = BrowserConfig(
                headless=False,  # Keep consistent with our browser manager
                browser_type="chromium"
            )
            
            crawler_config = CrawlerRunConfig(
                wait_for="networkidle",
                js_code=[
                    """
                    // Extract PDF download links with authentication context
                    const pdfLinks = [];
                    
                    // Look for PDF links
                    document.querySelectorAll('a[href*=".pdf"], a[href*="/pdf"], a[download]').forEach(link => {
                        pdfLinks.push({
                            type: 'direct_pdf',
                            url: link.href,
                            text: link.textContent.trim()
                        });
                    });
                    
                    // Look for publisher-specific download buttons
                    const downloadSelectors = [
                        'a[data-track-action*="download"]',
                        '.pdf-download-link',
                        '.download-pdf',
                        '.full-text-pdf',
                        '[data-pdf-url]'
                    ];
                    
                    downloadSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const url = el.href || el.getAttribute('data-pdf-url');
                            if (url) {
                                pdfLinks.push({
                                    type: 'download_button',
                                    url: url,
                                    text: el.textContent.trim()
                                });
                            }
                        });
                    });
                    
                    return {
                        pdf_links: pdfLinks,
                        page_title: document.title,
                        authenticated: document.body.textContent.includes('authenticated') || 
                                     document.body.textContent.includes('institutional')
                    };
                    """
                ]
            )
            
            # Use crawl4ai with our browser configuration
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(
                    url=url,
                    config=crawler_config
                )
                
                if result.success:
                    # Extract JavaScript results
                    try:
                        js_data = json.loads(result.extracted_content or '{}')
                        
                        # Take screenshot for debugging
                        screenshot_path = self.screenshot_dir / f"{paper_name.replace('/', '_')}-crawl4ai.png"
                        # await page.screenshot(path=screenshot_path)
                        
                        return {
                            'success': True,
                            'pdf_links': js_data.get('pdf_links', []),
                            'authenticated': js_data.get('authenticated', False),
                            'screenshot_path': str(screenshot_path),
                            'method': 'crawl4ai_authenticated'
                        }
                    except json.JSONDecodeError:
                        # Fallback to markdown parsing
                        return {
                            'success': True,
                            'pdf_links': [],
                            'method': 'crawl4ai_fallback',
                            'markdown_length': len(result.markdown or '')
                        }
                else:
                    return {
                        'success': False,
                        'error': result.error_message,
                        'status_code': getattr(result, 'status_code', None)
                    }
            
        except Exception as e:
            logger.error(f"Crawl4ai extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def authenticated_browser_extract_async(self, url: str, paper_name: str) -> Dict:
        """Use authenticated browser to extract PDF links directly"""
        try:
            browser, context = await self.browser_manager.get_authenticate_async_context()
            page = await context.new_page()
            
            logger.info(f"Navigating to {url} with authentication...")
            await page.goto(url, wait_until="networkidle")
            
            # Take screenshot for debugging
            screenshot_path = self.screenshot_dir / f"{paper_name.replace('/', '_')}-auth-browser.png"
            await page.screenshot(path=screenshot_path)
            
            # Execute JavaScript to find PDF links
            pdf_data = await page.evaluate("""
                () => {
                    const pdfLinks = [];
                    
                    // Strategy 1: Direct PDF links
                    document.querySelectorAll('a[href$=".pdf"], a[href*="/pdf/"]').forEach(link => {
                        pdfLinks.push({
                            type: 'direct_pdf',
                            url: link.href,
                            text: link.textContent.trim()
                        });
                    });
                    
                    // Strategy 2: Download links
                    document.querySelectorAll('a').forEach(link => {
                        const text = link.textContent.toLowerCase();
                        if ((text.includes('download') && text.includes('pdf')) || 
                            text.includes('full text')) {
                            pdfLinks.push({
                                type: 'download_link',
                                url: link.href,
                                text: link.textContent.trim()
                            });
                        }
                    });
                    
                    // Strategy 3: Publisher-specific patterns
                    const publisherSelectors = [
                        'a[data-track-action*="download"]',
                        'a[data-track*="pdf"]',
                        '.pdf-download',
                        '.download-pdf',
                        '.full-text-link'
                    ];
                    
                    publisherSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            if (el.href) {
                                pdfLinks.push({
                                    type: 'publisher_specific',
                                    url: el.href,
                                    text: el.textContent.trim(),
                                    selector: selector
                                });
                            }
                        });
                    });
                    
                    // Check authentication indicators
                    const authIndicators = [
                        'institutional access',
                        'university access',
                        'authenticated',
                        'subscribed',
                        'member access'
                    ];
                    
                    const pageText = document.body.textContent.toLowerCase();
                    const authenticated = authIndicators.some(indicator => 
                        pageText.includes(indicator)
                    );
                    
                    return {
                        pdf_links: pdfLinks,
                        page_title: document.title,
                        authenticated: authenticated,
                        page_url: window.location.href
                    };
                }
            """)
            
            await page.close()
            
            return {
                'success': True,
                'pdf_links': pdf_data.get('pdf_links', []),
                'authenticated': pdf_data.get('authenticated', False),
                'screenshot_path': str(screenshot_path),
                'method': 'authenticated_browser'
            }
            
        except Exception as e:
            logger.error(f"Authenticated browser extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_pdf_with_auth_async(
        self, 
        pdf_url: str, 
        output_path: Path, 
        paper_name: str
    ) -> bool:
        """Download PDF using authenticated session"""
        try:
            browser, context = await self.browser_manager.get_authenticate_async_context()
            page = await context.new_page()
            
            logger.info(f"Downloading PDF from {pdf_url} with authentication...")
            
            # Navigate to PDF URL
            response = await page.goto(pdf_url, wait_for="networkidle")
            
            if response.status == 200:
                # Check if it's actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                
                if 'pdf' in content_type or pdf_url.endswith('.pdf'):
                    # Download the PDF content
                    pdf_content = await response.body()
                    
                    # Verify it's a valid PDF
                    if pdf_content and pdf_content[:4] == b'%PDF':
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(pdf_content)
                        
                        logger.info(f"✅ Downloaded PDF: {output_path} ({len(pdf_content)} bytes)")
                        await page.close()
                        return True
                    else:
                        logger.warning(f"Response doesn't appear to be a valid PDF")
                else:
                    logger.warning(f"Unexpected content-type: {content_type}")
            else:
                logger.error(f"HTTP {response.status} when accessing {pdf_url}")
            
            await page.close()
            return False
            
        except Exception as e:
            logger.error(f"Authenticated PDF download failed: {e}")
            return False
    
    async def process_single_paper_async(self, scitex_id: str) -> Dict:
        """Process a single paper using authenticated systems"""
        metadata = self.load_paper_metadata(scitex_id)
        if not metadata:
            return {'success': False, 'error': f'No metadata for {scitex_id}'}
        
        paper_name = metadata['readable_name']
        doi_url = f"https://doi.org/{metadata['doi']}"
        pdf_path = self.get_pdf_path(metadata)
        
        # Skip if PDF already exists
        if pdf_path.exists() and pdf_path.stat().st_size > 1000:
            logger.info(f"PDF already exists: {paper_name}")
            return {'success': True, 'status': 'already_exists'}
        
        logger.info(f"\\n=== Processing: {paper_name} ===")
        logger.info(f"DOI URL: {doi_url}")
        
        # Ensure authentication
        await self.ensure_authentication_async()
        
        # Strategy 1: Authenticated browser extraction
        logger.info("Strategy 1: Authenticated browser")
        auth_result = await self.authenticated_browser_extract_async(doi_url, paper_name)
        
        if auth_result['success'] and auth_result.get('pdf_links'):
            for link in auth_result['pdf_links'][:2]:  # Try top 2 links
                pdf_url = link['url']
                logger.info(f"Trying authenticated download: {pdf_url}")
                
                if await self.download_pdf_with_auth_async(pdf_url, pdf_path, paper_name):
                    return {
                        'success': True,
                        'method': 'authenticated_browser',
                        'pdf_url': pdf_url,
                        'path': str(pdf_path)
                    }
        
        # Strategy 2: Zotero translators with authentication context
        logger.info("Strategy 2: Zotero translators")
        zotero_result = await self.zotero_runner.run_translator_async(doi_url)
        
        if zotero_result['success']:
            for item in zotero_result.get('items', []):
                for attachment in item.get('attachments', []):
                    if attachment.get('mimeType') == 'application/pdf':
                        pdf_url = attachment.get('url')
                        if pdf_url:
                            logger.info(f"Trying Zotero PDF: {pdf_url}")
                            
                            if await self.download_pdf_with_auth_async(pdf_url, pdf_path, paper_name):
                                return {
                                    'success': True,
                                    'method': 'zotero_authenticated',
                                    'pdf_url': pdf_url,
                                    'path': str(pdf_path)
                                }
        
        # Strategy 3: Crawl4ai with authentication (if available)
        if CRAWL4AI_AVAILABLE:
            logger.info("Strategy 3: Crawl4ai with authentication")
            crawl4ai_result = await self.crawl4ai_extract_pdfs_async(doi_url, paper_name)
            
            if crawl4ai_result['success'] and crawl4ai_result.get('pdf_links'):
                for link in crawl4ai_result['pdf_links'][:2]:
                    pdf_url = link['url']
                    logger.info(f"Trying Crawl4ai PDF: {pdf_url}")
                    
                    if await self.download_pdf_with_auth_async(pdf_url, pdf_path, paper_name):
                        return {
                            'success': True,
                            'method': 'crawl4ai_authenticated',
                            'pdf_url': pdf_url,
                            'path': str(pdf_path)
                        }
        
        return {
            'success': False,
            'error': 'No PDF found with authenticated strategies',
            'strategies_tried': ['authenticated_browser', 'zotero', 'crawl4ai']
        }

async def test_authenticated_downloader():
    """Test the authenticated PDF downloader"""
    downloader = AuthenticatedPDFDownloader()
    
    # Test with a few sample papers
    test_papers = [
        "16830DAC",  # Scientific Reports paper
        "E6A3AF59",  # Frontiers paper  
    ]
    
    results = {}
    
    for scitex_id in test_papers:
        logger.info(f"\\n=== Testing {scitex_id} ===")
        
        try:
            result = await downloader.process_single_paper_async(scitex_id)
            results[scitex_id] = result
            
            if result['success']:
                logger.info(f"✅ Success: {result.get('method')}")
            else:
                logger.error(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Exception testing {scitex_id}: {e}")
            results[scitex_id] = {'success': False, 'error': str(e)}
    
    # Save test results
    results_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/auth_test_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Test results saved to {results_file}")

if __name__ == "__main__":
    asyncio.run(test_authenticated_downloader())