#!/usr/bin/env python3
"""
Debug JavaScript Injection Error

Focus on identifying where the 'str' object is not callable error is coming from.
"""

import asyncio
import sys
import os
from pathlib import Path
import traceback

# Remove ZenRows to ensure local browser
if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
    del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
from scitex.scholar.utils._JavaScriptInjectionPDFDetector import JavaScriptInjectionPDFDetector


async def debug_injection_error():
    print('🐛 Debugging JavaScript Injection Error')
    print('='*50)
    
    try:
        print('🔧 Initializing browser...')
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        print('✅ Browser ready')
        
        test_url = "https://www.science.org/doi/10.1126/science.aao0702"
        print(f'📄 Testing: {test_url}')
        
        page = await context.new_page()
        
        print('Step 1: Loading page...')
        await page.goto(test_url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        print('Step 2: Initializing detector...')
        detector = JavaScriptInjectionPDFDetector()
        
        print('Step 3: Finding translator...')
        translator = detector.find_best_translator(test_url)
        if translator:
            print(f'✅ Found translator: {translator["label"]}')
        else:
            print('❌ No translator found')
        
        print('Step 4: Injecting shim...')
        try:
            await page.evaluate(detector._pdf_detection_shim)
            print('✅ Shim injected successfully')
        except Exception as shim_error:
            print(f'❌ Shim injection failed: {shim_error}')
            traceback.print_exc()
            return
        
        print('Step 5: Testing basic PDF detection...')
        try:
            basic_test = await page.evaluate('''
                () => {
                    try {
                        if (!window.Zotero || !window.Zotero.Utilities) {
                            return { error: "Zotero not available" };
                        }
                        
                        const pdfUrls = window.Zotero.Utilities.detectPDFUrls(document);
                        return { success: true, pdfUrls: pdfUrls };
                    } catch (e) {
                        return { error: e.toString(), stack: e.stack };
                    }
                }
            ''')
            
            if basic_test.get('success'):
                print(f'✅ Basic detection works: {len(basic_test["pdfUrls"])} PDFs')
            else:
                print(f'❌ Basic detection failed: {basic_test.get("error")}')
                
        except Exception as basic_error:
            print(f'❌ Basic test failed: {basic_error}')
            traceback.print_exc()
        
        print('Step 6: Running full detection with verbose error handling...')
        try:
            # Call the detection method with extra error handling
            result = await detector.detect_pdfs_with_injection(page, test_url)
            
            print('Detection completed!')
            print(f'Method: {result.detection_method}')
            print(f'PDFs found: {len(result.pdf_urls)}')
            print(f'Debug info: {result.debug_info}')
            
        except Exception as full_error:
            print(f'❌ Full detection failed: {full_error}')
            print('Full traceback:')
            traceback.print_exc()
        
        await page.close()
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'❌ Debug session failed: {e}')
        traceback.print_exc()


if __name__ == "__main__":
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    asyncio.run(debug_injection_error())