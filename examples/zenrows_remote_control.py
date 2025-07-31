#!/usr/bin/env python3
"""
ZenRows Remote Browser Control

This script gives you full control over the remote ZenRows browser.
You can interact with it through commands and see screenshots of what's happening.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from datetime import datetime
import base64

# Load environment variables
load_dotenv()

ZENROWS_API_KEY = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
if not ZENROWS_API_KEY:
    raise ValueError("SCITEX_SCHOLAR_ZENROWS_API_KEY not found in environment variables")

# Test DOI that requires institutional access
TEST_DOI = "10.1111/acer.15478"
OPENURL_BASE = "https://unimelb.hosted.exlibrisgroup.com/primo-explore/openurl"

async def remote_browser_control():
    """Full control over remote ZenRows browser"""
    
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
    
    print("ZenRows Remote Browser Control")
    print("="*60)
    print("You're controlling a browser running on ZenRows servers")
    print(f"Target URL: {target_url}")
    
    async with async_playwright() as p:
        connection_url = f"wss://browser.zenrows.com/?apikey={ZENROWS_API_KEY}"
        
        try:
            print("\nConnecting to remote browser...")
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
            
            print("Navigating to paper URL...")
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # Create screenshots directory
            screenshots_dir = "zenrows_screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            print(f"\nScreenshots saved to: {screenshots_dir}/")
            print("\n" + "="*60)
            print("REMOTE BROWSER COMMANDS:")
            print("="*60)
            print("Navigation:")
            print("  goto <url>             - Navigate to URL")
            print("  back                   - Go back")
            print("  forward                - Go forward")
            print("  reload                 - Reload page")
            print("\nInteraction:")
            print("  click <selector>       - Click element")
            print("  fill <selector> <text> - Fill input field")
            print("  type <text>           - Type text (at cursor)")
            print("  press <key>           - Press key (Enter, Tab, etc)")
            print("  select <selector> <value> - Select dropdown option")
            print("\nInspection:")
            print("  screenshot            - Take screenshot")
            print("  url                   - Show current URL")
            print("  title                 - Show page title")
            print("  text <selector>       - Get element text")
            print("  html                  - Show page HTML")
            print("  elements <selector>   - Count matching elements")
            print("\nQuick Login:")
            print("  login                 - Auto-fill credentials from env")
            print("\nOther:")
            print("  wait <seconds>        - Wait N seconds")
            print("  help                  - Show this help")
            print("  quit                  - Exit")
            print("="*60 + "\n")
            
            # Take initial screenshot
            screenshot_num = 1
            screenshot_path = f"{screenshots_dir}/{screenshot_num:03d}_initial.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved: {screenshot_path}")
            print(f"Current URL: {page.url}\n")
            
            while True:
                try:
                    command = input("remote> ").strip()
                    parts = command.split(maxsplit=2)
                    
                    if not parts:
                        continue
                    
                    cmd = parts[0].lower()
                    
                    if cmd in ['quit', 'q', 'exit']:
                        break
                    
                    elif cmd == 'help':
                        print("\nCOMMANDS:")
                        print("  goto <url>, back, forward, reload")
                        print("  click <selector>, fill <selector> <text>")
                        print("  type <text>, press <key>")
                        print("  screenshot, url, title, html")
                        print("  text <selector>, elements <selector>")
                        print("  login (auto-fill from env)")
                        print("  wait <seconds>, help, quit\n")
                    
                    elif cmd == 'screenshot':
                        screenshot_num += 1
                        screenshot_path = f"{screenshots_dir}/{screenshot_num:03d}_screenshot.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"Screenshot saved: {screenshot_path}")
                    
                    elif cmd == 'url':
                        print(f"Current URL: {page.url}")
                    
                    elif cmd == 'title':
                        title = await page.title()
                        print(f"Page title: {title}")
                    
                    elif cmd == 'goto' and len(parts) > 1:
                        url = ' '.join(parts[1:])
                        print(f"Navigating to: {url}")
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                        print("Navigation complete")
                    
                    elif cmd == 'back':
                        await page.go_back()
                        print("Went back")
                    
                    elif cmd == 'forward':
                        await page.go_forward()
                        print("Went forward")
                    
                    elif cmd == 'reload':
                        await page.reload()
                        print("Page reloaded")
                    
                    elif cmd == 'click' and len(parts) > 1:
                        selector = ' '.join(parts[1:])
                        await page.click(selector, timeout=5000)
                        print(f"Clicked: {selector}")
                    
                    elif cmd == 'fill' and len(parts) > 2:
                        selector = parts[1]
                        text = ' '.join(parts[2:])
                        await page.fill(selector, text, timeout=5000)
                        print(f"Filled {selector} with: {text}")
                    
                    elif cmd == 'type' and len(parts) > 1:
                        text = ' '.join(parts[1:])
                        await page.keyboard.type(text)
                        print(f"Typed: {text}")
                    
                    elif cmd == 'press' and len(parts) > 1:
                        key = parts[1]
                        await page.keyboard.press(key)
                        print(f"Pressed: {key}")
                    
                    elif cmd == 'select' and len(parts) > 2:
                        selector = parts[1]
                        value = ' '.join(parts[2:])
                        await page.select_option(selector, value)
                        print(f"Selected {value} in {selector}")
                    
                    elif cmd == 'text' and len(parts) > 1:
                        selector = ' '.join(parts[1:])
                        text = await page.text_content(selector)
                        print(f"Text content: {text}")
                    
                    elif cmd == 'html':
                        html = await page.content()
                        print(f"HTML length: {len(html)} characters")
                        print("First 500 chars:")
                        print(html[:500] + "...")
                    
                    elif cmd == 'elements' and len(parts) > 1:
                        selector = ' '.join(parts[1:])
                        count = await page.locator(selector).count()
                        print(f"Found {count} elements matching: {selector}")
                    
                    elif cmd == 'wait' and len(parts) > 1:
                        seconds = int(parts[1])
                        print(f"Waiting {seconds} seconds...")
                        await asyncio.sleep(seconds)
                        print("Wait complete")
                    
                    elif cmd == 'login':
                        print("Attempting auto-login with environment credentials...")
                        username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
                        password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
                        
                        if username and password:
                            # Try to find and fill username field
                            for selector in ['input[name="username"]', 'input[id="username"]', 
                                           'input[type="text"]', 'input[placeholder*="username" i]']:
                                try:
                                    await page.fill(selector, username, timeout=2000)
                                    print(f"Filled username: {selector}")
                                    break
                                except:
                                    pass
                            
                            # Try to find and fill password field
                            for selector in ['input[name="password"]', 'input[id="password"]', 
                                           'input[type="password"]']:
                                try:
                                    await page.fill(selector, password, timeout=2000)
                                    print(f"Filled password: {selector}")
                                    break
                                except:
                                    pass
                            
                            print("Credentials filled. Use 'click' command to submit.")
                        else:
                            print("No credentials found in environment")
                    
                    else:
                        print(f"Unknown command: {command}")
                        print("Type 'help' for available commands")
                    
                except Exception as e:
                    print(f"Error: {e}")
                    print("Command failed, but browser is still connected")
                    
        except Exception as e:
            print(f"\nConnection error: {e}")
        finally:
            if 'browser' in locals():
                await browser.close()
            print("\nRemote browser closed.")

if __name__ == "__main__":
    asyncio.run(remote_browser_control())