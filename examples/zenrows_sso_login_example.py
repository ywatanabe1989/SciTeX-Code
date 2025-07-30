#!/usr/bin/env python3
"""
Example of automated SSO login using ZenRows remote browser.

This script demonstrates:
1. Connecting to ZenRows Scraping Browser
2. Navigating to university SSO login
3. Filling credentials automatically
4. Handling 2FA/Okta prompt
5. Using authenticated session to resolve DOIs
"""

import asyncio
import os
from playwright.async_api import async_playwright
from scitex import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def login_to_university_sso():
    """Login to university SSO using ZenRows remote browser."""
    
    # Get credentials from environment
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    uni_username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
    uni_password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    
    if not all([zenrows_api_key, uni_username, uni_password]):
        print("Error: Missing required credentials in environment!")
        print("Required: ZENROWS_API_KEY, OPENATHENS_USERNAME, OPENATHENS_PASSWORD")
        return None
    
    print("="*70)
    print("ZenRows Remote Browser - University SSO Login")
    print("="*70)
    print(f"Username: {uni_username}")
    print(f"Resolver: {resolver_url}")
    print(f"ZenRows Key: {zenrows_api_key[:10]}...")
    print("="*70 + "\n")
    
    async with async_playwright() as p:
        # Connect to ZenRows Scraping Browser
        print("Connecting to ZenRows remote browser...")
        connection_url = f"wss://browser.zenrows.com?apikey={zenrows_api_key}&proxy_country=au"
        
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000  # 2 minute timeout
            )
            print("✓ Connected to ZenRows browser")
            
            # Create a new page
            page = await browser.new_page()
            print("✓ Created new page")
            
            # Navigate to OpenURL resolver
            print(f"\nNavigating to resolver: {resolver_url}")
            await page.goto(resolver_url, wait_until="domcontentloaded")
            
            # Example DOI to test
            test_doi = "10.1038/nature12373"
            
            # Build OpenURL query
            openurl_params = {
                "url_ver": "Z39.88-2004",
                "url_ctx_fmt": "infofi/fmt:kev:mtx:ctx",
                "ctx_ver": "Z39.88-2004",
                "ctx_enc": "info:ofi/enc:UTF-8",
                "rft.genre": "article",
                "rft_id": f"info:doi/{test_doi}",
                "rfr_id": "info:sid/scitex.scholar"
            }
            
            # Navigate to resolver with DOI
            from urllib.parse import urlencode
            full_url = f"{resolver_url}?{urlencode(openurl_params)}"
            print(f"\nResolving DOI: {test_doi}")
            await page.goto(full_url, wait_until="domcontentloaded")
            
            # Check if we need to login
            current_url = page.url
            print(f"\nCurrent URL: {current_url}")
            
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print("\n🔐 Login required - filling credentials...")
                
                # Wait for login form
                try:
                    # Look for common username field selectors
                    username_selectors = [
                        "#username",
                        "input[name='username']",
                        "input[name='user']",
                        "input[type='text']",
                        "#user",
                        "#login"
                    ]
                    
                    username_field = None
                    for selector in username_selectors:
                        try:
                            username_field = await page.wait_for_selector(selector, timeout=5000)
                            if username_field:
                                print(f"✓ Found username field: {selector}")
                                break
                        except:
                            continue
                    
                    if username_field:
                        # Fill username
                        await username_field.fill(uni_username)
                        print(f"✓ Filled username: {uni_username}")
                        
                        # Find password field
                        password_selectors = [
                            "#password",
                            "input[name='password']",
                            "input[type='password']",
                            "#pass"
                        ]
                        
                        password_field = None
                        for selector in password_selectors:
                            try:
                                password_field = await page.wait_for_selector(selector, timeout=5000)
                                if password_field:
                                    print(f"✓ Found password field: {selector}")
                                    break
                            except:
                                continue
                        
                        if password_field:
                            await password_field.fill(uni_password)
                            print("✓ Filled password")
                            
                            # Find and click submit button
                            submit_selectors = [
                                "button[type='submit']",
                                "input[type='submit']",
                                "button:has-text('Sign in')",
                                "button:has-text('Log in')",
                                "button:has-text('Login')",
                                "#submit"
                            ]
                            
                            for selector in submit_selectors:
                                try:
                                    submit_btn = await page.wait_for_selector(selector, timeout=2000)
                                    if submit_btn:
                                        print(f"✓ Found submit button: {selector}")
                                        await submit_btn.click()
                                        print("✓ Clicked submit")
                                        break
                                except:
                                    continue
                            
                            # Wait for navigation or 2FA
                            print("\n⏳ Waiting for authentication...")
                            print("   If 2FA/Okta prompt appears, approve it on your device")
                            
                            # Wait up to 60 seconds for successful login
                            for i in range(60):
                                await asyncio.sleep(1)
                                current_url = page.url
                                
                                # Check if we're past the login page
                                if "login" not in current_url.lower() and "auth" not in current_url.lower():
                                    print("\n✓ Authentication successful!")
                                    break
                                
                                if i % 10 == 0:
                                    print(f"   Still waiting... ({i}s)")
                        else:
                            print("✗ Could not find password field")
                    else:
                        print("✗ Could not find username field")
                        
                except Exception as e:
                    print(f"✗ Login error: {e}")
            
            # Check if we can find PDF links
            print("\n🔍 Looking for PDF links...")
            
            # Common PDF link patterns
            pdf_selectors = [
                "a[href*='.pdf']",
                "a:has-text('PDF')",
                "a:has-text('Full Text')",
                "a:has-text('Download')",
                "a[title*='PDF']",
                "button:has-text('PDF')",
                "a[href*='pdf']"
            ]
            
            pdf_url = None
            for selector in pdf_selectors:
                try:
                    pdf_links = await page.query_selector_all(selector)
                    if pdf_links:
                        for link in pdf_links:
                            href = await link.get_attribute("href")
                            if href:
                                pdf_url = href
                                print(f"✓ Found PDF link: {pdf_url[:50]}...")
                                break
                    if pdf_url:
                        break
                except:
                    continue
            
            if not pdf_url:
                print("✗ No PDF links found")
                # Take screenshot for debugging
                screenshot_path = "zenrows_debug.png"
                await page.screenshot(path=screenshot_path)
                print(f"   Screenshot saved: {screenshot_path}")
            
            # Return the authenticated browser for further use
            return browser, page, pdf_url
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None

