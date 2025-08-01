#!/usr/bin/env python3
"""Download papers using puppeteer with OpenAthens authentication."""
import json
import time
from pathlib import Path
import logging
from typing import Dict, List

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
OPENATHENS_SESSION = Path.home() / ".scitex/scholar/openathens_session.json"

def load_metadata() -> List[Dict]:
    """Load paper metadata from JSON file."""
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def load_openathens_cookies() -> List[Dict]:
    """Load OpenAthens session cookies."""
    with open(OPENATHENS_SESSION, 'r') as f:
        session_data = json.load(f)
    return session_data.get("full_cookies", [])

def load_progress() -> Dict:
    """Load download progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "in_progress": []}

def save_progress(progress: Dict):
    """Save download progress."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def create_download_instructions():
    """Create download instructions for manual execution."""
    papers = load_metadata()
    progress = load_progress()
    
    instructions = []
    instructions.append("# PDF Download Instructions with Puppeteer\n")
    instructions.append("## Papers to Download\n")
    
    for i, paper in enumerate(papers):
        if paper["filename"] in progress["downloaded"]:
            continue
            
        instructions.append(f"\n### {i+1}. {paper['title'][:80]}...\n")
        instructions.append(f"- **Filename**: `{paper['filename']}`\n")
        
        # List all available URLs
        if "pdf_url" in paper:
            instructions.append(f"- **Direct PDF**: {paper['pdf_url']}\n")
        if "doi" in paper:
            instructions.append(f"- **DOI**: https://doi.org/{paper['doi']}\n")
        if "sciencedirect_url" in paper:
            instructions.append(f"- **ScienceDirect**: {paper['sciencedirect_url']}\n")
        if "pmc_url" in paper:
            instructions.append(f"- **PMC**: {paper['pmc_url']}\n")
        if "pubmed_url" in paper:
            instructions.append(f"- **PubMed**: {paper['pubmed_url']}\n")
            
        instructions.append(f"- **Status**: ⏳ Pending\n")
    
    # Save instructions
    instruction_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/puppeteer_download_instructions.md")
    with open(instruction_file, 'w') as f:
        f.writelines(instructions)
    
    logger.info(f"Created instructions: {instruction_file}")
    
    # Create summary
    summary = {
        "total_papers": len(papers),
        "downloaded": len(progress["downloaded"]),
        "failed": len(progress["failed"]),
        "remaining": len(papers) - len(progress["downloaded"])
    }
    
    return summary

def main():
    """Main function."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if OpenAthens session exists
    if not OPENATHENS_SESSION.exists():
        logger.error(f"OpenAthens session file not found: {OPENATHENS_SESSION}")
        logger.info("Please authenticate using: python -m scitex.scholar.authenticate openathens")
        return
    
    # Load data
    papers = load_metadata()
    cookies = load_openathens_cookies()
    progress = load_progress()
    
    logger.info(f"Total papers: {len(papers)}")
    logger.info(f"OpenAthens cookies loaded: {len(cookies)} cookies")
    logger.info(f"Already downloaded: {len(progress['downloaded'])}")
    
    # Create download instructions
    summary = create_download_instructions()
    
    logger.info("\nDownload Summary:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    
    # Next steps
    logger.info("\nNext Steps:")
    logger.info("1. Use puppeteer MCP to navigate to each URL with cookies")
    logger.info("2. Download PDFs to the download directory")
    logger.info("3. Update progress file after each download")
    logger.info("4. Handle authentication challenges and captchas")

if __name__ == "__main__":
    main()