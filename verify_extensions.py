#!/usr/bin/env python3
"""
Verify that browser extensions are properly loaded and functional.
"""
import asyncio
import sys
import os

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def verify_extensions():
    print('🔍 Verifying browser extensions are properly loaded and functional...')
    print()
    
    try:
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible so we can see extensions
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        print('Step 1: Checking extension availability via JavaScript...')
        
        # Check if extensions are injected into the page
        extension_check = await page.evaluate('''() => {
            const results = {};
            
            // Check for common extension indicators
            results.zoteroConnector = !!window.Zotero;
            results.leanLibrary = !!document.querySelector('[data-lean-library]') || 
                                 !!window.leanLibrary;
            results.twoCapchaExtension = !!window.captchaSolver || 
                                       !!document.querySelector('[data-captcha-solver]');
            results.acceptCookies = !!window.cookieAcceptor ||
                                  !!document.querySelector('[data-cookie-acceptor]');
            
            // Check for extension-specific DOM modifications
            results.extensionScripts = Array.from(document.querySelectorAll('script')).length;
            results.extensionElements = Array.from(document.querySelectorAll('[data-extension-id]')).length;
            
            return results;
        }''')
        
        print('Extension detection results:')
        for ext, detected in extension_check.items():
            status = '✅' if detected else '❌'
            print(f'  {status} {ext}: {detected}')
        
        print()
        print('Step 2: Navigating to chrome://extensions/ to verify installation...')
        
        # Navigate to extensions page to see what's actually installed
        extensions_page = await context.new_page()
        await extensions_page.goto('chrome://extensions/')
        await extensions_page.wait_for_timeout(3000)
        
        # Take screenshot of extensions page
        await extensions_page.screenshot(path='extensions_page.png', full_page=True)
        print('✅ Extensions page screenshot saved: extensions_page.png')
        
        # Try to get extension info from the extensions page
        extension_info = await extensions_page.evaluate('''() => {
            const extensionElements = Array.from(document.querySelectorAll('extensions-item'));
            return extensionElements.map(el => {
                const name = el.shadowRoot?.querySelector('#name')?.textContent || 'Unknown';
                const id = el.getAttribute('id') || 'Unknown';
                const enabled = el.hasAttribute('enabled') || 
                              el.shadowRoot?.querySelector('#enableToggle')?.checked || false;
                return { name, id, enabled };
            });
        }''')
        
        print()
        print(f'Found {len(extension_info)} extensions:')
        for ext in extension_info:
            status = '✅' if ext['enabled'] else '❌'
            print(f'  {status} {ext["name"]} (ID: {ext["id"][:20]}...)')
        
        print()
        print('Step 3: Testing Cloudflare challenge detection...')
        
        # Navigate to a test page that might trigger Cloudflare
        test_page = await context.new_page()
        print('Navigating to Science.org to test Cloudflare handling...')
        
        try:
            await test_page.goto('https://www.science.org/', timeout=30000)
            await test_page.wait_for_timeout(5000)
            
            page_content = await test_page.content()
            current_url = test_page.url
            
            if 'cloudflare' in page_content.lower() or 'verify you are human' in page_content.lower():
                print('🔒 Cloudflare challenge detected!')
                await test_page.screenshot(path='cloudflare_test.png', full_page=True)
                print('Challenge screenshot: cloudflare_test.png')
                
                print('⏳ Waiting 30 seconds to see if 2Captcha extension handles it...')
                await test_page.wait_for_timeout(30000)
                
                # Check if challenge was resolved
                new_content = await test_page.content()
                new_url = test_page.url
                
                if 'cloudflare' not in new_content.lower() and new_url != current_url:
                    print('✅ Cloudflare challenge was automatically resolved!')
                else:
                    print('❌ Cloudflare challenge was NOT resolved automatically')
                    print('This suggests the 2Captcha extension is not working properly')
            else:
                print('✅ No Cloudflare challenge detected - direct access successful')
            
            await test_page.screenshot(path='science_org_test.png', full_page=True)
            print('Final screenshot: science_org_test.png')
            
        except Exception as nav_error:
            print(f'❌ Navigation to Science.org failed: {nav_error}')
        
        await test_page.close()
        await extensions_page.close()
        await page.close()
        
        print()
        print('🔧 RECOMMENDATIONS:')
        
        # Count enabled extensions
        enabled_count = len([ext for ext in extension_info if ext['enabled']])
        total_count = len(extension_info)
        
        if enabled_count < 10:
            print('❌ Too few extensions enabled - expected ~14 extensions')
            print('   Recommendation: Check extension loading in BrowserManager')
        else:
            print(f'✅ Good extension count: {enabled_count}/{total_count} extensions')
        
        if not extension_check.get('twoCapchaExtension'):
            print('❌ 2Captcha extension not detected in page context')
            print('   Recommendation: Verify 2Captcha extension is properly installed and enabled')
        
        if not extension_check.get('zoteroConnector'):
            print('❌ Zotero Connector not detected in page context')
            print('   Recommendation: Verify Zotero extension injection')
        
        print()
        input('Press Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_extensions())