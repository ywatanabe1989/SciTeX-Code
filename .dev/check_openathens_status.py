#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:43:00 (ywatanabe)"
# File: ./.dev/check_openathens_status.py
# ----------------------------------------

"""
Check OpenAthens authentication status and test with a specific paper.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar


def check_openathens_status():
    """Check OpenAthens authentication status."""
    
    # Enable OpenAthens
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
    os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"
    
    # Check if email is set
    email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("Please set your institutional email:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'")
        return
    
    print(f"Using email: {email}")
    
    # Initialize Scholar
    print("\nInitializing Scholar...")
    scholar = Scholar()
    
    # Check authentication status
    print("\n🔍 Checking OpenAthens authentication status...")
    
    if scholar.is_openathens_authenticated():
        print("✅ OpenAthens is authenticated!")
        print("   Session is active and ready for downloads")
    else:
        print("❌ OpenAthens is NOT authenticated")
        print("   Would you like to authenticate now? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            print("\n🔐 Starting OpenAthens authentication...")
            print("   A browser window will open for login")
            print("   Please complete the authentication process")
            
            try:
                result = scholar.authenticate_openathens()
                if result:
                    print("✅ Authentication successful!")
                else:
                    print("❌ Authentication failed")
            except Exception as e:
                print(f"❌ Authentication error: {e}")
    
    # Test with a specific Nature Neuroscience paper
    print("\n📥 Testing download of a Nature Neuroscience paper...")
    
    test_doi = "10.1038/s41593-025-01970-x"  # The alcohol paper
    output_dir = Path("./.dev/openathens_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"   DOI: {test_doi}")
        print("   Downloading...")
        
        # Create a more detailed download request
        from scitex.scholar._Paper import Paper
        
        # Create paper object
        paper = Paper(
            title="Suppression of binge alcohol drinking by an inhibitory neuronal ensemble in the mouse medial orbitofrontal cortex",
            doi=test_doi,
            journal="Nature Neuroscience",
            year=2025
        )
        
        # Try download with Scholar
        result = scholar.download_pdfs(
            [test_doi],
            download_dir=output_dir,
            show_progress=True,
            acknowledge_ethical_usage=False  # Using OpenAthens
        )
        
        # Check if downloaded
        pdf_files = list(output_dir.glob("*.pdf"))
        
        if pdf_files:
            size_mb = pdf_files[0].stat().st_size / (1024 * 1024)
            print(f"\n✅ Successfully downloaded: {pdf_files[0].name} ({size_mb:.1f} MB)")
            
            # Check method
            if hasattr(result, 'papers') and result.papers:
                downloaded_paper = result.papers[0]
                if hasattr(downloaded_paper, 'pdf_source'):
                    print(f"   Download method: {downloaded_paper.pdf_source}")
                    
                    if 'openathens' in downloaded_paper.pdf_source.lower():
                        print("\n🎉 OpenAthens is working correctly!")
                    else:
                        print(f"\n⚠️  Paper was downloaded via {downloaded_paper.pdf_source}, not OpenAthens")
        else:
            print("\n❌ Download failed")
            print("   This paper may require OpenAthens authentication")
            
    except Exception as e:
        print(f"\n❌ Error during download: {e}")
        import traceback
        traceback.print_exc()
    
    # Check session details
    print("\n📊 Session Information:")
    try:
        from scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator
        
        config = scholar._config
        auth = OpenAthensAuthenticator(config)
        
        session_dir = Path.home() / ".scitex" / "scholar" / "openathens_sessions"
        if session_dir.exists():
            session_files = list(session_dir.glob("*.json"))
            print(f"   Session directory: {session_dir}")
            print(f"   Session files: {len(session_files)}")
            
            if session_files:
                latest_session = max(session_files, key=lambda p: p.stat().st_mtime)
                print(f"   Latest session: {latest_session.name}")
                print(f"   Modified: {latest_session.stat().st_mtime}")
    except Exception as e:
        print(f"   Could not retrieve session information: {e}")


if __name__ == "__main__":
    check_openathens_status()