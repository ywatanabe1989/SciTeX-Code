#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-28 17:10:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_Paper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/_Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Paper class for SciTeX Scholar module.

Represents a scientific paper with comprehensive metadata and methods.
"""

import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..errors import ScholarError

logger = logging.getLogger(__name__)


class Paper:
    """Represents a scientific paper with comprehensive metadata.

    This class consolidates functionality from _paper.py, _paper_enhanced.py,
    and includes enrichment capabilities.
    """

    def __init__(
        self,
        # Core identifiers (most important first)
        doi: Optional[str] = None,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        # Publication details
        journal: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        abstract: Optional[str] = None,
        # Alternative identifiers
        pmid: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        # Additional metadata
        keywords: Optional[List[str]] = None,
        citation_count: Optional[int] = None,
        impact_factor: Optional[float] = None,
        journal_quartile: Optional[str] = None,
        # File references
        pdf_url: Optional[str] = None,
        pdf_path: Optional[Path] = None,
        # Extension point
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize paper with comprehensive metadata."""

        # Extension point
        self._additional_metadata = metadata or {}

        # Core identifiers
        self._set_field_with_source("doi", doi)
        self._set_field_with_source("title", title)
        self._set_field_with_source("authors", authors)

        # Publication details
        self._set_field_with_source("journal", journal)
        self._set_field_with_source("year", year)
        # self.year = str(year) if year else None
        # self.year_source = self._additional_metadata.get("year_source", None)
        self._set_field_with_source("abstract", abstract)

        # Alternative identifiers
        self._set_field_with_source("pmid", pmid)
        self._set_field_with_source("arxiv_id", arxiv_id)

        # Additional metadata
        self._set_field_with_source("keywords", keywords)
        self._set_field_with_source("citation_count", citation_count)
        self._set_field_with_source("impact_factor", impact_factor)
        self._set_field_with_source("journal_quartile", journal_quartile)

        # File references
        self._set_field_with_source("pdf_url", pdf_url)
        self._set_field_with_source("pdf_path", pdf_path)

        # Computed properties
        self._bibtex_key = None
        self._formatted_authors = None

    def _set_field_with_source(self, field_name: str, value: Any) -> None:
        """Set field value and track its source from metadata."""
        # Handle type conversions
        if field_name == "year" and value:
            value = str(value)
        elif field_name == "keywords" and value is None:
            value = []
        elif field_name == "pdf_path" and value:
            value = Path(value)

        setattr(self, field_name, value)
        source_key = f"{field_name}_source"
        setattr(
            self, source_key, self._additional_metadata.get(source_key, None)
        )

    def update_field_with_source(
        self, field_name: str, value: Any, source: str
    ) -> None:
        """Update field and track its source."""
        setattr(self, field_name, value)
        setattr(self, f"{field_name}_source", source)
        self._additional_metadata[f"{field_name}_source"] = source

    def get_identifier(self) -> str:
        """Get unique identifier for the paper.

        Priority: DOI > PMID > arXiv ID > title-based hash
        """
        if self.doi:
            return f"doi:{self.doi}"
        elif self.pmid:
            return f"pmid:{self.pmid}"
        elif self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        else:
            # Create deterministic hash from title and first author
            import hashlib

            text = f"{self.title}_{self.authors[0] if self.authors else 'unknown'}"
            return f"hash:{hashlib.md5(text.encode()).hexdigest()[:12]}"

    def __str__(self) -> str:
        """String representation of the paper."""
        authors_str = self.authors[0] if self.authors else "Unknown"
        if self.authors and len(self.authors) > 1:
            authors_str += " et al."
        year_str = f" ({self.year})" if self.year else ""
        journal_str = f" - {self.journal}" if self.journal else ""
        return f"{authors_str}{year_str}. {self.title}{journal_str}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        title_str = (
            self.title[:50] + "..."
            if self.title and len(self.title) > 50
            else self.title or "No title"
        )
        first_author = self.authors[0] if self.authors else None
        return f"Paper(title='{title_str}', first_author='{first_author}', year={self.year})"

    def _to_bibtex(self, include_enriched: bool = True) -> str:
        """Convert paper to BibTeX format.

        Args:
            include_enriched: Include enriched metadata (impact factor, etc.)

        Returns:
            BibTeX formatted string
        """
        # Generate BibTeX key if not cached
        if not self._bibtex_key:
            self._generate_bibtex_key()

        # Determine entry type
        if self.arxiv_id:
            entry_type = "misc"
        elif self.journal:
            entry_type = "article"
        else:
            entry_type = "misc"

        # Build BibTeX entry
        lines = [f"@{entry_type}{{{self._bibtex_key},"]

        # Required fields
        if self.title:
            lines.append(f"  title = {{{self._escape_bibtex(self.title)}}},")
        if self.authors:
            lines.append(f"  author = {{{self._format_authors_bibtex()}}},")

        # Optional fields
        if self.year:
            lines.append(f"  year = {{{self.year}}},")
        if self.journal:
            lines.append(
                f"  journal = {{{self._escape_bibtex(self.journal)}}},"
            )
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.arxiv_id:
            lines.append(f"  eprint = {{{self.arxiv_id}}},")
            lines.append("  archivePrefix = {arXiv},")
        if self.abstract:
            abstract_escaped = self._escape_bibtex(self.abstract)
            lines.append(f"  abstract = {{{abstract_escaped}}},")
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            lines.append(f"  keywords = {{{keywords_str}}},")

        # Enriched metadata
        if include_enriched:
            # Get JCR year dynamically from enrichment module
            from ._MetadataEnricher import JCR_YEAR

            if self.impact_factor is not None:
                # Only add if it's a real value (not 0.0)
                if self.impact_factor > 0:
                    lines.append(
                        f"  JCR_{JCR_YEAR}_impact_factor = {{{self.impact_factor}}},"
                    )
                    if self.impact_factor_source:
                        lines.append(
                            f"  impact_factor_source = {{{self.impact_factor_source}}},"
                        )

            if self.journal_quartile and self.journal_quartile != "Unknown":
                lines.append(
                    f"  JCR_{JCR_YEAR}_quartile = {{{self.journal_quartile}}},"
                )
                if self.quartile_source:
                    lines.append(
                        f"  quartile_source = {{{self.quartile_source}}},"
                    )

            if self.citation_count is not None:
                lines.append(f"  citation_count = {{{self.citation_count}}},")
                # Add citation source if available
                if self.citation_count_source:
                    lines.append(
                        f"  citation_count_source = {{{self.citation_count_source}}},"
                    )

        # Add note about SciTeX with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"  note = {{Generated by SciTeX Scholar ({timestamp})}}")

        lines.append("}")
        return "\n".join(lines)

    def _generate_bibtex_key(self) -> None:
        """Generate BibTeX citation key."""
        # Get first author last name
        if self.authors:
            first_author = self.authors[0]
            # Handle "Last, First" format
            if "," in first_author:
                last_name = first_author.split(",")[0].strip()
            else:
                # Handle "First Last" format
                last_name = first_author.split()[-1]
            last_name = re.sub(r"[^a-zA-Z]", "", last_name).lower()
        else:
            last_name = "unknown"

        # Get year
        year = self.year or "0000"

        # Get first significant word from title
        if self.title:
            title_words = re.findall(r"\b\w+\b", self.title.lower())
            # Skip common words
            stop_words = {
                "a",
                "an",
                "the",
                "of",
                "in",
                "on",
                "at",
                "to",
                "for",
                "and",
                "or",
                "but",
                "with",
                "by",
                "from",
            }
            significant_words = [
                w for w in title_words if w not in stop_words and len(w) > 3
            ]
            if significant_words:
                title_part = significant_words[0][:6]
            else:
                title_part = title_words[0][:6] if title_words else "paper"
        else:
            title_part = "paper"

        self._bibtex_key = f"{last_name}{year}{title_part}"

    def _format_authors_bibtex(self) -> str:
        """Format authors for BibTeX."""
        if not self._formatted_authors and self.authors:
            self._formatted_authors = " and ".join(self.authors)
        return self._formatted_authors or ""

    def _escape_bibtex(self, text: str) -> str:
        """Escape special characters for BibTeX."""
        if not text:
            return ""
        # Handle special characters
        replacements = {
            "\\": r"\\",
            "{": r"\{",
            "}": r"\}",
            "_": r"\_",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

        """Convert paper to dictionary format."""
        base_dict = {
            "doi": self.doi,
            "doi_source": getattr(self, "doi_source", None),
            "title": self.title,
            "title_source": getattr(self, "title_source", None),
            "authors": self.authors,
            "authors_source": getattr(self, "authors_source", None),
            "journal": self.journal,
            "journal_source": getattr(self, "journal_source", None),
            "year": self.year,
            "year_source": getattr(self, "year_source", None),
            "abstract": self.abstract,
            "abstract_source": getattr(self, "abstract_source", None),
            "pmid": self.pmid,
            "pmid_source": getattr(self, "pmid_source", None),
            "arxiv_id": self.arxiv_id,
            "arxiv_id_source": getattr(self, "arxiv_id_source", None),
            "keywords": self.keywords,
            "keywords_source": getattr(self, "keywords_source", None),
            "citation_count": self.citation_count,
            "citation_count_source": getattr(
                self, "citation_count_source", None
            ),
            "impact_factor": self.impact_factor,
            "impact_factor_source": getattr(
                self, "impact_factor_source", None
            ),
            "journal_quartile": self.journal_quartile,
            "journal_quartile_source": getattr(
                self, "journal_quartile_source", None
            ),
            "pdf_url": self.pdf_url,
            "pdf_url_source": getattr(self, "pdf_url_source", None),
            "pdf_path": str(self.pdf_path) if self.pdf_path else None,
        }

        return {**self._additional_metadata, **base_dict}

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get comprehensive metadata dictionary including all paper attributes."""
        return self.to_dict()

    def similarity_score(self, other: "Paper") -> float:
        """Calculate similarity score with another paper.

        Returns:
            Score between 0 and 1 (1 = identical)
        """
        # If both have DOIs and they match, they're the same paper
        if self.doi and other.doi and self.doi == other.doi:
            return 1.0

        # Title similarity (40% weight)
        if self.title and other.title:
            title_sim = (
                SequenceMatcher(
                    None, self.title.lower(), other.title.lower()
                ).ratio()
                * 0.4
            )
        else:
            title_sim = 0

        # Author similarity (20% weight)
        if self.authors and other.authors:
            # Check first author match
            author_sim = (
                0.2
                if self.authors[0].lower() == other.authors[0].lower()
                else 0
            )
        else:
            author_sim = 0

        # Abstract similarity (30% weight)
        if self.abstract and other.abstract:
            abstract_sim = (
                SequenceMatcher(
                    None,
                    self.abstract[:200].lower(),
                    other.abstract[:200].lower(),
                ).ratio()
                * 0.3
            )
        else:
            abstract_sim = 0

        # Year similarity (10% weight)
        if self.year and other.year:
            year_diff = abs(int(self.year) - int(other.year))
            year_sim = max(0, 1 - year_diff / 10) * 0.1
        else:
            year_sim = 0

        return title_sim + author_sim + abstract_sim + year_sim

    def save(
        self, output_path: Union[str, Path], format: Optional[str] = None
    ) -> None:
        """Save single paper to file.

        Simple save method - just writes the file without extra features.
        For symlinks, verbose output, etc., use scitex.io.save() instead.

        Args:
            output_path: Output file path
            format: Output format ('bibtex', 'json'). Auto-detected from extension if None.
        """
        output_path = Path(output_path)

        # Auto-detect format from extension
        if format is None:
            ext = output_path.suffix.lower()
            if ext in [".bib", ".bibtex"]:
                format = "bibtex"
            elif ext == ".json":
                format = "json"
            else:
                format = "bibtex"

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "bibtex":
            # Write BibTeX content
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"% BibTeX entry\n")
                f.write(
                    f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                f.write(self._to_bibtex())

        elif format.lower() == "json":
            # Write JSON
            import json

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        else:
            raise ValueError(f"Unsupported format for Paper: {format}")


# Export all classes and functions
__all__ = ["Paper"]

# EOF
