#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Capture cookies from logged-in session and test PDF download_async
# ----------------------------------------

"""
Captures cookies from an already logged-in OpenAthens session and tests PDF download_async.
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright
from pathlib import Path
import json

async def capture_and_test_async():
    """Capture cookies from logged-in session and test download_async."""
    
    print("=== Capturing Cookies from Logged-in Session ===\n")
    
    cookies = None
    
    async with async_playwright() as p:
        # Launch browser and navigate to the logged-in page
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Go to the research page (where you're logged in)
        research_url = "https://my.openathens.net/app/research"
        print(f"Navigating to: {research_url}")
        print("Please make sure you're logged in...")
        await page.goto(research_url)
        
        # Wait a moment for page to load
        await asyncio.sleep(3)
        
        # Check if logged in
        current_url = page.url
        print(f"\nCurrent URL: {current_url}")
        
        # Capture cookies
        print("\nCapturing cookies...")
        cookies = await page.context.cookies()
        print(f"Captured {len(cookies)} cookies")
        
        # Save cookies
        cookie_file = Path("openathens_session_cookies.json")
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"Saved cookies to: {cookie_file}")
        
        # Show cookie domains and important cookies
        domains = set()
        important_cookies = []
        
        for cookie in cookies:
            domains.add(cookie['domain'])
            name = cookie['name'].lower()
            if any(key in name for key in ['auth', 'session', 'token', 'openathens', 'saml']):
                important_cookies.append(f"{cookie['name']} ({cookie['domain']})")
        
        print(f"\nCookie domains: {', '.join(domains)}")
        if important_cookies:
            print(f"Important cookies: {', '.join(important_cookies)}")
        
        # Keep browser open for testing
        print("\n" + "="*50)
        print("Now let's test download_asyncing a PDF...")
        print("="*50)
        
        # Test URLs from different publishers
        test_urls = [
            ("Annual Reviews", "https://www.annualreviews.org/doi/pdf/10.1146/annurev-neuro-111020-103314"),
            ("Nature", "https://www.nature.com/articles/s41586-020-2314-9.pdf"),
            ("Science Direct", "https://www.sciencedirect.com/science/article/pii/S0092867420306772/pdfft"),
        ]
        
        for publisher, url in test_urls:
            print(f"\n\nTesting {publisher}...")
            print(f"URL: {url}")
            
            # Navigate to the PDF URL in the browser
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)
                
                current_url = page.url
                print(f"Redirected to: {current_url}")
                
                # Check if we got a PDF
                # Some publishers serve PDFs directly, others through viewers
                if 'pdf' in current_url.lower() or page.url == url:
                    print("✓ Reached PDF URL")
                else:
                    print("✗ Redirected away from PDF")
                    
            except Exception as e:
                print(f"✗ Error navigating: {e}")
        
        print("\n\nKeeping browser open. Press Enter to close...")
        input()
        
        await browser.close()
    
    # Now test with aiohttp using captured cookies
    print("\n" + "="*50)
    print("Testing direct download_async with captured cookies...")
    print("="*50)
    
    # Create cookie jar from captured cookies
    cookie_jar = aiohttp.CookieJar()
    
    # Group cookies by domain
    cookies_by_domain = {}
    for cookie in cookies:
        domain = cookie['domain']
        if domain not in cookies_by_domain:
            cookies_by_domain[domain] = {}
        cookies_by_domain[domain][cookie['name']] = cookie['value']
    
    print(f"\nCookies organized by domain:")
    for domain, domain_cookies in cookies_by_domain.items():
        print(f"  {domain}: {len(domain_cookies)} cookies")
    
    # Test download_async with aiohttp
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
        # Add all cookies to session
        for cookie in cookies:
            session.cookie_jar.update_cookies(
                {cookie['name']: cookie['value']},
                response_url=f"https://{cookie['domain'].lstrip('.')}"
            )
        
        # Test download_async
        test_url = "https://www.annualreviews.org/doi/pdf/10.1146/annurev-neuro-111020-103314"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,*/*',
            'Referer': 'https://my.openathens.net/',
        }
        
        print(f"\nTrying to download_async: {test_url}")
        
        try:
            async with session.get(test_url, headers=headers, allow_redirects=True) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                print(f"Final URL: {response.url}")
                
                if response.status == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                    content = await response.read()
                    pdf_path = Path("test_openathens_download_async.pdf")
                    
                    with open(pdf_path, 'wb') as f:
                        f.write(content)
                    
                    print(f"\n✓ SUCCESS! PDF download_asynced to: {pdf_path}")
                    print(f"File size: {len(content):,} bytes")
                else:
                    print("\n✗ Could not download_async PDF directly")
                    print("The cookies might not be sufficient for direct download_async")
                    print("May need to use browser automation for download_asyncs")
                    
        except Exception as e:
            print(f"\n✗ Download error: {e}")
    
    print("\n" + "="*50)
    print("Analysis complete!")
    print("\nConclusions:")
    print("- Check if browser navigation to PDFs worked")
    print("- Check if direct download_async with cookies worked")
    print("- Saved cookies are in 'openathens_session_cookies.json'")

if __name__ == "__main__":
    asyncio.run(capture_and_test_async())