#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 06:23:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/ArXivEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/engines/individual/ArXivEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from typing import Dict, List, Optional, Union

import feedparser
import requests
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils._standardize_metadata import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)
import json


class ArXivEngine(BaseDOIEngine):
    """ArXiv engine for open access papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()
        self.name = self.__class__.__name__
        self.email = email
        self.base_url = "http://export.arxiv.org/api/query"

    def _get_user_agent(self) -> str:
        """Get ArXiv-specific user agent."""
        return f"SciTeX Scholar (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "arXiv"

    @property
    def rate_limit_delay(self) -> float:
        return 3.0

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi is provided, all the information other than doi is ignored"""
        if doi:
            return self._search_by_doi(doi, return_as)
        else:
            return self._search_by_metadata(
                title, year, authors, max_results, return_as
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError)
        ),
    )
    def _search_by_doi(self, doi: str, return_as: str) -> Optional[Dict]:
        """Search solely on doi"""
        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )
        arxiv_id = doi.split("arXiv.")[-1]

        params = {
            "search_query": f'id:"{arxiv_id}"',
            "start": 0,
            "max_results": 1,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            for entry in feed.entries:
                return self._extract_metadata_from_entry(entry, return_as)
            return self._create_minimal_metadata(
                doi=doi,
                return_as=return_as,
            )
        except Exception as exc:
            logger.warning(f"ArXiv DOI search error: {exc}")
            return self._create_minimal_metadata(
                doi=doi,
                return_as=return_as,
            )

    def _build_arxiv_search_query(
        self, title: str, authors: Optional[List[str]] = None
    ) -> str:
        """Build arXiv search query handling special characters.

        ArXiv's exact title search with quotes fails on special characters like (LSTM).
        Use keyword-based search instead for better results.
        """
        import re

        # Extract significant words from title (>3 chars, skip common words)
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "using",
            "based",
            "into",
            "that",
            "this",
        }
        words = re.findall(r"\b\w+\b", title.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stop_words][
            :8
        ]  # Limit to 8 keywords

        # Build query with title keywords
        query_parts = [f"ti:{word}" for word in keywords]

        # Add first author if available for better precision
        if authors and len(authors) > 0:
            first_author_surname = authors[0].split()[-1]
            query_parts.append(f"au:{first_author_surname}")

        return " AND ".join(query_parts)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError)
        ),
    )
    def _search_by_metadata(
        self,
        title: str,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: Optional[
            int
        ] = 5,  # Increased from 1 to get more candidates
        return_as: Optional[str] = "dict",
    ) -> Optional[Dict]:
        """Search by metadata other than doi"""
        if not title:
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

        # Build search query using keywords instead of exact title
        search_query = self._build_arxiv_search_query(title, authors)

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            for entry in feed.entries:
                entry_title = entry.get("title", "").replace("\n", " ").strip()
                if self._is_title_match(title, entry_title):
                    return self._extract_metadata_from_entry(entry, return_as)
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

        except Exception as exc:
            logger.warning(f"ArXiv metadata error: {exc}")
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError)
        ),
    )
    def _scrape_doi(self, url_publisher):
        try:
            response = requests.get(url_publisher)
            soup = BeautifulSoup(response.content, "html.parser")
            doi_link = soup.find(
                "a", href=lambda href: href and "doi.org" in href
            )
            doi = doi_link.get("href").split("doi.org/")[-1]
            return doi
        except Exception as e:
            logger.warning(f"DOI not scraped from {url_publisher}\n{str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError)
        ),
    )
    def _extract_metadata_from_entry(
        self, entry, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from ArXiv entry"""
        arxiv_id = entry.id.split("/abs/")[-1].split("v")[0]
        year = entry.get("published", "")[:4]
        title = entry.get("title")
        if title and title.endswith("."):
            title = title[:-1]
        abstract = entry.get("summary")
        authors = [author.get("name") for author in entry.get("authors")]
        url_publisher = entry.get("link")
        doi = self._scrape_doi(url_publisher)

        # Generate ArXiv DOI if not found
        if not doi:
            doi = f"10.48550/arxiv.{arxiv_id.lower()}"

        metadata = {
            "id": {
                "doi": doi,
                "doi_engines": [self.name],
                "arxiv_id": arxiv_id,
                "arxiv_id_engines": [self.name],
            },
            "basic": {
                "title": title if title else None,
                "title_engines": [self.name] if title else None,
                "year": year if year else None,
                "year_engines": [self.name] if year else None,
                "abstract": abstract.replace("\n", " ") if abstract else None,
                "abstract_engines": [self.name] if abstract else None,
                "authors": authors if authors else None,
                "authors_engines": [self.name] if authors else None,
            },
            "publication": {
                "journal": self.name,
                "journal_engines": [self.name],
            },
            "url": {
                "doi": f"https://doi.org/{doi}",
                "doi_engines": [self.name],
                "publisher": url_publisher if url_publisher else None,
                "publisher_engines": [self.name] if url_publisher else None,
            },
            "system": {
                f"searched_by_{self.name}": True,
            },
        }

        metadata = standardize_metadata(metadata)

        if return_as == "dict":
            return metadata
        if return_as == "json":
            return json.dumps(metadata, indent=2)

    # def _extract_metadata_from_entry(
    #     self, entry, return_as: str
    # ) -> Optional[Dict]:
    #     """Extract metadata from ArXiv entry"""
    #     arxiv_id = entry.id.split("/abs/")[-1].split("v")[0]
    #     year = entry.get("published", "")[:4]
    #     title = entry.get("title")
    #     if title and title.endswith("."):
    #         title = title[:-1]

    #     abstract = entry.get("summary")
    #     authors = [author.get("name") for author in entry.get("authors")]
    #     url_publisher = entry.get("link")
    #     doi = self._scrape_doi(url_publisher)

    #     metadata = {
    #         "id": {
    #             "doi": doi if doi else None,
    #             "doi_engines": [self.name] if doi else None,
    #             "arxiv_id": arxiv_id if arxiv_id else None,
    #             "arxiv_id_engines": [self.name] if arxiv_id else None,
    #         },
    #         "basic": {
    #             "title": title if title else None,
    #             "title_engines": [self.name] if title else None,
    #             "year": year if year else None,
    #             "year_engines": [self.name] if year else None,
    #             "abstract": abstract.replace("\n", " ") if abstract else None,
    #             "abstract_engines": [self.name] if abstract else None,
    #             "authors": authors if authors else None,
    #             "authors_engines": [self.name] if authors else None,
    #         },
    #         "publication": {
    #             "journal": self.name,
    #             "journal_engines": [self.name],
    #         },
    #         "url": {
    #             "doi": "https://doi.org/" + doi if doi else None,
    #             "doi_engines": [self.name] if doi else None,
    #             "publisher": url_publisher if url_publisher else None,
    #             "publisher_engines": [self.name] if url_publisher else None,
    #         },
    #         "system": {
    #             f"searched_by_{self.name}": True,
    #         },
    #     }

    #     metadata = standardize_metadata(metadata)
    #     if return_as == "dict":
    #         return metadata
    #     if return_as == "json":
    #         return json.dumps(metadata, indent=2)


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Attention is All You Need"
    DOI = "https://doi.org/10.48550/arXiv.1706.03762"

    # Example: ArXiv search
    engine = ArXivEngine("test@example.com")

    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = engine.search(title=TITLE)
    outputs["metadata_by_title_json"] = engine.search(
        title=TITLE, return_as="json"
    )

    # Search by DOI
    outputs["metadata_by_doi_dict"] = engine.search(doi=DOI)
    outputs["metadata_by_doi_json"] = engine.search(doi=DOI, return_as="json")

    # Empty Result
    outputs["empty_dict"] = engine._create_minimal_metadata(return_as="dict")
    outputs["empty_json"] = engine._create_minimal_metadata(return_as="json")

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)

# python -m scitex.scholar.engines.individual.ArXivEngine

# EOF
