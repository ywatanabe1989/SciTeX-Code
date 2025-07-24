#!/usr/bin/env python3
"""
Enhanced Zotero Translator Runner with Authentication Support

This shows how to modify the ZoteroTranslatorRunner to use 
authenticated sessions from OpenAthens.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, BrowserContext


class AuthenticatedZoteroRunner:
    """
    Zotero Translator Runner that can use authenticated sessions.
    
    Key enhancement: Uses cookies from OpenAthens to access paywalled content
    before running translators.
    """
    
    def __init__(self, base_runner):
        """
        Initialize with existing ZoteroTranslatorRunner.
        
        Args:
            base_runner: Existing ZoteroTranslatorRunner instance
        """
        self.base_runner = base_runner
        self._auth_cookies = None
        
    def set_auth_cookies(self, cookies: List[Dict[str, Any]]):
        """Set authentication cookies from OpenAthens."""
        self._auth_cookies = cookies
        
    async def run_translator_with_auth(
        self,
        url: str,
        translator: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run translator with authenticated browser context.
        
        This is the key improvement - we inject OpenAthens cookies
        before navigating to the publisher page.
        """
        # Find translator if not provided
        if not translator:
            translator = self.base_runner.find_translator_for_url(url)
            if not translator:
                return {
                    'success': False,
                    'error': f'No translator found for {url}',
                    'items': []
                }
        
        print(f"Running {translator['label']} with authentication...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            try:
                context = await browser.new_context()
                
                # CRITICAL: Add authentication cookies if available
                if self._auth_cookies:
                    await context.add_cookies(self._auth_cookies)
                    print(f"  Added {len(self._auth_cookies)} auth cookies")
                
                page = await context.new_page()
                
                # Inject Zotero shim
                await page.add_init_script(self.base_runner._zotero_shim)
                
                # Navigate with authentication
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Now we should have access to the full page content
                # Run the translator
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
                                error: error.toString(),
                                items: []
                            };
                        }
                    }
                ''', translator_code)
                
                # Extract PDF URLs with better selectors for authenticated pages
                await self._enhance_pdf_discovery(page, result.get('items', []))
                
                return result
                
            finally:
                await browser.close()
    
    async def _enhance_pdf_discovery(self, page, items):
        """
        Enhanced PDF discovery for authenticated pages.
        
        When authenticated, publishers often show different PDF links.
        """
        # Enhanced selectors for authenticated users
        pdf_urls = await page.evaluate('''
            () => {
                const urls = [];
                
                // Selectors specific to authenticated pages
                const authSelectors = [
                    // Nature
                    'a[data-track-action="download pdf"]',
                    'a.c-pdf-download__link',
                    
                    // Science/AAAS
                    '.btn-pdf-download',
                    'a[data-article-pdf]',
                    
                    // Elsevier/ScienceDirect
                    'a.pdf-download-btn',
                    '.pdfLink',
                    
                    // Wiley
                    'a.pdf-download',
                    '.article-tools__item--pdf a',
                    
                    // Springer
                    'a.c-pdf-download',
                    'a[data-track-label="download-pdf"]',
                    
                    // Generic patterns
                    'a[href*=".pdf"][download]',
                    'a:has-text("Download PDF")',
                    'button:has-text("Download PDF")',
                    '[aria-label*="Download PDF"]'
                ];
                
                for (const selector of authSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const href = el.href || el.getAttribute('data-href');
                            if (href && !urls.includes(href)) {
                                urls.push(href);
                            }
                        }
                    } catch (e) {
                        // Ignore selector errors
                    }
                }
                
                return urls;
            }
        ''')
        
        # Add discovered PDFs to items
        for item in items:
            if pdf_urls and not any(
                att.get('mimeType') == 'application/pdf' 
                for att in item.get('attachments', [])
            ):
                item.setdefault('attachments', []).append({
                    'title': 'Full Text PDF (Authenticated)',
                    'mimeType': 'application/pdf',
                    'url': pdf_urls[0]
                })


# Example of how to use this in PDFDownloader
async def enhanced_try_zotero_translator(
    self,
    doi: str,
    url: str,
    output_path: Path,
    auth_cookies: Optional[List[Dict]] = None
) -> Optional[Path]:
    """
    Enhanced Zotero translator method that uses authentication.
    
    This would replace the existing _try_zotero_translator method.
    """
    if not self.zotero_translator_runner:
        return None
    
    # Create authenticated runner
    auth_runner = AuthenticatedZoteroRunner(self.zotero_translator_runner)
    
    # Get auth cookies from OpenAthens if available
    if self.openathens_authenticator and not auth_cookies:
        try:
            # Get cookies from OpenAthens
            auth_cookies = self.openathens_authenticator._full_cookies
        except:
            pass
    
    if auth_cookies:
        auth_runner.set_auth_cookies(auth_cookies)
        print("Using authenticated Zotero translator")
    
    # Run translator with auth
    result = await auth_runner.run_translator_with_auth(url)
    
    if not result.get('success'):
        return None
    
    # Extract PDF URLs
    pdf_urls = []
    for item in result.get('items', []):
        for attachment in item.get('attachments', []):
            if attachment.get('mimeType') == 'application/pdf':
                pdf_urls.append(attachment['url'])
    
    # Try downloading PDFs
    for pdf_url in pdf_urls:
        print(f"Trying authenticated PDF: {pdf_url}")
        
        # Download with auth session
        if await self._download_with_auth_session(
            pdf_url, 
            output_path, 
            auth_cookies,
            referer=url
        ):
            return output_path
    
    return None


async def _download_with_auth_session(
    self,
    url: str,
    output_path: Path,
    auth_cookies: List[Dict],
    referer: str = None
) -> bool:
    """
    Download file using authenticated session.
    
    Uses Playwright to maintain cookie session.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Add auth cookies
        if auth_cookies:
            await context.add_cookies(auth_cookies)
        
        try:
            # Use Playwright's download handling
            page = await context.new_page()
            
            # Set up download
            download_path = output_path.parent
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Start download
            async with page.expect_download() as download_info:
                await page.goto(url)
            
            download = await download_info.value
            
            # Save to specified path
            await download.save_as(output_path)
            
            return output_path.exists()
            
        except Exception as e:
            print(f"Auth download failed: {e}")
            return False
        finally:
            await browser.close()


# Usage example
async def demo_authenticated_zotero():
    """Demonstrate the enhanced Zotero + OpenAthens flow."""
    
    print("🔧 Enhanced Zotero Translator with OpenAthens")
    print("=" * 50)
    
    # Example URL requiring authentication
    test_url = "https://www.nature.com/articles/s41586-021-03819-2"
    
    print(f"\nTarget: {test_url}")
    print("\nWorkflow:")
    print("1. OpenAthens authenticates and provides cookies")
    print("2. Zotero Translator runs on authenticated page")
    print("3. Translator finds PDF links visible to subscribers")
    print("4. Download using authenticated session")
    
    print("\nKey advantages:")
    print("- Zotero knows exact PDF location for each publisher")
    print("- OpenAthens provides access to paywalled content")
    print("- Combined = very high success rate")
    
    print("\nImplementation needed:")
    print("1. Modify _try_zotero_translator to accept auth cookies")
    print("2. Pass cookies from OpenAthens to Zotero runner")
    print("3. Use authenticated download for PDF retrieval")


if __name__ == "__main__":
    asyncio.run(demo_authenticated_zotero())