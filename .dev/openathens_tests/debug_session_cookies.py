#!/usr/bin/env python3
"""
Debug script to check if cookies are properly saved and loaded.
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar._Scholar import Scholar
from src.scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator


async def check_authenticator_cookies():
    """Check if the authenticator has cookies stored."""
    
    print("🔍 Checking OpenAthens Cookie Storage")
    print("=" * 60)
    
    # Create authenticator
    auth = OpenAthensAuthenticator(
        email="Yusuke.Watanabe@unimelb.edu.au"
    )
    
    # Load session cache
    await auth._load_session_cache()
    
    print("\n1️⃣ Checking authentication status:")
    is_auth = await auth.is_authenticated()
    print(f"   Is authenticated: {is_auth}")
    
    print("\n2️⃣ Checking cookie storage:")
    
    # Check _cookies (simple dict)
    if hasattr(auth, '_cookies') and auth._cookies:
        print(f"   Simple cookies (_cookies): {len(auth._cookies)} cookies")
        for name in list(auth._cookies.keys())[:3]:
            print(f"     - {name}")
    else:
        print("   Simple cookies (_cookies): None or empty")
    
    # Check _full_cookies (list of dicts)
    if hasattr(auth, '_full_cookies') and auth._full_cookies:
        print(f"   Full cookies (_full_cookies): {len(auth._full_cookies)} cookies")
        domains = set()
        for cookie in auth._full_cookies:
            domains.add(cookie.get('domain', 'unknown'))
        print(f"     - Domains: {', '.join(domains)}")
    else:
        print("   Full cookies (_full_cookies): None or empty")
    
    # Check session cache file
    cache_file = auth.cache_dir / "openathens_session.json.enc"
    if cache_file.exists():
        print(f"\n3️⃣ Session cache file exists: {cache_file}")
        print(f"   Size: {cache_file.stat().st_size} bytes")
    else:
        print(f"\n3️⃣ Session cache file NOT found: {cache_file}")
    
    return auth


async def test_session_retrieval():
    """Test if PDFDownloader can retrieve the session."""
    
    print("\n\n🔍 Testing Session Retrieval in PDFDownloader")
    print("=" * 60)
    
    scholar = Scholar(openathens_enabled=True)
    downloader = scholar._pdf_downloader
    
    # Get authenticated session
    auth_session = await downloader._get_authenticated_session()
    
    if auth_session:
        print("\n✅ Session retrieved successfully!")
        print(f"   Provider: {auth_session.get('context', {}).get('provider')}")
        print(f"   Cookies: {len(auth_session.get('cookies', []))} cookies")
        
        # Show cookie details
        cookies = auth_session.get('cookies', [])
        if cookies:
            print("\n   Cookie details:")
            for cookie in cookies[:3]:  # First 3
                print(f"     - {cookie.get('name')}: domain={cookie.get('domain')}")
    else:
        print("\n❌ No session retrieved!")
        print("   This explains why downloads are failing.")


async def test_cookie_propagation():
    """Test if cookies are passed to download methods."""
    
    print("\n\n🔍 Testing Cookie Propagation")
    print("=" * 60)
    
    # Test URL
    test_url = "https://www.nature.com/articles/s41586-021-03819-2"
    
    scholar = Scholar(openathens_enabled=True)
    downloader = scholar._pdf_downloader
    
    # Manually get session
    auth_session = await downloader._get_authenticated_session()
    
    if auth_session:
        print(f"\n✅ Have auth session with {len(auth_session.get('cookies', []))} cookies")
        
        # Check if cookies would be used
        print("\n   Would be passed to:")
        if downloader.use_translators:
            print("     ✓ Zotero translators")
        if downloader.use_playwright:
            print("     ✓ Playwright scraping")
        print("     ✓ Direct pattern downloads")
        
        # Show what domains cookies are for
        domains = set()
        for cookie in auth_session.get('cookies', []):
            domain = cookie.get('domain', '')
            if domain:
                domains.add(domain)
        
        print(f"\n   Cookie domains: {', '.join(sorted(domains))}")
        print("\n   ⚠️  Note: Publisher sites may need proxy URLs or specific cookie domains")
    else:
        print("\n❌ No auth session available")


async def main():
    """Run all checks."""
    
    print("OpenAthens Session Debugging")
    print("=" * 60)
    print("\nThis script checks if cookies are properly stored and retrieved.\n")
    
    # Check authenticator
    auth = await check_authenticator_cookies()
    
    # Test retrieval
    await test_session_retrieval()
    
    # Test propagation
    await test_cookie_propagation()
    
    print("\n\n📊 Summary")
    print("=" * 60)
    print("\nIf cookies are stored but downloads still fail, possible issues:")
    print("1. Cookies are for .openathens.net, not publisher domains")
    print("2. Need to use proxy URLs (e.g., through EZProxy)")
    print("3. Publishers require different authentication flow")
    print("4. Cookies expire quickly or are invalidated")


if __name__ == "__main__":
    asyncio.run(main())