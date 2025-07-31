#!/usr/bin/env python3
"""Quick test of auth with ZenRows."""

import os
import asyncio
import json
from scitex.scholar.browser import ZenRowsAPIBrowser
from scitex.scholar.auth import AuthenticationManager

async def main():
    # Check auth
    auth_manager = AuthenticationManager()
    if not await auth_manager.authenticate():
        print("❌ No auth")
        return
    
    print("✅ Authenticated")
    auth_cookies = await auth_manager.get_auth_cookies()
    print(f"📍 Have {len(auth_cookies)} cookies")
    
    # Test one DOI
    doi = "10.1038/nature12373"
    url = f"https://doi.org/{doi}"
    
    browser = ZenRowsAPIBrowser()
    
    # Simple test without cookie injection
    print(f"\nTesting: {url}")
    
    # Use json_response to get detailed info
    params = {
        "url": url,
        "apikey": browser.api_key,
        "js_render": "true",
        "json_response": "true",
        "screenshot": "true",
        "premium_proxy": "true",
        "antibot": "true",
        "wait": "5000",
        "js_instructions": json.dumps([
            {"wait": 3000},
            {"wait_event": "networkidle"}
        ])
    }
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.zenrows.com/v1/",
            params=params,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            
            if response.status == 200:
                data = await response.json()
                
                # Check what we got
                print(f"✅ Response received")
                print(f"📊 HTML length: {len(data.get('html', ''))}")
                
                if data.get('screenshot'):
                    print(f"📸 Screenshot: {data['screenshot'].get('width')}x{data['screenshot'].get('height')}")
                
                # Save HTML for inspection
                if data.get('html'):
                    with open("test_output.html", "w") as f:
                        f.write(data['html'])
                    print("💾 Saved HTML to test_output.html")
                    
                    # Quick content check
                    html_lower = data['html'].lower()
                    if 'nature' in html_lower:
                        print("✅ Reached Nature site")
                    if 'sign in' in html_lower or 'log in' in html_lower:
                        print("⚠️  Login prompt detected")
                    if '.pdf' in html_lower:
                        print("✅ PDF reference found")
                
                # Save screenshot
                if data.get('screenshot', {}).get('data'):
                    import base64
                    img_data = base64.b64decode(data['screenshot']['data'])
                    with open("test_screenshot.png", "wb") as f:
                        f.write(img_data)
                    print("📸 Saved screenshot to test_screenshot.png")
            else:
                print(f"❌ Error: {response.status}")
                print(await response.text())

if __name__ == "__main__":
    asyncio.run(main())