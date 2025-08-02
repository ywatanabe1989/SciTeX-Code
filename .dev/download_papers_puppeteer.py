#!/usr/bin/env python3
"""Download papers using Puppeteer MCP server for authenticated access."""
import json
import os
import time
from pathlib import Path
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse, quote

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOAD_DIR = Path("/home/ywatanabe/proj/SciTeX-Code/downloaded_papers")
METADATA_FILE = Path("/home/ywatanabe/proj/SciTeX-Code/papers_metadata.json")
PROGRESS_FILE = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/download_progress.json")

def load_metadata() -> List[Dict]:
    """Load paper metadata from JSON file."""
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def load_progress() -> Dict:
    """Load download progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "skipped": []}

def save_progress(progress: Dict):
    """Save download progress."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def get_download_urls(paper: Dict) -> List[str]:
    """Get all possible download URLs for a paper."""
    urls = []
    
    # PMC PDF URL
    if "pdf_url" in paper:
        urls.append(paper["pdf_url"])
    
    # DOI URL
    if "doi" in paper:
        urls.append(f"https://doi.org/{paper['doi']}")
    
    # Publisher URLs
    if "sciencedirect_url" in paper:
        urls.append(paper["sciencedirect_url"])
    
    # PubMed/PMC URLs
    if "pmc_url" in paper:
        urls.append(paper["pmc_url"])
    if "pubmed_url" in paper:
        urls.append(paper["pubmed_url"])
        
    return urls

def create_download_script():
    """Create a bash script to download papers using puppeteer."""
    script_content = """#!/bin/bash
# Download papers using Puppeteer MCP

# Create download directory
mkdir -p /home/ywatanabe/proj/SciTeX-Code/downloaded_papers

echo "Starting PDF downloads..."
echo "========================="

# Function to check if PDF was downloaded
check_download() {
    local filename="$1"
    local filepath="/home/ywatanabe/proj/SciTeX-Code/downloaded_papers/${filename}"
    
    if [ -f "$filepath" ]; then
        echo "✓ Successfully downloaded: $filename"
        return 0
    else
        echo "✗ Failed to download: $filename"
        return 1
    fi
}

# Example downloads (to be populated)
"""
    
    # Load metadata
    papers = load_metadata()
    progress = load_progress()
    
    for i, paper in enumerate(papers[:5]):  # Start with first 5 papers
        if paper["filename"] in progress["downloaded"]:
            continue
            
        urls = get_download_urls(paper)
        if not urls:
            logger.warning(f"No URLs found for: {paper['title']}")
            continue
            
        script_content += f"""
# Paper {i+1}: {paper['title'][:50]}...
echo "Downloading paper {i+1}/{len(papers[:5])}: {paper['filename']}"
"""
        
        for url in urls:
            script_content += f"""
# Try URL: {url}
echo "Trying URL: {url}"
# Add puppeteer download command here
"""
    
    script_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/download_papers.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    logger.info(f"Created download script: {script_path}")

def main():
    """Main download function."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    papers = load_metadata()
    progress = load_progress()
    
    logger.info(f"Total papers: {len(papers)}")
    logger.info(f"Already downloaded: {len(progress['downloaded'])}")
    logger.info(f"Failed downloads: {len(progress['failed'])}")
    
    # Create download script
    create_download_script()
    
    # For now, let's create a summary
    summary = {
        "total_papers": len(papers),
        "papers_with_dois": sum(1 for p in papers if "doi" in p),
        "papers_with_pmc": sum(1 for p in papers if "pmc_url" in p or "pdf_url" in p),
        "papers_with_publisher_urls": sum(1 for p in papers if "sciencedirect_url" in p),
        "downloaded": len(progress["downloaded"]),
        "remaining": len(papers) - len(progress["downloaded"])
    }
    
    logger.info("Download Summary:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    
    # Save summary
    with open(DOWNLOAD_DIR / "download_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()