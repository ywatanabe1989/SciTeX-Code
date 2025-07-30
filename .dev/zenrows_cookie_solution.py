#!/usr/bin/env python3
"""Working ZenRows cookie transfer implementation."""

import asyncio
import aiohttp
import os
from typing import Dict, List
from playwright.async_api import async_playwright

class ZenRowsCookieResolver:
    """Resolves URLs with cookie authentication via ZenRows."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def resolve_with_cookies(self, url: str, cookies: List[Dict]) -> Dict:
        """Resolve URL using ZenRows REST API with cookies."""
        
        # Format cookies for HTTP header
        cookie_string = "; ".join([
            f"{c['name']}={c['value']}" 
            for c in cookies
        ])
        
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    content = await response.text()
                    return {
                        "success": True,
                        "content": content,
                        "final_url": response.headers.get('Zr-Final-Url', url)
                    }
                else:
                    return {"success": False, "error": f"Status {response.status}"}
                    
    async def capture_auth_cookies(self, url: str) -> List[Dict]:
        """Capture cookies from local authentication."""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(url)
        
        print("Please complete authentication and press Enter...")
        await asyncio.get_event_loop().run_in_executor(None, input)
        
        cookies = await context.cookies()
        
        await browser.close()
        await playwright.stop()
        
        return cookies

async def test():
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    resolver = ZenRowsCookieResolver(api_key)
    
    # Test DOI
    doi_url = "https://doi.org/10.1038/nature12373"
    
    # Step 1: Get cookies from auth
    cookies = await resolver.capture_auth_cookies(doi_url)
    print(f"Captured {len(cookies)} cookies")
    
    # Step 2: Resolve with ZenRows
    result = await resolver.resolve_with_cookies(doi_url, cookies)
    
    if result["success"]:
        print(f"✅ Success! Final URL: {result['final_url']}")
        
        # Check for access
        content = result["content"].lower()
        has_access = "full text" in content or "download pdf" in content
        is_blocked = "purchase" in content or "get access" in content
        
        print(f"Has access: {has_access}")
        print(f"Is blocked: {is_blocked}")
    else:
        print(f"❌ Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test())