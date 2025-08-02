#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 17:08:05 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/sources/_CrossRefSource.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/scholar/doi/sources/_CrossRefSource.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
CrossRef DOI source implementation.

This module provides DOI resolution through the CrossRef API.
"""
from scitex import logging
from typing import Any, Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class CrossRefSource(BaseDOISource):
    """CrossRef DOI source - no API key required, generous rate limits."""

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
        return "CrossRef"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1  # CrossRef is very generous

    # def search(
    #     self,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[List[str]] = None,
    # ) -> Optional[str]:
    #     """Search CrossRef for DOI."""
    #     url = "https://api.crossref.org/works"
    #     params = {
    #         "query": title,
    #         "rows": 5,
    #         "select": "DOI,title,published-print",
    #         "mailto": self.email,
    #     }

    #     if year:
    #         params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

    #     try:
    #         response = self.session.get(url, params=params, timeout=30)
    #         if response.status_code == 200:
    #             data = response.json()
    #             items = data.get("message", {}).get("items", [])

    #             for item in items:
    #                 item_title = " ".join(item.get("title", []))
    #                 if self._is_title_match(title, item_title):
    #                     return item.get("DOI")
    #     except Exception as e:
    #         logger.debug(f"CrossRef error: {e}")

    #     return None

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
        """Search CrossRef for DOI."""
        url = "https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 5,
            "select": "DOI,title,published-print",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()  # Will trigger retry on HTTP errors

        data = response.json()
        items = data.get("message", {}).get("items", [])

        for item in items:
            item_title = " ".join(item.get("title", []))
            if self._is_title_match(title, item_title):
                return item.get("DOI")

        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from CrossRef."""
        url = f"https://api.crossref.org/works/{doi}"
        params = {"mailto": self.email}

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("abstract")
        except Exception as e:
            logger.debug(f"CrossRef abstract error: {e}")

        return None

    # def get_metadata(
    #     self,
    #     title: str,
    #     year: Optional[int] = None,
    #     authors: Optional[List[str]] = None,
    # ) -> Optional[Dict[str, Any]]:
    #     """Get comprehensive metadata from CrossRef."""
    #     url = "https://api.crossref.org/works"
    #     params = {
    #         "query": title,
    #         "rows": 5,
    #         "select": "DOI,title,published-print,container-title,abstract,author",
    #         "mailto": self.email,
    #     }

    #     if year:
    #         params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

    #     response = self.session.get(url, params=params, timeout=30)
    #     response.raise_for_status()

    #     data = response.json()
    #     items = data.get("message", {}).get("items", [])

    #     for item in items:
    #         item_title = " ".join(item.get("title", []))
    #         if self._is_title_match(title, item_title):
    #             # Extract publication year
    #             pub_year = None
    #             if item.get("published-print", {}).get("date-parts"):
    #                 pub_year = item["published-print"]["date-parts"][0][0]

    #             # Extract authors
    #             extracted_authors = []
    #             for author in item.get("author", []):
    #                 given = author.get("given", "")
    #                 family = author.get("family", "")
    #                 if family:
    #                     if given:
    #                         extracted_authors.append(f"{given} {family}")
    #                     else:
    #                         extracted_authors.append(family)

    #             return {
    #                 "doi": item.get("DOI"),
    #                 "title": item_title,
    #                 "journal": item.get("container-title", [None])[0],
    #                 "year": pub_year,
    #                 "abstract": item.get("abstract"),
    #                 "authors": (
    #                     extracted_authors if extracted_authors else None
    #                 ),
    #             }

    #     return None

    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from CrossRef."""
        url = "https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 5,
            "select": "DOI,title,published-print,container-title,abstract,author",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data.get("message", {}).get("items", [])

        for item in items:
            item_title = " ".join(item.get("title", []))
            if self._is_title_match(title, item_title):
                pub_year = None
                if item.get("published-print", {}).get("date-parts"):
                    pub_year = item["published-print"]["date-parts"][0][0]

                extracted_authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if family:
                        if given:
                            extracted_authors.append(f"{given} {family}")
                        else:
                            extracted_authors.append(family)

                return {
                    "doi": item.get("DOI"),
                    "title": item_title,
                    "journal": item.get("container-title", [None])[0],
                    "year": pub_year,
                    "abstract": item.get("abstract"),
                    "authors": (
                        extracted_authors if extracted_authors else None
                    ),
                }

        return None


# EOF
