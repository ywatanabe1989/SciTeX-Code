#!/usr/bin/env python3
"""
OpenAthens Authentication Only

This script handles OpenAthens authentication and saves the session for later use.
Run this once to authenticate, then use the saved session in your scripts.

Usage:
    python authenticate_only.py

Required environment variable:
    export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@university.edu"
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Enable debug mode to see browser
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

from scitex.scholar import Scholar


def check_session_status():
    """Check and display session file status."""
    session_dir = Path.home() / ".scitex" / "scholar" / "openathens_sessions"
    
    print("\n📁 Session Directory Status:")
    print(f"   Location: {session_dir}")
    
    if not session_dir.exists():
        print("   Status: Directory does not exist (will be created)")
        return
    
    session_files = list(session_dir.glob("*.enc")) + list(session_dir.glob("*.json"))
    if session_files:
        print(f"   Files found: {len(session_files)}")
        for f in session_files:
            mod_time = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"   - {f.name}")
            print(f"     Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Size: {f.stat().st_size} bytes")
    else:
        print("   Status: No session files found")


def main():
    """Authenticate with OpenAthens and save session."""
    
    print("🔐 OpenAthens Authentication Setup")
    print("=" * 60)
    
    # Check email
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("\n❌ Error: Institutional email not set!")
        print("\nPlease run:")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@university.edu'")
        print("\nExample:")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL='john.doe@harvard.edu'")
        return
    
    print(f"\n📧 Email: {email}")
    print(f"🏛️  Institution: {email.split('@')[1]}")
    
    # Check current session status
    check_session_status()
    
    # Initialize Scholar
    print("\n🚀 Initializing Scholar with OpenAthens...")
    try:
        scholar = Scholar(
            openathens_enabled=True,
            openathens_email=email,
            enable_auto_download=False,  # Don't need downloads for auth
            acknowledge_scihub_ethical_usage=False  # Don't need Sci-Hub
        )
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Check if already authenticated
    print("\n🔍 Checking authentication status...")
    try:
        is_auth = scholar.is_openathens_authenticated()
        
        if is_auth:
            print("✅ Already authenticated! Session is valid.")
            print("\n💡 To force re-authentication, use:")
            print("   scholar.authenticate_openathens(force=True)")
            
            # Offer to re-authenticate
            response = input("\nRe-authenticate anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("\n✅ Using existing session. You're ready to download papers!")
                return
            
            print("\n🔄 Force re-authentication...")
            force = True
        else:
            print("❌ Not authenticated.")
            force = False
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        force = False
    
    # Authenticate
    print("\n🌐 Starting OpenAthens Authentication")
    print("-" * 60)
    print("⚠️  IMPORTANT STEPS:")
    print("1. A browser window will open")
    print("2. Your email will be auto-filled (if supported)")
    print("3. Select your institution from the dropdown")
    print("4. Complete login on your institution's page")
    print("5. Complete 2FA if required")
    print("6. Wait for the success message here")
    print("-" * 60)
    
    input("\nPress Enter to open browser for authentication...")
    
    try:
        print("\n⏳ Opening browser...")
        print("📱 Please complete login in the browser window...")
        
        success = scholar.authenticate_openathens(force=force)
        
        if success:
            print("\n✅ SUCCESS! Authentication complete!")
            print("🎉 Your session has been saved")
            
            # Check session again
            check_session_status()
            
            print("\n📝 Next Steps:")
            print("1. Your session is now saved and encrypted")
            print("2. You can close this script")
            print("3. Use Scholar normally - it will use the saved session")
            print("4. Sessions last ~8 hours")
            print("5. Re-run this script when session expires")
            
            print("\n🚀 Example usage:")
            print("```python")
            print("from scitex.scholar import Scholar")
            print("")
            print("scholar = Scholar(openathens_enabled=True)")
            print("papers = scholar.search('quantum computing')")
            print("papers.download_pdfs()  # Will use OpenAthens")
            print("```")
            
        else:
            print("\n❌ Authentication failed!")
            print("\nPossible issues:")
            print("- Login was cancelled")
            print("- 2FA was not completed")
            print("- Session timeout (5 minutes)")
            print("\nPlease try again.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Authentication cancelled by user")
    except Exception as e:
        print(f"\n❌ Authentication error: {e}")
        print("\nPlease check:")
        print("- Internet connection")
        print("- Institution supports OpenAthens")
        print("- Correct email domain")


if __name__ == "__main__":
    main()