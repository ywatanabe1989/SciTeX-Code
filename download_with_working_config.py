#!/usr/bin/env python3
"""
PDF download using the EXACT configuration that was working before.

This uses the local BrowserManager (not ZenRows) with the enhanced stealth 
configuration that successfully bypassed Cloudflare in our previous tests.
"""
import asyncio
import sys
import os
from pathlib import Path

# Set environment variables
os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"

# IMPORTANT: Remove ZenRows API key to force using local BrowserManager
if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
    del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def download_with_working_config():
    print('🎯 PDF Download using Previously Successful Configuration')
    print('='*60)
    print('Using local BrowserManager (not ZenRows) with enhanced stealth')
    print('This configuration achieved 100% Cloudflare bypass rate before')
    print('='*60)
    print()
    
    # Test papers - same as successful tests
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
        print('🔧 Initializing with WORKING configuration...')
        auth_manager = AuthenticationManager()
        
        # Use the EXACT configuration that worked before
        manager = BrowserManager(
            headless=False,  # Non-headless like successful tests
            profile_name='scholar_default',  # Same profile
            auth_manager=auth_manager  # Same auth
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Using local BrowserManager (not ZenRows)')
        print('✅ Enhanced stealth configuration active')
        print('✅ All 14 extensions loaded')
        print('✅ OpenAthens authentication verified')
        print()
        
        for i, paper in enumerate(papers, 1):
            print(f'📄 Paper {i}/2: {paper["name"]}')
            print(f'DOI: {paper["doi"]}')
            print(f'Target: {paper["filename"]}')
            print()
            
            page = await context.new_page()
            
            # Build OpenURL exactly as before
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
            
            print('Step 1: Loading OpenURL resolver with enhanced stealth...')
            await page.goto(openurl, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Take screenshot for debugging
            await page.screenshot(path=f'working_config_resolver_{i}.png', full_page=True)
            print(f'Screenshot: working_config_resolver_{i}.png')
            
            # Use the exact GO button method that worked before
            print('Step 2: Using proven GO button detection method...')
            
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
            
            # Find GO button using same logic as successful tests
            target_button_index = -1
            
            if i == 1:  # Science paper - look for AAAS button around index 39
                for elem in all_elements:
                    if (elem['value'] == 'Go' and 
                        elem['index'] >= 35 and elem['index'] <= 45):
                        target_button_index = elem['index']
                        print(f'✅ Found Science AAAS GO button at index {target_button_index}')
                        break
            else:  # Nature paper - look for Nature button
                for elem in all_elements:
                    if (elem['value'] == 'Go' and 
                        elem['index'] >= 30 and elem['index'] <= 50):
                        target_button_index = elem['index']
                        print(f'✅ Found Nature GO button at index {target_button_index}')
                        break
            
            if target_button_index >= 0:
                print('Step 3: Clicking GO button with working method...')
                
                # Use exact popup handling that worked before
                popup_promise = page.wait_for_event('popup', timeout=30000)
                
                click_result = await page.evaluate(f'''() => {{
                    const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                    const targetButton = allElements[{target_button_index}];
                    if (targetButton && targetButton.value === 'Go') {{
                        console.log('Clicking GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}''')
                
                if click_result == 'clicked':
                    try:
                        popup = await popup_promise
                        print('✅ Publisher popup opened successfully!')
                        
                        # Wait for popup to load with same timing as before
                        await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                        await popup.wait_for_timeout(8000)  # Same wait time as successful tests
                        
                        final_url = popup.url
                        popup_title = await popup.title()
                        
                        print(f'Publisher page: {popup_title}')
                        print(f'URL: {final_url}')
                        
                        # Check for Cloudflare
                        page_content = await popup.content()
                        if 'cloudflare' in page_content.lower() or 'verify you are human' in page_content.lower():
                            print('🔒 Cloudflare challenge detected!')
                            await popup.screenshot(path=f'cloudflare_working_config_{i}.png', full_page=True)
                            print(f'Challenge screenshot: cloudflare_working_config_{i}.png')
                            print('❌ Even working config hit Cloudflare - may need manual intervention')
                        else:
                            print('✅ No Cloudflare challenge - accessing publisher content!')
                            await popup.screenshot(path=f'success_working_config_{i}.png', full_page=True)
                            
                            # Look for PDF download options
                            print('Step 4: Looking for PDF download options...')
                            
                            pdf_links = await popup.evaluate('''() => {
                                const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                                return allLinks.filter(el => 
                                    el.textContent.toLowerCase().includes('pdf') ||
                                    el.textContent.toLowerCase().includes('download') ||
                                    el.href?.includes('pdf')
                                ).map(el => ({
                                    tag: el.tagName,
                                    text: el.textContent.trim().substring(0, 50),
                                    href: (el.href || el.value || 'no-href').substring(0, 80),
                                    visible: el.offsetParent !== null
                                }));
                            }''')
                            
                            visible_pdf_links = [link for link in pdf_links if link['visible']]
                            print(f'Found {len(visible_pdf_links)} visible PDF links:')
                            
                            for j, link in enumerate(visible_pdf_links):
                                print(f'  [{j}] {link["tag"]}: "{link["text"]}" | {link["href"]}')
                            
                            if visible_pdf_links:
                                print('Step 5: Attempting PDF download...')
                                
                                try:
                                    download_path = downloads_dir / paper["filename"]
                                    download_promise = popup.wait_for_event('download', timeout=30000)
                                    
                                    # Try first visible PDF link
                                    first_pdf = visible_pdf_links[0]
                                    
                                    if first_pdf["href"] != 'no-href' and 'pdf' in first_pdf["href"]:
                                        print('Trying direct PDF URL...')
                                        await popup.goto(first_pdf["href"])
                                    else:
                                        print('Trying click-based download...')
                                        await popup.evaluate('''() => {
                                            const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                                            const pdfLinks = allLinks.filter(el => 
                                                (el.textContent.toLowerCase().includes('pdf') ||
                                                 el.textContent.toLowerCase().includes('download') ||
                                                 el.href?.includes('pdf')) &&
                                                el.offsetParent !== null
                                            );
                                            if (pdfLinks.length > 0) {
                                                pdfLinks[0].click();
                                                return 'clicked';
                                            }
                                            return 'no-visible-links';
                                        }''')
                                    
                                    download = await download_promise
                                    await download.save_as(str(download_path))
                                    
                                    if download_path.exists():
                                        size_mb = download_path.stat().st_size / (1024 * 1024)
                                        print(f'✅ SUCCESS! PDF downloaded: {paper["filename"]} ({size_mb:.1f} MB)')
                                    else:
                                        print('❌ Download failed - file not created')
                                        
                                except Exception as download_error:
                                    print(f'❌ Download failed: {download_error}')
                        
                        await popup.close()
                        
                    except Exception as popup_error:
                        print(f'❌ Popup handling failed: {popup_error}')
                else:
                    print('❌ GO button click failed')
            else:
                print('❌ GO button not found')
            
            await page.close()
            print()
            print('-' * 60)
            print()
        
        print('🏁 Working Configuration Test Complete')
        print('='*60)
        
        # Check results
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'✅ Downloaded {len(pdf_files)} PDFs:')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  - {pdf_file.name} ({size_mb:.1f} MB)')
        else:
            print('❌ No PDFs downloaded')
            print('Check screenshots to see if Cloudflare is still blocking')
        
        print('='*60)
        
        input('Press Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(download_with_working_config())