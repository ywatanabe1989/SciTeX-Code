#!/usr/bin/env python3
"""Debug OpenAthens authentication and PDF download process."""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Enable debug mode
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

from src.scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator
from src.scitex.scholar import Scholar

async def debug_authentication():
    """Debug the authentication process step by step."""
    
    print("OpenAthens Authentication Debugging")
    print("=" * 80)
    print()
    
    # Check environment variables
    print("1. Environment Configuration:")
    print(f"   OPENATHENS_ENABLED: {os.getenv('SCITEX_SCHOLAR_OPENATHENS_ENABLED', 'Not set')}")
    print(f"   OPENATHENS_EMAIL: {os.getenv('SCITEX_SCHOLAR_OPENATHENS_EMAIL', 'Not set')}")
    print(f"   OPENATHENS_USERNAME: {os.getenv('SCITEX_SCHOLAR_OPENATHENS_USERNAME', 'Not set')}")
    print(f"   DEBUG_MODE: {os.getenv('SCITEX_SCHOLAR_DEBUG_MODE', 'Not set')}")
    print()
    
    # Check session cache
    cache_dir = Path.home() / ".scitex" / "scholar" / "openathens_sessions"
    print("2. Session Cache Status:")
    print(f"   Cache directory: {cache_dir}")
    print(f"   Directory exists: {cache_dir.exists()}")
    
    if cache_dir.exists():
        session_files = list(cache_dir.glob("*.enc")) + list(cache_dir.glob("*.json"))
        print(f"   Session files found: {len(session_files)}")
        for f in session_files:
            print(f"     - {f.name} (modified: {datetime.fromtimestamp(f.stat().st_mtime)})")
    print()
    
    # Test authentication
    print("3. Testing OpenAthens Authenticator:")
    try:
        auth = OpenAthensAuthenticator(
            email=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
            debug_mode=True
        )
        
        async with auth:
            # Check if already authenticated
            is_auth = await auth.is_authenticated()
            print(f"   Already authenticated: {is_auth}")
            
            if not is_auth:
                print("\n4. Starting Authentication Process:")
                print("   Browser window will open...")
                print("   Please complete login with 2FA")
                
                # Attempt authentication
                success = await auth.authenticate(force=True)
                print(f"\n   Authentication result: {'SUCCESS' if success else 'FAILED'}")
                
                if success:
                    print("   Session saved successfully")
                    print(f"   Session expires: {auth._session_expiry}")
            else:
                print(f"   Session valid until: {auth._session_expiry}")
                
            # Test download if authenticated
            if await auth.is_authenticated():
                print("\n5. Testing PDF Download:")
                test_url = "https://journals.lww.com/co-neurology/fulltext/2024/04000/ambulatory_seizure_detection.3.aspx"
                test_output = Path("./test_openathens_download.pdf")
                
                print(f"   Test URL: {test_url}")
                print("   Attempting download...")
                
                result = await auth.download_with_auth(test_url, test_output)
                
                if result:
                    print(f"   ✓ Download successful: {result}")
                    print(f"   File size: {result.stat().st_size} bytes")
                else:
                    print("   ✗ Download failed")
                    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_scholar_integration():
    """Test full Scholar integration with OpenAthens."""
    
    print("\n" + "=" * 80)
    print("6. Testing Scholar Integration:")
    
    try:
        # Initialize Scholar
        scholar = Scholar(
            openathens_enabled=True,
            openathens_email=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
            enable_auto_download=False,  # Manual control
            acknowledge_scihub_ethical_usage=False  # No fallback
        )
        
        # Check if OpenAthens is configured
        print(f"   OpenAthens configured: {hasattr(scholar, '_openathens_authenticator')}")
        
        # Search for a paper
        print("\n7. Testing Paper Search and Download:")
        test_doi = "10.1097/WCO.0000000000001260"
        print(f"   Searching for DOI: {test_doi}")
        
        papers = scholar.search(test_doi, limit=1)
        
        if papers:
            paper = papers[0]
            print(f"   Found: {paper.title}")
            print(f"   Journal: {paper.journal}")
            
            # Try to download
            print("\n   Attempting download via OpenAthens...")
            success = paper.download_pdf()
            
            if success:
                print(f"   ✓ Download successful: {paper.pdf_path}")
            else:
                print("   ✗ Download failed")
        else:
            print("   ✗ Paper not found")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all debug tests."""
    await debug_authentication()
    await test_scholar_integration()
    
    print("\n" + "=" * 80)
    print("Debug session complete!")
    print("\nNext steps:")
    print("1. If authentication failed, check browser window for errors")
    print("2. If download failed after auth, check cookie persistence")
    print("3. Run with SCITEX_SCHOLAR_DEBUG_MODE=true for browser visibility")

if __name__ == "__main__":
    asyncio.run(main())