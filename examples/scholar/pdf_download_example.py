#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example of downloading PDFs for papers.

This example shows how to:
1. Search for papers
2. Download available PDFs
3. Handle papers without PDFs gracefully

Note: Only open-access papers can be downloaded automatically.
"""

import asyncio
from pathlib import Path
from scitex.scholar import search_papers, PDFDownloader

async def main():
    """Download PDFs for papers."""
    
    # Create download directory
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    
    # Initialize PDF downloader
    downloader = PDFDownloader(download_dir=download_dir)
    
    # Search for open-access papers (more likely to have PDFs)
    print("Searching for open-access papers...")
    papers = await search_papers(
        query="arxiv machine learning neural networks",  # arXiv papers are open-access
        limit=5
    )
    
    if not papers:
        print("No papers found.")
        return
    
    print(f"Found {len(papers)} papers\n")
    
    # Try to download PDFs
    downloaded = 0
    failed = 0
    
    for paper in papers:
        print(f"Paper: {paper.title[:60]}...")
        
        # Check if paper has a PDF URL
        if paper.pdf_url:
            print(f"  PDF URL: {paper.pdf_url}")
            try:
                pdf_path = await downloader.download_paper(paper)
                if pdf_path:
                    print(f"  ✅ Downloaded to: {pdf_path}")
                    downloaded += 1
                else:
                    print(f"  ❌ Download failed")
                    failed += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                failed += 1
        else:
            print(f"  ⚠️  No PDF URL available")
        print()
    
    # Summary
    print(f"\nDownload Summary:")
    print(f"- Successfully downloaded: {downloaded}")
    print(f"- Failed downloads: {failed}")
    print(f"- No PDF available: {len(papers) - downloaded - failed}")
    print(f"\nPDFs saved in: {download_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main())