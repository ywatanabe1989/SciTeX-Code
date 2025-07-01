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

__all__ = [
    "build_index",
    "enhance_bibliography_with_metrics",
    "EnhancedVectorSearchEngine",
    "full_literature_review",
    "get_paper_info",
    "get_scholar_dir",
    "JournalMetrics",
    "LiteratureReviewWorkflow",
    "LocalSearchEngine",
    "lookup_journal_impact_factor",
    "MCPServer",
    "Paper",
    "PaperAcquisition",
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