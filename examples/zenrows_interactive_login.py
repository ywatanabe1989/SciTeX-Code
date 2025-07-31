#!/usr/bin/env python3
"""
ZenRows Interactive Login with Screenshots

This script connects to ZenRows browser and takes periodic screenshots
so you can see what's happening on the remote browser.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

ZENROWS_API_KEY = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
if not ZENROWS_API_KEY:
    raise ValueError("SCITEX_SCHOLAR_ZENROWS_API_KEY not found in environment variables")

# Test DOI that requires institutional access
TEST_DOI = "10.1111/acer.15478"
OPENURL_BASE = "https://unimelb.hosted.exlibrisgroup.com/primo-explore/openurl"

async def interactive_login():
    """Interactive login with screenshots"""
    
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
    
    print("ZenRows Interactive Login")
    print("="*60)
    print(f"Target URL: {target_url}")
    
    async with async_playwright() as p:
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
            
            # Create screenshots directory
            screenshots_dir = "zenrows_screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            print(f"\nScreenshots will be saved to: {screenshots_dir}/")
            print("\n" + "="*60)
            print("INSTRUCTIONS:")
            print("="*60)
            print("1. Check the screenshots folder to see the current page")
            print("2. Type commands to interact with the page:")
            print("   - 'screenshot' or 's': Take a new screenshot")
            print("   - 'fill username <value>': Fill username field")
            print("   - 'fill password <value>': Fill password field")  
            print("   - 'click submit': Click the submit button")
            print("   - 'wait': Wait 30 seconds for Okta")
            print("   - 'url': Show current URL")
            print("   - 'quit' or 'q': Exit")
            print("="*60 + "\n")
            
            # Take initial screenshot
            screenshot_path = f"{screenshots_dir}/initial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Initial screenshot saved: {screenshot_path}")
            
            while True:
                try:
                    command = input("\nEnter command: ").strip().lower()
                    
                    if command in ['quit', 'q']:
                        break
                    
                    elif command in ['screenshot', 's']:
                        screenshot_path = f"{screenshots_dir}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"Screenshot saved: {screenshot_path}")
                    
                    elif command.startswith('fill username '):
                        username = command[14:]
                        # Try multiple username field selectors
                        selectors = [
                            'input[name="username"]',
                            'input[id="username"]',
                            'input[type="text"]',
                            'input[placeholder*="username" i]',
                            'input[placeholder*="email" i]'
                        ]
                        filled = False
                        for selector in selectors:
                            try:
                                await page.fill(selector, username, timeout=2000)
                                print(f"Filled username field: {selector}")
                                filled = True
                                break
                            except:
                                continue
                        if not filled:
                            print("Could not find username field")
                    
                    elif command.startswith('fill password '):
                        password = command[14:]
                        # Try multiple password field selectors
                        selectors = [
                            'input[name="password"]',
                            'input[id="password"]',
                            'input[type="password"]'
                        ]
                        filled = False
                        for selector in selectors:
                            try:
                                await page.fill(selector, password, timeout=2000)
                                print(f"Filled password field: {selector}")
                                filled = True
                                break
                            except:
                                continue
                        if not filled:
                            print("Could not find password field")
                    
                    elif command == 'click submit':
                        # Try multiple submit button selectors
                        selectors = [
                            'button[type="submit"]',
                            'input[type="submit"]',
                            'button:has-text("Sign in")',
                            'button:has-text("Login")',
                            'button:has-text("Log in")'
                        ]
                        clicked = False
                        for selector in selectors:
                            try:
                                await page.click(selector, timeout=2000)
                                print(f"Clicked submit button: {selector}")
                                clicked = True
                                break
                            except:
                                continue
                        if not clicked:
                            print("Could not find submit button")
                    
                    elif command == 'wait':
                        print("Waiting 30 seconds for Okta verification...")
                        await asyncio.sleep(30)
                        print("Wait complete")
                    
                    elif command == 'url':
                        print(f"Current URL: {page.url}")
                    
                    else:
                        print("Unknown command. Type 'screenshot', 'fill username <value>', 'fill password <value>', 'click submit', 'wait', 'url', or 'quit'")
                    
                except Exception as e:
                    print(f"Error: {e}")
                    
        except Exception as e:
            print(f"\nConnection error: {e}")
        finally:
            if 'browser' in locals():
                await browser.close()
            print("\nBrowser closed.")

if __name__ == "__main__":
    asyncio.run(interactive_login())