#!/usr/bin/env python3
"""Download all papers from enriched BibTeX file."""

import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

async def download_all_papers():
    """Download all papers from enriched BibTeX."""
    from src.scitex.scholar import Scholar
    from src.scitex.scholar._Papers import Papers
    
    # Load enriched papers
    bib_file = Path("src/scitex/scholar/docs/papers-partial-enriched.bib")
    papers = Papers.from_bibtex(bib_file)
    
    # Extract DOIs
    dois = []
    for paper in papers:
        if paper.doi:
            dois.append(paper.doi)
    
    print(f"Found {len(dois)} papers with DOIs")
    
    # Create Scholar instance
    scholar = Scholar()
    
    # Download directory
    download_dir = Path("downloaded_papers")
    download_dir.mkdir(exist_ok=True)
    
    # Download PDFs
    print(f"\nDownloading PDFs to {download_dir.absolute()}")
    results = scholar.download_pdfs(
        dois[:5],  # Start with first 5 papers
        download_dir=download_dir,
        show_progress=True,
        acknowledge_ethical_usage=True
    )
    
    return results

if __name__ == "__main__":
    import asyncio
    results = asyncio.run(download_all_papers())
    print(f"\nDownload complete. Results: {results}")