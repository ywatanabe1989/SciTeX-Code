#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test script to verify publisher URL first optimization

"""
Test the optimized ScholarURLFinder that tries publisher URL first
before OpenURL resolution.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scitex.scholar import ScholarConfig, ScholarURLFinder, ScholarBrowserManager
from scitex.log import getLogger

logger = getLogger(__name__)


async def test_optimization(dois: list):
    """Test URL finding with publisher-first optimization."""
    config = ScholarConfig()
    
    # Initialize browser manager
    browser_manager = ScholarBrowserManager(config=config)
    await browser_manager.initialize()
    
    try:
        # Initialize URL finder
        url_finder = ScholarURLFinder(
            config=config,
            browser_manager=browser_manager,
            use_cache=False  # Don't use cache to test actual behavior
        )
        
        results = []
        for doi in dois:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing DOI: {doi}")
            logger.info(f"{'='*60}")
            
            result = await url_finder.find_urls(doi)
            
            # Check if OpenURL was skipped
            skipped = result.get("openurl_skipped", False)
            skip_reason = result.get("openurl_skip_reason", "")
            pdf_count = len(result.get("urls_pdf", []))
            
            logger.info(f"\nResults for {doi}:")
            logger.info(f"  - PDFs found: {pdf_count}")
            logger.info(f"  - OpenURL skipped: {skipped}")
            if skipped:
                logger.info(f"  - Skip reason: {skip_reason}")
            logger.info(f"  - Publisher URL: {result.get('url_publisher', 'None')}")
            logger.info(f"  - OpenURL resolved: {result.get('url_openurl_resolved', 'None')}")
            
            results.append({
                "doi": doi,
                "pdf_count": pdf_count,
                "openurl_skipped": skipped,
                "skip_reason": skip_reason
            })
        
        # Summary
        logger.success(f"\n{'='*60}")
        logger.success("OPTIMIZATION TEST SUMMARY")
        logger.success(f"{'='*60}")
        
        total_tested = len(results)
        total_skipped = sum(1 for r in results if r["openurl_skipped"])
        total_with_pdfs = sum(1 for r in results if r["pdf_count"] > 0)
        
        logger.success(f"Total DOIs tested: {total_tested}")
        logger.success(f"OpenURL resolutions skipped: {total_skipped}/{total_tested} ({total_skipped/total_tested*100:.1f}%)")
        logger.success(f"DOIs with PDFs found: {total_with_pdfs}/{total_tested} ({total_with_pdfs/total_tested*100:.1f}%)")
        
        logger.success("\nDetailed results:")
        for r in results:
            status = "✅ OPTIMIZED" if r["openurl_skipped"] else "⚠️ NEEDED OPENURL"
            logger.success(f"  {r['doi']}: {status} ({r['pdf_count']} PDFs)")
        
    finally:
        await browser_manager.close()


async def main():
    # Test with a mix of open access and paywalled articles
    test_dois = [
        "10.1038/s41598-024-64867-y",  # Nature Scientific Reports (open access)
        "10.3389/fnhum.2016.00052",     # Frontiers (open access)  
        "10.1016/j.tics.2010.09.001",   # Elsevier (paywalled)
        "10.1038/s41593-018-0209-y",     # Nature Neuroscience (paywalled)
    ]
    
    await test_optimization(test_dois)


if __name__ == "__main__":
    asyncio.run(main())