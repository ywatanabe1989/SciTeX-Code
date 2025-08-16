#!/usr/bin/env python3
"""Download open access papers that don't require authentication"""

import asyncio
import json
from pathlib import Path
from scitex.logging import getLogger
from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarURLFinder,
    ScholarPDFDownloader,
)

logger = getLogger(__name__)

async def download_openaccess_papers():
    """Download open access papers from the list"""
    
    # Load open access papers list
    papers_file = Path("/home/ywatanabe/proj/scitex_repo/scholar/docs/papers_openaccess.json")
    with open(papers_file, 'r') as f:
        data = json.load(f)
    
    papers = data['open_access_papers']
    logger.info(f"Loaded {len(papers)} open access papers")
    
    # Initialize browser without authentication (open access doesn't need it)
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    url_finder = ScholarURLFinder(context)
    pdf_downloader = ScholarPDFDownloader(context)
    
    # Output directory
    output_dir = Path("/tmp/openaccess_papers")
    output_dir.mkdir(exist_ok=True)
    
    # Track results
    successful = []
    failed = []
    
    # Download each paper
    for i, paper in enumerate(papers[:3], 1):  # Test with first 3 papers
        doi = paper['doi']
        title = paper['title'][:50]
        journal = paper['journal']
        
        logger.info(f"\n[{i}/{len(papers[:3])}] Processing: {title}...")
        logger.info(f"  DOI: {doi}")
        logger.info(f"  Journal: {journal}")
        
        try:
            # Step 1: Find URLs
            urls = await url_finder.find_urls(doi=doi)
            
            if urls.get("url_final_pdf"):
                pdf_url = urls["url_final_pdf"]
                logger.info(f"  Found PDF URL: {pdf_url[:80]}...")
                
                # Step 2: Download PDF
                output_file = output_dir / f"{doi.replace('/', '_')}.pdf"
                success = await pdf_downloader.download_from_url(
                    pdf_url,
                    output_file,
                    timeout_sec=60
                )
                
                if success and output_file.exists():
                    size_mb = output_file.stat().st_size / 1024 / 1024
                    logger.info(f"  ✓ Downloaded: {output_file.name} ({size_mb:.2f} MB)")
                    successful.append({
                        'doi': doi,
                        'title': title,
                        'file': str(output_file),
                        'size_mb': size_mb
                    })
                else:
                    logger.error(f"  ✗ Download failed")
                    failed.append({
                        'doi': doi,
                        'title': title,
                        'reason': 'Download failed'
                    })
            else:
                logger.warning(f"  No PDF URL found")
                failed.append({
                    'doi': doi,
                    'title': title,
                    'reason': 'No PDF URL found'
                })
                
        except Exception as e:
            logger.error(f"  Error: {e}")
            failed.append({
                'doi': doi,
                'title': title,
                'reason': str(e)
            })
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("DOWNLOAD SUMMARY - OPEN ACCESS PAPERS")
    logger.info("="*60)
    logger.info(f"Successful downloads: {len(successful)}/{len(papers[:3])}")
    
    if successful:
        logger.info("\nSuccessfully downloaded:")
        for paper in successful:
            logger.info(f"  • {paper['title']} ({paper['size_mb']:.2f} MB)")
    
    if failed:
        logger.warning(f"\nFailed downloads: {len(failed)}")
        for paper in failed:
            logger.warning(f"  • {paper['title']}: {paper['reason']}")
    
    # Save results
    results_file = output_dir / "download_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'successful': successful,
            'failed': failed,
            'total': len(papers[:3])
        }, f, indent=2)
    logger.info(f"\nResults saved to: {results_file}")
    
    await browser_manager.close()

if __name__ == "__main__":
    asyncio.run(download_openaccess_papers())