#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 18:25:00 (ywatanabe)"
# File: ./src/scitex/scholar/doi/sources/_SemanticScholarSourceEnhanced.py
# ----------------------------------------
from __future__ import annotations

"""Enhanced Semantic Scholar DOI source with improved extraction logic.

This enhanced version addresses issues found in the original implementation:
1. Better title matching with Unicode normalization
2. More robust DOI extraction from multiple fields
3. Enhanced debugging and logging
4. Improved error handling
"""

from typing import List, Optional
import requests
from scitex import logging

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


def is_rate_limited(exception):
    """Check if exception is due to rate limiting."""
    return (
        isinstance(exception, requests.HTTPError)
        and exception.response.status_code == 429
    )


class SemanticScholarSourceEnhanced(BaseDOISource):
    """Enhanced Semantic Scholar source with improved DOI extraction."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()
        self.email = email
        self._session = None
        self.base_url = "https://api.semanticscholar.org/graph/v1"

    @property
    def session(self):
        """Lazy load session with proper headers."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": f"SciTeX/1.0 (mailto:{self.email})",
                "Accept": "application/json"
            })
        return self._session

    @property
    def name(self) -> str:
        return "semantic_scholar_enhanced"

    @property
    def rate_limit_delay(self) -> float:
        return 1.2  # Slightly more conservative than original

    def _is_title_match(self, query_title: str, paper_title: str, threshold: float = 0.8) -> bool:
        """Enhanced title matching using TextNormalizer utility."""
        # Use the advanced TextNormalizer from utils
        is_match = self.text_normalizer.is_likely_same_title(query_title, paper_title, threshold)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Title match result: {is_match} (threshold: {threshold})")
            logger.debug(f"Query: {query_title}")
            logger.debug(f"Paper: {paper_title}")

        return is_match

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.5, min=2, max=60),
        retry=retry_if_exception(is_rate_limited),
        before_sleep=lambda retry_state: logger.info(
            f"Semantic Scholar rate limited, retrying in {retry_state.next_action.sleep:.1f}s..."
        ),
    )
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Enhanced search with better DOI extraction."""
        if not title:
            return None
            
        logger.debug(f"Searching Semantic Scholar for: {title}")
        
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": "title,year,authors,externalIds,url,venue",
            "limit": 10,  # Increased limit for better matching
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 429:
                raise requests.HTTPError("Rate limited", response=response)
            
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"Semantic Scholar returned {len(data.get('data', []))} results")
            
            papers = data.get("data", [])
            
            # Try multiple matching strategies
            for paper in papers:
                doi = self._extract_doi_from_paper(paper, title, year, authors)
                if doi:
                    logger.info(f"Found DOI via enhanced Semantic Scholar: {doi}")
                    return doi
            
            logger.debug("No DOI found in Semantic Scholar results")
            return None
            
        except requests.RequestException as e:
            logger.debug(f"Semantic Scholar API error: {e}")
            return None

    def _extract_doi_from_paper(
        self, 
        paper: dict, 
        query_title: str, 
        query_year: Optional[int], 
        query_authors: Optional[List[str]]
    ) -> Optional[str]:
        """Extract DOI from paper with multiple validation strategies."""
        
        paper_title = paper.get("title", "")
        paper_year = paper.get("year")
        
        # Title matching
        if not self._is_title_match(query_title, paper_title):
            logger.debug(f"Title mismatch: '{paper_title}' vs '{query_title}'")
            return None
        
        # Year validation (if provided)
        if query_year and paper_year:
            try:
                paper_year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                query_year_int = int(query_year) if isinstance(query_year, str) else query_year
                
                if abs(paper_year_int - query_year_int) > 2:  # Allow 2 year difference
                    logger.debug(f"Year mismatch: {paper_year_int} vs {query_year_int}")
                    return None
            except (ValueError, TypeError):
                pass  # Skip year validation if conversion fails
        
        # Extract DOI from multiple possible fields
        external_ids = paper.get("externalIds", {})
        
        # Primary DOI field
        if external_ids and "DOI" in external_ids:
            doi = external_ids["DOI"]
            if doi:
                return self._clean_doi(doi)
        
        # Alternative DOI sources
        for field in ["doi", "DOI"]:
            if field in paper and paper[field]:
                return self._clean_doi(paper[field])
        
        # Extract from URL field if present using utility
        paper_url = paper.get("url", "")
        if paper_url:
            doi = self.url_doi_extractor.extract_doi_from_url(paper_url)
            if doi:
                return doi
        
        logger.debug(f"No DOI found in paper: {paper_title}")
        return None

    def _clean_doi(self, doi: str) -> str:
        """Clean and normalize DOI (minimal wrapper for consistency)."""
        if not doi:
            return doi
        # Basic cleaning - full DOI cleaning is handled by utils when needed
        return doi.strip()

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from Semantic Scholar by DOI."""
        url = f"{self.base_url}/paper/DOI:{doi}"
        params = {"fields": "abstract"}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get("abstract")
            
        except requests.RequestException as e:
            logger.debug(f"Error fetching abstract for DOI {doi}: {e}")
            return None

    @property
    def requires_email(self) -> bool:
        """Semantic Scholar doesn't strictly require email but it's recommended."""
        return False

    def __str__(self) -> str:
        return f"SemanticScholarSourceEnhanced(email={self.email})"


# Export
__all__ = ["SemanticScholarSourceEnhanced"]

# EOF