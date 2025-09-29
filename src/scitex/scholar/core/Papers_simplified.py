#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 06:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/Papers_simplified.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Papers_simplified.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Papers class for SciTeX Scholar module.

Papers is a simple collection of Paper objects.
All business logic is handled by Scholar or utility functions.
"""

from typing import List, Iterator, Union, Optional, Callable, Any, Dict
from pathlib import Path
from scitex.scholar.core.Paper import Paper
from scitex import logging

logger = logging.getLogger(__name__)


class Papers:
    """A simple collection of Paper objects.

    This is a minimal collection class. All business logic
    (loading, saving, enrichment, etc.) is handled by Scholar.
    """

    def __init__(self, papers: Optional[List[Paper]] = None, project: Optional[str] = None, config: Optional[Any] = None):
        """Initialize with a list of papers.

        Args:
            papers: List of Paper objects (or empty list)
            project: Project name (for compatibility)
            config: Config object (for compatibility)
        """
        self._papers = papers or []
        self.project = project  # For compatibility
        self.config = config    # For compatibility

    # =========================================================================
    # BASIC COLLECTION METHODS
    # =========================================================================

    def __len__(self) -> int:
        """Number of papers in collection."""
        return len(self._papers)

    def __iter__(self) -> Iterator[Paper]:
        """Iterate over papers."""
        return iter(self._papers)

    def __getitem__(self, index: Union[int, slice]) -> Union[Paper, "Papers"]:
        """Get paper(s) by index.

        Args:
            index: Integer index or slice

        Returns:
            Single Paper if integer index
            New Papers collection if slice
        """
        if isinstance(index, slice):
            return Papers(self._papers[index], project=self.project, config=self.config)
        return self._papers[index]

    def __repr__(self) -> str:
        """String representation."""
        return f"Papers(count={len(self)}, project={self.project})"

    def __str__(self) -> str:
        """Human-readable string."""
        if len(self) == 0:
            return "Empty Papers collection"
        elif len(self) == 1:
            return f"Papers collection with 1 paper"
        else:
            return f"Papers collection with {len(self)} papers"

    # =========================================================================
    # SIMPLE COLLECTION OPERATIONS
    # =========================================================================

    def append(self, paper: Paper) -> None:
        """Add a paper to the collection.

        Args:
            paper: Paper to add
        """
        self._papers.append(paper)

    def extend(self, papers: Union[List[Paper], "Papers"]) -> None:
        """Add multiple papers to the collection.

        Args:
            papers: List of papers or another Papers collection
        """
        if isinstance(papers, Papers):
            self._papers.extend(papers._papers)
        else:
            self._papers.extend(papers)

    def filter(self, condition: Optional[Callable[[Paper], bool]] = None, **kwargs) -> "Papers":
        """Filter papers by condition or keywords.

        Args:
            condition: Function that takes a Paper and returns bool
            **kwargs: Keyword arguments for filtering (year_min, year_max, etc.)

        Returns:
            New Papers collection with filtered papers
        """
        # If a condition function is provided, use it
        if condition:
            filtered = [p for p in self._papers if condition(p)]
            return Papers(filtered, project=self.project, config=self.config)

        # Otherwise use keyword arguments for backward compatibility
        from scitex.scholar.utils.papers_utils import filter_papers_advanced
        return filter_papers_advanced(self, **kwargs)

    def sort(self, key: Optional[Callable[[Paper], Any]] = None, reverse: bool = False) -> "Papers":
        """Sort papers.

        Args:
            key: Function to extract sort key from Paper
            reverse: Sort in descending order

        Returns:
            New sorted Papers collection
        """
        sorted_papers = sorted(self._papers, key=key, reverse=reverse)
        return Papers(sorted_papers, project=self.project, config=self.config)

    def to_list(self) -> List[Paper]:
        """Get papers as a list.

        Returns:
            List of Paper objects
        """
        return list(self._papers)

    @property
    def papers(self) -> List[Paper]:
        """Get the underlying papers list (for compatibility)."""
        return self._papers

    # =========================================================================
    # BACKWARD COMPATIBILITY METHODS (delegating to utilities/Scholar)
    # =========================================================================

    @classmethod
    def from_bibtex(cls, bibtex_input: Union[str, Path]) -> "Papers":
        """Load papers from BibTeX. DEPRECATED: Use Scholar.from_bibtex()"""
        logger.warning("Papers.from_bibtex() is deprecated. Use Scholar.from_bibtex() instead.")
        from scitex.scholar.utils.papers_utils import papers_from_bibtex_file

        if isinstance(bibtex_input, (str, Path)) and Path(bibtex_input).exists():
            return papers_from_bibtex_file(bibtex_input)
        else:
            # Assume it's BibTeX text
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
                f.write(bibtex_input)
                temp_path = f.name
            try:
                return papers_from_bibtex_file(temp_path)
            finally:
                os.unlink(temp_path)

    def save(self, output_path: Union[str, Path], format: str = "auto", **kwargs) -> None:
        """Save papers to file. DEPRECATED: Use Scholar.save() or Scholar.export_bibtex()"""
        logger.warning("Papers.save() is deprecated. Use Scholar.save() or Scholar.export_bibtex() instead.")

        output_path = Path(output_path)

        if format == "auto":
            ext = output_path.suffix.lower()
            if ext in [".bib", ".bibtex"]:
                format = "bibtex"
            elif ext == ".json":
                format = "json"
            elif ext == ".csv":
                format = "csv"
            else:
                format = "bibtex"

        if format == "bibtex":
            from scitex.scholar.utils.papers_utils import papers_to_bibtex
            papers_to_bibtex(self, output_path)
        elif format == "json":
            from scitex.scholar.utils.papers_utils import papers_to_dict
            import json
            with open(output_path, 'w') as f:
                json.dump(papers_to_dict(self), f, indent=2)
        elif format == "csv":
            from scitex.scholar.utils.papers_utils import papers_to_dataframe
            df = papers_to_dataframe(self)
            df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_dataframe(self) -> Any:
        """Convert to DataFrame. DEPRECATED: Use papers_utils.papers_to_dataframe()"""
        logger.warning("Papers.to_dataframe() is deprecated. Use papers_utils.papers_to_dataframe() instead.")
        from scitex.scholar.utils.papers_utils import papers_to_dataframe
        return papers_to_dataframe(self)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary. DEPRECATED: Use papers_utils.papers_to_dict()"""
        from scitex.scholar.utils.papers_utils import papers_to_dict
        return papers_to_dict(self)

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics. DEPRECATED: Use papers_utils.papers_statistics()"""
        from scitex.scholar.utils.papers_utils import papers_statistics
        return papers_statistics(self)

    # The following methods should be removed completely in future versions:
    # - sync_with_library() -> Scholar internal
    # - create_project_symlinks() -> Scholar internal
    # - download_pdfs() -> Scholar.download_pdfs()
    # - enrich() -> Scholar.enrich()
    # - merge_papers() -> papers_utils.merge_papers()
    # - deduplicate() -> papers_utils.deduplicate_papers()


if __name__ == "__main__":

    def main():
        """Demonstrate simplified Papers class."""
        print("=" * 60)
        print("Papers Class - Simplified Collection Demo")
        print("=" * 60)

        # Create some test papers
        papers = Papers([
            Paper(title="Paper A", year=2023, journal="Nature"),
            Paper(title="Paper B", year=2024, journal="Science"),
            Paper(title="Paper C", year=2022, journal="Cell"),
        ])

        print(f"\n1. Basic collection: {papers}")
        print(f"   Length: {len(papers)}")

        # Filter
        recent = papers.filter(lambda p: p.year >= 2023)
        print(f"\n2. Filter (year >= 2023): {len(recent)} papers")

        # Sort
        by_year = papers.sort(key=lambda p: p.year or 0)
        print(f"\n3. Sorted by year:")
        for p in by_year:
            print(f"   {p.year}: {p.title}")

        print("\n✅ Papers is now a simple collection!")
        print("   - Basic collection operations only")
        print("   - No business logic")
        print("   - All operations through Scholar")

    main()

# EOF