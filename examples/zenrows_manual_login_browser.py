#!/usr/bin/env python3
"""
ZenRows Manual Login Browser

This script opens a ZenRows browser session and navigates to a paper URL,
then keeps the browser open for manual login. The browser window will stay
open so you can manually enter credentials and handle Okta authentication.

Usage:
    python zenrows_manual_login_browser.py
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZENROWS_API_KEY = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
if not ZENROWS_API_KEY:
    raise ValueError("SCITEX_SCHOLAR_ZENROWS_API_KEY not found in environment variables")

# Test DOI that requires institutional access
TEST_DOI = "10.1111/acer.15478"
OPENURL_BASE = "https://unimelb.hosted.exlibrisgroup.com/primo-explore/openurl"

async def manual_login_browser():
    """Open ZenRows browser for manual login"""
    
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
    
    # Construct the full URL
    query_string = "&".join(f"{k}={v}" for k, v in openurl_params.items())
    target_url = f"{OPENURL_BASE}?{query_string}"
    
    print(f"Starting ZenRows browser session...")
    print(f"Target URL: {target_url}")
    
    async with async_playwright() as p:
        # Connect to ZenRows Scraping Browser
        connection_url = f"wss://browser.zenrows.com/?apikey={ZENROWS_API_KEY}"
        
        try:
            print("\nConnecting to ZenRows browser...")
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            print("Navigating to paper URL...")
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            print("\n" + "="*60)
            print("BROWSER IS NOW OPEN FOR MANUAL LOGIN")
            print("="*60)
            print("\nThe browser will stay open for you to:")
            print("1. Enter your username and password")
            print("2. Complete Okta verification on your phone")
            print("3. Access the paper once authenticated")
            print("\nPress Ctrl+C when you're done to close the browser")
            print("="*60 + "\n")
            
            # Keep the browser open indefinitely
            while True:
                await asyncio.sleep(10)
                # Optionally check page status
                current_url = page.url
                if current_url != target_url:
                    print(f"Current page: {current_url[:100]}...")
                
        except KeyboardInterrupt:
            print("\n\nClosing browser session...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            if 'browser' in locals():
                await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    print("ZenRows Manual Login Browser")
    print("="*60)
    asyncio.run(manual_login_browser())