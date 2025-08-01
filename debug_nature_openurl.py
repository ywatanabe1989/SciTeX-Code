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

async def debug_nature_openurl():
    # Nature Neuroscience article info
    doi = "10.1038/s41593-025-01990-7"
    journal = "Nature Neuroscience"
    year = 2025
    
    print('Debugging Nature OpenURL resolver page...')
    
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
        
        print(f'OpenURL: {openurl}')
        print('Loading OpenURL resolver...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Take screenshot
        await page.screenshot(path='nature_openurl_debug.png', full_page=True)
        print('📸 Screenshot: nature_openurl_debug.png')
        
        # Debug all elements
        all_elements = await page.evaluate('''() => {
            const allElements = Array.from(document.querySelectorAll('input, button, a'));
            return allElements.map((el, index) => ({
                index: index,
                tag: el.tagName,
                type: el.type || 'none',
                value: el.value || 'none',
                text: el.textContent?.trim() || 'none',
                className: el.className || 'none',
                id: el.id || 'none',
                href: el.href || 'none'
            }));
        }''')
        
        print(f'\\nFound {len(all_elements)} elements:')
        
        nature_elements = []
        go_elements = []
        
        for elem in all_elements:
            # Look for Nature-related elements
            if ('nature' in elem['text'].lower() or 
                'nature' in elem['href'].lower() or
                elem['value'] == 'GO'):
                
                print(f'\\n[{elem["index"]}] {elem["tag"]} (type: {elem["type"]})')
                print(f'    Value: {elem["value"]}')
                print(f'    Text: {elem["text"][:100]}...')
                print(f'    Href: {elem["href"][:100]}...')
                print(f'    Class: {elem["className"]}')
                
                if 'nature' in elem['text'].lower():
                    nature_elements.append(elem)
                    print('    🎯 NATURE ELEMENT!')
                
                if elem['value'] == 'GO':
                    go_elements.append(elem)
                    print('    🔘 GO BUTTON!')
        
        print(f'\\n📊 SUMMARY:')
        print(f'Nature elements: {len(nature_elements)}')
        print(f'GO buttons: {len(go_elements)}')
        
        # Try clicking the first GO button if it exists
        if go_elements:
            first_go_index = go_elements[0]['index']
            print(f'\\nTrying to click first GO button (index {first_go_index})...')
            
            try:
                popup_promise = page.wait_for_event('popup', timeout=15000)
                
                await page.evaluate(f'''() => {{
                    const allElements = Array.from(document.querySelectorAll('input, button, a'));
                    const targetButton = allElements[{first_go_index}];
                    if (targetButton) {{
                        console.log('Clicking GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}''')
                
                print('Waiting for popup...')
                popup = await popup_promise
                
                await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                await popup.wait_for_timeout(5000)
                
                popup_title = await popup.title()
                popup_url = popup.url
                
                print(f'\\n✅ POPUP SUCCESS!')
                print(f'Title: {popup_title}')
                print(f'URL: {popup_url}')
                
                # Take popup screenshot
                await popup.screenshot(path='nature_popup_debug.png', full_page=True)
                print('📸 Popup screenshot: nature_popup_debug.png')
                
                await popup.close()
                
            except Exception as popup_error:
                print(f'Popup failed: {popup_error}')
        
        print('\\nBrowser is open for inspection...')
        input('Press Enter to close...')
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_nature_openurl())