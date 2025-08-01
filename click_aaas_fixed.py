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

async def click_aaas_fixed():
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
    
    print('Clicking AAAS GO button with fixed selectors...')
    print(f'Target: {title}')
    print(f'DOI: {doi}')
    print()
    
    try:
        manager = BrowserManager(
            headless=False,  # Visible to see the process
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        print('Step 1: Loading OpenURL resolver page...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        print('Step 2: Finding AAAS GO button with multiple selectors...')
        
        # Try multiple button selectors
        button_selectors = [
            'input[value="GO"]',
            'button:has-text("GO")',
            'input[type="button"][value="GO"]',
            'input[type="submit"][value="GO"]',
            '.go-button',
            '[value="GO"]'
        ]
        
        all_buttons = []
        for selector in button_selectors:
            try:
                buttons = await page.query_selector_all(selector)
                for btn in buttons:
                    if btn not in all_buttons:
                        all_buttons.append(btn)
                        print(f'Found button with selector: {selector}')
            except:
                continue
        
        print(f'Total unique buttons found: {len(all_buttons)}')
        
        if len(all_buttons) >= 3:
            # Click the third button (AAAS)
            aaas_button = all_buttons[2]
            print('✅ Found AAAS GO button (3rd button)')
            
            print('Step 3: Clicking AAAS GO button and handling popup...')
            
            # Handle popup
            popup_promise = page.wait_for_event('popup', timeout=30000)
            await aaas_button.click()
            print('🔄 Clicked! Waiting for popup...')
            
            popup = await popup_promise
            print('✅ Popup opened!')
            
            # Wait for popup to load
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(5000)
            
            # Take initial screenshot
            await popup.screenshot(path='aaas_popup_initial.png', full_page=True)
            print('📸 Screenshot: aaas_popup_initial.png')
            
            initial_title = await popup.title()
            initial_url = popup.url
            print(f'Initial popup: "{initial_title}" | {initial_url}')
            
            # Wait for any authentication redirects
            print('Step 4: Waiting for authentication and redirects...')
            await popup.wait_for_timeout(15000)
            
            # Take screenshot after redirects
            await popup.screenshot(path='aaas_popup_after_auth.png', full_page=True)
            print('📸 Screenshot: aaas_popup_after_auth.png')
            
            final_title = await popup.title()
            final_url = popup.url
            print(f'After auth: "{final_title}" | {final_url}')
            
            # Check if we reached Science.org
            if 'science.org' in final_url.lower():
                print('🎉 SUCCESS: Reached Science.org with institutional access!')
                
                # Now check for Lean Library OpenAthens PDF button - THE WIN CONDITION!
                print('\\nStep 5: Checking for Lean Library OpenAthens PDF button...')
                
                # Wait a bit more for Lean Library to load
                await popup.wait_for_timeout(8000)
                
                # Take final screenshot
                await popup.screenshot(path='aaas_science_final.png', full_page=True)
                print('📸 Screenshot: aaas_science_final.png')
                
                # Check for Lean Library elements
                lean_check = await popup.evaluate('''() => {
                    const leanElements = document.querySelectorAll('*[class*="lean"], *[data-lean], *[id*="lean"]');
                    const pdfButtons = Array.from(document.querySelectorAll('button, a, input')).filter(el => 
                        el.textContent.toLowerCase().includes('pdf') ||
                        el.textContent.toLowerCase().includes('download') ||
                        el.getAttribute('title')?.toLowerCase().includes('pdf')
                    );
                    
                    // Also check for OpenAthens-specific elements
                    const openathensElements = Array.from(document.querySelectorAll('*')).filter(el => 
                        el.textContent.toLowerCase().includes('openathens') ||
                        el.className.toLowerCase().includes('openathens') ||
                        el.getAttribute('data-provider')?.toLowerCase().includes('openathens')
                    );
                    
                    return {
                        leanCount: leanElements.length,
                        leanElements: Array.from(leanElements).map(el => ({
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0, 100),
                            className: el.className,
                            id: el.id,
                            attributes: Object.fromEntries(Array.from(el.attributes).map(attr => [attr.name, attr.value]))
                        })),
                        pdfButtons: pdfButtons.map(el => ({
                            tag: el.tagName,
                            text: el.textContent.trim(),
                            href: el.href || el.value || 'no-href',
                            className: el.className,
                            title: el.title || ''
                        })),
                        openathensElements: openathensElements.map(el => ({
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0, 50),
                            className: el.className
                        }))
                    };
                }''')
                
                print(f'\\n🔍 ANALYSIS RESULTS:')
                print(f'Lean Library elements: {lean_check["leanCount"]}')
                print(f'PDF/Download buttons: {len(lean_check["pdfButtons"])}')
                print(f'OpenAthens elements: {len(lean_check["openathensElements"])}')
                
                if lean_check["leanCount"] > 0:
                    print('\\n🏆 WE WIN! Lean Library is active:')
                    for elem in lean_check["leanElements"]:
                        print(f'  - {elem["tag"]}.{elem["className"]}: {elem["text"][:50]}...')
                        if 'pdf' in elem["text"].lower() or 'openathens' in str(elem).lower():
                            print('    🎯 BINGO! OpenAthens PDF access detected!')
                
                if lean_check["pdfButtons"]:
                    print(f'\\n📄 PDF/Download buttons found:')
                    for btn in lean_check["pdfButtons"]:
                        print(f'  - {btn["tag"]}: "{btn["text"]}" | {btn["href"][:50]}...')
                        if 'institutional' in btn["text"].lower() or 'openathens' in btn["href"].lower():
                            print('    🎯 Institutional/OpenAthens access!')
                
                if lean_check["openathensElements"]:
                    print(f'\\n🔐 OpenAthens elements found:')
                    for elem in lean_check["openathensElements"]:
                        print(f'  - {elem["tag"]}: "{elem["text"]}"')
                
                # Check page content for institutional access indicators
                content = await popup.content()
                institutional_indicators = [
                    'institutional access',
                    'university access',
                    'download pdf',
                    'full text access',
                    'subscribed content'
                ]
                
                found_indicators = [ind for ind in institutional_indicators if ind in content.lower()]
                if found_indicators:
                    print(f'\\n✅ INSTITUTIONAL ACCESS CONFIRMED! Found: {found_indicators}')
                else:
                    # Check if still behind paywall
                    paywall_indicators = ['register', 'subscribe', 'purchase', 'sign in to access']
                    found_paywall = [ind for ind in paywall_indicators if ind in content.lower()]
                    if found_paywall:
                        print(f'\\n⚠️  Still behind paywall: {found_paywall}')
                    else:
                        print('\\n❓ Access status unclear')
                
            else:
                print(f'❌ Did not reach Science.org. Final URL: {final_url}')
                if 'openathens' in final_url.lower():
                    print('🔐 Still in OpenAthens authentication flow')
                elif 'shibboleth' in final_url.lower():
                    print('🔐 In Shibboleth authentication flow')
            
            print('\\n' + '='*60)
            print('INSTITUTIONAL ACCESS TEST COMPLETE')
            print('='*60)
            print('Screenshots taken:')
            print('1. aaas_popup_initial.png - Initial popup')
            print('2. aaas_popup_after_auth.png - After authentication')
            print('3. aaas_science_final.png - Final Science.org page')
            print('='*60)
            
            input('\\nPress Enter to close browsers...')
            await popup.close()
            
        else:
            print(f'❌ Expected at least 3 buttons, found {len(all_buttons)}')
            # Take screenshot for debugging
            await page.screenshot(path='debug_buttons.png', full_page=True)
            print('📸 Debug screenshot: debug_buttons.png')
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(click_aaas_fixed())