#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:50:00 (ywatanabe)"
# File: ./.dev/debug_openathens_issue.py
# ----------------------------------------

"""
Debug OpenAthens authentication issue.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar
from scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator
from scitex.scholar._PDFDownloader import PDFDownloader


async def debug_openathens():
    """Debug OpenAthens authentication issue."""
    
    # Enable OpenAthens
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
    os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "false"
    
    print("🔍 Debugging OpenAthens authentication issue...")
    print("="*60)
    
    # Initialize Scholar
    scholar = Scholar()
    
    # Check 1: Is OpenAthens configured?
    print("\n1. OpenAthens Configuration:")
    print(f"   - Enabled: {scholar._config.use_openathens}")
    print(f"   - Organization ID: {scholar._config.openathens_org_id}")
    print(f"   - Username: {scholar._config.openathens_username}")
    print(f"   - Email: {scholar._config.openathens_email}")
    
    # Check 2: Is authenticated?
    is_auth = scholar.is_openathens_authenticated()
    print(f"\n2. Authentication Status: {'✅ Authenticated' if is_auth else '❌ Not authenticated'}")
    
    # Check 3: Session details
    if hasattr(scholar, '_pdf_downloader') and scholar._pdf_downloader:
        downloader = scholar._pdf_downloader
        print(f"\n3. PDF Downloader Settings:")
        print(f"   - use_openathens: {downloader.use_openathens}")
        print(f"   - openathens_authenticator: {downloader.openathens_authenticator is not None}")
        
        if downloader.openathens_authenticator:
            auth = downloader.openathens_authenticator
            print(f"\n4. OpenAthens Authenticator:")
            print(f"   - Is authenticated: {await auth.is_authenticated_async()}")
            print(f"   - Has cookies: {auth._cookies is not None and len(auth._cookies) > 0}")
            print(f"   - Has full cookies: {auth._full_cookies is not None and len(auth._full_cookies) > 0}")
            
            # Check session
            session = await auth.get_session_async()
            if session:
                print(f"\n5. Session Details:")
                print(f"   - Provider: {session.get('context', {}).get('provider', 'Unknown')}")
                print(f"   - Cookies count: {len(session.get('cookies', []))}")
                print(f"   - Full cookies count: {len(session.get('full_cookies', []))}")
            else:
                print("\n5. No session found")
    
    # Test with a Nature paper
    print("\n" + "="*60)
    print("Testing with Nature Neuroscience paper...")
    
    test_doi = "10.1038/s41593-025-01970-x"
    output_dir = Path("./.dev/openathens_debug")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Manually check the download flow
    if scholar._pdf_downloader:
        downloader = scholar._pdf_downloader
        
        # Get the resolved URL
        from scitex.scholar._DOIResolver import DOIResolver
        resolver = DOIResolver()
        url = await resolver.resolve_async(test_doi)
        print(f"\nResolved URL: {url}")
        
        # Check authenticated session
        auth_session = await downloader._get_authenticated_session_async()
        if auth_session:
            print(f"\nAuthenticated session found:")
            print(f"   - Provider: {auth_session.get('context', {}).get('provider', 'Unknown')}")
            print(f"   - Has cookies: {'cookies' in auth_session}")
        else:
            print("\nNo authenticated session")
        
        # Check which strategies will be used
        if auth_session and downloader.use_openathens and downloader.openathens_authenticator:
            print("\nWill use OpenAthens strategy order")
        else:
            print("\nWill use non-authenticated strategy order")
        
        # Test OpenAthens strategy directly
        if downloader.openathens_authenticator and await downloader.openathens_authenticator.is_authenticated_async():
            print("\n📥 Testing OpenAthens strategy directly...")
            try:
                output_path = output_dir / f"{test_doi.replace('/', '_')}.pdf"
                result = await downloader._try_openathens_async(
                    test_doi, 
                    url, 
                    output_path, 
                    auth_session
                )
                if result:
                    print(f"✅ OpenAthens download succeeded: {result}")
                else:
                    print("❌ OpenAthens download failed")
            except Exception as e:
                print(f"❌ OpenAthens error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_openathens())