#!/usr/bin/env python3
"""
Download Papers Using Cached Authentication

This script uses your local browser with cached credentials to download papers.
"""

import os
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def download_with_cached_auth(dois):
    """Download papers using cached browser authentication"""
    
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    
    print("Download Papers with Cached Authentication")
    print("="*60)
    print(f"Using resolver: {resolver_url}")
    print(f"Downloads will be saved to: {download_dir}/")
    print(f"Papers to download: {len(dois)}")
    print("="*60 + "\n")
    
    async with async_playwright() as p:
        # Use local browser with your cached credentials
        browser = await p.chromium.launch(
            headless=False,  # Keep visible so you can monitor
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport=None,
            accept_downloads=True
        )
        
        # Set download path
        page = await context.new_page()
        
        successful_downloads = []
        failed_downloads = []
        
        for i, doi in enumerate(dois, 1):
            print(f"\n[{i}/{len(dois)}] Processing DOI: {doi}")
            
            try:
                # Build OpenURL
                url = f"{resolver_url}?url_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.genre=article&rft_id=info:doi/{doi}"
                
                print(f"  Navigating to resolver...")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)  # Let page fully load
                
                # Look for common download/access buttons
                download_selectors = [
                    'a:has-text("PDF")',
                    'a:has-text("Download")',
                    'a:has-text("Full Text")',
                    'a:has-text("View")',
                    'button:has-text("PDF")',
                    'a[href*=".pdf"]',
                    'a.download-link',
                    'a.pdf-link'
                ]
                
                clicked = False
                for selector in download_selectors:
                    try:
                        # Check if element exists
                        if await page.locator(selector).count() > 0:
                            print(f"  Found download link: {selector}")
                            
                            # Start waiting for download before clicking
                            async with page.expect_download() as download_info:
                                await page.click(selector, timeout=5000)
                            
                            download = await download_info.value
                            
                            # Save with DOI-based filename
                            filename = f"{doi.replace('/', '_')}.pdf"
                            save_path = download_dir / filename
                            await download.save_as(save_path)
                            
                            print(f"  ✓ Downloaded to: {save_path}")
                            successful_downloads.append((doi, str(save_path)))
                            clicked = True
                            break
                    except Exception as e:
                        continue
                
                if not clicked:
                    print(f"  ✗ No download link found")
                    failed_downloads.append((doi, "No download link found"))
                    
                    # Take screenshot for debugging
                    screenshot_path = download_dir / f"failed_{doi.replace('/', '_')}.png"
                    await page.screenshot(path=screenshot_path)
                    print(f"  Screenshot saved: {screenshot_path}")
                
                # Brief pause between downloads
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                failed_downloads.append((doi, str(e)))
        
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Successful: {len(successful_downloads)}")
        for doi, path in successful_downloads:
            print(f"  ✓ {doi} -> {path}")
        
        print(f"\nFailed: {len(failed_downloads)}")
        for doi, reason in failed_downloads:
            print(f"  ✗ {doi}: {reason}")
        
        print("\nPress Enter to close browser...")
        input()
        
        await browser.close()

# Test DOIs
TEST_DOIS = [
    "10.1111/acer.15478",  # Original test paper
    "10.1038/s41586-020-2649-2",  # Nature paper
    "10.1126/science.abc1234",  # Science paper (might not exist)
    "10.1016/j.cell.2020.04.035",  # Cell paper
    "10.1056/NEJMoa2001017"  # NEJM paper
]

if __name__ == "__main__":
    # You can modify this list or pass your own
    asyncio.run(download_with_cached_auth(TEST_DOIS[:2]))  # Test with first 2