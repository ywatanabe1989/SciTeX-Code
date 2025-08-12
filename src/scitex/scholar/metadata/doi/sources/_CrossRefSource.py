#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 13:54:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/sources/_CrossRefSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_CrossRefSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
CrossRef DOI source implementation.

This module provides DOI resolution through the CrossRef API.
"""

from typing import Any, Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class CrossRefSource(BaseDOISource):
    """CrossRef DOI source - no API key required, generous rate limits."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()  # Initialize base class
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
            )
        return self._session

    @property
    def name(self) -> str:
        return "CrossRef"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1  # CrossRef is very generous

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search CrossRef for DOI using enhanced request handling.

        Note: For comprehensive metadata including journal info, use get_metadata() instead.
        This method only returns the DOI string for backward compatibility.
        """
        url = "https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 5,
            "select": "DOI,title,published-print",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        # Use enhanced request method with automatic retries and rate limiting
        response = self._make_request_with_retry(
            url, params=params, timeout=30, max_retries=3
        )

        if not response or response.status_code != 200:
            return None

        try:
            data = response.json()
            items = data.get("message", {}).get("items", [])

            for item in items:
                item_title = " ".join(item.get("title", []))
                if self._is_title_match(title, item_title):
                    return item.get("DOI")
        except Exception as e:
            logger.debug(f"Error parsing CrossRef response: {e}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from CrossRef using enhanced request handling."""
        url = f"https://api.crossref.org/works/{doi}"
        params = {"mailto": self.email}

        response = self._make_request_with_retry(
            url, params=params, timeout=30, max_retries=3
        )

        if not response or response.status_code != 200:
            return None

        try:
            data = response.json()
            return data.get("message", {}).get("abstract")
        except Exception as e:
            logger.debug(f"CrossRef abstract error: {e}")

        return None

    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from CrossRef using enhanced request handling."""
        url = "https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 5,
            "select": "DOI,title,published-print,published-online,container-title,short-container-title,publisher,volume,issue,ISSN,abstract,author",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        response = self._make_request_with_retry(
            url, params=params, timeout=30, max_retries=3
        )

        if not response or response.status_code != 200:
            return None

        try:
            data = response.json()
            items = data.get("message", {}).get("items", [])

            for item in items:
                item_title = " ".join(item.get("title", []))
                if item_title.endswith("."):
                    item_title = item_title[:-1]
                if self._is_title_match(title, item_title):
                    # Extract publication year from multiple sources
                    pub_year = None
                    published = item.get("published-print") or item.get(
                        "published-online"
                    )
                    if published and published.get("date-parts"):
                        pub_year = published["date-parts"][0][0]

                    # Extract authors
                    extracted_authors = []
                    for author in item.get("author", []):
                        given = author.get("given", "")
                        family = author.get("family", "")
                        if family:
                            if given:
                                extracted_authors.append(f"{given} {family}")
                            else:
                                extracted_authors.append(family)

                    # Extract comprehensive journal information
                    container_titles = item.get("container-title", [])
                    short_container_titles = item.get(
                        "short-container-title", []
                    )

                    journal = container_titles[0] if container_titles else None
                    short_journal = (
                        short_container_titles[0]
                        if short_container_titles
                        else None
                    )

                    # Get ISSN (can be a list)
                    issn_list = item.get("ISSN", [])
                    issn = issn_list[0] if issn_list else None

                    return {
                        "doi": item.get("DOI"),
                        "title": item_title,
                        "journal": journal,
                        "journal_source": "crossref",
                        "short_journal": short_journal,
                        "publisher": item.get("publisher"),
                        "volume": item.get("volume"),
                        "issue": item.get("issue"),
                        "issn": issn,
                        "year": pub_year,
                        "abstract": item.get("abstract"),
                        "authors": (
                            extracted_authors if extracted_authors else None
                        ),
                    }
        except Exception as e:
            logger.debug(f"Error parsing CrossRef metadata response: {e}")

        return None

# EOF
