#!/usr/bin/env python3
"""Download PDFs using the Scholar module with authentication."""

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex.scholar import Papers
from scitex.scholar.download import PDFDownloader
from scitex import logging

logger = logging.getLogger(__name__)


async def download_pdfs_from_metadata():
    """Download PDFs based on papers_metadata.json."""
    
    # Load paper metadata
    metadata_file = Path("papers_metadata.json")
    if not metadata_file.exists():
        logger.error(f"Metadata file not found: {metadata_file}")
        return
    
    with open(metadata_file) as f:
        papers_data = json.load(f)
    
    print(f"Found {len(papers_data)} papers in metadata")
    
    # Create Papers collection
    papers = Papers()
    
    # Add papers to collection
    for paper_data in papers_data[:10]:  # Process first 10 papers
        paper = papers.add_paper(
            title=paper_data['title'],
            authors=[paper_data['authors']],
            year=paper_data['year'],
            journal=paper_data['journal']
        )
        
        # Add URLs and identifiers
        if 'doi' in paper_data:
            paper.doi = paper_data['doi']
        
        if 'pubmed_url' in paper_data:
            paper.pubmed_url = paper_data['pubmed_url']
        
        if 'pmc_url' in paper_data:
            paper.pmc_url = paper_data['pmc_url']
        
        if 'pdf_url' in paper_data:
            paper.pdf_url = paper_data['pdf_url']
        
        if 'sciencedirect_url' in paper_data:
            paper.publisher_url = paper_data['sciencedirect_url']
    
    print(f"\nCreated Papers collection with {len(papers)} papers")
    
    # Download PDFs with various strategies
    output_dir = Path("downloaded_papers")
    output_dir.mkdir(exist_ok=True)
    
    # Try downloading PDFs
    download_results = await papers.download_pdfs_async(
        output_dir=output_dir,
        use_openathens=True,  # Use OpenAthens authentication
        use_crawl4ai=True,    # Try Crawl4AI
        use_browser=True,     # Use browser automation
        max_concurrent=1,     # One at a time to avoid rate limits
        show_progress=True
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("Download Summary:")
    print(f"{'='*60}")
    
    success_count = 0
    failed_count = 0
    
    for paper, result in download_results.items():
        if result and result.get('success'):
            success_count += 1
            print(f"✓ {paper.title[:50]}...")
            print(f"  → {result['path']}")
        else:
            failed_count += 1
            print(f"✗ {paper.title[:50]}...")
            if result and 'error' in result:
                print(f"  → Error: {result['error']}")
    
    print(f"\nTotal: {success_count} successful, {failed_count} failed")
    
    # Save updated progress
    progress = {
        'total': len(papers),
        'downloaded': success_count,
        'failed': failed_count,
        'results': {
            paper.title: {
                'success': result.get('success', False),
                'path': result.get('path'),
                'error': str(result.get('error', '')) if result else 'No result'
            }
            for paper, result in download_results.items()
        }
    }
    
    with open('.dev/scholar_download_progress.json', 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"\nProgress saved to .dev/scholar_download_progress.json")


if __name__ == "__main__":
    asyncio.run(download_pdfs_from_metadata())