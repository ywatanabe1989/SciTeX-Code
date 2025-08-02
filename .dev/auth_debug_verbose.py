#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:52:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/.dev/auth_debug_verbose.py
# ----------------------------------------
"""
Verbose authentication debugging to track URL changes and success detection.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, "src")

async def verbose_auth_debug():
    """Run authentication with verbose URL tracking."""
    print("🔍 Verbose Authentication Debug")
    print("=" * 50)
    
    from scitex.scholar.auth._OpenAthensAuthenticator import OpenAthensAuthenticator
    from scitex.scholar.config import ScholarConfig
    
    # Get email from environment
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("❌ No email found. Set SCITEX_SCHOLAR_OPENATHENS_EMAIL")
        return False
    
    print(f"📧 Using email: {email}")
    
    # Create config and authenticator
    config = ScholarConfig()
    authenticator = OpenAthensAuthenticator(email=email, config=config, debug_mode=True)
    
    print(f"🎯 Success indicators: {authenticator.SUCCESS_INDICATORS}")
    print(f"⏰ Timeout: {authenticator.timeout} seconds")
    
    try:
        print("\n🚀 Starting authentication with URL tracking...")
        
        # Patch the wait_for_login_completion method to be more verbose
        original_wait_method = authenticator.browser_authenticator.wait_for_login_completion_async
        
        async def verbose_wait_for_login(page, success_indicators):
            """Verbose version of wait_for_login_completion_async."""
            max_wait_time = authenticator.timeout
            check_interval = 2
            elapsed_time = 0
            seen_sso_page = False
            last_url = ""

            print(f"\n⏱️  Starting to wait for login completion (max {max_wait_time}s)")
            
            while elapsed_time < max_wait_time:
                try:
                    current_url = page.url
                    
                    # Only print URL changes to reduce noise
                    if current_url != last_url:
                        print(f"🌐 URL changed to: {current_url}")
                        last_url = current_url
                    
                    # Track SSO navigation
                    if authenticator.browser_authenticator._is_sso_page(current_url):
                        if not seen_sso_page:
                            print(f"🔐 SSO/login page detected: {current_url}")
                        seen_sso_page = True

                    # Check for success
                    if authenticator.browser_authenticator._check_success_indicators(current_url, success_indicators):
                        print(f"✅ Success indicator found in URL: {current_url}")
                        
                        if await authenticator.browser_authenticator._verify_login_success(page, seen_sso_page, elapsed_time):
                            print(f"🎉 Login verified successfully!")
                            return True

                    # Show progress every 10 seconds
                    if elapsed_time % 10 == 0 and elapsed_time > 0:
                        print(f"⏳ Still waiting... ({elapsed_time}s elapsed, URL: {current_url})")

                    await asyncio.sleep(check_interval)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    print(f"❌ Error during wait loop: {e}")
                    break

            print(f"⏰ Timeout reached after {elapsed_time}s")
            return False
        
        # Replace the method temporarily
        authenticator.browser_authenticator.wait_for_login_completion_async = verbose_wait_for_login
        
        # Run authentication
        result = await authenticator.authenticate(force=True)
        
        if result:
            print("✅ Authentication completed successfully!")
            print(f"🍪 Got {len(result.get('cookies', []))} cookies")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

def main():
    """Run the verbose debug."""
    print("🔍 This will show detailed URL tracking during authentication")
    print("📋 Watch for:")
    print("   - URL changes as you navigate")
    print("   - When success indicators are detected")
    print("   - Any errors or unexpected behavior")
    print()
    
    try:
        success = asyncio.run(verbose_auth_debug())
        return success
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# EOF