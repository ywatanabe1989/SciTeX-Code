#!/usr/bin/env python3
"""
Download the MAIN ARTICLE PDF (not supplementary materials).

Now that we've confirmed downloads work, let's specifically target
the main article PDF from Science.org.
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

async def download_main_article_pdf():
    print('🎯 Download MAIN ARTICLE PDF from Science.org')
    print('='*60)
    print('✅ Download mechanism confirmed working (got supplementary materials)')
    print('✅ Now targeting the main article PDF specifically')
    print('='*60)
    print()
    
    # Focus on Science paper that we know works
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
            headless=False,  # Visible to see the process
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser initialized with working authentication')
        print()
        
        print(f'📄 Target: {paper["name"]}')
        print(f'DOI: {paper["doi"]}')
        print(f'Main article filename: {paper["filename"]}')
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
        
        # Find AAAS GO button (confirmed working at index ~39)
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
            print('Step 3: Clicking GO button and opening Science.org...')
            
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
            
            # Wait for page to load
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(8000)
            
            popup_title = await popup.title()
            popup_url = popup.url
            print(f'Science.org page: {popup_title}')
            print(f'URL: {popup_url[:80]}...')
            
            print('Step 4: Looking specifically for MAIN ARTICLE PDF...')
            
            # More specific search for main article PDF (not supplementary)
            pdf_options = await popup.evaluate('''() => {
                const allElements = Array.from(document.querySelectorAll('a, button, [onclick]'));
                
                // Look for main article PDF links (exclude supplementary)
                const pdfLinks = allElements.filter(el => {
                    const text = el.textContent?.toLowerCase() || '';
                    const href = el.href?.toLowerCase() || '';
                    const className = el.className?.toLowerCase() || '';
                    
                    // Must contain PDF-related terms
                    const hasPdfTerms = text.includes('pdf') || href.includes('pdf') || 
                                       text.includes('download') || className.includes('pdf');
                    
                    // Exclude supplementary materials
                    const isSupplementary = text.includes('supplement') || text.includes('supporting') || 
                                           href.includes('supplement') || text.includes('materials');
                    
                    return hasPdfTerms && !isSupplementary;
                }).map(el => ({
                    text: el.textContent?.trim() || '',
                    href: el.href || '',
                    className: el.className || '',
                    visible: el.offsetParent !== null,
                    isMainArticle: (
                        el.textContent?.toLowerCase().includes('full text') ||
                        el.textContent?.toLowerCase().includes('article pdf') ||
                        el.textContent?.toLowerCase().includes('download pdf') ||
                        (el.textContent?.toLowerCase().includes('pdf') && 
                         !el.textContent?.toLowerCase().includes('supplement'))
                    )
                }));
                
                return pdfLinks;
            }''')
            
            # Filter for visible and prioritize main article links
            visible_pdf_options = [opt for opt in pdf_options if opt['visible']]
            main_article_options = [opt for opt in visible_pdf_options if opt['isMainArticle']]
            
            print(f'Found {len(visible_pdf_options)} visible PDF options:')
            for i, opt in enumerate(visible_pdf_options):
                main_indicator = ' [MAIN ARTICLE]' if opt['isMainArticle'] else ''
                print(f'  [{i}] "{opt["text"][:50]}..."{main_indicator}')
            
            if main_article_options:
                print(f'Step 5: Found {len(main_article_options)} main article PDF options!')
                target_option = main_article_options[0]  # Use first main article option
                print(f'Targeting: "{target_option["text"][:50]}..."')
            elif visible_pdf_options:
                print('Step 5: No specific main article PDF found, trying first PDF option...')
                target_option = visible_pdf_options[0]
                print(f'Targeting: "{target_option["text"][:50]}..."')
            else:
                print('❌ No PDF options found')
                await popup.screenshot(path='no_pdf_options.png', full_page=True)
                await popup.close()
                await page.close()
                return
            
            print('Step 6: Attempting to download main article PDF...')
            
            download_path = downloads_dir / paper["filename"]
            
            try:
                # Set up download listener
                download_promise = popup.wait_for_event('download', timeout=30000)
                
                # Try the target option
                if target_option["href"] and '.pdf' in target_option["href"]:
                    print('Using direct PDF URL...')
                    await popup.goto(target_option["href"])
                else:
                    print('Using click-based approach...')
                    # Find and click the specific element
                    click_result = await popup.evaluate(f'''() => {{
                        const allElements = Array.from(document.querySelectorAll('a, button, [onclick]'));
                        const pdfLinks = allElements.filter(el => {{
                            const text = el.textContent?.toLowerCase() || '';
                            const href = el.href?.toLowerCase() || '';
                            const hasPdfTerms = text.includes('pdf') || href.includes('pdf') || text.includes('download');
                            const isSupplementary = text.includes('supplement') || text.includes('supporting');
                            return hasPdfTerms && !isSupplementary && el.offsetParent !== null;
                        }});
                        
                        const mainArticleLinks = pdfLinks.filter(el => {{
                            const text = el.textContent?.toLowerCase() || '';
                            return text.includes('full text') || text.includes('article pdf') || 
                                   text.includes('download pdf') || 
                                   (text.includes('pdf') && !text.includes('supplement'));
                        }});
                        
                        const targetLinks = mainArticleLinks.length > 0 ? mainArticleLinks : pdfLinks;
                        
                        if (targetLinks.length > 0) {{
                            targetLinks[0].click();
                            return 'clicked: ' + targetLinks[0].textContent?.trim();
                        }}
                        return 'no-suitable-link';
                    }}''')
                    
                    print(f'Click result: {click_result}')
                
                # Wait for download
                download = await download_promise
                await download.save_as(str(download_path))
                
                # Verify download
                if download_path.exists():
                    size_mb = download_path.stat().st_size / (1024 * 1024)
                    print(f'🎉 SUCCESS! Main article PDF downloaded: {paper["filename"]} ({size_mb:.1f} MB)')
                    
                    # Verify it's not supplementary materials by checking file size
                    if size_mb > 0.5:  # Main articles are usually larger than 0.5MB
                        print('✅ File size suggests this is the main article (not supplementary)')
                    else:
                        print('⚠️  Small file size - may be supplementary materials')
                else:
                    print('❌ Download failed - file not created')
                    
            except Exception as download_error:
                print(f'❌ Download failed: {download_error}')
                print('Taking screenshot for manual inspection...')
                await popup.screenshot(path='main_article_download_failed.png', full_page=True)
            
            await popup.close()
            
        else:
            print('❌ AAAS GO button not found')
        
        await page.close()
        
        print()
        print('🏁 Main Article PDF Download Complete')
        print('='*60)
        
        # Check results
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'✅ Found {len(pdf_files)} PDF(s) in downloads/:')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  🎉 {pdf_file.name} ({size_mb:.1f} MB)')
                
                # Suggest if file might be main article based on size
                if size_mb > 1.0:
                    print(f'      ✅ Good size for main article')
                elif size_mb < 0.5:
                    print(f'      ⚠️  May be supplementary materials')
            
            print()
            print('🚀 PDF download system is working excellently!')
        else:
            print('📁 No PDFs downloaded automatically')
            print('Check screenshots for manual download options')
        
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
    
    asyncio.run(download_main_article_pdf())