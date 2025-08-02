#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:48:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/.dev/debug_auth_timing.py
# ----------------------------------------
"""
Debug authentication timing to understand when and why the browser closes.
"""

import sys
import os
import asyncio
import time

# Add src to path
sys.path.insert(0, "src")

async def debug_auth_timing():
    """Debug the authentication timing and browser behavior."""
    print("🐛 Debugging Authentication Timing")
    print("=" * 50)
    
    from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
    
    # Get email from environment
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("❌ No email found. Set SCITEX_SCHOLAR_OPENATHENS_EMAIL")
        return False
    
    print(f"📧 Using email: {email}")
    
    try:
        # Create auth manager
        auth_manager = AuthenticationManager(email_openathens=email)
        
        print("🏢 Auth manager created successfully")
        
        # Get the OpenAthens provider directly
        if "openathens" in auth_manager.providers:
            openathens = auth_manager.providers["openathens"]
            
            # Check current status
            print("\n🔍 Checking current authentication status...")
            is_auth = await auth_manager.is_authenticated(verify_live=False)
            print(f"🔐 Currently authenticated: {is_auth}")
            
            if is_auth:
                print("ℹ️  Already authenticated. Forcing re-authentication for debugging...")
                
            print("\n🚀 Starting authentication with debugging...")
            print("⚠️  Watch for when the browser window closes!")
            print("⚠️  Note the exact timing and any error messages")
            
            start_time = time.time()
            print(f"⏰ Start time: {time.strftime('%H:%M:%S')}")
            
            try:
                # Force authentication to see timing
                result = await auth_manager.authenticate(provider_name="openathens", force=True)
                
                end_time = time.time()
                elapsed = end_time - start_time
                print(f"⏰ End time: {time.strftime('%H:%M:%S')}")
                print(f"⏱️  Total elapsed: {elapsed:.2f} seconds")
                
                if result:
                    print("✅ Authentication completed successfully!")
                    print(f"🍪 Got {len(result.get('cookies', []))} cookies")
                else:
                    print("❌ Authentication failed")
                    
            except Exception as e:
                end_time = time.time()
                elapsed = end_time - start_time
                print(f"⏰ Exception at: {time.strftime('%H:%M:%S')}")
                print(f"⏱️  Time before exception: {elapsed:.2f} seconds")
                print(f"❌ Exception during authentication: {e}")
                
                # Print more details about the exception
                import traceback
                traceback.print_exc()
                
        else:
            print("❌ OpenAthens provider not found")
            
    except Exception as e:
        print(f"❌ Error during debug test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

def main():
    """Run the debug timing test."""
    print("🐛 This test will help identify when/why the browser closes")
    print("📋 Instructions:")
    print("   1. Watch the browser window carefully")
    print("   2. Note exactly when it closes")
    print("   3. Try to login as normally as possible")
    print("   4. Report what you observe")
    print()
    
    try:
        success = asyncio.run(debug_auth_timing())
        return success
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# EOF