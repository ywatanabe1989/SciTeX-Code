#!/usr/bin/env python3
"""
Debug script to check OpenAthens authentication session handling.

This helps identify why authenticated downloads might be failing.
"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar._Scholar import Scholar
from src.scitex.scholar._PDFDownloader import PDFDownloader


async def check_auth_session():
    """Check if authentication session is properly stored and retrieved."""
    
    print("🔍 Checking OpenAthens Session")
    print("=" * 60)
    
    # Create scholar instance
    scholar = Scholar(openathens_enabled=True)
    
    # Check if authenticated
    is_auth = await scholar.is_authenticated_async()
    print(f"\n1️⃣ Is authenticated: {is_auth}")
    
    if is_auth:
        # Check the downloader's auth session
        downloader = scholar._pdf_downloader
        
        # Get authenticated session
        auth_session = await downloader._get_authenticated_session()
        
        if auth_session:
            print("\n2️⃣ Authentication session found!")
            
            # Check cookies
            cookies = auth_session.get('cookies', [])
            print(f"   • Number of cookies: {len(cookies)}")
            
            # Show cookie domains (sanitized)
            domains = set()
            for cookie in cookies:
                domain = cookie.get('domain', 'unknown')
                domains.add(domain)
            
            print(f"   • Cookie domains: {', '.join(sorted(domains))}")
            
            # Check for important cookies
            important_cookies = []
            for cookie in cookies:
                name = cookie.get('name', '').lower()
                if any(key in name for key in ['auth', 'session', 'token', 'openathens', 'ezproxy']):
                    important_cookies.append(cookie['name'])
            
            if important_cookies:
                print(f"   • Important cookies: {', '.join(important_cookies[:5])}")
            
            # Check provider
            provider = auth_session.get('context', {}).get('provider', 'Unknown')
            print(f"   • Provider: {provider}")
            
            print("\n3️⃣ Testing cookie propagation:")
            
            # Test if cookies would be passed to methods
            if hasattr(downloader, '_try_zotero_translator'):
                print("   ✅ Zotero translator method exists")
            if hasattr(downloader, '_download_file_with_auth'):
                print("   ✅ Auth download helper exists")
            if hasattr(downloader, '_run_translator_with_auth'):
                print("   ✅ Translator auth helper exists")
            
            return True
        else:
            print("\n❌ No authentication session found!")
            print("   This explains why downloads are failing.")
            return False
    else:
        print("\n❌ Not authenticated")
        return False


async def test_single_download():
    """Test downloading a single paper with debug info."""
    
    print("\n\n🧪 Testing Single Download")
    print("=" * 60)
    
    # Test with a Nature paper (usually has good Zotero translator)
    test_doi = "10.1038/s41586-021-03819-2"
    print(f"\nTest DOI: {test_doi}")
    print("Expected: Should use Zotero translator with auth cookies")
    
    scholar = Scholar(openathens_enabled=True)
    
    # Enable debug logging
    import logging
    logging.getLogger('scitex.scholar').setLevel(logging.DEBUG)
    
    print("\nStarting download with debug logging...")
    
    # Download single paper
    result = await scholar.download_pdfs_async(
        [test_doi],
        download_dir="./test_downloads",
        show_progress=True
    )
    
    print(f"\nResult: {result['successful']}/{result['successful'] + result['failed']} successful")
    
    if result['results']:
        paper_result = result['results'][0]
        print(f"Method used: {paper_result.get('method', 'Unknown')}")
        if not paper_result['success']:
            print(f"Error: {paper_result.get('error', 'Unknown error')}")


async def main():
    """Run all checks."""
    
    print("OpenAthens Session Debugging")
    print("=" * 60)
    print("\nThis script checks if the authenticated session is properly")
    print("stored and passed to download methods.\n")
    
    # Check session
    has_session = await check_auth_session()
    
    if has_session:
        # Test download
        await test_single_download()
    else:
        print("\n⚠️  No session found. Please authenticate first:")
        print("   scholar = Scholar(openathens_enabled=True)")
        print("   scholar.authenticate_openathens()")


if __name__ == "__main__":
    asyncio.run(main())