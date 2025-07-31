#!/usr/bin/env python3
"""Example: Local browser authentication with ZenRows stealth benefits.

This shows how to:
1. Use local browser for complex auth flows
2. Get ZenRows anti-bot protection
3. Maintain authenticated sessions
4. Download papers with clean IP reputation
"""

import asyncio
import os
from pathlib import Path

from scitex.scholar.browser._ZenRowsStealthyLocal import ZenRowsStealthyLocal
from scitex import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def login_and_download_with_stealth():
    """Login to institution and download paper using ZenRows stealth."""
    
    # Initialize stealthy local browser
    browser = ZenRowsStealthyLocal(
        headless=False,  # Show browser for interactive login
        use_residential=True,  # Use premium residential IPs
        country="us"
    )
    
    try:
        # Create browser context
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Browser opened with ZenRows stealth protection:")
        print("- Residential IP address")
        print("- Anti-bot detection bypass")
        print("- Full local control\n")
        
        # Example 1: Check our IP
        print("Checking IP address...")
        await page.goto("https://httpbin.org/ip")
        ip_content = await page.content()
        print(f"Current IP info: {ip_content[:200]}...\n")
        
        # Example 2: Navigate to institution login
        # Replace with your institution's login URL
        login_url = "https://www.nature.com/nature/login"
        print(f"Navigating to login page: {login_url}")
        await page.goto(login_url)
        
        # Option A: Manual login
        print("\n=== MANUAL LOGIN ===")
        print("Please log in manually in the browser window.")
        print("Press Enter when logged in...")
        input()
        
        # Option B: Automated login (uncomment and customize)
        """
        # Fill in credentials
        await page.fill('input[name="username"]', os.getenv("INSTITUTION_USERNAME"))
        await page.fill('input[name="password"]', os.getenv("INSTITUTION_PASSWORD"))
        
        # Click login button
        await page.click('button[type="submit"]')
        
        # Wait for login to complete
        await page.wait_for_url("**/dashboard", timeout=30000)
        """
        
        print("\n✅ Logged in successfully!")
        
        # Save cookies for future use
        cookies = await context.cookies()
        print(f"Saved {len(cookies)} cookies from session")
        
        # Example 3: Navigate to a paper
        paper_url = "https://www.nature.com/articles/nature12373"
        print(f"\nNavigating to paper: {paper_url}")
        await page.goto(paper_url)
        
        # Example 4: Download PDF
        print("\nLooking for PDF download link...")
        
        # Find PDF link (customize selector for your site)
        pdf_link = await page.query_selector('a[data-track-action="download pdf"]')
        if pdf_link:
            # Set up download handling
            async with page.expect_download() as download_info:
                await pdf_link.click()
                download = await download_info.value
            
            # Save PDF
            save_path = Path("./downloaded_paper_stealth.pdf")
            await download.save_as(save_path)
            print(f"✅ PDF downloaded to: {save_path}")
        else:
            print("❌ Could not find PDF download link")
            print("Selectors to try:")
            print('  - a[href$=".pdf"]')
            print('  - a:has-text("Download PDF")')
            print('  - button:has-text("Download")')
        
        # Keep browser open for inspection
        print("\n🔍 Browser will stay open for 30 seconds for inspection...")
        await asyncio.sleep(30)
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await browser.cleanup()
        print("\nBrowser closed.")


async def batch_download_with_stealth():
    """Download multiple papers using authenticated session."""
    
    browser = ZenRowsStealthyLocal(
        headless=True,  # Can run headless after login
        use_residential=True
    )
    
    # Paper DOIs to download
    dois = [
        "10.1038/nature12373",
        "10.1126/science.1234567",  # Example
        "10.1073/pnas.0123456789",  # Example
    ]
    
    try:
        context = await browser.new_context()
        page = await context.new_page()
        
        # Load saved cookies (from previous login)
        # cookies = load_cookies_from_file()
        # await context.add_cookies(cookies)
        
        for doi in dois:
            try:
                # Construct URL (customize for your resolver)
                url = f"https://doi.org/{doi}"
                print(f"\nProcessing: {doi}")
                
                await page.goto(url)
                await page.wait_for_timeout(2000)  # Wait for redirects
                
                # Your download logic here
                print(f"  Current URL: {page.url}")
                
            except Exception as e:
                print(f"  Error with {doi}: {e}")
                
    finally:
        await browser.cleanup()


async def test_anti_bot_protection():
    """Test that ZenRows bypasses bot detection."""
    
    browser = ZenRowsStealthyLocal(use_residential=True)
    
    try:
        results = await browser.test_stealth()
        
        print("\n=== Anti-Bot Test Results ===")
        print(f"IP Check: {'✅ Using proxy' if results.get('ip_check') else '❌ Direct connection'}")
        
        bot_tests = results.get('bot_tests', {})
        print(f"\nBot Detection Tests:")
        print(f"  Webdriver detected: {'❌ Yes' if bot_tests.get('webdriver') else '✅ No'}")
        print(f"  Headless detected: {'❌ Yes' if bot_tests.get('headless') else '✅ No'}")
        print(f"  Chrome object: {'✅ Present' if bot_tests.get('chrome') else '❌ Missing'}")
        print(f"  Plugins: {'✅ Present' if bot_tests.get('plugins') else '❌ Missing'}")
        print(f"  Languages: {'✅ Present' if bot_tests.get('languages') else '❌ Missing'}")
        
        if results.get('screenshot'):
            print(f"\nScreenshot saved: {results['screenshot']}")
            
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    print("ZenRows Stealthy Local Browser Examples\n")
    print("1. Login and download single paper")
    print("2. Batch download with session")
    print("3. Test anti-bot protection")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        asyncio.run(login_and_download_with_stealth())
    elif choice == "2":
        asyncio.run(batch_download_with_stealth())
    elif choice == "3":
        asyncio.run(test_anti_bot_protection())
    else:
        print("Invalid choice")

# EOF