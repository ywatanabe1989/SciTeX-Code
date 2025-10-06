#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:14:22 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_SemanticScholarSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from functools import lru_cache
from typing import Dict, List, Optional, Union

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import to_complete_metadata_structure
from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class SemanticScholarSource(BaseDOISource):
    """Combined Semantic Scholar source with enhanced features."""

    def __init__(
        self, email: str = "research@example.com", api_key: str = None
    ):
        super().__init__(email)
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self._rate_limit_delay = 0.5 if self.api_key else 1.2

    def _get_user_agent(self) -> str:
        return f"SciTeX/1.0 (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "Semantic_Scholar"

    @property
    def rate_limit_delay(self) -> float:
        return self._rate_limit_delay

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            headers = {
                "User-Agent": self._get_user_agent(),
                "Accept": "application/json",
            }
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self._session.headers.update(headers)
        return self._session

    def _handle_rate_limit(self):
        """Handle rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        corpus_id: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi or corpus_id is provided, all other information is ignored"""
        if doi:
            return self._search_by_doi(doi, return_as)
        elif corpus_id:
            return self._search_by_corpus_id(corpus_id, return_as)
        else:
            return self._search_by_metadata(
                title, year, authors, max_results, return_as
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_doi(self, doi: str, return_as: str) -> Optional[Dict]:
        """Search by DOI directly"""
        self._handle_rate_limit()

        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )
        url = f"{self.base_url}/paper/{doi}"
        params = {
            "fields": "title,year,authors,externalIds,url,venue,abstract"
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            # if response.status_code == 429:
            #     raise requests.ConnectionError("Rate limit exceeded")

            # if response.status_code == 404:
            #     logger.warn(f"Semantic Scholar DOI not found: {doi}")
            #     return None

            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata_from_paper(paper, return_as)
        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warn(f"Semantic Scholar DOI search error: {exc}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_metadata(
        self,
        title: str,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: int = 1,
        return_as: str = "dict",
    ) -> Optional[Dict]:
        """Search by metadata other than doi"""
        if not title:
            return None

        self._handle_rate_limit()
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": "title,year,authors,externalIds,url,venue,abstract",
            "limit": 10,
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                raise requests.ConnectionError("Rate limit exceeded")
            response.raise_for_status()

            data = response.json()
            papers = data.get("data", [])

            for paper in papers:
                paper_title = paper.get("title", "")
                paper_year = paper.get("year")
                paper_authors = [
                    author.get("name", "")
                    for author in paper.get("authors", [])
                ]

                # Check title match
                if not self._is_title_match(title, paper_title):
                    continue

                # Check year match if provided
                if year and paper_year and int(year) != int(paper_year):
                    continue

                # Check author match if provided
                if authors and paper_authors:
                    # Check if any provided author appears in paper authors
                    author_match = any(
                        any(
                            provided_author.lower() in paper_author.lower()
                            for paper_author in paper_authors
                        )
                        for provided_author in authors
                    )
                    if not author_match:
                        continue

                return self._extract_metadata_from_paper(paper, return_as)

            return None

        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warn(f"Semantic Scholar metadata error: {exc}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_corpus_id(
        self, corpus_id: str, return_as: str
    ) -> Optional[Dict]:
        """Search by Corpus ID directly"""
        if not corpus_id.isdigit():
            corpus_id = corpus_id.replace("CorpusId:", "")

        self._handle_rate_limit()

        url = f"{self.base_url}/paper/CorpusId:{corpus_id}"
        params = {
            "fields": "title,year,authors,externalIds,url,venue,abstract"
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                raise requests.ConnectionError("Rate limit exceeded")

            if response.status_code == 404:
                logger.warn(
                    f"Semantic Scholar Corpus ID not found: {corpus_id}"
                )
                return None

            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata_from_paper(paper, return_as)
        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warn(f"Semantic Scholar Corpus ID search error: {exc}")
            return None

    def _extract_metadata_from_paper(
        self, paper: dict, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from Semantic Scholar paper"""
        paper_title = paper.get("title", "")
        paper_year = paper.get("year")
        extracted_authors = []
        for author in paper.get("authors", []):
            if author.get("name"):
                extracted_authors.append(author["name"])

        external_ids = paper.get("externalIds", {})
        doi = external_ids.get("DOI")
        corpus_id = external_ids.get("CorpusId")

        metadata = {
            "id": {
                "doi": doi,
                "doi_sources": [self.name] if doi else None,
                "corpus_id": corpus_id,
                "corpus_id_sources": [self.name] if corpus_id else None,
            },
            "basic": {
                "title": paper_title if paper_title else None,
                "title_sources": [self.name] if paper_title else None,
                "year": paper_year if paper_year else None,
                "year_sources": [self.name] if paper_year else None,
                "abstract": (
                    paper.get("abstract") if paper.get("abstract") else None
                ),
                "abstract_sources": (
                    [self.name] if paper.get("abstract") else None
                ),
                "authors": extracted_authors if extracted_authors else None,
                "authors_sources": [self.name] if extracted_authors else None,
            },
            "publication": {
                "journal": paper.get("venue") if paper.get("venue") else None,
                "journal_sources": [self.name] if paper.get("venue") else None,
            },
            "url": {
                "doi": f"https://doi.org/{doi}" if doi else None,
                "doi_sources": [self.name] if doi else None,
                "publisher": paper.get("url") if paper.get("url") else None,
                "publisher_sources": [self.name] if paper.get("url") else None,
            },
            "system": {
                f"searched_by_{self.name}": True,
            },
        }

        metadata = to_complete_metadata_structure(metadata)

        if return_as == "dict":
            return metadata
        if return_as == "json":
            return json.dumps(metadata, indent=2)

    def _clean_doi(self, doi: str) -> str:
        return doi.strip() if doi else doi


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Attention is All You Need"
    DOI = "10.1126/science.aao0702"
    CORPUS_ID = "276988304"

    source = SemanticScholarSource("test@example.com")
    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = source.search(title=TITLE)
    outputs["metadata_by_title_json"] = source.search(
        title=TITLE, return_as="json"
    )

    # # Search by DOI
    # outputs["metadata_by_doi_dict"] = source.search(doi=DOI)
    # outputs["metadata_by_doi_json"] = source.search(doi=DOI, return_as="json")

    # # Search by Corpus ID
    # outputs["metadata_by_corpus_id_dict"] = source.search(corpus_id=CORPUS_ID)
    # outputs["metadata_by_corpus_id_json"] = source.search(
    #     corpus_id=CORPUS_ID, return_as="json"
    # )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)


# python -m scitex.scholar.metadata.doi.sources._SemanticScholarSource

# EOF
