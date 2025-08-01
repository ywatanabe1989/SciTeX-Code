#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 15:05:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/Scholar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Main Scholar class with integrated enhanced storage.

This is the primary interface for the Scholar module.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union

from scitex import logging
from .database._StorageIntegratedDB import StorageIntegratedDB
from .download._BrowserDownloadHelper import BrowserDownloadHelper
from .download._ScreenshotDownloadHelper import ScreenshotDownloadHelper
from .doi import DOIResolver
from .open_url import OpenURLResolver
from ._Paper import Paper

logger = logging.getLogger(__name__)


class Scholar:
    """Main interface for SciTeX Scholar with enhanced storage."""
    
    def __init__(self, library: str = "default"):
        """Initialize Scholar.
        
        Args:
            library: Library name to use
        """
        self.library = library
        self.db = StorageIntegratedDB(library)
        self.doi_resolver = DOIResolver()
        self.openurl_resolver = OpenURLResolver()
        self.browser_helper = BrowserDownloadHelper(library)
        
    # ========== Paper Management ==========
    
    def add_paper(self, paper: Union[Paper, Dict]) -> int:
        """Add paper to library.
        
        Args:
            paper: Paper object or metadata dict
            
        Returns:
            Paper ID
        """
        if isinstance(paper, Paper):
            metadata = paper.to_dict()
        else:
            metadata = paper
            
        return self.db.add_paper(metadata)
        
    def get_paper(self, identifier: str) -> Optional[Dict]:
        """Get paper by DOI or storage key.
        
        Args:
            identifier: DOI (10.xxxx/yyyy) or storage key (ABCD1234)
            
        Returns:
            Paper data with full details
        """
        # Check if it's a DOI
        if "/" in identifier and identifier.startswith("10."):
            return self.db.get_paper_by_doi(identifier)
        else:
            # Assume storage key
            return self.db.get_paper_by_key(identifier)
            
    def search_papers(self, query: str) -> List[Dict]:
        """Search papers (not implemented yet)."""
        # This would use full-text search
        logger.warning("Search not implemented yet")
        return []
        
    # ========== DOI Resolution ==========
    
    async def resolve_doi(self, paper_id: int) -> Optional[str]:
        """Resolve DOI for a paper.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            DOI if found
        """
        paper = self.db.get_paper_by_key(paper_id)
        if not paper:
            return None
            
        if paper.get("doi"):
            return paper["doi"]
            
        # Try to resolve
        doi = await self.doi_resolver.resolve_doi_async(
            title=paper.get("title"),
            authors=paper.get("authors"),
            year=paper.get("year")
        )
        
        if doi:
            # Update database
            with self.db._get_connection() as conn:
                conn.execute(
                    "UPDATE papers SET doi = ? WHERE id = ?",
                    (doi, paper_id)
                )
                conn.execute(
                    "UPDATE enrichment_status SET doi_resolved = 1 WHERE paper_id = ?",
                    (paper_id,)
                )
                conn.commit()
                
            # Update lookup
            self.db.lookup.add_entry(
                storage_key=paper["storage_key"],
                doi=doi,
                title=paper["title"],
                authors=paper["authors"],
                year=paper["year"]
            )
            
            logger.info(f"Resolved DOI for paper {paper_id}: {doi}")
            
        return doi
        
    # ========== PDF Download ==========
    
    def download_pdf(self, paper_id: int, method: str = "browser") -> Dict:
        """Download PDF for a paper.
        
        Args:
            paper_id: Paper ID
            method: Download method ("browser", "direct", "screenshot")
            
        Returns:
            Download result
        """
        paper = self.db.get_paper_by_key(paper_id)
        if not paper:
            return {"success": False, "error": "Paper not found"}
            
        # Get URLs to try
        urls = []
        
        # DOI URL
        if paper.get("doi"):
            urls.append(f"https://doi.org/{paper['doi']}")
            
            # Try OpenURL
            try:
                openurl_result = self.openurl_resolver.resolve(paper["doi"])
                if openurl_result and openurl_result.get("url"):
                    urls.append(openurl_result["url"])
            except:
                pass
                
        # Direct URL if available
        if paper.get("url"):
            urls.append(paper["url"])
            
        if not urls:
            return {"success": False, "error": "No URLs available"}
            
        if method == "browser":
            # Create browser download session
            session_id = self.browser_helper.create_download_session(max_papers=1)
            self.browser_helper.open_download_helper(session_id)
            return {
                "success": False,
                "method": "browser",
                "session_id": session_id,
                "message": "Browser helper opened for manual download"
            }
            
        elif method == "screenshot":
            # Use screenshot download helper
            if not paper.get("storage_key"):
                return {"success": False, "error": "No storage key"}
                
            # Run async download
            loop = asyncio.new_event_loop()
            helper = ScreenshotDownloadHelper(self.db.storage)
            result = loop.run_until_complete(
                helper.download_with_screenshots(
                    storage_key=paper["storage_key"],
                    urls=urls,
                    headless=False
                )
            )
            loop.close()
            
            # Update database if successful
            if result["success"] and result.get("pdf_path"):
                pdf_path = Path(result["pdf_path"])
                self.db.attach_pdf(
                    paper_id=paper_id,
                    pdf_path=pdf_path,
                    original_filename=pdf_path.name,
                    pdf_url=urls[0]
                )
                
            return result
            
        else:
            return {"success": False, "error": f"Unknown method: {method}"}
            
    def get_papers_without_pdf(self) -> List[Dict]:
        """Get all papers without PDFs."""
        return self.db.get_papers_needing_pdf()
        
    # ========== Storage Access ==========
    
    def get_pdf_path(self, paper_id: int) -> Optional[Path]:
        """Get path to PDF file.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            Path to PDF if exists
        """
        paper = self.db.get_paper_by_key(paper_id)
        if not paper or not paper.get("pdfs"):
            return None
            
        # Get latest PDF
        latest_pdf = paper["pdfs"][0]
        storage_key = paper["storage_key"]
        
        pdf_path = self.db.storage.storage_dir / storage_key / latest_pdf["filename"]
        return pdf_path if pdf_path.exists() else None
        
    def get_screenshots(self, paper_id: int) -> List[Path]:
        """Get all screenshots for a paper.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            List of screenshot paths
        """
        paper = self.db.get_paper_by_key(paper_id)
        if not paper:
            return []
            
        storage_key = paper["storage_key"]
        screenshots = self.db.storage.list_screenshots(storage_key)
        
        paths = []
        for screenshot in screenshots:
            path = self.db.storage.storage_dir / storage_key / "screenshots" / screenshot["filename"]
            if path.exists():
                paths.append(path)
                
        return paths
        
    # ========== Migration ==========
    
    def import_from_zotero(self, storage_path: Path, 
                          db_path: Optional[Path] = None) -> Dict[str, int]:
        """Import from existing Zotero library.
        
        Args:
            storage_path: Path to Zotero/storage directory
            db_path: Optional path to zotero.sqlite
            
        Returns:
            Import statistics
        """
        return self.db.migrate_from_zotero(storage_path, db_path)
        
    def import_from_bibtex(self, bibtex_path: Path) -> Dict[str, int]:
        """Import papers from BibTeX file.
        
        Args:
            bibtex_path: Path to .bib file
            
        Returns:
            Import statistics
        """
        from .io import BibtexIO
        
        stats = {"added": 0, "skipped": 0, "errors": 0}
        
        # Load BibTeX
        bib_io = BibtexIO()
        papers = bib_io.load(bibtex_path)
        
        for paper in papers:
            try:
                # Check if already exists
                if paper.doi and self.db.get_paper_by_doi(paper.doi):
                    stats["skipped"] += 1
                    continue
                    
                # Add to database
                self.add_paper(paper)
                stats["added"] += 1
                
            except Exception as e:
                logger.error(f"Error importing paper: {e}")
                stats["errors"] += 1
                
        return stats
        
    # ========== Statistics ==========
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return self.db.get_statistics()
        
    def get_storage_info(self) -> Dict:
        """Get storage information."""
        return self.db.storage.get_storage_stats()


