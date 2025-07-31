#!/usr/bin/env python3
"""
Complete guide for manual login with ZenRows Scraping Browser.

This script demonstrates:
1. Connecting to ZenRows remote browser
2. Navigating to your university login
3. Manually entering credentials
4. Maintaining session for multiple DOIs
"""

import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime

async def manual_login_workflow():
    """Complete workflow for manual SSO login."""
    
    # Get credentials
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("Error: Please set SCITEX_SCHOLAR_ZENROWS_API_KEY")
        return
    
    print("ZenRows Manual Login Guide")
    print("=" * 70)
    print("\nThis guide will walk you through:")
    print("1. Connecting to ZenRows remote browser")
    print("2. Navigating to your university login")
    print("3. Manually entering your credentials")
    print("4. Using the session to access papers")
    print("=" * 70)
    
    async with async_playwright() as p:
        # Step 1: Connect to ZenRows
        print("\n🔌 Step 1: Connecting to ZenRows browser...")
        connection_url = f"wss://browser.zenrows.com?apikey={api_key}&proxy_country=au"
        
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000  # 2 minute timeout
            )
            print("✓ Connected to ZenRows remote browser!")
            
            # Create a new page
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # Step 2: Navigate to resolver with a test DOI
            print("\n🌐 Step 2: Navigating to OpenURL resolver...")
            resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
            test_doi = "10.1038/nature12373"
            openurl = f"{resolver_url}?rft_id=info:doi/{test_doi}"
            
            print(f"   URL: {openurl}")
            await page.goto(openurl, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Let page load
            
            # Step 3: Click on full-text link
            print("\n🖱️  Step 3: Looking for full-text link...")
            
            # Find and click Nature link (or similar)
            nature_link = await page.query_selector("a:has-text('Nature')")
            if nature_link:
                print("   Found 'Nature' link, clicking...")
                
                # This will open a new tab
                await nature_link.click()
                await page.wait_for_timeout(5000)
                
                # Switch to new tab if opened
                pages = browser.contexts[0].pages
                if len(pages) > 1:
                    print("   New tab opened, switching to it...")
                    login_page = pages[-1]
                    await login_page.wait_for_load_state()
                else:
                    login_page = page
            else:
                print("   No Nature link found, checking current page...")
                login_page = page
            
            # Step 4: Check if we're at login page
            current_url = login_page.url
            print(f"\n📍 Current URL: {current_url}")
            
            if "login" in current_url.lower() or "openathens" in current_url.lower():
                print("\n🔐 Step 4: Login page detected!")
                print("=" * 70)
                print("MANUAL LOGIN REQUIRED")
                print("=" * 70)
                
                # Take screenshot to show current state
                screenshot_path = f"login_page_{datetime.now().strftime('%H%M%S')}.png"
                await login_page.screenshot(path=screenshot_path)
                print(f"\n📸 Screenshot saved: {screenshot_path}")
                
                # Check for username field
                username_field = await login_page.query_selector(
                    "input[type='text'], input[name='username'], #username, input[name='user']"
                )
                
                if username_field:
                    print("\n✓ Username field found!")
                    
                    # Option 1: Automated fill (if you want)
                    username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
                    if username:
                        print(f"   Filling username: {username}")
                        await username_field.fill(username)
                        
                        # Look for password field
                        password_field = await login_page.query_selector(
                            "input[type='password'], #password"
                        )
                        
                        if password_field:
                            password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
                            if password:
                                print("   Filling password: ****")
                                await password_field.fill(password)
                                
                                # Find submit button
                                submit_btn = await login_page.query_selector(
                                    "button[type='submit'], input[type='submit'], button:has-text('Next'), button:has-text('Sign in')"
                                )
                                
                                if submit_btn:
                                    print("   Clicking submit button...")
                                    await submit_btn.click()
                                    print("\n⏳ Waiting for authentication...")
                                    
                                    # Wait for redirect or 2FA
                                    await login_page.wait_for_timeout(5000)
                
                # Manual login instructions
                print("\n" + "="*70)
                print("📝 MANUAL LOGIN INSTRUCTIONS:")
                print("="*70)
                print("1. The browser is now at your university login page")
                print("2. You can manually enter your credentials")
                print("3. Complete any 2FA/Okta verification if required")
                print("4. The script will detect when login is complete")
                print("="*70)
                
                # Wait for manual login (check every 2 seconds for up to 2 minutes)
                print("\n⏳ Waiting for manual login completion...")
                print("   (Script will check every 2 seconds)")
                
                login_complete = False
                for i in range(60):  # 2 minutes max
                    await asyncio.sleep(2)
                    
                    # Check if we've navigated away from login
                    new_url = login_page.url
                    if new_url != current_url and "login" not in new_url.lower():
                        print(f"\n✅ Login successful! Now at: {new_url}")
                        login_complete = True
                        break
                    
                    # Progress indicator
                    if i % 5 == 0:
                        print(f"   Still waiting... ({i*2}s / 120s)")
                
                if not login_complete:
                    print("\n⚠️  Login timeout - you may need to complete login manually")
            
            # Step 5: Test the authenticated session
            print("\n🧪 Step 5: Testing authenticated session...")
            
            # Try accessing another paper
            test_dois = [
                "10.1016/j.neuron.2018.01.048",
                "10.1126/science.1172133"
            ]
            
            for doi in test_dois:
                print(f"\n   Testing DOI: {doi}")
                
                # Navigate to new DOI
                new_url = f"{resolver_url}?rft_id=info:doi/{doi}"
                await page.goto(new_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                
                # Look for PDF or full-text
                pdf_link = await page.query_selector("a[href*='.pdf']")
                full_text = await page.query_selector("a:has-text('Full Text')")
                
                if pdf_link or full_text:
                    print(f"   ✓ Access confirmed for {doi}")
                else:
                    print(f"   ⚠️  No direct access found for {doi}")
            
            # Step 6: Save session info
            print("\n💾 Step 6: Session information")
            
            # Get cookies
            cookies = await login_page.context.cookies()
            print(f"   Cookies saved: {len(cookies)} cookies")
            
            # You could save these for future use
            session_file = f"zenrows_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(session_file, 'w') as f:
                json.dump({
                    "cookies": cookies,
                    "timestamp": datetime.now().isoformat(),
                    "browser": "zenrows"
                }, f, indent=2)
            print(f"   Session saved to: {session_file}")
            
            # Final screenshot
            final_screenshot = f"final_state_{datetime.now().strftime('%H%M%S')}.png"
            await page.screenshot(path=final_screenshot)
            print(f"   Final screenshot: {final_screenshot}")
            
            # Keep browser open for a bit if needed
            print("\n⏸️  Browser will close in 10 seconds...")
            print("   (You can take manual screenshots if needed)")
            await asyncio.sleep(10)
            
            await browser.close()
            print("\n✅ Browser closed")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("Manual Login Guide Complete!")
    print("="*70)
    print("\nKey Points:")
    print("• ZenRows browser runs on their servers (not locally)")
    print("• You can see and interact with the browser")
    print("• Session persists across page navigations")
    print("• Cookies can be saved for session reuse")
    print("• Great for bypassing anti-bot measures")
    print("="*70)

async def quick_manual_login():
    """Simplified version for quick manual login."""
    
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        return
    
    print("Quick Manual Login")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Connect
        browser = await p.chromium.connect_over_cdp(
            f"wss://browser.zenrows.com?apikey={api_key}&proxy_country=au"
        )
        page = await browser.new_page()
        
        # Go to resolver
        resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
        doi = "10.1038/nature12373"
        await page.goto(f"{resolver_url}?rft_id=info:doi/{doi}")
        
        print("\n🌐 Browser is ready at resolver page")
        print("📝 You can now:")
        print("   1. Click on any full-text link")
        print("   2. Login when prompted")
        print("   3. Access papers with your institutional subscription")
        
        # Keep open for manual interaction
        print("\n⏸️  Browser will stay open for 5 minutes...")
        print("   Use this time to login and access papers")
        
        await asyncio.sleep(300)  # 5 minutes
        
        await browser.close()
        print("\n✅ Session ended")

if __name__ == "__main__":
    import sys
    
    # Source environment
    import subprocess
    env_file = "/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src"
    result = subprocess.run(
        f"source {env_file} && env",
        shell=True,
        capture_output=True,
        text=True,
        executable="/bin/bash"
    )
    
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('SCITEX_'):
                    os.environ[key] = value
    
    # Choose mode
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(quick_manual_login())
    else:
        asyncio.run(manual_login_workflow())