#!/usr/bin/env python3
"""
Debug why browser is closing after selecting University of Melbourne.

This will show exactly what URLs are being checked and when.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator
import logging

# Enable debug logging to see everything
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def test_authentication_with_manual_monitoring():
    """Test authentication with manual URL monitoring."""
    
    print("🔍 Browser Closing Debug Test")
    print("=" * 60)
    print("\nThis test will help identify why the browser closes prematurely.")
    print("\nWhat SHOULD happen:")
    print("1. Browser opens at my.openathens.net")
    print("2. You type your email")
    print("3. You click 'University of Melbourne'")
    print("4. Browser goes to sso.unimelb.edu.au - SHOULD STAY OPEN")
    print("5. You complete login (username, password, 2FA)")
    print("6. Browser redirects back to OpenAthens")
    print("7. ONLY THEN should browser close")
    
    print("\n⚠️  Changes made:")
    print("• Removed problematic URL check that fired too early")
    print("• Disabled auto-fill to prevent issues")
    print("• Added requirement to see SSO page before success")
    print("• Added better debugging output")
    
    print("\n" + "=" * 60)
    
    # Create authenticator WITHOUT email to ensure no auto-fill
    auth = OpenAthensAuthenticator(
        email=None,  # No email = no auto-fill
        debug_mode=True
    )
    
    print("\n🌐 Starting authentication...")
    print("Please watch the console output to see what URLs are detected.\n")
    
    try:
        success = await auth.authenticate(force=True)
        
        if success:
            print("\n✅ Authentication completed successfully!")
            print("The browser stayed open through the entire process.")
        else:
            print("\n❌ Authentication failed or timed out")
            
    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("BROWSER CLOSING DEBUG TEST")
    print("=" * 60)
    print("\nThis test has fixes for:")
    print("• Premature browser closing")
    print("• Auto-fill issues")
    print("• Better success detection")
    print("\nStarting in 3 seconds...\n")
    
    import time
    time.sleep(3)
    
    asyncio.run(test_authentication_with_manual_monitoring())