#!/usr/bin/env python3
"""Debug DOI translator execution."""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright

async def debug_doi_translator():
    """Debug why DOI translator fails."""
    
    doi = "10.1084/jem.20202717"
    doi_url = f"https://doi.org/{doi}"
    
    print("🔍 Debugging DOI Translator Execution")
    print("=" * 60)
    
    # Load DOI translator
    translator_path = Path(__file__).parent.parent / "src/scitex/scholar/zotero_translators/DOI.js"
    with open(translator_path, 'r', encoding='utf-8') as f:
        translator_code = f.read()
    
    print(f"Translator size: {len(translator_code)} characters")
    
    # Check for syntax issues
    print("\nChecking for common issues:")
    
    # Look for /** BEGIN TEST CASES **/ section
    test_cases_idx = translator_code.find("/** BEGIN TEST CASES **/")
    if test_cases_idx > 0:
        print(f"✓ Found test cases section at position {test_cases_idx}")
        # Remove test cases for execution
        translator_code_clean = translator_code[:test_cases_idx]
        print(f"Cleaned translator size: {len(translator_code_clean)} characters")
    else:
        translator_code_clean = translator_code
    
    # Run in browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            
            # Navigate to DOI URL
            await page.goto(doi_url, wait_until='domcontentloaded')
            
            # Try to execute translator step by step
            print("\n🔄 Executing translator in browser...")
            
            # First, inject minimal Zotero environment
            await page.evaluate('''
                window.Zotero = {
                    debug: console.log,
                    loadTranslator: function() {
                        return {
                            setTranslator: function() {},
                            setSearch: function() {},
                            setHandler: function() {},
                            translate: async function() {}
                        };
                    },
                    selectItems: function(items, callback) { callback(items); }
                };
                window.Z = window.Zotero;
                window._zoteroItems = [];
            ''')
            
            # Try to inject translator
            try:
                result = await page.evaluate(f'''
                    try {{
                        // Inject translator code without test cases
                        {translator_code_clean}
                        
                        return {{
                            success: true,
                            detectWeb: typeof detectWeb === 'function',
                            doWeb: typeof doWeb === 'function',
                            getDOIs: typeof getDOIs === 'function'
                        }};
                    }} catch (e) {{
                        return {{
                            success: false,
                            error: e.toString(),
                            line: e.lineNumber,
                            column: e.columnNumber
                        }};
                    }}
                ''')
                
                print(f"\nTranslator injection result: {result}")
                
                if result['success']:
                    # Try to run detectWeb
                    detect_result = await page.evaluate('''
                        try {
                            const result = detectWeb(document, window.location.href);
                            return { success: true, result: result };
                        } catch (e) {
                            return { success: false, error: e.toString() };
                        }
                    ''')
                    print(f"\ndetectWeb result: {detect_result}")
                    
            except Exception as e:
                print(f"\n❌ Injection error: {e}")
                
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_doi_translator())