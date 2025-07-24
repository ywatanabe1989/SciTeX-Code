#!/usr/bin/env python3
"""
Demonstrate the authentication flow without actual downloads.

This shows how OpenAthens authentication enhances Zotero translators
without requiring actual PDF downloads.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar._PDFDownloader import PDFDownloader
from src.scitex.scholar._ZoteroTranslatorRunner import ZoteroTranslatorRunner


async def demo_auth_enhanced_discovery():
    """Demonstrate how auth enhances discovery."""
    
    print("🔍 Authentication-Enhanced Discovery Demo")
    print("=" * 60)
    
    # Example: Nature paper
    test_doi = "10.1038/s41586-021-03819-2"
    test_url = "https://www.nature.com/articles/s41586-021-03819-2"
    
    print(f"\n📄 Test article:")
    print(f"   DOI: {test_doi}")
    print(f"   URL: {test_url}")
    
    # Initialize components
    downloader = PDFDownloader(
        use_openathens=True,
        use_translators=True,
        use_scihub=False
    )
    
    print("\n" + "-" * 40)
    print("STEP 1: Authentication Check")
    print("-" * 40)
    
    # Check authentication
    auth_session = await downloader._get_authenticated_session()
    
    if auth_session:
        provider = auth_session.get('context', {}).get('provider', 'Unknown')
        cookies = auth_session.get('cookies', [])
        print(f"\n✅ Authenticated via: {provider}")
        print(f"   Cookies available: {len(cookies)}")
        
        # Show some cookie domains (sanitized)
        domains = set()
        for cookie in cookies[:5]:  # First 5 cookies
            domain = cookie.get('domain', 'unknown')
            domains.add(domain)
        print(f"   Cookie domains: {', '.join(domains)}")
    else:
        print("\n❌ No authentication available")
        print("   Zotero will run on PUBLIC page only")
    
    print("\n" + "-" * 40)
    print("STEP 2: Zotero Translator Selection")
    print("-" * 40)
    
    if downloader.zotero_translator_runner:
        translator = downloader.zotero_translator_runner.find_translator_for_url(test_url)
        if translator:
            print(f"\n✅ Found translator: {translator['label']}")
            print(f"   Translator ID: {translator['translatorID']}")
            print(f"   Target: {translator.get('target', 'N/A')}")
        else:
            print("\n❌ No translator found for this URL")
    
    print("\n" + "-" * 40)
    print("STEP 3: Discovery Strategy Order")
    print("-" * 40)
    
    print("\nStrategies that will be tried (in order):")
    strategies = [
        ("Zotero translators", "Uses auth cookies, finds subscriber PDFs"),
        ("Direct patterns", "Tries known PDF URL patterns with auth"),
        ("Playwright", "Scrapes page with auth session"),
        ("Sci-Hub", "Last resort, doesn't use auth")
    ]
    
    for i, (name, description) in enumerate(strategies, 1):
        auth_used = "✅ Uses auth" if name != "Sci-Hub" else "❌ No auth"
        print(f"\n{i}. {name}")
        print(f"   {description}")
        print(f"   {auth_used}")
    
    print("\n" + "-" * 40)
    print("EXPECTED BEHAVIOR")
    print("-" * 40)
    
    if auth_session:
        print("\n✅ With authentication:")
        print("   1. Zotero translator runs on AUTHENTICATED page")
        print("   2. Finds 'Download PDF' button (subscriber only)")
        print("   3. Extracts PDF URL with proper access")
        print("   4. Downloads using authenticated session")
        print("\n   Result: Direct institutional PDF access!")
    else:
        print("\n❌ Without authentication:")
        print("   1. Zotero translator runs on PUBLIC page")
        print("   2. Finds 'Access through institution' button")
        print("   3. No PDF URL available")
        print("   4. Falls back to other methods")
        print("\n   Result: Likely needs Sci-Hub or fails")
    
    print("\n" + "-" * 40)
    print("KEY INSIGHT")
    print("-" * 40)
    
    print("\n🔑 Authentication + Zotero = Reliable PDF Access")
    print("\n   • Authentication provides ACCESS to paywalled content")
    print("   • Zotero knows WHERE PDFs are on 600+ sites")
    print("   • Combined: Find and download PDFs reliably!")
    print("\n   This is why we separate auth (layer) from discovery (engines)")


async def show_enhanced_selectors():
    """Show how authentication enhances PDF discovery."""
    
    print("\n\n🔍 Enhanced PDF Selectors Demo")
    print("=" * 60)
    
    print("\nStandard selectors (work on any page):")
    standard = [
        'a[href*=".pdf"]',
        'a[href*="/pdf/"]',
        'a:has-text("PDF")',
        '.pdf-link'
    ]
    for sel in standard:
        print(f"   • {sel}")
    
    print("\nAuthenticated selectors (only visible to subscribers):")
    auth_only = [
        'a[data-track-action="download pdf"]  # Nature',
        '.c-pdf-download__link                 # Nature',
        '.btn-pdf-download                     # Science',
        '.pdf-download-btn                     # Elsevier',
        'a.pdf-download                        # Wiley',
        'a[data-track-label="download-pdf"]    # Springer'
    ]
    for sel in auth_only:
        print(f"   • {sel}")
    
    print("\n✨ With authentication, we can find these subscriber-only elements!")


async def main():
    """Run the demonstration."""
    await demo_auth_enhanced_discovery()
    await show_enhanced_selectors()
    
    print("\n\n" + "=" * 60)
    print("📚 Summary")
    print("=" * 60)
    print("\nThe fix ensures that:")
    print("1. Authentication is obtained ONCE at the start")
    print("2. Auth session is passed to ALL discovery engines")
    print("3. Zotero translators can access subscriber content")
    print("4. Much higher success rate for institutional users")
    print("\nThis demonstrates the proper separation of concerns:")
    print("- Authentication (OpenAthens, EZProxy, etc.) = ACCESS")
    print("- Discovery (Zotero, patterns, etc.) = KNOWLEDGE")


if __name__ == "__main__":
    asyncio.run(main())