#!/usr/bin/env python3
"""
Direct Science.org PDF download using Atypon/Science.org URL patterns.

Based on the Zotero Atypon Journals translator, Science.org articles
have predictable PDF URLs that we can construct directly.
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

async def download_science_pdf_direct():
    print('🎯 Direct Science.org PDF Download using Atypon URL Patterns')
    print('='*60)
    print('✅ Based on Zotero Atypon Journals translator knowledge')
    print('✅ Using predictable Science.org PDF URL structure')
    print('='*60)
    print()
    
    # Target paper
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
        print('🔧 Initializing browser with working authentication...')
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser initialized with authentication')
        print()
        
        print(f'📄 Target: {paper["name"]}')
        print(f'DOI: {paper["doi"]}')
        print(f'Filename: {paper["filename"]}')
        print()
        
        # Create page for PDF download
        pdf_page = await context.new_page()
        
        # Based on Zotero Atypon translator, Science.org PDF URLs follow this pattern:
        # https://www.science.org/doi/pdf/10.1126/science.XXXXX
        
        article_url = f"https://www.science.org/doi/{paper['doi']}"
        pdf_url = f"https://www.science.org/doi/pdf/{paper['doi']}"
        
        print(f'Article URL: {article_url}')
        print(f'Direct PDF URL: {pdf_url}')
        print()
        
        print('Step 1: Testing direct PDF URL access...')
        
        download_path = downloads_dir / paper["filename"]
        download_success = False
        
        try:
            # Method 1: Direct PDF URL navigation with download handling
            print('Attempting direct PDF download...')
            
            # Set up download event listener
            download_promise = pdf_page.wait_for_event('download', timeout=30000)
            
            # Navigate directly to PDF URL
            await pdf_page.goto(pdf_url, timeout=30000)
            
            try:
                # Wait for download event
                download = await download_promise
                await download.save_as(str(download_path))
                
                # Verify download
                if download_path.exists() and download_path.stat().st_size > 1000:
                    size_mb = download_path.stat().st_size / (1024 * 1024)
                    print(f'🎉 SUCCESS! Direct PDF downloaded: {paper["filename"]} ({size_mb:.1f} MB)')
                    download_success = True
                
            except Exception as download_wait_error:
                print(f'Download event failed: {download_wait_error}')
                
                # Check if PDF was displayed in browser instead of downloaded
                current_url = pdf_page.url
                page_content = await pdf_page.content()
                
                if 'application/pdf' in page_content or pdf_url in current_url:
                    print('✅ PDF loaded in browser - may need manual save')
                    
                    # Try to trigger download via JavaScript
                    try:
                        print('Attempting to trigger download via JavaScript...')
                        await pdf_page.evaluate(f'''() => {{
                            const link = document.createElement('a');
                            link.href = '{pdf_url}';
                            link.download = '{paper["filename"]}';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }}''')
                        
                        # Wait a bit for download to start
                        await pdf_page.wait_for_timeout(5000)
                        
                        if download_path.exists():
                            size_mb = download_path.stat().st_size / (1024 * 1024)
                            print(f'✅ JavaScript download succeeded: {paper["filename"]} ({size_mb:.1f} MB)')
                            download_success = True
                        
                    except Exception as js_error:
                        print(f'JavaScript download failed: {js_error}')
        
        except Exception as direct_error:
            print(f'Direct PDF access failed: {direct_error}')
        
        if not download_success:
            print('Method 2: Fallback to article page with PDF link detection...')
            
            # Navigate to article page first
            await pdf_page.goto(article_url, timeout=30000)
            await pdf_page.wait_for_timeout(3000)
            
            # Look for PDF download links on the article page
            pdf_links = await pdf_page.evaluate(f'''() => {{
                // Science.org specific PDF link selectors
                const selectors = [
                    'a[href*="/doi/pdf/{paper["doi"]}"]',
                    'a[href*="pdf"]',
                    'a[data-track-action*="pdf"]',
                    '.article-pdf-link',
                    '.pdf-download'
                ];
                
                let foundLinks = [];
                
                for (const selector of selectors) {{
                    try {{
                        const elements = Array.from(document.querySelectorAll(selector));
                        for (const el of elements) {{
                            if (el.offsetParent !== null) {{
                                foundLinks.push({{
                                    text: el.textContent?.trim() || '',
                                    href: el.href || '',
                                    selector: selector
                                }});
                            }}
                        }}
                    }} catch (e) {{
                        // Skip invalid selectors
                    }}
                }}
                
                return foundLinks;
            }}''')
            
            print(f'Found {len(pdf_links)} PDF links on article page:')
            for i, link in enumerate(pdf_links):
                print(f'  [{i}] "{link["text"][:40]}..." | {link["href"][:60]}...')
            
            if pdf_links:
                print('Trying first PDF link...')
                best_link = pdf_links[0]
                
                try:
                    download_promise = pdf_page.wait_for_event('download', timeout=20000)
                    
                    if best_link["href"]:
                        await pdf_page.goto(best_link["href"])
                    else:
                        # Click the link
                        await pdf_page.evaluate(f'''() => {{
                            const links = Array.from(document.querySelectorAll('a[href*="pdf"]'));
                            if (links.length > 0) {{
                                links[0].click();
                                return 'clicked';
                            }}
                            return 'no-link';
                        }}''')
                    
                    download = await download_promise
                    await download.save_as(str(download_path))
                    
                    if download_path.exists():
                        size_mb = download_path.stat().st_size / (1024 * 1024) 
                        print(f'✅ Fallback download succeeded: {paper["filename"]} ({size_mb:.1f} MB)')
                        download_success = True
                        
                except Exception as fallback_error:
                    print(f'Fallback download failed: {fallback_error}')
        
        # Take screenshot for analysis
        await pdf_page.screenshot(path='science_direct_pdf_attempt.png', full_page=True)
        print('Screenshot: science_direct_pdf_attempt.png')
        
        await pdf_page.close()
        
        print()
        print('🏁 Direct Science.org PDF Download Complete')
        print('='*60)
        
        # Final results
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'🎉 SUCCESS! Found {len(pdf_files)} PDF(s):')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  ✅ {pdf_file.name} ({size_mb:.1f} MB)')
                
                # Check if it looks like the main article
                if size_mb > 0.8:
                    print(f'      ✅ Good size for main article')
                else:
                    print(f'      ⚠️  Small size - check if complete')
            
            print()
            print('🚀 Direct PDF download approach working!')
        else:
            print('⚠️  No PDFs downloaded automatically')
            print('PDF may have opened in browser - check for manual save options')
        
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
    
    asyncio.run(download_science_pdf_direct())