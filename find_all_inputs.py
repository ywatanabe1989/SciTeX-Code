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

async def find_all_inputs():
    # Nature Neuroscience article info
    doi = "10.1038/s41593-025-01990-7"
    journal = "Nature Neuroscience"
    year = 2025
    
    print('🔍 Finding all input elements on Nature OpenURL page...')
    
    try:
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        # Build OpenURL for Nature article
        from urllib.parse import urlencode
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
            "rft.jtitle": journal,
            "rft.date": str(year),
            "rft_id": f"info:doi/{doi}",
            "url_ver": "Z39.88-2004"
        }
        
        resolver_url = os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"]
        openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
        
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Find ALL input elements and check their properties
        all_inputs = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input'));
            return inputs.map((input, index) => ({
                index: index,
                type: input.type,
                value: input.value,
                name: input.name || 'no-name',
                id: input.id || 'no-id',
                className: input.className || 'no-class',
                onclick: input.onclick ? 'has-onclick' : 'no-onclick',
                outerHTML: input.outerHTML
            }));
        }''')
        
        print(f'\\nFound {len(all_inputs)} input elements:')
        
        go_candidates = []
        for i, inp in enumerate(all_inputs):
            print(f'\\n[{i}] Type: {inp["type"]} | Value: "{inp["value"]}" | Name: {inp["name"]}')
            print(f'    ID: {inp["id"]} | Class: {inp["className"]}')
            print(f'    OnClick: {inp["onclick"]}')
            print(f'    HTML: {inp["outerHTML"]}')
            
            # Look for GO-like values (case insensitive)
            if inp["value"].upper() in ["GO", "GO!"]:
                go_candidates.append((i, inp))
                print(f'    🎯 POTENTIAL GO BUTTON!')
        
        print(f'\\n📊 SUMMARY: Found {len(go_candidates)} potential GO buttons')
        
        if go_candidates:
            # Try clicking the first GO candidate
            first_go_index, first_go = go_candidates[0]
            print(f'\\nTrying to click first GO button (index {first_go_index}): "{first_go["value"]}"')
            
            try:
                popup_promise = page.wait_for_event('popup', timeout=15000)
                
                await page.evaluate(f'''() => {{
                    const inputs = Array.from(document.querySelectorAll('input'));
                    const targetButton = inputs[{first_go_index}];
                    if (targetButton) {{
                        console.log('Clicking GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}''')
                
                print('🔄 GO button clicked! Waiting for popup...')
                popup = await popup_promise
                
                await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                await popup.wait_for_timeout(8000)
                
                popup_title = await popup.title()
                popup_url = popup.url
                
                print(f'\\n✅ POPUP SUCCESS!')
                print(f'Title: {popup_title}')
                print(f'URL: {popup_url}')
                
                # Take popup screenshot
                await popup.screenshot(path='nature_popup_success.png', full_page=True)
                print('📸 Popup screenshot: nature_popup_success.png')
                
                if 'nature.com' in popup_url.lower():
                    print('🎉 SUCCESS! Reached Nature.com with institutional access!')
                    
                    # Check for Lean Library
                    lean_elements = await popup.evaluate('document.querySelectorAll("*[class*=\'lean\'], *[data-lean], *[id*=\'lean\']").length')
                    print(f'Lean Library elements: {lean_elements}')
                    
                    if lean_elements > 0:
                        print('🏆 WE WIN! Lean Library is active on Nature!')
                
                await popup.close()
                
            except Exception as popup_error:
                print(f'Popup failed: {popup_error}')
        
        else:
            print('❌ No GO buttons found')
        
        print('\\nBrowser is open for inspection...')
        input('Press Enter to close...')
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_all_inputs())