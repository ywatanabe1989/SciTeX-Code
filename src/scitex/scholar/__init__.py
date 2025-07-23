#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 15:49:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
SciTeX Scholar - Scientific Literature Management Made Simple

This module provides a unified interface for:
- Searching scientific literature across multiple sources
- Automatic paper enrichment with journal metrics
- PDF downloads and local library management
- Bibliography generation in multiple formats

Quick Start:
    from scitex.scholar import Scholar

    scholar = Scholar()
    papers = scholar.search("deep learning")
    papers.save("papers.bib")
"""

# Import main class
from ._Scholar import Scholar, search, search_quick, enrich_bibtex

# Import configuration
from ._Config import ScholarConfig

# Import core classes for advanced users
from ._Paper import Paper
from ._Papers import Papers

# Backward compatibility alias
PaperCollection = Papers

# Import utility functions
from ._utils import (
    papers_to_bibtex,
    papers_to_ris,
    papers_to_json,
    papers_to_markdown
)

# Citation enrichment is now part of UnifiedEnricher

# Import Sci-Hub downloader
from ._SciHubDownloader import dois_to_local_pdfs, dois_to_local_pdfs_async

# Create module-level convenience function
def download_pdfs(
    dois,
    download_dir=None,
    force=False,
    max_workers=4,
    show_progress=True,
    acknowledge_ethical_usage=None,
    **kwargs
):
    """
    Download PDFs for DOIs using default Scholar instance.
    
    This is a convenience function that creates a Scholar instance if needed.
    For more control, use Scholar().download_pdfs() directly.
    
    Args:
        dois: DOI strings (list or single string) or Papers/Paper objects
        download_dir: Directory to save PDFs
        force: Force re-download
        max_workers: Maximum concurrent downloads
        show_progress: Show download progress
        acknowledge_ethical_usage: Acknowledge ethical usage for Sci-Hub
        **kwargs: Additional arguments
        
    Returns:
        Dictionary with download results
        
    Examples:
        >>> import scitex as stx
        >>> stx.scholar.download_pdfs(["10.1234/doi1", "10.5678/doi2"])
        >>> stx.scholar.download_pdfs("10.1234/single-doi")
    """
    scholar = Scholar()
    return scholar.download_pdfs(
        dois,
        download_dir=download_dir,
        force=force,
        max_workers=max_workers,
        show_progress=show_progress,
        acknowledge_ethical_usage=acknowledge_ethical_usage,
        **kwargs
    )

# Version
__version__ = "2.0.0"

# What users see with "from scitex.scholar import *"
__all__ = [
    # Main interface
    'Scholar',
    'ScholarConfig',

    # Convenience functions
    'search',
    'search_quick',
    'enrich_bibtex',
    'download_pdfs',  # NEW: Module-level convenience function

    # Core classes
    'Paper',
    'Papers',
    'PaperCollection',  # Backward compatibility alias

    # Format converters
    'papers_to_bibtex',
    'papers_to_ris',
    'papers_to_json',
    'papers_to_markdown',

    # Utils
    # 'enrich_with_citations',  # Now part of Scholar.enrich_papers()

    # Sci-Hub downloader
    'dois_to_local_pdfs',
    'dois_to_local_pdfs_async'
]

# For backward compatibility, provide access to old functions with deprecation warnings
def __getattr__(name):
    """Provide backward compatibility with deprecation warnings."""
    import warnings
    
    # Handle special IPython attributes
    if name in ['__custom_documentations__', '__wrapped__']:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    # Map old names to new functionality
    compatibility_map = {
        'search_sync': 'search',
        'build_index': 'Scholar()._index_local_pdfs',
        'get_scholar_dir': 'Scholar().workspace_dir',
        'LocalSearchEngine': 'Scholar',
        'VectorSearchEngine': 'Scholar',
        'PDFDownloader': 'Scholar',
        'search_papers': 'search',
        'SemanticScholarPaper': 'Paper',
        'PaperMetadata': 'Paper',
        'PaperAcquisition': 'Scholar',
        'SemanticScholarClient': 'Scholar',
        'JournalMetrics': 'Scholar',
        'PaperEnrichmentService': 'Scholar',
        'generate_enriched_bibliography': 'Papers.save'
    }

    if name in compatibility_map:
        warnings.warn(
            f"{name} is deprecated. Use {compatibility_map[name]} instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # Return the Scholar class for most cases
        if name in ['search_sync', 'search_papers']:
            return search
        elif name == 'build_index':
            def build_index(paths, **kwargs):
                scholar = Scholar()
                stats = {}
                for path in paths:
                    stats.update(scholar._index_local_pdfs(path))
                return stats
            return build_index
        else:
            return Scholar

    from ..errors import ScholarError
    raise ScholarError(
        f"Module attribute not found: '{name}'",
        context={"module": __name__, "attribute": name},
        suggestion=f"Available attributes: Scholar, Paper, Papers, search, enrich_bibtex"
    )


# Module docstring for help()
def _module_docstring():
    """
    SciTeX Scholar - Scientific Literature Management

    Main Classes:
        Scholar: Main interface for all functionality
        Paper: Represents a scientific paper
        Papers: Collection of papers with analysis tools

    Quick Start:
        >>> from scitex.scholar import Scholar
        >>> scholar = Scholar()
        >>> papers = scholar.search("machine learning")
        >>> papers.filter(year_min=2020).save("ml_papers.bib")

    Common Workflows:
        # Search and enrich
        papers = scholar.search("deep learning", year_min=2022)

        # Download PDFs
        scholar.download_pdfs(papers)

        # Filter results
        high_impact = papers.filter(impact_factor_min=5.0)

        # Save bibliography
        papers.save("bibliography.bib", format="bibtex")

        # Search local library
        scholar._index_local_pdfs("./my_papers")
        local = scholar.search_local("transformer")

    For more information, see the documentation at:
    https://github.com/ywatanabe1989/SciTeX-Code
    """
    pass

# Set module docstring
__doc__ = _module_docstring.__doc__

# EOF
