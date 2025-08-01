#!/usr/bin/env python3
"""Complete PDF download script with multiple strategies."""
import json
import os
import time
import requests
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
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
DOWNLOAD_REPORT = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/download_report.md")

# User agent for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def load_metadata() -> List[Dict]:
    """Load paper metadata from JSON file."""
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def load_progress() -> Dict:
    """Load download progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            # Ensure all keys exist
            if "manual_required" not in data:
                data["manual_required"] = []
            if "in_progress" not in data:
                data["in_progress"] = []
            return data
    return {
        "downloaded": [],
        "failed": [],
        "manual_required": [],
        "in_progress": []
    }

def save_progress(progress: Dict):
    """Save download progress."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def try_direct_download(url: str, filepath: Path) -> Tuple[bool, str]:
    """Try direct download of PDF."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Check if content is PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower() and response.content[:4] != b'%PDF':
            return False, f"Not a PDF (content-type: {content_type})"
        
        # Save PDF
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Verify file size
        file_size = filepath.stat().st_size
        if file_size < 10000:  # Less than 10KB
            filepath.unlink()
            return False, f"File too small ({file_size} bytes)"
            
        return True, f"Success ({file_size / 1024:.1f} KB)"
        
    except Exception as e:
        if filepath.exists():
            filepath.unlink()
        return False, f"Error: {str(e)}"

def check_pdf_urls(paper: Dict) -> List[Tuple[str, str]]:
    """Get all possible PDF URLs for a paper."""
    urls = []
    
    # Direct PDF URL
    if "pdf_url" in paper:
        urls.append((paper["pdf_url"], "Direct PDF"))
    
    # PMC PDF construction
    if "pmc_url" in paper and "PMC" in paper["pmc_url"]:
        pmc_id = paper["pmc_url"].split("/")[-1]
        if pmc_id.startswith("PMC"):
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
            urls.append((pdf_url, "PMC PDF"))
    
    return urls

def generate_download_report(papers: List[Dict], progress: Dict):
    """Generate comprehensive download report."""
    report = []
    report.append("# PDF Download Report\n")
    report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Summary
    total = len(papers)
    downloaded = len(progress["downloaded"])
    failed = len(progress["failed"])
    manual = len(progress["manual_required"])
    remaining = total - downloaded
    
    report.append("## Summary\n")
    report.append(f"- Total papers: {total}\n")
    report.append(f"- Successfully downloaded: {downloaded} ({downloaded/total*100:.1f}%)\n")
    report.append(f"- Failed attempts: {failed}\n")
    report.append(f"- Manual download required: {manual}\n")
    report.append(f"- Remaining: {remaining}\n")
    
    # Downloaded papers
    if progress["downloaded"]:
        report.append("\n## Successfully Downloaded\n")
        for filename in sorted(progress["downloaded"]):
            report.append(f"- ✅ {filename}\n")
    
    # Manual download required
    if progress["manual_required"]:
        report.append("\n## Manual Download Required\n")
        for item in progress["manual_required"]:
            paper = next((p for p in papers if p["filename"] == item["filename"]), None)
            if paper:
                report.append(f"\n### {paper['title'][:80]}...\n")
                report.append(f"- **Filename**: `{item['filename']}`\n")
                report.append(f"- **Reason**: {item.get('reason', 'Authentication required')}\n")
                
                # List all available URLs
                if "doi" in paper:
                    report.append(f"- **DOI**: https://doi.org/{paper['doi']}\n")
                if "sciencedirect_url" in paper:
                    report.append(f"- **ScienceDirect**: {paper['sciencedirect_url']}\n")
                if "pmc_url" in paper:
                    report.append(f"- **PMC**: {paper['pmc_url']}\n")
                if "pubmed_url" in paper:
                    report.append(f"- **PubMed**: {paper['pubmed_url']}\n")
    
    # Failed downloads
    if progress["failed"]:
        report.append("\n## Failed Downloads\n")
        for item in progress["failed"]:
            report.append(f"- ❌ {item['filename']}: {item.get('error', 'Unknown error')}\n")
    
    # Save report
    with open(DOWNLOAD_REPORT, 'w') as f:
        f.writelines(report)
    
    logger.info(f"Download report saved to: {DOWNLOAD_REPORT}")

def main():
    """Main download function."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    papers = load_metadata()
    progress = load_progress()
    
    logger.info(f"Starting PDF download process for {len(papers)} papers...")
    
    for i, paper in enumerate(papers):
        if paper["filename"] in progress["downloaded"]:
            continue
        
        logger.info(f"\n[{i+1}/{len(papers)}] Processing: {paper['title'][:60]}...")
        filepath = DOWNLOAD_DIR / paper["filename"]
        
        # Try different download strategies
        pdf_urls = check_pdf_urls(paper)
        download_success = False
        
        for url, source in pdf_urls:
            logger.info(f"  Trying {source}: {url}")
            success, message = try_direct_download(url, filepath)
            
            if success:
                logger.info(f"  ✅ {message}")
                progress["downloaded"].append(paper["filename"])
                download_success = True
                save_progress(progress)
                time.sleep(2)  # Be polite
                break
            else:
                logger.warning(f"  ❌ {message}")
        
        if not download_success:
            # Add to manual download list
            manual_entry = {
                "filename": paper["filename"],
                "title": paper["title"],
                "reason": "All automatic download attempts failed"
            }
            
            if manual_entry not in progress["manual_required"]:
                progress["manual_required"].append(manual_entry)
                save_progress(progress)
    
    # Generate final report
    generate_download_report(papers, progress)
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("Download Summary:")
    logger.info(f"  Total papers: {len(papers)}")
    logger.info(f"  Downloaded: {len(progress['downloaded'])}")
    logger.info(f"  Manual required: {len(progress['manual_required'])}")
    logger.info(f"  Failed: {len(progress['failed'])}")

if __name__ == "__main__":
    main()