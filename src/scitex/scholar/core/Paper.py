#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 21:02:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Paper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""Paper class for SciTeX Scholar module.

Paper is a DotDict-based container that mirrors BASE_STRUCTURE exactly.
This ensures single source of truth - Paper structure IS BASE_STRUCTURE.
All operations are handled by utility functions in scitex.scholar.utils.paper_utils.
"""

import copy
from datetime import datetime
from typing import Dict, Optional, Union

from scitex.dict import DotDict
from scitex.scholar.engines.utils import BASE_STRUCTURE


class Paper(DotDict):
    """A scientific paper - DotDict container matching BASE_STRUCTURE exactly.

    This class inherits from DotDict and initializes with BASE_STRUCTURE.
    All operations on papers are handled by:
    - Scholar class for high-level operations
    - Utility functions in paper_utils for conversions

    Usage:
        # Create empty paper with BASE_STRUCTURE
        paper = Paper()

        # Access nested fields naturally
        paper.id.doi = "10.1234/test"
        paper.basic.title = "My Paper"
        paper.basic.authors = ["Smith, J.", "Doe, A."]
        paper.citation_count.total = 85
        paper.citation_count.y2025 = 10
        paper.url.openurl_resolved = "https://..."
        paper.container.library_id = "C74FDF10"

        # Create from existing data
        paper = Paper(data_dict)

        # Convert to plain dict
        plain_dict = paper.to_dict()
    """

    def __init__(self, data: Optional[Union[Dict, DotDict]] = None):
        """Initialize Paper with BASE_STRUCTURE and optional data.

        Args:
            data: Optional dictionary to populate the paper with
        """
        # Start with a deep copy of BASE_STRUCTURE
        structure = copy.deepcopy(BASE_STRUCTURE)

        # Add container section for Paper-specific metadata
        structure["container"] = {
            "library_id": None,
            "scitex_id": None,
            "created_at": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
            "updated_at": datetime.now().isoformat(),
            "project": None,
            "projects": [],
            "master_storage_path": None,
            "readable_name": None,
            "metadata_file": None,
            "pdf_downloaded_at": None,
            "pdf_size_bytes": None,
        }

        # Initialize with structure
        super().__init__(structure)

        # If data provided, update with it
        if data is not None:
            self._update_from_data(data)

    def __getattr__(self, key):
        """Override to provide backward compatibility with flat field access."""
        # Try parent class first
        try:
            return super().__getattr__(key)
        except AttributeError:
            pass

        # Backward compatibility mappings for flat field access
        flat_to_nested = {
            # Basic fields
            "title": ("basic", "title"),
            "authors": ("basic", "authors"),
            "year": ("basic", "year"),
            "abstract": ("basic", "abstract"),
            "keywords": ("basic", "keywords"),

            # ID fields
            "doi": ("id", "doi"),
            "pmid": ("id", "pmid"),
            "arxiv_id": ("id", "arxiv_id"),
            "library_id": ("container", "library_id"),
            "scholar_id": ("id", "scholar_id"),

            # Publication fields
            "journal": ("publication", "journal"),
            "volume": ("publication", "volume"),
            "issue": ("publication", "issue"),
            "publisher": ("publication", "publisher"),
            "impact_factor": ("publication", "impact_factor"),
            "pages": ("publication", "first_page"),  # Return first_page for legacy pages

            # URL fields
            "url": ("url", "doi"),
            "pdf_url": ("url", "pdfs"),  # Returns list
            "openaccess_url": ("url", "openurl_resolved"),

            # Container fields
            "project": ("container", "project"),
            "created_at": ("container", "created_at"),
            "updated_at": ("container", "updated_at"),

            # Legacy names
            "citation_count": ("citation_count", "total"),
            "journal_impact_factor": ("publication", "impact_factor"),
        }

        # Special handling for pdf_url - return first item from list
        if key == "pdf_url":
            try:
                pdfs = self._data.get("url", {}).get("pdfs")
                if pdfs and isinstance(pdfs, list) and len(pdfs) > 0:
                    return pdfs[0] if isinstance(pdfs[0], str) else pdfs[0].get("url")
                return None
            except (KeyError, TypeError, AttributeError):
                return None

        if key in flat_to_nested:
            section, field = flat_to_nested[key]
            try:
                return self._data[section][field]
            except (KeyError, TypeError):
                return None

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """Override to provide backward compatibility with flat field access."""
        # Allow setting internal _data
        if key == "_data" or key.startswith("_"):
            super().__setattr__(key, value)
            return

        # Backward compatibility mappings
        flat_to_nested = {
            "title": ("basic", "title"),
            "authors": ("basic", "authors"),
            "year": ("basic", "year"),
            "abstract": ("basic", "abstract"),
            "keywords": ("basic", "keywords"),
            "doi": ("id", "doi"),
            "pmid": ("id", "pmid"),
            "arxiv_id": ("id", "arxiv_id"),
            "library_id": ("container", "library_id"),
            "scholar_id": ("id", "scholar_id"),
            "journal": ("publication", "journal"),
            "volume": ("publication", "volume"),
            "issue": ("publication", "issue"),
            "publisher": ("publication", "publisher"),
            "impact_factor": ("publication", "impact_factor"),
            "pages": ("publication", "first_page"),
            "url": ("url", "doi"),
            "openaccess_url": ("url", "openurl_resolved"),
            "project": ("container", "project"),
            "created_at": ("container", "created_at"),
            "updated_at": ("container", "updated_at"),
            "citation_count": ("citation_count", "total"),
            "journal_impact_factor": ("publication", "impact_factor"),
        }

        # Special handling for pages - split if contains dash
        if key == "pages" and value and "-" in str(value):
            first, last = str(value).split("-", 1)
            self._data["publication"]["first_page"] = first.strip()
            self._data["publication"]["last_page"] = last.strip()
            return

        # Special handling for pdf_url - store as list
        if key == "pdf_url" and value:
            if not self._data.get("url"):
                self._data["url"] = {}
            self._data["url"]["pdfs"] = [value] if isinstance(value, str) else value
            return

        if key in flat_to_nested:
            section, field = flat_to_nested[key]
            try:
                self._data[section][field] = value
            except (KeyError, TypeError):
                super().__setattr__(key, value)
        else:
            super().__setattr__(key, value)


    def _update_from_data(self, data: Union[Dict, DotDict]):
        """Update Paper from dictionary, handling both flat and nested formats.

        Args:
            data: Dictionary with paper data (can be flat or nested)
        """
        if isinstance(data, DotDict):
            data = data.to_dict()

        # If data has the full structure (metadata + container), use it
        if "metadata" in data and "container" in data:
            self.update(data)
        # If data has BASE_STRUCTURE sections, update metadata
        elif "id" in data and "basic" in data:
            self.update({"metadata": data})
        # Otherwise, assume flat format and map to structure
        else:
            self._map_flat_to_structure(data)

    def _map_flat_to_structure(self, flat_data: Dict):
        """Map flat dictionary to nested BASE_STRUCTURE format.

        Args:
            flat_data: Flat dictionary with fields like doi, title, etc.
        """
        # ID section
        if "doi" in flat_data:
            self.id.doi = flat_data["doi"]
            if "doi_source" in flat_data:
                self.id.doi_engines = flat_data["doi_source"]
        if "arxiv_id" in flat_data:
            self.id.arxiv_id = flat_data["arxiv_id"]
        if "pmid" in flat_data:
            self.id.pmid = flat_data["pmid"]
        if "semantic_id" in flat_data:
            self.id.semantic_id = flat_data["semantic_id"]
        if "ieee_id" in flat_data:
            self.id.ieee_id = flat_data["ieee_id"]
        if "scholar_id" in flat_data or "scitex_id" in flat_data:
            self.id.scholar_id = flat_data.get("scholar_id") or flat_data.get(
                "scitex_id"
            )

        # Basic section
        if "title" in flat_data:
            self.basic.title = flat_data["title"]
            if "title_source" in flat_data:
                self.basic.title_engines = flat_data["title_source"]
        if "authors" in flat_data:
            self.basic.authors = flat_data["authors"]
            if "authors_source" in flat_data:
                self.basic.authors_engines = flat_data["authors_source"]
        if "year" in flat_data:
            self.basic.year = flat_data["year"]
            if "year_source" in flat_data:
                self.basic.year_engines = flat_data["year_source"]
        if "abstract" in flat_data:
            self.basic.abstract = flat_data["abstract"]
            if "abstract_source" in flat_data:
                self.basic.abstract_engines = flat_data["abstract_source"]
        if "keywords" in flat_data:
            self.basic.keywords = flat_data["keywords"]
        if "type" in flat_data:
            self.basic.type = flat_data["type"]

        # Citation count section
        if "citation_count" in flat_data:
            self.citation_count.total = flat_data["citation_count"]
        for year in range(2015, 2026):
            year_key = f"citation_{year}"
            if year_key in flat_data:
                self.citation_count[str(year)] = flat_data[year_key]

        # Publication section
        if "journal" in flat_data:
            self.publication.journal = flat_data["journal"]
            if "journal_source" in flat_data:
                self.publication.journal_engines = flat_data["journal_source"]
        if "short_journal" in flat_data:
            self.publication.short_journal = flat_data["short_journal"]
        if (
            "impact_factor" in flat_data
            or "journal_impact_factor" in flat_data
        ):
            self.publication.impact_factor = flat_data.get(
                "impact_factor"
            ) or flat_data.get("journal_impact_factor")
        if "issn" in flat_data:
            self.publication.issn = flat_data["issn"]
        if "volume" in flat_data:
            self.publication.volume = flat_data["volume"]
        if "issue" in flat_data:
            self.publication.issue = flat_data["issue"]
        if "pages" in flat_data:
            pages = flat_data["pages"]
            if pages and "-" in str(pages):
                first, last = str(pages).split("-", 1)
                self.publication.first_page = first.strip()
                self.publication.last_page = last.strip()
        if "first_page" in flat_data:
            self.publication.first_page = flat_data["first_page"]
        if "last_page" in flat_data:
            self.publication.last_page = flat_data["last_page"]
        if "publisher" in flat_data:
            self.publication.publisher = flat_data["publisher"]

        # URL section
        if "url" in flat_data or "url_doi" in flat_data:
            self.url.doi = flat_data.get("url_doi") or flat_data.get("url")
        if "url_publisher" in flat_data:
            self.url.publisher = flat_data["url_publisher"]
            self.url.publisher_engines = "ScholarURLFinder"
        if "url_openurl_query" in flat_data:
            self.url.openurl_query = flat_data["url_openurl_query"]
        if (
            "url_openurl_resolved" in flat_data
            or "openaccess_url" in flat_data
        ):
            self.url.openurl_resolved = flat_data.get(
                "url_openurl_resolved"
            ) or flat_data.get("openaccess_url")
            self.url.openurl_resolved_engines = "ScholarURLFinder"
        if "urls_pdf" in flat_data:
            self.url.pdfs = flat_data["urls_pdf"]
            self.url.pdfs_engines = "ScholarURLFinder"
        elif "pdf_url" in flat_data:
            self.url.pdfs = [flat_data["pdf_url"]]
        if "urls_supplementary" in flat_data:
            self.url.supplementary_files = flat_data["urls_supplementary"]
        if "urls_additional" in flat_data:
            self.url.additional_files = flat_data["urls_additional"]

        # Path section
        if "pdf_path" in flat_data:
            self.path.pdfs = [flat_data["pdf_path"]]
            self.path.pdfs_engines = "ParallelPDFDownloader"
        if "paths_pdf" in flat_data:
            self.path.pdfs = flat_data["paths_pdf"]
        if "paths_supplementary" in flat_data:
            self.path.supplementary_files = flat_data["paths_supplementary"]
        if "paths_additional" in flat_data:
            self.path.additional_files = flat_data["paths_additional"]

        # System section
        for engine in [
            "arXiv",
            "CrossRef",
            "CrossRefLocal",
            "OpenAlex",
            "PubMed",
            "Semantic_Scholar",
            "URL",
        ]:
            key = f"searched_by_{engine}"
            if key in flat_data:
                self.system[key] = flat_data[key]

        # Container section
        if "library_id" in flat_data:
            self.container.library_id = flat_data["library_id"]
        if "scitex_id" in flat_data:
            self.container.scitex_id = flat_data["scitex_id"]
        if "created_at" in flat_data:
            self.container.created_at = flat_data["created_at"]
        if "created_by" in flat_data:
            self.container.created_by = flat_data["created_by"]
        if "updated_at" in flat_data:
            self.container.updated_at = flat_data["updated_at"]
        if "project" in flat_data:
            self.container.project = flat_data["project"]
        if "projects" in flat_data:
            self.container.projects = flat_data["projects"]
        if "master_storage_path" in flat_data:
            self.container.master_storage_path = flat_data[
                "master_storage_path"
            ]
        if "readable_name" in flat_data:
            self.container.readable_name = flat_data["readable_name"]
        if "metadata_file" in flat_data:
            self.container.metadata_file = flat_data["metadata_file"]
        if "pdf_downloaded_at" in flat_data:
            self.container.pdf_downloaded_at = flat_data["pdf_downloaded_at"]
        if "pdf_size_bytes" in flat_data:
            self.container.pdf_size_bytes = flat_data["pdf_size_bytes"]


# For backward compatibility, provide methods as module-level functions
def to_dict(paper: Paper) -> Dict:
    """Convert paper to dictionary."""
    return paper.to_dict()


def to_bibtex(paper: Paper, include_enriched: bool = True) -> str:
    """Convert paper to BibTeX."""
    from scitex.scholar.utils.paper_utils import paper_to_bibtex

    return paper_to_bibtex(paper, include_enriched=include_enriched)


def save_to_library(paper: Paper, force: bool = False) -> str:
    """Save paper to library."""
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.storage import ScholarLibrary
    from scitex.scholar.utils.paper_utils import save_paper_to_library

    config = ScholarConfig()
    library = ScholarLibrary(project=paper.container.project, config=config)
    return save_paper_to_library(paper, library, force=force)


def from_library(library_id: str, config=None) -> Paper:
    """Create Paper from library."""
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.storage import ScholarLibrary
    from scitex.scholar.utils.paper_utils import load_paper_from_library

    config = config or ScholarConfig()
    library = ScholarLibrary(project="default", config=config)
    return load_paper_from_library(library_id, library)


# For backward compatibility with Paper.from_library classmethod
Paper.from_library = classmethod(
    lambda cls, library_id, config=None: from_library(library_id, config)
)


if __name__ == "__main__":

    def main():
        """Demonstrate Paper class usage as DotDict with BASE_STRUCTURE."""
        print("=" * 60)
        print("Paper Class - DotDict with BASE_STRUCTURE Demo")
        print("=" * 60)

        # Paper is now a DotDict initialized with BASE_STRUCTURE
        paper = Paper()

        # Set values using dot notation (matches BASE_STRUCTURE exactly!)
        paper.id.doi = "10.5555/3295222.3295349"
        paper.basic.title = "Attention Is All You Need"
        paper.basic.authors = [
            "Vaswani, Ashish",
            "Shazeer, Noam",
            "Parmar, Niki",
        ]
        paper.basic.year = 2017
        paper.basic.abstract = "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks..."
        paper.basic.keywords = ["transformer", "attention", "neural networks"]
        paper.publication.journal = (
            "Advances in Neural Information Processing Systems"
        )
        paper.citation_count.total = 50000
        paper.citation_count["2024"] = 5000
        paper.container.project = "transformer_papers"
        paper.url.doi = "https://doi.org/10.5555/3295222.3295349"
        paper.url.pdfs = ["https://arxiv.org/pdf/1706.03762.pdf"]

        print("1. Paper structure matches BASE_STRUCTURE:")
        print(f"   DOI: {paper.id.doi}")
        print(f"   Title: {paper.basic.title}")
        print(f"   Authors: {len(paper.basic.authors)} authors")
        print(f"   Citations (total): {paper.citation_count.total}")
        print(f"   Citations (2024): {paper.citation_count['2024']}")
        print(f"   URL: {paper.url.doi}")
        print()

        print("2. Create from flat dict:")
        flat_data = {
            "doi": "10.1234/test",
            "title": "Test Paper",
            "authors": ["Test, A."],
            "year": 2025,
            "citation_count": 10,
        }
        paper2 = Paper(flat_data)
        print(f"   Title: {paper2.basic.title}")
        print(f"   DOI: {paper2.id.doi}")
        print()

        print("3. Convert to dict:")
        paper_dict = paper.to_dict()
        print(f"   Top-level keys: {list(paper_dict.keys())}")
        print(f"   ID section keys: {list(paper_dict['id'].keys())[:3]}...")
        print()

        print("✨ Paper is now a DotDict with BASE_STRUCTURE!")
        print("   - True single source of truth")
        print("   - Nested access: paper.id.doi, paper.citation_count.total")
        print("   - Matches JSON format exactly")
        print("   - Handles both flat and nested input")

    main()

# python -m scitex.scholar.core.Paper

# EOF
