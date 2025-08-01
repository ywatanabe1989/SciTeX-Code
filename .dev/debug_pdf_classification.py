#!/usr/bin/env python3
"""
Debug PDF Classification Issue

Investigate why we're seeing 2 main PDFs instead of 1 main + 2 supplementary,
and ensure we download the actual main article PDF.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'src')
from playwright.async_api import async_playwright

async def debug_pdf_classification():
    print('🔍 Debugging PDF Classification Issue')
    print('='*50)
    print('🎯 Goal: Identify true main PDF vs supplementary material')
    print('💡 Problem: Getting 2 "main" PDFs, both seem to be supplements')
    print('='*50)
    
    test_url = "https://www.science.org/doi/10.1126/science.aao0702"
    
    # Create debug directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
    debug_dir = Path(f"downloads/pdf_debug_{timestamp}")
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    dimension_spoof = '''
        (() => {
            const TARGET_WIDTH = 1920;
            const TARGET_HEIGHT = 1080;
            Object.defineProperty(window, 'innerWidth', { get: () => TARGET_WIDTH });
            Object.defineProperty(window, 'innerHeight', { get: () => TARGET_HEIGHT });
            console.log('[DEBUG] Dimensions spoofed');
        })();
    '''
    
    playwright = await async_playwright().start()
    
    try:
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--window-size=400,300",  # Small for debugging
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
        )
        
        context = await browser.new_context(viewport={"width": 400, "height": 300})
        page = await context.new_page()
        await page.add_init_script(dimension_spoof)
        
        print('✅ Browser initialized for PDF debugging')
        
        # Navigate and wait
        await page.goto(test_url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        print('✅ Page loaded, analyzing PDF links...')
        
        # Detailed PDF analysis
        pdf_detailed_analysis = await page.evaluate('''
            () => {
                const results = [];
                
                // Find all PDF-related links with detailed information
                const selectors = [
                    'a[href*=".pdf"]',
                    'a[href*="/pdf/"]',
                    'a[href*="/doi/pdf/"]',
                    'a[href*="suppl"]',
                    '.download-pdf',
                    '.pdf-download',
                    '[data-track-action*="pdf"]'
                ];
                
                const foundUrls = new Set();
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    
                    for (const el of elements) {
                        const href = el.href || el.getAttribute('href') || el.getAttribute('data-pdf-url');
                        
                        if (href && !foundUrls.has(href)) {
                            foundUrls.add(href);
                            
                            // Analyze the URL and context
                            const text = el.textContent.trim();
                            const parent = el.parentElement;
                            const parentText = parent ? parent.textContent.trim() : '';
                            
                            // Classification logic
                            const isSupplementary = href.includes('suppl') || 
                                                   text.toLowerCase().includes('supplement') ||
                                                   text.toLowerCase().includes('supporting');
                            
                            const isMainArticle = href.includes('/doi/pdf/') && 
                                                 !href.includes('suppl') &&
                                                 !text.toLowerCase().includes('supplement');
                            
                            const isFirstRelease = text.toLowerCase().includes('first release') ||
                                                  text.toLowerCase().includes('version');
                            
                            // Get element position and visibility
                            const rect = el.getBoundingClientRect();
                            const isVisible = rect.width > 0 && rect.height > 0 && 
                                            el.offsetParent !== null;
                            
                            results.push({
                                url: href,
                                text: text.substring(0, 100),
                                parentText: parentText.substring(0, 100),
                                isSupplementary: isSupplementary,
                                isMainArticle: isMainArticle,
                                isFirstRelease: isFirstRelease,
                                isVisible: isVisible,
                                selector: selector,
                                className: el.className,
                                id: el.id || 'no-id',
                                position: {
                                    x: Math.round(rect.x),
                                    y: Math.round(rect.y),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                }
                            });
                        }
                    }
                }
                
                return results;
            }
        ''')
        
        print(f'📊 Detailed PDF Analysis: {len(pdf_detailed_analysis)} unique PDFs found')
        print()
        
        # Categorize and display results
        main_pdfs = [p for p in pdf_detailed_analysis if p['isMainArticle']]
        supp_pdfs = [p for p in pdf_detailed_analysis if p['isSupplementary']]
        first_release_pdfs = [p for p in pdf_detailed_analysis if p['isFirstRelease']]
        other_pdfs = [p for p in pdf_detailed_analysis if not (p['isMainArticle'] or p['isSupplementary'] or p['isFirstRelease'])]
        
        print(f'📋 PDF CATEGORIZATION:')
        print(f'🎯 Main Article PDFs: {len(main_pdfs)}')
        print(f'📎 Supplementary PDFs: {len(supp_pdfs)}')
        print(f'📄 First Release PDFs: {len(first_release_pdfs)}')
        print(f'❓ Other PDFs: {len(other_pdfs)}')
        print()
        
        # Show details for each category
        if main_pdfs:
            print('🎯 MAIN ARTICLE PDFs:')
            for i, pdf in enumerate(main_pdfs, 1):
                print(f'   {i}. Text: "{pdf["text"]}"')
                print(f'      URL: {pdf["url"]}')
                print(f'      Visible: {pdf["isVisible"]}')
                print(f'      Position: {pdf["position"]["x"]},{pdf["position"]["y"]} ({pdf["position"]["width"]}x{pdf["position"]["height"]})')
                print()
        
        if supp_pdfs:
            print('📎 SUPPLEMENTARY PDFs:')
            for i, pdf in enumerate(supp_pdfs, 1):
                print(f'   {i}. Text: "{pdf["text"]}"')
                print(f'      URL: {pdf["url"]}')
                print(f'      Visible: {pdf["isVisible"]}')
                print()
        
        if first_release_pdfs:
            print('📄 FIRST RELEASE PDFs:')
            for i, pdf in enumerate(first_release_pdfs, 1):
                print(f'   {i}. Text: "{pdf["text"]}"')
                print(f'      URL: {pdf["url"]}')
                print(f'      Visible: {pdf["isVisible"]}')
                print()
        
        if other_pdfs:
            print('❓ OTHER PDFs:')
            for i, pdf in enumerate(other_pdfs, 1):
                print(f'   {i}. Text: "{pdf["text"]}"')
                print(f'      URL: {pdf["url"]}')
                print(f'      Visible: {pdf["isVisible"]}')
                print()
        
        # Take screenshot with PDF links highlighted
        screenshot_path = debug_dir / "pdf_links_analysis.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f'📸 Screenshot saved: {screenshot_path.name}')
        
        # Test downloading the most likely main PDF
        true_main_pdf = None
        if main_pdfs:
            # Choose the main PDF that's most likely to be the article
            main_candidates = sorted(main_pdfs, key=lambda x: (
                x['isVisible'],  # Prioritize visible links
                not x['text'].lower().find('supplement'),  # Avoid supplements
                len(x['text'])  # Prefer longer, more descriptive text
            ), reverse=True)
            
            true_main_pdf = main_candidates[0]
            print(f'🎯 IDENTIFIED TRUE MAIN PDF:')
            print(f'   Text: "{true_main_pdf["text"]}"')
            print(f'   URL: {true_main_pdf["url"]}')
            
            # Quick download test
            print(f'\n📥 Testing main PDF download...')
            try:
                await page.goto(true_main_pdf["url"], timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Check if it's actually a PDF
                pdf_check = await page.evaluate('''
                    () => {
                        return {
                            url: window.location.href,
                            contentType: document.contentType || '',
                            title: document.title,
                            hasPDFEmbed: document.querySelector('embed[type="application/pdf"]') !== null,
                            bodyText: document.body ? document.body.textContent.substring(0, 200) : ''
                        };
                    }
                ''')
                
                print(f'   📄 URL: {pdf_check["url"][:60]}...')
                print(f'   📋 Content-Type: {pdf_check["contentType"]}')
                print(f'   📄 Title: {pdf_check["title"][:50]}...')
                print(f'   🎯 Is PDF: {pdf_check["hasPDFEmbed"] or "application/pdf" in pdf_check["contentType"]}')
                
                if pdf_check["hasPDFEmbed"] or "application/pdf" in pdf_check["contentType"]:
                    print('   ✅ This appears to be the real main article PDF!')
                else:
                    print('   ⚠️  This might not be a direct PDF link')
                    print(f'   📝 Body preview: {pdf_check["bodyText"][:100]}...')
                
            except Exception as e:
                print(f'   ❌ PDF download test failed: {e}')
        
        # Summary recommendations
        print(f'\n💡 CLASSIFICATION RECOMMENDATIONS:')
        print(f'1. True main PDF should be: {true_main_pdf["url"] if true_main_pdf else "Not found"}')
        print(f'2. Supplementary PDFs: {len(supp_pdfs)} found')
        print(f'3. Classification logic needs refinement for Science.org')
        print(f'4. Consider link text and parent context for better detection')
        
        await browser.close()
        
    except Exception as e:
        print(f'❌ Debug failed: {e}')
    
    finally:
        await playwright.stop()
    
    print(f'\n📁 Debug results saved to: {debug_dir}')
    return debug_dir

if __name__ == "__main__":
    asyncio.run(debug_pdf_classification())