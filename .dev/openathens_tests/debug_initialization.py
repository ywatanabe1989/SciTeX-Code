#!/usr/bin/env python3
"""Debug OpenAthens initialization issues."""

import os
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Enable all debug output
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

import logging
logging.basicConfig(level=logging.DEBUG)

from src.scitex.scholar import Scholar
from src.scitex.scholar._Config import ScholarConfig


def debug_initialization():
    """Debug the initialization process step by step."""
    
    print("🔍 OpenAthens Initialization Debug")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n1. Environment Variables:")
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    enabled = os.getenv("SCITEX_SCHOLAR_OPENATHENS_ENABLED")
    debug = os.getenv("SCITEX_SCHOLAR_DEBUG_MODE")
    
    print(f"   OPENATHENS_EMAIL: {email or 'Not set'}")
    print(f"   OPENATHENS_ENABLED: {enabled or 'Not set'}")
    print(f"   DEBUG_MODE: {debug or 'Not set'}")
    
    if not email:
        print("\n❌ Email not set. Setting it now...")
        email = "test@university.edu"  # Replace with your email
        os.environ["SCITEX_SCHOLAR_OPENATHENS_EMAIL"] = email
        print(f"   Set to: {email}")
    
    # Step 2: Create config
    print("\n2. Creating ScholarConfig:")
    try:
        config = ScholarConfig(
            openathens_enabled=True,
            openathens_email=email,
            debug_mode=True
        )
        print("   ✅ Config created successfully")
        print(f"   - openathens_enabled: {config.openathens_enabled}")
        print(f"   - openathens_email: {config.openathens_email}")
        print(f"   - debug_mode: {config.debug_mode}")
    except Exception as e:
        print(f"   ❌ Config creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Initialize Scholar
    print("\n3. Initializing Scholar:")
    try:
        scholar = Scholar(config=config)
        print("   ✅ Scholar initialized successfully")
    except Exception as e:
        print(f"   ❌ Scholar initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Check PDF downloader
    print("\n4. Checking PDF Downloader:")
    try:
        pdf_downloader = scholar._pdf_downloader
        print(f"   ✅ PDF downloader exists: {pdf_downloader}")
        print(f"   - use_openathens: {pdf_downloader.use_openathens}")
        
        if hasattr(pdf_downloader, 'openathens_authenticator'):
            auth = pdf_downloader.openathens_authenticator
            print(f"   - openathens_authenticator: {auth}")
            if auth:
                print(f"     - email: {auth.email}")
                print(f"     - debug_mode: {auth.debug_mode}")
        else:
            print("   - No openathens_authenticator attribute")
            
    except Exception as e:
        print(f"   ❌ PDF downloader check failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Test authentication check
    print("\n5. Testing authentication check:")
    try:
        is_auth = scholar.is_openathens_authenticated()
        print(f"   ✅ Check succeeded: {is_auth}")
    except Exception as e:
        print(f"   ❌ Authentication check failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 6: Test download initialization
    print("\n6. Testing download function:")
    try:
        # Don't actually download, just test the setup
        test_doi = "10.1038/s41586-019-1666-5"
        papers = scholar.search(test_doi, limit=1)
        
        if papers:
            print(f"   ✅ Found paper: {papers[0].title[:50]}...")
            
            # Check if download would work
            paper = papers[0]
            print(f"   - Has download_pdf method: {hasattr(paper, 'download_pdf')}")
            
    except Exception as e:
        print(f"   ❌ Search/download test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_initialization()