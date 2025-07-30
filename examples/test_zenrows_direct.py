#!/usr/bin/env python3
"""
Direct test of ZenRows browser connection for manual SSO login.

This script shows the simplest way to:
1. Connect to ZenRows browser
2. Navigate to a DOI through your institution
3. Allow manual login
4. Get the PDF URL
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def test_zenrows_direct():
    """Direct test of ZenRows browser."""
    
    # Get credentials
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    
    if not all([zenrows_api_key, resolver_url]):
        print("Missing required environment variables!")
        return
    
    print("ZenRows Direct Browser Test")
    print("=" * 50)
    print(f"Resolver: {resolver_url}")
    print(f"API Key: {zenrows_api_key[:10]}...")
    print("=" * 50 + "\n")
    
    async with async_playwright() as p:
        # Connect to ZenRows
        print("Connecting to ZenRows browser...")
        connection_url = f"wss://browser.zenrows.com?apikey={zenrows_api_key}&proxy_country=au"
        
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=connection_url,
                timeout=120000
            )
            print("✓ Connected!\n")
            
            # Create page
            page = await browser.new_page()
            
            # Test DOI
            test_doi = "10.1038/nature12373"
            
            # Build OpenURL
            openurl = f"{resolver_url}?rft_id=info:doi/{test_doi}"
            
            print(f"Navigating to: {openurl}\n")
            await page.goto(openurl, wait_until="domcontentloaded")
            
            # Get current URL
            current_url = page.url
            print(f"Current URL: {current_url}\n")
            
            # Check if login is needed
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print("🔐 LOGIN REQUIRED")
                print("=" * 50)
                print("Please login manually in the browser.")
                print("The script will wait for you to complete login.")
                print("=" * 50 + "\n")
                
                # Wait for user to complete login (timeout after 2 minutes)
                print("Waiting for login completion...")
                for i in range(120):
                    await asyncio.sleep(1)
                    new_url = page.url
                    if new_url != current_url and "login" not in new_url.lower():
                        print(f"\n✓ Login successful! Now at: {new_url}")
                        break
                    if i % 10 == 0:
                        print(f"  Still waiting... ({i}s)")
            
            # Look for PDF
            print("\nLooking for PDF links...")
            pdf_links = await page.query_selector_all("a[href*='.pdf'], a:has-text('PDF')")
            
            if pdf_links:
                for link in pdf_links:
                    href = await link.get_attribute("href")
                    if href:
                        print(f"✓ Found PDF: {href}")
                        break
            else:
                print("✗ No PDF links found")
                
                # Take screenshot
                await page.screenshot(path="zenrows_page.png")
                print("Screenshot saved: zenrows_page.png")
            
            await browser.close()
            print("\n✓ Test complete!")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

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
    
    # Run test
    asyncio.run(test_zenrows_direct())