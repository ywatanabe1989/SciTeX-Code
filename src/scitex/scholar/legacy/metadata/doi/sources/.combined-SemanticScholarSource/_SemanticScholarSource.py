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

    def __init__(self, email: str = "research@example.com", api_key: str = None):
        super().__init__()  # Initialize base class to access utilities
        self.email = email
        self.api_key = api_key or os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        self._session = None
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        
        # Enhanced rate limiting based on API key availability
        self._rate_limit_delay = 0.5 if self.api_key else 2.0  # Faster with API key

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            import requests

            self._session = requests.Session()
            headers = {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
            
            # Add API key if available
            if self.api_key:
                headers["x-api-key"] = self.api_key
                logger.info("Using Semantic Scholar API key for enhanced rate limits")
            
            self._session.headers.update(headers)
        return self._session

    @property
    def name(self) -> str:
        return "SemanticScholar"

    @property
    def rate_limit_delay(self) -> float:
        return self._rate_limit_delay  # Dynamic based on API key availability

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.5, min=2, max=60),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"Rate limited, retrying in {retry_state.next_action.sleep:.1f} seconds..."
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
            doi = self._extract_doi_from_paper(paper, title, year)
            if doi:
                logger.info(f"Found DOI from Semantic Scholar: {doi}")
                return doi

        return None
        
    def _extract_doi_from_paper(self, paper: dict, query_title: str, query_year: Optional[int]) -> Optional[str]:
        """Enhanced DOI extraction from paper with multiple validation strategies."""
        paper_title = paper.get("title", "")
        paper_year = paper.get("year")
        
        # Title matching
        if not paper_title or not self._is_title_match(query_title, paper_title):
            return None
            
        # Year validation (if provided) - allow 2 year difference for robustness
        if query_year and paper_year:
            try:
                paper_year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                query_year_int = int(query_year) if isinstance(query_year, str) else query_year
                
                if abs(paper_year_int - query_year_int) > 2:
                    return None
            except (ValueError, TypeError):
                pass  # Skip year validation if conversion fails
        
        # Extract DOI from multiple possible fields
        external_ids = paper.get("externalIds", {})
        
        # Primary DOI field
        if external_ids and "DOI" in external_ids:
            doi = external_ids["DOI"]
            if doi:
                return doi.strip()
        
        # Alternative DOI sources
        for field in ["doi", "DOI"]:
            if field in paper and paper[field]:
                return paper[field].strip()
        
        # Extract from URL field if present using utility
        paper_url = paper.get("url", "")
        if paper_url:
            doi = self.url_doi_extractor.extract_doi_from_url(paper_url)
            if doi:
                return doi
        
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
        wait=wait_exponential(multiplier=1.5, min=2, max=60),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"Rate limited, retrying in {retry_state.next_action.sleep:.1f} seconds..."
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
            # Use enhanced DOI extraction logic
            doi = self._extract_doi_from_paper(paper, title, year)
            if doi:
                paper_title = paper.get("title", "")
                paper_year = paper.get("year")
                
                extracted_authors = []
                for author in paper.get("authors", []):
                    if author.get("name"):
                        extracted_authors.append(author["name"])

                return {
                    "doi": doi,
                    "title": paper_title,
                    "journal": paper.get("venue"),
                    "journal_source": "semantic_scholar",
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2.0, min=1, max=30),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"CorpusID resolution rate limited, retrying in {retry_state.next_action.sleep:.1f} seconds..."
        ),
    )
    def resolve_corpus_id(self, corpus_id: str) -> Optional[str]:
        """Resolve DOI from CorpusID using Semantic Scholar API."""
        if not corpus_id or not corpus_id.isdigit():
            return None
            
        try:
            url = f"{self.base_url}/paper/CorpusId:{corpus_id}"
            params = {"fields": "externalIds,title"}
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                raise requests.HTTPError("Rate limited", response=response)
            elif response.status_code == 404:
                logger.debug(f"CorpusID {corpus_id} not found in Semantic Scholar")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            external_ids = data.get('externalIds', {})
            doi = external_ids.get('DOI')
            
            if doi:
                logger.info(f"Resolved CorpusID {corpus_id} → DOI: {doi}")
                return doi
            else:
                logger.debug(f"CorpusID {corpus_id} found but no DOI available")
                return None
                
        except requests.HTTPError as e:
            if e.response and e.response.status_code == 429:
                raise  # Re-raise for retry logic
            logger.debug(f"CorpusID resolution HTTP error for {corpus_id}: {e}")
            return None
        except Exception as e:
            logger.debug(f"CorpusID resolution error for {corpus_id}: {e}")
            return None

# EOF
