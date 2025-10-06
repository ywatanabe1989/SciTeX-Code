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
        self,
        project: Union[str, Path] = None,
        config: Optional[ScholarConfig] = None
    ):
        """Initialize ScholarLibrary.

        Args:
            project: Project name (str) or library directory path (Path)
            config: Optional ScholarConfig instance
        """
        self.config = config or ScholarConfig()

        # Handle both project name and library directory path
        if isinstance(project, Path):
            # If Path is the library root dir (e.g., ~/.scitex/scholar/library)
            # use the default project from config
            if project.name == 'library':
                self.project = self.config.resolve("project", None)
                self.config.library_dir = str(project)
            else:
                # Path points to specific project dir
                # e.g., /home/user/.scitex/scholar/library/myproject -> "myproject"
                self.project = project.name if project.is_dir() else project.stem
                # Set library_dir to parent if it's named 'library'
                if project.parent.name == 'library':
                    self.config.library_dir = str(project.parent)
        else:
            # Standard project name
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

    def _extract_primitive(self, value):
        """Extract primitive value from DotDict or nested structure."""
        from scitex.dict import DotDict

        if value is None:
            return None
        if isinstance(value, DotDict):
            # Convert DotDict to plain dict first
            value = dict(value)
        if isinstance(value, dict):
            # For nested dict structures, return as-is (will be handled by save_resolved_paper)
            return value
        # Return primitive types as-is
        return value

    def save_paper(self, paper: "Paper", force: bool = False) -> str:
        """Save paper to library with explicit parameters.

        Supports both old flat Paper and new Pydantic Paper structures.
        """
        # Check if this is a Pydantic Paper (has metadata attribute)
        if hasattr(paper, 'metadata'):
            # New Pydantic Paper structure
            return self._library_manager.save_resolved_paper(
                # Required fields
                title=paper.metadata.basic.title or '',
                doi=paper.metadata.id.doi or '',

                # Optional bibliographic fields
                year=paper.metadata.basic.year,
                authors=paper.metadata.basic.authors,
                journal=paper.metadata.publication.journal,
                abstract=paper.metadata.basic.abstract,

                # Additional bibliographic fields
                volume=paper.metadata.publication.volume,
                issue=paper.metadata.publication.issue,
                pages=f"{paper.metadata.publication.first_page or ''}-{paper.metadata.publication.last_page or ''}" if paper.metadata.publication.first_page else None,
                publisher=paper.metadata.publication.publisher,
                issn=paper.metadata.publication.issn,

                # Enrichment fields
                citation_count=paper.metadata.citation_count.total,
                impact_factor=paper.metadata.publication.impact_factor,

                # Library management
                library_id=paper.container.library_id,
                project=self.project,
            )
        else:
            # Old flat Paper structure (legacy support)
            paper_dict = paper.to_dict() if hasattr(paper, 'to_dict') else {}

            return self._library_manager.save_resolved_paper(
                # Required fields
                title=self._extract_primitive(getattr(paper, 'title', paper_dict.get('title', ''))),
                doi=self._extract_primitive(getattr(paper, 'doi', paper_dict.get('doi', ''))),

                # Optional bibliographic fields
                year=self._extract_primitive(getattr(paper, 'year', paper_dict.get('year'))),
                authors=self._extract_primitive(getattr(paper, 'authors', paper_dict.get('authors'))),
                journal=self._extract_primitive(getattr(paper, 'journal', paper_dict.get('journal'))),
                abstract=self._extract_primitive(getattr(paper, 'abstract', paper_dict.get('abstract'))),

                # Additional bibliographic fields
                volume=self._extract_primitive(getattr(paper, 'volume', paper_dict.get('volume'))),
                issue=self._extract_primitive(getattr(paper, 'issue', paper_dict.get('issue'))),
                pages=self._extract_primitive(getattr(paper, 'pages', paper_dict.get('pages'))),
                publisher=self._extract_primitive(getattr(paper, 'publisher', paper_dict.get('publisher'))),
                issn=self._extract_primitive(getattr(paper, 'issn', paper_dict.get('issn'))),

                # Enrichment fields
                citation_count=self._extract_primitive(getattr(paper, 'citation_count', paper_dict.get('citation_count'))),
                impact_factor=self._extract_primitive(getattr(paper, 'journal_impact_factor', paper_dict.get('journal_impact_factor'))),

                # Source tracking
                doi_source=self._extract_primitive(getattr(paper, 'doi_source', paper_dict.get('doi_source'))),
                title_source=self._extract_primitive(getattr(paper, 'title_source', paper_dict.get('title_source'))),
                abstract_source=self._extract_primitive(getattr(paper, 'abstract_source', paper_dict.get('abstract_source'))),

                # Library management
                library_id=self._extract_primitive(getattr(paper, 'library_id', paper_dict.get('library_id'))),
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
