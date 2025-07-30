#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:43:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/sources/_SemanticScholarSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/sources/_SemanticScholarSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict

import requests

"""Semantic Scholar DOI source implementation.

This module provides DOI resolution through the Semantic Scholar API."""
from scitex import logging
from typing import List, Optional

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


def is_rate_limited(exception):
    """Check if exception is due to rate limiting."""
    return (
        isinstance(exception, requests.HTTPError)
        and exception.response.status_code == 429
    )


class SemanticScholarSource(BaseDOISource):
    """Semantic Scholar - free API with good abstract coverage."""

    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self._session = None
        self.base_url = "https://api.semanticscholar.org/graph/v1"

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
        return "SemanticScholar"

    @property
    def rate_limit_delay(self) -> float:
        return 1.0  # Semantic Scholar recommends 1 request per second

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=10, max=120),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"Rate limited, retrying in {retry_state.next_action.sleep} seconds..."
        ),
    )
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search Semantic Scholar for DOI by title."""
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": "title,year,externalIds",
            "limit": 5,
        }

        response = self.session.get(url, params=params, timeout=30)
        if response.status_code == 429:
            raise requests.HTTPError("Rate limited", response=response)
        response.raise_for_status()

        data = response.json()
        papers = data.get("data", [])

        for paper in papers:
            paper_title = paper.get("title", "")
            if paper_title and self._is_title_match(title, paper_title):
                if year and paper.get("year"):
                    paper_year = paper.get("year")
                    try:
                        if isinstance(paper_year, str):
                            paper_year = int(paper_year)
                        if isinstance(year, str):
                            year = int(year)
                        if abs(paper_year - year) > 1:
                            continue
                    except (ValueError, TypeError):
                        continue

                external_ids = paper.get("externalIds", {})
                if external_ids and "DOI" in external_ids:
                    return external_ids["DOI"]

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from Semantic Scholar by DOI."""
        url = f"{self.base_url}/paper/DOI:{doi}"
        params = {"fields": "abstract"}

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                abstract = data.get("abstract")
                if abstract:
                    logger.debug(
                        f"Found abstract from Semantic Scholar for DOI: {doi}"
                    )
                    return abstract
            elif response.status_code == 404:
                logger.debug(f"Paper not found in Semantic Scholar: {doi}")
            elif response.status_code == 429:
                logger.warning("Semantic Scholar rate limited")
        except Exception as e:
            logger.debug(f"Semantic Scholar abstract error: {e}")

        return None

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=10, max=120),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"Rate limited, retrying in {retry_state.next_action.sleep} seconds..."
        ),
    )
    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from Semantic Scholar."""
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": "title,year,externalIds,authors,abstract,venue",
            "limit": 5,
        }

        response = self.session.get(url, params=params, timeout=30)
        if response.status_code == 429:
            raise requests.HTTPError("Rate limited", response=response)
        response.raise_for_status()

        data = response.json()
        papers = data.get("data", [])

        for paper in papers:
            paper_title = paper.get("title", "")
            if paper_title and self._is_title_match(title, paper_title):
                if year and paper.get("year"):
                    paper_year = paper.get("year")
                    try:
                        if isinstance(paper_year, str):
                            paper_year = int(paper_year)
                        if isinstance(year, str):
                            year = int(year)
                        if abs(paper_year - year) > 1:
                            continue
                    except (ValueError, TypeError):
                        continue

                extracted_authors = []
                for author in paper.get("authors", []):
                    if author.get("name"):
                        extracted_authors.append(author["name"])

                external_ids = paper.get("externalIds", {})
                return {
                    "doi": external_ids.get("DOI"),
                    "title": paper_title,
                    "journal": paper.get("venue"),
                    "year": (
                        paper_year
                        if isinstance(paper_year, int)
                        else paper.get("year")
                    ),
                    "abstract": paper.get("abstract"),
                    "authors": (
                        extracted_authors if extracted_authors else None
                    ),
                }

        return None

# EOF
