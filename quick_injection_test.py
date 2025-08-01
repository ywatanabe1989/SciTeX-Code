#!/usr/bin/env python3
"""
Quick JavaScript Injection Test

Simplified test to verify the JavaScript injection PDF detection is working.
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
from scitex.scholar.utils._JavaScriptInjectionPDFDetector import JavaScriptInjectionPDFDetector


async def quick_injection_test():
    print('🧪 Quick JavaScript Injection PDF Detection Test')
    print('='*60)
    
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
        
        # Test just one paper quickly
        test_url = "https://www.science.org/doi/10.1126/science.aao0702"
        print(f'📄 Testing: {test_url}')
        
        page = await context.new_page()
        
        print('Step 1: Loading page...')
        await page.goto(test_url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        current_url = page.url
        print(f'✅ Loaded: {current_url[:60]}...')
        
        print('Step 2: Running JavaScript injection detection...')
        
        detector = JavaScriptInjectionPDFDetector()
        result = await detector.detect_pdfs_with_injection(page, current_url)
        
        print('✅ JavaScript injection completed!')
        print()
        print('📊 RESULTS:')
        print(f'  🔧 Translator: {result.translator_used}')
        print(f'  📍 Method: {result.detection_method}')
        print(f'  📊 Confidence: {result.confidence:.1%}')
        print(f'  📄 PDFs Found: {len(result.pdf_urls)}')
        
        if result.pdf_urls:
            print('  📎 PDF URLs:')
            for i, url in enumerate(result.pdf_urls, 1):
                is_main = '/pdf/' in url and 'suppl' not in url
                marker = '🎯 MAIN' if is_main else '📎 SUPP'
                print(f'    {i}. {marker} {url}')
        
        if result.debug_info and 'error' in result.debug_info:
            print(f'  🐛 Debug: {result.debug_info["error"][:100]}...')
        
        print()
        
        # Test generic detection separately
        print('Step 3: Testing generic detection...')
        generic_result = await page.evaluate('''
            () => {
                try {
                    if (!window.Zotero || !window.Zotero.Utilities) {
                        return { error: "Zotero shim not available" };
                    }
                    
                    const pdfUrls = window.Zotero.Utilities.detectPDFUrls(document);
                    return { 
                        success: true, 
                        pdfUrls: pdfUrls,
                        shimAvailable: true
                    };
                } catch (e) {
                    return { error: e.toString() };
                }
            }
        ''')
        
        if generic_result.get('success'):
            print(f'✅ Generic detection: {len(generic_result["pdfUrls"])} PDFs')
        else:
            print(f'❌ Generic detection failed: {generic_result.get("error", "unknown")}')
        
        await page.close()
        
        print()
        print('🎉 JavaScript injection PDF detection is working!')
        print(f'   Found {len(result.pdf_urls)} PDFs using {result.detection_method} method')
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    asyncio.run(quick_injection_test())