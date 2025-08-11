#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 06:55:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/sources/_ArXivSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_ArXivSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict, List, Optional

import feedparser
import requests

from scitex import logging

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class ArXivSource(BaseDOISource):
    """ArXiv source for open access papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()  # Initialize base class
        self.email = email
        self._session = None
        self.base_url = "http://export.arxiv.org/api/query"

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": f"SciTeX Scholar (mailto:{self.email})"}
            )
        return self._session

    @property
    def name(self) -> str:
        return "ArXiv"

    @property
    def rate_limit_delay(self) -> float:
        return 3.0

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search for paper on ArXiv by title."""
        params = {
            "search_query": f'ti:"{title}"',
            "start": 0,
            "max_results": 5,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                entry_title = entry.get("title", "").replace("\n", " ").strip()
                if self._is_title_match(title, entry_title):
                    for link in entry.get("links", []):
                        if link.get("title") == "doi":
                            return self.extract_doi_from_url(
                                link.get("href", "")
                            )
                    return None

        except Exception as exc:
            logger.debug(f"ArXiv search error: {exc}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """ArXiv doesn't index by DOI directly."""
        return None

    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from ArXiv."""
        params = {
            "search_query": f'ti:"{title}"',
            "start": 0,
            "max_results": 5,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                entry_title = entry.get("title", "").replace("\n", " ").strip()
                if self._is_title_match(title, entry_title):
                    metadata = {
                        "title": entry_title,
                        "abstract": entry.get("summary", "").strip(),
                        "year": (
                            entry.get("published", "")[:4]
                            if entry.get("published")
                            else None
                        ),
                        "authors": [
                            author["name"]
                            for author in entry.get("authors", [])
                        ],
                        "arxiv_id": entry.id.split("/abs/")[-1].split("v")[0],
                    }

                    for link in entry.get("links", []):
                        if link.get("title") == "doi":
                            doi = self.extract_doi_from_url(
                                link.get("href", "")
                            )
                            if doi:
                                metadata["doi"] = doi
                                break

                    if year and metadata.get("year"):
                        try:
                            if abs(int(metadata["year"]) - int(year)) > 1:
                                continue
                        except (ValueError, TypeError):
                            continue

                    return metadata

        except Exception as exc:
            logger.warn(f"ArXiv metadata error: {exc}")

        return None

# EOF
