#!/usr/bin/env python3
"""Check what we get from ZenRows with different approaches."""

import os
import asyncio
import json
from scitex.scholar.browser import ZenRowsAPIBrowser

async def main():
    doi = "10.1038/nature12373"
    
    # Test 1: Simple screenshot without auth
    print("1️⃣ Testing without auth injection...")
    browser = ZenRowsAPIBrowser()
    
    result = await browser.navigate_and_screenshot(
        url=f"https://doi.org/{doi}",
        screenshot_path="test_no_auth.png",
        return_html=True
    )
    
    if result['success']:
        print(f"✅ Success")
        print(f"📊 HTML: {result.get('html_length', 0):,} bytes")
        
        if result.get('html'):
            # Save for inspection
            with open("test_no_auth.html", "w") as f:
                f.write(result['html'])
            
            # Check content
            html = result['html'].lower()
            if 'nature' in html:
                print("✅ Reached Nature")
            if 'access' in html and ('get' in html or 'purchase' in html):
                print("⚠️  Paywall detected")
            if '.pdf' in html:
                print("✅ PDF reference found")
                
            # Extract title
            import re
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', result['html'], re.IGNORECASE)
            if title_match:
                print(f"📖 Title: {title_match.group(1).strip()[:80]}")
    
    # Test 2: Try OpenURL (which might work better with institutional access)
    print("\n2️⃣ Testing OpenURL resolver...")
    openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
    
    result2 = await browser.navigate_and_screenshot(
        url=openurl,
        screenshot_path="test_openurl.png",
        return_html=True,
        wait_ms=8000  # Longer wait for resolver
    )
    
    if result2['success']:
        print(f"✅ Success")
        print(f"📊 HTML: {result2.get('html_length', 0):,} bytes")
        
        if result2.get('html'):
            with open("test_openurl.html", "w") as f:
                f.write(result2['html'])
            
            html = result2['html'].lower()
            if 'exlibris' in html or 'sfx' in html:
                print("✅ Reached library resolver")
            
            # Look for target URLs
            import re
            link_pattern = r'href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(link_pattern, result2['html'], re.IGNORECASE)
            
            access_links = []
            for url, text in matches:
                text_lower = text.lower()
                if any(word in text_lower for word in ['full text', 'get it', 'go', 'view', 'access']):
                    access_links.append((url, text.strip()))
            
            if access_links:
                print(f"\n🔗 Found {len(access_links)} potential access links:")
                for url, text in access_links[:3]:
                    print(f"   - {text}: {url[:60]}...")
    
    print("\n📁 Files saved:")
    print("- test_no_auth.png/html")
    print("- test_openurl.png/html")
    print("\n💡 Note: ZenRows uses its own proxy network, so auth cookies")
    print("   from your browser session may not transfer properly.")
    print("   OpenURL resolver might provide better institutional access.")

if __name__ == "__main__":
    asyncio.run(main())