#!/usr/bin/env python3
"""
Enhanced PDF Downloader Implementation

Shows how to refactor _PDFDownloader.py to properly separate 
authentication from discovery engines.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class EnhancedPDFDownloadStrategy:
    """
    Enhanced strategy for PDF downloads that separates auth from discovery.
    
    Key changes:
    1. Authentication is handled first, providing session data
    2. Discovery engines use the authenticated session
    3. Zotero translators can access paywalled content
    """
    
    async def download_pdf_with_auth(
        self,
        doi: str,
        url: str,
        output_path: Path,
        progress_callback: Optional[callable] = None
    ) -> Optional[Path]:
        """
        Download PDF with proper authentication + discovery flow.
        
        This method should replace the current _download_from_doi method.
        """
        logger.info(f"Starting enhanced download for {doi}")
        
        # Step 1: Get authenticated session from any available provider
        auth_session = await self._get_authenticated_session()
        
        if auth_session:
            provider_name = auth_session.get('context', {}).get('provider', 'Unknown')
            logger.info(f"Using authenticated session from {provider_name}")
        else:
            logger.info("No authentication available, proceeding without auth")
        
        # Step 2: Try discovery engines with authentication
        discovery_strategies = [
            ("Direct patterns", self._try_direct_patterns_with_auth),
            ("Zotero translators", self._try_zotero_translator_with_auth),
            ("Playwright scraping", self._try_playwright_with_auth),
            ("Sci-Hub", self._try_scihub),  # Doesn't need auth
        ]
        
        for name, strategy in discovery_strategies:
            logger.info(f"Trying {name} for {doi}")
            
            if progress_callback:
                progress_callback(None, None, doi, method=name, status=None)
            
            try:
                # Pass auth session to each strategy
                pdf_path = await strategy(doi, url, output_path, auth_session)
                if pdf_path:
                    logger.info(f"Success with {name}: {pdf_path}")
                    return pdf_path
            except Exception as e:
                logger.debug(f"{name} failed for {doi}: {e}")
        
        logger.error(f"All strategies failed for {doi}")
        return None
    
    async def _get_authenticated_session(self) -> Optional[Dict[str, Any]]:
        """
        Get authenticated session from authentication manager.
        
        This checks all registered auth providers and returns
        the session from the first authenticated one.
        """
        if hasattr(self, 'auth_manager') and self.auth_manager:
            return await self.auth_manager.get_authenticated_session()
        
        # Fallback to direct OpenAthens check for compatibility
        if self.openathens_authenticator:
            try:
                if await self.openathens_authenticator.is_authenticated():
                    # Get cookies from OpenAthens
                    cookies = []
                    if hasattr(self.openathens_authenticator, '_full_cookies'):
                        cookies = self.openathens_authenticator._full_cookies
                    
                    return {
                        'cookies': cookies,
                        'headers': {},
                        'context': {'provider': 'OpenAthens'}
                    }
            except Exception as e:
                logger.debug(f"OpenAthens session check failed: {e}")
        
        return None
    
    async def _try_direct_patterns_with_auth(
        self,
        doi: str,
        url: str,
        output_path: Path,
        auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Try direct patterns with optional authentication."""
        pdf_urls = self._get_publisher_pdf_urls(url, doi)
        
        for pdf_url in pdf_urls:
            logger.info(f"Trying direct pattern: {pdf_url}")
            
            # Download with auth session if available
            if await self._download_file_with_auth(
                pdf_url, output_path, auth_session, referer=url
            ):
                return output_path
        
        return None
    
    async def _try_zotero_translator_with_auth(
        self,
        doi: str,
        url: str,
        output_path: Path,
        auth_session: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """
        Enhanced Zotero translator that uses authenticated session.
        
        This is the key improvement - Zotero translators can now
        access paywalled content using auth cookies.
        """
        if not self.zotero_translator_runner:
            return None
        
        # Use authenticated browser context for translator
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Add authentication cookies if available
            if auth_session and auth_session.get('cookies'):
                await context.add_cookies(auth_session['cookies'])
                logger.info(f"Added {len(auth_session['cookies'])} auth cookies to Zotero translator")
            
            try:
                page = await context.new_page()
                
                # Inject Zotero shim
                await page.add_init_script(self.zotero_translator_runner._zotero_shim)
                
                # Navigate with auth
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Find and run translator
                translator = self.zotero_translator_runner.find_translator_for_url(url)
                if not translator:
                    logger.debug(f"No translator found for {url}")
                    return None
                
                logger.info(f"Running {translator['label']} on authenticated page")
                
                # Execute translator
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
                    logger.debug(f"Translator failed: {result.get('error')}")
                    return None
                
                # Enhanced PDF discovery for authenticated pages
                pdf_urls = await self._find_authenticated_pdf_urls(page)
                
                # Also check translator results
                for item in result.get('items', []):
                    for attachment in item.get('attachments', []):
                        if attachment.get('mimeType') == 'application/pdf':
                            pdf_urls.append(attachment.get('url'))
                
                # Try downloading PDFs with auth
                for pdf_url in pdf_urls:
                    if pdf_url:
                        logger.info(f"Trying Zotero-discovered PDF: {pdf_url}")
                        if await self._download_file_with_auth(
                            pdf_url, output_path, auth_session, referer=url
                        ):
                            return output_path
                
            finally:
                await browser.close()
        
        return None
    
    async def _find_authenticated_pdf_urls(self, page) -> List[str]:
        """
        Find PDF URLs on authenticated pages.
        
        When authenticated, publishers show different download links.
        """
        return await page.evaluate('''
            () => {
                const urls = [];
                
                // Enhanced selectors for authenticated users
                const authSelectors = [
                    // Nature
                    'a[data-track-action="download pdf"]',
                    '.c-pdf-download__link',
                    
                    // Science
                    '.btn-pdf-download',
                    'a[data-article-pdf]',
                    
                    // Elsevier
                    '.pdf-download-btn',
                    'a.pdfLink',
                    
                    // Wiley
                    'a.pdf-download',
                    '.article-tools__pdf a',
                    
                    // Springer
                    'a[data-track-label="download-pdf"]',
                    
                    // Generic
                    'a:has-text("Download PDF")',
                    'a[href*=".pdf"][class*="download"]'
                ];
                
                const foundUrls = new Set();
                
                for (const selector of authSelectors) {
                    try {
                        document.querySelectorAll(selector).forEach(el => {
                            const href = el.href || el.getAttribute('data-href');
                            if (href && !href.includes('javascript:')) {
                                foundUrls.add(href);
                            }
                        });
                    } catch (e) {}
                }
                
                return Array.from(foundUrls);
            }
        ''')
    
    async def _download_file_with_auth(
        self,
        url: str,
        output_path: Path,
        auth_session: Optional[Dict[str, Any]] = None,
        referer: Optional[str] = None
    ) -> bool:
        """
        Download file with optional authenticated session.
        
        Uses cookies and headers from auth session if available.
        """
        # If we have auth cookies, use Playwright to maintain session
        if auth_session and auth_session.get('cookies'):
            return await self._download_with_playwright_session(
                url, output_path, auth_session, referer
            )
        
        # Otherwise use regular download
        return await self._download_file(url, output_path, referer)
    
    async def _download_with_playwright_session(
        self,
        url: str,
        output_path: Path,
        auth_session: Dict[str, Any],
        referer: Optional[str] = None
    ) -> bool:
        """Download using Playwright with authenticated session."""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Add auth cookies
            if auth_session.get('cookies'):
                await context.add_cookies(auth_session['cookies'])
            
            try:
                page = await context.new_page()
                
                # Set up download handling
                download_path = output_path.parent
                download_path.mkdir(parents=True, exist_ok=True)
                
                # Navigate and trigger download
                response = await page.goto(url, wait_until='domcontentloaded')
                
                # Check if it's a direct PDF
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' in content_type:
                    # Direct PDF download
                    content = await response.body()
                    if content.startswith(b'%PDF'):
                        output_path.write_bytes(content)
                        logger.info(f"Downloaded PDF with auth to {output_path}")
                        return True
                
                # Otherwise look for download button/link
                download_triggered = False
                
                # Try clicking download button
                try:
                    await page.click('a:has-text("Download PDF")', timeout=5000)
                    download_triggered = True
                except:
                    pass
                
                if download_triggered:
                    # Wait for download
                    async with page.expect_download(timeout=30000) as download_info:
                        pass
                    download = await download_info.value
                    await download.save_as(output_path)
                    return True
                
            except Exception as e:
                logger.debug(f"Playwright download failed: {e}")
            finally:
                await browser.close()
        
        return False


# Example of how to initialize the enhanced downloader
def create_enhanced_downloader():
    """
    Create an enhanced PDF downloader with proper auth/discovery separation.
    
    This shows how the PDFDownloader should be initialized with the new
    authentication architecture.
    """
    from _PDFDownloader import PDFDownloader
    from _AuthenticationProviders import AuthenticationManager, create_authentication_provider
    
    # Create base downloader
    downloader = PDFDownloader(
        use_translators=True,
        use_scihub=True,
        use_playwright=True
    )
    
    # Create authentication manager
    auth_manager = AuthenticationManager()
    
    # Register authentication providers based on config
    if downloader.use_openathens:
        openathens = create_authentication_provider('openathens', {
            'email': downloader.openathens_config.get('email'),
            'debug_mode': downloader.openathens_config.get('debug_mode', False)
        })
        auth_manager.register_provider(openathens)
    
    # Register IP-based auth (always available)
    ip_auth = create_authentication_provider('ip_based')
    auth_manager.register_provider(ip_auth)
    
    # Future: Register other providers
    # if use_ezproxy:
    #     ezproxy = create_authentication_provider('ezproxy', ezproxy_config)
    #     auth_manager.register_provider(ezproxy)
    
    # Attach auth manager to downloader
    downloader.auth_manager = auth_manager
    
    return downloader


print("""
Enhanced PDF Downloader Implementation Summary:

1. Authentication is now separate from discovery
   - AuthenticationManager handles all auth providers
   - Each provider can be registered independently
   - Session data is passed to discovery engines

2. Zotero translators now work with authentication
   - Cookies are injected before running translators
   - Can access paywalled content
   - Enhanced PDF discovery for authenticated pages

3. Graceful fallbacks
   - If auth fails, still tries without auth
   - Multiple discovery engines tried in order
   - Clear logging of what's happening

4. Future-proof architecture
   - Easy to add new auth methods (EZProxy, Shibboleth)
   - Discovery engines work with any auth provider
   - No tight coupling between components

Next steps:
1. Replace _download_from_doi with download_pdf_with_auth
2. Initialize auth_manager in PDFDownloader.__init__
3. Update all discovery methods to accept auth_session
4. Test with various publisher sites
""")