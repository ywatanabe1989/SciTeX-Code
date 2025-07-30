#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:55:00 (ywatanabe)"
# File: ./.dev/zenrows_complete_resolver.py
# ----------------------------------------
"""Complete step-by-step URL resolver using ZenRows with cookie authentication.

This combines:
1. Local authentication capture
2. Cookie validation via ZenRows
3. Publisher URL resolution with authenticated cookies
"""

import asyncio
import json
import aiohttp
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsCompleteResolver:
    """Complete resolver with authentication, validation, and URL resolution."""
    
    def __init__(self, api_key: str, visible_browser: bool = True):
        self.api_key = api_key
        self.visible_browser = visible_browser
        self.session_dir = Path.home() / ".scitex/scholar/zenrows_sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.browser: Optional[Browser] = None
        
    async def initialize(self):
        """Initialize Playwright for local authentication."""
        self.playwright = await async_playwright().start()
        
    async def cleanup(self):
        """Clean up resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    # Step 1: Capture authentication cookies locally
    async def capture_auth_cookies(self, start_url: str) -> Tuple[List[Dict], str]:
        """Capture authentication cookies using local browser.
        
        Args:
            start_url: URL to start authentication (e.g., DOI URL)
            
        Returns:
            Tuple of (cookies, final_url_after_auth)
        """
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(
                headless=not self.visible_browser,
                args=['--disable-blink-features=AutomationControlled']
            )
            
        context = await self.browser.new_context()
        page = await context.new_page()
        
        logger.info(f"🌐 Opening {start_url} for authentication")
        await page.goto(start_url, wait_until='domcontentloaded')
        
        print("\n" + "="*60)
        print("⏳ Please complete authentication in the browser")
        print("   This may include:")
        print("   - Institutional login")
        print("   - OpenAthens/Shibboleth authentication")
        print("   - Two-factor authentication if required")
        print("\n   Press Enter when you see the article page...")
        print("="*60)
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        # Capture cookies and final URL
        cookies = await context.cookies()
        final_url = page.url
        
        logger.info(f"✅ Captured {len(cookies)} cookies")
        logger.info(f"📍 Final URL: {final_url}")
        
        await page.close()
        await context.close()
        
        return cookies, final_url
        
    # Step 2: Validate cookies using ZenRows
    async def validate_cookies_zenrows(self, cookies: List[Dict]) -> bool:
        """Validate cookies using ZenRows API.
        
        Args:
            cookies: List of cookie dictionaries
            
        Returns:
            True if cookies are valid
        """
        # Format cookies
        cookie_string = "; ".join([
            f"{c['name']}={c['value']}" 
            for c in cookies
        ])
        
        # Test with OpenAthens check URL
        test_url = "https://my.openathens.net/?passiveLogin=false"
        
        params = {
            "url": test_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string
        }
        
        logger.info("🔍 Validating cookies via ZenRows...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"ZenRows returned status {response.status}")
                        return False
                        
                    content = await response.text()
                    
                    # Check for authentication success
                    is_authenticated = any(
                        indicator in content.lower()
                        for indicator in ["log out", "sign out", "your account", "dashboard"]
                    ) and not any(
                        indicator in content.lower()
                        for indicator in ["sign in", "log in", "enter password"]
                    )
                    
                    if is_authenticated:
                        logger.info("✅ Cookies validated successfully")
                    else:
                        logger.warning("❌ Cookies appear to be invalid")
                        
                    return is_authenticated
                    
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
            
    # Step 3: Resolve publisher URL with authenticated cookies
    async def resolve_publisher_url(
        self, 
        target_url: str,
        cookies: List[Dict]
    ) -> Dict:
        """Resolve publisher URL using ZenRows with cookies.
        
        Args:
            target_url: Publisher URL to access
            cookies: Authenticated cookies
            
        Returns:
            Dict with resolution results
        """
        # Format cookies
        cookie_string = "; ".join([
            f"{c['name']}={c['value']}" 
            for c in cookies
        ])
        
        params = {
            "url": target_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string,
            "autoparse": "false"  # We want raw HTML
        }
        
        logger.info(f"🎯 Resolving {target_url} with cookies via ZenRows...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"ZenRows returned status {response.status}",
                            "url": target_url
                        }
                        
                    content = await response.text()
                    
                    # Get final URL from headers if available
                    final_url = response.headers.get('Zr-Final-Url', target_url)
                    
                    # Analyze content for access
                    content_lower = content.lower()
                    
                    has_access = any(
                        indicator in content_lower
                        for indicator in [
                            "full text", "download pdf", "view pdf",
                            "download article", "article pdf"
                        ]
                    )
                    
                    is_blocked = any(
                        indicator in content_lower
                        for indicator in [
                            "access denied", "purchase article",
                            "subscribe", "get access", "buy article"
                        ]
                    )
                    
                    # Save content snippet for debugging
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    snippet_file = self.session_dir / f"content_{timestamp}.html"
                    with open(snippet_file, 'w', encoding='utf-8') as f:
                        f.write(content[:10000])  # First 10KB
                        
                    return {
                        "success": has_access and not is_blocked,
                        "url": target_url,
                        "final_url": final_url,
                        "has_access": has_access,
                        "is_blocked": is_blocked,
                        "content_snippet": str(snippet_file)
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": target_url
            }
            
    # Complete workflow
    async def resolve_doi(self, doi: str) -> Dict:
        """Complete workflow to resolve a DOI.
        
        Args:
            doi: DOI to resolve
            
        Returns:
            Dict with complete resolution results
        """
        doi_url = f"https://doi.org/{doi}"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Resolving DOI: {doi}")
        logger.info('='*60)
        
        # Step 1: Capture authentication
        cookies, auth_final_url = await self.capture_auth_cookies(doi_url)
        
        # Step 2: Validate cookies
        is_valid = await self.validate_cookies_zenrows(cookies)
        
        if not is_valid:
            logger.warning("⚠️  Cookies validation failed, but continuing anyway...")
            
        # Step 3: Resolve publisher URL
        result = await self.resolve_publisher_url(auth_final_url, cookies)
        
        # Add additional info
        result['doi'] = doi
        result['cookies_valid'] = is_valid
        result['cookie_count'] = len(cookies)
        
        return result


async def test_complete_workflow():
    """Test the complete resolution workflow."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsCompleteResolver(api_key, visible_browser=True)
    
    try:
        await resolver.initialize()
        
        # Test papers
        test_dois = [
            ("10.1038/nature12373", "Nature"),
            ("10.1002/hipo.22488", "Hippocampus"),
            ("10.1016/j.neuron.2018.01.048", "Neuron")
        ]
        
        print("\n🧪 Complete ZenRows Resolution Test")
        print("This test will:")
        print("1. Open DOI URL in local browser for authentication")
        print("2. Validate captured cookies via ZenRows")
        print("3. Access publisher URL via ZenRows with cookies")
        print("4. Check for full-text access")
        
        results = []
        
        for doi, name in test_dois:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print('='*60)
            
            result = await resolver.resolve_doi(doi)
            
            # Display results
            print(f"\n📊 Results for {name}:")
            print(f"   Success: {'✅' if result['success'] else '❌'}")
            print(f"   Cookies valid: {'✅' if result['cookies_valid'] else '❌'}")
            print(f"   Has access: {result.get('has_access', False)}")
            print(f"   Is blocked: {result.get('is_blocked', False)}")
            print(f"   Final URL: {result.get('final_url', 'N/A')}")
            
            if result.get('error'):
                print(f"   Error: {result['error']}")
                
            results.append((name, result))
            
            # Wait between papers
            if doi != test_dois[-1][0]:
                print("\n⏳ Waiting before next paper...")
                await asyncio.sleep(5)
                
        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        
        successful = sum(1 for _, r in results if r['success'])
        print(f"\nSuccess rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
        
        for name, result in results:
            status = "✅" if result['success'] else "❌"
            cookies = "✅" if result['cookies_valid'] else "❌"
            print(f"{status} {name} (cookies: {cookies})")
            
    finally:
        await resolver.cleanup()


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())