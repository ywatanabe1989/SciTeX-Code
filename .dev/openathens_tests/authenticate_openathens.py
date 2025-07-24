#!/usr/bin/env python3
"""Authenticate with OpenAthens and save session for future use."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Enable debug mode to see the browser
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

from src.scitex.scholar import Scholar

def authenticate_openathens():
    """One-time OpenAthens authentication with 2FA."""
    
    print("OpenAthens Authentication Setup")
    print("=" * 60)
    print("This will open a browser window for manual authentication")
    print("You'll need to:")
    print("1. Enter your institutional email")
    print("2. Select your institution") 
    print("3. Complete login with 2FA")
    print("4. The session will be saved for future use")
    print("=" * 60)
    print()
    
    # Initialize Scholar
    scholar = Scholar(
        openathens_enabled=True,
        openathens_email=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
        enable_auto_download=False,
        acknowledge_scihub_ethical_usage=False
    )
    
    try:
        # This will open browser for manual authentication
        print("Opening browser for authentication...")
        success = scholar.authenticate_openathens(force=True)
        
        if success:
            print("\n✓ SUCCESS! OpenAthens session saved")
            print("You can now use OpenAthens for PDF downloads")
            print("The session will remain active for several hours")
            print("\nTo test downloads, run your original script again")
        else:
            print("\n✗ Authentication failed or was cancelled")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    authenticate_openathens()