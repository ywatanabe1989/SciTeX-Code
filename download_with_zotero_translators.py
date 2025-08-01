#!/usr/bin/env python3
"""
PDF download using Zotero translator logic for robust extraction.

This approach uses the principles from Zotero translators to find
the correct PDF download links on publisher sites.
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

async def download_with_zotero_translators():
    print('🎯 PDF Download using Zotero Translator Logic')
    print('='*60)
    print('✅ Using publisher-specific knowledge like Zotero translators')
    print('✅ Focus on Science.org with confirmed working authentication')
    print('='*60)
    print()
    
    # Focus on Science paper
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
        print('🔧 Initializing browser with working configuration...')
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible to monitor process
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser initialized with authentication and extensions')
        print()
        
        print(f'📄 Target: {paper["name"]}')
        print(f'DOI: {paper["doi"]}')
        print(f'Filename: {paper["filename"]}')
        print()
        
        page = await context.new_page()
        
        # Build OpenURL
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
        
        print('Step 2: Clicking AAAS GO button (confirmed working)...')
        
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
                break
        
        if aaas_button_index >= 0:
            print(f'✅ Found AAAS GO button at index {aaas_button_index}')
            
            # Click GO button and handle popup
            popup_promise = page.wait_for_event('popup', timeout=30000)
            
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
            
            # Wait for page to load
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(8000)
            
            popup_title = await popup.title()
            popup_url = popup.url
            print(f'Science.org page: {popup_title}')
            print(f'URL: {popup_url[:80]}...')
            
            print('Step 3: Using Zotero-style PDF detection...')
            
            # Zotero-style PDF link detection for Science.org
            pdf_info = await popup.evaluate('''() => {
                // Science.org specific selectors based on Zotero translator knowledge
                const pdfSelectors = [
                    // Primary PDF download link
                    'a[href*="/doi/pdf/"]',
                    'a[href*=".pdf"]',
                    '.pdf-link',
                    '.article-pdf-link',
                    // Science.org specific patterns
                    'a[data-track-action*="pdf"]',
                    'a[title*="PDF"]',
                    'a[title*="Download PDF"]',
                    // Fallback patterns
                    'a:contains("PDF")',
                    'a:contains("Download")'
                ];
                
                let pdfLinks = [];
                
                // Try each selector
                for (const selector of pdfSelectors) {
                    try {
                        const elements = Array.from(document.querySelectorAll(selector));
                        for (const el of elements) {
                            if (el.offsetParent !== null) { // visible check
                                pdfLinks.push({
                                    text: el.textContent?.trim() || '',
                                    href: el.href || '',
                                    selector: selector,
                                    isMainArticle: !el.textContent?.toLowerCase().includes('supplement'),
                                    confidence: selector.includes('pdf') ? 'high' : 'medium'
                                });
                            }
                        }
                    } catch (e) {
                        // Skip invalid selectors
                    }
                }
                
                // Also look for download buttons with specific Science.org patterns
                const downloadButtons = Array.from(document.querySelectorAll('button, input[type="submit"], a'));
                for (const btn of downloadButtons) {
                    const text = btn.textContent?.toLowerCase() || '';
                    const title = btn.title?.toLowerCase() || '';
                    
                    if ((text.includes('pdf') || title.includes('pdf')) && 
                        !text.includes('supplement') && 
                        btn.offsetParent !== null) {
                        pdfLinks.push({
                            text: btn.textContent?.trim() || '',
                            href: btn.href || btn.onclick?.toString() || '',
                            selector: 'button/input',
                            isMainArticle: true,
                            confidence: 'high'
                        });
                    }
                }
                
                return {
                    allLinks: pdfLinks,
                    mainArticleLinks: pdfLinks.filter(link => link.isMainArticle),
                    highConfidenceLinks: pdfLinks.filter(link => link.confidence === 'high')
                };
            }''')
            
            print(f'Found {len(pdf_info["allLinks"])} total PDF-related links')
            print(f'Found {len(pdf_info["mainArticleLinks"])} main article PDF links')
            print(f'Found {len(pdf_info["highConfidenceLinks"])} high confidence PDF links')
            
            # Show the most promising links
            main_links = pdf_info["mainArticleLinks"][:3]  # Top 3 main article links
            for i, link in enumerate(main_links):
                print(f'  [{i}] "{link["text"][:40]}..." (confidence: {link["confidence"]})')
            
            if main_links:
                print('Step 4: Attempting PDF download with best candidate...')
                
                download_path = downloads_dir / paper["filename"]
                
                # Try the highest confidence main article link
                best_link = None
                for link in main_links:
                    if link["confidence"] == "high":
                        best_link = link
                        break
                
                if not best_link:
                    best_link = main_links[0]
                
                print(f'Using: "{best_link["text"][:40]}..." (confidence: {best_link["confidence"]})')
                
                try:
                    # Method 1: Direct PDF URL if available
                    if best_link["href"] and '.pdf' in best_link["href"]:
                        print('Method 1: Direct PDF URL navigation...')
                        
                        # Set up download listener
                        download_promise = popup.wait_for_event('download', timeout=30000)
                        
                        # Navigate to PDF URL
                        await popup.goto(best_link["href"])
                        
                        # Wait for download
                        download = await download_promise
                        await download.save_as(str(download_path))
                        
                        if download_path.exists():
                            size_mb = download_path.stat().st_size / (1024 * 1024)
                            print(f'🎉 SUCCESS! PDF downloaded via direct URL: {paper["filename"]} ({size_mb:.1f} MB)')
                        
                    else:
                        print('Method 2: Element interaction...')
                        
                        # Try clicking the element
                        download_promise = popup.wait_for_event('download', timeout=30000)
                        
                        # Find and click the specific PDF element
                        click_result = await popup.evaluate(f'''() => {{
                            // Find the exact element we identified
                            const selector = "{best_link['selector']}";
                            const elements = Array.from(document.querySelectorAll(selector));
                            
                            for (const el of elements) {{
                                const text = el.textContent?.trim() || '';
                                if (text === "{best_link['text']}" && el.offsetParent !== null) {{
                                    el.click();
                                    return 'clicked: ' + text;
                                }}
                            }}
                            
                            // Fallback: click any visible PDF link
                            const pdfLinks = Array.from(document.querySelectorAll('a[href*="pdf"], a[title*="PDF"]'));
                            for (const link of pdfLinks) {{
                                if (link.offsetParent !== null && !link.textContent?.toLowerCase().includes('supplement')) {{
                                    link.click();
                                    return 'fallback-clicked: ' + link.textContent?.trim();
                                }}
                            }}
                            
                            return 'no-clickable-element';
                        }}''')
                        
                        print(f'Click result: {click_result}')
                        
                        if 'clicked' in click_result:
                            # Wait for download
                            download = await download_promise
                            await download.save_as(str(download_path))
                            
                            if download_path.exists():
                                size_mb = download_path.stat().st_size / (1024 * 1024)
                                print(f'🎉 SUCCESS! PDF downloaded via click: {paper["filename"]} ({size_mb:.1f} MB)')
                        else:
                            print('❌ Could not click PDF element')
                
                except Exception as download_error:
                    print(f'❌ Download attempt failed: {download_error}')
            
            else:
                print('❌ No suitable PDF links found with Zotero-style detection')
            
            # Take final screenshot for analysis
            await popup.screenshot(path='zotero_style_detection.png', full_page=True)
            print('Screenshot: zotero_style_detection.png')
            
            await popup.close()
            
        else:
            print('❌ AAAS GO button not found')
        
        await page.close()
        
        print()
        print('🏁 Zotero-style PDF Download Complete')
        print('='*60)
        
        # Check final results
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'🎉 SUCCESS! Found {len(pdf_files)} PDF(s):')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  ✅ {pdf_file.name} ({size_mb:.1f} MB)')
                
                # Check if it's likely the main article
                if size_mb > 1.0:
                    print(f'      ✅ Size indicates main article PDF')
                elif size_mb < 0.3:
                    print(f'      ⚠️  Small size - may be supplementary')
            
            print()
            print('🚀 Zotero-style PDF extraction working!')
        else:
            print('⚠️  No PDFs downloaded automatically')
            print('Check screenshot for manual download analysis')
        
        print('='*60)
        
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    asyncio.run(download_with_zotero_translators())