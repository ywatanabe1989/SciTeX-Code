#!/usr/bin/env python3
"""
ZenRows Final Solution

Complete working solution for downloading papers via ZenRows.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def download_papers_zenrows(dois):
    """Download papers using ZenRows to bypass bot protection"""
    
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                            "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    screenshot_dir = Path("zenrows_screenshots") 
    screenshot_dir.mkdir(exist_ok=True)
    
    print("ZenRows Paper Download Solution")
    print("="*60)
    print(f"Resolver: {resolver_url}")
    print(f"Downloads: {download_dir}/")
    print(f"Screenshots: {screenshot_dir}/")
    print("="*60)
    
    async with async_playwright() as p:
        # Connect to ZenRows remote browser with Australian proxy
        proxy_country = os.getenv("SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", "au")
        connection_url = f"wss://browser.zenrows.com/?apikey={api_key}&proxy_country={proxy_country}"
        print(f"Using proxy country: {proxy_country}")
        
        browser = await p.chromium.connect_over_cdp(
            endpoint_url=connection_url,
            timeout=120000
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        results = []
        
        for i, doi in enumerate(dois, 1):
            print(f"\n[{i}/{len(dois)}] Processing: {doi}")
            print("-"*40)
            
            page = await context.new_page()
            
            try:
                # Navigate to resolver
                url = f"{resolver_url}?doi={doi}"
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Screenshot resolver page
                resolver_screenshot = screenshot_dir / f"{i:02d}_resolver_{doi.replace('/', '_')}.png"
                await page.screenshot(path=resolver_screenshot, full_page=True)
                print(f"Resolver screenshot: {resolver_screenshot}")
                
                # Look for GO links (they are anchor tags, not buttons!)
                go_links = await page.locator('a:has-text("GO")').all()
                print(f"Found {len(go_links)} GO links")
                
                if go_links:
                    # Click the first GO link
                    print("Clicking first GO link...")
                    
                    # Handle new page/tab
                    async with context.expect_page() as new_page_info:
                        await go_links[0].click()
                    
                    new_page = await new_page_info.value
                    await new_page.wait_for_load_state("networkidle", timeout=30000)
                    
                    new_url = new_page.url
                    print(f"Opened: {new_url[:80]}...")
                    
                    # Screenshot the target page
                    target_screenshot = screenshot_dir / f"{i:02d}_target_{doi.replace('/', '_')}.png"
                    await new_page.screenshot(path=target_screenshot, full_page=True)
                    print(f"Target screenshot: {target_screenshot}")
                    
                    # Look for PDF
                    pdf_found = False
                    
                    # Direct PDF link
                    if new_url.endswith('.pdf'):
                        print("Direct PDF URL!")
                        # Download directly
                        response = await new_page.goto(new_url)
                        if response:
                            content = await response.body()
                            filename = f"{doi.replace('/', '_')}.pdf"
                            filepath = download_dir / filename
                            with open(filepath, 'wb') as f:
                                f.write(content)
                            print(f"✓ Downloaded: {filepath}")
                            results.append((doi, str(filepath), "success"))
                            pdf_found = True
                    
                    # Look for PDF links on page
                    if not pdf_found:
                        pdf_selectors = [
                            'a[href$=".pdf"]',
                            'a:has-text("PDF")',
                            'a:has-text("Download")',
                            'button:has-text("PDF")',
                            'iframe[src*=".pdf"]'
                        ]
                        
                        for selector in pdf_selectors:
                            try:
                                elements = await new_page.locator(selector).all()
                                if elements:
                                    element = elements[0]
                                    href = await element.get_attribute('href') if element else None
                                    
                                    if href:
                                        # Make absolute URL
                                        if href.startswith('/'):
                                            base = '/'.join(new_url.split('/')[:3])
                                            href = base + href
                                        
                                        print(f"Found PDF link: {href[:80]}...")
                                        
                                        # Download PDF
                                        pdf_response = await new_page.goto(href)
                                        if pdf_response:
                                            content = await pdf_response.body()
                                            filename = f"{doi.replace('/', '_')}.pdf"
                                            filepath = download_dir / filename
                                            with open(filepath, 'wb') as f:
                                                f.write(content)
                                            print(f"✓ Downloaded: {filepath}")
                                            results.append((doi, str(filepath), "success"))
                                            pdf_found = True
                                            break
                            except:
                                continue
                    
                    if not pdf_found:
                        print("✗ No PDF found")
                        results.append((doi, new_url, "no_pdf"))
                    
                    await new_page.close()
                    
                else:
                    print("✗ No GO links found")
                    
                    # Check content for access issues
                    content = await page.content()
                    if "no full text" in content.lower():
                        results.append((doi, None, "no_access"))
                    else:
                        results.append((doi, None, "no_go_links"))
                
            except Exception as e:
                print(f"✗ Error: {e}")
                results.append((doi, None, f"error: {str(e)[:50]}"))
            
            finally:
                await page.close()
        
        await browser.close()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        successful = [r for r in results if r[2] == "success"]
        print(f"Successful downloads: {len(successful)}/{len(results)}")
        
        for doi, result, status in results:
            if status == "success":
                print(f"✓ {doi} -> {result}")
            else:
                print(f"✗ {doi}: {status}")
        
        return results


async def main():
    # Test DOIs
    test_dois = [
        "10.1371/journal.pone.0021079",  # Open access - should work
        "10.1111/acer.15478",  # May need auth
        "10.1038/s41586-019-1786-y",  # Nature - may need auth
    ]
    
    await download_papers_zenrows(test_dois)


if __name__ == "__main__":
    asyncio.run(main())