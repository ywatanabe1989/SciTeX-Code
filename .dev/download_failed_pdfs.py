#!/usr/bin/env python3
"""Download failed PDFs from download_progress.json"""

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex.scholar.download._PDFDownloader import PDFDownloader
from scitex import logging

logger = logging.getLogger(__name__)


async def download_failed_pdfs():
    """Download PDFs that failed in previous attempts."""
    
    # Load download progress
    progress_file = Path(".dev/download_progress.json")
    if not progress_file.exists():
        logger.error(f"Progress file not found: {progress_file}")
        return
    
    with open(progress_file) as f:
        progress = json.load(f)
    
    failed_papers = progress.get("failed", [])
    manual_needed = progress.get("manual_required", [])
    
    print(f"Found {len(failed_papers)} failed downloads")
    print(f"Found {len(manual_needed)} papers requiring manual download")
    
    # Prepare papers for download
    papers_to_download = []
    
    # Add failed papers
    for paper in failed_papers:
        papers_to_download.append({
            'title': paper['title'],
            'url': paper['url'],
            'filename': paper['filename']
        })
    
    # Also try manual_required papers
    for paper in manual_needed[:3]:  # Try first 3
        papers_to_download.append({
            'title': paper['title'],
            'filename': paper['filename']
        })
    
    if not papers_to_download:
        print("No papers to download")
        return
    
    # Initialize downloader with multiple strategies
    downloader = PDFDownloader(
        download_dir=Path("downloaded_papers"),
        use_translators=True,
        use_playwright=True,
        use_openathens=True,  # Try with OpenAthens
        max_concurrent=1,  # Download one at a time
        debug_mode=True,
    )
    
    # Download each paper
    for paper in papers_to_download:
        print(f"\n{'='*60}")
        print(f"Downloading: {paper['title']}")
        print(f"Filename: {paper['filename']}")
        
        # Try with URL if available
        if 'url' in paper:
            print(f"URL: {paper['url']}")
            result = await downloader.download_async(
                paper['url'],
                filename=paper['filename']
            )
            
            if result:
                print(f"✓ Success: {result}")
            else:
                print(f"✗ Failed to download from URL")
        
        # Try with title search
        else:
            print("No URL available, trying title search...")
            # This would require implementing a search method
            # For now, we'll skip
            print("Title search not implemented yet")
    
    print(f"\n{'='*60}")
    print("Download attempts completed")


if __name__ == "__main__":
    asyncio.run(download_failed_pdfs())