#!/usr/bin/env python3
"""
Demo of the integrated ZenRows screenshot functionality with automatic CAPTCHA handling.
This shows how to use the enhanced ZenRowsRemoteBrowserManager.
"""

import os
import asyncio
from scitex.scholar.browser import ZenRowsRemoteBrowserManager, ZenRowsAPIBrowser
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

logger = logging.getLogger(__name__)


async def demo_integrated_browser():
    """Demonstrate the integrated browser with screenshot capabilities."""
    
    print("\n🔧 ZenRows Integrated Browser Demo")
    print("=" * 60)
    
    # Test URLs
    test_cases = [
        {
            "name": "Neuron_Article",
            "url": "https://doi.org/10.1016/j.neuron.2018.01.048",
            "description": "Cell/Neuron article (often has Cloudflare)"
        },
        {
            "name": "Nature_Article",
            "url": "https://doi.org/10.1038/nature12373",
            "description": "Nature article"
        },
        {
            "name": "Science_Article",
            "url": "https://doi.org/10.1126/science.1172133",
            "description": "Science article"
        }
    ]
    
    # Create output directory
    os.makedirs("screenshots_zenrows", exist_ok=True)
    
    # Method 1: Using ZenRowsRemoteBrowserManager (recommended)
    print("\n1️⃣ Using ZenRowsRemoteBrowserManager with API backend")
    print("-" * 60)
    
    # Initialize with optional auth
    auth_manager = None
    try:
        auth_manager = AuthenticationManager()
        if await auth_manager.authenticate():
            logger.success("Authentication available")
    except:
        logger.info("Proceeding without authentication")
    
    # Create browser manager
    browser_manager = ZenRowsRemoteBrowserManager(auth_manager=auth_manager)
    
    for test in test_cases:
        print(f"\n📸 {test['name']}: {test['description']}")
        
        screenshot_path = f"screenshots_zenrows/integrated_{test['name']}.png"
        
        # Take screenshot with automatic CAPTCHA handling
        result = await browser_manager.take_screenshot_reliable(
            url=test['url'],
            output_path=screenshot_path,
            use_api=True,  # Use API mode (recommended)
            wait_ms=5000
        )
        
        if result['success']:
            print(f"   ✅ Success!")
            if result.get('screenshot', {}).get('saved'):
                print(f"   📸 Screenshot: {screenshot_path}")
                if result.get('screenshot', {}).get('width'):
                    print(f"   📐 Size: {result['screenshot']['width']}x{result['screenshot']['height']}")
            if result.get('captcha_solved'):
                print(f"   🔓 CAPTCHA was automatically solved")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    
    # Clean up
    await browser_manager.close()
    
    # Method 2: Direct API browser for batch operations
    print("\n\n2️⃣ Using ZenRowsAPIBrowser for batch screenshots")
    print("-" * 60)
    
    api_browser = ZenRowsAPIBrowser()
    
    # Batch screenshot example
    urls = [test['url'] for test in test_cases]
    results = await api_browser.batch_screenshot(
        urls=urls,
        output_dir="screenshots_zenrows/batch",
        max_concurrent=2  # Process 2 at a time
    )
    
    print(f"\n📊 Batch results:")
    for i, result in enumerate(results):
        name = test_cases[i]['name']
        if result['success']:
            print(f"   ✅ {name}: Screenshot saved")
        else:
            print(f"   ❌ {name}: {result.get('error')}")
    
    # Method 3: Extract data while taking screenshots
    print("\n\n3️⃣ Using navigate_and_extract for data + screenshots")
    print("-" * 60)
    
    test_doi = "10.1016/j.neuron.2018.01.048"
    
    result = await browser_manager.navigate_and_extract(
        url=f"https://doi.org/{test_doi}",
        extract_pdf_url=True,
        take_screenshot=True,
        screenshot_path="screenshots_zenrows/extract_example.png"
    )
    
    if result['success']:
        print(f"✅ Navigation successful")
        if result.get('pdf_url'):
            print(f"📄 PDF URL found: {result['pdf_url'][:80]}...")
        if result.get('screenshot', {}).get('saved'):
            print(f"📸 Screenshot saved: {result['screenshot']['path']}")
        print(f"📊 HTML size: {result.get('html_length', 0):,} bytes")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("\n✅ Demo complete! Check screenshots_zenrows/ for results")
    print("\n💡 Key features demonstrated:")
    print("- Automatic CAPTCHA handling via ZenRows")
    print("- Reliable screenshot capture using API mode")
    print("- Batch processing capabilities")
    print("- Data extraction with screenshots")
    print("- No need to wait for 2Captcha (handled by ZenRows)")


async def demo_api_browser_only():
    """Quick demo using only the API browser."""
    
    print("\n🚀 Quick API Browser Demo")
    print("=" * 40)
    
    browser = ZenRowsAPIBrowser()
    
    result = await browser.navigate_and_screenshot(
        url="https://doi.org/10.1038/nature12373",
        screenshot_path="screenshots_zenrows/quick_demo.png",
        return_html=True
    )
    
    if result['success']:
        print("✅ Screenshot captured successfully")
        print(f"📸 Path: {result['screenshot']['path']}")
        print(f"📐 Size: {result['screenshot']['width']}x{result['screenshot']['height']}")
        print(f"📄 HTML: {result['html_length']:,} bytes")
    else:
        print(f"❌ Failed: {result['error']}")


async def main():
    """Run all demos."""
    
    # Check API key
    if not os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
        print("❌ Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
    
    # Run demos
    await demo_integrated_browser()
    print("\n\n" + "="*60 + "\n")
    await demo_api_browser_only()


if __name__ == "__main__":
    asyncio.run(main())