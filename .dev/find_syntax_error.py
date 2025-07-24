#!/usr/bin/env python3
"""Find the exact syntax error in DOI translator."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def find_error():
    """Test DOI translator line by line to find syntax error."""
    
    print("🔍 Finding Syntax Error in DOI Translator")
    print("=" * 60)
    
    # Load translator
    translator_path = Path(__file__).parent.parent / "src/scitex/scholar/zotero_translators/DOI.js"
    with open(translator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove test cases
    test_idx = content.find("/** BEGIN TEST CASES **/")
    if test_idx > 0:
        content = content[:test_idx]
    
    # Split into sections
    lines = content.split('\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            await page.goto("about:blank")
            
            # Test progressively
            test_sections = [
                ("Metadata only", lines[:13]),  # Just the JSON metadata
                ("License block", lines[:36]),   # Include license
                ("DOI regex", lines[:50]),       # Include regex definition
                ("getDOIs function", lines[:72]), # First function
                ("All functions", lines[:152]),  # Before async functions
                ("With async", lines)            # Everything
            ]
            
            for name, section in test_sections:
                code = '\n'.join(section)
                
                # For metadata, wrap in comment
                if name == "Metadata only":
                    code = "/*\n" + code + "\n*/"
                
                try:
                    result = await page.evaluate(f'''
                        () => {{
                            try {{
                                // Test code section
                                {code}
                                return {{ success: true, section: "{name}" }};
                            }} catch (e) {{
                                return {{ 
                                    success: false, 
                                    section: "{name}",
                                    error: e.toString(),
                                    message: e.message
                                }};
                            }}
                        }}
                    ''')
                    
                    if result['success']:
                        print(f"✅ {name}: OK")
                    else:
                        print(f"❌ {name}: {result['error']}")
                        break
                        
                except Exception as e:
                    print(f"❌ {name}: Injection failed - {str(e)[:100]}")
                    
                    # Try to find the specific line
                    if "Unexpected token ':'" in str(e):
                        print("\n  Looking for the problematic colon...")
                        
                        # Check each line for the issue
                        for i, line in enumerate(section[-20:], len(section)-20):
                            if ':' in line and not any(x in line for x in ['://', 'function', 'if', 'for']):
                                print(f"  Line {i+1}: {line.strip()}")
                    break
                    
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(find_error())