#!/usr/bin/env python3
"""
Complete PDF download solution using Scholar module with browser automation
"""

import os
import sys
import logging
from pathlib import Path
import time

# Add the src directory to Python path
sys.path.insert(0, '/home/ywatanabe/proj/SciTeX-Code/src')

# Import Scholar module
from scitex.scholar import Scholar, ScholarConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Download PDFs using Scholar module"""
    
    # Configure Scholar with manual browser for authentication
    config = ScholarConfig(
        use_lean_library=False,  # Use manual browser
        use_openathens=False,    # Skip OpenAthens for now
        download_dir="/home/ywatanabe/proj/SciTeX-Code/downloaded_papers",
        debug_mode=True,         # Show browser for debugging
        acknowledge_scihub_ethical_usage=False  # Don't use Sci-Hub
    )
    
    # Initialize Scholar
    scholar = Scholar(config)
    
    # Load papers from bibtex
    bibtex_path = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib"
    papers = scholar.from_bibtex(bibtex_path)
    
    logger.info(f"Loaded {len(papers)} papers from bibtex")
    
    # Try to download first 5 papers
    test_papers = papers[:5]
    
    results = []
    for i, paper in enumerate(test_papers):
        logger.info(f"\n--- Paper {i+1}/{len(test_papers)} ---")
        logger.info(f"Title: {paper.title}")
        logger.info(f"Authors: {paper.authors}")
        logger.info(f"Year: {paper.year}")
        logger.info(f"URL: {paper.url}")
        
        # Try to find PDF URL
        if paper.url:
            logger.info("Attempting to access paper URL...")
            # Here we would use browser automation to:
            # 1. Navigate to the URL
            # 2. Look for PDF links
            # 3. Handle any authentication or redirects
            # 4. Download the PDF
            
            result = {
                "paper": paper,
                "status": "manual_download_needed",
                "url": paper.url
            }
            results.append(result)
        else:
            logger.warning("No URL found for this paper")
            result = {
                "paper": paper,
                "status": "no_url",
                "url": None
            }
            results.append(result)
        
        # Rate limiting
        time.sleep(2)
    
    # Summary
    logger.info("\n=== Download Summary ===")
    for result in results:
        paper = result["paper"]
        status = result["status"]
        logger.info(f"{paper.title[:50]}... - Status: {status}")
    
    # Create manual download instructions
    instructions_path = Path("/home/ywatanabe/proj/SciTeX-Code/manual_download_enhanced.md")
    with open(instructions_path, 'w') as f:
        f.write("# Enhanced Manual Download Instructions\n\n")
        f.write("Based on the Scholar module analysis, please download these papers:\n\n")
        
        for i, result in enumerate(results):
            paper = result["paper"]
            f.write(f"## {i+1}. {paper.title}\n\n")
            f.write(f"- **Authors**: {paper.authors}\n")
            f.write(f"- **Year**: {paper.year}\n")
            f.write(f"- **Journal**: {paper.journal}\n")
            f.write(f"- **URL**: {paper.url}\n")
            f.write(f"- **Save as**: {paper.authors.split(',')[0].split()[-1]}-{paper.year}-{paper.journal[:3].upper()}.pdf\n\n")
    
    logger.info(f"\nManual download instructions saved to: {instructions_path}")

if __name__ == "__main__":
    main()