#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def take_science_screenshot():
    auth_manager = AuthenticationManager()
    manager = BrowserManager(
        headless=True,  # Headless for screenshot
        profile_name='scholar_default',
        auth_manager=auth_manager
    )
    
    try:
        print('Taking screenshot of Science.org with extensions and auth...')
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        url = 'https://www.science.org/doi/10.1126/science.aao0702'
        print(f'Navigating to: {url}')
        await page.goto(url, timeout=60000)
        
        # Wait for page to fully load and extensions to process
        print('Waiting for page to load and extensions to process...')
        await page.wait_for_timeout(15000)
        
        # Check page state
        title = await page.title()
        print(f'Page title: {title}')
        
        # Take full page screenshot
        await page.screenshot(path='science_with_extensions_final.png', full_page=True)
        print('Screenshot saved: science_with_extensions_final.png')
        
        # Check for extensions working
        try:
            lean_count = await page.evaluate('document.querySelectorAll("*[class*=\'lean\'], *[data-lean], *[id*=\'lean\']").length')
            pdf_count = await page.evaluate('Array.from(document.querySelectorAll("button, a")).filter(el => el.textContent.toLowerCase().includes("pdf")).length')
            
            print(f'Lean Library elements found: {lean_count}')
            print(f'PDF buttons found: {pdf_count}')
            
            # Use built-in detection method
            has_lean_button = await manager.has_lean_library_pdf_button(page, url)
            print(f'BrowserManager detects Lean Library PDF button: {has_lean_button}')
            
        except Exception as e:
            print(f'Error checking elements: {e}')
        
        # Check if we bypassed Cloudflare
        content = await page.content()
        if 'challenges.cloudflare.com' in content:
            print('❌ Still showing Cloudflare challenge')
        elif 'Hippocampal ripples down-regulate synapses' in content:
            print('✅ Successfully loaded Science article!')
        elif 'Just a moment' in title:
            print('🤖 Cloudflare processing (may resolve automatically)')
        else:
            print('? Unknown page state')
            
        print('\\nScreenshot captured showing current state of Science.org page')
        print('with extensions loaded and authentication active.')
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        try:
            await manager.__aexit__(None, None, None)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(take_science_screenshot())