#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 10:59:57 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_SemanticScholarSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_SemanticScholarSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import random
import time
from typing import List, Optional

import requests

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

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
    ) -> Optional[str]:
        """Get comprehensive metadata from Semantic Scholar."""
        if not title:
            return None

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
            response.raise_for_status()
            data = response.json()
            papers = data.get("data", [])

            for paper in papers:
                paper_title = paper.get("title", "")
                if self._is_title_match(title, paper_title):
                    doi = self._extract_doi_from_paper(
                        paper, title, year, authors
                    )
                    if doi:
                        paper_year = paper.get("year")
                        extracted_authors = []
                        for author in paper.get("authors", []):
                            if author.get("name"):
                                extracted_authors.append(author["name"])

                        external_ids = paper.get("externalIds", {})
                        scholar_id = external_ids.get("CorpusId")

                        metadata = {
                            "id": {
                                "doi": doi,
                                "doi_source": self.name,
                                "scholar_id": scholar_id,
                                "scholar_id_source": (
                                    self.name if scholar_id else None
                                ),
                            },
                            "basic": {
                                "title": paper_title if paper_title else None,
                                "title_source": (
                                    self.name if paper_title else None
                                ),
                                "year": paper_year if paper_year else None,
                                "year_source": (
                                    self.name if paper_year else None
                                ),
                                "abstract": (
                                    paper.get("abstract")
                                    if paper.get("abstract")
                                    else None
                                ),
                                "abstract_source": (
                                    self.name
                                    if paper.get("abstract")
                                    else None
                                ),
                                "authors": (
                                    extracted_authors
                                    if extracted_authors
                                    else None
                                ),
                                "authors_source": (
                                    self.name if extracted_authors else None
                                ),
                            },
                            "publication": {
                                "journal": (
                                    paper.get("venue")
                                    if paper.get("venue")
                                    else None
                                ),
                                "journal_source": (
                                    self.name if paper.get("venue") else None
                                ),
                            },
                            "url": {
                                "publisher": (
                                    paper.get("url")
                                    if paper.get("url")
                                    else None
                                ),
                                "publisher_source": (
                                    self.name if paper.get("url") else None
                                ),
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

            return None

        except Exception as exc:
            logger.warn(f"Semantic Scholar metadata error: {exc}")
            return None

    def _extract_doi_from_paper(
        self,
        paper: dict,
        query_title: str,
        query_year: Optional[int],
        query_authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        paper_title = paper.get("title", "")
        paper_year = paper.get("year")

        if not self._is_title_match(query_title, paper_title):
            return None

        if query_year and paper_year:
            try:
                paper_year_int = (
                    int(paper_year)
                    if isinstance(paper_year, str)
                    else paper_year
                )
                query_year_int = (
                    int(query_year)
                    if isinstance(query_year, str)
                    else query_year
                )
                if abs(paper_year_int - query_year_int) > 2:
                    return None
            except (ValueError, TypeError):
                pass

        external_ids = paper.get("externalIds", {})
        if external_ids and "DOI" in external_ids:
            doi = external_ids["DOI"]
            if doi:
                return self._clean_doi(doi)

        for field in ["doi", "DOI"]:
            if field in paper and paper[field]:
                return self._clean_doi(paper[field])

        paper_url = paper.get("url", "")
        if paper_url:
            doi = self.url_doi_extractor.extract_doi_from_url(paper_url)
            if doi:
                return doi

        return None

    def _clean_doi(self, doi: str) -> str:
        return doi.strip() if doi else doi

    def resolve_corpus_id(self, corpus_id: str) -> Optional[str]:
        if not corpus_id or not corpus_id.isdigit():
            return None

        max_retries = 3
        base_delay = 0.5 if self.api_key else 2.0

        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/paper/CorpusId:{corpus_id}"
                params = {"fields": "externalIds,title"}

                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = (base_delay * (2**attempt)) + random.uniform(
                            0.5, 1.5
                        )
                        time.sleep(delay)
                        continue
                    return None
                elif response.status_code == 404:
                    return None

                response.raise_for_status()

                data = response.json()
                external_ids = data.get("externalIds", {})
                doi = external_ids.get("DOI")
                if doi:
                    return doi
                return None

            except requests.HTTPError as exc:
                if exc.response and exc.response.status_code == 429:
                    continue
                return None
            except Exception as exc:
                return None
        return None


if __name__ == "__main__":
    from pprint import pprint

    source = SemanticScholarSource("test@example.com")

    metadata = source.search("Hippocampal ripples down-regulate synapses")
    pprint(metadata)

    corpus_doi = source.resolve_corpus_id("276988304")
    print(f"CorpusID DOI: {corpus_doi}")


# python -m scitex.scholar.metadata.doi.sources._SemanticScholarSource

# EOF
