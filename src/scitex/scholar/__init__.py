#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:08:10 (ywatanabe)"
# File: ./src/scitex/scholar/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Scitex scholar module for scientific literature search and analysis."""

# PRIMARY INTERFACE - NEW unified Scholar class (enhanced interface)
from ._scholar import Scholar, PaperCollection

# Legacy Scholar class available as ScholarLegacy
try:
    from .scholar import Scholar as ScholarLegacy
except ImportError:
    ScholarLegacy = None

# Core legacy imports
from ._local_search import LocalSearchEngine
from ._paper import Paper
from ._pdf_downloader import PDFDownloader
from ._search import build_index, get_scholar_dir, search_sync
from ._vector_search import VectorSearchEngine

# Enhanced functionality imports
try:
    from ._paper_acquisition import PaperAcquisition, PaperMetadata, search_papers_with_ai, full_literature_review
except ImportError:
    PaperAcquisition = None
    PaperMetadata = None
    search_papers_with_ai = None
    full_literature_review = None

try:
    from ._semantic_scholar_client import SemanticScholarClient, S2Paper, search_papers, get_paper_info
except ImportError:
    SemanticScholarClient = None
    S2Paper = None
    search_papers = None
    get_paper_info = None

try:
    from ._journal_metrics import JournalMetrics, lookup_journal_impact_factor, enhance_bibliography_with_metrics
except ImportError:
    JournalMetrics = None
    lookup_journal_impact_factor = None
    enhance_bibliography_with_metrics = None

# Optional advanced modules
try:
    from ._literature_review_workflow import LiteratureReviewWorkflow
except ImportError:
    LiteratureReviewWorkflow = None

try:
    from ._vector_search_engine import VectorSearchEngine as EnhancedVectorSearchEngine
except ImportError:
    EnhancedVectorSearchEngine = None

try:
    from ._mcp_server import MCPServer
except ImportError:
    MCPServer = None

try:
    from ._paper_enrichment import PaperEnrichmentService, generate_enriched_bibliography
except ImportError:
    PaperEnrichmentService = None
    generate_enriched_bibliography = None

try:
    from ._impact_factor_integration import ImpactFactorService, EnhancedJournalMetrics
except ImportError:
    ImpactFactorService = None
    EnhancedJournalMetrics = None

__all__ = [
    # PRIMARY INTERFACE - Use these for new code
    "Scholar",                    # Main unified interface (new enhanced)
    "PaperCollection",           # Container for search results
    "ScholarLegacy",             # Legacy Scholar class
    
    # Legacy components - for backward compatibility
    "build_index",
    "enhance_bibliography_with_metrics",
    "EnhancedJournalMetrics",
    "EnhancedVectorSearchEngine",
    "full_literature_review",
    "generate_enriched_bibliography",
    "get_paper_info",
    "get_scholar_dir",
    "ImpactFactorService",
    "JournalMetrics",
    "LiteratureReviewWorkflow",
    "LocalSearchEngine",
    "lookup_journal_impact_factor",
    "MCPServer",
    "Paper",
    "PaperAcquisition",
    "PaperEnrichmentService",
    "PaperMetadata",
    "PDFDownloader",
    "S2Paper",
    "search_papers",
    "search_papers_with_ai",
    "search_sync",
    "SemanticScholarClient",
    "VectorSearchEngine",
]

# EOF