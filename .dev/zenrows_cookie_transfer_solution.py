#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:30:00 (ywatanabe)"
# File: ./.dev/zenrows_cookie_transfer_solution.py
# ----------------------------------------
"""Improved cookie transfer mechanism for ZenRows integration.

This implements a working solution for transferring cookies from local
authenticated browser sessions to ZenRows browser instances.
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

logger = logging.getLogger(__name__)


class ZenRowsCookieTransferManager:
    """Manages cookie transfer between local and ZenRows browsers."""
    
    def __init__(self, zenrows_api_key: str):
        self.api_key = zenrows_api_key
        self.local_browser: Optional[Browser] = None
        self.zenrows_browser: Optional[Browser] = None
        self.local_context: Optional[BrowserContext] = None
        self.zenrows_context: Optional[BrowserContext] = None
        
    async def initialize(self):
        """Initialize both local and ZenRows browsers."""
        playwright = await async_playwright().start()
        
        # Local browser for authentication
        self.local_browser = await playwright.chromium.launch(
            headless=False,  # Visible for auth
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # ZenRows browser for accessing content
        self.zenrows_browser = await playwright.chromium.connect_over_cdp(
            f"wss://browser.zenrows.com?apikey={self.api_key}"
        )
        
        # Create contexts
        self.local_context = await self.local_browser.new_context()
        self.zenrows_context = await self.zenrows_browser.new_context()
        
    async def authenticate_locally(self, auth_url: str) -> List[Dict]:
        """Authenticate in local browser and capture cookies.
        
        Args:
            auth_url: URL to authenticate (e.g., OpenAthens login)
            
        Returns:
            List of cookie dictionaries
        """
        page = await self.local_context.new_page()
        
        print(f"🔐 Authenticating at: {auth_url}")
        await page.goto(auth_url)
        
        # Wait for user to complete authentication
        print("⏳ Please complete authentication in the browser...")
        print("   Press Enter when done...")
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        # Capture all cookies
        cookies = await self.local_context.cookies()
        print(f"✅ Captured {len(cookies)} cookies")
        
        await page.close()
        return cookies
        
    def filter_relevant_cookies(self, cookies: List[Dict], target_url: str) -> List[Dict]:
        """Filter cookies relevant to the target domain.
        
        Args:
            cookies: List of all cookies
            target_url: Target URL to access
            
        Returns:
            Filtered list of relevant cookies
        """
        target_domain = urlparse(target_url).netloc
        relevant_cookies = []
        
        for cookie in cookies:
            cookie_domain = cookie.get('domain', '').lstrip('.')
            
            # Check if cookie applies to target domain
            if (cookie_domain == target_domain or 
                target_domain.endswith('.' + cookie_domain) or
                cookie_domain.endswith('.' + target_domain)):
                relevant_cookies.append(cookie)
                
        print(f"📍 Filtered to {len(relevant_cookies)} relevant cookies for {target_domain}")
        return relevant_cookies
        
    async def transfer_cookies_to_zenrows(self, cookies: List[Dict]):
        """Transfer cookies to ZenRows browser context.
        
        Args:
            cookies: List of cookie dictionaries to transfer
        """
        # Clean cookies for Playwright format
        cleaned_cookies = []
        
        for cookie in cookies:
            cleaned = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie.get('path', '/'),
            }
            
            # Optional fields
            if 'expires' in cookie and cookie['expires'] > 0:
                cleaned['expires'] = cookie['expires']
            if 'httpOnly' in cookie:
                cleaned['httpOnly'] = cookie['httpOnly']
            if 'secure' in cookie:
                cleaned['secure'] = cookie['secure']
            if 'sameSite' in cookie:
                cleaned['sameSite'] = cookie['sameSite']
                
            cleaned_cookies.append(cleaned)
            
        # Add cookies to ZenRows context
        await self.zenrows_context.add_cookies(cleaned_cookies)
        print(f"🍪 Transferred {len(cleaned_cookies)} cookies to ZenRows")
        
    async def access_with_cookies(self, url: str) -> Optional[Page]:
        """Access a URL using ZenRows with transferred cookies.
        
        Args:
            url: URL to access
            
        Returns:
            Page object if successful
        """
        page = await self.zenrows_context.new_page()
        
        try:
            print(f"🌐 Accessing {url} via ZenRows...")
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.ok:
                print(f"✅ Successfully accessed: {page.url}")
                return page
            else:
                print(f"❌ Failed to access: Status {response.status if response else 'None'}")
                await page.close()
                return None
                
        except Exception as e:
            print(f"❌ Error accessing URL: {e}")
            await page.close()
            return None
            
    async def verify_authentication(self, page: Page) -> bool:
        """Verify if authentication is working on the page.
        
        Args:
            page: Page to check
            
        Returns:
            True if authenticated access detected
        """
        # Check for common authentication indicators
        auth_indicators = [
            'Sign out', 'Logout', 'My Account', 'Profile',
            'Institutional access', 'Full text', 'Download PDF'
        ]
        
        content = await page.content()
        authenticated = any(indicator.lower() in content.lower() 
                          for indicator in auth_indicators)
        
        if authenticated:
            print("✅ Authentication verified - access granted")
        else:
            print("⚠️  Could not verify authentication")
            
        return authenticated
        
    async def cleanup(self):
        """Clean up browser instances."""
        if self.local_context:
            await self.local_context.close()
        if self.zenrows_context:
            await self.zenrows_context.close()
        if self.local_browser:
            await self.local_browser.close()
        if self.zenrows_browser:
            await self.zenrows_browser.close()


async def test_cookie_transfer():
    """Test the cookie transfer mechanism with a real example."""
    
    # Configuration
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    # Test with Nature paper
    auth_url = "https://www.nature.com/articles/nature12373"  # Will redirect to auth
    target_url = "https://www.nature.com/articles/nature12373"
    
    manager = ZenRowsCookieTransferManager(api_key)
    
    try:
        # Initialize browsers
        await manager.initialize()
        
        # Step 1: Authenticate locally
        cookies = await manager.authenticate_locally(auth_url)
        
        # Step 2: Filter relevant cookies
        relevant_cookies = manager.filter_relevant_cookies(cookies, target_url)
        
        # Step 3: Transfer to ZenRows
        await manager.transfer_cookies_to_zenrows(relevant_cookies)
        
        # Step 4: Access with ZenRows
        page = await manager.access_with_cookies(target_url)
        
        if page:
            # Step 5: Verify authentication
            authenticated = await manager.verify_authentication(page)
            
            # Try to find PDF link
            pdf_links = await page.locator('a[href*=".pdf"], a:has-text("Download PDF")').all()
            
            if pdf_links:
                print(f"🎉 Found {len(pdf_links)} PDF download links!")
                for link in pdf_links[:3]:  # Show first 3
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    print(f"   - {text}: {href}")
            else:
                print("❌ No PDF links found")
                
            # Save screenshot
            await page.screenshot(path=".dev/zenrows_cookie_test.png")
            print("📸 Screenshot saved: .dev/zenrows_cookie_test.png")
            
            await page.close()
            
    finally:
        await manager.cleanup()


async def test_with_doi_resolver():
    """Test cookie transfer with OpenURL resolver workflow."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    # OpenURL resolver URL (example: University of Melbourne)
    resolver_base = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    doi = "10.1038/nature12373"
    openurl = f"{resolver_base}?url_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.genre=article&rft.doi={doi}"
    
    manager = ZenRowsCookieTransferManager(api_key)
    
    try:
        await manager.initialize()
        
        # First authenticate with the resolver
        print("🔗 Step 1: Authenticate with OpenURL resolver")
        cookies = await manager.authenticate_locally(openurl)
        
        # The resolver should redirect to publisher after auth
        # Let's try to access the publisher directly with cookies
        publisher_url = f"https://doi.org/{doi}"
        
        print(f"\n🔗 Step 2: Access publisher via DOI with cookies")
        relevant_cookies = manager.filter_relevant_cookies(cookies, publisher_url)
        await manager.transfer_cookies_to_zenrows(relevant_cookies)
        
        page = await manager.access_with_cookies(publisher_url)
        
        if page:
            final_url = page.url
            print(f"📍 Final URL: {final_url}")
            
            authenticated = await manager.verify_authentication(page)
            
            # Debug: Print some page info
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # Check for paywall or access messages
            paywall_indicators = ['Purchase', 'Subscribe', 'Get access', 'Buy article']
            content = await page.content()
            
            has_paywall = any(indicator.lower() in content.lower() 
                            for indicator in paywall_indicators)
            
            if has_paywall and not authenticated:
                print("🚧 Paywall detected - authentication may not have transferred")
            
            await page.close()
            
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    print("Cookie Transfer Solution for ZenRows")
    print("=" * 50)
    print("Choose test:")
    print("1. Direct authentication test")
    print("2. OpenURL resolver workflow test")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_cookie_transfer())
    elif choice == "2":
        asyncio.run(test_with_doi_resolver())
    else:
        print("Invalid choice")