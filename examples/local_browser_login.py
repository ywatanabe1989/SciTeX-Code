#!/usr/bin/env python3
"""
Local Browser Login - Opens browser on YOUR PC

This script opens a browser window on your local computer (not ZenRows)
so you can see it and manually login.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test DOI that requires institutional access
TEST_DOI = "10.1111/acer.15478"
OPENURL_BASE = "https://unimelb.hosted.exlibrisgroup.com/primo-explore/openurl"

async def local_browser_login():
    """Open local browser for manual login"""
    
    # Build OpenURL
    openurl_params = {
        "institution": "61UNIMELB",
        "vid": "61UNIMELB_PRODUCTION",
        "atitle": "Neurobiological effects of binge drinking",
        "jtitle": "Alcoholism: Clinical and Experimental Research",
        "doi": TEST_DOI,
        "sid": "scitex",
        "svc_dat": "viewservice"
    }
    
    query_string = "&".join(f"{k}={v}" for k, v in openurl_params.items())
    target_url = f"{OPENURL_BASE}?{query_string}"
    
    print("Local Browser Login")
    print("="*60)
    print("Opening browser on YOUR computer...")
    print(f"Target URL: {target_url}")
    
    async with async_playwright() as p:
        # Launch LOCAL browser (not ZenRows)
        browser = await p.chromium.launch(
            headless=False,  # This makes the browser visible
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = await context.new_page()
        
        print("\nNavigating to paper URL...")
        await page.goto(target_url, wait_until="networkidle", timeout=60000)
        
        print("\n" + "="*60)
        print("BROWSER IS NOW OPEN ON YOUR COMPUTER")
        print("="*60)
        print("\nYou can now:")
        print("1. See the browser window on your screen")
        print("2. Manually enter your username and password")
        print("3. Complete Okta verification")
        print("4. Access the paper")
        print("\nPress Enter when you're done to close the browser")
        print("="*60 + "\n")
        
        # Wait for user to press Enter
        input("Press Enter when done...")
        
        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    print("This will open a browser on YOUR computer (not ZenRows)")
    asyncio.run(local_browser_login())