#!/usr/bin/env python3
import asyncio
import sys
import os

# Set the environment variables
os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def click_aaas_for_institutional_access():
    auth_manager = AuthenticationManager()
    
    # Build the OpenURL manually
    doi = "10.1126/science.aao0702"
    title = "Hippocampal ripples down-regulate synapses"
    journal = "Science"
    year = 2018
    volume = 359
    issue = 6383
    
    # Create OpenURL parameters
    from urllib.parse import urlencode
    params = {
        "ctx_ver": "Z39.88-2004",
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft.genre": "article",
        "rft.atitle": title,
        "rft.jtitle": journal,
        "rft.date": str(year),
        "rft.volume": str(volume),
        "rft.issue": str(issue),
        "rft.spage": "1524",
        "rft.epage": "1527",
        "rft.doi": doi
    }
    
    resolver_url = os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"]
    openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
    
    print('Step 1: Clicking AAAS GO button for institutional access...')
    print(f'Target: {title}')
    print(f'DOI: {doi}')
    print()
    
    try:
        manager = BrowserManager(
            headless=False,  # Visible to see authentication flow
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        print('Step 2: Loading OpenURL resolver page...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Take screenshot of the resolver page
        await page.screenshot(path='step1_resolver_page.png', full_page=True)
        print('📸 Screenshot 1: step1_resolver_page.png')
        
        print('Step 3: Looking for AAAS GO button...')
        
        # Find the third GO button (AAAS is the third option in the screenshot)
        go_buttons = await page.query_selector_all('input[value="GO"]')
        print(f'Found {len(go_buttons)} GO buttons')
        
        if len(go_buttons) >= 3:
            aaas_button = go_buttons[2]  # Third button is AAAS
            print('✅ Found AAAS GO button (3rd button)')
            
            print('Step 4: Clicking AAAS GO button...')
            
            # Click and handle popup
            async with page.expect_popup(timeout=30000) as popup_info:
                await aaas_button.click()
                print('🔄 Clicked! Waiting for popup...')
            
            popup = await popup_info.value
            print('✅ Popup opened - following institutional redirect...')
            
            # Wait for initial load
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(5000)
            
            # Take screenshot of initial popup
            await popup.screenshot(path='step2_initial_popup.png', full_page=True)
            print('📸 Screenshot 2: step2_initial_popup.png')
            
            initial_title = await popup.title()
            initial_url = popup.url
            print(f'Initial popup: "{initial_title}" | {initial_url}')
            
            # Wait for any redirects/authentication
            print('Step 5: Waiting for authentication redirects...')
            await popup.wait_for_timeout(10000)
            
            # Take screenshot after redirects
            await popup.screenshot(path='step3_after_redirects.png', full_page=True)
            print('📸 Screenshot 3: step3_after_redirects.png')
            
            auth_title = await popup.title()
            auth_url = popup.url
            print(f'After redirects: "{auth_title}" | {auth_url}')
            
            # Check if we need to continue authentication
            if 'openathens' in auth_url.lower() or 'shibboleth' in auth_url.lower():
                print('🔐 OpenAthens/Shibboleth authentication detected')
                print('Step 6: Waiting for authentication to complete...')
                await popup.wait_for_timeout(15000)
                
                # Take screenshot of auth result
                await popup.screenshot(path='step4_auth_complete.png', full_page=True)
                print('📸 Screenshot 4: step4_auth_complete.png')
                
                final_title = await popup.title()
                final_url = popup.url
                print(f'After auth: "{final_title}" | {final_url}')
            
            # Final check - should be at Science.org now
            print('Step 7: Checking final destination...')
            await popup.wait_for_timeout(5000)
            
            final_title = await popup.title()
            final_url = popup.url
            content = await popup.content()
            
            # Take final screenshot
            await popup.screenshot(path='step5_final_result.png', full_page=True)
            print('📸 Screenshot 5: step5_final_result.png')
            
            print(f'\\n🎯 FINAL RESULT:')
            print(f'Title: {final_title}')
            print(f'URL: {final_url}')
            
            if 'science.org' in final_url.lower():
                print('🎉 SUCCESS: Reached Science.org!')
                
                # Check for institutional access indicators
                access_indicators = [
                    'download pdf',
                    'full text',
                    'institutional access',
                    'university access'
                ]
                
                has_access = any(indicator in content.lower() for indicator in access_indicators)
                has_paywall = any(term in content.lower() for term in ['register', 'subscribe', 'purchase'])
                
                if has_access and not has_paywall:
                    print('✅ FULL SUCCESS: Institutional access confirmed!')
                elif has_access:
                    print('⚠️  Partial success: Access indicators found but paywall still present')
                else:
                    print('❌ No clear institutional access indicators')
                
                # Check for Lean Library OpenAthens PDF button - THIS IS THE WIN CONDITION!
                print('\\nStep 8: Checking for Lean Library OpenAthens PDF button...')
                
                lean_elements = await popup.evaluate('''() => {
                    const elements = document.querySelectorAll('*[class*="lean"], *[data-lean], *[id*="lean"]');
                    const results = [];
                    elements.forEach(el => {
                        const text = el.textContent || el.innerText || '';
                        const attrs = {};
                        for (let attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        results.push({
                            tag: el.tagName,
                            text: text.substring(0, 100),
                            attributes: attrs,
                            className: el.className
                        });
                    });
                    return results;
                }''')
                
                if lean_elements and len(lean_elements) > 0:
                    print(f'🏆 WE WIN! Found {len(lean_elements)} Lean Library elements:')
                    for elem in lean_elements:
                        print(f'  - {elem["tag"]}: {elem["text"][:50]}...')
                        if 'pdf' in elem["text"].lower() or 'openathens' in str(elem).lower():
                            print('    🎯 PDF/OpenAthens related!')
                else:
                    print('❌ No Lean Library elements found')
                
                # Also check for any PDF buttons
                pdf_buttons = await popup.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button, a, input'));
                    return buttons.filter(btn => 
                        btn.textContent.toLowerCase().includes('pdf') ||
                        btn.textContent.toLowerCase().includes('download')
                    ).map(btn => ({
                        tag: btn.tagName,
                        text: btn.textContent.trim(),
                        href: btn.href || btn.value || 'no-href',
                        className: btn.className
                    }));
                }''')
                
                if pdf_buttons:
                    print(f'\\n📄 Found {len(pdf_buttons)} PDF/Download buttons:')
                    for btn in pdf_buttons:
                        print(f'  - {btn["tag"]}: "{btn["text"]}" | {btn["href"]}')
                
            else:
                print(f'❌ Did not reach Science.org. Final URL: {final_url}')
            
            print('\\n' + '='*60)
            print('INSTITUTIONAL ACCESS FLOW COMPLETE')
            print('='*60)
            print('Check the screenshots for the full authentication flow:')
            print('1. step1_resolver_page.png - OpenURL resolver')
            print('2. step2_initial_popup.png - Initial popup')
            print('3. step3_after_redirects.png - After redirects')
            print('4. step4_auth_complete.png - Auth completion')
            print('5. step5_final_result.png - Final Science.org page')
            print('='*60)
            
            input('Press Enter to close browsers...')
            await popup.close()
            
        else:
            print(f'❌ Expected at least 3 GO buttons, found {len(go_buttons)}')
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(click_aaas_for_institutional_access())