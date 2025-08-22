#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:13:20 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/ScholarLibrary.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/ScholarLibrary.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from difflib import SequenceMatcher
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
        """Save paper to library."""
        return self._library_manager.save_resolved_paper(
            title=paper.title,
            doi=paper.doi,
            year=paper.year,
            authors=paper.authors,
            journal=paper.journal,
            abstract=paper.abstract,
            metadata=paper.to_dict(),
            paper_id=paper.library_id,
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

# EOF
