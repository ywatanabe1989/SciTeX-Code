#!/usr/bin/env python3
"""Direct PDF download for papers with direct PDF URLs."""
import json
import requests
import time
from pathlib import Path
import logging
from typing import Dict, List, Optional

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

def download_pdf(url: str, filepath: Path) -> bool:
    """Download PDF from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if content is PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower():
            logger.warning(f"Non-PDF content type: {content_type}")
            return False
        
        # Save PDF
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Verify file size
        file_size = filepath.stat().st_size
        if file_size < 10000:  # Less than 10KB
            logger.warning(f"File too small ({file_size} bytes), likely not a valid PDF")
            filepath.unlink()
            return False
            
        logger.info(f"Downloaded: {filepath.name} ({file_size / 1024:.1f} KB)")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        if filepath.exists():
            filepath.unlink()
        return False

def main():
    """Main download function."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    papers = load_metadata()
    progress = load_progress()
    
    logger.info(f"Total papers: {len(papers)}")
    logger.info(f"Starting download of papers with direct PDF URLs...")
    
    downloaded_count = 0
    
    for paper in papers:
        if paper["filename"] in progress["downloaded"]:
            continue
            
        # Check for direct PDF URL
        if "pdf_url" in paper:
            filepath = DOWNLOAD_DIR / paper["filename"]
            
            logger.info(f"\nAttempting to download: {paper['title'][:60]}...")
            logger.info(f"URL: {paper['pdf_url']}")
            
            if download_pdf(paper["pdf_url"], filepath):
                progress["downloaded"].append(paper["filename"])
                downloaded_count += 1
                save_progress(progress)
                time.sleep(2)  # Be polite
            else:
                progress["failed"].append({
                    "filename": paper["filename"],
                    "url": paper["pdf_url"],
                    "title": paper["title"]
                })
                save_progress(progress)
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info(f"Download Summary:")
    logger.info(f"  Successfully downloaded: {downloaded_count}")
    logger.info(f"  Total downloaded so far: {len(progress['downloaded'])}")
    logger.info(f"  Failed: {len(progress['failed'])}")
    logger.info(f"  Remaining: {len(papers) - len(progress['downloaded'])}")
    
    # List failed downloads
    if progress["failed"]:
        logger.info(f"\nFailed downloads:")
        for fail in progress["failed"]:
            logger.info(f"  - {fail['title'][:60]}...")

if __name__ == "__main__":
    main()