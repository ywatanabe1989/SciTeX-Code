#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:50:00 (ywatanabe)"
# File: ./.dev/zenrows_corrected_cookie_implementation.py
# ----------------------------------------
"""Corrected ZenRows cookie implementation based on FAQ documentation.

Key insights from ZenRows FAQ:
1. Cookies are returned in Zr-Cookies header
2. Use session_id to maintain same IP
3. Send cookies as Custom Headers in subsequent requests
"""

import asyncio
import aiohttp
import os
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsCorrectedCookieResolver:
    """Corrected implementation using ZenRows cookie handling as documented."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_cookies: Dict[str, str] = {}
        self.session_id = None
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for maintaining same IP."""
        import uuid
        return str(uuid.uuid4())
        
    async def initial_request(self, url: str) -> Tuple[str, Dict[str, str]]:
        """Make initial request and capture cookies from response headers.
        
        Returns:
            Tuple of (response_content, cookies_dict)
        """
        # Generate session ID for this session
        self.session_id = self._generate_session_id()
        
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.session_id  # Maintain same IP
        }
        
        logger.info(f"Making initial request to: {url}")
        logger.info(f"Session ID: {self.session_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status != 200:
                    logger.error(f"Request failed with status: {response.status}")
                    return "", {}
                    
                content = await response.text()
                
                # Extract cookies from Zr-Cookies header
                zr_cookies = response.headers.get('Zr-Cookies', '')
                final_url = response.headers.get('Zr-Final-Url', url)
                
                logger.info(f"Final URL: {final_url}")
                
                if zr_cookies:
                    logger.info(f"Captured cookies: {zr_cookies[:50]}...")
                    # Parse cookies
                    cookies_dict = self._parse_cookie_header(zr_cookies)
                    self.session_cookies.update(cookies_dict)
                else:
                    logger.warning("No cookies in response headers")
                    
                return content, self.session_cookies
                
    def _parse_cookie_header(self, cookie_header: str) -> Dict[str, str]:
        """Parse cookie header string into dictionary."""
        cookies = {}
        
        # Split by semicolon and parse each cookie
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name.strip()] = value.strip()
                
        return cookies
        
    async def authenticated_request(
        self, 
        url: str, 
        cookies: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Make authenticated request using cookies as custom headers.
        
        Args:
            url: Target URL
            cookies: Cookie dict (uses session cookies if not provided)
            
        Returns:
            Dict with response details
        """
        if cookies is None:
            cookies = self.session_cookies
            
        if not cookies:
            logger.warning("No cookies available for authenticated request")
            
        # Format cookies for Custom Headers
        cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        # Build headers dict
        headers = {
            "Cookie": cookie_string
        }
        
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.session_id,  # Use same session ID
            "custom_headers": "true"  # Enable custom headers
        }
        
        logger.info(f"Making authenticated request to: {url}")
        logger.info(f"Using {len(cookies)} cookies")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                headers=headers,  # Pass cookies as headers
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"Status {response.status}",
                        "url": url
                    }
                    
                content = await response.text()
                final_url = response.headers.get('Zr-Final-Url', url)
                
                # Check for new cookies
                new_cookies = response.headers.get('Zr-Cookies', '')
                if new_cookies:
                    logger.info("Updating session cookies")
                    self.session_cookies.update(self._parse_cookie_header(new_cookies))
                    
                # Analyze content
                content_lower = content.lower()
                has_access = any(
                    indicator in content_lower
                    for indicator in ["full text", "download pdf", "view pdf"]
                )
                
                is_blocked = any(
                    indicator in content_lower
                    for indicator in ["purchase", "subscribe", "get access"]
                )
                
                return {
                    "success": has_access and not is_blocked,
                    "url": url,
                    "final_url": final_url,
                    "has_access": has_access,
                    "is_blocked": is_blocked,
                    "cookie_count": len(self.session_cookies),
                    "session_id": self.session_id
                }
                
    async def complete_flow(self, auth_url: str, target_url: str) -> Dict:
        """Complete authentication flow.
        
        Args:
            auth_url: URL for authentication (e.g., institutional login)
            target_url: Target publisher URL
            
        Returns:
            Dict with results
        """
        logger.info("=== Starting authentication flow ===")
        
        # Step 1: Initial request to capture cookies
        content, cookies = await self.initial_request(auth_url)
        
        if not cookies:
            logger.warning("No cookies captured from initial request")
            # Try target URL directly
            return await self.authenticated_request(target_url)
            
        # Step 2: Access target with cookies
        logger.info(f"\n=== Accessing target with {len(cookies)} cookies ===")
        result = await self.authenticated_request(target_url, cookies)
        
        return result


async def test_corrected_implementation():
    """Test the corrected cookie implementation."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsCorrectedCookieResolver(api_key)
    
    # Test cases
    test_cases = [
        {
            "name": "Nature",
            "doi": "10.1038/nature12373",
            "auth_url": "https://doi.org/10.1038/nature12373",
            "target_url": "https://www.nature.com/articles/nature12373"
        },
        {
            "name": "Httpbin Cookie Test",
            "doi": None,
            "auth_url": "https://httpbin.org/cookies/set?test1=value1&test2=value2",
            "target_url": "https://httpbin.org/cookies"
        }
    ]
    
    print("🧪 ZenRows Corrected Cookie Implementation Test")
    print("Based on official FAQ documentation")
    print("="*60)
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print("-"*40)
        
        if test_case['name'] == "Httpbin Cookie Test":
            # For httpbin, we can test cookie flow directly
            result = await resolver.complete_flow(
                test_case['auth_url'],
                test_case['target_url']
            )
        else:
            # For real publishers, just test direct access
            result = await resolver.authenticated_request(test_case['target_url'])
            
        print(f"\n📊 Results:")
        print(f"   Success: {'✅' if result.get('success') else '❌'}")
        print(f"   Final URL: {result.get('final_url', 'N/A')}")
        print(f"   Has access: {result.get('has_access', False)}")
        print(f"   Is blocked: {result.get('is_blocked', False)}")
        print(f"   Session cookies: {result.get('cookie_count', 0)}")
        
        # Wait between tests
        await asyncio.sleep(2)


async def test_with_authentication():
    """Test with simulated authentication flow."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsCorrectedCookieResolver(api_key)
    
    print("\n🔐 Testing with Authentication Flow")
    print("="*60)
    
    # Step 1: Simulate getting auth cookies
    print("\n1️⃣ Getting authentication cookies...")
    
    # In real scenario, this would be OpenAthens or institutional login
    # For testing, we'll use httpbin to set cookies
    auth_url = "https://httpbin.org/response-headers?Set-Cookie=auth_token%3Dsecret123%3B%20path%3D%2F"
    
    content, cookies = await resolver.initial_request(auth_url)
    print(f"   Captured {len(cookies)} cookies")
    
    # Step 2: Use cookies to access protected content
    print("\n2️⃣ Accessing protected content with cookies...")
    
    # Test if cookies are being sent
    test_url = "https://httpbin.org/cookies"
    result = await resolver.authenticated_request(test_url)
    
    print(f"\n📊 Final Results:")
    print(f"   Session ID: {result.get('session_id')}")
    print(f"   Cookie count: {result.get('cookie_count')}")
    print(f"   Success: {'✅' if result.get('success') else '❌'}")


if __name__ == "__main__":
    print("Choose test:")
    print("1. Test corrected implementation")
    print("2. Test with authentication flow")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(test_corrected_implementation())
    elif choice == "2":
        asyncio.run(test_with_authentication())
    else:
        print("Invalid choice")