#!/usr/bin/env python3
"""
Debug ZenRows browser with screenshots to see what's happening.
"""

import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def debug_zenrows_with_screenshots():
    """Debug ZenRows browser by taking screenshots at each step."""
    
    # Get API key
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not api_key:
        print("Error: SCITEX_SCHOLAR_ZENROWS_API_KEY not set")
        return
    
    print("ZenRows Browser Debug with Screenshots")
    print("=" * 70)
    
    # Create screenshots directory
    screenshot_dir = "zenrows_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"Screenshots will be saved to: {screenshot_dir}/")
    
    # Test DOI
    test_doi = "10.1038/nature12373"
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                            "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    
    async with async_playwright() as p:
        # Connect to ZenRows browser
        print("\nConnecting to ZenRows browser...")
        connection_url = f"wss://browser.zenrows.com?apikey={api_key}&proxy_country=au"
        
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            print("✓ Connected!")
            
            # Create page with viewport
            page = await browser.new_page(
                viewport={"width": 1920, "height": 1080}
            )
            
            # Helper to take timestamped screenshot
            async def take_screenshot(name):
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"{screenshot_dir}/{timestamp}_{name}.png"
                await page.screenshot(path=filename, full_page=True)
                print(f"  📸 Screenshot: {filename}")
                return filename
            
            # Step 1: Navigate to resolver
            openurl = f"{resolver_url}?rft_id=info:doi/{test_doi}"
            print(f"\n1. Navigating to OpenURL resolver...")
            print(f"   URL: {openurl}")
            
            await page.goto(openurl, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)  # Wait for JavaScript
            
            current_url = page.url
            page_title = await page.title()
            print(f"   Current URL: {current_url}")
            print(f"   Page Title: {page_title}")
            await take_screenshot("01_resolver_page")
            
            # Step 2: Look for links
            print(f"\n2. Looking for links on the page...")
            
            # Get all links
            links = await page.query_selector_all("a")
            print(f"   Found {len(links)} links total")
            
            # Look for relevant links
            relevant_links = []
            for link in links[:20]:  # Check first 20 links
                try:
                    text = await link.text_content()
                    href = await link.get_attribute("href")
                    onclick = await link.get_attribute("onclick")
                    
                    if text and any(keyword in text.lower() for keyword in ["full text", "pdf", "article", "nature"]):
                        relevant_links.append({
                            "text": text.strip(),
                            "href": href,
                            "onclick": onclick
                        })
                except:
                    continue
            
            print(f"   Found {len(relevant_links)} relevant links:")
            for i, link in enumerate(relevant_links[:5]):
                print(f"     {i+1}. {link['text']}")
                if link['href']:
                    print(f"        href: {link['href'][:80]}...")
                if link['onclick']:
                    print(f"        onclick: {link['onclick'][:80]}...")
            
            # Step 3: Try clicking on full-text link
            if relevant_links:
                print(f"\n3. Trying to click on first relevant link...")
                
                # Find and click the first good link
                for link_info in relevant_links:
                    try:
                        # Find the link element again
                        if link_info['text']:
                            link_elem = await page.query_selector(f"a:has-text('{link_info['text']}')")
                            if link_elem:
                                print(f"   Clicking: {link_info['text']}")
                                
                                # Click and wait for navigation
                                await link_elem.click()
                                await page.wait_for_timeout(5000)  # Wait for redirect/popup
                                
                                # Check if new page/tab opened
                                pages = browser.contexts[0].pages
                                if len(pages) > 1:
                                    print(f"   New tab opened! Switching to it...")
                                    new_page = pages[-1]
                                    await new_page.wait_for_load_state()
                                    
                                    new_url = new_page.url
                                    new_title = await new_page.title()
                                    print(f"   New tab URL: {new_url}")
                                    print(f"   New tab title: {new_title}")
                                    
                                    await new_page.screenshot(
                                        path=f"{screenshot_dir}/{datetime.now().strftime('%H%M%S')}_02_new_tab.png",
                                        full_page=True
                                    )
                                    print(f"  📸 Screenshot: 02_new_tab.png")
                                else:
                                    # Same page navigation
                                    new_url = page.url
                                    new_title = await page.title()
                                    print(f"   Navigated to: {new_url}")
                                    print(f"   Page title: {new_title}")
                                    await take_screenshot("02_after_click")
                                
                                break
                    except Exception as e:
                        print(f"   Failed to click: {e}")
                        continue
            
            # Step 4: Check for login page
            current_url = page.url
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print(f"\n4. Login page detected!")
                await take_screenshot("03_login_page")
                
                # Look for login form elements
                username_field = await page.query_selector("input[type='text'], input[name='username'], #username")
                password_field = await page.query_selector("input[type='password'], #password")
                
                if username_field and password_field:
                    print("   Found login form fields")
                    print("   📝 Manual login would be required here")
                else:
                    print("   Could not identify login form fields")
            
            # Step 5: Final state
            print(f"\n5. Final state:")
            final_url = page.url
            final_title = await page.title()
            print(f"   URL: {final_url}")
            print(f"   Title: {final_title}")
            await take_screenshot("04_final_state")
            
            # Check for PDF elements
            pdf_links = await page.query_selector_all("a[href*='.pdf']")
            pdf_buttons = await page.query_selector_all("button:has-text('PDF'), a:has-text('PDF')")
            
            print(f"\n   PDF elements found:")
            print(f"   - Direct PDF links: {len(pdf_links)}")
            print(f"   - PDF buttons/links: {len(pdf_buttons)}")
            
            await browser.close()
            print("\n✓ Browser closed")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("Debug complete! Check the screenshots folder.")
    print("="*70)

if __name__ == "__main__":
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
    
    # Run debug
    asyncio.run(debug_zenrows_with_screenshots())