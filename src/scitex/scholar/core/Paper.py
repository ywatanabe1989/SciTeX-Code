#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 05:40:00 (ywatanabe)"
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

Paper is a pure dataclass - just a data container.
All operations are handled by utility functions in scitex.scholar.utils.paper_utils.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Paper:
    """A scientific paper - pure data container.

    This is a dataclass with no methods, just fields.
    All operations on papers are handled by:
    - Scholar class for high-level operations
    - Utility functions in paper_utils for conversions

    Attributes:
        title: Paper title
        authors: List of author names
        year: Publication year
        abstract: Paper abstract
        keywords: List of keywords
        doi: Digital Object Identifier
        pmid: PubMed ID
        arxiv_id: arXiv identifier
        library_id: Internal library ID
        journal: Journal name
        volume: Journal volume
        issue: Journal issue
        pages: Page numbers
        publisher: Publisher name
        citation_count: Number of citations
        journal_impact_factor: Journal impact factor (2-year)
        url: Paper URL
        pdf_url: Direct PDF URL
        openaccess_url: Open access URL
        sources: Dictionary tracking source of each field
        created_at: When this record was created
        updated_at: When this record was last updated
        project: Associated project name
    """

    # Basic information (required or commonly present)
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    # Identifiers
    doi: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    library_id: Optional[str] = None

    # Publication details
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None

    # Metrics
    citation_count: Optional[int] = None
    journal_impact_factor: Optional[float] = None

    # URLs
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    openaccess_url: Optional[str] = None

    # Metadata tracking
    sources: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    project: Optional[str] = None

    # Compatibility fields (for transition period)
    _bibtex_key: Optional[str] = field(default=None, repr=False)
    _bibtex_entry_type: str = field(default="misc", repr=False)
    _original_bibtex_fields: Dict = field(default_factory=dict, repr=False)


# For backward compatibility, provide methods as module-level functions
# These will be deprecated in future versions

def to_dict(paper: Paper) -> Dict:
    """Convert paper to dictionary. DEPRECATED: Use paper_utils.paper_to_dict()"""
    from scitex.scholar.utils.paper_utils import paper_to_dict
    return paper_to_dict(paper)


def to_bibtex(paper: Paper, include_enriched: bool = True) -> str:
    """Convert paper to BibTeX. DEPRECATED: Use paper_utils.paper_to_bibtex()"""
    from scitex.scholar.utils.paper_utils import paper_to_bibtex
    return paper_to_bibtex(paper, key=paper._bibtex_key, include_enriched=include_enriched)


def save_to_library(paper: Paper, force: bool = False) -> str:
    """Save paper to library. DEPRECATED: Use Scholar.save() or paper_utils.save_paper_to_library()"""
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.storage import ScholarLibrary
    from scitex.scholar.utils.paper_utils import save_paper_to_library

    config = ScholarConfig()
    library = ScholarLibrary(project=paper.project, config=config)
    return save_paper_to_library(paper, library, force=force)


def load_from_library(paper: Paper, library_id: str) -> None:
    """Load paper from library. DEPRECATED: Use Scholar.from_library()"""
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.storage import ScholarLibrary
    from scitex.scholar.utils.paper_utils import load_paper_from_library

    config = ScholarConfig()
    library = ScholarLibrary(project=paper.project, config=config)
    loaded_paper = load_paper_from_library(library_id, library)

    # Update current paper's fields
    for field_name in paper.__dataclass_fields__:
        setattr(paper, field_name, getattr(loaded_paper, field_name))


def from_library(library_id: str, config=None) -> Paper:
    """Create Paper from library. DEPRECATED: Use Scholar.from_library()"""
    from scitex.scholar.config import ScholarConfig
    from scitex.scholar.storage import ScholarLibrary
    from scitex.scholar.utils.paper_utils import load_paper_from_library

    config = config or ScholarConfig()
    library = ScholarLibrary(project="default", config=config)
    return load_paper_from_library(library_id, library)


def save(paper: Paper, output_path: str, format: str = "auto") -> None:
    """Save paper to file. DEPRECATED: Use paper_utils.save()"""
    from scitex.scholar.utils.paper_utils import save as save_paper
    save_paper(paper, output_path, format)


# Monkey-patch methods for backward compatibility
# These allow old code to still call paper.to_dict(), paper.save_to_library(), etc.
# This is temporary and will be removed in future versions

def _create_bound_method(func, paper):
    """Create a bound method for a paper instance."""
    def bound_method(*args, **kwargs):
        return func(paper, *args, **kwargs)
    return bound_method


def __getattr__(name):
    """Module-level __getattr__ for backward compatibility."""
    # This only works in Python 3.7+
    if name == 'Paper':
        return Paper
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Add compatibility methods to Paper instances
original_init = Paper.__init__


def new_init(self, *args, **kwargs):
    """Extended init that adds compatibility methods."""
    original_init(self, *args, **kwargs)

    # Add compatibility methods
    self.to_dict = lambda: to_dict(self)
    self.to_bibtex = lambda include_enriched=True: to_bibtex(self, include_enriched)
    self.save_to_library = lambda force=False: save_to_library(self, force)
    self.load_from_library = lambda library_id: load_from_library(self, library_id)
    self.save = lambda output_path, format="auto": save(self, output_path, format)

    # Add string representations
    from scitex.scholar.utils.paper_utils import paper_str, paper_repr
    self.__str__ = lambda: paper_str(self)
    self.__repr__ = lambda: paper_repr(self)

    # Add metadata property for backward compatibility
    from scitex.scholar.utils.paper_utils import paper_to_structured_dict
    self.metadata = paper_to_structured_dict(self)


Paper.__init__ = new_init


# For backward compatibility with Paper.from_library classmethod
Paper.from_library = classmethod(lambda cls, library_id, config=None: from_library(library_id, config))


if __name__ == "__main__":

    def main():
        """Demonstrate Paper class usage as pure dataclass."""
        print("=" * 60)
        print("Paper Class - Pure Dataclass Demo")
        print("=" * 60)

        # Paper is now a simple dataclass
        paper = Paper(
            title="Attention Is All You Need",
            authors=["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki"],
            year=2017,
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
            keywords=["transformer", "attention", "neural networks"],
            doi="10.5555/3295222.3295349",
            journal="Advances in Neural Information Processing Systems",
            citation_count=50000,
            project="transformer_papers",
        )

        print("1. Paper is a pure dataclass:")
        print(f"   Title: {paper.title}")
        print(f"   DOI: {paper.doi}")
        print(f"   Authors: {len(paper.authors)} authors")
        print()

        # Use utility functions for operations
        from scitex.scholar.utils.paper_utils import paper_to_dict, paper_to_bibtex

        print("2. Operations use utility functions:")
        paper_dict = paper_to_dict(paper)
        print(f"   paper_to_dict() -> {list(paper_dict.keys())[:5]}...")
        print()

        print("3. BibTeX generation via utility:")
        bibtex = paper_to_bibtex(paper)
        print("   " + "\n   ".join(bibtex.split("\n")[:5]) + "...")
        print()

        # Backward compatibility still works
        print("4. Backward compatibility (temporary):")
        print(f"   paper.to_dict() still works: {len(paper.to_dict())} fields")
        print(f"   paper.to_bibtex() still works: {len(paper.to_bibtex())} chars")
        print()

        print("✨ Paper is now a clean dataclass!")
        print("   - No methods in the class itself")
        print("   - All operations via utility functions")
        print("   - Backward compatibility maintained")

    main()

# python -m scitex.scholar.core.Paper

# EOF