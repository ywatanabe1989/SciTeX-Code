#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:40:00 (ywatanabe)"
# File: ./.dev/zenrows_url_resolver_with_cookies.py
# ----------------------------------------
"""Focused implementation: Resolve publisher URLs with authentication cookies via ZenRows.

This specifically addresses the cookie transfer problem to bypass bot detection
and CAPTCHA layers when accessing publisher sites.
"""

import asyncio
import os
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsURLResolver:
    """Resolves URLs to final publisher pages using ZenRows with authentication cookies."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.playwright = None
        self.local_browser: Optional[Browser] = None
        self.zenrows_browser: Optional[Browser] = None
        
    async def initialize(self):
        """Initialize Playwright and browsers."""
        self.playwright = await async_playwright().start()
        
    async def get_local_browser(self) -> Browser:
        """Get local browser for authentication."""
        if not self.local_browser:
            self.local_browser = await self.playwright.chromium.launch(
                headless=False,  # Need to see auth process
                args=['--disable-blink-features=AutomationControlled']
            )
        return self.local_browser
        
    async def get_zenrows_browser(self) -> Browser:
        """Get ZenRows browser for bypassing bot detection."""
        if not self.zenrows_browser:
            logger.info("Connecting to ZenRows browser...")
            self.zenrows_browser = await self.playwright.chromium.connect_over_cdp(
                f"wss://browser.zenrows.com?apikey={self.api_key}"
            )
            logger.info("✅ Connected to ZenRows")
        return self.zenrows_browser
        
    async def authenticate_and_get_cookies(self, auth_url: str) -> Tuple[List[Dict], str]:
        """Authenticate locally and capture cookies.
        
        Returns:
            Tuple of (cookies, final_url_after_auth)
        """
        browser = await self.get_local_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        logger.info(f"🔐 Opening authentication URL: {auth_url}")
        await page.goto(auth_url, wait_until='domcontentloaded')
        
        print("\n" + "="*60)
        print("⏳ Please complete authentication in the browser")
        print("   (login with institutional credentials if prompted)")
        print("   Press Enter when you reach the final article page...")
        print("="*60)
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        # Get cookies and final URL
        cookies = await context.cookies()
        final_url = page.url
        
        logger.info(f"✅ Captured {len(cookies)} cookies")
        logger.info(f"📍 Final URL after auth: {final_url}")
        
        # Debug: Show some cookie info
        logger.debug("Cookie domains captured:")
        domains = set(c.get('domain', '') for c in cookies)
        for domain in sorted(domains):
            count = sum(1 for c in cookies if c.get('domain', '') == domain)
            logger.debug(f"  - {domain}: {count} cookies")
        
        await page.close()
        await context.close()
        
        return cookies, final_url
        
    async def resolve_with_zenrows(self, target_url: str, cookies: List[Dict]) -> Dict:
        """Resolve URL using ZenRows with cookies.
        
        Args:
            target_url: URL to access
            cookies: Authentication cookies
            
        Returns:
            Dict with resolution results
        """
        browser = await self.get_zenrows_browser()
        context = await browser.new_context()
        
        # Add cookies to context
        logger.info(f"🍪 Adding {len(cookies)} cookies to ZenRows context")
        
        # Format cookies for Playwright
        formatted_cookies = []
        for cookie in cookies:
            formatted = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie.get('path', '/')
            }
            
            # Optional fields
            if 'expires' in cookie and cookie['expires'] > 0:
                formatted['expires'] = int(cookie['expires'])
            if 'httpOnly' in cookie:
                formatted['httpOnly'] = bool(cookie['httpOnly'])
            if 'secure' in cookie:
                formatted['secure'] = bool(cookie['secure'])
            if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                formatted['sameSite'] = cookie['sameSite']
                
            formatted_cookies.append(formatted)
            
        await context.add_cookies(formatted_cookies)
        
        page = await context.new_page()
        
        try:
            logger.info(f"🌐 Navigating to {target_url} via ZenRows...")
            
            # Navigate with longer timeout for bot checks
            response = await page.goto(
                target_url, 
                wait_until='domcontentloaded',
                timeout=60000  # 60 seconds
            )
            
            # Wait a bit for any redirects or bot checks
            await page.wait_for_timeout(5000)
            
            final_url = page.url
            status = response.status if response else None
            
            logger.info(f"📍 Final URL: {final_url}")
            logger.info(f"📊 Status: {status}")
            
            # Check page content for access indicators
            content = await page.content()
            
            # Check for authentication success
            auth_success_indicators = [
                'full text', 'download pdf', 'view pdf',
                'institutional access', 'access provided',
                'log out', 'sign out'
            ]
            
            has_access = any(
                indicator in content.lower() 
                for indicator in auth_success_indicators
            )
            
            # Check for paywall/blocked access
            blocked_indicators = [
                'access denied', 'purchase article', 'subscribe',
                'get access', 'request access', 'paywall',
                'please sign in', 'please log in'
            ]
            
            is_blocked = any(
                indicator in content.lower() 
                for indicator in blocked_indicators
            )
            
            # Save screenshot for debugging
            screenshot_path = f".dev/zenrows_resolved_{urlparse(target_url).netloc}.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            result = {
                'success': has_access and not is_blocked,
                'initial_url': target_url,
                'final_url': final_url,
                'status': status,
                'has_access_indicators': has_access,
                'has_blocked_indicators': is_blocked,
                'screenshot': screenshot_path
            }
            
            # Debug: Check specific cookies in page
            page_cookies = await context.cookies(final_url)
            logger.debug(f"Cookies available on final page: {len(page_cookies)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during resolution: {e}")
            return {
                'success': False,
                'initial_url': target_url,
                'error': str(e)
            }
            
        finally:
            await page.close()
            await context.close()
            
    async def cleanup(self):
        """Clean up browser instances."""
        if self.local_browser:
            await self.local_browser.close()
        if self.zenrows_browser:
            await self.zenrows_browser.close()
        if self.playwright:
            await self.playwright.stop()


async def test_single_paper(doi: str, name: str):
    """Test URL resolution for a single paper."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsURLResolver(api_key)
    
    try:
        await resolver.initialize()
        
        # Step 1: Start with DOI URL
        doi_url = f"https://doi.org/{doi}"
        
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"DOI: {doi}")
        print(f"URL: {doi_url}")
        print('='*60)
        
        # Step 2: Authenticate locally and get cookies
        cookies, auth_final_url = await resolver.authenticate_and_get_cookies(doi_url)
        
        # Step 3: Try to access the same URL via ZenRows with cookies
        print(f"\n🚀 Attempting to access via ZenRows with cookies...")
        result = await resolver.resolve_with_zenrows(auth_final_url, cookies)
        
        # Display results
        print(f"\n📊 Results:")
        print(f"   Success: {'✅' if result['success'] else '❌'}")
        print(f"   Final URL: {result.get('final_url', 'N/A')}")
        print(f"   Has access indicators: {result.get('has_access_indicators', False)}")
        print(f"   Has blocked indicators: {result.get('has_blocked_indicators', False)}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
            
        return result
        
    finally:
        await resolver.cleanup()


async def test_all_papers():
    """Test all five papers."""
    
    papers = [
        ("10.1002/hipo.22488", "Hippocampus"),
        ("10.1038/nature12373", "Nature"),
        ("10.1016/j.neuron.2018.01.048", "Neuron"),
        ("10.1126/science.1172133", "Science"),
        ("10.1073/pnas.0408942102", "PNAS")
    ]
    
    print("\n🧪 ZenRows URL Resolution Test")
    print("This test will:")
    print("1. Open each paper URL in local browser for authentication")
    print("2. Capture authentication cookies")
    print("3. Access the same URL via ZenRows with cookies")
    print("4. Check if authentication transferred successfully")
    
    results = []
    
    for doi, name in papers:
        try:
            result = await test_single_paper(doi, name)
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Failed to test {name}: {e}")
            results.append((name, {'success': False, 'error': str(e)}))
            
        # Wait between papers
        print("\n⏳ Waiting before next paper...")
        await asyncio.sleep(3)
        
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    successful = sum(1 for _, r in results if r.get('success'))
    print(f"\nSuccess rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
    
    for name, result in results:
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {name}")
        if not result.get('success') and result.get('error'):
            print(f"   Error: {result['error'][:50]}...")


if __name__ == "__main__":
    # Test single paper or all
    print("\nZenRows URL Resolution with Cookies")
    print("1. Test single paper (Nature)")
    print("2. Test all five papers")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_single_paper("10.1038/nature12373", "Nature"))
    elif choice == "2":
        asyncio.run(test_all_papers())
    else:
        print("Invalid choice")