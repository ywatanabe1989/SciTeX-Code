#!/usr/bin/env python3
"""Open paper URLs in browser tabs for manual download."""
import json
import webbrowser
import time
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
METADATA_FILE = Path("/home/ywatanabe/proj/SciTeX-Code/papers_metadata.json")
PROGRESS_FILE = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/download_progress.json")

def load_metadata() -> list:
    """Load paper metadata from JSON file."""
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def load_progress() -> dict:
    """Load download progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded": [], "manual_required": []}

def get_best_url(paper: dict) -> str:
    """Get the best URL for downloading the paper."""
    # Priority order:
    # 1. DOI (most reliable for institutional access)
    # 2. Publisher URL (ScienceDirect, etc.)
    # 3. PMC URL
    # 4. PubMed URL
    
    if "doi" in paper:
        return f"https://doi.org/{paper['doi']}"
    elif "sciencedirect_url" in paper:
        return paper["sciencedirect_url"]
    elif "pmc_url" in paper:
        return paper["pmc_url"]
    elif "pubmed_url" in paper:
        return paper["pubmed_url"]
    elif "pdf_url" in paper:
        return paper["pdf_url"]
    else:
        return None

def main():
    """Main function."""
    papers = load_metadata()
    progress = load_progress()
    
    # Get list of papers that need manual download
    papers_to_download = []
    for paper in papers:
        if paper["filename"] not in progress.get("downloaded", []):
            url = get_best_url(paper)
            if url:
                papers_to_download.append({
                    "title": paper["title"],
                    "filename": paper["filename"],
                    "url": url
                })
    
    if not papers_to_download:
        logger.info("All papers have been downloaded!")
        return
    
    logger.info(f"Opening {len(papers_to_download)} papers in browser tabs...")
    logger.info("Please download each PDF and save with the specified filename:\n")
    
    # Print instructions
    for i, paper in enumerate(papers_to_download, 1):
        logger.info(f"{i}. {paper['title'][:60]}...")
        logger.info(f"   Save as: {paper['filename']}")
        logger.info(f"   URL: {paper['url']}\n")
    
    # Ask for confirmation
    response = input("\nPress Enter to open all URLs in browser tabs, or 'q' to quit: ")
    if response.lower() == 'q':
        logger.info("Operation cancelled.")
        return
    
    # Open URLs in browser
    for paper in papers_to_download:
        logger.info(f"Opening: {paper['title'][:60]}...")
        webbrowser.open_new_tab(paper['url'])
        time.sleep(1)  # Small delay between tabs
    
    logger.info("\nAll URLs have been opened in browser tabs.")
    logger.info("Please download each PDF and save to:")
    logger.info(f"  {METADATA_FILE.parent / 'downloaded_papers'}")
    logger.info("\nMake sure to use the exact filenames listed above!")

if __name__ == "__main__":
    main()