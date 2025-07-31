#!/usr/bin/env python3
"""
OpenURL Resolver with ZenRows Stealth Browser

This example shows how to use the local ZenRows stealth browser
for institutional OpenURL resolution with anti-bot bypass.

Perfect for:
- Institutional resolvers with bot detection
- Complex authentication flows
- Sites that block automated tools
"""

import asyncio
import os
from pathlib import Path

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser._ZenRowsStealthyLocal import ZenRowsStealthyLocal
from scitex import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthyOpenURLResolver(OpenURLResolver):
    """OpenURL resolver using local browser with ZenRows stealth proxy.
    
    This combines:
    - Full local browser control for authentication
    - ZenRows proxy for anti-bot bypass
    - OpenURL institutional resolution
    """
    
    def __init__(
        self,
        auth_manager,
        resolver_url: str,
        zenrows_api_key: Optional[str] = None,
        headless: bool = False,
        use_residential: bool = True,
        country: str = "us"
    ):
        """Initialize stealthy OpenURL resolver.
        
        Args:
            auth_manager: Authentication manager
            resolver_url: Base URL of institutional resolver
            zenrows_api_key: ZenRows API key (or from env)
            headless: Run browser in headless mode
            use_residential: Use premium residential proxies
            country: Proxy country location
        """
        super().__init__(auth_manager, resolver_url)
        
        # Initialize ZenRows stealth browser
        self.stealth_browser = ZenRowsStealthyLocal(
            headless=headless,
            zenrows_api_key=zenrows_api_key,
            use_residential=use_residential,
            country=country
        )
        self.headless = headless
        
    async def _resolve_single_async(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Resolve URL using stealthy browser."""
        openurl = self.build_openurl(**kwargs)
        doi = kwargs.get("doi", "")
        
        logger.info(f"Resolving via ZenRows stealth browser: {openurl}")
        
        try:
            # Get stealth browser
            browser = await self.stealth_browser.get_browser()
            context = await self.stealth_browser.new_context()
            page = await context.new_page()
            
            # Navigate to OpenURL
            await page.goto(openurl, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # Check if we need to authenticate
            current_url = page.url
            if "login" in current_url.lower() or "auth" in current_url.lower():
                if not self.headless:
                    logger.info("Authentication required - please login in browser")
                    print("\n" + "="*60)
                    print("👨‍💻 AUTHENTICATION REQUIRED")
                    print("="*60)
                    print("\nPlease login in the browser window.")
                    print("Press Enter when logged in...")
                    input()
                else:
                    logger.warning("Authentication required but browser is headless")
                    return {
                        "final_url": None,
                        "resolver_url": openurl,
                        "access_type": "auth_required",
                        "success": False,
                    }
            
            # Wait for any redirects to settle
            await page.wait_for_timeout(2000)
            final_url = page.url
            
            # Check if we reached the publisher
            if self._is_publisher_url(final_url, doi):
                logger.info(f"Reached publisher: {final_url}")
                
                # Check for PDF access
                pdf_found = await self._check_pdf_access(page)
                
                return {
                    "final_url": final_url,
                    "resolver_url": openurl,
                    "access_type": "stealth_resolved",
                    "success": pdf_found,
                    "has_pdf": pdf_found,
                }
            
            # Still at resolver - look for links
            logger.info("Looking for resolver links...")
            
            # Common resolver link patterns
            link_selectors = [
                f'a[href*="{doi}"]',
                'a:has-text("Full Text")',
                'a:has-text("Get Full Text")',
                'a:has-text("View Article")',
                'a:has-text("Access Article")',
                '.full-text-link',
                'a[class*="fulltext"]',
            ]
            
            for selector in link_selectors:
                try:
                    link = await page.wait_for_selector(selector, timeout=2000)
                    if link:
                        logger.info(f"Found link: {selector}")
                        await link.click()
                        await page.wait_for_timeout(3000)
                        
                        final_url = page.url
                        if self._is_publisher_url(final_url, doi):
                            pdf_found = await self._check_pdf_access(page)
                            return {
                                "final_url": final_url,
                                "resolver_url": openurl,
                                "access_type": "stealth_resolved",
                                "success": pdf_found,
                                "has_pdf": pdf_found,
                            }
                        break
                except:
                    continue
            
            # No access found
            return {
                "final_url": final_url,
                "resolver_url": openurl,
                "access_type": "stealth_no_access",
                "success": False,
            }
            
        except Exception as e:
            logger.error(f"Stealth resolution error: {e}")
            return {
                "final_url": None,
                "resolver_url": openurl,
                "access_type": "stealth_error",
                "success": False,
                "error": str(e),
            }
        finally:
            # Keep page open if not headless for inspection
            if not self.headless:
                await asyncio.sleep(5)
            await page.close()
    
    async def _check_pdf_access(self, page) -> bool:
        """Check if page has PDF download access."""
        pdf_selectors = [
            'a[href$=".pdf"]',
            'a:has-text("Download PDF")',
            'a:has-text("PDF")',
            'button:has-text("Download")',
            'a[data-track-action="download pdf"]',
            '.pdf-link',
        ]
        
        for selector in pdf_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=1000)
                if element:
                    return True
            except:
                continue
        
        return False
    
    async def cleanup(self):
        """Clean up browser resources."""
        await self.stealth_browser.cleanup()


async def main():
    """Test stealthy OpenURL resolver."""
    
    # Initialize authentication
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Get resolver URL
    resolver_url = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    print("OpenURL Resolution with ZenRows Stealth")
    print("=" * 50)
    print(f"\nResolver: {resolver_url}")
    print("\nFeatures:")
    print("✅ Local browser control")
    print("✅ ZenRows anti-bot bypass")
    print("✅ Manual authentication support")
    print("✅ Clean residential IPs\n")
    
    # Create stealthy resolver
    resolver = StealthyOpenURLResolver(
        auth_manager,
        resolver_url,
        headless=False  # Show browser for manual auth
    )
    
    # DOIs to resolve
    dois = [
        "10.1002/hipo.22488",
        "10.1038/nature12373",
        "10.1016/j.neuron.2018.01.048",
        "10.1126/science.1172133",
        "10.1073/pnas.0608765104",  # Known anti-bot issues
    ]
    
    print(f"Testing {len(dois)} DOIs:\n")
    
    try:
        # Test single resolution
        print(f"1. Testing single DOI: {dois[0]}")
        result = await resolver._resolve_single_async(doi=dois[0])
        
        if result:
            print(f"   Success: {result['success']}")
            print(f"   Final URL: {result.get('final_url', 'N/A')}")
            print(f"   Access type: {result.get('access_type', 'N/A')}")
            print(f"   Has PDF: {result.get('has_pdf', False)}")
        
        print("\n2. Testing batch resolution:")
        
        # Resolve multiple DOIs
        results = []
        for i, doi in enumerate(dois[1:], 2):
            print(f"\n   [{i}/{len(dois)}] Resolving {doi}")
            result = await resolver._resolve_single_async(doi=doi)
            results.append(result)
            
            if result:
                print(f"   Success: {result['success']}")
                if result['success']:
                    print(f"   ✅ PDF access available")
                else:
                    print(f"   ❌ No PDF access")
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        # Summary
        print("\n" + "="*50)
        print("Summary:")
        success_count = sum(1 for r in results if r and r.get('success'))
        print(f"✅ Successful resolutions: {success_count}/{len(results)}")
        
        print("\nResolution types:")
        types = {}
        for r in results:
            if r:
                access_type = r.get('access_type', 'unknown')
                types[access_type] = types.get(access_type, 0) + 1
        
        for access_type, count in types.items():
            print(f"  - {access_type}: {count}")
        
    finally:
        await resolver.cleanup()
        print("\n✅ Browser closed")


if __name__ == "__main__":
    asyncio.run(main())

# EOF