#!/usr/bin/env python3
"""
PDF download with extended wait time for manual authentication.

This version waits longer before closing the browser to allow 
time for manual authentication and PDF download.
"""
import asyncio
import sys
import os
from pathlib import Path

# Remove ZenRows to ensure local browser
if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
    del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def download_with_wait_time():
    print('🎯 PDF Download with Extended Wait Time for Authentication')
    print('='*60)
    print('✅ Browser will stay open for 5 minutes for manual authentication')
    print('✅ You can complete University login and download PDFs')
    print('='*60)
    print()
    
    # Test with Science paper
    paper = {
        "name": "Science - Hippocampal ripples",
        "doi": "10.1126/science.aao0702",
        "title": "Hippocampal ripples down-regulate synapses",
        "journal": "Science",
        "year": 2018,
        "volume": 359,
        "issue": 6383,
        "pages": "1524-1527",
        "filename": "Norimoto-2018-Science-Hippocampal_ripples.pdf"
    }
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    try:
        print('🔧 Initializing browser...')
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible for manual interaction
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser initialized with fixed profile + extensions')
        print()
        
        print(f'📄 Opening: {paper["name"]}')
        print(f'DOI: {paper["doi"]}')
        print(f'Target filename: {paper["filename"]}')
        print()
        
        page = await context.new_page()
        
        # Build OpenURL for Science paper
        from urllib.parse import urlencode
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
            "rft.atitle": paper["title"],
            "rft.jtitle": paper["journal"],
            "rft.date": str(paper["year"]),
            "rft.volume": str(paper["volume"]),
            "rft.issue": str(paper["issue"]),
            "rft.spage": "1524",
            "rft.epage": "1527",
            "rft.doi": paper["doi"]
        }
        
        resolver_url = os.environ.get("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                                    "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
        openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
        
        print('Step 1: Loading OpenURL resolver...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        print('Step 2: Finding and clicking AAAS GO button...')
        
        # Find and click AAAS GO button
        all_elements = await page.evaluate('''() => {
            const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
            return allElements.map((el, index) => ({
                index: index,
                value: el.value || 'none'
            }));
        }''')
        
        aaas_button_index = -1
        for elem in all_elements:
            if (elem['value'] == 'Go' and elem['index'] >= 35 and elem['index'] <= 45):
                aaas_button_index = elem['index']
                print(f'✅ Found AAAS GO button at index {aaas_button_index}')
                break
        
        if aaas_button_index >= 0:
            print('Step 3: Clicking GO button and opening Science.org popup...')
            
            # Set up popup listener
            popup_promise = page.wait_for_event('popup', timeout=30000)
            
            # Click GO button
            await page.evaluate(f'''() => {{
                const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                const targetButton = allElements[{aaas_button_index}];
                if (targetButton && targetButton.value === 'Go') {{
                    targetButton.click();
                    return 'clicked';
                }}
                return 'not-found';
            }}''')
            
            popup = await popup_promise
            print('✅ Science.org popup opened!')
            
            # Wait for popup to load
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(5000)
            
            popup_title = await popup.title()
            popup_url = popup.url
            print(f'Popup page: {popup_title}')
            print(f'URL: {popup_url[:80]}...')
            print()
            
            print('🔐 MANUAL AUTHENTICATION REQUIRED')
            print('='*50)
            print('The University of Melbourne login page is now open.')
            print('Please:')
            print('1. Complete your University authentication in the popup')
            print('2. You will be redirected to the Science.org article')
            print('3. Look for "Download PDF" or "PDF" links')
            print('4. Download the PDF and save it to the downloads/ folder')
            print(f'5. Suggested filename: {paper["filename"]}')
            print()
            print('⏰ Browser will stay open for 5 minutes to complete this process.')
            print()
            
            # Wait 5 minutes for manual authentication and download
            print('Waiting 5 minutes for manual authentication and PDF download...')
            for i in range(30):  # 30 intervals of 10 seconds = 5 minutes
                await asyncio.sleep(10)
                
                # Check if PDF was downloaded
                pdf_files = list(downloads_dir.glob("*.pdf"))
                if pdf_files:
                    print(f'✅ PDF DETECTED! Found: {[f.name for f in pdf_files]}')
                    break
                
                remaining_time = 5 - (i + 1) * 10 / 60
                if remaining_time > 0:
                    print(f'⏰ Time remaining: {remaining_time:.1f} minutes...')
            
            print()
            print('🔍 Checking for downloaded PDFs...')
            
            pdf_files = list(downloads_dir.glob("*.pdf"))
            if pdf_files:
                print('🎉 SUCCESS! Found downloaded PDFs:')
                for pdf_file in pdf_files:
                    size_mb = pdf_file.stat().st_size / (1024 * 1024)
                    print(f'  ✅ {pdf_file.name} ({size_mb:.1f} MB)')
                print()
                print('🏆 PDF download system is fully functional!')
            else:
                print('📁 No PDFs found in downloads/ directory')
                print('If you downloaded manually, make sure to save to downloads/ folder')
            
            # Take final screenshot
            try:
                await popup.screenshot(path='final_state.png', full_page=True)
                print('📸 Final state screenshot: final_state.png')
            except:
                pass
            
            await popup.close()
            
        else:
            print('❌ AAAS GO button not found')
        
        await page.close()
        
        print()
        print('🏁 Session Complete')
        print('='*60)
        
        # Final summary
        final_pdf_files = list(downloads_dir.glob("*.pdf"))
        if final_pdf_files:
            print(f'📁 Final result: {len(final_pdf_files)} PDF(s) in downloads/')
            for pdf_file in final_pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'   🎉 {pdf_file.name} ({size_mb:.1f} MB)')
        else:
            print('📁 No PDFs in downloads/ - check if saved elsewhere')
        
        print('='*60)
        print('🚀 PDF download system test complete!')
        
        # Clean up
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    asyncio.run(download_with_wait_time())