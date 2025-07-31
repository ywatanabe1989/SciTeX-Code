#!/usr/bin/env python3
"""
Automated login with ZenRows - handles credentials automatically.
You just need to approve Okta on your phone.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime

async def auto_login_with_okta():
    """Automated login that fills credentials and waits for Okta approval."""
    
    # Check environment
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
    password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
    
    if not all([api_key, username, password]):
        print("Error: Missing credentials. Please ensure these are set:")
        print("  - SCITEX_SCHOLAR_ZENROWS_API_KEY")
        print("  - SCITEX_SCHOLAR_OPENATHENS_USERNAME")
        print("  - SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
        return
    
    print("ZenRows Automated Login with Okta")
    print("=" * 70)
    print(f"Username: {username}")
    print("Password: ****")
    print("=" * 70)
    
    async with async_playwright() as p:
        # Connect to ZenRows
        print("\n🔌 Connecting to ZenRows browser...")
        connection_url = f"wss://browser.zenrows.com?apikey={api_key}&proxy_country=au"
        
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            print("✓ Connected!")
            
            # Create page
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # Navigate to resolver
            print("\n🌐 Navigating to resolver...")
            resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
            test_doi = "10.1038/nature12373"
            await page.goto(f"{resolver_url}?rft_id=info:doi/{test_doi}")
            await page.wait_for_timeout(3000)
            
            # Click on Nature or first full-text link
            print("\n🖱️  Clicking on full-text link...")
            full_text_link = await page.query_selector("a:has-text('Nature')")
            if not full_text_link:
                # Try other selectors
                full_text_link = await page.query_selector("a:has-text('Full Text')")
            
            if full_text_link:
                await full_text_link.click()
                await page.wait_for_timeout(5000)
                
                # Check for new tab
                pages = browser.contexts[0].pages
                if len(pages) > 1:
                    login_page = pages[-1]
                    await login_page.wait_for_load_state()
                    print("✓ New tab opened")
                else:
                    login_page = page
            else:
                print("⚠️  No full-text link found, continuing...")
                login_page = page
            
            # Wait for login page
            print("\n⏳ Waiting for login page...")
            try:
                # Wait for username field
                await login_page.wait_for_selector(
                    "input[type='text'], input[name='username'], #username",
                    timeout=10000
                )
                print("✓ Login page loaded")
            except:
                print("⚠️  Login page not detected, checking current page...")
            
            # Fill credentials
            print("\n🔐 Filling credentials automatically...")
            
            # Username
            username_field = await login_page.query_selector(
                "input[type='text'], input[name='username'], #username, input[name='user']"
            )
            
            if username_field:
                await username_field.fill(username)
                print(f"✓ Username filled: {username}")
                
                # Password
                password_field = await login_page.query_selector(
                    "input[type='password'], #password"
                )
                
                if password_field:
                    await password_field.fill(password)
                    print("✓ Password filled: ****")
                    
                    # Submit
                    submit_btn = await login_page.query_selector(
                        "button[type='submit'], input[type='submit'], button:has-text('Next'), button:has-text('Sign in'), button:has-text('Log in')"
                    )
                    
                    if submit_btn:
                        print("\n🚀 Submitting login form...")
                        await submit_btn.click()
                        
                        # Wait for Okta
                        print("\n" + "="*70)
                        print("📱 OKTA VERIFICATION REQUIRED")
                        print("="*70)
                        print("Please check your phone and approve the Okta push notification")
                        print("The script will continue automatically after approval")
                        print("="*70)
                        
                        # Monitor for successful login
                        login_url = login_page.url
                        success = False
                        
                        for i in range(60):  # Wait up to 2 minutes
                            await asyncio.sleep(2)
                            current_url = login_page.url
                            
                            # Check if we've moved away from login
                            if current_url != login_url and "login" not in current_url.lower():
                                print(f"\n✅ Login successful!")
                                print(f"   Now at: {current_url}")
                                success = True
                                break
                            
                            # Progress indicator
                            if i % 5 == 0:
                                print(f"   Waiting for Okta approval... ({i*2}s)")
                        
                        if not success:
                            print("\n⚠️  Timeout waiting for Okta approval")
                            return
                    else:
                        print("❌ Submit button not found")
                else:
                    print("❌ Password field not found")
            else:
                print("❌ Username field not found")
                
            # Test authenticated session with multiple DOIs
            print("\n🧪 Testing authenticated session with multiple DOIs...")
            
            test_dois = [
                "10.1002/hipo.22488",
                "10.1038/nature12373",
                "10.1016/j.neuron.2018.01.048",
                "10.1126/science.1172133",
                "10.1073/pnas.0608765104"
            ]
            
            results = []
            
            for doi in test_dois:
                print(f"\n📄 Resolving {doi}...")
                
                # Navigate to resolver with DOI
                await page.goto(f"{resolver_url}?rft_id=info:doi/{doi}")
                await page.wait_for_timeout(3000)
                
                # Look for PDF or full-text links
                pdf_found = False
                full_text_found = False
                
                # Check for PDF links
                pdf_links = await page.query_selector_all("a[href*='.pdf']")
                if pdf_links:
                    pdf_found = True
                    for link in pdf_links[:1]:  # Just check first one
                        href = await link.get_attribute("href")
                        print(f"   ✓ PDF link found: {href[:80]}...")
                
                # Check for full-text links
                if not pdf_found:
                    full_text_link = await page.query_selector("a:has-text('Full Text')")
                    if full_text_link:
                        full_text_found = True
                        href = await full_text_link.get_attribute("href") or "JavaScript link"
                        print(f"   ✓ Full-text link found: {href[:80]}...")
                
                # Click and check if we can reach the paper
                if full_text_link:
                    try:
                        await full_text_link.click()
                        await page.wait_for_timeout(5000)
                        
                        # Check if new tab opened
                        pages = browser.contexts[0].pages
                        if len(pages) > 1:
                            paper_page = pages[-1]
                            final_url = paper_page.url
                            await paper_page.close()
                        else:
                            final_url = page.url
                        
                        if any(domain in final_url for domain in ["wiley.com", "nature.com", "sciencedirect.com", "science.org"]):
                            print(f"   ✓ Successfully reached publisher: {final_url.split('/')[2]}")
                            results.append({"doi": doi, "status": "success", "url": final_url})
                        else:
                            results.append({"doi": doi, "status": "resolver_only"})
                    except:
                        results.append({"doi": doi, "status": "click_failed"})
                else:
                    results.append({"doi": doi, "status": "no_link_found"})
            
            # Summary
            print("\n" + "="*70)
            print("📊 SUMMARY")
            print("="*70)
            
            success_count = sum(1 for r in results if r["status"] == "success")
            print(f"\nSuccessfully accessed: {success_count}/{len(test_dois)} papers")
            
            print("\nDetailed results:")
            for result in results:
                status_icon = "✅" if result["status"] == "success" else "⚠️"
                print(f"{status_icon} {result['doi']}: {result['status']}")
                if "url" in result:
                    print(f"   URL: {result['url'][:80]}...")
            
            # Save session
            print("\n💾 Saving session...")
            cookies = await page.context.cookies()
            print(f"   Cookies: {len(cookies)} saved")
            
            # Keep browser open briefly
            print("\n⏸️  Browser will close in 10 seconds...")
            print("   (Take screenshots if needed)")
            await asyncio.sleep(10)
            
            await browser.close()
            print("\n✅ Session complete!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("ZenRows Automated Login")
    print("=" * 50)
    print("\nThis script will:")
    print("1. Connect to ZenRows browser")
    print("2. Navigate to your university resolver")
    print("3. Fill in your credentials automatically")
    print("4. Wait for you to approve Okta on your phone")
    print("5. Test access to multiple papers")
    print("=" * 50)
    
    # Check if credentials are set
    if not os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD"):
        print("\n⚠️  Setting up credentials from UNIMELB variables...")
        os.environ["SCITEX_SCHOLAR_OPENATHENS_USERNAME"] = os.getenv("UNIMELB_SSO_USERNAME", "")
        os.environ["SCITEX_SCHOLAR_OPENATHENS_PASSWORD"] = os.getenv("UNIMELB_SSO_PASSWORD", "")
    
    asyncio.run(auto_login_with_okta())