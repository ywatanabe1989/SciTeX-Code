#!/usr/bin/env python3
"""
ZenRows Click GO Button

This script navigates to the resolver and clicks the GO button to access papers.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def download_via_go_button():
    """Download papers by clicking GO buttons on resolver page"""
    
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                            "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    
    print("ZenRows Download via GO Button")
    print("="*60)
    
    # Test DOIs
    test_dois = [
        ("10.1371/journal.pone.0021079", "Open Access - PLoS One"),
        ("10.1111/acer.15478", "Paywalled - Alcoholism Research"),
        ("10.1038/s41586-020-2649-2", "Nature paper")
    ]
    
    async with async_playwright() as p:
        connection_url = f"wss://browser.zenrows.com/?apikey={zenrows_api_key}"
        browser = await p.chromium.connect_over_cdp(
            endpoint_url=connection_url,
            timeout=120000
        )
        
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080}
        )
        
        for doi, description in test_dois:
            print(f"\n{'='*60}")
            print(f"Testing: {description}")
            print(f"DOI: {doi}")
            print("-"*60)
            
            page = await context.new_page()
            
            try:
                # Navigate to resolver
                url = f"{resolver_url}?doi={doi}"
                print(f"Navigating to resolver...")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Take initial screenshot
                os.makedirs("zenrows_screenshots", exist_ok=True)
                screenshot_path = f"zenrows_screenshots/resolver_{doi.replace('/', '_')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"Resolver screenshot: {screenshot_path}")
                
                # Look for GO buttons
                go_buttons = await page.locator('input[type="submit"][value="GO"]').all()
                print(f"Found {len(go_buttons)} GO buttons")
                
                if go_buttons:
                    # Try the first GO button (usually DOAJ or first open access option)
                    print("Clicking first GO button...")
                    
                    # Handle potential popup
                    async with page.expect_popup() as popup_info:
                        await go_buttons[0].click()
                        print("Clicked GO button, waiting for popup...")
                    
                    try:
                        popup = await popup_info.value
                        await popup.wait_for_load_state("networkidle", timeout=30000)
                        
                        popup_url = popup.url
                        print(f"Popup opened: {popup_url[:80]}...")
                        
                        # Take screenshot of popup
                        popup_screenshot = f"zenrows_screenshots/popup_{doi.replace('/', '_')}.png"
                        await popup.screenshot(path=popup_screenshot, full_page=True)
                        print(f"Popup screenshot: {popup_screenshot}")
                        
                        # Look for PDF links in popup
                        pdf_found = False
                        pdf_selectors = [
                            'a[href*=".pdf"]',
                            'a:has-text("PDF")',
                            'a:has-text("Download")',
                            'button:has-text("PDF")',
                            'a.pdf-link'
                        ]
                        
                        for selector in pdf_selectors:
                            try:
                                if await popup.locator(selector).count() > 0:
                                    pdf_link = popup.locator(selector).first
                                    href = await pdf_link.get_attribute('href')
                                    
                                    if href:
                                        # Make absolute URL if needed
                                        if href.startswith('/'):
                                            base_url = '/'.join(popup_url.split('/')[:3])
                                            href = base_url + href
                                        
                                        print(f"Found PDF link: {href[:80]}...")
                                        
                                        # Download PDF
                                        pdf_response = await popup.goto(href)
                                        if pdf_response:
                                            content_type = pdf_response.headers.get('content-type', '')
                                            if 'pdf' in content_type.lower():
                                                pdf_content = await pdf_response.body()
                                                filename = f"{doi.replace('/', '_')}.pdf"
                                                filepath = download_dir / filename
                                                
                                                with open(filepath, 'wb') as f:
                                                    f.write(pdf_content)
                                                
                                                print(f"✓ Downloaded to: {filepath}")
                                                pdf_found = True
                                                break
                            except Exception as e:
                                continue
                        
                        if not pdf_found:
                            print("✗ No PDF link found in popup")
                        
                        await popup.close()
                        
                    except asyncio.TimeoutError:
                        print("✗ Popup timeout - might need authentication")
                    except Exception as e:
                        print(f"✗ Popup error: {e}")
                
                else:
                    print("✗ No GO buttons found - might need authentication or no access")
                    
                    # Check for "No full text" message
                    content = await page.content()
                    if "no full text" in content.lower():
                        print("  Resolver indicates no full text available")
                
            except Exception as e:
                print(f"✗ Error processing {doi}: {e}")
            
            finally:
                await page.close()
                
            # Delay between DOIs
            await asyncio.sleep(2)
        
        await browser.close()
        print("\n" + "="*60)
        print("Download session complete")

if __name__ == "__main__":
    asyncio.run(download_via_go_button())