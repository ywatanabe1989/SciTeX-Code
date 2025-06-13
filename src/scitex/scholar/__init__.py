#!/usr/bin/env python3
"""Scitex scholar module."""

from ._local_search import LocalSearchEngine, logger
from ._paper import Paper
from ._pdf_downloader import PDFDownloader, logger
from ._search import build_index, get_scholar_dir, logger, search_sync
from ._vector_search import VectorSearchEngine, logger
from ._web_sources import logger

__all__ = [
    "LocalSearchEngine",
    "PDFDownloader",
    "Paper",
    "VectorSearchEngine",
    "build_index",
    "get_scholar_dir",
    "logger",
    "logger",
    "logger",
    "logger",
    "logger",
    "search_sync",
]
