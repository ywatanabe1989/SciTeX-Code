#!/usr/bin/env python3
"""
Comprehensive PDF download script for all 75 enriched papers.

This script implements the Scholar workflow step 7:
- Download PDFs using AI agents (Claude Code)  
- Cookie acceptance
- Captcha handling
- Zotero translators
- Store PDFs in format: FIRSTAUTHOR-YEAR-JOURNAL.pdf
- Headless mode and screenshots for debugging
- Skip unsolvable problems and escalate to user
- Progress tracking and resumability

Usage:
    python download_all_pdfs.py [--resume] [--limit N] [--debug]
"""

import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from scitex.scholar import Papers
from scitex.scholar.config import ScholarConfig
from scitex.scholar.download._SmartPDFDownloader import SmartPDFDownloader
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import DOIToURLResolver
from scitex import logging

logger = logging.getLogger(__name__)

class PDFDownloadManager:
    """Manages the complete PDF download process for all papers."""
    
    def __init__(self, config: Optional[ScholarConfig] = None, collection_name: str = "papers"):
        self.config = config or ScholarConfig()
        self.collection_name = collection_name
        
        # Use proper path manager for file organization
        self.path_manager = self.config.path_manager
        
        # Progress tracking in workspace
        self.progress_file = self.path_manager.get_workspace_logs_dir() / "pdf_download_progress.json"
        self.progress = self._load_progress()
        
        # Initialize components
        self.auth_manager = AuthenticationManager(config=self.config)
        self.downloader = SmartPDFDownloader(config=self.config)
        self.url_resolver = DOIToURLResolver(config=self.config)
        
        # Output directory - use downloads directory from path manager
        self.output_dir = self.path_manager.get_downloads_dir()
        
        # Collection directory for organized storage
        self.collection_dir = self.path_manager.get_collection_dir(collection_name)
        self.readable_dir = self.path_manager.get_collection_readable_dir(collection_name)
        
        # Initialize collection BibTeX file
        self._initialize_collection_bibtex()
        
    def _load_progress(self) -> Dict:
        """Load download progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load progress: {e}")
        
        return {
            "completed": {},
            "failed": {},
            "skipped": {},
            "started_at": None,
            "last_updated": None,
            "total_papers": 0,
            "success_count": 0,
            "failure_count": 0,
            "skip_count": 0
        }
    
    def _save_progress(self):
        """Save current progress to file."""
        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            self.progress_file.parent.mkdir(exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def _generate_filename(self, paper) -> str:
        """Generate filename in format: FIRSTAUTHOR-YEAR-JOURNAL.pdf"""
        try:
            # Get first author
            first_author = "Unknown"
            if hasattr(paper, 'authors') and paper.authors:
                # Extract last name from first author
                first_author_full = paper.authors[0].strip()
                if ',' in first_author_full:
                    first_author = first_author_full.split(',')[0].strip()
                else:
                    # Assume "First Last" format, take last name
                    parts = first_author_full.split()
                    first_author = parts[-1] if parts else "Unknown"
            
            # Get year
            year = getattr(paper, 'year', 'Unknown')
            
            # Get journal (simplified)
            journal = getattr(paper, 'journal', 'Unknown')
            if journal and len(journal) > 20:
                # Shorten long journal names
                journal = journal[:20].strip()
            
            # Clean up for filename
            def clean_for_filename(s):
                return "".join(c for c in s if c.isalnum() or c in (' ', '-', '_')).strip()
            
            first_author = clean_for_filename(first_author)
            journal = clean_for_filename(journal)
            
            filename = f"{first_author}-{year}-{journal}.pdf"
            return filename
            
        except Exception as e:
            logger.warning(f"Failed to generate filename for paper: {e}")
            # Fallback to simple format
            return f"paper_{hash(str(paper)) % 10000}.pdf"
    
    def _initialize_collection_bibtex(self):
        """Initialize collection BibTeX file with header if it doesn't exist."""
        collection_bibtex = self.collection_dir / f"{self.collection_name}.bib"
        
        if not collection_bibtex.exists():
            header = f"""% BibTeX bibliography for collection: {self.collection_name}
% Generated by SciTeX Scholar PDF Downloader
% Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
% 
% This file contains papers downloaded and organized by SciTeX Scholar.
% Each entry corresponds to a paper stored in the collection directory.
%

"""
            with open(collection_bibtex, 'w', encoding='utf-8') as f:
                f.write(header)
    
    def _save_paper_to_collection_bibtex(self, paper, paper_storage_paths: Dict):
        """Save paper to collection-specific BibTeX file."""
        collection_bibtex = self.collection_dir / f"{self.collection_name}.bib"
        
        # Create BibTeX entry
        bibtex_entry = self._paper_to_bibtex_entry(paper)
        
        # Append to collection BibTeX file
        with open(collection_bibtex, 'a', encoding='utf-8') as f:
            f.write(bibtex_entry + "\n\n")
    
    def _paper_to_bibtex_entry(self, paper) -> str:
        """Convert paper to BibTeX entry format."""
        # Generate entry key
        first_author = "unknown"
        if hasattr(paper, 'authors') and paper.authors:
            author_parts = paper.authors[0].split()
            first_author = author_parts[-1].lower() if author_parts else "unknown"
        
        year = getattr(paper, 'year', 'unknown')
        title_words = paper.title.lower().split()[:3] if paper.title else ['unknown']
        title_key = ''.join(word[:4] for word in title_words)
        
        entry_key = f"{first_author}{year}{title_key}"
        
        # Build entry
        entry_type = "article"  # Default to article
        
        lines = [f"@{entry_type}{{{entry_key},"]
        
        # Add fields
        if paper.title:
            lines.append(f'  title = {{{paper.title}}},')
        
        if hasattr(paper, 'authors') and paper.authors:
            authors_str = ' and '.join(paper.authors)
            lines.append(f'  author = {{{authors_str}}},')
        
        if hasattr(paper, 'year') and paper.year:
            lines.append(f'  year = {{{paper.year}}},')
        
        if hasattr(paper, 'journal') and paper.journal:
            lines.append(f'  journal = {{{paper.journal}}},')
        
        if hasattr(paper, 'doi') and paper.doi:
            lines.append(f'  doi = {{{paper.doi}}},')
        
        # Add source tracking
        if hasattr(paper, 'doi_source') and paper.doi_source:
            lines.append(f'  doi_source = {{{paper.doi_source}}},')
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f'  note = {{Downloaded by SciTeX Scholar ({timestamp})}}')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    async def download_single_paper(self, paper, paper_id: str) -> Tuple[bool, str]:
        """Download PDF for a single paper."""
        logger.info(f"Processing paper: {paper.title[:50]}...")
        
        try:
            # Check if already completed
            if paper_id in self.progress["completed"]:
                logger.info("Already downloaded, skipping")
                return True, "Already completed"
            
            # Check if failed too many times
            if paper_id in self.progress["failed"]:
                failure_info = self.progress["failed"][paper_id]
                if failure_info.get("attempts", 0) >= 3:
                    logger.info("Too many failures, skipping")
                    return False, "Too many failures"
            
            # Get DOI
            doi = getattr(paper, 'doi', None)
            if not doi:
                logger.warning("No DOI available")
                return False, "No DOI"
            
            # Resolve URL
            logger.info(f"Resolving URL for DOI: {doi}")
            result = await self.url_resolver.resolve_single_async(doi)
            url = result.get('url') if result else None
            
            if not url:
                logger.warning("Could not resolve DOI to URL")
                return False, "URL resolution failed"
            
            # Prepare paper metadata for path manager
            paper_info = {
                'title': paper.title,
                'authors': getattr(paper, 'authors', []),
                'year': getattr(paper, 'year', None),
                'doi': doi,
                'journal': getattr(paper, 'journal', None),
                'url': url
            }
            
            # Get storage paths using path manager
            storage_paths = self.path_manager.get_paper_storage_paths(
                paper_info, self.collection_name
            )
            
            # Create metadata.json in the paper directory
            metadata_file = storage_paths["storage_path"] / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(paper_info, f, indent=2)
            
            # Generate original filename from journal
            original_filename = self._generate_original_filename(paper_info)
            pdf_path = storage_paths["storage_path"] / original_filename
            
            # Create Paper object for SmartPDFDownloader
            from scitex.scholar._Paper import Paper
            paper_obj = Paper(
                title=paper_info['title'],
                authors=paper_info['authors'],
                year=paper_info['year'],
                doi=paper_info['doi'],
                journal=paper_info['journal'],
                url=paper_info['url']
            )
            
            # Download PDF
            logger.info(f"Downloading to: {pdf_path}")
            success, downloaded_path = await self.downloader.download_single(paper_obj)
            
            # Move to proper location if successful
            if success and downloaded_path and downloaded_path.exists():
                if downloaded_path != pdf_path:
                    pdf_path.parent.mkdir(parents=True, exist_ok=True)
                    downloaded_path.rename(pdf_path)
                success = True
            else:
                success = False
            
            if success:
                # Save to collection BibTeX
                self._save_paper_to_collection_bibtex(paper, storage_paths)
                
                logger.success(f"Successfully downloaded: {pdf_path}")
                self.progress["completed"][paper_id] = {
                    "timestamp": datetime.now().isoformat(),
                    "storage_path": str(storage_paths["storage_path"]),
                    "readable_path": str(storage_paths["readable_path"]),
                    "unique_id": storage_paths["unique_id"],
                    "original_filename": original_filename,
                    "doi": doi,
                    "url": url
                }
                self.progress["success_count"] = len(self.progress["completed"])
                return True, f"Downloaded: {storage_paths['unique_id']}"
            else:
                logger.warning("Download failed")
                return False, "Download failed"
                
        except Exception as e:
            logger.error(f"Error downloading paper: {e}")
            return False, str(e)
    
    def _generate_original_filename(self, paper_info: Dict) -> str:
        """Generate original filename as it would appear from the journal."""
        # Use a simple approach for now
        title = paper_info.get('title', 'unknown').replace(' ', '_')
        # Clean title for filename
        title = "".join(c for c in title if c.isalnum() or c in ('_', '-'))[:50]
        return f"{title}.pdf"
    
    def _record_failure(self, paper_id: str, error: str):
        """Record a failure for a paper."""
        if paper_id not in self.progress["failed"]:
            self.progress["failed"][paper_id] = {
                "attempts": 0,
                "errors": []
            }
        
        self.progress["failed"][paper_id]["attempts"] += 1
        self.progress["failed"][paper_id]["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": error
        })
        
        self.progress["failure_count"] = len(self.progress["failed"])
    
    async def download_all_papers(self, bibtex_file: str, resume: bool = True, limit: Optional[int] = None):
        """Download PDFs for all papers in the BibTeX file."""
        logger.info("Starting comprehensive PDF download process")
        
        # Load papers
        papers = Papers.from_bibtex(bibtex_file)
        total_papers = len(papers)
        
        if limit:
            papers = papers[:limit]
            logger.info(f"Limited to {limit} papers for testing")
        
        self.progress["total_papers"] = total_papers
        if not self.progress["started_at"]:
            self.progress["started_at"] = datetime.now().isoformat()
        
        logger.info(f"Loaded {len(papers)} papers from {bibtex_file}")
        
        # Process each paper
        for i, paper in enumerate(papers):
            paper_id = f"paper_{i:03d}"
            
            try:
                logger.info(f"\n[{i+1}/{len(papers)}] Processing {paper_id}")
                
                success, message = await self.download_single_paper(paper, paper_id)
                
                if success:
                    logger.info(f"✅ {message}")
                else:
                    logger.warning(f"❌ {message}")
                    self._record_failure(paper_id, message)
                
                # Save progress every 5 papers
                if (i + 1) % 5 == 0:
                    self._save_progress()
                    self._print_progress()
                
                # Rate limiting - be respectful
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                logger.info("Download interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error processing {paper_id}: {e}")
                self._record_failure(paper_id, str(e))
        
        # Final save and summary
        self._save_progress()
        self._print_final_summary()
    
    def _print_progress(self):
        """Print current progress."""
        completed = len(self.progress["completed"])
        failed = len(self.progress["failed"])
        total = self.progress["total_papers"]
        
        print(f"\n📊 Progress Report:")
        print(f"  ✅ Completed: {completed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📝 Total: {total}")
        
        if total > 0:
            success_rate = completed / (completed + failed) * 100 if (completed + failed) > 0 else 0
            print(f"  📈 Success rate: {success_rate:.1f}%")
    
    def _print_final_summary(self):
        """Print final download summary."""
        print("\n" + "="*60)
        print("🎉 PDF Download Summary")
        print("="*60)
        
        completed = len(self.progress["completed"])
        failed = len(self.progress["failed"])
        total = self.progress["total_papers"]
        
        print(f"Total papers processed: {completed + failed}/{total}")
        print(f"✅ Successfully downloaded: {completed}")
        print(f"❌ Failed downloads: {failed}")
        
        if completed + failed > 0:
            success_rate = completed / (completed + failed) * 100
            print(f"📈 Overall success rate: {success_rate:.1f}%")
        
        if completed > 0:
            print(f"\n📁 File Organization:")
            print(f"  Library collection: {self.collection_dir}")
            print(f"  Human-readable links: {self.readable_dir}")
            print(f"  Collection BibTeX: {self.collection_dir / f'{self.collection_name}.bib'}")
            print(f"  Downloads workspace: {self.output_dir}")
            print(f"  Progress file: {self.progress_file}")
            
            print(f"\n📊 Directory Structure:")
            print(f"  ~/.scitex/scholar/library/{self.collection_name}/")
            print(f"  ├── <8-DIGIT-ID>/")
            print(f"  │   ├── <original-filename>.pdf")
            print(f"  │   └── metadata.json")
            print(f"  └── {self.collection_name}.bib")
            print(f"  ~/.scitex/scholar/library/{self.collection_name}-human-readable/")
            print(f"  └── <AUTHOR-YEAR-JOURNAL>/ -> ../<8-DIGIT-ID>/")
        
        if failed > 0:
            print(f"\n⚠️  {failed} papers require manual attention")
            print("Check the progress file for details on failures")


async def main():
    """Main function for PDF download script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download PDFs for all enriched papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all papers
  python download_all_pdfs.py
  
  # Resume previous download
  python download_all_pdfs.py --resume
  
  # Test with first 5 papers
  python download_all_pdfs.py --limit 5
  
  # Debug mode with verbose logging
  python download_all_pdfs.py --debug --limit 3
        """
    )
    
    parser.add_argument(
        "--resume", 
        action="store_true", 
        help="Resume from previous progress"
    )
    
    parser.add_argument(
        "--limit", 
        type=int, 
        help="Limit number of papers to process (for testing)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--bibtex",
        default="src/scitex/scholar/docs/papers-enriched.bib",
        help="Path to enriched BibTeX file"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize config and manager
    config = ScholarConfig()
    manager = PDFDownloadManager(config=config)
    
    # Start download process
    try:
        await manager.download_all_papers(
            bibtex_file=args.bibtex,
            resume=args.resume,
            limit=args.limit
        )
        
        print("\n🎯 PDF download process completed!")
        print("Check the output directory and progress file for results.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Download interrupted by user")
        print("Progress has been saved. Resume with --resume flag.")
        return 1
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))