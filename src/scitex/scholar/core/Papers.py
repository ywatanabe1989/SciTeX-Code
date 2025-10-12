#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 22:24:29 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/Papers.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Papers class for SciTeX Scholar module.

Papers is a simple collection of Paper objects.
All business logic is handled by Scholar or utility functions.

This is a simplified version - reduced from 39 methods to ~15 methods.
Business logic has been moved to Scholar and utility functions.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.core.Paper import Paper

logger = logging.getLogger(__name__)


class Papers:
    """A simple collection of Paper objects.

    This is a minimal collection class. Most business logic
    (loading, saving, enrichment, etc.) is handled by Scholar.

    Methods have been reduced from 39 to ~15 for simplicity.
    Complex operations should use Scholar or utility functions.
    """

    def __init__(
        self,
        papers: Optional[Union[List[Paper], List[Dict]]] = None,
        project: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize Papers collection.

        Args:
            papers: List of Paper objects or dicts to convert to Papers
            project: Project name for organizing papers
            config: Scholar configuration
        """
        self.project = project or "default"
        self.config = config or ScholarConfig()

        # Initialize papers list
        self._papers: List[Paper] = []

        if papers:
            for item in papers:
                if isinstance(item, Paper):
                    self._papers.append(item)
                elif isinstance(item, dict):
                    # Handle dict input - Pydantic handles validation
                    paper = Paper.from_dict(item)
                    self._papers.append(paper)
                else:
                    logger.warning(f"Skipping invalid item type: {type(item)}")

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
        """Get paper(s) by index or slice.

        Args:
            index: Integer index or slice

        Returns:
            Single Paper if integer index, Papers collection if slice
        """
        if isinstance(index, slice):
            return Papers(
                self._papers[index], project=self.project, config=self.config
            )
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

    def __dir__(self) -> List[str]:
        """Custom dir for better discoverability."""
        base_attrs = object.__dir__(self)
        custom_attrs = [
            "papers",
            "filter",
            "sort_by",
            "append",
            "extend",
            "to_list",
            "summary",
            "to_dict",
            "to_dataframe",
            "from_bibtex",
            "save",
        ]
        return sorted(set(base_attrs + custom_attrs))

    # =========================================================================
    # SIMPLE COLLECTION OPERATIONS
    # =========================================================================

    @property
    def papers(self) -> List[Paper]:
        """Get the underlying papers list."""
        return self._papers

    def append(self, paper: Paper) -> None:
        """Add a paper to the collection.

        Args:
            paper: Paper to add
        """
        if isinstance(paper, Paper):
            self._papers.append(paper)
        else:
            logger.warning(f"Cannot append non-Paper object: {type(paper)}")

    def extend(self, papers: Union[List[Paper], "Papers"]) -> None:
        """Add multiple papers to the collection.

        Args:
            papers: List of papers or another Papers collection
        """
        if isinstance(papers, Papers):
            self._papers.extend(papers._papers)
        elif isinstance(papers, list):
            for paper in papers:
                if isinstance(paper, Paper):
                    self._papers.append(paper)
        else:
            logger.warning(f"Cannot extend with type: {type(papers)}")

    def to_list(self) -> List[Paper]:
        """Get papers as a list.

        Returns:
            List of Paper objects
        """
        return list(self._papers)

    def filter(
        self,
        condition: Optional[Callable[[Paper], bool]] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        has_doi: Optional[bool] = None,
        has_abstract: Optional[bool] = None,
        has_pdf: Optional[bool] = None,
        min_citations: Optional[int] = None,
        max_citations: Optional[int] = None,
        min_impact_factor: Optional[float] = None,
        max_impact_factor: Optional[float] = None,
        journal: Optional[str] = None,
        author: Optional[str] = None,
        keyword: Optional[str] = None,
        publisher: Optional[str] = None,
        **kwargs,
    ) -> "Papers":
        """Filter papers by condition or criteria.

        Args:
            condition: Function that takes a Paper and returns bool
            year_min: Minimum year
            year_max: Maximum year
            has_doi: Filter papers with/without DOI
            has_abstract: Filter papers with/without abstract
            has_pdf: Filter papers with/without PDF URL
            min_citations: Minimum citation count
            max_citations: Maximum citation count
            min_impact_factor: Minimum journal impact factor
            max_impact_factor: Maximum journal impact factor
            journal: Journal name (partial match)
            author: Author name (partial match)
            keyword: Keyword (searches in keywords, title, abstract)
            publisher: Publisher name (partial match)
            **kwargs: Additional keyword arguments for backward compatibility

        Returns:
            New Papers collection with filtered papers

        Examples:
            # Using lambda condition with Paper fields
            # Available Paper fields: title, authors, year, abstract, keywords,
            # doi, pmid, arxiv_id, journal, volume, issue, pages, publisher,
            # citation_count, journal_impact_factor, url, pdf_url, etc.

            # Filter by single condition
            high_impact = papers.filter(lambda p: p.journal_impact_factor and p.journal_impact_factor > 10)
            highly_cited = papers.filter(lambda p: p.citation_count and p.citation_count > 500)
            recent = papers.filter(lambda p: p.year and p.year >= 2020)

            # Complex conditions
            elite = papers.filter(
                lambda p: p.journal_impact_factor and p.journal_impact_factor > 10
                         and p.citation_count and p.citation_count > 500
            )

            # Using built-in parameters
            high_impact_v2 = papers.filter(min_impact_factor=10.0)
            highly_cited_v2 = papers.filter(min_citations=500)
            recent_v2 = papers.filter(year_min=2020)

            # Combining multiple parameters
            filtered = papers.filter(
                min_impact_factor=5.0,
                min_citations=100,
                year_min=2015,
                year_max=2023,
                journal="Nature",
                has_doi=True
            )

            # Range filtering
            mid_impact = papers.filter(min_impact_factor=3.0, max_impact_factor=10.0)
            mid_citations = papers.filter(min_citations=100, max_citations=1000)

            # Keyword search (searches in keywords, title, and abstract)
            ml_papers = papers.filter(keyword="machine learning")
            eeg_papers = papers.filter(keyword="EEG")

            # Journal and author filtering
            nature_papers = papers.filter(journal="Nature")  # Partial match
            smith_papers = papers.filter(author="Smith")     # Partial match

            # Boolean filters
            with_doi = papers.filter(has_doi=True)
            with_abstract = papers.filter(has_abstract=True)
            with_pdf = papers.filter(has_pdf=True)

            # Chain filters for AND logic
            elite_recent = papers.filter(min_impact_factor=10).filter(year_min=2020)
        """
        # If a lambda/function condition is provided, use it
        if condition is not None and callable(condition):
            filtered = [p for p in self._papers if condition(p)]
            logger.info(
                f"Lambda filter: {len(self._papers)} -> {len(filtered)} papers"
            )
            return Papers(filtered, project=self.project, config=self.config)

        # Otherwise use criteria-based filtering
        from scitex.scholar.utils.papers_utils import filter_papers_advanced

        result = filter_papers_advanced(
            self,
            year_min=year_min,
            year_max=year_max,
            has_doi=has_doi,
            has_abstract=has_abstract,
            has_pdf=has_pdf,
            min_citations=min_citations or kwargs.get("min_citations"),
            max_citations=max_citations or kwargs.get("max_citations"),
            min_impact_factor=min_impact_factor
            or kwargs.get("min_impact_factor"),
            max_impact_factor=max_impact_factor
            or kwargs.get("max_impact_factor"),
            journal=journal,
            author=author,
            keyword=keyword,
            publisher=publisher,
        )

        # Preserve project and config
        result.project = self.project
        result.config = self.config

        logger.info(f"Filtered: {len(self._papers)} -> {len(result)} papers")
        return result

    def sort_by(self, *criteria, reverse: bool = False, **kwargs) -> "Papers":
        """Sort papers by criteria.

        Args:
            *criteria: Field names (as strings) or lambda functions to sort by
            reverse: Sort in descending order (default: False)
            **kwargs: Additional options

        Returns:
            New sorted Papers collection

        Available Paper fields for sorting:
            - 'title': Paper title
            - 'year': Publication year
            - 'citation_count': Number of citations
            - 'journal_impact_factor': Journal impact factor
            - 'journal': Journal name
            - 'publisher': Publisher name
            - 'doi': Digital Object Identifier
            - 'created_at': When record was created
            - 'updated_at': When record was last updated

        Examples:
            # Sort by single field (ascending)
            by_year = papers.sort_by('year')
            by_title = papers.sort_by('title')

            # Sort by single field (descending)
            by_citations_desc = papers.sort_by('citation_count', reverse=True)
            by_impact_desc = papers.sort_by('journal_impact_factor', reverse=True)

            # Sort by multiple fields (primary, secondary, etc.)
            by_year_then_citations = papers.sort_by('year', 'citation_count')

            # Using lambda functions for custom sorting
            by_citations = papers.sort_by(lambda p: p.citation_count or 0, reverse=True)
            by_impact = papers.sort_by(lambda p: p.journal_impact_factor or 0, reverse=True)

            # Complex sorting with null handling
            by_year_safe = papers.sort_by(lambda p: p.year if p.year else 9999)

            # Sort by computed values
            by_citation_per_year = papers.sort_by(
                lambda p: (p.citation_count or 0) / (2024 - p.year) if p.year else 0,
                reverse=True
            )

            # Top papers by impact factor
            top_impact = papers.sort_by('journal_impact_factor', reverse=True)
            for p in top_impact[:10]:
                print(f"IF={p.journal_impact_factor:.1f} - {p.journal}")

            # Top papers by citations
            top_cited = papers.sort_by('citation_count', reverse=True)
            for p in top_cited[:10]:
                print(f"{p.citation_count} citations - {p.title[:50]}...")
        """
        if not criteria:
            return Papers(
                self._papers, project=self.project, config=self.config
            )

        # Handle single lambda
        if len(criteria) == 1 and callable(criteria[0]):
            sorted_papers = sorted(
                self._papers, key=criteria[0], reverse=reverse
            )
            return Papers(
                sorted_papers, project=self.project, config=self.config
            )

        # Handle field names
        from scitex.scholar.utils.papers_utils import sort_papers_multi

        return sort_papers_multi(self, list(criteria), reverse=reverse)

    # =========================================================================
    # BACKWARD COMPATIBILITY METHODS
    # These delegate to utilities or Scholar for the actual implementation
    # =========================================================================

    @classmethod
    def from_bibtex(cls, bibtex_input: Union[str, Path]) -> "Papers":
        """Load papers from BibTeX.

        DEPRECATED: Use Scholar.from_bibtex() instead.
        This method is kept for backward compatibility.

        Args:
            bibtex_input: Path to BibTeX file or BibTeX string

        Returns:
            Papers collection
        """
        logger.warning(
            "Papers.from_bibtex() is deprecated. Use Scholar.from_bibtex() instead."
        )

        # Check if it's a file path
        if isinstance(bibtex_input, (str, Path)):
            path = Path(bibtex_input)
            if path.exists():
                return cls._from_bibtex_file(path)

        # Otherwise treat as BibTeX text
        return cls._from_bibtex_text(str(bibtex_input))

    @classmethod
    def _from_bibtex_file(cls, file_path: Union[str, Path]) -> "Papers":
        """Load papers from BibTeX file.

        Args:
            file_path: Path to BibTeX file

        Returns:
            Papers collection
        """
        import bibtexparser

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"BibTeX file not found: {file_path}")

        logger.info(f"Loading BibTeX from {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        logger.info(
            f"Loaded {len(bib_db.entries)} BibTeX entries from {file_path}"
        )

        papers = []
        for entry in bib_db.entries:
            paper = cls._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)

        logger.success(f"Created {len(papers)} papers from BibTeX file")
        return cls(papers)

    @classmethod
    def _from_bibtex_text(cls, bibtex_content: str) -> "Papers":
        """Load papers from BibTeX text.

        Args:
            bibtex_content: BibTeX content as string

        Returns:
            Papers collection
        """
        import bibtexparser

        bib_db = bibtexparser.loads(bibtex_content)
        logger.info(f"Parsed {len(bib_db.entries)} BibTeX entries from text")

        papers = []
        for entry in bib_db.entries:
            paper = cls._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)

        logger.success(f"Created {len(papers)} papers from BibTeX text")
        return cls(papers)

    @staticmethod
    def _bibtex_entry_to_paper(entry: Dict[str, Any]) -> Paper:
        """Convert BibTeX entry to Paper object.

        Args:
            entry: BibTeX entry dictionary

        Returns:
            Paper object
        """
        # Get fields from BibTeX entry
        fields = {k.lower(): v for k, v in entry.items()}

        # Parse authors
        authors = []
        if "author" in fields:
            author_str = fields["author"]
            authors = [a.strip() for a in author_str.split(" and ")]

        # Parse year - let Pydantic handle validation
        year = None
        if "year" in fields:
            year_str = str(fields["year"])
            if year_str.isdigit():
                year = int(year_str)

            # Parse keywords
            keywords = []
            if "keywords" in fields:
                keywords = [k.strip() for k in fields["keywords"].split(",")]

            # Create structured data for Paper
            basic_data = {
                "title": fields.get("title", "").strip("{}"),
                "authors": authors,
                "abstract": fields.get("abstract", ""),
                "year": year,
                "keywords": keywords,
            }

            id_data = {
                "doi": fields.get("doi"),
                "pmid": fields.get("pmid"),
                "arxiv_id": fields.get("arxiv"),
            }

            publication_data = {
                "journal": fields.get("journal"),
            }

            url_data = {
                "pdf": fields.get("url"),
            }

            # Create Paper with Pydantic structure
            paper = Paper()

            # Set basic metadata
            paper.metadata.basic.title = basic_data.get("title", "")
            paper.metadata.basic.authors = basic_data.get("authors")
            paper.metadata.basic.abstract = basic_data.get("abstract")
            paper.metadata.basic.year = basic_data.get("year")
            paper.metadata.basic.keywords = basic_data.get("keywords")

            # Set ID metadata
            if id_data.get("doi"):
                paper.metadata.set_doi(id_data["doi"])
            paper.metadata.id.pmid = id_data.get("pmid")
            paper.metadata.id.arxiv_id = id_data.get("arxiv_id")

            # Set publication metadata
            paper.metadata.publication.journal = publication_data.get("journal")

            # Set URL metadata
            if url_data.get("pdf"):
                paper.metadata.url.pdfs.append({"url": url_data["pdf"], "source": "bibtex"})

            # Store original BibTeX fields for later reconstruction
            paper._original_bibtex_fields = fields.copy()
            paper._bibtex_entry_type = entry.get("entry_type", "misc")
            paper._bibtex_key = entry.get("key", "")

            return paper

    def save(
        self,
        output_path: Union[str, Path],
        format: Optional[str] = "auto",
        **kwargs,
    ) -> None:
        """Save papers to file.

        DEPRECATED: Use Scholar.save_papers() or Scholar.export_bibtex() instead.
        This method is kept for backward compatibility.

        Args:
            output_path: Path to save file
            format: Output format (auto, bibtex, json, csv)
            **kwargs: Additional options
        """
        logger.warning(
            "Papers.save() is deprecated. Use Scholar.export_bibtex() instead."
        )

        output_path = Path(output_path)

        # Auto-detect format from extension
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

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "bibtex":
            from scitex.scholar.utils.papers_utils import papers_to_bibtex

            bibtex_content = papers_to_bibtex(self, output_path=None)
            output_path.write_text(bibtex_content)
            logger.success(f"Saved {len(self)} papers to {output_path}")

        elif format.lower() == "json":
            import json

            from scitex.scholar.utils.papers_utils import papers_to_dict

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    papers_to_dict(self), f, indent=2, ensure_ascii=False
                )
            logger.success(f"Saved {len(self)} papers to {output_path}")

        elif format.lower() == "csv":
            from scitex.scholar.utils.papers_utils import papers_to_dataframe

            df = papers_to_dataframe(self)
            df.to_csv(output_path, index=False)
            logger.success(f"Saved {len(self)} papers to {output_path}")

        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        DEPRECATED: Use papers_utils.papers_to_dict() for new code.

        Returns:
            Dictionary representation
        """
        from scitex.scholar.utils.papers_utils import papers_to_dict

        return papers_to_dict(self)

    def to_dataframe(self) -> Any:
        """Convert to pandas DataFrame.

        DEPRECATED: Use papers_utils.papers_to_dataframe() for new code.

        Returns:
            DataFrame with papers data
        """
        try:
            from scitex.scholar.utils.papers_utils import papers_to_dataframe

            return papers_to_dataframe(self)
        except ImportError:
            logger.error("pandas is required for to_dataframe()")
            return None

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics.

        DEPRECATED: Use papers_utils.papers_statistics() for new code.

        Returns:
            Dictionary with statistics
        """
        from scitex.scholar.utils.papers_utils import papers_statistics

        return papers_statistics(self)

    # =========================================================================
    # METHODS REMOVED (use Scholar or utilities instead):
    # =========================================================================
    # The following methods have been removed to simplify the class:
    # - sync_with_library() -> Use Scholar internally
    # - create_project_symlinks() -> Use Scholar internally
    # - get_project_statistics() -> Use Scholar.get_library_statistics()
    # - download_pdfs() -> Use Scholar.download_pdfs()
    # - enrich() -> Use Scholar.enrich()
    # - merge_papers() -> Use papers_utils.merge_papers()
    # - deduplicate() -> Use papers_utils.deduplicate_papers()
    #
    # This reduces complexity from 39 methods to ~15 methods.
    # All business logic is now in Scholar or utility functions.


# For backward compatibility
__all__ = ["Papers"]


if __name__ == "__main__":

    def main():
        """Demonstrate simplified Papers class."""
        print("=" * 60)
        print("Papers Class - Simplified Collection")
        print("=" * 60)

        # Create test papers
        # Create sample papers with Pydantic structure
        p1 = Paper()
        p1.metadata.basic.title = "Paper 1"
        p1.metadata.basic.year = 2023
        p1.metadata.publication.journal = "Nature"

        p2 = Paper()
        p2.metadata.basic.title = "Paper 2"
        p2.metadata.basic.year = 2024
        p2.metadata.publication.journal = "Science"

        p3 = Paper()
        p3.metadata.basic.title = "Paper 3"
        p3.metadata.basic.year = 2022
        p3.metadata.publication.journal = "Cell"

        papers = Papers([p1, p2, p3])

        print(f"\n1. Collection: {papers}")
        print(f"   Count: {len(papers)}")
        print(f"   First: {papers[0].metadata.basic.title}")

        # Test filtering
        recent = papers.filter(lambda p: p.metadata.basic.year and p.metadata.basic.year >= 2023)
        print(f"\n2. Filtered (year >= 2023): {len(recent)} papers")

        # Test sorting
        sorted_papers = papers.sort_by(lambda p: p.metadata.basic.year or 0)
        print(f"\n3. Sorted by year:")
        for p in sorted_papers:
            print(f"   {p.metadata.basic.year}: {p.metadata.basic.title}")

        print("\n✅ Papers class simplified!")
        print("   - Reduced from 39 to ~15 methods")
        print("   - Business logic moved to Scholar")
        print("   - Clean collection interface")

    main()

# EOF
