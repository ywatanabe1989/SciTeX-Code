#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

# Set the environment variables
os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def download_science_pdf():
    # Science paper info
    doi = "10.1126/science.aao0702"
    title = "Hippocampal ripples down-regulate synapses"
    journal = "Science"
    year = 2018
    volume = 359
    issue = 6383
    pages = "1524-1527"
    filename = "Norimoto-2018-Science-Hippocampal_ripples.pdf"
    
    print('🎯 Downloading Science paper PDF using known working method...')
    print(f'Article: {title}')
    print(f'DOI: {doi}')
    print(f'Target: {filename}')
    print()
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    try:
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible to see download process
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        page = await context.new_page()
        
        # Build OpenURL manually (same as our successful test)
        from urllib.parse import urlencode
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
            "rft.atitle": title,
            "rft.jtitle": journal,
            "rft.date": str(year),
            "rft.volume": str(volume),
            "rft.issue": str(issue),
            "rft.spage": "1524",
            "rft.epage": "1527",
            "rft.doi": doi
        }
        
        resolver_url = os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"]
        openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
        
        print('Step 1: Loading OpenURL resolver...')
        await page.goto(openurl, timeout=60000)
        await page.wait_for_timeout(3000)
        
        print('Step 2: Finding AAAS GO button (element 39 method)...')
        
        # Use our proven method - find all elements and get the 39th (AAAS button)
        all_elements = await page.evaluate('''() => {
            const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
            return allElements.map((el, index) => ({
                index: index,
                tag: el.tagName,
                type: el.type || 'none',
                value: el.value || 'none',
                text: el.textContent?.trim() || 'none'
            }));
        }''')
        
        # Look for AAAS GO button (should be around index 39)
        aaas_button_index = -1
        for elem in all_elements:
            if (elem['value'] == 'Go' and 
                elem['index'] >= 35 and elem['index'] <= 45):  # Around where AAAS button should be
                aaas_button_index = elem['index']
                print(f'✅ Found AAAS GO button at index {aaas_button_index}')
                break
        
        if aaas_button_index >= 0:
            print('Step 3: Clicking AAAS GO button and accessing Science.org...')
            
            # Handle popup and click AAAS button
            popup_promise = page.wait_for_event('popup', timeout=30000)
            
            await page.evaluate(f'''() => {{
                const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                const targetButton = allElements[{aaas_button_index}];
                if (targetButton && targetButton.value === 'Go') {{
                    console.log('Clicking AAAS GO button:', targetButton);
                    targetButton.click();
                    return 'clicked';
                }}
                return 'not-found';
            }}''')
            
            popup = await popup_promise
            print('✅ Science.org popup opened!')
            
            # Wait for Science.org page to load completely
            await popup.wait_for_load_state('domcontentloaded', timeout=30000)
            await popup.wait_for_timeout(8000)
            
            popup_title = await popup.title()
            popup_url = popup.url
            print(f'Science page: {popup_title}')
            print(f'URL: {popup_url}')
            
            if 'science.org' in popup_url.lower():
                print('Step 4: Looking for PDF download links on Science.org...')
                
                # Look for PDF links on Science.org
                pdf_links = await popup.evaluate('''() => {
                    const allLinks = Array.from(document.querySelectorAll('a, button'));
                    return allLinks.filter(el => 
                        el.textContent.toLowerCase().includes('pdf') ||
                        el.href?.includes('pdf') ||
                        el.getAttribute('data-track-action')?.includes('pdf')
                    ).map(el => ({
                        tag: el.tagName,
                        text: el.textContent.trim(),
                        href: el.href || 'no-href',
                        className: el.className,
                        trackAction: el.getAttribute('data-track-action') || 'none'
                    }));
                }''')
                
                print(f'Found {len(pdf_links)} PDF-related links:')
                for i, link in enumerate(pdf_links):
                    print(f'  [{i}] {link["tag"]}: "{link["text"]}" | {link["href"][:60]}...')
                
                # Try to download PDF
                pdf_downloaded = False
                download_path = downloads_dir / filename
                
                if pdf_links:
                    # Try the most promising PDF link
                    main_pdf_link = None
                    
                    # Look for direct PDF download link
                    for link in pdf_links:
                        if 'download pdf' in link["text"].lower():
                            main_pdf_link = link
                            break
                        elif link["href"] != 'no-href' and '.pdf' in link["href"]:
                            main_pdf_link = link
                            break
                    
                    # Fallback to first PDF link
                    if not main_pdf_link and pdf_links:
                        main_pdf_link = pdf_links[0]
                    
                    if main_pdf_link:
                        print(f'Step 5: Attempting PDF download...')
                        print(f'Target link: {main_pdf_link["text"][:50]}...')
                        print(f'URL: {main_pdf_link["href"][:80]}...')
                        
                        try:
                            # Set up download listener
                            download_promise = popup.wait_for_event('download', timeout=30000)
                            
                            # Try direct navigation to PDF URL if it's a direct PDF link
                            if main_pdf_link["href"] != 'no-href' and '.pdf' in main_pdf_link["href"]:
                                print('Trying direct PDF URL navigation...')
                                await popup.goto(main_pdf_link["href"])
                            else:
                                print('Trying click-based download...')
                                # Click the PDF link
                                await popup.evaluate(f'''() => {{
                                    const allLinks = Array.from(document.querySelectorAll('a, button'));
                                    const pdfLinks = allLinks.filter(el => 
                                        el.textContent.toLowerCase().includes('pdf') ||
                                        el.href?.includes('pdf')
                                    );
                                    if (pdfLinks.length > 0) {{
                                        pdfLinks[0].click();
                                        return 'clicked';
                                    }}
                                    return 'no-link';
                                }}''')
                            
                            # Wait for download
                            download = await download_promise
                            await download.save_as(str(download_path))
                            
                            print(f'✅ SUCCESS! PDF downloaded: {download_path}')
                            
                            # Check file size
                            if download_path.exists():
                                size_mb = download_path.stat().st_size / (1024 * 1024)
                                print(f'File size: {size_mb:.1f} MB')
                                pdf_downloaded = True
                            
                        except Exception as download_error:
                            print(f'Download attempt failed: {download_error}')
                
                if not pdf_downloaded:
                    print('⚠️  Automatic PDF download failed')
                    print('Taking screenshot for manual inspection...')
                    await popup.screenshot(path='science_pdf_page.png', full_page=True)
                    print('Screenshot saved: science_pdf_page.png')
                    
                    print('\\nManual download options visible:')
                    for i, link in enumerate(pdf_links):
                        print(f'  Option {i+1}: {link["text"]}')
                
            else:
                print(f'❌ Did not reach Science.org: {popup_url}')
            
            await popup.close()
        
        else:
            print('❌ AAAS GO button not found')
            await page.screenshot(path='openurl_debug.png', full_page=True)
            print('Debug screenshot: openurl_debug.png')
        
        print('\\n' + '='*60)
        print('SCIENCE PDF DOWNLOAD TEST COMPLETE')
        print('='*60)
        
        # Check if PDF was downloaded
        download_path = downloads_dir / filename
        if download_path.exists():
            size_mb = download_path.stat().st_size / (1024 * 1024)
            print(f'✅ SUCCESS: {filename} ({size_mb:.1f} MB)')
        else:
            print('❌ PDF not downloaded automatically')
            print('Check screenshots for manual download options')
        
        print('='*60)
        
        input('\\nPress Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(download_science_pdf())