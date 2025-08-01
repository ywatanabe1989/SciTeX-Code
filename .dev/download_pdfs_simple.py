#!/usr/bin/env python3
"""Simple PDF download script using direct URLs."""

import json
import os
import sys
import asyncio
from pathlib import Path
import aiohttp
import aiofiles

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex import logging

logger = logging.getLogger(__name__)


async def download_pdf_async(session, url, output_path):
    """Download a PDF from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,*/*',
            'Referer': 'https://scholar.google.com/'
        }
        
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            if response.status == 200:
                content = await response.read()
                
                # Check if it's a PDF
                if content.startswith(b'%PDF'):
                    async with aiofiles.open(output_path, 'wb') as f:
                        await f.write(content)
                    return True, None
                else:
                    return False, "Not a PDF file"
            else:
                return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)


async def main():
    """Download PDFs from known URLs."""
    
    # Load metadata
    with open('papers_metadata.json') as f:
        papers = json.load(f)
    
    # Create output directory
    output_dir = Path('downloaded_papers')
    output_dir.mkdir(exist_ok=True)
    
    # Papers with direct PDF URLs
    pdf_papers = [p for p in papers if 'pdf_url' in p]
    print(f"Found {len(pdf_papers)} papers with PDF URLs")
    
    # Create session
    async with aiohttp.ClientSession() as session:
        for paper in pdf_papers[:5]:  # Try first 5
            print(f"\n{'='*60}")
            print(f"Paper: {paper['title']}")
            print(f"PDF URL: {paper['pdf_url']}")
            
            output_path = output_dir / paper['filename']
            
            # Skip if already exists
            if output_path.exists():
                print(f"✓ Already exists: {output_path}")
                continue
            
            # Try download
            success, error = await download_pdf_async(
                session, 
                paper['pdf_url'], 
                output_path
            )
            
            if success:
                print(f"✓ Downloaded: {output_path}")
            else:
                print(f"✗ Failed: {error}")
                
                # Try alternative URLs
                if 'pmc_url' in paper:
                    print(f"  Trying PMC page: {paper['pmc_url']}")
                    # Navigate to PMC page to get actual PDF URL
                    # This would require browser automation
    
    print(f"\n{'='*60}")
    print("Download complete")
    
    # List downloaded files
    downloaded = list(output_dir.glob('*.pdf'))
    print(f"\nDownloaded {len(downloaded)} PDFs:")
    for pdf in downloaded:
        print(f"  - {pdf.name}")


if __name__ == "__main__":
    asyncio.run(main())