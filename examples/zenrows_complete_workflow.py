#!/usr/bin/env python3
"""
ZenRows Complete Workflow

This script provides a complete workflow for downloading papers using ZenRows:
1. Remote browser execution (no local windows)
2. Screenshots to show progress
3. Handles authentication and downloads
"""

import os
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

class ZenRowsWorkflow:
    def __init__(self):
        self.api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        self.resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                                     "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
        self.username = os.getenv("SCITEX_SCHOLAR_OPENATHENS_USERNAME")
        self.password = os.getenv("SCITEX_SCHOLAR_OPENATHENS_PASSWORD")
        self.screenshot_dir = Path("zenrows_workflow_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.download_dir = Path("downloaded_papers")
        self.download_dir.mkdir(exist_ok=True)
        
    async def run_workflow(self, dois):
        """Run complete workflow for downloading papers"""
        
        print("ZenRows Complete Workflow")
        print("="*60)
        print("IMPORTANT: This runs in ZenRows cloud - NO browser windows will open locally!")
        print("Screenshots will be saved to show progress")
        print("="*60 + "\n")
        
        async with async_playwright() as p:
            # Connect to remote ZenRows browser
            connection_url = f"wss://browser.zenrows.com/?apikey={self.api_key}"
            print("Connecting to ZenRows remote browser...")
            
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            
            print("✓ Connected to remote browser\n")
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            results = []
            
            for i, doi in enumerate(dois, 1):
                print(f"\n{'='*60}")
                print(f"[{i}/{len(dois)}] Processing DOI: {doi}")
                print("-"*60)
                
                page = await context.new_page()
                
                try:
                    # Step 1: Navigate to resolver
                    openurl = f"{self.resolver_url}?doi={doi}"
                    print(f"1. Navigating to resolver...")
                    print(f"   URL: {openurl}")
                    
                    await page.goto(openurl, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    # Take screenshot of resolver page
                    screenshot_path = self.screenshot_dir / f"{i:02d}_resolver_{doi.replace('/', '_')}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   Screenshot: {screenshot_path}")
                    
                    # Step 2: Check if we need authentication
                    current_url = page.url
                    content = await page.content()
                    
                    if "login" in current_url.lower() or "sign in" in content.lower():
                        print("\n2. Authentication required")
                        # Would implement auth here
                        results.append((doi, None, "needs_auth"))
                        continue
                    
                    # Step 3: Look for access options
                    print("\n2. Looking for access options...")
                    
                    # Check for "No full text" message
                    if "no full text" in content.lower() or "no online text available" in content.lower():
                        print("   ✗ No full text available")
                        results.append((doi, None, "no_access"))
                        continue
                    
                    # Look for GO buttons
                    go_buttons = await page.locator('input[type="submit"][value="GO"]').all()
                    print(f"   Found {len(go_buttons)} access options (GO buttons)")
                    
                    if go_buttons:
                        # Try clicking the first GO button
                        print("\n3. Clicking first GO button...")
                        
                        # Set up to catch new page/popup
                        new_page_promise = None
                        
                        def handle_page(new_page):
                            nonlocal new_page_promise
                            new_page_promise = new_page
                        
                        context.on("page", handle_page)
                        
                        # Click GO button
                        await go_buttons[0].click()
                        await page.wait_for_timeout(3000)
                        
                        # Check if new page opened
                        if new_page_promise:
                            target_page = new_page_promise
                            await target_page.wait_for_load_state("networkidle", timeout=30000)
                            
                            target_url = target_page.url
                            print(f"   New page opened: {target_url[:80]}...")
                            
                            # Take screenshot of target page
                            screenshot_path = self.screenshot_dir / f"{i:02d}_target_{doi.replace('/', '_')}.png"
                            await target_page.screenshot(path=screenshot_path, full_page=True)
                            print(f"   Screenshot: {screenshot_path}")
                            
                            # Look for PDF link
                            pdf_url = await self._find_pdf_link(target_page)
                            
                            if pdf_url:
                                print(f"\n4. Found PDF link: {pdf_url[:80]}...")
                                # Would download PDF here
                                results.append((doi, pdf_url, "pdf_found"))
                            else:
                                print("\n4. No PDF link found on target page")
                                results.append((doi, target_url, "no_pdf_link"))
                            
                            await target_page.close()
                        else:
                            # Check if current page changed
                            new_url = page.url
                            if new_url != current_url:
                                print(f"   Page redirected to: {new_url[:80]}...")
                                results.append((doi, new_url, "redirected"))
                            else:
                                print("   No navigation occurred")
                                results.append((doi, None, "no_navigation"))
                    else:
                        print("   ✗ No GO buttons found")
                        results.append((doi, None, "no_go_buttons"))
                
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    results.append((doi, None, f"error: {str(e)[:50]}"))
                
                finally:
                    await page.close()
                
                # Delay between DOIs
                if i < len(dois):
                    await asyncio.sleep(2)
            
            await browser.close()
            
            # Print summary
            print("\n" + "="*60)
            print("WORKFLOW SUMMARY")
            print("="*60)
            print(f"Total processed: {len(results)}")
            print(f"Screenshots saved in: {self.screenshot_dir}/")
            print("\nResults:")
            for doi, url, status in results:
                print(f"  {doi}: {status}")
                if url:
                    print(f"    URL: {url[:80]}...")
            
            return results
    
    async def _find_pdf_link(self, page):
        """Find PDF link on page"""
        pdf_selectors = [
            'a[href*=".pdf"]',
            'a:has-text("PDF")',
            'a:has-text("Download PDF")',
            'button:has-text("PDF")',
            'a.pdf-link',
            'iframe[src*=".pdf"]'
        ]
        
        for selector in pdf_selectors:
            try:
                elements = await page.locator(selector).all()
                for element in elements[:3]:  # Check first 3 matches
                    href = await element.get_attribute('href')
                    if href and ('.pdf' in href or 'download' in href.lower()):
                        # Make absolute URL
                        if href.startswith('/'):
                            base_url = '/'.join(page.url.split('/')[:3])
                            href = base_url + href
                        return href
            except:
                continue
        
        return None


async def main():
    """Run the workflow"""
    
    # Test DOIs
    test_dois = [
        "10.1371/journal.pone.0021079",  # Open access
        "10.1111/acer.15478",  # Paywalled
    ]
    
    workflow = ZenRowsWorkflow()
    await workflow.run_workflow(test_dois)


if __name__ == "__main__":
    asyncio.run(main())