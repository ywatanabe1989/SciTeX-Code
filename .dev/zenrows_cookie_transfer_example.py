#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-30 21:40:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/.dev/zenrows_cookie_transfer_example.py
# ----------------------------------------
"""Simple example demonstrating ZenRows cookie transfer mechanism.

This example shows the core concept:
1. Make initial request to capture cookies
2. Use captured cookies in subsequent requests
3. Maintain session with session_id
"""

import asyncio
import os
import aiohttp
from typing import Dict, Optional, Tuple


class ZenRowsCookieManager:
    """Simple cookie manager for ZenRows requests."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_id = "12345"  # ZenRows requires numeric session_id
        self.cookies: Dict[str, str] = {}
        
    def _parse_cookie_header(self, cookie_header: str) -> Dict[str, str]:
        """Parse cookie header into dictionary."""
        cookies = {}
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name.strip()] = value.strip()
        return cookies
        
    async def make_request(
        self, 
        url: str, 
        use_cookies: bool = True
    ) -> Tuple[str, Dict[str, str], int]:
        """Make request through ZenRows.
        
        Returns:
            Tuple of (content, new_cookies, status_code)
        """
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.session_id
        }
        
        headers = {}
        if use_cookies and self.cookies:
            # Send cookies as Custom Headers (per ZenRows FAQ)
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            print(f"→ Sending {len(self.cookies)} cookies")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    content = await response.text()
                    status = response.status
                    
                    # Extract cookies from response
                    zr_cookies = response.headers.get('Zr-Cookies', '')
                    new_cookies = {}
                    
                    if zr_cookies:
                        new_cookies = self._parse_cookie_header(zr_cookies)
                        self.cookies.update(new_cookies)
                        print(f"← Received {len(new_cookies)} new cookies")
                        
                    return content[:500], new_cookies, status  # Truncate content for demo
                    
        except Exception as e:
            print(f"Error: {e}")
            return "", {}, 0


async def demonstrate_cookie_transfer():
    """Demonstrate the cookie transfer mechanism."""
    
    api_key = os.environ.get("ZENROWS_API_KEY") or os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("❌ Please set ZENROWS_API_KEY or SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
        
    manager = ZenRowsCookieManager(api_key)
    
    print("ZenRows Cookie Transfer Demo")
    print("=" * 40)
    
    # Step 1: Initial request to a site that sets cookies
    print("\n1. Initial request (no cookies)")
    url1 = "https://httpbin.org/cookies/set?session=abc123&user=demo"
    content1, cookies1, status1 = await manager.make_request(url1, use_cookies=False)
    print(f"   Status: {status1}")
    print(f"   Cookies received: {list(cookies1.keys())}")
    
    # Step 2: Follow-up request with cookies
    print("\n2. Follow-up request (with cookies)")
    url2 = "https://httpbin.org/cookies"  # This endpoint shows what cookies were sent
    content2, cookies2, status2 = await manager.make_request(url2, use_cookies=True)
    print(f"   Status: {status2}")
    print(f"   Response shows we sent: {content2}")
    
    # Step 3: Simulate institutional access pattern
    print("\n3. Simulating institutional access pattern")
    
    # First, hit institutional resolver (this would set auth cookies)
    print("\n   a) Institutional resolver")
    resolver_url = "https://httpbin.org/response-headers?Set-Cookie=inst_session=xyz789"
    content3, cookies3, status3 = await manager.make_request(resolver_url)
    print(f"      Status: {status3}")
    print(f"      Total cookies now: {len(manager.cookies)}")
    
    # Then, access publisher with accumulated cookies
    print("\n   b) Publisher access with cookies")
    publisher_url = "https://httpbin.org/headers"  # Shows headers including cookies
    content4, cookies4, status4 = await manager.make_request(publisher_url)
    print(f"      Status: {status4}")
    print(f"      Cookies sent to publisher: {len(manager.cookies)}")
    
    # Summary
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"- Session ID: {manager.session_id}")
    print(f"- Total cookies accumulated: {len(manager.cookies)}")
    print(f"- Cookie names: {list(manager.cookies.keys())}")
    
    return manager


async def test_with_real_publisher():
    """Test with a real publisher URL."""
    
    api_key = os.environ.get("ZENROWS_API_KEY") or os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("❌ Please set ZENROWS_API_KEY or SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
        
    manager = ZenRowsCookieManager(api_key)
    
    print("\nTesting with Real Publisher")
    print("=" * 40)
    
    # Test with Nature
    doi = "10.1038/nature12373"
    url = f"https://doi.org/{doi}"
    
    print(f"\nAccessing: {url}")
    content, cookies, status = await manager.make_request(url)
    
    print(f"Status: {status}")
    print(f"Cookies received: {len(cookies)}")
    
    # Check if we have access indicators in content
    if content:
        has_pdf = "pdf" in content.lower()
        has_access = "full text" in content.lower() or "download" in content.lower()
        needs_auth = "sign in" in content.lower() or "log in" in content.lower()
        
        print(f"\nContent analysis:")
        print(f"- Contains 'pdf': {has_pdf}")
        print(f"- Contains 'full text/download': {has_access}")
        print(f"- Contains 'sign in/log in': {needs_auth}")
        
        
if __name__ == "__main__":
    print("Choose demo:")
    print("1. Basic cookie transfer demo")
    print("2. Real publisher test")
    
    choice = input("\nEnter choice (1 or 2): ")
    
    if choice == "1":
        asyncio.run(demonstrate_cookie_transfer())
    elif choice == "2":
        asyncio.run(test_with_real_publisher())
    else:
        print("Invalid choice")