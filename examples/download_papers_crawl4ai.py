#!/usr/bin/env python3
"""Download papers using Crawl4AI strategy."""

import asyncio
import os
from pathlib import Path
from scitex.scholar.download._Crawl4AIDownloadStrategy import Crawl4AIDownloadStrategy
from scitex import logging

logger = logging.getLogger(__name__)

# Set up University of Melbourne OpenAthens resolver
os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"

# Paper data extracted from BibTeX
papers_data = [
    {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
        "first_author": "Hulsemann",
        "year": "2019",
        "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096",
        "bibtex_key": "Hlsemann2019QuantificationOPA",
        "doi": "10.3389/fnins.2019.00573"  # Found the DOI for this paper
    },
    {
        "title": "Generative models, linguistic communication and active inference",
        "first_author": "Friston",
        "year": "2020",
        "url": "https://api.semanticscholar.org/CorpusID:220603864",
        "bibtex_key": "Friston2020GenerativeMLB",
        "doi": "10.1016/j.neubiorev.2020.07.005"  # Found the DOI
    },
    {
        "title": "The functional role of cross-frequency coupling",
        "first_author": "Canolty",
        "year": "2010",
        "url": "https://www.sciencedirect.com/science/article/pii/S1364661310002068",
        "bibtex_key": "Canolty2010TheFRC",
        "doi": "10.1016/j.tics.2010.09.001"  # Extracted from URL
    }
]

# Create a simple Paper class to match the expected interface
class SimplePaper:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

async def download_papers():
    """Download all papers using Crawl4AI."""
    
    # Create output directory
    output_dir = "pdfs"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Initialize Crawl4AI strategy
    strategy = Crawl4AIDownloadStrategy(
        browser_type="chromium",
        headless=False,  # Set to False to see what's happening
        profile_name="scitex_academic",
        simulate_user=True
    )
    
    # Download each paper
    results = {}
    for paper_data in papers_data:
        paper = SimplePaper(**paper_data)
        logger.info(f"\nDownloading: {paper.title}")
        
        try:
            # Progress callback
            async def progress_callback(method, status, path=None):
                logger.info(f"  [{method}] Status: {status}")
                if path:
                    logger.info(f"  Downloaded to: {path}")
            
            # Download
            pdf_path = await strategy.download_async(
                paper=paper,
                output_dir=output_dir,
                progress_callback=progress_callback
            )
            
            results[paper.bibtex_key] = {
                "success": pdf_path is not None,
                "path": pdf_path,
                "title": paper.title
            }
            
            # Small delay between downloads
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to download {paper.title}: {e}")
            results[paper.bibtex_key] = {
                "success": False,
                "path": None,
                "title": paper.title,
                "error": str(e)
            }
    
    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    
    for key, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"\n{status}: {result['title']}")
        if result["success"]:
            print(f"  Path: {result['path']}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    # Count successes
    success_count = sum(1 for r in results.values() if r["success"])
    print(f"\nTotal: {success_count}/{len(results)} papers downloaded successfully")

if __name__ == "__main__":
    asyncio.run(download_papers())