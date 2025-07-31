#!/usr/bin/env python3
"""
Final working example: Resolve DOIs using ZenRows with two approaches:
1. Direct DOI resolution (works for open access)
2. Browser-based resolution (works for paywalled content with login)
"""

import os
import asyncio
import requests
from urllib.parse import urlencode
from playwright.async_api import async_playwright

class ZenRowsDOIResolver:
    """Resolve DOIs using ZenRows API and Browser."""
    
    def __init__(self, api_key, resolver_url=None):
        self.api_key = api_key
        self.resolver_url = resolver_url or "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
        self.zenrows_api_url = "https://api.zenrows.com/v1/"
        
    def try_direct_doi(self, doi):
        """Try resolving DOI directly (works for open access)."""
        print(f"\n1. Trying direct DOI resolution for {doi}...")
        
        params = {
            "url": f"https://doi.org/{doi}",
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "proxy_country": "au"
        }
        
        try:
            response = requests.get(self.zenrows_api_url, params=params, timeout=20)
            
            if response.status_code == 200:
                final_url = response.headers.get("Zr-Final-Url", "")
                
                if any(domain in final_url for domain in ["nature.com", "wiley.com", "sciencedirect.com", "science.org", "pnas.org"]):
                    print(f"  ✓ Success! Redirected to: {final_url}")
                    return {
                        "doi": doi,
                        "pdf_url": final_url,
                        "method": "direct",
                        "title": self._extract_title(response.text)
                    }
                else:
                    print(f"  ✗ Redirected to unexpected URL: {final_url}")
            else:
                print(f"  ✗ Failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
        return None
    
    async def try_browser_resolution(self, doi):
        """Use ZenRows browser for institutional access."""
        print(f"\n2. Trying browser-based resolution for {doi}...")
        
        connection_url = f"wss://browser.zenrows.com?apikey={self.api_key}&proxy_country=au"
        
        async with async_playwright() as p:
            try:
                # Connect to ZenRows browser
                browser = await p.chromium.connect_over_cdp(connection_url, timeout=120000)
                page = await browser.new_page()
                
                # Build OpenURL
                openurl = f"{self.resolver_url}?rft_id=info:doi/{doi}"
                print(f"  Navigating to: {openurl}")
                
                await page.goto(openurl, wait_until="domcontentloaded", timeout=30000)
                
                # Wait a bit for JavaScript
                await page.wait_for_timeout(3000)
                
                # Check current URL
                current_url = page.url
                print(f"  Current URL: {current_url}")
                
                # Look for PDF links or full-text indicators
                pdf_link = None
                
                # Strategy 1: Direct PDF link
                pdf_elements = await page.query_selector_all("a[href*='.pdf']")
                if pdf_elements:
                    for elem in pdf_elements:
                        href = await elem.get_attribute("href")
                        if href:
                            pdf_link = href
                            break
                
                # Strategy 2: Full-text link
                if not pdf_link:
                    full_text_selectors = [
                        "a:has-text('Full Text')",
                        "a:has-text('PDF')",
                        "a:has-text('View PDF')",
                        "a:has-text('Download PDF')"
                    ]
                    
                    for selector in full_text_selectors:
                        try:
                            elem = await page.query_selector(selector)
                            if elem:
                                href = await elem.get_attribute("href")
                                if href:
                                    pdf_link = href
                                    break
                        except:
                            continue
                
                await browser.close()
                
                if pdf_link:
                    print(f"  ✓ Found PDF link: {pdf_link}")
                    return {
                        "doi": doi,
                        "pdf_url": pdf_link,
                        "method": "browser",
                        "resolver_url": current_url
                    }
                else:
                    # Check if we reached a publisher page
                    if any(domain in current_url for domain in ["nature.com", "wiley.com", "sciencedirect.com"]):
                        print(f"  ✓ Reached publisher page: {current_url}")
                        return {
                            "doi": doi,
                            "pdf_url": current_url,
                            "method": "browser",
                            "note": "At publisher page - manual download needed"
                        }
                    else:
                        print("  ✗ No PDF link found")
                        
            except Exception as e:
                print(f"  ✗ Browser error: {e}")
                
        return None
    
    def _extract_title(self, html):
        """Extract title from HTML."""
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            title = match.group(1)
            # Clean up common patterns
            title = title.replace(" | Nature", "").replace(" - ScienceDirect", "")
            return title.strip()
        return "Unknown"
    
    async def resolve_dois(self, dois):
        """Resolve multiple DOIs using best available method."""
        results = []
        
        for doi in dois:
            print(f"\n{'='*70}")
            print(f"Resolving DOI: {doi}")
            print(f"{'='*70}")
            
            # Try direct resolution first
            result = self.try_direct_doi(doi)
            
            # If that fails, try browser
            if not result:
                result = await self.try_browser_resolution(doi)
            
            if result:
                results.append(result)
                print(f"\n✅ Successfully resolved using {result['method']} method")
            else:
                results.append({
                    "doi": doi,
                    "error": "Could not resolve",
                    "method": "none"
                })
                print(f"\n❌ Failed to resolve {doi}")
        
        return results

async def main():
    """Test DOI resolution with ZenRows."""
    
    # Get credentials
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("Error: SCITEX_SCHOLAR_ZENROWS_API_KEY not set")
        return
    
    print("ZenRows DOI Resolution - Final Working Example")
    print("=" * 70)
    
    # Test DOIs
    dois = [
        "10.1038/nature12373",      # Nature - often open
        "10.1002/hipo.22488",       # Wiley - usually paywalled
        "10.1016/j.neuron.2018.01.048",  # Elsevier - usually paywalled
        "10.1126/science.1172133",  # Science - usually paywalled
        "10.1073/pnas.0608765104",  # PNAS - often open
    ]
    
    # Create resolver
    resolver = ZenRowsDOIResolver(api_key)
    
    # Resolve DOIs
    results = await resolver.resolve_dois(dois)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if "pdf_url" in r)
    print(f"\nSuccessfully resolved: {success_count}/{len(dois)} DOIs")
    
    print("\nResults by method:")
    direct_count = sum(1 for r in results if r.get("method") == "direct")
    browser_count = sum(1 for r in results if r.get("method") == "browser")
    failed_count = sum(1 for r in results if r.get("method") == "none")
    
    print(f"  Direct resolution: {direct_count}")
    print(f"  Browser resolution: {browser_count}")
    print(f"  Failed: {failed_count}")
    
    print("\nDetailed results:")
    for result in results:
        doi = result["doi"]
        if "pdf_url" in result:
            print(f"  ✓ {doi}")
            print(f"    URL: {result['pdf_url'][:80]}...")
            print(f"    Method: {result['method']}")
        else:
            print(f"  ✗ {doi}: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("Conclusion:")
    print("- Direct DOI resolution works for open access papers")
    print("- Browser resolution needed for paywalled content")
    print("- Manual login may be required for institutional access")
    print("="*70)

if __name__ == "__main__":
    # Source environment
    import subprocess
    
    env_file = "/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src"
    result = subprocess.run(
        f"source {env_file} && env",
        shell=True,
        capture_output=True,
        text=True,
        executable="/bin/bash"
    )
    
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('SCITEX_'):
                    os.environ[key] = value
    
    # Run async main
    asyncio.run(main())