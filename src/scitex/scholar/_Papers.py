#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-28 17:13:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_Papers.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/_Papers.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Papers class for SciTeX Scholar module.

A collection of papers with analysis and export capabilities.
"""

import json
import logging
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import pandas as pd

from ..errors import ScholarError
from ._Paper import Paper

logger = logging.getLogger(__name__)


class Papers:
    """
    A collection of papers with analysis and export capabilities.

    Provides fluent interface for filtering, sorting, and batch operations.
    """

    def __init__(
        self,
        papers: List[Paper],
        auto_deduplicate: bool = True,
        source_priority: List[str] = None,
    ):
        """
        Initialize collection with list of papers.

        Args:
            papers: List of Paper objects
            auto_deduplicate: Automatically remove duplicates (default: True)
            source_priority: List of sources in priority order for deduplication
        """
        self._papers = papers
        self._enriched = False
        self._df_cache = None
        self._source_priority = source_priority

        # Automatically deduplicate unless explicitly disabled
        if auto_deduplicate and papers:
            self._deduplicate_in_place(source_priority=source_priority)

    @classmethod
    def from_bibtex(cls, bibtex_input: Union[str, Path]) -> "Papers":
        """
        Create Papers from BibTeX file path or content string.

        This method intelligently detects whether the input is a file path or
        BibTeX content string and handles it appropriately.

        Args:
            bibtex_input: Either:
                - Path to a BibTeX file (str or Path object)
                - BibTeX content as a string

        Returns:
            Papers instance

        Examples:
            >>> # From file path
            >>> collection = Papers.from_bibtex("papers.bib")
            >>> collection = Papers.from_bibtex(Path("~/refs/papers.bib"))

            >>> # From BibTeX content string
            >>> bibtex_content = '''@article{example2023,
            ...     title = {Example Paper},
            ...     author = {John Doe},
            ...     year = {2023}
            ... }'''
            >>> collection = Papers.from_bibtex(bibtex_content)
        """
        # Detect if input is a file path or content
        is_path = False

        # Convert to string for checking
        input_str = str(bibtex_input)

        # Check if it's likely a path
        if (
            len(input_str) < 500
        ):  # Paths are typically shorter than BibTeX content
            # Check for path-like characteristics
            if (
                input_str.endswith(".bib")
                or input_str.endswith(".bibtex")
                or "/" in input_str
                or "\\" in input_str
                or input_str.startswith("~")
                or input_str.startswith(".")
                or os.path.exists(os.path.expanduser(input_str))
            ):
                is_path = True

        # If it contains @ at the beginning of a line, it's likely content
        if "\n@" in input_str or input_str.strip().startswith("@"):
            is_path = False

        # Delegate to appropriate method
        if is_path:
            return cls._from_bibtex_file(input_str)
        else:
            return cls._from_bibtex_text(input_str)

    @classmethod
    def _from_bibtex_file(cls, file_path: Union[str, Path]) -> "Papers":
        """
        Create Papers from a BibTeX file.

        Args:
            file_path: Path to the BibTeX file

        Returns:
            Papers instance
        """
        # Load from file
        bibtex_path = Path(os.path.expanduser(str(file_path)))
        if not bibtex_path.exists():
            raise ScholarError(f"BibTeX file not found: {bibtex_path}")

        # Use scitex.io to load the file
        from scitex.io import load

        entries = load(str(bibtex_path))
        logger.info(f"Loaded {len(entries)} entries from {bibtex_path}")

        # Convert entries to Paper objects
        papers = []
        for entry in entries:
            paper = cls._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created Papers with {len(papers)} papers from file")
        return cls(papers, auto_deduplicate=True)

    @classmethod
    def _from_bibtex_text(cls, bibtex_content: str) -> "Papers":
        """
        Create Papers from BibTeX content string.

        Args:
            bibtex_content: BibTeX content as a string

        Returns:
            Papers instance
        """
        # Parse BibTeX content directly
        # Write to temp file and load
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bib", delete=False
        ) as f:
            f.write(bibtex_content)
            temp_path = f.name

        try:
            from scitex.io import load

            entries = load(temp_path)
        finally:
            import os

            os.unlink(temp_path)
        logger.info(f"Parsed {len(entries)} entries from BibTeX content")

        # Convert entries to Paper objects
        papers = []
        for entry in entries:
            paper = cls._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created Papers with {len(papers)} papers from text")
        return cls(papers, auto_deduplicate=True)

    @staticmethod
    def _bibtex_entry_to_paper(entry: Dict[str, Any]) -> Optional[Paper]:
        """
        Convert a BibTeX entry dict to a Paper object.

        Args:
            entry: BibTeX entry dictionary with 'entry_type', 'key', and 'fields'

        Returns:
            Paper object or None if conversion fails
        """
        try:
            # Extract fields
            fields = entry.get("fields", {})

            # Required fields
            title = fields.get("title", "")
            if not title:
                logger.warning(
                    f"Skipping entry {entry.get('key', 'unknown')} - no title"
                )
                return None

            # Authors
            author_str = fields.get("author", "")
            authors = []
            if author_str:
                # Split by ' and ' for BibTeX format
                authors = [a.strip() for a in author_str.split(" and ")]

            # Create Paper object
            paper = Paper(
                title=title,
                authors=authors,
                abstract=fields.get("abstract", ""),
                source="bibtex",
                year=fields.get("year"),
                doi=fields.get("doi"),
                pmid=fields.get("pmid"),
                arxiv_id=fields.get(
                    "eprint"
                ),  # arXiv ID often stored as eprint
                journal=fields.get("journal"),
                keywords=(
                    fields.get("keywords", "").split(", ")
                    if fields.get("keywords")
                    else []
                ),
                metadata={
                    "bibtex_key": entry.get("key", ""),
                    "bibtex_entry_type": entry.get("entry_type", "misc"),
                },
            )

            # Store original BibTeX fields for later reconstruction
            paper._original_bibtex_fields = fields.copy()
            paper._bibtex_entry_type = entry.get("entry_type", "misc")
            paper._bibtex_key = entry.get("key", "")

            # Check for enriched metadata
            # Citation count
            if "citation_count" in fields:
                try:
                    paper.citation_count = int(fields["citation_count"])
                    paper.citation_count_source = fields.get(
                        "citation_count_source", "bibtex"
                    )
                except ValueError:
                    pass

            # Impact factor (check various field names)
            for field_name in fields:
                if "impact_factor" in field_name and "JCR" in field_name:
                    try:
                        paper.impact_factor = float(fields[field_name])
                        paper.impact_factor_source = fields.get(
                            "impact_factor_source", "bibtex"
                        )
                        break
                    except ValueError:
                        pass

            # Journal quartile
            for field_name in fields:
                if "quartile" in field_name and "JCR" in field_name:
                    paper.journal_quartile = fields[field_name]
                    paper.quartile_source = fields.get(
                        "quartile_source", "bibtex"
                    )
                    break

            # Additional fields that might be present
            if "volume" in fields:
                paper.volume = fields["volume"]
            if "pages" in fields:
                paper.pages = fields["pages"]
            if "url" in fields:
                paper.pdf_url = fields["url"]

            return paper

        except Exception as e:
            logger.error(f"Error converting BibTeX entry to Paper: {e}")
            return None

    @property
    def papers(self) -> List[Paper]:
        """Get the list of papers."""
        return self._papers

    @property
    def summary(self) -> Dict[str, Any]:
        """
        Get basic summary statistics as a dictionary.

        Returns:
            Dictionary with basic statistics (fast, suitable for properties)

        Examples:
            >>> papers_obj.summary
            {'total': 20, 'sources': {'pubmed': 20}, 'years': {'min': 2020, 'max': 2025}}
        """
        summary_dict = {
            "total": len(self._papers),
            "sources": {},
            "years": None,
            "has_citations": 0,
            "has_impact_factors": 0,
            "has_pdfs": 0,
        }

        if not self._papers:
            return summary_dict

        # Count by source
        for p in self._papers:
            summary_dict["sources"][p.source] = (
                summary_dict["sources"].get(p.source, 0) + 1
            )

        # Year range
        years = [
            int(p.year) for p in self._papers if p.year and p.year.isdigit()
        ]
        if years:
            summary_dict["years"] = {"min": min(years), "max": max(years)}

        # Quick counts
        summary_dict["has_citations"] = sum(
            1 for p in self._papers if p.citation_count is not None
        )
        summary_dict["has_impact_factors"] = sum(
            1 for p in self._papers if p.impact_factor is not None
        )
        summary_dict["has_pdfs"] = sum(
            1 for p in self._papers if p.pdf_url or p.pdf_path
        )

        return summary_dict

    def __len__(self) -> int:
        """Number of papers in collection."""
        return len(self._papers)

    def __iter__(self) -> Iterator[Paper]:
        """Iterate over papers."""
        return iter(self._papers)

    def __getitem__(self, index: Union[int, slice]) -> Union[Paper, "Papers"]:
        """Get paper by index or slice."""
        if isinstance(index, slice):
            return Papers(self._papers[index], auto_deduplicate=False)
        return self._papers[index]

    def __dir__(self) -> List[str]:
        """Return list of attributes for tab completion."""
        # Include all public methods and properties
        return [
            "papers",
            "summary",
            "filter",
            "save",
            "sort_by",
            "summarize",
            "to_dataframe",
            "to_dict",
            "from_bibtex",
        ]

    def __repr__(self) -> str:
        """String representation for REPL."""
        return f"<Papers with {len(self._papers)} papers>"

    def filter(
        self,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_citations: Optional[int] = None,
        max_citations: Optional[int] = None,
        citation_count_min: Optional[int] = None,  # Alias for min_citations
        impact_factor_min: Optional[float] = None,
        open_access_only: bool = False,
        journals: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        title_keywords: Optional[List[str]] = None,
        source: Optional[Union[str, List[str]]] = None,
        has_pdf: Optional[bool] = None,
    ) -> "Papers":
        """
        Filter papers by various criteria.

        Returns new Papers with filtered results.
        """
        filtered = []

        # Handle citation_count_min as alias for min_citations
        if citation_count_min is not None:
            min_citations = citation_count_min

        n_papers_before = len(self._papers)

        for paper in self._papers:
            # Year filters
            if year_min and paper.year:
                try:
                    if int(paper.year) < year_min:
                        continue
                except ValueError:
                    continue

            if year_max and paper.year:
                try:
                    if int(paper.year) > year_max:
                        continue
                except ValueError:
                    continue

            # Citation filters
            if min_citations and (
                not paper.citation_count
                or paper.citation_count < min_citations
            ):
                continue
            if (
                max_citations
                and paper.citation_count
                and paper.citation_count > max_citations
            ):
                continue

            # Impact factor filter
            if impact_factor_min and (
                not paper.impact_factor
                or paper.impact_factor < impact_factor_min
            ):
                continue

            # Open access filter
            if open_access_only and not paper.pdf_url:
                continue

            # PDF availability filter
            if has_pdf is not None:
                if has_pdf and not (paper.pdf_url or paper.pdf_path):
                    continue
                elif not has_pdf and (paper.pdf_url or paper.pdf_path):
                    continue

            # Journal filter
            if journals and paper.journal not in journals:
                continue

            # Author filter
            if authors:
                author_match = any(
                    any(
                        author_name.lower() in paper_author.lower()
                        for paper_author in paper.authors
                    )
                    for author_name in authors
                )
                if not author_match:
                    continue

            # Keyword filter
            if keywords:
                # Check in title, abstract, and keywords
                text_to_search = (
                    f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}"
                ).lower()

                keyword_match = any(
                    keyword.lower() in text_to_search for keyword in keywords
                )
                if not keyword_match:
                    continue

            # Title keywords filter
            if title_keywords and paper.title:
                title_lower = paper.title.lower()
                title_match = any(
                    keyword.lower() in title_lower
                    for keyword in title_keywords
                )
                if not title_match:
                    continue

            # Source filter
            if source:
                sources = [source] if isinstance(source, str) else source
                if paper.source not in sources:
                    continue

            filtered.append(paper)

        logger.info(
            f"Filtered {len(self._papers)} papers to {len(filtered)} papers"
        )

        filted = Papers(filtered, auto_deduplicate=False)

        n_papers_after = len(filted)

        print(f"Filtered: {n_papers_before} -> {n_papers_after} papers")

        return filted

    def sort_by(self, *criteria, **kwargs) -> "Papers":
        """
        Sort papers by multiple criteria.

        Args:
            *criteria: Either:
                - Single string: sort_by('impact_factor')
                - Multiple strings: sort_by('impact_factor', 'year')
                - Tuples of (criteria, reverse): sort_by(('impact_factor', True), ('year', False))
                - Mixed: sort_by('impact_factor', ('year', False))
            **kwargs:
                - reverse: Default reverse setting for all criteria (default True)

        Supported criteria:
            - 'citations' or 'citation_count': Number of citations
            - 'year': Publication year
            - 'impact_factor': Journal impact factor
            - 'title': Paper title (alphabetical)
            - 'journal': Journal name (alphabetical)
            - 'first_author': First author name (alphabetical)
            - 'relevance': Currently uses citation count

        Returns:
            New sorted Papers

        Examples:
            # Sort by impact factor (descending)
            papers.sort_by('impact_factor')

            # Sort by impact factor (desc), then year (desc)
            papers.sort_by('impact_factor', 'year')

            # Sort by impact factor (desc), then year (asc)
            papers.sort_by(('impact_factor', True), ('year', False))

            # Mixed format
            papers.sort_by('impact_factor', ('year', False))
        """
        default_reverse = kwargs.get("reverse", True)

        # Normalize criteria to list of (criterion, reverse) tuples
        normalized_criteria = []
        for criterion in criteria:
            if isinstance(criterion, tuple) and len(criterion) == 2:
                normalized_criteria.append(criterion)
            elif isinstance(criterion, str):
                normalized_criteria.append((criterion, default_reverse))
            else:
                from ..errors import DataError

                raise DataError(
                    f"Invalid sort criterion: {criterion}",
                    context={
                        "criterion": criterion,
                        "valid_criteria": list(criteria.keys()),
                    },
                    suggestion="Use one of: relevance, year, citations, impact_factor",
                )

        # If no criteria specified, default to citations
        if not normalized_criteria:
            normalized_criteria = [("citations", default_reverse)]

        def get_sort_value(paper, criterion):
            """Get the sort value for a paper based on criterion."""
            if criterion in ("citations", "citation_count"):
                return paper.citation_count or 0
            elif criterion == "year":
                try:
                    return int(paper.year) if paper.year else 0
                except ValueError:
                    return 0
            elif criterion == "impact_factor":
                return paper.impact_factor or 0
            elif criterion == "title":
                return paper.title.lower()
            elif criterion == "journal":
                return paper.journal.lower() if paper.journal else ""
            elif criterion == "first_author":
                return paper.authors[0].lower() if paper.authors else ""
            elif criterion == "relevance":
                # Use citation count as proxy for relevance
                return paper.citation_count or 0
            else:
                logger.warning(f"Unknown sort criteria: {criterion}. Using 0.")
                return 0

        # Create sort key function that handles multiple criteria
        def sort_key(paper):
            values = []
            for criterion, reverse in normalized_criteria:
                value = get_sort_value(paper, criterion)
                # For reverse sorting, negate numeric values
                # For strings, we'll handle reverse in the sorted() call
                if reverse and isinstance(value, (int, float)):
                    value = -value
                values.append(value)
            return tuple(values)

        # Sort papers
        # For string criteria with reverse=True, we need special handling
        # This is complex with multiple criteria, so we'll use a different approach
        # We'll build the sort key differently

        # Actually, let's use a cleaner approach with functools
        from functools import cmp_to_key

        def compare_papers(paper1, paper2):
            """Compare two papers based on multiple criteria."""
            for criterion, reverse in normalized_criteria:
                val1 = get_sort_value(paper1, criterion)
                val2 = get_sort_value(paper2, criterion)

                # Compare values
                if val1 < val2:
                    result = -1
                elif val1 > val2:
                    result = 1
                else:
                    result = 0

                # Apply reverse if needed
                if reverse:
                    result = -result

                # If not equal, return the result
                if result != 0:
                    return result

            # All criteria are equal
            return 0

        sorted_papers = sorted(self._papers, key=cmp_to_key(compare_papers))
        return Papers(sorted_papers, auto_deduplicate=False)

    def _calculate_completeness_score(
        self, paper: Paper, source_priority: List[str] = None
    ) -> int:
        """
        Calculate a completeness score for a paper based on available data.
        Higher score = more complete data.

        Args:
            paper: The paper to score
            source_priority: List of sources in priority order (first = highest priority)
        """
        score = 0

        # Basic fields (1 point each)
        if paper.title:
            score += 1
        if paper.authors and len(paper.authors) > 0:
            score += 1
        if paper.abstract and len(paper.abstract) > 50:
            score += 2  # Abstract is valuable
        if paper.year:
            score += 1
        if paper.journal:
            score += 1

        # Identifiers (2 points each - very valuable for lookups)
        if paper.doi:
            score += 2
        if paper.pmid:
            score += 2
        if paper.arxiv_id:
            score += 2

        # Enriched data (1 point each)
        if paper.citation_count is not None:
            score += 1
        if paper.impact_factor is not None:
            score += 1
        if paper.keywords and len(paper.keywords) > 0:
            score += 1
        if paper.pdf_url:
            score += 1

        # Source priority bonus (higher bonus for sources listed first)
        if source_priority and paper.source in source_priority:
            # Give 10 points for first source, 9 for second, etc.
            priority_index = source_priority.index(paper.source)
            score += 10 - priority_index

        return score

    def _merge_papers(
        self, paper1: Paper, paper2: Paper, source_priority: List[str] = None
    ) -> Paper:
        """
        Merge two duplicate papers, keeping the best data from each.

        Args:
            paper1: First paper
            paper2: Second paper
            source_priority: List of sources in priority order (first = highest priority)
        """
        # Determine which paper should be the base (higher completeness score)
        score1 = self._calculate_completeness_score(paper1, source_priority)
        score2 = self._calculate_completeness_score(paper2, source_priority)

        if score1 >= score2:
            base_paper, other_paper = paper1, paper2
        else:
            base_paper, other_paper = paper2, paper1

        # Merge all sources
        all_sources = list(
            set(
                getattr(base_paper, "all_sources", [base_paper.source])
                + getattr(other_paper, "all_sources", [other_paper.source])
            )
        )

        # Create merged paper starting from base
        merged = Paper(
            title=base_paper.title or other_paper.title,
            authors=(
                base_paper.authors
                if base_paper.authors
                else other_paper.authors
            ),
            abstract=(
                base_paper.abstract
                if len(base_paper.abstract or "")
                >= len(other_paper.abstract or "")
                else other_paper.abstract
            ),
            source=base_paper.source,  # Keep the base paper's source
            year=base_paper.year or other_paper.year,
            doi=base_paper.doi or other_paper.doi,
            pmid=base_paper.pmid or other_paper.pmid,
            arxiv_id=base_paper.arxiv_id or other_paper.arxiv_id,
            journal=base_paper.journal or other_paper.journal,
            keywords=list(
                set((base_paper.keywords or []) + (other_paper.keywords or []))
            ),
            citation_count=(
                max(
                    base_paper.citation_count or 0,
                    other_paper.citation_count or 0,
                )
                if (base_paper.citation_count or other_paper.citation_count)
                else None
            ),
            pdf_url=base_paper.pdf_url or other_paper.pdf_url,
            pdf_path=base_paper.pdf_path or other_paper.pdf_path,
            impact_factor=base_paper.impact_factor
            or other_paper.impact_factor,
            journal_quartile=base_paper.journal_quartile
            or other_paper.journal_quartile,
            journal_rank=base_paper.journal_rank or other_paper.journal_rank,
            h_index=base_paper.h_index or other_paper.h_index,
            metadata={
                **other_paper.metadata,
                **base_paper.metadata,
            },  # Base paper metadata takes precedence
        )

        # Set all sources
        merged.all_sources = all_sources
        merged.metadata["all_sources"] = all_sources

        # Keep citation source from the paper that had the citation
        if base_paper.citation_count is not None:
            merged.citation_count_source = base_paper.citation_count_source
        elif other_paper.citation_count is not None:
            merged.citation_count_source = other_paper.citation_count_source

        # Keep impact factor source from the paper that had it
        if base_paper.impact_factor is not None:
            merged.impact_factor_source = base_paper.impact_factor_source
        elif other_paper.impact_factor is not None:
            merged.impact_factor_source = other_paper.impact_factor_source

        # Keep quartile source from the paper that had it
        if base_paper.journal_quartile is not None:
            merged.quartile_source = base_paper.quartile_source
        elif other_paper.journal_quartile is not None:
            merged.quartile_source = other_paper.quartile_source

        return merged

    def _deduplicate_in_place(
        self, threshold: float = 0.85, source_priority: List[str] = None
    ) -> None:
        """
        Remove duplicate papers in-place based on similarity threshold.
        Intelligently merges data from duplicates.

        Args:
            threshold: Similarity threshold (0-1) above which papers are considered duplicates
            source_priority: List of sources in priority order (first = highest priority)
        """
        if not self._papers:
            return

        unique_papers = [self._papers[0]]

        for paper in self._papers[1:]:
            is_duplicate = False

            for i, unique_paper in enumerate(unique_papers):
                if paper.similarity_score(unique_paper) > threshold:
                    is_duplicate = True
                    # Merge the papers instead of just keeping one
                    merged_paper = self._merge_papers(
                        unique_paper, paper, source_priority
                    )
                    unique_papers[i] = merged_paper
                    logger.debug(
                        f"Merged duplicate papers from sources: {merged_paper.all_sources}"
                    )
                    break

            if not is_duplicate:
                unique_papers.append(paper)

        if len(unique_papers) < len(self._papers):
            logger.info(
                f"Deduplicated {len(self._papers)} papers to {len(unique_papers)} unique papers"
            )
            self._papers = unique_papers

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert collection to pandas DataFrame for analysis.

        Returns:
            DataFrame with paper metadata
        """
        if self._df_cache is not None:
            return self._df_cache

        # Import JCR year dynamically to include in column names
        from ._MetadataEnricher import JCR_YEAR

        data = []
        for paper in self._papers:
            row = {
                "title": paper.title,
                "authors": paper.authors if paper.authors else [],
                "year": (
                    int(paper.year)
                    if paper.year and paper.year.isdigit()
                    else None
                ),
                "journal": paper.journal or "N/A",
                "citation_count": (
                    paper.citation_count
                    if paper.citation_count is not None
                    else f"N/A ({getattr(paper, 'citation_count_na_reason', 'Not enriched')})"
                ),
                "citation_count_source": paper.citation_count_source or "N/A",
                # f'JCR_{JCR_YEAR}_impact_factor': paper.impact_factor if paper.impact_factor is not None else 'N/A',
                "impact_factor": (
                    paper.impact_factor
                    if paper.impact_factor is not None
                    else f"N/A ({getattr(paper, 'impact_factor_na_reason', 'Not enriched')})"
                ),
                "impact_factor_source": paper.impact_factor_source or "N/A",
                # f'JCR_{JCR_YEAR}_quartile': paper.journal_quartile or 'N/A',
                "quartile": (
                    paper.journal_quartile
                    if paper.journal_quartile
                    else f"N/A ({getattr(paper, 'journal_quartile_na_reason', 'Not enriched')})"
                ),
                "quartile_source": paper.quartile_source or "N/A",
                "doi": paper.doi or "N/A",
                "pmid": paper.pmid or "N/A",
                "arxiv_id": paper.arxiv_id or "N/A",
                "source": paper.source,
                "has_pdf": bool(paper.pdf_url or paper.pdf_path),
                "pdf_path": str(paper.pdf_path) if paper.pdf_path else "N/A",
                "pdf_source": (
                    paper.pdf_source
                    if hasattr(paper, "pdf_source") and paper.pdf_source
                    else "N/A"
                ),
                "keywords": paper.keywords if paper.keywords else [],
                "abstract": paper.abstract or "N/A",
            }
            data.append(row)

        self._df_cache = pd.DataFrame(data)
        return self._df_cache

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert collection to dictionary format.

        Returns:
            Dictionary with metadata and papers list

        Examples:
            >>> papers_dict = papers.to_dict()
            >>> print(papers_dict['metadata']['total'])
            20
            >>> print(papers_dict['papers'][0]['title'])
            'Example Paper Title'
        """
        return {
            "metadata": {
                "total": len(self._papers),
                "sources": (
                    dict(self.summary["sources"]) if self._papers else {}
                ),
                "years": self.summary["years"],
                "has_citations": self.summary["has_citations"],
                "has_impact_factors": self.summary["has_impact_factors"],
                "has_pdfs": self.summary["has_pdfs"],
                "enriched": self._enriched,
            },
            "papers": [paper.to_dict() for paper in self._papers],
        }

    def save(
        self,
        output_path: Union[str, Path],
        format: Optional[str] = None,
        include_enriched: bool = True,
    ) -> None:
        """
        Save collection to file. Format is auto-detected from extension if not specified.

        Simple save method like numpy.save() - just writes the file without extra features.
        For symlinks, verbose output, etc., use scitex.io.save() instead.

        Args:
            output_path: Output file path
            format: Output format ('bibtex', 'json', 'csv'). Auto-detected from extension if None.
            include_enriched: Include enriched metadata (for bibtex format)

        Examples:
            >>> # Save as BibTeX (auto-detected from extension)
            >>> papers_obj.save("/path/to/references.bib")

            >>> # Save as JSON
            >>> papers_obj.save("/path/to/papers.json")

            >>> # Save as CSV for data analysis
            >>> papers_obj.save("/path/to/papers.csv")

            >>> # Save BibTeX without enriched metadata
            >>> papers_obj.save("refs.bib", include_enriched=False)

            >>> # Explicitly specify format
            >>> papers_obj.save("myfile.txt", format="bibtex")
        """
        output_path = Path(output_path)

        # Auto-detect format from extension if not specified
        if format is None:
            ext = output_path.suffix.lower()
            if ext in [".bib", ".bibtex"]:
                format = "bibtex"
            elif ext == ".json":
                format = "json"
            elif ext == ".csv":
                format = "csv"
            else:
                # Default to bibtex
                format = "bibtex"

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "bibtex":
            # Write BibTeX content directly
            bibtex_content = self._to_bibtex(include_enriched=include_enriched)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"% BibTeX bibliography\n")
                f.write(
                    f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"% Number of entries: {len(self._papers)}\n\n")
                f.write(bibtex_content)

        elif format.lower() == "json":
            # Write JSON directly
            import json

            data = {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "num_papers": len(self._papers),
                    "enriched": self._enriched,
                },
                "papers": [p.to_dict() for p in self._papers],
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format.lower() == "csv":
            # Write CSV directly
            df = self.to_dataframe()
            df.to_csv(output_path, index=False)

        else:
            from ..errors import FileFormatError

            raise FileFormatError(
                filepath=str(filepath),
                expected_format="One of: bib, ris, json, csv, md, xlsx",
                actual_format=format,
            )

    def download_pdfs(
        self,
        scholar=None,
        download_dir: Optional[Union[str, Path]] = None,
        force: bool = False,
        max_workers: int = 4,
        show_progress: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Download PDFs for papers in this collection.

        Args:
            scholar: Scholar instance to use for downloading. If None, creates a new instance.
            download_dir: Directory to save PDFs (default: uses scholar's workspace)
            force: Force re-download even if files exist
            max_workers: Maximum concurrent downloads
            show_progress: Show download progress
            **kwargs: Additional arguments passed to downloader

        Returns:
            Dictionary with download results:
                - 'successful': Number of successful downloads
                - 'failed': Number of failed downloads
                - 'results': List of detailed results
                - 'downloaded_files': Dict mapping DOIs to file paths

        Examples:
            >>> papers = scholar.search("deep learning")
            >>> # Using existing scholar instance
            >>> results = papers.download_pdfs(scholar)
            >>> print(f"Downloaded {results['successful']} PDFs")

            >>> # Or create new scholar instance automatically
            >>> results = papers.download_pdfs(download_dir="./my_pdfs")
        """
        if scholar is None:
            from ._Scholar import Scholar

            scholar = Scholar()

        return scholar.download_pdfs(
            self,
            download_dir=download_dir,
            force=force,
            max_workers=max_workers,
            show_progress=show_progress,
            **kwargs,
        )

    def _to_bibtex_entries(
        self, include_enriched: bool
    ) -> List[Dict[str, Any]]:
        """Convert collection to BibTeX entries format for scitex.io."""
        entries = []
        used_keys = set()

        for paper in self._papers:
            # Ensure unique keys
            paper._generate_bibtex_key()
            original_key = paper._bibtex_key

            counter = 1
            while paper._bibtex_key in used_keys:
                paper._bibtex_key = (
                    f"{original_key}{chr(ord('a') + counter - 1)}"
                )
                counter += 1

            used_keys.add(paper._bibtex_key)

            # Create entry in scitex.io format
            entry = {
                "entry_type": self._determine_entry_type(paper),
                "key": paper._bibtex_key,
                "fields": self._paper_to_bibtex_fields(
                    paper, include_enriched
                ),
            }
            entries.append(entry)

        return entries

    def _determine_entry_type(self, paper: Paper) -> str:
        """Determine BibTeX entry type for a paper."""
        # Use original entry type if available
        if hasattr(paper, "_bibtex_entry_type") and paper._bibtex_entry_type:
            return paper._bibtex_entry_type

        # Otherwise determine based on paper properties
        if paper.arxiv_id:
            return "misc"
        elif paper.journal:
            return "article"
        else:
            return "misc"

    def _paper_to_bibtex_fields(
        self, paper: Paper, include_enriched: bool
    ) -> Dict[str, str]:
        """Convert paper to BibTeX fields dict."""
        fields = {}

        # If paper has original BibTeX fields, start with those
        if hasattr(paper, "_original_bibtex_fields"):
            fields = paper._original_bibtex_fields.copy()

        # Required fields (always override to ensure accuracy)
        fields["title"] = paper.title
        fields["author"] = (
            " and ".join(paper.authors) if paper.authors else "Unknown"
        )

        # Optional fields (only override if we have better data)
        if paper.year:
            fields["year"] = str(paper.year)

        if paper.journal:
            fields["journal"] = paper.journal

        if paper.doi:
            fields["doi"] = paper.doi

        if paper.arxiv_id:
            fields["eprint"] = paper.arxiv_id
            fields["archivePrefix"] = "arXiv"

        if paper.abstract:
            fields["abstract"] = paper.abstract

        if paper.keywords:
            fields["keywords"] = ", ".join(paper.keywords)

        if paper.pdf_url:
            fields["url"] = paper.pdf_url

        # Volume and pages (from original or paper object)
        if hasattr(paper, "volume") and paper.volume:
            fields["volume"] = str(paper.volume)
        if hasattr(paper, "pages") and paper.pages:
            fields["pages"] = str(paper.pages)

        # Enriched metadata
        if include_enriched:
            # Get JCR year dynamically from enrichment module
            from ._MetadataEnricher import JCR_YEAR

            if paper.impact_factor is not None and paper.impact_factor > 0:
                fields[f"JCR_{JCR_YEAR}_impact_factor"] = str(
                    paper.impact_factor
                )
                if paper.impact_factor_source:
                    fields["impact_factor_source"] = paper.impact_factor_source

            if paper.journal_quartile and paper.journal_quartile != "Unknown":
                fields[f"JCR_{JCR_YEAR}_quartile"] = paper.journal_quartile
                if hasattr(paper, "quartile_source") and paper.quartile_source:
                    fields["quartile_source"] = paper.quartile_source

            if paper.citation_count is not None:
                fields["citation_count"] = str(paper.citation_count)
                if paper.citation_count_source:
                    fields["citation_count_source"] = (
                        paper.citation_count_source
                    )

            # Add enrichment note
            enriched_info = []
            if paper.impact_factor is not None and paper.impact_factor > 0:
                enriched_info.append(f"IF={paper.impact_factor}")
            if paper.citation_count is not None:
                enriched_info.append(f"Citations={paper.citation_count}")

            if enriched_info:
                enrichment_note = (
                    f"[SciTeX Enhanced: {', '.join(enriched_info)}]"
                )
                if "note" in fields:
                    fields["note"] = f"{fields['note']}; {enrichment_note}"
                else:
                    fields["note"] = enrichment_note

        return fields

    def _to_json(self) -> str:
        """Convert collection to JSON format."""
        data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_papers": len(self._papers),
                "enriched": self._enriched,
            },
            "papers": [paper.to_dict() for paper in self._papers],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def summarize(self) -> None:
        """
        Print a summary of the paper collection.

        Displays key statistics about the collection including paper counts,
        year distribution, enrichment status, sources, and example papers.

        Returns:
            None (prints to stdout)

        Examples:
            >>> papers_obj.summarize()
            Paper Collection Summary
            ==================================================
            Total papers: 20
            Year range: 2020 - 2025
            ...
        """
        lines = [
            "Paper Collection Summary",
            "=" * 50,
            f"Total papers: {len(self._papers)}",
        ]

        if not self._papers:
            lines.append("(Empty collection)")
            print("\n".join(lines))
            return

        # Get year statistics
        years = [
            int(p.year) for p in self._papers if p.year and p.year.isdigit()
        ]
        if years:
            year_counts = {}
            for year in years:
                year_counts[year] = year_counts.get(year, 0) + 1

            lines.append(f"Year range: {min(years)} - {max(years)}")
            # Show year distribution if varied
            if len(year_counts) > 1 and len(year_counts) <= 10:
                lines.append("\nYear distribution:")
                for year in sorted(year_counts.keys(), reverse=True)[:5]:
                    lines.append(f"  {year}: {year_counts[year]} papers")
                if len(year_counts) > 5:
                    lines.append(
                        f"  ... and {len(year_counts) - 5} more years"
                    )

        # Enrichment statistics
        with_citations = sum(
            1 for p in self._papers if p.citation_count is not None
        )
        with_impact_factor = sum(
            1 for p in self._papers if p.impact_factor is not None
        )
        with_doi = sum(1 for p in self._papers if p.doi)
        with_pdf = sum(1 for p in self._papers if p.pdf_url or p.pdf_path)

        lines.append("\nEnrichment status:")
        if with_citations > 0:
            pct = (with_citations / len(self._papers)) * 100
            lines.append(
                f"  Citation data: {with_citations}/{len(self._papers)} ({pct:.0f}%)"
            )
        if with_impact_factor > 0:
            pct = (with_impact_factor / len(self._papers)) * 100
            lines.append(
                f"  Impact factors: {with_impact_factor}/{len(self._papers)} ({pct:.0f}%)"
            )
        if with_doi > 0:
            pct = (with_doi / len(self._papers)) * 100
            lines.append(
                f"  DOIs: {with_doi}/{len(self._papers)} ({pct:.0f}%)"
            )
        if with_pdf > 0:
            pct = (with_pdf / len(self._papers)) * 100
            lines.append(
                f"  PDFs available: {with_pdf}/{len(self._papers)} ({pct:.0f}%)"
            )

        # Source distribution
        sources = {}
        for p in self._papers:
            sources[p.source] = sources.get(p.source, 0) + 1

        if sources:
            lines.append("\nSources:")
            for source, count in sorted(
                sources.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"  {source}: {count} papers")

        # Top journals if available
        journals = {}
        for p in self._papers:
            if p.journal:
                journals[p.journal] = journals.get(p.journal, 0) + 1

        if journals and len(journals) > 1:
            lines.append("\nTop journals:")
            for journal, count in sorted(
                journals.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                if len(journal) > 50:
                    journal = journal[:47] + "..."
                lines.append(f"  {journal}: {count}")
            if len(journals) > 5:
                lines.append(f"  ... and {len(journals) - 5} more journals")

        # Show a few example papers
        if len(self._papers) > 0:
            lines.append("\nExample papers:")
            for i, paper in enumerate(self._papers[:3]):
                title = (
                    paper.title
                    if len(paper.title) <= 60
                    else paper.title[:57] + "..."
                )
                lines.append(f"  {i+1}. {title}")
                if paper.authors:
                    first_author = (
                        paper.authors[0]
                        if len(paper.authors[0]) <= 20
                        else paper.authors[0][:17] + "..."
                    )
                    author_info = f"{first_author}"
                    if len(paper.authors) > 1:
                        author_info += (
                            f" et al. ({len(paper.authors)} authors)"
                        )
                    lines.append(f"     {author_info}, {paper.year}")
            if len(self._papers) > 3:
                lines.append(f"  ... and {len(self._papers) - 3} more papers")

        print("\n".join(lines))

    def _to_bibtex(self, include_enriched: bool = True) -> str:
        """
        Convert entire collection to BibTeX string.

        Args:
            include_enriched: Include enriched metadata (impact factor, etc.)

        Returns:
            BibTeX formatted string for all papers
        """
        bibtex_entries = []
        used_keys = set()

        for paper in self._papers:
            # Ensure unique keys
            paper._generate_bibtex_key()
            original_key = paper._bibtex_key

            counter = 1
            while paper._bibtex_key in used_keys:
                paper._bibtex_key = (
                    f"{original_key}{chr(ord('a') + counter - 1)}"
                )
                counter += 1

            used_keys.add(paper._bibtex_key)
            bibtex_entries.append(paper._to_bibtex(include_enriched))

        return "\n\n".join(bibtex_entries)


# Export all classes and functions
__all__ = ["Papers"]

# EOF
