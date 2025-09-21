#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 00:04:52 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/Paper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Paper class for SciTeX Scholar module.

Represents a scientific paper with comprehensive metadata and methods."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from scitex import logging
from scitex.dict import DotDict
from scitex.scholar.config import ScholarConfig
from scitex.scholar.engines.utils import (
    BASE_STRUCTURE,
    metadata2bibtex,
    standardize_metadata,
)
from scitex.scholar.storage import ScholarLibrary

# from scitex.scholar.storage import LibraryCacheManager, LibraryManager

logger = logging.getLogger(__name__)


class Paper:
    """Represents a scientific paper with comprehensive metadata.

    This class consolidates functionality from _paper.py, _paper_enhanced.py,
    and includes enrichment capabilities."""

    def __init__(
        self,
        id: Optional[Dict[str, Any]] = None,
        basic: Optional[Dict[str, Any]] = None,
        citation_count: Optional[Dict[str, Any]] = None,
        publication: Optional[Dict[str, Any]] = None,
        url: Optional[Dict[str, Any]] = None,
        path: Optional[Dict[str, Any]] = None,
        system: Optional[Dict[str, Any]] = None,
        library_id: Optional[str] = None,
        project: Optional[str] = None,
        config: Optional["ScholarConfig"] = None,
    ):
        """Initialize paper with complete metadata structure."""

        metadata = {}
        for arg_name, arg_value in [
            ("id", id),
            ("basic", basic),
            ("citation_count", citation_count),
            ("publication", publication),
            ("url", url),
            ("path", path),
            ("system", system),
        ]:
            if arg_value:
                metadata[arg_name] = arg_value

        self._metadata = standardize_metadata(metadata)
        self.library_id = library_id
        self.project = project
        self.config = config or ScholarConfig()
        self.library = ScholarLibrary(project=self.project, config=self.config)
        self._bibtex_key = None

        # Auto-generate properties
        self._create_properties()

    def _create_properties(self):
        """Dynamically create properties from BASE_STRUCTURE."""
        common_fields = [
            "doi",
            "title",
            "authors",
            "year",
            "abstract",
            "journal",
            "pmid",
            "arxiv_id",
            "keywords",
        ]

        for section_name, section_fields in BASE_STRUCTURE.items():
            # Create section-level property
            section_getter = self._make_section_getter(section_name)
            setattr(self.__class__, section_name, property(section_getter))

            # Create common field shortcuts only
            for field_name, _ in section_fields.items():
                if (
                    not field_name.endswith("_engines")
                    and field_name in common_fields
                ):
                    field_getter = self._make_field_getter(
                        section_name, field_name
                    )
                    field_setter = self._make_field_setter(
                        section_name, field_name
                    )
                    setattr(
                        self.__class__,
                        field_name,
                        property(field_getter, field_setter),
                    )

    def _make_section_getter(self, section_name):
        """Create section getter function that returns DotDict."""

        def getter(self):
            return DotDict(self._metadata[section_name])

        return getter

    def _make_field_getter(self, section_name, field_name):
        """Create field getter function."""

        def getter(self):
            return self._metadata[section_name][field_name]

        return getter

    def _make_field_setter(self, section_name, field_name):
        """Create field setter function."""

        def setter(self, value):
            self._metadata[section_name][field_name] = value

        return setter

    def __dir__(self):
        """Custom dir for IPython tab completion."""

        # Get default attributes
        attrs = set(object.__dir__(self))

        # Add section names
        attrs.update(BASE_STRUCTURE.keys())

        # Add field properties
        common_fields = [
            "doi",
            "title",
            "authors",
            "year",
            "abstract",
            "journal",
            "pmid",
            "arxiv_id",
            "keywords",
        ]

        for section_name, section_fields in BASE_STRUCTURE.items():
            for field_name in section_fields.keys():
                if not field_name.endswith("_engines"):
                    prop_name = (
                        field_name
                        if field_name in common_fields
                        else f"{section_name}_{field_name}"
                    )
                    attrs.add(prop_name)

        return sorted(attrs)

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

    def to_bibtex(self, include_enriched: bool = True) -> str:
        """Convert paper to BibTeX format."""
        return metadata2bibtex(self._metadata, key=self._bibtex_key)

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary format."""
        return self._metadata

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary."""
        return self._metadata

    # I think library manager and cache manager should be simply instanciated in __init__
    @property
    def library_manager(self):
        """Get library manager instance (lazy loading)."""
        if self._library_manager is None:
            from scitex.scholar.storage import LibraryManager

            self._library_manager = LibraryManager(
                project=self.project, config=self.config
            )
        return self._library_manager

    def save_to_library(self, force: bool = False) -> str:
        return self.library.save_paper(self, force=force)

    def load_from_library(self, library_id: str) -> None:
        metadata = self.library.load_paper(library_id)
        self._metadata = standardize_metadata(metadata)
        self.library_id = library_id

    @classmethod
    def from_library(
        cls, library_id: str, config: Optional["ScholarConfig"] = None
    ) -> "Paper":
        """Create Paper instance from library by ID."""
        paper = cls(config=config, library_id=library_id)
        paper.load_from_library(library_id)
        return paper

    def save(
        self, output_path: Union[str, Path], format: Optional[str] = "auto"
    ) -> None:
        """Save single paper to file."""
        output_path = Path(output_path)

        if format == "auto":
            ext = output_path.suffix.lower()
            if ext in [".bib", ".bibtex"]:
                format = "bibtex"
            elif ext == ".json":
                format = "json"
            else:
                format = "bibtex"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format.lower() == "bibtex":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"% BibTeX entry\n")
                f.write(
                    f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                f.write(self.to_bibtex())
        elif format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format for Paper: {format}")


# __all__ = ["Paper"]

if __name__ == "__main__":

    def main():
        """Demonstrate Paper class usage with storage integration."""
        print("=" * 60)
        print("Paper Class Demo - Individual Publication Storage")
        print("=" * 60)

        paper = Paper(
            basic={
                "title": "Attention Is All You Need",
                "authors": [
                    "Vaswani, Ashish",
                    "Shazeer, Noam",
                    "Parmar, Niki",
                ],
                "year": "2017",
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
                "keywords": ["transformer", "attention", "neural networks"],
            },
            id={
                "doi": "10.5555/3295222.3295349",
            },
            publication={
                "journal": "Advances in Neural Information Processing Systems",
            },
            citation_count={
                "total": 50000,
            },
            project="transformer_papers",
        )

        print("1. Created Paper:")
        print(f"   {paper}")
        print(f"   DOI: {paper.doi}")
        print(f"   Authors: {len(paper.authors)} authors")
        print()

        print("2. BibTeX Format:")
        bibtex = paper.to_bibtex()
        print("   " + "\n   ".join(bibtex.split("\n")[:8]) + "...")
        print()

        print("3. Dictionary Format:")
        paper_dict = paper.to_dict()
        print(f"   Sections: {list(paper_dict.keys())}")
        print()

        # print(dir(paper))
        # from pprint import pprint
        # pprint(paper.metadata)
        # __import__("ipdb").set_trace()

        print("Paper demo completed! ✨")
        print()

    main()

# python -m scitex.scholar.core.Paper

# EOF
