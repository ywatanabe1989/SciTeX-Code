#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:45:00 (ywatanabe)"
# File: ./.dev/zenrows_cookie_intercept_resolver.py
# ----------------------------------------
"""Cookie transfer implementation using intercept pattern as suggested.

This implements the approach from suggestions.md using request interception
to transfer cookies from local authenticated browser to ZenRows API.
"""

import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Route
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsCookieInterceptResolver:
    """Resolves URLs using local auth + ZenRows proxy with cookie transfer."""
    
    PUBLISHER_DOMAINS = [
        "nature.com",
        "sciencedirect.com", 
        "elsevier.com",
        "wiley.com",
        "onlinelibrary.wiley.com",
        "science.org",
        "pnas.org",
        "cell.com",
        "springer.com",
        "tandfonline.com",
        "acs.org",
        "academic.oup.com"
    ]
    
    def __init__(self, zenrows_api_key: str):
        self.api_key = zenrows_api_key
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.intercepted_urls: Set[str] = set()
        
    async def initialize(self):
        """Initialize browser for local authentication."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Need to see auth
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context()
        
    async def handle_route(self, route: Route):
        """Intercept requests to publishers and proxy through ZenRows with cookies."""
        request_url = route.request.url
        
        # Check if this is a publisher request
        is_publisher_request = any(
            domain in request_url for domain in self.PUBLISHER_DOMAINS
        )
        
        if not is_publisher_request:
            # Not a publisher, continue normally
            await route.continue_()
            return
            
        logger.info(f"🎯 Intercepting publisher request: {request_url}")
        
        # Get cookies from the browser context
        cookies_list = await route.request.context.cookies()
        
        # Format cookies for HTTP header
        cookie_string = "; ".join([
            f"{c['name']}={c['value']}" 
            for c in cookies_list
        ])
        
        logger.info(f"🍪 Sending {len(cookies_list)} cookies to ZenRows")
        
        # Prepare ZenRows API request
        params = {
            "url": request_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string
        }
        
        try:
            # Make request through ZenRows
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        logger.info("✅ ZenRows successfully fetched the page")
                        
                        # Get response data
                        body = await response.read()
                        headers = dict(response.headers)
                        
                        # Remove some headers that might cause issues
                        headers.pop('content-encoding', None)
                        headers.pop('transfer-encoding', None)
                        
                        # Fulfill the request with ZenRows response
                        await route.fulfill(
                            status=response.status,
                            headers=headers,
                            body=body
                        )
                        
                        # Track successful intercept
                        self.intercepted_urls.add(request_url)
                        
                    else:
                        logger.error(f"❌ ZenRows returned status {response.status}")
                        # Let the request continue normally as fallback
                        await route.continue_()
                        
        except Exception as e:
            logger.error(f"❌ Error during ZenRows request: {e}")
            # Fallback to normal request
            await route.continue_()
            
    async def resolve_with_intercept(self, doi_url: str) -> Dict:
        """Resolve DOI URL using intercept pattern.
        
        Args:
            doi_url: DOI URL to resolve (e.g., https://doi.org/10.1038/nature12373)
            
        Returns:
            Dict with resolution results
        """
        page = await self.context.new_page()
        
        # Enable request interception
        await page.context.route("**/*", self.handle_route)
        
        try:
            logger.info(f"🌐 Navigating to {doi_url}")
            
            # Navigate to DOI URL - this will trigger auth flow
            await page.goto(doi_url, wait_until='domcontentloaded')
            
            # Wait for user to complete authentication
            print("\n" + "="*60)
            print("⏳ Please complete authentication if prompted")
            print("   The page will automatically follow redirects")
            print("   Press Enter when you reach the final article page...")
            print("="*60)
            
            await asyncio.get_event_loop().run_in_executor(None, input)
            
            # Get final URL and check status
            final_url = page.url
            title = await page.title()
            
            logger.info(f"📍 Final URL: {final_url}")
            logger.info(f"📄 Page title: {title}")
            
            # Check if we intercepted any requests
            intercepted_count = len(self.intercepted_urls)
            logger.info(f"🎯 Intercepted {intercepted_count} publisher requests")
            
            # Check page content for access
            content = await page.content()
            
            # Access indicators
            has_access = any(
                indicator in content.lower()
                for indicator in [
                    'full text', 'download pdf', 'view pdf',
                    'download article', 'article pdf'
                ]
            )
            
            # Blocked indicators
            is_blocked = any(
                indicator in content.lower()
                for indicator in [
                    'access denied', 'purchase article',
                    'get access', 'subscribe to journal'
                ]
            )
            
            # Save screenshot
            screenshot_path = f".dev/intercept_{urlparse(final_url).netloc}.png"
            await page.screenshot(path=screenshot_path)
            
            return {
                'success': has_access and not is_blocked,
                'initial_url': doi_url,
                'final_url': final_url,
                'title': title,
                'intercepted_requests': intercepted_count,
                'has_access': has_access,
                'is_blocked': is_blocked,
                'screenshot': screenshot_path
            }
            
        finally:
            # Disable interception
            await page.context.unroute("**/*", self.handle_route)
            await page.close()
            
    async def cleanup(self):
        """Clean up resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def test_intercept_pattern():
    """Test the intercept pattern with a paper."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsCookieInterceptResolver(api_key)
    
    try:
        await resolver.initialize()
        
        # Test papers
        test_papers = [
            {
                'doi': '10.1038/nature12373',
                'name': 'Nature',
                'description': 'Nature - often requires complex auth'
            },
            {
                'doi': '10.1126/science.1172133',
                'name': 'Science',
                'description': 'Science - strict bot detection'
            },
            {
                'doi': '10.1016/j.neuron.2018.01.048',
                'name': 'Neuron',
                'description': 'Elsevier - strong anti-bot measures'
            }
        ]
        
        print("\n🧪 ZenRows Cookie Intercept Test")
        print("This test will:")
        print("1. Navigate to DOI URL in local browser")
        print("2. Intercept requests to publishers")
        print("3. Forward them through ZenRows with cookies")
        print("4. Return the content to your browser")
        
        results = []
        
        for paper in test_papers:
            print(f"\n{'='*60}")
            print(f"Testing: {paper['name']}")
            print(f"DOI: {paper['doi']}")
            print(f"Challenge: {paper['description']}")
            print('='*60)
            
            doi_url = f"https://doi.org/{paper['doi']}"
            
            result = await resolver.resolve_with_intercept(doi_url)
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   Success: {'✅' if result['success'] else '❌'}")
            print(f"   Final URL: {result['final_url']}")
            print(f"   Intercepted requests: {result['intercepted_requests']}")
            print(f"   Has access: {result['has_access']}")
            print(f"   Is blocked: {result['is_blocked']}")
            
            results.append((paper['name'], result))
            
            # Wait between papers
            if paper != test_papers[-1]:
                print("\n⏳ Waiting before next paper...")
                await asyncio.sleep(3)
                
        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        
        successful = sum(1 for _, r in results if r['success'])
        print(f"\nSuccess rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
        
        for name, result in results:
            status = "✅" if result['success'] else "❌"
            intercepts = result['intercepted_requests']
            print(f"{status} {name} (intercepted {intercepts} requests)")
            
    finally:
        await resolver.cleanup()


if __name__ == "__main__":
    asyncio.run(test_intercept_pattern())