async def main():
    """Main test function."""
    
    # Source environment variables
    import subprocess
    env_file = "/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src"
    
    # Source the file
    result = subprocess.run(
        f"source {env_file} && env",
        shell=True,
        capture_output=True,
        text=True,
        executable="/bin/bash"
    )
    
    if result.returncode == 0:
        # Parse environment variables
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('SCITEX_'):
                    os.environ[key] = value
    
    # Run the login test
    browser, page, pdf_url = await login_to_university_sso()
    
    if browser:
        print("\n" + "="*70)
        print("SESSION ESTABLISHED")
        print("="*70)
        print("The remote browser session is now authenticated.")
        print("You can use this session to resolve multiple DOIs.")
        
        # Test more DOIs with the authenticated session
        if page:
            test_dois = [
                "10.1016/j.neuron.2018.01.048",
                "10.1126/science.1172133"
            ]
            
            print(f"\nTesting more DOIs with authenticated session...")
            for doi in test_dois:
                print(f"\nResolving: {doi}")
                # Build URL and navigate
                openurl_params = {
                    "url_ver": "Z39.88-2004",
                    "rft.genre": "article",
                    "rft_id": f"info:doi/{doi}",
                    "rfr_id": "info:sid/scitex.scholar"
                }
                from urllib.parse import urlencode
                full_url = f"{os.getenv('SCITEX_SCHOLAR_OPENURL_RESOLVER_URL')}?{urlencode(openurl_params)}"
                
                await page.goto(full_url, wait_until="domcontentloaded")
                
                # Quick check for PDF
                pdf_link = await page.query_selector("a[href*='.pdf']")
                if pdf_link:
                    print("  ✓ PDF available")
                else:
                    print("  ✗ No PDF found")
        
        # Close browser
        await browser.close()
        print("\n✓ Browser closed")

if __name__ == "__main__":
    asyncio.run(main())