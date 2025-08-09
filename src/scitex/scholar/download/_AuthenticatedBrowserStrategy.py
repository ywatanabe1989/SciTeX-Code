#!/usr/bin/env python3
"""
Authenticated Browser Download Strategy

Downloads PDFs from paywalled journals using the existing Scholar browser system
with OpenAthens authentication and extensions for captcha/cookie handling.

This strategy properly integrates with:
- BrowserManager for authenticated browser sessions
- AuthenticationManager for OpenAthens (UniMelb) access
- Chrome extensions (captcha solver, cookie acceptor, Zotero connector)
- Screenshot debugging and progress tracking
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from scitex.logging import getLogger
from ._BaseDownloadStrategy import BaseDownloadStrategy
from scitex.scholar.browser import BrowserManager
from ..auth._AuthenticationManager import AuthenticationManager  
from scitex.scholar.config import ScholarConfig

logger = getLogger(__name__)

class AuthenticatedBrowserStrategy(BaseDownloadStrategy):
    """
    Download PDFs using authenticated browser sessions for paywalled journals.
    
    This strategy handles:
    - OpenAthens authentication via BrowserManager  
    - Publisher-specific PDF extraction patterns
    - Screenshot debugging for troubleshooting
    - Proper session management and cleanup
    """
    
    def __init__(self, config: ScholarConfig = None):
        super().__init__()
        self.config = config or ScholarConfig()
        
        # Initialize browser and auth managers  
        self.auth_manager = AuthenticationManager(config=self.config)
        self.browser_manager = BrowserManager(
            browser_mode="stealth",  # Use stealth mode for PDF downloads
            auth_manager=self.auth_manager,
            chrome_profile_name="extension",  # Use extension profile with all extensions
            config=self.config
        )
        
        # Screenshot directory using config path management
        self.screenshot_dir = self.config.get_screenshots_dir("pdf_download")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self._authenticated = False
        self._extensions_checked = False
        
    async def can_download(self, url: str, metadata: Dict[str, Any]) -> bool:
        """
        Check if this strategy can handle the URL.
        
        This strategy is designed exclusively for paywalled content that requires 
        institutional authentication. It targets major academic publishers.
        """
        domain = self._extract_domain(url)
        
        # Comprehensive list of paywalled publishers that require institutional access
        paywalled_domains = [
            # IEEE (engineering, computer science)
            'ieeexplore.ieee.org',
            'ieee.org',
            
            # Elsevier (multidisciplinary)
            'www.sciencedirect.com',
            'sciencedirect.com',
            
            # Springer Nature (multidisciplinary) 
            'link.springer.com',
            'springer.com',
            'www.nature.com',
            'nature.com',
            
            # Wiley (multidisciplinary)
            'onlinelibrary.wiley.com',
            'wiley.com',
            
            # American Physical Society
            'journals.aps.org',
            'aps.org',
            
            # American Chemical Society
            'pubs.acs.org',
            'acs.org',
            
            # Cell Press
            'www.cell.com',
            'cell.com',
            
            # Lancet
            'www.thelancet.com',
            'thelancet.com',
            
            # Taylor & Francis
            'www.tandfonline.com',
            'tandfonline.com',
            
            # SAGE
            'journals.sagepub.com',
            'sagepub.com',
            
            # Oxford Academic
            'academic.oup.com',
            'oup.com',
            
            # Cambridge University Press
            'www.cambridge.org',
            'cambridge.org',
            
            # American Association for the Advancement of Science
            'www.science.org',
            'science.org',
            
            # Annual Reviews
            'www.annualreviews.org',
            'annualreviews.org'
        ]
        
        # Always attempt paywalled content - this is our specialty
        is_paywalled_domain = any(domain.endswith(d) or d in domain for d in paywalled_domains)
        is_doi_url = 'doi.org' in url
        
        # Accept all academic content as potentially paywalled
        return is_paywalled_domain or is_doi_url
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    async def _ensure_authentication(self) -> bool:
        """Ensure we have valid authentication."""
        if self._authenticated:
            return True
            
        try:
            logger.info("Checking authentication status...")
            auth_status = await self.auth_manager.check_authentication_status_async()
            
            if auth_status.get('authenticated', False):
                logger.info("✅ Authentication verified")
                self._authenticated = True
                return True
            else:
                logger.warning("❌ Not authenticated - limited access to paywalled content")
                return False
                
        except Exception as e:
            logger.error(f"Authentication check failed: {e}")
            return False
    
    async def _extract_pdf_urls_from_page(self, page, paper_name: str) -> List[Dict[str, str]]:
        """Extract PDF URLs from the current page using JavaScript."""
        try:
            # Take screenshot for debugging
            screenshot_path = self.screenshot_dir / f"{paper_name.replace('/', '_')}-extraction.png"
            await page.screenshot(path=screenshot_path)
            logger.debug(f"Screenshot saved: {screenshot_path}")
            
            # Execute JavaScript to find PDF links
            pdf_data = await page.evaluate("""
                () => {
                    const pdfLinks = [];
                    
                    // Strategy 1: Direct PDF links
                    document.querySelectorAll('a[href*=".pdf"], a[href$=".pdf"]').forEach(link => {
                        if (link.href) {
                            pdfLinks.push({
                                url: link.href,
                                text: link.textContent.trim(),
                                type: 'direct_pdf'
                            });
                        }
                    });
                    
                    // Strategy 2: Download buttons and links
                    document.querySelectorAll('a').forEach(link => {
                        const text = link.textContent.toLowerCase();
                        const href = link.href || '';
                        
                        if (href && (
                            text.includes('download pdf') ||
                            text.includes('pdf download') ||
                            text.includes('full text pdf') ||
                            text.includes('view pdf') ||
                            (text.includes('download') && text.includes('pdf')) ||
                            link.hasAttribute('data-pdf-url')
                        )) {
                            pdfLinks.push({
                                url: href,
                                text: link.textContent.trim(),
                                type: 'download_button'
                            });
                        }
                    });
                    
                    // Strategy 3: Publisher-specific patterns
                    const publisherSelectors = [
                        // IEEE
                        'a[href*="/stamp/stamp.jsp"]',
                        'a[href*="/iel"]',
                        // Elsevier/ScienceDirect
                        'a[href*="/pii/"]',
                        'a.pdf-download-btn',
                        // Springer
                        'a[href*="/content/pdf/"]',
                        // Wiley
                        'a[href*="/doi/pdf/"]',
                        // Nature
                        'a[data-track-action*="download pdf"]',
                        // General patterns
                        '.pdf-link',
                        '.download-pdf',
                        '[data-pdf-url]'
                    ];
                    
                    publisherSelectors.forEach(selector => {
                        try {
                            document.querySelectorAll(selector).forEach(el => {
                                const url = el.href || el.getAttribute('data-pdf-url');
                                if (url) {
                                    pdfLinks.push({
                                        url: url,
                                        text: el.textContent.trim(),
                                        type: 'publisher_specific',
                                        selector: selector
                                    });
                                }
                            });
                        } catch (e) {
                            // Ignore selector errors
                        }
                    });
                    
                    // Remove duplicates
                    const uniqueUrls = new Set();
                    const uniqueLinks = pdfLinks.filter(link => {
                        if (uniqueUrls.has(link.url)) {
                            return false;
                        }
                        uniqueUrls.add(link.url);
                        return true;
                    });
                    
                    return {
                        pdf_links: uniqueLinks,
                        page_title: document.title,
                        current_url: window.location.href,
                        total_links: document.querySelectorAll('a').length
                    };
                }
            """)
            
            pdf_links = pdf_data.get('pdf_links', [])
            logger.info(f"Found {len(pdf_links)} potential PDF links")
            
            return pdf_links
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return []
    
    async def _download_pdf_with_browser(self, pdf_url: str, output_path: Path, paper_name: str) -> bool:
        """Download PDF using the authenticated browser session."""
        try:
            browser, context = await self.browser_manager.get_authenticated_browser_and_context_async()
            page = await context.new_page()
            
            logger.info(f"Downloading PDF from: {pdf_url}")
            
            # Navigate to PDF URL
            response = await page.goto(pdf_url, wait_for="networkidle", timeout=30000)
            
            if response and response.status == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'pdf' in content_type:
                    # Direct PDF response
                    pdf_content = await response.body()
                    
                    if pdf_content and pdf_content[:4] == b'%PDF':
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(pdf_content)
                        
                        logger.info(f"✅ Downloaded PDF: {len(pdf_content):,} bytes")
                        await page.close()
                        return True
                    else:
                        logger.warning("Response is not a valid PDF")
                else:
                    # Might be a page with PDF links - try to extract
                    logger.debug(f"Got HTML page, looking for PDF links...")
                    
                    # Take screenshot of the page
                    screenshot_path = self.screenshot_dir / f"{paper_name.replace('/', '_')}-download-page.png"
                    await page.screenshot(path=screenshot_path)
                    
                    # Look for PDF download links on this page
                    pdf_links = await self._extract_pdf_urls_from_page(page, paper_name)
                    
                    # Try the first PDF link found
                    for link in pdf_links[:2]:  # Try top 2 links
                        try:
                            new_pdf_url = link['url']
                            logger.debug(f"Trying extracted PDF URL: {new_pdf_url}")
                            
                            new_response = await page.goto(new_pdf_url, timeout=15000)
                            if new_response and new_response.status == 200:
                                new_content_type = new_response.headers.get('content-type', '').lower()
                                if 'pdf' in new_content_type:
                                    pdf_content = await new_response.body()
                                    if pdf_content and pdf_content[:4] == b'%PDF':
                                        output_path.parent.mkdir(parents=True, exist_ok=True)
                                        with open(output_path, 'wb') as f:
                                            f.write(pdf_content)
                                        logger.info(f"✅ Downloaded PDF from extracted link: {len(pdf_content):,} bytes")
                                        await page.close()
                                        return True
                        except Exception as e:
                            logger.debug(f"Failed to download from extracted link: {e}")
                            continue
            else:
                logger.warning(f"Failed to access PDF URL: HTTP {response.status if response else 'no response'}")
            
            await page.close()
            return False
            
        except Exception as e:
            logger.error(f"Browser PDF download failed: {e}")
            return False
    
    async def download(
        self,
        url: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        session_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """
        Download PDF using authenticated browser session.
        
        Args:
            url: DOI or publisher URL
            output_path: Where to save the PDF  
            metadata: Paper metadata
            session_data: Session data (unused - browser manages sessions)
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        if not metadata:
            metadata = {}
        
        paper_name = metadata.get('readable_name', 'unknown_paper')
        
        logger.info(f"Starting authenticated browser download for: {paper_name}")
        logger.info(f"URL: {url}")
        
        # Ensure authentication
        auth_available = await self._ensure_authentication()
        if not auth_available:
            logger.warning("No authentication available - may have limited access")
        
        try:
            # Get authenticated browser context  
            browser, context = await self.browser_manager.get_authenticated_browser_and_context_async()
            page = await context.new_page()
            
            # Navigate to the paper page
            logger.info(f"Navigating to paper page...")
            response = await page.goto(url, wait_for="networkidle", timeout=30000)
            
            if not response or response.status != 200:
                logger.error(f"Failed to load paper page: HTTP {response.status if response else 'no response'}")
                await page.close()
                return None
            
            # Take screenshot of the paper page
            screenshot_path = self.screenshot_dir / f"{paper_name.replace('/', '_')}-paper-page.png"
            await page.screenshot(path=screenshot_path)
            logger.debug(f"Paper page screenshot: {screenshot_path}")
            
            # Extract PDF URLs from the page
            pdf_links = await self._extract_pdf_urls_from_page(page, paper_name)
            
            await page.close()
            
            if not pdf_links:
                logger.warning("No PDF links found on paper page")
                return None
            
            # Try downloading from each PDF link
            for i, link in enumerate(pdf_links[:3]):  # Try top 3 links
                pdf_url = link['url']
                logger.info(f"Attempting download {i+1}/{min(3, len(pdf_links))}: {link['type']}")
                logger.debug(f"PDF URL: {pdf_url}")
                
                if await self._download_pdf_with_browser(pdf_url, output_path, paper_name):
                    logger.info(f"✅ Successfully downloaded PDF using authenticated browser")
                    return output_path
                
                # Brief pause between attempts
                await asyncio.sleep(1)
            
            logger.warning(f"❌ All PDF download attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"Authenticated browser download failed: {e}")
            return None
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy."""
        return {
            'name': 'AuthenticatedBrowserStrategy',
            'description': 'Downloads PDFs using authenticated browser sessions for paywalled journals',
            'authentication': 'OpenAthens (UniMelb)',
            'browser_mode': 'stealth',
            'extensions': ['captcha_solver', 'cookie_acceptor', 'zotero_connector'],
            'supported_auth_types': ['OpenAthens', 'Shibboleth', 'EZProxy'],
            'debugging': f'Screenshots saved to {self.screenshot_dir}'
        }

# EOF