#!/usr/bin/env python3
"""
Download all 75 papers from the AI2 BibTeX file using Scholar module.
This script implements Step 8 of the Scholar workflow with fallback strategies.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import scitex as stx
from scitex.scholar import Scholar
from scitex.errors import SciTeXWarning

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define output directories
OUTPUT_DIR = Path(__file__).parent / "downloaded_papers"
PROGRESS_FILE = Path(__file__).parent / "download_progress.json"
FAILED_DOIS_FILE = Path(__file__).parent / "failed_downloads.json"

def load_progress():
    """Load download progress from file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded": [], "failed": [], "skipped": []}

def save_progress(progress):
    """Save download progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def main():
    """Main workflow for downloading all papers."""
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load the enriched BibTeX file from step 6
    bibtex_file = Path(__file__).parent.parent / "src/scitex/scholar/docs/from_user/papers.bib"
    if not bibtex_file.exists():
        logger.error(f"BibTeX file not found: {bibtex_file}")
        return
    
    logger.info(f"Loading papers from {bibtex_file}")
    
    # Initialize Scholar
    scholar = Scholar()
    
    # Load papers
    papers = scholar.load_bibtex(str(bibtex_file))
    logger.info(f"Loaded {len(papers)} papers from BibTeX")
    
    # Load progress
    progress = load_progress()
    logger.info(f"Previous progress: {len(progress['downloaded'])} downloaded, {len(progress['failed'])} failed")
    
    # Filter out already processed papers
    processed_dois = set(progress['downloaded'] + progress['failed'])
    papers_to_download = [p for p in papers if p.doi and p.doi not in processed_dois]
    
    logger.info(f"Papers to download: {len(papers_to_download)}")
    
    # Download PDFs
    successful = 0
    failed = 0
    
    for i, paper in enumerate(papers_to_download):
        logger.info(f"\n[{i+1}/{len(papers_to_download)}] Processing: {paper.title[:80]}...")
        
        if not paper.doi:
            logger.warning("No DOI available, skipping")
            progress['skipped'].append({
                "title": paper.title,
                "reason": "No DOI"
            })
            continue
        
        # Generate filename
        first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
        year = paper.year or "0000"
        journal = paper.journal or "Unknown"
        journal_abbrev = ''.join([word[0].upper() for word in journal.split()[:3]])
        filename = f"{first_author}-{year}-{journal_abbrev}.pdf"
        filepath = OUTPUT_DIR / filename
        
        # Check if already exists
        if filepath.exists():
            logger.info(f"Already downloaded: {filename}")
            progress['downloaded'].append(paper.doi)
            successful += 1
            continue
        
        try:
            # Try to download
            logger.info(f"Downloading DOI: {paper.doi}")
            
            # Use Scholar's download_pdfs method with ethical acknowledgment
            downloaded_papers = scholar.download_pdfs(
                [paper.doi],
                output_dir=str(OUTPUT_DIR),
                acknowledge_ethical_usage=True,
                use_openathens=False,  # Skip OpenAthens for now
                timeout=60
            )
            
            if downloaded_papers and downloaded_papers[0].pdf_path:
                # Rename to our format
                original_path = Path(downloaded_papers[0].pdf_path)
                if original_path.exists():
                    original_path.rename(filepath)
                    logger.info(f"✓ Downloaded successfully: {filename}")
                    progress['downloaded'].append(paper.doi)
                    successful += 1
                else:
                    raise Exception("PDF file not found after download")
            else:
                raise Exception("Download returned no PDF")
                
        except Exception as e:
            logger.error(f"✗ Failed to download: {str(e)}")
            progress['failed'].append({
                "doi": paper.doi,
                "title": paper.title,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            failed += 1
        
        # Save progress after each download
        save_progress(progress)
        
        # Small delay to be respectful
        if i < len(papers_to_download) - 1:
            logger.info("Waiting 2 seconds before next download...")
            import time
            time.sleep(2)
    
    # Final summary
    logger.info("\n" + "="*80)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*80)
    logger.info(f"Total papers in BibTeX: {len(papers)}")
    logger.info(f"Previously downloaded: {len(progress['downloaded']) - successful}")
    logger.info(f"Newly downloaded: {successful}")
    logger.info(f"Failed downloads: {failed}")
    logger.info(f"Total successful: {len(progress['downloaded'])}")
    logger.info(f"Total failed: {len(progress['failed'])}")
    logger.info(f"Success rate: {len(progress['downloaded']) / len(papers) * 100:.1f}%")
    
    # Save failed DOIs for manual intervention
    if progress['failed']:
        with open(FAILED_DOIS_FILE, 'w') as f:
            json.dump(progress['failed'], f, indent=2)
        logger.info(f"\nFailed downloads saved to: {FAILED_DOIS_FILE}")
        logger.info("These require manual intervention or alternative methods.")
    
    logger.info(f"\nDownloaded PDFs are in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()