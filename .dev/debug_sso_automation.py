#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Debug SSO automation with Puppeteer MCP

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scitex.scholar.auth._OpenAthensAuthenticator import OpenAthensAuthenticator


async def debug_sso_with_puppeteer():
    """Debug SSO automation step by step using Puppeteer MCP."""
    print("=" * 60)
    print("SSO Automation Debug with Puppeteer")
    print("=" * 60)
    
    # Check environment variables
    print("Environment Variables:")
    unimelb_username = os.environ.get("UNIMELB_SSO_USERNAME")
    unimelb_password = os.environ.get("UNIMELB_SSO_PASSWORD")
    openathens_email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    
    print(f"UNIMELB_SSO_USERNAME: {unimelb_username}")
    print(f"UNIMELB_SSO_PASSWORD: {'Set' if unimelb_password else 'Not set'}")
    print(f"SCITEX_SCHOLAR_OPENATHENS_EMAIL: {openathens_email}")
    
    if not unimelb_username or not unimelb_password:
        print("❌ UniMelb credentials not configured properly")
        return False
    
    print(f"\n🚀 Starting OpenAthens authentication debug...")
    print("This will:")
    print("1. Navigate to OpenAthens login page")
    print("2. Attempt SSO automation")
    print("3. Take screenshots at each step")
    print("4. Report actual authentication status")
    
    try:
        # Create authenticator
        auth = OpenAthensAuthenticator(
            email=openathens_email,
            timeout=300,  # 5 minutes timeout
            debug_mode=True
        )
        
        print(f"\n📧 Email notifications will be sent to:")
        print(f"- UniMelb: {os.environ.get('UNIMELB_EMAIL', 'Not set')}")
        print(f"- Fallback: {os.environ.get('SCITEX_EMAIL_YWATANABE', 'Not set')}")
        
        # Try authentication
        print(f"\n🔐 Attempting authentication...")
        result = await auth.authenticate(force=True)
        
        print(f"\n📊 Authentication Result:")
        print(f"Success: {bool(result)}")
        print(f"Cookies: {len(result.get('cookies', []))} cookies received")
        
        # Verify authentication status
        is_authenticated = await auth.is_authenticated(verify_live=True)
        print(f"Live verification: {is_authenticated}")
        
        # Get session info
        session_info = await auth.get_session_info()
        print(f"\n📋 Session Info:")
        for key, value in session_info.items():
            print(f"  {key}: {value}")
        
        return is_authenticated
        
    except Exception as e:
        print(f"❌ Authentication failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def debug_with_puppeteer_mcp():
    """Use Puppeteer MCP to manually debug the authentication flow."""
    print("\n" + "=" * 60)
    print("Manual Puppeteer Debug")
    print("=" * 60)
    
    try:
        # Import MCP Puppeteer functions
        from mcp_puppeteer import (
            puppeteer_navigate,
            puppeteer_screenshot,
            puppeteer_evaluate,
            puppeteer_fill,
            puppeteer_click
        )
        
        # Navigate to OpenAthens
        print("🌐 Navigating to OpenAthens...")
        nav_result = await puppeteer_navigate("https://my.openathens.net/?passiveLogin=false")
        print(f"Navigation result: {nav_result}")
        
        # Take initial screenshot
        print("📸 Taking initial screenshot...")
        await puppeteer_screenshot("openathens_initial", width=1280, height=720)
        
        # Check page content
        print("🔍 Analyzing page content...")
        page_info = await puppeteer_evaluate("""
            () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    hasEmailInput: !!document.querySelector('input[type="email"], input[name*="email"], #type-ahead'),
                    hasPasswordInput: !!document.querySelector('input[type="password"]'),
                    hasInstitutionSearch: !!document.querySelector('#type-ahead'),
                    visibleText: document.body.innerText.substring(0, 500)
                };
            }
        """)
        
        print(f"Page Analysis:")
        for key, value in page_info.items():
            print(f"  {key}: {value}")
        
        # If we're on the institution search page, try to enter UniMelb email
        if page_info.get('hasInstitutionSearch'):
            print("\n🏫 Found institution search - entering UniMelb email...")
            
            unimelb_email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
            if unimelb_email:
                # Fill institution search
                await puppeteer_fill("#type-ahead", unimelb_email)
                await puppeteer_screenshot("after_email_entry", width=1280, height=720)
                
                # Wait for dropdown and try to find UniMelb
                await asyncio.sleep(2)
                
                dropdown_info = await puppeteer_evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('*'));
                        const unimelb_elements = elements.filter(el => 
                            el.textContent && el.textContent.includes('University of Melbourne')
                        );
                        return {
                            found_unimelb: unimelb_elements.length > 0,
                            dropdown_visible: document.querySelectorAll('.dropdown, .autocomplete, .suggestions').length > 0,
                            all_text: document.body.innerText.substring(0, 1000)
                        };
                    }
                """)
                
                print(f"Dropdown Analysis:")
                for key, value in dropdown_info.items():
                    print(f"  {key}: {value}")
                
                # Try to click UniMelb if found
                if dropdown_info.get('found_unimelb'):
                    print("✅ Found University of Melbourne in dropdown")
                    
                    click_result = await puppeteer_evaluate("""
                        () => {
                            const elements = Array.from(document.querySelectorAll('*'));
                            for (let element of elements) {
                                if (element.textContent && element.textContent.includes('University of Melbourne')) {
                                    element.click();
                                    return 'Clicked University of Melbourne';
                                }
                            }
                            return 'University of Melbourne not found for clicking';
                        }
                    """)
                    
                    print(f"Click result: {click_result}")
                    await puppeteer_screenshot("after_unimelb_click", width=1280, height=720)
                    
                    # Wait for redirect to UniMelb SSO
                    await asyncio.sleep(3)
                    
                    # Check if we're now on UniMelb SSO page
                    sso_info = await puppeteer_evaluate("""
                        () => {
                            return {
                                title: document.title,
                                url: window.location.href,
                                isUniMelbSSO: window.location.href.includes('unimelb') || 
                                              window.location.href.includes('okta') ||
                                              document.title.includes('University of Melbourne'),
                                hasUsernameField: !!document.querySelector('input[name="identifier"]'),
                                hasPasswordField: !!document.querySelector('input[name="credentials.passcode"]'),
                                pageText: document.body.innerText.substring(0, 500)
                            };
                        }
                    """)
                    
                    print(f"\nSSO Page Analysis:")
                    for key, value in sso_info.items():
                        print(f"  {key}: {value}")
                    
                    await puppeteer_screenshot("sso_page", width=1280, height=720)
                    
                    # If we're on UniMelb SSO, try to fill credentials
                    if sso_info.get('isUniMelbSSO'):
                        print("\n🔐 On UniMelb SSO page - attempting login...")
                        
                        username = os.environ.get("UNIMELB_SSO_USERNAME")
                        password = os.environ.get("UNIMELB_SSO_PASSWORD")
                        
                        if username and sso_info.get('hasUsernameField'):
                            print(f"📝 Filling username: {username}")
                            await puppeteer_fill('input[name="identifier"]', username)
                            await puppeteer_screenshot("after_username", width=1280, height=720)
                            
                            # Click Next button
                            next_clicked = await puppeteer_evaluate("""
                                () => {
                                    const nextBtn = document.querySelector('input[value="Next"], button:contains("Next")');
                                    if (nextBtn) {
                                        nextBtn.click();
                                        return 'Next button clicked';
                                    }
                                    return 'Next button not found';
                                }
                            """)
                            print(f"Next button: {next_clicked}")
                            
                            await asyncio.sleep(2)
                            await puppeteer_screenshot("after_next_click", width=1280, height=720)
                            
                            # Check for password field
                            password_check = await puppeteer_evaluate("""
                                () => {
                                    return {
                                        hasPasswordField: !!document.querySelector('input[name="credentials.passcode"]'),
                                        currentUrl: window.location.href,
                                        pageTitle: document.title
                                    };
                                }
                            """)
                            
                            print(f"Password page check: {password_check}")
                            
                            if password and password_check.get('hasPasswordField'):
                                print("🔒 Filling password...")
                                await puppeteer_fill('input[name="credentials.passcode"]', password)
                                await puppeteer_screenshot("after_password", width=1280, height=720)
                                
                                # Click Verify button
                                verify_clicked = await puppeteer_evaluate("""
                                    () => {
                                        const verifyBtn = document.querySelector('input[value="Verify"], button:contains("Verify")');
                                        if (verifyBtn) {
                                            verifyBtn.click();
                                            return 'Verify button clicked';
                                        }
                                        return 'Verify button not found';
                                    }
                                """)
                                print(f"Verify button: {verify_clicked}")
                                
                                await asyncio.sleep(3)
                                await puppeteer_screenshot("after_verify_click", width=1280, height=720)
                                
                                # Check for 2FA
                                duo_check = await puppeteer_evaluate("""
                                    () => {
                                        return {
                                            currentUrl: window.location.href,
                                            pageTitle: document.title,
                                            hasDuoFrame: !!document.querySelector('#duo_iframe, iframe[src*="duosecurity"]'),
                                            has2FAElements: !!document.querySelector('.authenticator-verify-list, .duo-frame'),
                                            pageText: document.body.innerText.substring(0, 800)
                                        };
                                    }
                                """)
                                
                                print(f"\n🔐 2FA Check:")
                                for key, value in duo_check.items():
                                    print(f"  {key}: {value}")
                                
                                await puppeteer_screenshot("duo_page", width=1280, height=720)
                                
                                # If Duo/2FA is present, try to trigger push notification
                                if duo_check.get('has2FAElements') or 'duo' in duo_check.get('pageText', '').lower():
                                    print("📱 Found 2FA page - looking for push notification...")
                                    
                                    push_result = await puppeteer_evaluate("""
                                        () => {
                                            // Look for push notification button/link
                                            const pushElements = Array.from(document.querySelectorAll('*')).filter(el =>
                                                el.textContent && (
                                                    el.textContent.includes('push notification') ||
                                                    el.textContent.includes('Push') ||
                                                    el.textContent.includes('Send Push') ||
                                                    el.textContent.includes('Duo Push')
                                                )
                                            );
                                            
                                            if (pushElements.length > 0) {
                                                pushElements[0].click();
                                                return 'Push notification requested';
                                            }
                                            
                                            // Try clicking any button that might be push
                                            const buttons = document.querySelectorAll('button, a.button, input[type="button"]');
                                            for (let btn of buttons) {
                                                if (btn.textContent && btn.textContent.toLowerCase().includes('push')) {
                                                    btn.click();
                                                    return 'Found and clicked push button';
                                                }
                                            }
                                            
                                            return 'No push notification option found';
                                        }
                                    """)
                                    
                                    print(f"Push notification result: {push_result}")
                                    await puppeteer_screenshot("after_push_request", width=1280, height=720)
                                    
                                    print("\n📱 Push notification should now be sent to your device!")
                                    print("Check your mobile device for the Duo/Okta verification prompt")
                                    
                                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Puppeteer debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run SSO debugging with both methods."""
    print("🔍 SSO Authentication Debug Session")
    print("=" * 60)
    
    # Method 1: Test our current SSO automation
    print("Method 1: Testing current SSO automation...")
    automation_success = await debug_sso_with_puppeteer()
    
    # Method 2: Manual step-by-step with Puppeteer MCP  
    print("\nMethod 2: Manual debugging with Puppeteer MCP...")
    manual_success = await debug_with_puppeteer_mcp()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print(f"SSO Automation Success: {'✅' if automation_success else '❌'}")
    print(f"Manual Debug Success: {'✅' if manual_success else '❌'}")
    
    if not automation_success:
        print("\n🔧 Issues found with SSO automation:")
        print("1. Authentication may be reporting success prematurely")
        print("2. 2FA push notification may not be triggered correctly")
        print("3. Email notifications sent before actual completion")
        
    if manual_success:
        print("\n✅ Manual process worked - check your mobile device!")
    
    print("\n📧 Email notification timing issue identified:")
    print("- Success emails sent before 2FA completion")
    print("- Need to wait for actual authentication completion")
    print("- 2FA notification should be sent when push is requested")


if __name__ == "__main__":
    asyncio.run(main())