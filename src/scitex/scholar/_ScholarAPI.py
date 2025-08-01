#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_ScholarAPI.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/_ScholarAPI.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""High-level API for SciTeX Scholar operations.

Provides simple interface for common scholar tasks using the lookup index.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from scitex import logging
from .lookup import get_default_lookup
from ._Paper import Paper

logger = logging.getLogger(__name__)


class ScholarAPI:
    """High-level API for scholar operations."""
    
    def __init__(self, library_name: str = "default"):
        """Initialize Scholar API.
        
        Args:
            library_name: Library to use (default: "default")
        """
        self.library_name = library_name
        self.lookup = get_default_lookup()
        
        # Set base paths
        scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
        self.base_dir = scitex_dir / "scholar" / "library" / library_name
        self.storage_dir = self.base_dir / "storage"
        
    def get_paper_by_doi(self, doi: str) -> Optional[Paper]:
        """Get paper by DOI.
        
        Args:
            doi: DOI to lookup
            
        Returns:
            Paper object if found
        """
        # Lookup storage key
        storage_key = self.lookup.lookup_by_doi(doi)
        if not storage_key:
            logger.debug(f"DOI not found in index: {doi}")
            return None
            
        return self._load_paper_from_storage(storage_key)
        
    def get_paper_by_title(self, title: str) -> Optional[Paper]:
        """Get paper by exact title match.
        
        Args:
            title: Paper title
            
        Returns:
            Paper object if found
        """
        storage_key = self.lookup.lookup_by_title(title)
        if not storage_key:
            logger.debug(f"Title not found in index: {title[:50]}...")
            return None
            
        return self._load_paper_from_storage(storage_key)
        
    def find_similar_papers(self, title: str, authors: Optional[List[str]] = None,
                          year: Optional[int] = None) -> List[Tuple[Paper, float]]:
        """Find similar papers based on title, authors, and year.
        
        Args:
            title: Paper title
            authors: Author list
            year: Publication year
            
        Returns:
            List of (Paper, similarity_score) tuples
        """
        candidates = self.lookup.find_duplicates(title, authors, year)
        
        results = []
        for storage_key, score in candidates:
            paper = self._load_paper_from_storage(storage_key)
            if paper:
                results.append((paper, score))
                
        return results
        
    def _load_paper_from_storage(self, storage_key: str) -> Optional[Paper]:
        """Load paper from storage directory.
        
        Args:
            storage_key: 8-character storage key
            
        Returns:
            Paper object if found
        """
        paper_dir = self.storage_dir / "by_key" / storage_key
        metadata_path = paper_dir / "metadata.json"
        
        if not metadata_path.exists():
            logger.warning(f"Metadata not found for key: {storage_key}")
            return None
            
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                
            # Check if PDF exists
            pdf_path = paper_dir / "paper.pdf"
            if pdf_path.exists():
                data["pdf_path"] = pdf_path
                
            return Paper(**data)
            
        except Exception as e:
            logger.error(f"Failed to load paper {storage_key}: {e}")
            return None
            
    def has_pdf(self, doi: str) -> bool:
        """Check if paper has PDF.
        
        Args:
            doi: DOI to check
            
        Returns:
            True if PDF exists
        """
        storage_key = self.lookup.lookup_by_doi(doi)
        if not storage_key:
            return False
            
        metadata = self.lookup.lookup_by_key(storage_key)
        return metadata.get("has_pdf", False) if metadata else False
        
    def get_pdf_path(self, doi: str) -> Optional[Path]:
        """Get PDF path for a paper.
        
        Args:
            doi: DOI to lookup
            
        Returns:
            Path to PDF if exists
        """
        storage_key = self.lookup.lookup_by_doi(doi)
        if not storage_key:
            return None
            
        pdf_path = self.storage_dir / "by_key" / storage_key / "paper.pdf"
        return pdf_path if pdf_path.exists() else None
        
    def get_papers_needing_pdf(self) -> List[Paper]:
        """Get list of papers without PDFs."""
        storage_keys = self.lookup.get_papers_without_pdf()
        
        papers = []
        for key in storage_keys:
            paper = self._load_paper_from_storage(key)
            if paper:
                papers.append(paper)
                
        return papers
        
    def get_papers_needing_doi(self) -> List[Paper]:
        """Get list of papers without DOIs."""
        storage_keys = self.lookup.get_papers_without_doi()
        
        papers = []
        for key in storage_keys:
            paper = self._load_paper_from_storage(key)
            if paper:
                papers.append(paper)
                
        return papers
        
    def update_lookup_index(self, paper: Paper, storage_key: str) -> bool:
        """Update lookup index for a paper.
        
        Args:
            paper: Paper object
            storage_key: Storage key
            
        Returns:
            Success status
        """
        # Check if PDF exists
        pdf_path = self.storage_dir / "by_key" / storage_key / "paper.pdf"
        has_pdf = pdf_path.exists()
        pdf_size = pdf_path.stat().st_size if has_pdf else None
        
        return self.lookup.add_entry(
            storage_key=storage_key,
            doi=paper.doi,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            has_pdf=has_pdf,
            pdf_size=pdf_size
        )
        
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        lookup_stats = self.lookup.get_statistics()
        
        # Add storage statistics
        if self.storage_dir.exists():
            storage_size = sum(f.stat().st_size for f in self.storage_dir.rglob("*") if f.is_file())
            lookup_stats["storage_size_mb"] = storage_size / 1024 / 1024
            
        return lookup_stats


# Convenience functions
def get_paper_by_doi(doi: str, library: str = "default") -> Optional[Paper]:
    """Quick lookup by DOI."""
    api = ScholarAPI(library)
    return api.get_paper_by_doi(doi)


def has_pdf(doi: str, library: str = "default") -> bool:
    """Check if paper has PDF."""
    api = ScholarAPI(library)
    return api.has_pdf(doi)


def get_pdf_path(doi: str, library: str = "default") -> Optional[Path]:
    """Get PDF path for paper."""
    api = ScholarAPI(library)
    return api.get_pdf_path(doi)


if __name__ == "__main__":
    print("SciTeX Scholar API")
    print("=" * 60)
    
    # Example usage
    api = ScholarAPI()
    
    # Check if paper exists
    paper = api.get_paper_by_doi("10.1234/example")
    if paper:
        print(f"Found: {paper}")
        print(f"Has PDF: {api.has_pdf(paper.doi)}")
        
    # Get papers needing PDFs
    need_pdf = api.get_papers_needing_pdf()
    print(f"\nPapers without PDFs: {len(need_pdf)}")
    
    # Get statistics
    stats = api.get_statistics()
    print(f"\nStatistics: {stats}")

# EOF