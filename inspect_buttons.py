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

async def inspect_buttons():
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
    
    print('Inspecting button HTML structure...')
    
    try:
        manager = BrowserManager(
            headless=False,  # Visible
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        print('Loading OpenURL resolver page...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        print('Inspecting all button-like elements...')
        
        # Get all potential button elements and their HTML
        button_info = await page.evaluate('''() => {
            const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
            return allElements.map((el, index) => ({
                index: index,
                tag: el.tagName,
                type: el.type || 'none',
                value: el.value || 'none',
                text: el.textContent?.trim() || 'none',
                innerHTML: el.innerHTML || 'none',
                outerHTML: el.outerHTML.substring(0, 200),
                className: el.className || 'none',
                id: el.id || 'none',
                onclick: el.onclick ? 'has-onclick' : 'no-onclick',
                name: el.name || 'none'
            }));
        }''')
        
        print(f'\\nFound {len(button_info)} potential button elements:')
        for i, btn in enumerate(button_info):
            print(f'\\n[{i}] {btn["tag"]} (type: {btn["type"]})')
            print(f'    Value: {btn["value"]}')
            print(f'    Text: {btn["text"]}')
            print(f'    Class: {btn["className"]}')
            print(f'    ID: {btn["id"]}')
            print(f'    Name: {btn["name"]}')
            print(f'    OnClick: {btn["onclick"]}')
            print(f'    HTML: {btn["outerHTML"][:100]}...')
            
            # Check if this looks like a GO button
            if (btn["value"] == "GO" or 
                "GO" in btn["text"] or 
                "go" in btn["outerHTML"].lower()):
                print('    🎯 POTENTIAL GO BUTTON!')
        
        print('\\n' + '='*60)
        print('Now manually clicking the third GO button...')
        print('='*60)
        
        # Try to find GO buttons more specifically
        go_buttons = []
        for i, btn in enumerate(button_info):
            if btn["value"] == "GO":
                go_buttons.append((i, btn))
                print(f'GO button {len(go_buttons)}: Element [{i}] - {btn["outerHTML"][:100]}...')
        
        if len(go_buttons) >= 3:
            third_go_index = go_buttons[2][0]  # Get the element index of the 3rd GO button
            print(f'\\nClicking 3rd GO button (element index {third_go_index})...')
            
            # Click by evaluating JavaScript directly
            popup_promise = page.wait_for_event('popup', timeout=30000)
            
            await page.evaluate(f'''() => {{
                const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                const targetButton = allElements[{third_go_index}];
                if (targetButton) {{
                    console.log('Clicking button:', targetButton);
                    targetButton.click();
                }} else {{
                    console.log('Button not found!');
                }}
            }}''')
            
            print('🔄 Click executed! Waiting for popup...')
            
            try:
                popup = await popup_promise
                print('✅ Popup opened!')
                
                # Wait for popup to load
                await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                await popup.wait_for_timeout(10000)
                
                # Take screenshot and get info
                await popup.screenshot(path='aaas_popup_success.png', full_page=True)
                print('📸 Screenshot: aaas_popup_success.png')
                
                popup_title = await popup.title()
                popup_url = popup.url
                print(f'\\nPopup result:')
                print(f'Title: {popup_title}')
                print(f'URL: {popup_url}')
                
                if 'science.org' in popup_url.lower():
                    print('🎉 SUCCESS! Reached Science.org!')
                    
                    # Check for Lean Library
                    lean_elements = await popup.evaluate('document.querySelectorAll("*[class*=\'lean\'], *[data-lean], *[id*=\'lean\']").length')
                    print(f'Lean Library elements: {lean_elements}')
                    
                    if lean_elements > 0:
                        print('🏆 WE WIN! Lean Library is active!')
                
                input('Press Enter to close browsers...')
                await popup.close()
                
            except Exception as popup_error:
                print(f'Popup error: {popup_error}')
                print('Taking screenshot of main page...')
                await page.screenshot(path='after_click_main.png', full_page=True)
                print('📸 Screenshot: after_click_main.png')
        
        else:
            print(f'❌ Found only {len(go_buttons)} GO buttons, need at least 3')
        
        input('\\nPress Enter to close main browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(inspect_buttons())