#!/usr/bin/env python3
"""Web-related utilities module for scitex."""

from ._search_pubmed import (
    search_pubmed,
    _search_pubmed,
    _fetch_details,
    _parse_abstract_xml,
    _get_citation,
    get_crossref_metrics,
    save_bibtex,
    format_bibtex,
    fetch_async,
    batch__fetch_details,
    parse_args,
    run_main,
)
from ._summarize_url import summarize_url, extract_main_content, crawl_url

__all__ = [
    "search_pubmed",
    "_search_pubmed",
    "_fetch_details",
    "_parse_abstract_xml",
    "_get_citation",
    "get_crossref_metrics",
    "save_bibtex",
    "format_bibtex",
    "fetch_async",
    "batch__fetch_details",
    "parse_args",
    "run_main",
    "summarize_url",
    "extract_main_content",
    "crawl_url",
]
