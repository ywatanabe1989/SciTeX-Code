#!/usr/bin/env python3
"""
PDF download script with enhanced Cloudflare/CAPTCHA handling.

This script handles the Cloudflare security challenge that's preventing 
PDF downloads from Science.org and Nature.com.
"""
import asyncio
import sys
import os
from pathlib import Path

# Set environment variables
os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def download_with_captcha_handling():
    print('🎯 Downloading PDFs with enhanced Cloudflare/CAPTCHA handling...')
    print('📋 Strategy: Use 2Captcha extension + longer wait times')
    print()
    
    # Test papers
    papers = [
        {
            "name": "Science - Hippocampal ripples",
            "doi": "10.1126/science.aao0702",
            "title": "Hippocampal ripples down-regulate synapses",
            "journal": "Science",
            "year": 2018,
            "volume": 359,
            "issue": 6383,
            "pages": "1524-1527",
            "filename": "Norimoto-2018-Science-Hippocampal_ripples.pdf"
        },
        {
            "name": "Nature - MRI brain development",
            "doi": "10.1038/s41593-025-01990-7", 
            "title": "Addressing artifactual bias in large, automated MRI analyses of brain development",
            "journal": "Nature Neuroscience",
            "year": 2025,
            "filename": "Author-2025-NatureNeuroscience-MRI_brain_development.pdf"
        }
    ]
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    try:
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible for CAPTCHA handling
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        for i, paper in enumerate(papers, 1):
            print(f'📄 Paper {i}/2: {paper["name"]}')
            print(f'DOI: {paper["doi"]}')
            print(f'Target: {paper["filename"]}')
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
                "rft.doi": paper["doi"]
            }
            
            if paper.get("volume"):
                params["rft.volume"] = str(paper["volume"])
            if paper.get("issue"):
                params["rft.issue"] = str(paper["issue"])
            if paper.get("pages"):
                pages = paper["pages"].split("-")
                params["rft.spage"] = pages[0]
                if len(pages) > 1:
                    params["rft.epage"] = pages[1]
            
            resolver_url = os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"]
            openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
            
            print('Step 1: Loading OpenURL resolver...')
            await page.goto(openurl, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Take screenshot of resolver page
            await page.screenshot(path=f'resolver_page_{i}.png', full_page=True)
            print(f'Screenshot saved: resolver_page_{i}.png')
            
            # Find and click GO button using our proven method
            print('Step 2: Finding GO buttons...')
            
            all_elements = await page.evaluate('''() => {
                const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                return allElements.map((el, index) => ({
                    index: index,
                    tag: el.tagName,
                    type: el.type || 'none',
                    value: el.value || 'none',
                    text: el.textContent?.trim().substring(0, 50) || 'none'
                }));
            }''')
            
            # Look for GO buttons around index 35-45 (where AAAS/Nature buttons typically are)
            go_button_index = -1
            for elem in all_elements:
                if (elem['value'] == 'Go' and 
                    elem['index'] >= 30 and elem['index'] <= 50):
                    go_button_index = elem['index']
                    print(f'✅ Found GO button at index {go_button_index}')
                    break
            
            if go_button_index >= 0:
                print('Step 3: Clicking GO button...')
                
                # Set up popup listener
                popup_promise = page.wait_for_event('popup', timeout=30000)
                
                # Click the GO button
                await page.evaluate(f'''() => {{
                    const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                    const targetButton = allElements[{go_button_index}];
                    if (targetButton && targetButton.value === 'Go') {{
                        console.log('Clicking GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}''')
                
                try:
                    popup = await popup_promise
                    print('✅ Publisher popup opened!')
                    
                    # Wait for popup to load
                    await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                    
                    # Check if we hit Cloudflare challenge
                    current_url = popup.url
                    page_content = await popup.content()
                    
                    if 'cloudflare' in page_content.lower() or 'verify you are human' in page_content.lower():
                        print('🔒 Detected Cloudflare challenge - waiting for 2Captcha extension...')
                        await popup.screenshot(path=f'cloudflare_challenge_{i}.png', full_page=True)
                        print(f'Challenge screenshot: cloudflare_challenge_{i}.png')
                        
                        # Wait longer for 2Captcha extension to handle it
                        print('⏳ Waiting 60 seconds for automatic CAPTCHA solving...')
                        await popup.wait_for_timeout(60000)
                        
                        # Check if challenge was solved
                        new_url = popup.url
                        new_content = await popup.content()
                        
                        if new_url != current_url or 'cloudflare' not in new_content.lower():
                            print('✅ Cloudflare challenge appears to be solved!')
                            await popup.screenshot(path=f'post_challenge_{i}.png', full_page=True)
                        else:
                            print('⚠️  Challenge may still be active - continuing anyway...')
                    
                    # Wait a bit more for page to stabilize
                    await popup.wait_for_timeout(10000)
                    
                    final_url = popup.url
                    popup_title = await popup.title()
                    print(f'Final page: {popup_title}')
                    print(f'URL: {final_url}')
                    
                    # Take screenshot of final page
                    await popup.screenshot(path=f'final_page_{i}.png', full_page=True)
                    print(f'Final page screenshot: final_page_{i}.png')
                    
                    # Look for PDF download options
                    print('Step 4: Looking for PDF download links...')
                    
                    pdf_elements = await popup.evaluate('''() => {
                        const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                        return allLinks.filter(el => 
                            el.textContent.toLowerCase().includes('pdf') ||
                            el.textContent.toLowerCase().includes('download') ||
                            el.href?.includes('pdf')
                        ).map((el, index) => ({
                            index: index,
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0, 50),
                            href: (el.href || el.value || 'no-href').substring(0, 80),
                            visible: el.offsetParent !== null
                        }));
                    }''')
                    
                    visible_pdf_elements = [el for el in pdf_elements if el['visible']]
                    print(f'Found {len(visible_pdf_elements)} visible PDF-related elements:')
                    
                    for j, elem in enumerate(visible_pdf_elements):
                        print(f'  [{j}] {elem["tag"]}: "{elem["text"]}" | {elem["href"]}')
                    
                    if visible_pdf_elements:
                        print('Step 5: Attempting PDF download...')
                        
                        # Try to download the most promising PDF link
                        download_path = downloads_dir / paper["filename"]
                        
                        try:
                            # Set up download listener
                            download_promise = popup.wait_for_event('download', timeout=30000)
                            
                            # Try clicking the first visible PDF element
                            first_pdf = visible_pdf_elements[0]
                            print(f'Clicking: {first_pdf["text"]}')
                            
                            # If it has a direct PDF href, navigate to it
                            if first_pdf["href"] != 'no-href' and '.pdf' in first_pdf["href"]:
                                await popup.goto(first_pdf["href"])
                            else:
                                # Click the element
                                await popup.evaluate(f'''() => {{
                                    const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                                    const pdfLinks = allLinks.filter(el => 
                                        el.textContent.toLowerCase().includes('pdf') ||
                                        el.textContent.toLowerCase().includes('download') ||
                                        el.href?.includes('pdf')
                                    );
                                    const visiblePdfLinks = pdfLinks.filter(el => el.offsetParent !== null);
                                    if (visiblePdfLinks.length > 0) {{
                                        visiblePdfLinks[0].click();
                                        return 'clicked';
                                    }}
                                    return 'no-visible-links';
                                }}''')
                            
                            # Wait for download
                            download = await download_promise
                            await download.save_as(str(download_path))
                            
                            if download_path.exists():
                                size_mb = download_path.stat().st_size / (1024 * 1024)
                                print(f'✅ SUCCESS! PDF downloaded: {paper["filename"]} ({size_mb:.1f} MB)')
                            else:
                                print('❌ Download failed - file not found')
                                
                        except Exception as download_error:
                            print(f'❌ Download failed: {download_error}')
                            print('Manual download may be required')
                    
                    else:
                        print('❌ No visible PDF download elements found')
                    
                    await popup.close()
                    
                except Exception as popup_error:
                    print(f'❌ Popup handling failed: {popup_error}')
            
            else:
                print('❌ No GO button found in expected range')
                
            await page.close()
            print()
            print('-' * 60)
            print()
        
        print('🏁 PDF DOWNLOAD ATTEMPT COMPLETED')
        print('='*60)
        
        # List any downloaded files
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'📁 Downloaded PDFs ({len(pdf_files)}):')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  - {pdf_file.name} ({size_mb:.1f} MB)')
        else:
            print('📁 No PDFs downloaded automatically')
            print('Check screenshots for debugging and manual download options')
        
        print('='*60)
        
        input('Press Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(download_with_captcha_handling())