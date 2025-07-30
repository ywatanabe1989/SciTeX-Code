#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:35:00 (ywatanabe)"
# File: ./.dev/zenrows_browser_manager_enhanced.py
# ----------------------------------------
"""Enhanced ZenRows browser manager with proper cookie handling.

This implementation focuses on the cookie transfer mechanism that was
identified as the main blocker in the previous integration attempts.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs
from playwright.async_api import Browser, BrowserContext, Page, Cookie
import os

logger = logging.getLogger(__name__)


class ZenRowsBrowserManager:
    """Enhanced browser manager with ZenRows integration and cookie support."""
    
    def __init__(self, api_key: str, visible: bool = False):
        """Initialize ZenRows browser manager.
        
        Args:
            api_key: ZenRows API key
            visible: Whether to show browser UI (for debugging)
        """
        self.api_key = api_key
        self.visible = visible
        self.zenrows_browser: Optional[Browser] = None
        self.local_browser: Optional[Browser] = None
        self._cookie_jar: Dict[str, List[Cookie]] = {}
        
    async def get_authenticated_browser(self) -> Browser:
        """Get or create ZenRows browser instance."""
        if not self.zenrows_browser:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            
            # Connect to ZenRows browser
            self.zenrows_browser = await playwright.chromium.connect_over_cdp(
                f"wss://browser.zenrows.com?apikey={self.api_key}"
            )
            
        return self.zenrows_browser
        
    async def get_local_browser(self) -> Browser:
        """Get or create local browser for authentication."""
        if not self.local_browser:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            
            self.local_browser = await playwright.chromium.launch(
                headless=not self.visible,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
        return self.local_browser
        
    async def create_authenticated_context(self, cookies: Optional[List[Dict]] = None) -> BrowserContext:
        """Create a browser context with authentication cookies.
        
        Args:
            cookies: Optional list of cookies to add to context
            
        Returns:
            Configured browser context
        """
        browser = await self.get_authenticated_browser()
        
        # Create context with standard options
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True
        )
        
        # Add cookies if provided
        if cookies:
            await self._add_cookies_to_context(context, cookies)
            
        return context
        
    async def _add_cookies_to_context(self, context: BrowserContext, cookies: List[Dict]):
        """Add cookies to browser context with proper formatting.
        
        Args:
            context: Browser context to add cookies to
            cookies: List of cookie dictionaries
        """
        formatted_cookies = []
        
        for cookie in cookies:
            # Ensure required fields
            if not all(k in cookie for k in ['name', 'value', 'domain']):
                continue
                
            formatted = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie.get('path', '/')
            }
            
            # Add optional fields if present
            optional_fields = ['expires', 'httpOnly', 'secure', 'sameSite']
            for field in optional_fields:
                if field in cookie:
                    formatted[field] = cookie[field]
                    
            formatted_cookies.append(formatted)
            
        if formatted_cookies:
            await context.add_cookies(formatted_cookies)
            logger.info(f"Added {len(formatted_cookies)} cookies to context")
            
    async def authenticate_and_capture_cookies(self, auth_url: str, wait_for_selector: Optional[str] = None) -> List[Dict]:
        """Authenticate in local browser and capture cookies.
        
        Args:
            auth_url: URL to authenticate at
            wait_for_selector: Optional selector to wait for after auth
            
        Returns:
            List of captured cookies
        """
        browser = await self.get_local_browser()
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            logger.info(f"Authenticating at: {auth_url}")
            await page.goto(auth_url)
            
            if wait_for_selector:
                # Wait for specific element
                await page.wait_for_selector(wait_for_selector, timeout=300000)  # 5 min timeout
            else:
                # Manual wait
                print("\n⏳ Please complete authentication in the browser...")
                print("   Press Enter when done...")
                await asyncio.get_event_loop().run_in_executor(None, input)
                
            # Capture cookies
            cookies = await context.cookies()
            logger.info(f"Captured {len(cookies)} cookies")
            
            # Store in cookie jar by domain
            for cookie in cookies:
                domain = cookie.get('domain', '').lstrip('.')
                if domain not in self._cookie_jar:
                    self._cookie_jar[domain] = []
                self._cookie_jar[domain].append(cookie)
                
            return cookies
            
        finally:
            await page.close()
            await context.close()
            
    def get_cookies_for_url(self, url: str) -> List[Dict]:
        """Get relevant cookies for a specific URL.
        
        Args:
            url: Target URL
            
        Returns:
            List of relevant cookies
        """
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        
        relevant_cookies = []
        
        # Check all stored domains
        for domain, cookies in self._cookie_jar.items():
            # Check if cookie domain matches target
            if (domain == hostname or 
                hostname.endswith('.' + domain) or
                domain.endswith('.' + hostname)):
                relevant_cookies.extend(cookies)
                
        # Remove duplicates by name
        unique_cookies = {}
        for cookie in relevant_cookies:
            unique_cookies[cookie['name']] = cookie
            
        return list(unique_cookies.values())
        
    async def navigate_with_cookies(self, url: str, cookies: Optional[List[Dict]] = None) -> Optional[Page]:
        """Navigate to URL using ZenRows with cookies.
        
        Args:
            url: Target URL
            cookies: Optional cookies (will auto-detect if not provided)
            
        Returns:
            Page object if successful
        """
        # Get cookies for URL if not provided
        if not cookies:
            cookies = self.get_cookies_for_url(url)
            
        # Create context with cookies
        context = await self.create_authenticated_context(cookies)
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url} with {len(cookies)} cookies")
            
            # Navigate
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response:
                logger.info(f"Response status: {response.status}")
                
                # Check if we hit a paywall or auth page
                content = await page.content()
                
                auth_indicators = ['sign in', 'log in', 'access through your institution']
                if any(indicator in content.lower() for indicator in auth_indicators):
                    logger.warning("Authentication may be required")
                    
                access_indicators = ['full text', 'download pdf', 'view pdf']
                if any(indicator in content.lower() for indicator in access_indicators):
                    logger.info("Access indicators found - authentication may be working")
                    
            return page
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            await page.close()
            return None
            
    async def extract_pdf_urls(self, page: Page) -> List[str]:
        """Extract PDF URLs from a page.
        
        Args:
            page: Page to extract from
            
        Returns:
            List of PDF URLs found
        """
        pdf_urls = []
        
        # Common PDF link patterns
        pdf_selectors = [
            'a[href$=".pdf"]',
            'a[href*="/pdf/"]',
            'a[href*="pdf"][href*="download"]',
            'a:has-text("Download PDF")',
            'a:has-text("View PDF")',
            'a:has-text("Full Text PDF")',
            'button:has-text("Download")',
            'a[data-track-action="download pdf"]'
        ]
        
        for selector in pdf_selectors:
            try:
                elements = await page.locator(selector).all()
                
                for elem in elements:
                    href = await elem.get_attribute('href')
                    if href:
                        # Make absolute URL
                        if not href.startswith('http'):
                            base_url = page.url.split('?')[0]
                            base_url = '/'.join(base_url.split('/')[:3])
                            href = base_url + '/' + href.lstrip('/')
                            
                        if href not in pdf_urls:
                            pdf_urls.append(href)
                            
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                
        logger.info(f"Found {len(pdf_urls)} PDF URLs")
        return pdf_urls
        
    async def download_with_retry(self, url: str, max_attempts: int = 3) -> Optional[Page]:
        """Download with retry logic and cookie refresh.
        
        Args:
            url: URL to download
            max_attempts: Maximum retry attempts
            
        Returns:
            Page object if successful
        """
        for attempt in range(max_attempts):
            logger.info(f"Attempt {attempt + 1}/{max_attempts} for {url}")
            
            # Try with current cookies
            page = await self.navigate_with_cookies(url)
            
            if page:
                # Check if we have access
                content = await page.content()
                
                # If we see paywall, try to re-authenticate
                if 'purchase' in content.lower() or 'subscribe' in content.lower():
                    logger.warning("Paywall detected, attempting re-authentication")
                    await page.close()
                    
                    # Try to refresh auth
                    auth_url = url  # Use same URL for auth
                    new_cookies = await self.authenticate_and_capture_cookies(auth_url)
                    
                    # Retry with new cookies
                    continue
                    
                # Success
                return page
                
            # Wait before retry
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        return None
        
    async def cleanup(self):
        """Clean up browser resources."""
        if self.zenrows_browser:
            await self.zenrows_browser.close()
            self.zenrows_browser = None
            
        if self.local_browser:
            await self.local_browser.close()
            self.local_browser = None


async def test_enhanced_manager():
    """Test the enhanced ZenRows browser manager."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    manager = ZenRowsBrowserManager(api_key, visible=True)
    
    try:
        # Test DOI
        doi = "10.1038/nature12373"
        url = f"https://doi.org/{doi}"
        
        print(f"\n🧪 Testing enhanced cookie transfer for: {doi}")
        print("=" * 60)
        
        # Step 1: Authenticate and capture cookies
        print("\n1️⃣ Authenticating locally...")
        cookies = await manager.authenticate_and_capture_cookies(url)
        print(f"   Captured {len(cookies)} cookies")
        
        # Step 2: Navigate with ZenRows
        print("\n2️⃣ Accessing with ZenRows...")
        page = await manager.navigate_with_cookies(url, cookies)
        
        if page:
            print(f"   ✅ Successfully navigated to: {page.url}")
            
            # Step 3: Extract PDF URLs
            print("\n3️⃣ Looking for PDF links...")
            pdf_urls = await manager.extract_pdf_urls(page)
            
            if pdf_urls:
                print(f"   ✅ Found {len(pdf_urls)} PDF URLs:")
                for pdf_url in pdf_urls[:3]:
                    print(f"      - {pdf_url}")
            else:
                print("   ❌ No PDF URLs found")
                
            # Save screenshot
            await page.screenshot(path=".dev/enhanced_manager_test.png")
            print("\n📸 Screenshot saved: .dev/enhanced_manager_test.png")
            
            await page.close()
            
        else:
            print("   ❌ Failed to navigate")
            
    finally:
        await manager.cleanup()
        

if __name__ == "__main__":
    asyncio.run(test_enhanced_manager())