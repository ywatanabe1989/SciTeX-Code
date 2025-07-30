#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-30 21:30:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/.dev/zenrows_complete_workflow_demo.py
# ----------------------------------------
"""Complete ZenRows workflow demonstration.

This script demonstrates:
1. Testing ZenRows API connectivity
2. Cookie transfer mechanism
3. OpenURL resolution with cookies
4. Publisher access with authentication
"""

import asyncio
import os
import sys
from pathlib import Path
import aiohttp
import json
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ZenRowsWorkflowDemo:
    """Demonstrates complete ZenRows workflow."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_id = str(123456)  # Fixed numeric session ID
        self.cookies: Dict[str, str] = {}
        
    async def test_api_connectivity(self) -> bool:
        """Test basic API connectivity."""
        print("\n1. Testing API Connectivity")
        print("=" * 40)
        
        params = {
            "url": "https://www.google.com",
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        print("✅ ZenRows API is working!")
                        return True
                    else:
                        print(f"❌ API error: {response.status}")
                        content = await response.text()
                        print(f"Error: {content[:200]}")
                        return False
                        
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            return False
            
    async def test_openurl_resolver(self) -> Dict:
        """Test OpenURL resolver access."""
        print("\n2. Testing OpenURL Resolver")
        print("=" * 40)
        
        # University of Melbourne OpenURL
        base_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
        params_openurl = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
            "rft.atitle": "A mesoscale connectome of the mouse brain",
            "rft.jtitle": "Nature",
            "rft.date": "2014",
            "rft_id": "info:doi/10.1038/nature12373"
        }
        
        from urllib.parse import urlencode
        openurl = f"{base_url}?{urlencode(params_openurl)}"
        
        print(f"OpenURL: {openurl[:100]}...")
        
        params = {
            "url": openurl,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.session_id,
            "wait": "5"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        print("✅ Resolver accessed successfully")
                        
                        # Check for cookies in response
                        zr_cookies = response.headers.get('Zr-Cookies', '')
                        if zr_cookies:
                            print(f"🍪 Received cookies: {zr_cookies[:100]}...")
                            # Parse and store cookies
                            for cookie in zr_cookies.split(';'):
                                cookie = cookie.strip()
                                if '=' in cookie:
                                    name, value = cookie.split('=', 1)
                                    self.cookies[name.strip()] = value.strip()
                                    
                        # Get final URL
                        final_url = response.headers.get('Zr-Final-Url', openurl)
                        print(f"Final URL: {final_url[:100]}...")
                        
                        return {
                            "success": True,
                            "final_url": final_url,
                            "cookie_count": len(self.cookies)
                        }
                    else:
                        print(f"❌ Resolver error: {response.status}")
                        return {"success": False}
                        
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            return {"success": False}
            
    async def test_publisher_access(self, doi: str) -> Dict:
        """Test direct publisher access with cookies."""
        print(f"\n3. Testing Publisher Access (DOI: {doi})")
        print("=" * 40)
        
        url = f"https://doi.org/{doi}"
        
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.session_id,
            "wait": "5"
        }
        
        # Add cookies if we have them
        headers = {}
        if self.cookies:
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            print(f"🍪 Sending {len(self.cookies)} cookies")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        
                        # Check for access indicators
                        has_pdf = "pdf" in content.lower()
                        has_download = "download" in content.lower()
                        has_access = "full text" in content.lower()
                        needs_login = "log in" in content.lower() or "sign in" in content.lower()
                        
                        print(f"✅ Publisher page accessed")
                        print(f"   - Has PDF link: {'✓' if has_pdf else '✗'}")
                        print(f"   - Has download: {'✓' if has_download else '✗'}")
                        print(f"   - Has full text: {'✓' if has_access else '✗'}")
                        print(f"   - Needs login: {'✓' if needs_login else '✗'}")
                        
                        # Save sample for analysis
                        with open(".dev/zenrows_publisher_response.html", "w") as f:
                            f.write(content)
                        print("   💾 Response saved to zenrows_publisher_response.html")
                        
                        return {
                            "success": True,
                            "has_access": has_access and not needs_login,
                            "indicators": {
                                "pdf": has_pdf,
                                "download": has_download,
                                "full_text": has_access,
                                "needs_login": needs_login
                            }
                        }
                    else:
                        print(f"❌ Publisher error: {response.status}")
                        return {"success": False}
                        
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            return {"success": False}


async def main():
    """Run the complete workflow demo."""
    
    print("ZenRows Complete Workflow Demo")
    print("*" * 50)
    
    # Get API key
    api_key = os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("❌ Please set SCITEX_SCHOLAR_ZENROWS_API_KEY")
        return
        
    demo = ZenRowsWorkflowDemo(api_key)
    
    # Step 1: Test API
    if not await demo.test_api_connectivity():
        print("\n⚠️  Fix API connectivity before continuing")
        return
        
    # Step 2: Test OpenURL resolver
    resolver_result = await demo.test_openurl_resolver()
    
    # Step 3: Test publisher access
    test_doi = "10.1038/nature12373"
    publisher_result = await demo.test_publisher_access(test_doi)
    
    # Summary
    print("\n" + "=" * 50)
    print("Workflow Summary:")
    print(f"- API connectivity: ✅")
    print(f"- OpenURL resolver: {'✅' if resolver_result.get('success') else '❌'}")
    print(f"- Cookies collected: {len(demo.cookies)}")
    print(f"- Publisher access: {'✅' if publisher_result.get('success') else '❌'}")
    
    if publisher_result.get('has_access'):
        print("\n🎉 SUCCESS: Full access achieved with ZenRows!")
    else:
        print("\n⚠️  Limited access - authentication may be needed")
        
    print("\nNext Steps:")
    print("1. Authenticate with OpenAthens locally")
    print("2. Transfer session cookies to ZenRows")
    print("3. Access paywalled content through ZenRows")


if __name__ == "__main__":
    asyncio.run(main())