#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:40:14 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/sources/_OpenAlexSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/sources/_OpenAlexSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import requests

from typing import Any
from typing import Dict

"""
OpenAlex DOI source implementation.

This module provides DOI resolution through the OpenAlex API.
"""

import logging
from typing import List
from typing import Optional
from tenacity import retry
from tenacity import (
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class OpenAlexSource(BaseDOISource):
    """OpenAlex - free and open alternative to proprietary databases."""

    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
            )
        return self._session

    @property
    def name(self) -> str:
        return "OpenAlex"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1  # OpenAlex is generous

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search OpenAlex for DOI."""
        url = "https://api.openalex.org/works"

        filters = [f'title.search:"{title}"']
        if year:
            filters.append(f"publication_year:{year}")

        params = {
            "filter": ",".join(filters),
            "per_page": 5,
            "mailto": self.email,
        }

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        for work in results:
            work_title = work.get("title", "")
            if work_title and self._is_title_match(title, work_title):
                doi_url = work.get("doi", "")
                if doi_url:
                    return doi_url.replace("https://doi.org/", "")
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from OpenAlex."""
        url = "https://api.openalex.org/works"

        filters = [f'title.search:"{title}"']
        if year:
            filters.append(f"publication_year:{year}")

        params = {
            "filter": ",".join(filters),
            "per_page": 5,
            "mailto": self.email,
        }

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        for work in results:
            work_title = work.get("title", "")
            if work_title and self._is_title_match(title, work_title):
                doi_url = work.get("doi", "")
                doi = (
                    doi_url.replace("https://doi.org/", "")
                    if doi_url
                    else None
                )

                authors_list = []
                for authorship in work.get("authorships", []):
                    author = authorship.get("author", {})
                    if author.get("display_name"):
                        authors_list.append(author["display_name"])

                journal = None
                host_venue = work.get("host_venue", {})
                if host_venue:
                    journal = host_venue.get("display_name")

                return {
                    "doi": doi,
                    "title": work_title,
                    "journal": journal,
                    "year": work.get("publication_year"),
                    "abstract": None,
                    "authors": authors_list if authors_list else None,
                }
        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """OpenAlex doesn't provide abstracts."""
        return None

# EOF
