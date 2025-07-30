#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug ZenRows API to understand errors."""

import asyncio
import os
import aiohttp


async def debug_zenrows():
    """Debug ZenRows API calls."""
    
    api_key = os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
        
    print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Test different configurations
    test_configs = [
        {
            "name": "Basic request",
            "params": {
                "url": "https://www.nature.com",
                "apikey": api_key
            }
        },
        {
            "name": "With JS render",
            "params": {
                "url": "https://www.nature.com",
                "apikey": api_key,
                "js_render": "true"
            }
        },
        {
            "name": "With premium proxy",
            "params": {
                "url": "https://www.nature.com",
                "apikey": api_key,
                "premium_proxy": "true"
            }
        },
        {
            "name": "With session ID (numeric)",
            "params": {
                "url": "https://www.nature.com",
                "apikey": api_key,
                "session_id": "123456"
            }
        }
    ]
    
    for config in test_configs:
        print(f"\n{'='*50}")
        print(f"Test: {config['name']}")
        print(f"Params: {config['params']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=config['params'],
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    status = response.status
                    content = await response.text()
                    
                    print(f"Status: {status}")
                    
                    if status != 200:
                        print(f"Error response: {content[:500]}")
                    else:
                        print("✅ Success!")
                        print(f"Content length: {len(content)} bytes")
                        
                        # Check headers
                        zr_cookies = response.headers.get('Zr-Cookies', '')
                        zr_final_url = response.headers.get('Zr-Final-Url', '')
                        
                        if zr_cookies:
                            print(f"Cookies received: {zr_cookies[:100]}...")
                        if zr_final_url:
                            print(f"Final URL: {zr_final_url}")
                            
        except Exception as e:
            print(f"Exception: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(debug_zenrows())