#!/usr/bin/env python3
"""
Simple ZenRows Stealth Download Example

This shows the simplest way to use ZenRows stealth browser
for downloading paywalled papers with university authentication.

Just set these environment variables:
- SCITEX_SCHOLAR_ZENROWS_API_KEY: Your ZenRows API key
- SCITEX_SCHOLAR_ZENROWS_USE_STEALTH_BROWSER: true (default)
"""

import asyncio
import os

# Enable ZenRows stealth browser
os.environ["SCITEX_SCHOLAR_ZENROWS_USE_STEALTH_BROWSER"] = "true"

from scitex.scholar import Scholar
from scitex import logging

logging.basicConfig(level=logging.INFO)


async def simple_download():
    """Simple example of downloading papers with ZenRows stealth."""
    
    print("Simple ZenRows Stealth Download")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
        print("\n❌ Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        print("   export SCITEX_SCHOLAR_ZENROWS_API_KEY=your_api_key")
        return
    
    print("\n✅ ZenRows API key found")
    print("✅ Stealth browser enabled (anti-bot bypass)")
    
    # Initialize Scholar with ZenRows stealth
    scholar = Scholar(debug_mode=False)  # Set True to see browser
    
    # DOIs to download (these often require institutional access)
    dois = [
        "10.1038/nature12373",  # Nature
        "10.1126/science.1234567",  # Science
        "10.1016/j.cell.2023.08.040",  # Cell
    ]
    
    print(f"\n📥 Downloading {len(dois)} papers...")
    print("\nNote: The browser will use ZenRows proxy automatically")
    print("      for anti-bot protection and clean IP reputation.\n")
    
    # Download papers
    papers = await scholar.download_pdfs_async(
        dois,
        output_dir="./zenrows_downloads",
        show_progress=True,
        organize_by_year=True
    )
    
    # Show results
    print("\nResults:")
    for paper in papers:
        if paper.pdf_path:
            print(f"✅ {paper.doi} → {paper.pdf_path}")
        else:
            print(f"❌ {paper.doi} → Failed to download")
    
    # Summary
    success = sum(1 for p in papers if p.pdf_path)
    print(f"\nSummary: {success}/{len(papers)} downloaded successfully")


def main():
    """Run the example."""
    print("\nZenRows Stealth Browser Benefits:")
    print("✅ Bypasses anti-bot detection automatically")
    print("✅ Uses clean residential IP addresses")
    print("✅ Handles JavaScript-heavy sites")
    print("✅ Works with institutional authentication")
    print("✅ No manual proxy configuration needed\n")
    
    # Show current configuration
    print("Current Configuration:")
    print(f"  ZENROWS_API_KEY: {'✅ Set' if os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY') else '❌ Not set'}")
    print(f"  STEALTH_BROWSER: {os.getenv('SCITEX_SCHOLAR_ZENROWS_USE_STEALTH_BROWSER', 'true')}")
    print(f"  DEBUG_MODE: False (set to True to see browser)\n")
    
    # Option to set debug mode
    debug = input("Show browser window? (y/N): ").strip().lower() == 'y'
    if debug:
        # This would show the browser for manual login if needed
        print("\n🔍 Browser will be visible for debugging/login")
    
    # Run async function
    asyncio.run(simple_download())


if __name__ == "__main__":
    main()

# EOF