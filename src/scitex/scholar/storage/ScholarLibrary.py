#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 04:18:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/ScholarLibrary.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex.scholar.config import ScholarConfig

from ._LibraryCacheManager import LibraryCacheManager
from ._LibraryManager import LibraryManager
from .BibTeXHandler import BibTeXHandler


class ScholarLibrary:
    """Unified Scholar library management combining cache and storage operations."""

    def __init__(
        self, project: str = None, config: Optional[ScholarConfig] = None
    ):
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self._cache_manager = LibraryCacheManager(
            project=self.project, config=self.config
        )
        self._library_manager = LibraryManager(
            project=self.project, config=self.config
        )
        self.bibtex_handler = BibTeXHandler(
            project=self.project, config=self.config
        )

    def load_paper(self, library_id: str) -> Dict[str, Any]:
        """Load paper metadata from library."""
        return self._cache_manager.load_paper_metadata(library_id)

    def save_paper(self, paper: "Paper", force: bool = False) -> str:
        """Save paper to library with explicit parameters."""
        # Extract all available fields from paper object
        paper_dict = paper.to_dict() if hasattr(paper, 'to_dict') else {}

        return self._library_manager.save_resolved_paper(
            # Required fields
            title=getattr(paper, 'title', paper_dict.get('title', '')),
            doi=getattr(paper, 'doi', paper_dict.get('doi', '')),

            # Optional bibliographic fields
            year=getattr(paper, 'year', paper_dict.get('year')),
            authors=getattr(paper, 'authors', paper_dict.get('authors')),
            journal=getattr(paper, 'journal', paper_dict.get('journal')),
            abstract=getattr(paper, 'abstract', paper_dict.get('abstract')),

            # Additional bibliographic fields
            volume=getattr(paper, 'volume', paper_dict.get('volume')),
            issue=getattr(paper, 'issue', paper_dict.get('issue')),
            pages=getattr(paper, 'pages', paper_dict.get('pages')),
            publisher=getattr(paper, 'publisher', paper_dict.get('publisher')),
            issn=getattr(paper, 'issn', paper_dict.get('issn')),

            # Enrichment fields
            citation_count=getattr(paper, 'citation_count', paper_dict.get('citation_count')),

            # Source tracking
            doi_source=getattr(paper, 'doi_source', paper_dict.get('doi_source')),
            title_source=getattr(paper, 'title_source', paper_dict.get('title_source')),
            abstract_source=getattr(paper, 'abstract_source', paper_dict.get('abstract_source')),

            # Library management
            library_id=getattr(paper, 'library_id', paper_dict.get('library_id')),
            project=self.project,
        )

    def papers_from_bibtex(
        self, bibtex_input: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from BibTeX file or content."""
        return self.bibtex_handler.papers_from_bibtex(bibtex_input)

    def paper_from_bibtex_entry(
        self, entry: Dict[str, Any]
    ) -> Optional["Paper"]:
        """Convert BibTeX entry to Paper."""
        return self.bibtex_handler.paper_from_bibtex_entry(entry)

    def check_existing_doi(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Check if DOI exists in library."""
        return self._cache_manager.is_doi_stored(title, year)


if __name__ == "__main__":

    # Implement main guard to demonstrate typical usage of this script
    def main():
        pass

    main()

# EOF
