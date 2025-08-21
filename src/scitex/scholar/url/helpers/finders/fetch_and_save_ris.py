#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: fetch_and_save_ris.py
# ----------------------------------------

"""
Fetch and save RIS data from ScienceDirect for analysis.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def fetch_ris_data(pii: str = "S1087079220300964"):
    """Fetch RIS data from ScienceDirect."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to the article
        article_url = f"https://www.sciencedirect.com/science/article/pii/{pii}"
        print(f"📄 Navigating to {article_url}")
        await page.goto(article_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Handle cookie popup
        try:
            cookie_button = await page.query_selector('button#onetrust-accept-btn-handler')
            if cookie_button:
                await cookie_button.click()
                print("✅ Accepted cookies")
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Try to fetch RIS data using the export citation link
        print("🔍 Looking for export citation option...")
        
        # Method 1: Fetch RIS using JavaScript within page context
        ris_url = f"/sdfe/arp/cite?pii={pii}&format=application%2Fx-research-info-systems&withabstract=true"
        
        print(f"📥 Fetching RIS using page.evaluate...")
        
        # Fetch RIS data using JavaScript
        ris_text = await page.evaluate(f'''
            async () => {{
                try {{
                    const response = await fetch("{ris_url}", {{
                        credentials: 'include',
                        headers: {{
                            'Accept': 'text/plain, */*'
                        }}
                    }});
                    return await response.text();
                }} catch (e) {{
                    return null;
                }}
            }}
        ''')
        
        if ris_text and not ris_text.startswith('<!DOCTYPE'):
            print("✅ Got RIS data!")
            
            # Save RIS data
            output_dir = Path(__file__).parent / "sample_data"
            output_dir.mkdir(exist_ok=True)
            
            ris_file = output_dir / f"{pii}.ris"
            with open(ris_file, "w", encoding="utf-8") as f:
                f.write(ris_text)
            
            print(f"💾 Saved RIS to: {ris_file}")
            print("\n📋 RIS Content Preview:")
            print("-" * 50)
            print(ris_text[:1000])
            print("-" * 50)
            
            # Parse and display key fields
            print("\n🔍 Parsed RIS Fields:")
            for line in ris_text.split('\n'):
                if line.strip():
                    if line.startswith(('TY', 'T1', 'TI', 'AU', 'DO', 'UR', 'L1', 'L2', 'PY')):
                        print(f"  {line}")
            
            return ris_text
        else:
            print("❌ Could not fetch RIS data (may require authentication)")
            
            # Method 2: Try using the export button on the page
            print("🔍 Looking for export button on page...")
            
            # Look for cite/export button
            export_button = await page.query_selector('button[aria-label*="Cite"], button[aria-label*="Export"], a[href*="export"]')
            if export_button:
                print("Found export button, clicking...")
                await export_button.click()
                await page.wait_for_timeout(2000)
                
                # Look for RIS option
                ris_option = await page.query_selector('text=/RIS/i, text=/EndNote/i')
                if ris_option:
                    await ris_option.click()
                    await page.wait_for_timeout(3000)
            
            # Check if we got a download
            print("📄 Current URL:", page.url)
            
            # Save the page HTML for debugging
            html_file = output_dir / f"{pii}.html"
            html_content = await page.content()
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"💾 Saved page HTML to: {html_file}")
        
        await browser.close()
        return None


async def main():
    """Main function to fetch and analyze RIS data."""
    
    # Test with the sleep EEG article
    pii = "S1087079220300964"
    
    print("🚀 Fetching RIS data from ScienceDirect")
    print("=" * 50)
    
    ris_data = await fetch_ris_data(pii)
    
    if ris_data:
        print("\n✅ Successfully fetched and saved RIS data!")
        print("\n📝 RIS Format Explanation:")
        print("  - RIS is a standard format for bibliographic data exchange")
        print("  - Each field starts with a two-character tag (e.g., TY, AU, TI)")
        print("  - The tag is followed by '  - ' and then the value")
        print("  - References end with 'ER  -'")
        print("\n  Key tags for PDF URLs:")
        print("  - L1: Primary document link (usually PDF)")
        print("  - L2: Secondary document link")
        print("  - UR: General URL for the article")
    else:
        print("\n⚠️ Could not fetch RIS data. This usually means:")
        print("  1. The page requires authentication")
        print("  2. The export feature is behind a paywall")
        print("  3. The page structure has changed")


if __name__ == "__main__":
    asyncio.run(main())