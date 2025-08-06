#!/usr/bin/env python3
"""
Simple Chrome launcher that uses the working BrowserManager approach
"""
import asyncio
from src.scitex.scholar.browser.local._BrowserManager import BrowserManager

async def launch_chrome_for_manual_use():
    """Launch Chrome using the proven BrowserManager approach."""
    print("🚀 Launching Chrome with Scholar extensions (using BrowserManager)...")
    
    # Create browser manager (same as working _BrowserManager)
    browser_manager = BrowserManager()
    
    # Get browser with all extensions loaded
    browser = await browser_manager.get_browser_async_with_profile()
    
    # Create a new page to keep browser active
    page = await browser.new_page()
    await page.goto("https://www.google.com")
    
    print("✅ Chrome is running with all Scholar extensions!")
    print("🔗 Extensions loaded: Lean Library, Pop-up Blocker, Cookie Acceptor, CAPTCHA Solvers")
    print("🔑 API keys are configured")
    print("🌐 You can now use Chrome manually")
    print("🛑 Press Ctrl+C to close")
    
    try:
        # Keep the browser open
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Closing Chrome...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(launch_chrome_for_manual_use())