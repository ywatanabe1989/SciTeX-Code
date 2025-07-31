#!/usr/bin/env python3
"""
Local Browser - Persistent Session

Opens a local browser that stays open until you explicitly close it.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test DOI that requires institutional access
TEST_DOI = "10.1111/acer.15478"
OPENURL_BASE = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")

async def persistent_browser():
    """Open local browser that stays open"""
    
    # Build OpenURL with correct parameters for sfxlcl41
    openurl_params = {
        "url_ver": "Z39.88-2004",
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft.genre": "article",
        "rft.atitle": "Neurobiological effects of binge drinking help explain binge drinking maintenance and relapse",
        "rft.jtitle": "Alcoholism: Clinical and Experimental Research",
        "rft.doi": TEST_DOI,
        "rfr_id": "info:sid/scitex:scholar"
    }
    
    query_string = "&".join(f"{k}={v}" for k, v in openurl_params.items())
    target_url = f"{OPENURL_BASE}?{query_string}"
    
    print("Local Browser - Persistent Session")
    print("="*60)
    print("Opening browser on YOUR computer...")
    print(f"Target URL: {target_url}")
    
    async with async_playwright() as p:
        # Launch LOCAL browser with specific settings
        browser = await p.chromium.launch(
            headless=False,  # Show the browser
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = await browser.new_context(
            viewport=None,  # Use full screen
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        try:
            print("\nNavigating to paper URL...")
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            print("\n" + "="*60)
            print("BROWSER IS OPEN ON YOUR SCREEN")
            print("="*60)
            print("\nInstructions:")
            print("1. Look for a 'Login' or 'Sign in' link/button")
            print("2. Click it to go to your institution's login page")
            print("3. Enter your credentials")
            print("4. Complete Okta verification if needed")
            print("5. You should then see the paper or download options")
            print("\nThe browser will stay open for 10 minutes")
            print("Press Ctrl+C to close it earlier")
            print("="*60 + "\n")
            
            # Keep browser open for 10 minutes
            for i in range(60):  # 60 * 10 seconds = 10 minutes
                await asyncio.sleep(10)
                current_url = page.url
                if current_url != target_url:
                    print(f"Page changed to: {current_url[:80]}...")
                
        except KeyboardInterrupt:
            print("\nClosing browser...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    try:
        asyncio.run(persistent_browser())
    except KeyboardInterrupt:
        print("\nBrowser session ended.")