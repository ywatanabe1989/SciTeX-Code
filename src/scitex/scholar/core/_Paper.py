#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 17:05:25 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/_Paper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/_Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Paper class for SciTeX Scholar module.

Represents a scientific paper with comprehensive metadata and methods.
"""

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import log
from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig

logger = log.getLogger(__name__)


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
        # URLs
        url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        # File references
        pdf_path: Optional[Path] = None,
        # Source information
        source: Optional[str] = None,
        # Extension point
        metadata: Optional[Dict[str, Any]] = None,
        # Library integration (enhanced)
        library_id: Optional[str] = None,
        project: Optional[str] = None,
        config: Optional["ScholarConfig"] = None,
    ):
        """Initialize paper with comprehensive metadata."""

        # Library integration (enhanced)
        self.library_id = library_id
        self.project = project

        # Initialize configuration
        self.config = config if config else ScholarConfig()

        # Initialize storage managers (lazy loading)
        self._library_manager = None
        self._library_cache_manager = None

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

        # URLs
        self._set_field_with_source("url", url)
        self._set_field_with_source("pdf_url", pdf_url)

        # File references
        self._set_field_with_source("pdf_path", pdf_path)

        # Source information
        self._set_field_with_source("source", source)

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
            from .metadata.enrichment._MetadataEnricher import JCR_YEAR

            if self.impact_factor is not None:
                # Only add if it's a real value (not 0.0)
                if self.impact_factor > 0:
                    lines.append(
                        f"  impact_factor = {{{self.impact_factor}}},"
                    )
                    # Add impact factor source as JCR_YEAR
                    lines.append(
                        f"  impact_factor_source = {{JCR_{JCR_YEAR}}},"
                    )

            if self.journal_quartile and self.journal_quartile != "Unknown":
                lines.append(
                    f"  journal_quartile = {{{self.journal_quartile}}},"
                )
                # Add quartile source
                lines.append(f"  quartile_source = {{JCR_{JCR_YEAR}}},")
                quartile_source = self.metadata.get("quartile_source")
                if quartile_source:
                    lines.append(f"  quartile_source = {{{quartile_source}}},")

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary format."""
        return {
            # Core identifiers
            "doi": self.doi,
            "title": self.title,
            "authors": self.authors,
            # Publication details
            "journal": self.journal,
            "year": self.year,
            "abstract": self.abstract,
            # Alternative identifiers
            "pmid": self.pmid,
            "arxiv_id": self.arxiv_id,
            # Additional metadata
            "keywords": self.keywords,
            "citation_count": self.citation_count,
            "impact_factor": self.impact_factor,
            "journal_quartile": self.journal_quartile,
            # URLs
            "url": self.url,
            "pdf_url": self.pdf_url,
            # File references
            "pdf_path": str(self.pdf_path) if self.pdf_path else None,
            # Source information
            "source": self.source,
            # Library integration
            "library_id": self.library_id,
            # Extension metadata
            **self._additional_metadata,
        }

    def to_bibtex(self, include_enriched: bool = True) -> str:
        """Convert paper to BibTeX format.

        Args:
            include_enriched: Include enriched metadata (impact factor, etc.)

        Returns:
            BibTeX formatted string
        """
        return self._to_bibtex(include_enriched=include_enriched)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get additional metadata dictionary."""
        return self._additional_metadata

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

    @property
    def library_manager(self):
        """Get library manager instance (lazy loading)."""
        if self._library_manager is None:
            from scitex.scholar.storage import LibraryManager

            self._library_manager = LibraryManager(
                project=self.project, config=self.config
            )
        return self._library_manager

    @property
    def library_cache_manager(self):
        """Get library cache manager instance (lazy loading)."""
        if self._library_cache_manager is None:
            from scitex.scholar.storage import LibraryCacheManager

            self._library_cache_manager = LibraryCacheManager(
                project=self.project, config=self.config
            )
        return self._library_cache_manager

    def save_to_library(self, force: bool = False) -> str:
        """Save paper to the Scholar library system.

        This stores the paper in the centralized library with proper ID generation,
        metadata persistence, and project organization.

        Returns:
            str: The generated library ID for the paper
        """
        if not self.title:
            raise ValueError("Paper must have a title to save to library")

        # Generate or use existing library ID
        if not self.library_id:
            storage_path, readable_name, paper_id = (
                self.config.paths.get_paper_storage_paths(
                    doi=self.doi,
                    title=self.title,
                    authors=self.authors,
                    journal=self.journal,
                    year=self.year,
                    project=self.project or "MASTER",
                )
            )
            self.library_id = paper_id

        # Save to library using LibraryManager
        self.library_manager.save_resolved_paper(
            title=self.title,
            doi=self.doi,
            year=self.year,
            authors=self.authors,
            journal=self.journal,
            abstract=self.abstract,
            metadata=self.to_dict(),
            paper_id=self.library_id,
        )

        logger.info(f"Paper saved to library with ID: {self.library_id}")
        return self.library_id

    def load_from_library(self, library_id: str) -> None:
        """Load paper data from library by ID.

        Args:
            library_id: The 8-character library ID
        """
        master_dir = self.config.get_library_master_dir()
        paper_dir = master_dir / library_id
        metadata_file = paper_dir / "metadata.json"

        if not metadata_file.exists():
            raise ScholarError(f"Paper not found in library: {library_id}")

        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Update paper fields from library metadata
        for field, value in metadata.items():
            if hasattr(self, field) and field not in [
                "config",
                "_library_manager",
                "_library_cache_manager",
            ]:
                setattr(self, field, value)

        self.library_id = library_id
        logger.info(f"Paper loaded from library: {library_id}")

    @classmethod
    def from_library(
        cls, library_id: str, config: Optional["ScholarConfig"] = None
    ) -> "Paper":
        """Create Paper instance from library by ID.

        Args:
            library_id: The 8-character library ID
            config: Scholar configuration

        Returns:
            Paper instance loaded from library
        """
        paper = cls(config=config, library_id=library_id)
        paper.load_from_library(library_id)
        return paper

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


if __name__ == "__main__":

    def main():
        """Demonstrate Paper class usage with storage integration."""
        print("=" * 60)
        print("Paper Class Demo - Individual Publication Storage")
        print("=" * 60)

        # Create a sample paper
        paper = Paper(
            title="Attention Is All You Need",
            authors=["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki"],
            journal="Advances in Neural Information Processing Systems",
            year=2017,
            doi="10.5555/3295222.3295349",
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
            keywords=["transformer", "attention", "neural networks"],
            citation_count=50000,
            project="transformer_papers",
        )

        print("1. Created Paper:")
        print(f"   {paper}")
        print(f"   DOI: {paper.doi}")
        print(f"   Authors: {len(paper.authors)} authors")
        print()

        # Demonstrate BibTeX conversion
        print("2. BibTeX Format:")
        bibtex = paper.to_bibtex()
        print("   " + "\n   ".join(bibtex.split("\n")[:8]) + "...")
        print()

        # Demonstrate dictionary conversion
        print("3. Dictionary Format:")
        paper_dict = paper.to_dict()
        print(f"   Keys: {list(paper_dict.keys())[:8]}...")
        print()

        # Demonstrate similarity checking
        similar_paper = Paper(
            title="Attention is All You Need",  # Slight variation
            authors=["Vaswani, A.", "Shazeer, N."],
            year=2017,
        )

        similarity = paper.similarity_score(similar_paper)
        print(f"4. Similarity Score: {similarity:.2f} (with similar paper)")
        print()

        # Demonstrate storage operations
        print("5. Storage Operations:")
        try:
            # Save to library
            library_id = paper.save_to_library()
            print(f"   ✅ Saved to library with ID: {library_id}")

            # Load from library
            loaded_paper = Paper.from_library(library_id)
            print(f"   ✅ Loaded from library: {loaded_paper.title[:50]}...")

            # Verify they match
            match_score = paper.similarity_score(loaded_paper)
            print(
                f"   ✅ Storage integrity check: {match_score:.2f} similarity"
            )

        except Exception as e:
            print(f"   ⚠️  Storage demo skipped: {e}")

        print()

        # Demonstrate file saving
        print("6. File Export:")
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                suffix=".bib", delete=False
            ) as tmp:
                paper.save(tmp.name, format="bibtex")
                print(f"   ✅ Saved to file: {tmp.name}")

            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as tmp:
                paper.save(tmp.name, format="json")
                print(f"   ✅ Saved to file: {tmp.name}")

        except Exception as e:
            print(f"   ⚠️  File export demo skipped: {e}")

        print()
        print("Paper demo completed! ✨")
        print()

    main()

# python -m scitex.scholar.core._Paper

# EOF
