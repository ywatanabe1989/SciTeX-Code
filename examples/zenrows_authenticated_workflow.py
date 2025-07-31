#!/usr/bin/env python3
"""
ZenRows Authenticated Workflow

Complete workflow for using ZenRows to bypass bot protection
while authenticating with institutional credentials.
"""

import os
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager

# Load environment variables
load_dotenv()

class ZenRowsAuthenticatedDownloader:
    """Handles authenticated downloads through ZenRows"""
    
    def __init__(self):
        self.zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        self.resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                                     "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
        self.username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
        self.password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
        self.session_file = Path("zenrows_session.json")
        self.download_dir = Path("downloaded_papers")
        self.download_dir.mkdir(exist_ok=True)
        
    async def establish_authenticated_session(self):
        """Establish authenticated session with ZenRows browser"""
        
        print("Establishing Authenticated Session with ZenRows")
        print("="*60)
        
        async with async_playwright() as p:
            # Connect to ZenRows
            connection_url = f"wss://browser.zenrows.com/?apikey={self.zenrows_api_key}"
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            # Navigate to a paper that requires authentication
            test_doi = "10.1111/acer.15478"
            openurl = f"{self.resolver_url}?doi={test_doi}"
            
            print(f"Navigating to: {openurl}")
            await page.goto(openurl, wait_until="networkidle")
            
            # Check if we need to authenticate
            current_url = page.url
            content = await page.content()
            
            if "login" in current_url.lower() or "sign in" in content.lower():
                print("\nAuthentication required. Attempting auto-login...")
                
                # Try to find and fill login fields
                login_success = await self._attempt_auto_login(page)
                
                if not login_success:
                    print("\nAuto-login failed. Manual intervention needed.")
                    print("Please check zenrows_screenshots/ for current page")
                    
                    # Take screenshot
                    screenshot_path = "zenrows_screenshots/login_page.png"
                    os.makedirs("zenrows_screenshots", exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    
                    # Here you would implement manual login flow
                    # For now, we'll return False
                    await browser.close()
                    return False
            
            # Save session data
            cookies = await context.cookies()
            session_data = {
                "cookies": cookies,
                "timestamp": datetime.now().isoformat(),
                "resolver_url": self.resolver_url
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"\nSession saved to: {self.session_file}")
            await browser.close()
            return True
    
    async def _attempt_auto_login(self, page):
        """Attempt automatic login with credentials"""
        
        try:
            # Common username field selectors
            username_selectors = [
                'input[name="username"]',
                'input[id="username"]',
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="username" i]',
                'input[placeholder*="email" i]'
            ]
            
            # Common password field selectors
            password_selectors = [
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]'
            ]
            
            # Try to fill username
            username_filled = False
            for selector in username_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.fill(selector, self.username, timeout=2000)
                        print(f"Filled username field: {selector}")
                        username_filled = True
                        break
                except:
                    continue
            
            # Try to fill password
            password_filled = False
            for selector in password_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.fill(selector, self.password, timeout=2000)
                        print(f"Filled password field: {selector}")
                        password_filled = True
                        break
                except:
                    continue
            
            if username_filled and password_filled:
                # Try to submit
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Sign in")',
                    'button:has-text("Login")',
                    'button:has-text("Log in")'
                ]
                
                for selector in submit_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            await page.click(selector)
                            print(f"Clicked submit: {selector}")
                            
                            # Wait for navigation or Okta
                            await page.wait_for_timeout(5000)
                            
                            # Check if we need Okta verification
                            if "okta" in page.url.lower():
                                print("\nOkta verification required!")
                                print("Complete verification on your phone...")
                                
                                # Wait up to 60 seconds for Okta
                                for i in range(12):
                                    await page.wait_for_timeout(5000)
                                    if "okta" not in page.url.lower():
                                        print("Okta verification completed!")
                                        break
                            
                            return True
                    except:
                        continue
            
            return False
            
        except Exception as e:
            print(f"Auto-login error: {e}")
            return False
    
    async def download_with_session(self, dois):
        """Download papers using established session"""
        
        print("\nDownloading Papers with ZenRows Session")
        print("="*60)
        
        # Load session if available
        session_data = None
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            print(f"Loaded session from: {self.session_file}")
        
        async with async_playwright() as p:
            connection_url = f"wss://browser.zenrows.com/?apikey={self.zenrows_api_key}"
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Restore cookies if available
            if session_data and 'cookies' in session_data:
                await context.add_cookies(session_data['cookies'])
                print("Restored session cookies")
            
            page = await context.new_page()
            
            results = []
            for i, doi in enumerate(dois, 1):
                print(f"\n[{i}/{len(dois)}] Downloading DOI: {doi}")
                
                try:
                    # Build OpenURL
                    openurl = f"{self.resolver_url}?doi={doi}"
                    
                    # Navigate to resolver
                    await page.goto(openurl, wait_until="networkidle")
                    await page.wait_for_timeout(2000)
                    
                    # Look for download links
                    download_found = False
                    download_selectors = [
                        'a:has-text("PDF")',
                        'a:has-text("Download")',
                        'a:has-text("Full Text")',
                        'a[href*=".pdf"]',
                        'button:has-text("PDF")'
                    ]
                    
                    for selector in download_selectors:
                        try:
                            if await page.locator(selector).count() > 0:
                                # Get the link URL
                                link_element = page.locator(selector).first
                                href = await link_element.get_attribute('href')
                                
                                if href:
                                    print(f"Found PDF link: {href[:80]}...")
                                    
                                    # Navigate to PDF
                                    pdf_response = await page.goto(href)
                                    
                                    if pdf_response:
                                        # Save PDF
                                        pdf_content = await pdf_response.body()
                                        filename = f"{doi.replace('/', '_')}.pdf"
                                        filepath = self.download_dir / filename
                                        
                                        with open(filepath, 'wb') as f:
                                            f.write(pdf_content)
                                        
                                        print(f"✓ Saved to: {filepath}")
                                        results.append((doi, str(filepath), "success"))
                                        download_found = True
                                        break
                        except Exception as e:
                            continue
                    
                    if not download_found:
                        print(f"✗ No download link found")
                        results.append((doi, None, "no_link"))
                        
                        # Take screenshot for debugging
                        screenshot_path = f"zenrows_screenshots/no_link_{doi.replace('/', '_')}.png"
                        os.makedirs("zenrows_screenshots", exist_ok=True)
                        await page.screenshot(path=screenshot_path)
                
                except Exception as e:
                    print(f"✗ Error: {e}")
                    results.append((doi, None, str(e)))
                
                # Delay between downloads
                if i < len(dois):
                    await page.wait_for_timeout(3000)
            
            await browser.close()
            
            # Print summary
            print("\n" + "="*60)
            print("DOWNLOAD SUMMARY")
            print("="*60)
            successful = [r for r in results if r[2] == "success"]
            print(f"Successful: {len(successful)}/{len(results)}")
            for doi, path, status in results:
                if status == "success":
                    print(f"  ✓ {doi} -> {path}")
                else:
                    print(f"  ✗ {doi}: {status}")
            
            return results


async def main():
    """Main workflow"""
    
    downloader = ZenRowsAuthenticatedDownloader()
    
    # Step 1: Establish authenticated session (only needed once)
    print("Step 1: Establishing authenticated session")
    session_established = await downloader.establish_authenticated_session()
    
    if not session_established:
        print("\nSession establishment failed. Manual login required.")
        print("Use zenrows_remote_control.py for manual login")
        return
    
    # Step 2: Download papers using the session
    print("\nStep 2: Downloading papers")
    test_dois = [
        "10.1111/acer.15478",  # Requires institutional access
        "10.1371/journal.pone.0021079",  # Open access
        "10.1038/s41586-020-2649-2",  # Nature paper
    ]
    
    results = await downloader.download_with_session(test_dois)
    
    print("\nWorkflow complete!")


if __name__ == "__main__":
    asyncio.run(main())