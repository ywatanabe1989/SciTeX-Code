#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:25:00 (ywatanabe)"
# File: ./src/scitex/scholar/__init__.py
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
from .scholar import Scholar, search, quick_search

# Import core classes for advanced users
from ._core import Paper, PaperCollection

# Import utility functions
from ._utils import (
    papers_to_bibtex,
    papers_to_ris,
    papers_to_json,
    papers_to_markdown
)

# Version
__version__ = "2.0.0"

# What users see with "from scitex.scholar import *"
__all__ = [
    # Main interface
    'Scholar',
    
    # Convenience functions
    'search',
    'quick_search',
    
    # Core classes
    'Paper',
    'PaperCollection',
    
    # Format converters
    'papers_to_bibtex',
    'papers_to_ris', 
    'papers_to_json',
    'papers_to_markdown'
]

# For backward compatibility, provide access to old functions with deprecation warnings
def __getattr__(name):
    """Provide backward compatibility with deprecation warnings."""
    import warnings
    
    # Map old names to new functionality
    compatibility_map = {
        'search_sync': 'search',
        'build_index': 'Scholar().index_local_pdfs',
        'get_scholar_dir': 'Scholar().workspace_dir',
        'LocalSearchEngine': 'Scholar',
        'VectorSearchEngine': 'Scholar',
        'PDFDownloader': 'Scholar',
        'search_papers': 'search',
        'S2Paper': 'Paper',
        'PaperMetadata': 'Paper',
        'PaperAcquisition': 'Scholar',
        'SemanticScholarClient': 'Scholar',
        'JournalMetrics': 'Scholar',
        'PaperEnrichmentService': 'Scholar',
        'generate_enriched_bibliography': 'PaperCollection.save'
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
                    stats.update(scholar.index_local_pdfs(path))
                return stats
            return build_index
        else:
            return Scholar
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Module docstring for help()
def _module_docstring():
    """
    SciTeX Scholar - Scientific Literature Management
    
    Main Classes:
        Scholar: Main interface for all functionality
        Paper: Represents a scientific paper
        PaperCollection: Collection of papers with analysis tools
    
    Quick Start:
        >>> from scitex.scholar import Scholar
        >>> scholar = Scholar()
        >>> papers = scholar.search("machine learning")
        >>> papers.filter(year_min=2020).save("ml_papers.bib")
    
    Common Workflows:
        # Search and enrich
        papers = scholar.search("deep learning", year_min=2022)
        
        # Download PDFs
        papers.download_pdfs()
        
        # Filter results
        high_impact = papers.filter(impact_factor_min=5.0)
        
        # Save bibliography
        papers.save("bibliography.bib", format="bibtex")
        
        # Search local library
        scholar.index_local_pdfs("./my_papers")
        local = scholar.search_local("transformer")
    
    For more information, see the documentation at:
    https://github.com/ywatanabe1989/SciTeX-Code
    """
    pass

# Set module docstring
__doc__ = _module_docstring.__doc__