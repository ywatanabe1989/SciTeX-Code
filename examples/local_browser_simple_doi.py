#!/usr/bin/env python3
"""
Simple DOI Access with Local Browser

Opens a local browser with just the DOI appended to your OpenURL resolver.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def simple_doi_access():
    """Simple DOI-based access"""
    
    # Get resolver URL from environment or use default
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    
    # Test DOI
    doi = "10.1111/acer.15478"
    
    # Simple approach - just append DOI
    simple_url = f"{resolver_url}?doi={doi}"
    
    # Also try with more parameters
    full_url = f"{resolver_url}?url_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.genre=article&rft_id=info:doi/{doi}"
    
    print("Simple DOI Access Test")
    print("="*60)
    print(f"Resolver: {resolver_url}")
    print(f"DOI: {doi}")
    print(f"Simple URL: {simple_url}")
    print(f"Full URL: {full_url}")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(viewport=None)
        
        # Try simple URL first
        print("\nOpening simple DOI URL...")
        page1 = await context.new_page()
        await page1.goto(simple_url, wait_until="domcontentloaded")
        
        # Also try full URL
        print("Opening full OpenURL...")
        page2 = await context.new_page()
        await page2.goto(full_url, wait_until="domcontentloaded")
        
        print("\n" + "="*60)
        print("BROWSER TABS OPEN")
        print("="*60)
        print("Tab 1: Simple DOI URL")
        print("Tab 2: Full OpenURL format")
        print("\nOne of these should work with your institution")
        print("Browser stays open for 5 minutes")
        print("Press Ctrl+C to close")
        print("="*60 + "\n")
        
        try:
            await asyncio.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print("\nClosing...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_doi_access())