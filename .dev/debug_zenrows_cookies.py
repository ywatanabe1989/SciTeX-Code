#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 21:05:00 (ywatanabe)"
# File: ./.dev/debug_zenrows_cookies.py
# ----------------------------------------
"""Debug script to understand why cookies aren't transferring properly.

This minimal script tests different cookie formats and API approaches.
"""

import asyncio
import aiohttp
import os
import json


async def test_zenrows_api_formats():
    """Test different ways to send cookies to ZenRows."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    # Test URL that will echo cookies back
    test_url = "https://httpbin.org/cookies"
    
    print("🔍 ZenRows Cookie Format Debug")
    print("="*50)
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Test URL: {test_url}")
    
    # Different cookie format attempts
    test_formats = [
        {
            "name": "Format 1: Simple cookie string",
            "params": {
                "url": test_url,
                "apikey": api_key,
                "custom_cookies": "test1=value1; test2=value2"
            }
        },
        {
            "name": "Format 2: With js_render",
            "params": {
                "url": test_url,
                "apikey": api_key,
                "js_render": "true",
                "custom_cookies": "test1=value1; test2=value2"
            }
        },
        {
            "name": "Format 3: With premium_proxy",
            "params": {
                "url": test_url,
                "apikey": api_key,
                "js_render": "true",
                "premium_proxy": "true",
                "custom_cookies": "test1=value1; test2=value2"
            }
        },
        {
            "name": "Format 4: URL encoded cookies",
            "params": {
                "url": test_url,
                "apikey": api_key,
                "js_render": "true",
                "custom_cookies": "test1%3Dvalue1%3B%20test2%3Dvalue2"
            }
        }
    ]
    
    for test_format in test_formats:
        print(f"\n\n📝 Testing: {test_format['name']}")
        print(f"   Cookies: {test_format['params'].get('custom_cookies', 'None')}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=test_format['params'],
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        
                        # Try to parse JSON
                        try:
                            data = json.loads(content)
                            cookies = data.get("cookies", {})
                            
                            if cookies:
                                print("   ✅ Cookies received:")
                                for k, v in cookies.items():
                                    print(f"      - {k}: {v}")
                            else:
                                print("   ❌ No cookies in response")
                                
                        except json.JSONDecodeError:
                            print("   ❌ Response is not JSON")
                            if "test1" in content:
                                print("   ✅ But cookies appear in HTML!")
                            else:
                                print("   ❌ No cookies found in response")
                                
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error: {error_text[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Exception: {e}")


async def test_with_real_publisher():
    """Test with a real publisher to see response."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    # Simple test with Nature
    test_url = "https://www.nature.com/nature"
    
    print("\n\n🌐 Testing with Real Publisher")
    print("="*50)
    
    params = {
        "url": test_url,
        "apikey": api_key,
        "js_render": "true",
        "premium_proxy": "true",
        "custom_cookies": "test_cookie=test_value"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"Status: {response.status}")
                
                # Check headers
                print("\nResponse Headers:")
                for key, value in response.headers.items():
                    if key.lower().startswith('zr-'):
                        print(f"  {key}: {value}")
                        
                if response.status == 200:
                    content = await response.text()
                    
                    # Just check if we got HTML
                    if "<html" in content.lower():
                        print("✅ Got HTML response")
                        print(f"   Content length: {len(content)} bytes")
                        
                        # Save for inspection
                        with open('.dev/zenrows_debug_response.html', 'w') as f:
                            f.write(content[:10000])
                        print("💾 Saved to: .dev/zenrows_debug_response.html")
                        
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_browser_api():
    """Test if Browser API handles cookies differently."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    
    print("\n\n🌐 Testing Browser API Cookie Handling")
    print("="*50)
    
    from playwright.async_api import async_playwright
    
    try:
        playwright = await async_playwright().start()
        
        # Connect to ZenRows browser
        browser = await playwright.chromium.connect_over_cdp(
            f"wss://browser.zenrows.com?apikey={api_key}"
        )
        
        context = await browser.new_context()
        
        # Add cookies before navigation
        await context.add_cookies([
            {
                "name": "browser_test",
                "value": "browser_value",
                "domain": ".httpbin.org",
                "path": "/"
            }
        ])
        
        page = await context.new_page()
        
        # Navigate to cookie echo page
        await page.goto("https://httpbin.org/cookies")
        
        # Get page content
        content = await page.content()
        
        # Check if our cookie appears
        if "browser_test" in content:
            print("✅ Cookie was sent via Browser API!")
        else:
            print("❌ Cookie not found in Browser API response")
            
        # Extract JSON if possible
        try:
            json_text = await page.locator("pre").text_content()
            data = json.loads(json_text)
            print(f"Cookies received: {data.get('cookies', {})}")
        except:
            print("Could not extract JSON from page")
            
        await browser.close()
        await playwright.stop()
        
    except Exception as e:
        print(f"❌ Browser API error: {e}")


async def main():
    """Run all debug tests."""
    
    print("🔍 ZenRows Cookie Debug Suite")
    print("This will test various cookie transfer methods\n")
    
    # Test 1: Different API formats
    await test_zenrows_api_formats()
    
    # Test 2: Real publisher
    await test_with_real_publisher()
    
    # Test 3: Browser API
    await test_browser_api()
    
    print("\n\n📊 Debug Summary:")
    print("Check which methods successfully transfer cookies")
    print("Browser API vs REST API may have different behaviors")


if __name__ == "__main__":
    asyncio.run(main())