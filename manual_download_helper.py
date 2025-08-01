#!/usr/bin/env python3
"""
Manual download helper - opens papers in browser for manual PDF download.

This script provides a more human-like approach by:
1. Opening the OpenURL resolver pages manually
2. Letting the user click GO buttons manually  
3. Avoiding automated popup handling that triggers bot detection
4. Providing clear instructions for manual PDF download
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def manual_download_helper():
    print('🎯 Manual PDF Download Helper')
    print('='*60)
    print('This script opens the papers in a browser for manual download.')
    print('This avoids bot detection by eliminating automated popup handling.')
    print('='*60)
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
            "suggested_filename": "Norimoto-2018-Science-Hippocampal_ripples.pdf"
        },
        {
            "name": "Nature - MRI brain development",
            "doi": "10.1038/s41593-025-01990-7",
            "title": "Addressing artifactual bias in large, automated MRI analyses of brain development",
            "journal": "Nature Neuroscience", 
            "year": 2025,
            "suggested_filename": "Author-2025-NatureNeuroscience-MRI_brain_development.pdf"
        }
    ]
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    try:
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Must be visible for manual interaction
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser opened with authenticated session and extensions loaded')
        print('✅ All 14 extensions should be available')
        print()
        
        for i, paper in enumerate(papers, 1):
            print(f'📄 Paper {i}/2: {paper["name"]}')
            print(f'DOI: {paper["doi"]}')
            print(f'Suggested filename: {paper["suggested_filename"]}')
            print()
            
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
            
            resolver_url = os.environ.get("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                                        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
            openurl = f"{resolver_url}?{urlencode(params, safe=':/')}"
            
            # Open the OpenURL resolver page
            page = await context.new_page()
            await page.goto(openurl, timeout=60000)
            await page.wait_for_timeout(2000)
            
            print(f'✅ Opened OpenURL resolver page in new tab')
            print(f'URL: {openurl[:80]}...')
            print()
            
            print('📋 MANUAL INSTRUCTIONS:')
            print('=' * 40)
            
            if i == 1:  # Science paper
                print('1. Look for "American Association for the Advancement of Science" row')
                print('2. Click the "Go" button in that row (usually around button #39)')
                print('3. If Cloudflare challenge appears, wait for 2Captcha extension to solve it')
                print('4. Once on Science.org, look for "Download PDF" link')
                print('5. Right-click "Download PDF" → Save Link As...')
                print(f'6. Save as: {paper["suggested_filename"]}')
            else:  # Nature paper
                print('1. Look for "Nature" or "Springer" row')
                print('2. Click the "Go" button in that row')
                print('3. If Cloudflare challenge appears, wait for 2Captcha extension to solve it')
                print('4. Once on Nature.com, look for PDF download options')
                print('5. Click PDF download link or right-click → Save Link As...')
                print(f'6. Save as: {paper["suggested_filename"]}')
            
            print()
            print('💡 TIPS:')
            print('- If you see Cloudflare "Verify you are human", wait ~30 seconds')
            print('- The 2Captcha extension should solve it automatically')
            print('- If challenge persists, you may need to solve it manually')
            print('- Lean Library extension may show institutional access options')
            print('- Save PDFs to the downloads/ directory')
            print()
            
            input(f'Press Enter when you have downloaded the PDF for paper {i}/2...')
            print()
        
        print('🎉 Manual Download Process Complete!')
        print('='*60)
        
        # Check what was downloaded
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'📁 Found {len(pdf_files)} PDF files in downloads directory:')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  ✅ {pdf_file.name} ({size_mb:.1f} MB)')
            print()
            print('🚀 SUCCESS! PDFs downloaded successfully.')
        else:
            print('📁 No PDF files found in downloads directory.')
            print('Make sure to save PDFs to the downloads/ folder.')
        
        print('='*60)
        print()
        
        input('Press Enter to close browser...')
        await manager.__aexit__(None, None, None)
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    os.environ["SCITEX_SCHOLAR_ZOTERO_TRANSLATORS_DIR"] = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/zotero_translators/"
    
    asyncio.run(manual_download_helper())