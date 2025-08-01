#!/usr/bin/env python3
"""
Simple paper opener - just opens the papers for manual download.

This completely eliminates automation detection by:
1. Just opening the URLs in tabs
2. No automation, no clicking, no waiting for events
3. Let extensions and user handle everything manually
4. Maximum compatibility with all browser extensions
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')
from scitex.scholar.browser.local._BrowserManager import BrowserManager
from scitex.scholar.auth._AuthenticationManager import AuthenticationManager

async def simple_paper_opener():
    print('🎯 Simple Paper Opener')
    print('='*50) 
    print('Opens papers in browser tabs for manual download.')
    print('Zero automation = Zero bot detection.')
    print('='*50)
    print()
    
    # Papers with their OpenURL resolver links
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
        print('🔧 Initializing authenticated browser...')
        auth_manager = AuthenticationManager()
        
        manager = BrowserManager(
            headless=False,  # Visible
            profile_name='scholar_default',
            auth_manager=auth_manager
        )
        
        browser, context = await manager.get_authenticated_context()
        
        print('✅ Browser ready with:')
        print('  - OpenAthens authentication active')
        print('  - All 14 extensions loaded')
        print('  - Scholar profile with institutional access')
        print()
        
        # Build OpenURL for each paper and open in tabs
        resolver_base = os.environ.get("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
                                     "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
        
        paper_urls = []
        
        for paper in papers:
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
            
            openurl = f"{resolver_base}?{urlencode(params, safe=':/')}"
            paper_urls.append((paper, openurl))
        
        print('📂 Opening papers in separate tabs...')
        print()
        
        for i, (paper, url) in enumerate(paper_urls, 1):
            print(f'Tab {i}: {paper["name"]}')
            print(f'  DOI: {paper["doi"]}')
            print(f'  Suggested filename: {paper["filename"]}')
            
            # Simply open in a new tab - no automation
            page = await context.new_page()
            await page.goto(url)
            
            print(f'  ✅ Opened in tab')
            print()
        
        print('🎯 MANUAL DOWNLOAD INSTRUCTIONS')
        print('='*50)
        print()
        print('For each tab:')
        print('1. Find the appropriate publisher GO button:')
        print('   - Science paper: Look for "American Association..." → Click GO')
        print('   - Nature paper: Look for "Nature" or "Springer" → Click GO')
        print()
        print('2. If Cloudflare challenge appears:')
        print('   - Wait for 2Captcha extension to solve automatically (~30 sec)')
        print('   - Or solve manually if needed')
        print()
        print('3. On publisher site:')
        print('   - Look for "Download PDF" or "PDF" links')
        print('   - Right-click → Save Link As...')
        print('   - Save to downloads/ directory with suggested filename')
        print()
        print('4. Extensions should help:')
        print('   - Lean Library: Shows institutional access')
        print('   - Zotero: May offer direct save options')
        print('   - Cookie Acceptor: Handles cookie banners')
        print()
        
        print('💡 ADVANTAGES OF THIS APPROACH:')
        print('- No automation detection')
        print('- Extensions work normally')
        print('- Manual control over timing')
        print('- Can handle any challenges manually')
        print('- Real human browsing behavior')
        print()
        
        input('Download the PDFs manually, then press Enter when done...')
        
        print()
        print('📁 Checking downloads directory...')
        
        pdf_files = list(downloads_dir.glob("*.pdf"))
        if pdf_files:
            print(f'✅ Found {len(pdf_files)} PDF files:')
            for pdf_file in pdf_files:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f'  - {pdf_file.name} ({size_mb:.1f} MB)')
            print()
            print('🎉 SUCCESS! Papers downloaded successfully!')
        else:
            print('❌ No PDF files found in downloads/ directory')
            print('Make sure you saved the PDFs to the downloads folder.')
        
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
    
    asyncio.run(simple_paper_opener())