# Convenience functions
def get_default_scholar() -> Scholar:
    """Get Scholar instance for default library."""
    return Scholar("default")


if __name__ == "__main__":
    print("SciTeX Scholar - Integrated System")
    print("=" * 60)
    
    print("\nComplete workflow example:")
    print("""
    from scitex.scholar import Scholar
    
    # Initialize
    scholar = Scholar()
    
    # Add paper from partial info
    paper_id = scholar.add_paper({
        "title": "Attention is All You Need",
        "authors": ["Vaswani, A.", "Shazeer, N."],
        "year": 2017
    })
    
    # Resolve DOI
    doi = await scholar.resolve_doi(paper_id)
    print(f"Resolved DOI: {doi}")
    
    # Download PDF with screenshots
    result = scholar.download_pdf(paper_id, method="screenshot")
    if result["success"]:
        print(f"PDF downloaded: {result['pdf_path']}")
        print(f"Screenshots: {result['screenshots']}")
    else:
        # Fall back to browser helper
        result = scholar.download_pdf(paper_id, method="browser")
        
    # Access stored files
    pdf_path = scholar.get_pdf_path(paper_id)
    screenshots = scholar.get_screenshots(paper_id)
    
    # Import from Zotero
    stats = scholar.import_from_zotero(
        Path("~/Zotero/storage")
    )
    print(f"Imported: {stats}")
    """)
    
    print("\nStorage structure:")
    print("""
    storage/
    ├── ABCD1234/
    │   ├── attention-is-all-you-need.pdf    # Original filename
    │   ├── storage_metadata.json            # Metadata
    │   ├── metadata.json                    # Paper metadata
    │   └── screenshots/                     # Download attempts
    │       ├── 20250801_150000-attempt-1-initial.jpg
    │       ├── 20250801_150005-attempt-1-success.jpg
    │       └── screenshots.json
    
    storage-human-readable/
    └── Vaswani-2017-NeurIPS-ABCD -> ../storage/ABCD1234
    """)

# EOF