#!/usr/bin/env python3
"""Debug ZenRows response handling."""

import os
import asyncio
import json
import aiohttp

async def main():
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("❌ No API key")
        return
    
    url = "https://doi.org/10.1038/nature12373"
    
    # Request with screenshot only (no json_response)
    print("1️⃣ Testing with screenshot=true only...")
    params = {
        "url": url,
        "apikey": api_key,
        "js_render": "true",
        "screenshot": "true",
        "premium_proxy": "true",
        "antibot": "true",
        "wait": "5000"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.zenrows.com/v1/", params=params) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {response.headers.get('content-length')}")
            
            # Save raw response
            content = await response.read()
            print(f"Response size: {len(content)} bytes")
            
            # Check if it's an image
            if content[:4] == b'\x89PNG':
                print("✅ Got PNG image")
                with open("direct_screenshot.png", "wb") as f:
                    f.write(content)
                print("📸 Saved to direct_screenshot.png")
            else:
                print(f"First 100 bytes: {content[:100]}")
    
    # Request with json_response
    print("\n2️⃣ Testing with json_response=true...")
    params["json_response"] = "true"
    
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.zenrows.com/v1/", params=params) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            content = await response.text()
            print(f"Response size: {len(content)} bytes")
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
                print("✅ Valid JSON response")
                print(f"Keys: {list(data.keys())}")
                
                if 'html' in data:
                    print(f"HTML size: {len(data['html'])} bytes")
                    with open("response.html", "w") as f:
                        f.write(data['html'])
                    print("💾 Saved HTML to response.html")
                    
                    # Check content
                    if data['html']:
                        if '<title>' in data['html']:
                            import re
                            title = re.search(r'<title>([^<]+)</title>', data['html'])
                            if title:
                                print(f"📖 Title: {title.group(1)}")
                
                if 'screenshot' in data:
                    print(f"Screenshot info: {data['screenshot'].get('width')}x{data['screenshot'].get('height')}")
                    if data['screenshot'].get('data'):
                        import base64
                        img_data = base64.b64decode(data['screenshot']['data'])
                        with open("json_screenshot.png", "wb") as f:
                            f.write(img_data)
                        print("📸 Saved screenshot from JSON")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"First 200 chars: {content[:200]}")
                with open("raw_response.txt", "w") as f:
                    f.write(content)
                print("💾 Saved raw response to raw_response.txt")

if __name__ == "__main__":
    asyncio.run(main())