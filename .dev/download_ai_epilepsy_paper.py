#!/usr/bin/env python3
"""
Download: Artificial intelligence in epilepsy — applications and pathways to the clinic
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.scitex.scholar import Scholar, ScholarConfig
from src.scitex.scholar._PDFDownloader import PDFDownloader
from src.scitex.scholar._OpenURLResolver import OpenURLResolver

async def download_ai_epilepsy_paper():
    """Try multiple methods to download the AI epilepsy paper."""
    
    print("=" * 80)
    print("DOWNLOADING: Artificial intelligence in epilepsy")
    print("=" * 80)
    
    # First, search for the paper to get metadata
    config = ScholarConfig(
        pdf_dir="./.dev/pdfs_ai_epilepsy",
        enable_auto_download=False,
        enable_auto_enrich=False,
        acknowledge_scihub_ethical_usage=True,
        debug_mode=True
    )
    
    scholar = Scholar(config)
    
    # Search for the specific paper
    query = "Artificial intelligence in epilepsy applications and pathways to the clinic"
    print(f"\nSearching for: {query}")
    
    papers = scholar.search(
        query=query,
        limit=5,
        sources=["pubmed", "crossref"]
    )
    
    target_paper = None
    for paper in papers.papers:
        if "artificial intelligence" in paper.title.lower() and "epilepsy" in paper.title.lower():
            target_paper = paper
            break
    
    if not target_paper:
        print("❌ Could not find the specific paper via search")
        print("\nTrying manual metadata...")
        # Create manual metadata
        target_paper = type('Paper', (), {
            'title': 'Artificial intelligence in epilepsy — applications and pathways to the clinic',
            'doi': '10.1038/s41582-024-00965-9',  # From Nature Reviews Neurology
            'journal': 'Nature Reviews Neurology',
            'year': 2024,
            'authors': [],
            'pmid': None
        })()
    
    print(f"\n✓ Target paper:")
    print(f"  Title: {target_paper.title}")
    print(f"  DOI: {target_paper.doi}")
    print(f"  Journal: {target_paper.journal}")
    
    output_dir = Path("./.dev/pdfs_ai_epilepsy")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Method 1: Try OpenURL resolver
    print("\n" + "-" * 60)
    print("Method 1: OpenURL Resolver (University of Melbourne)")
    print("-" * 60)
    
    resolver = OpenURLResolver("https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    
    paper_metadata = {
        "title": target_paper.title,
        "journal": target_paper.journal,
        "year": target_paper.year,
        "doi": target_paper.doi,
    }
    
    openurl = resolver.build_openurl(paper_metadata)
    print(f"OpenURL: {openurl[:100]}...")
    print("\nYou can paste this URL in your browser for institutional access")
    
    result = await resolver.resolve_async(paper_metadata)
    if result:
        print(f"✓ Resolver found access: {result['access_type']}")
        if result.get('full_text_urls'):
            print(f"  Found {len(result['full_text_urls'])} links")
    
    # Method 2: Try Scholar download
    print("\n" + "-" * 60)
    print("Method 2: Scholar Module Download")
    print("-" * 60)
    
    downloaded = scholar.download_pdfs(
        target_paper.doi,
        download_dir=output_dir,
        force=True,
        show_progress=True
    )
    
    if len(downloaded) > 0:
        print("✅ Download successful!")
        for paper in downloaded.papers:
            if paper.pdf_path:
                pdf_path = Path(paper.pdf_path)
                if pdf_path.exists():
                    size_kb = pdf_path.stat().st_size / 1024
                    print(f"   File: {pdf_path.name} ({size_kb:.1f} KB)")
                    
                    # Check content
                    import subprocess
                    try:
                        text = subprocess.run(
                            ["pdftotext", str(pdf_path), "-", "-l", "1"],
                            capture_output=True,
                            text=True
                        ).stdout[:300].lower()
                        
                        if "artificial intelligence" in text and "epilepsy" in text:
                            print("   ✅ This appears to be the correct paper!")
                        elif "reporting summary" in text:
                            print("   ⚠️  This is a reporting summary")
                    except:
                        pass
    else:
        print("❌ Scholar download failed")
    
    # Method 3: Direct PDFDownloader with all strategies
    print("\n" + "-" * 60)
    print("Method 3: Direct PDFDownloader")
    print("-" * 60)
    
    downloader = PDFDownloader(
        download_dir=output_dir,
        use_lean_library=True,
        use_openathens=False,
        use_playwright=True,
        use_scihub=True,
        acknowledge_ethical_usage=True,
        debug_mode=True
    )
    
    direct_result = await downloader.download_pdf_async(
        identifier=target_paper.doi,
        output_dir=output_dir,
        filename="AI_epilepsy_2024.pdf",
        force=True
    )
    
    if direct_result:
        print(f"✅ Direct download successful: {direct_result.name}")
        size_kb = direct_result.stat().st_size / 1024
        print(f"   Size: {size_kb:.1f} KB")
    else:
        print("❌ Direct download failed")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    pdf_files = list(output_dir.glob("*.pdf"))
    if pdf_files:
        print(f"\n✅ Downloaded {len(pdf_files)} file(s):")
        for pdf in pdf_files:
            size_kb = pdf.stat().st_size / 1024
            print(f"   - {pdf.name} ({size_kb:.1f} KB)")
    else:
        print("\n❌ No files downloaded")
        print("\nTo access this paper:")
        print("1. Use the OpenURL link in your browser")
        print("2. Install Lean Library extension and try again")
        print("3. Access via Nature Reviews website with institutional login")

if __name__ == "__main__":
    asyncio.run(download_ai_epilepsy_paper())