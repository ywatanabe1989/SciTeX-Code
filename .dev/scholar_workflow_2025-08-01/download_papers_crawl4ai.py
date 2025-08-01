#!/usr/bin/env python3
"""
Download PDFs using Crawl4AI MCP server
"""

import json
import os
import time
import logging
from pathlib import Path
import asyncio
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load paper information
def load_paper_info():
    """Load paper information from bibtex and download URLs"""
    papers = []
    
    # Load from download_urls.json
    download_urls_path = Path("/home/ywatanabe/proj/SciTeX-Code/download_urls.json")
    if download_urls_path.exists():
        with open(download_urls_path, 'r') as f:
            papers = json.load(f)
    
    # Also load URLs from manual instructions
    manual_urls = [
        {"title": "Quantification of Phase-Amplitude Coupling", "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096", "filename": "Hulsemann-2019-FIN.pdf"},
        {"title": "Generative models, linguistic communication", "url": "https://api.semanticscholar.org/CorpusId:220603864", "filename": "Friston-2020-NAB.pdf"},
        {"title": "The functional role of cross-frequency coupling", "url": "https://www.sciencedirect.com/science/article/pii/S1364661310002068", "filename": "Canolty-2010-TIC.pdf"},
        {"title": "Untangling cross-frequency coupling", "url": "https://www.sciencedirect.com/science/article/pii/S0959438814001640", "filename": "Aru-2014-COI.pdf"},
        {"title": "Measuring phase-amplitude coupling", "url": "https://www.ncbi.nlm.nih.gov/pubmed/20463205", "filename": "Tort-2010-JON.pdf"},
    ]
    
    return manual_urls[:5]  # Start with first 5 papers

async def download_pdf_with_crawl4ai(url: str, filename: str, output_dir: Path) -> bool:
    """Download a PDF using Crawl4AI"""
    try:
        logger.info(f"Attempting to download: {filename} from {url}")
        
        # First, try to get the page with Crawl4AI
        # Note: This is a simplified example - we need the actual MCP tool call
        # The real implementation would use the MCP tools
        
        output_path = output_dir / filename
        if output_path.exists():
            logger.info(f"File already exists: {filename}")
            return True
            
        # TODO: Implement actual Crawl4AI MCP calls here
        # For now, we'll create a placeholder
        logger.warning(f"Crawl4AI integration pending for: {filename}")
        
        return False
        
    except Exception as e:
        logger.error(f"Error downloading {filename}: {str(e)}")
        return False

async def main():
    """Main function to download papers"""
    output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/downloaded_papers")
    output_dir.mkdir(exist_ok=True)
    
    papers = load_paper_info()
    logger.info(f"Found {len(papers)} papers to download")
    
    # Track results
    results = {
        "successful": [],
        "failed": [],
        "skipped": []
    }
    
    # Download papers
    for paper in papers:
        url = paper.get("url")
        filename = paper.get("filename")
        
        if not url or not filename:
            logger.warning(f"Missing URL or filename for paper: {paper.get('title', 'Unknown')}")
            results["skipped"].append(paper)
            continue
            
        success = await download_pdf_with_crawl4ai(url, filename, output_dir)
        
        if success:
            results["successful"].append(paper)
        else:
            results["failed"].append(paper)
            
        # Rate limiting
        await asyncio.sleep(2)
    
    # Save results
    results_path = output_dir.parent / "download_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    logger.info(f"\nDownload Summary:")
    logger.info(f"Successful: {len(results['successful'])}")
    logger.info(f"Failed: {len(results['failed'])}")
    logger.info(f"Skipped: {len(results['skipped'])}")
    
    if results["failed"]:
        logger.info("\nFailed downloads:")
        for paper in results["failed"]:
            logger.info(f"  - {paper.get('title', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(main())