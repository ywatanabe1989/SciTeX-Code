#!/usr/bin/env python3
"""
Pre-Commit Regression Check

Lightweight regression test that runs before any code changes are committed.
Ensures core functionality is preserved.
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

async def quick_regression_check():
    """Quick regression check for pre-commit hook."""
    print('⚡ PRE-COMMIT REGRESSION CHECK')
    print('='*40)
    
    # Remove ZenRows to ensure local browser
    if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
        del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]
    
    try:
        # Test 1: Core imports work
        print('🔍 Testing core imports...')
        from scitex.scholar.browser.local._BrowserManager import BrowserManager
        from scitex.scholar.utils._PDFClassifier import PDFClassifier
        from scitex.scholar.utils._DirectPDFDownloader import DirectPDFDownloader
        print('✅ Core imports successful')
        
        # Test 2: Invisible browser can be initialized
        print('🎭 Testing invisible browser initialization...')
        from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
        
        auth_manager = AuthenticationManager()
        manager = BrowserManager(
            auth_manager=auth_manager,
            invisible=True,
            viewport_size=(1, 1),
            profile_name='pre_commit_test'
        )
        print('✅ Invisible browser manager created')
        
        # Test 3: PDF classifier works
        print('🔍 Testing PDF classification...')
        classifier = PDFClassifier()
        test_urls = [
            "https://www.science.org/doi/pdf/10.1126/science.aao0702",
            "https://www.science.org/doi/suppl/10.1126/science.aao0702/suppl_file/test.pdf"
        ]
        
        result = classifier.classify_pdf_list(test_urls)
        
        if result["main_count"] == 1 and result["supplementary_count"] == 1:
            print('✅ PDF classification working correctly')
        else:
            print(f'❌ PDF classification failed: {result["main_count"]} main, {result["supplementary_count"]} supp')
            return False
        
        # Test 4: Screenshot downloader initializes
        print('📸 Testing screenshot downloader...')
        downloader = DirectPDFDownloader(capture_screenshots=True)
        print('✅ Screenshot downloader initialized')
        
        print('\n🎉 PRE-COMMIT CHECK PASSED')
        print('✅ All core functionality preserved')
        print('🚀 Safe to commit changes')
        return True
        
    except Exception as e:
        print(f'\n❌ PRE-COMMIT CHECK FAILED')
        print(f'🚨 Error: {e}')
        print('⛔ COMMIT BLOCKED - fix issues before committing')
        return False

if __name__ == "__main__":
    # Set required environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    success = asyncio.run(quick_regression_check())
    exit(0 if success else 1)