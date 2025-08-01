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

async def download_papers_pdf():
    print('🎯 Downloading PDFs for both successfully accessed papers...')
    print()
    
    # Paper metadata
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
            "volume": None,
            "issue": None,
            "pages": None,
            "filename": "Author-2025-NatureNeuroscience-MRI_brain_development.pdf"
        }
    ]
    
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
        
        for i, paper in enumerate(papers, 1):
            print(f'📄 Paper {i}/2: {paper["name"]}')
            print(f'DOI: {paper["doi"]}')
            print(f'Target filename: {paper["filename"]}')
            print()
            
            page = await context.new_page()
            
            # Build OpenURL for the paper
            from urllib.parse import urlencode
            params = {
                "ctx_ver": "Z39.88-2004",
                "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
                "rft.genre": "article",
                "rft.atitle": paper["title"],
                "rft.jtitle": paper["journal"],
                "rft.date": str(paper["year"]),
                "rft_id": f"info:doi/{paper['doi']}",
                "url_ver": "Z39.88-2004"
            }
            
            if paper["volume"]:
                params["rft.volume"] = str(paper["volume"])
            if paper["issue"]:
                params["rft.issue"] = str(paper["issue"])
            if paper["pages"]:
                params["rft.spage"] = paper["pages"].split("-")[0]
                params["rft.epage"] = paper["pages"].split("-")[1]
            
            resolver_url = os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"]
            openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
            
            print(f'Step 1: Loading OpenURL resolver...')
            await page.goto(openurl, timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Find the appropriate GO button
            go_buttons = await page.evaluate('''() => {
                const goButtons = Array.from(document.querySelectorAll('input[value="Go"]'));
                return goButtons.map((btn, index) => {
                    const parentRow = btn.closest('tr') || btn.parentElement;
                    const rowText = parentRow ? parentRow.textContent.trim() : '';
                    return {
                        index: index,
                        value: btn.value,
                        rowText: rowText,
                        isPublisher: rowText.toLowerCase().includes('nature') || 
                                   rowText.toLowerCase().includes('american association') ||
                                   rowText.toLowerCase().includes('science')
                    };
                });
            }''')
            
            publisher_button_index = -1
            for j, btn in enumerate(go_buttons):
                if btn["isPublisher"]:
                    publisher_button_index = j
                    print(f'✅ Found publisher GO button: {btn["rowText"][:50]}...')
                    break
            
            if publisher_button_index >= 0:
                print(f'Step 2: Clicking publisher GO button...')
                
                # Handle popup and click the publisher GO button
                popup_promise = page.wait_for_event('popup', timeout=30000)
                
                await page.evaluate(f'''() => {{
                    const goButtons = Array.from(document.querySelectorAll('input[value="Go"]'));
                    const targetButton = goButtons[{publisher_button_index}];
                    if (targetButton) {{
                        console.log('Clicking publisher GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}''')
                
                popup = await popup_promise
                print('✅ Publisher page opened!')
                
                # Wait for popup to load completely
                await popup.wait_for_load_state('domcontentloaded', timeout=30000)
                await popup.wait_for_timeout(8000)
                
                popup_title = await popup.title()
                popup_url = popup.url
                print(f'Publisher page: {popup_title}')
                print(f'URL: {popup_url}')
                
                # Look for PDF download links
                print(f'Step 3: Looking for PDF download options...')
                
                pdf_links = await popup.evaluate('''() => {
                    const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                    return allLinks.filter(el => 
                        el.textContent.toLowerCase().includes('pdf') ||
                        el.textContent.toLowerCase().includes('download') ||
                        el.href?.includes('pdf') ||
                        el.getAttribute('data-track-action')?.includes('pdf')
                    ).map(el => ({
                        tag: el.tagName,
                        text: el.textContent.trim(),
                        href: el.href || el.value || 'no-href',
                        className: el.className,
                        id: el.id,
                        trackAction: el.getAttribute('data-track-action') || 'none'
                    }));
                }''')
                
                print(f'Found {len(pdf_links)} potential PDF links:')
                for link in pdf_links:
                    print(f'  - {link["tag"]}: "{link["text"][:50]}" | {link["href"][:50]}...')
                
                # Try to find and click the main PDF download link
                pdf_downloaded = False
                
                if pdf_links:
                    # Look for the most likely PDF download link
                    main_pdf_link = None
                    
                    # Priority order: direct PDF links, download buttons, view PDF
                    for link in pdf_links:
                        if 'download pdf' in link["text"].lower():
                            main_pdf_link = link
                            break
                        elif link["href"] != 'no-href' and link["href"].endswith('.pdf'):
                            main_pdf_link = link
                            break
                        elif 'pdf' in link["text"].lower() and 'view' not in link["text"].lower():
                            main_pdf_link = link
                            break
                    
                    if not main_pdf_link and pdf_links:
                        main_pdf_link = pdf_links[0]  # Fallback to first PDF-related link
                    
                    if main_pdf_link:
                        print(f'Step 4: Attempting to download PDF...')
                        print(f'Target: {main_pdf_link["text"][:50]}...')
                        
                        # Set up download path
                        download_path = downloads_dir / paper["filename"]
                        
                        # Configure download behavior
                        await popup.set_extra_http_headers({
                            'Accept': 'application/pdf,application/octet-stream,*/*'
                        })
                        
                        try:
                            # Method 1: Try direct navigation to PDF URL
                            if main_pdf_link["href"] != 'no-href' and 'pdf' in main_pdf_link["href"].lower():
                                print('Trying direct PDF URL download...')
                                
                                # Listen for download
                                download_promise = popup.wait_for_event('download', timeout=30000)
                                
                                await popup.goto(main_pdf_link["href"])
                                
                                try:
                                    download = await download_promise
                                    await download.save_as(str(download_path))
                                    print(f'✅ PDF downloaded successfully: {download_path}')
                                    pdf_downloaded = True
                                except:
                                    print('Direct download failed, trying click method...')
                            
                            # Method 2: Try clicking the PDF link
                            if not pdf_downloaded:
                                print('Trying click-based PDF download...')
                                
                                download_promise = popup.wait_for_event('download', timeout=30000)
                                
                                # Find and click the PDF element
                                await popup.evaluate(f'''() => {{
                                    const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                                    const pdfLinks = allLinks.filter(el => 
                                        el.textContent.toLowerCase().includes('pdf') ||
                                        el.textContent.toLowerCase().includes('download') ||
                                        el.href?.includes('pdf')
                                    );
                                    if (pdfLinks.length > 0) {{
                                        pdfLinks[0].click();
                                        return 'clicked';
                                    }}
                                    return 'no-link';
                                }}''')
                                
                                try:
                                    download = await download_promise
                                    await download.save_as(str(download_path))
                                    print(f'✅ PDF downloaded successfully: {download_path}')
                                    pdf_downloaded = True
                                except:
                                    print('Click-based download failed')
                            
                        except Exception as download_error:
                            print(f'❌ Download failed: {download_error}')
                
                if not pdf_downloaded:
                    print(f'⚠️  Could not download PDF automatically for {paper["name"]}')
                    print('Taking screenshot for manual inspection...')
                    await popup.screenshot(path=f'pdf_download_failed_{i}.png', full_page=True)
                    print(f'Screenshot saved: pdf_download_failed_{i}.png')
                
                await popup.close()
                
            else:
                print(f'❌ No publisher GO button found for {paper["name"]}')
            
            await page.close()
            print()
        
        print('\\n' + '='*60)
        print('PDF DOWNLOAD TEST COMPLETE')
        print('='*60)
        print('Check the downloads/ directory for PDF files.')
        print('Screenshots saved for any failed downloads.')
        print('='*60)
        
        # List downloaded files
        downloaded_files = list(downloads_dir.glob("*.pdf"))
        if downloaded_files:
            print(f'\\n📁 Downloaded PDFs ({len(downloaded_files)}):')
            for pdf_file in downloaded_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  - {pdf_file.name} ({size_mb:.1f} MB)')
        else:
            print('\\n❌ No PDFs were downloaded automatically')
        
        input('\\nPress Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(download_papers_pdf())