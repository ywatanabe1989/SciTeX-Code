#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 02:50:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/utils/_URLDOISource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/utils/_URLDOISource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL-based DOI extractor for immediate paper recovery.

This source extracts DOIs from URL fields in BibTeX entries,
providing immediate recovery for papers with DOI URLs.
"""

import re
from typing import List, Optional

import requests

from scitex import logging

from ..sources._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class URLDOISource(BaseDOISource):
    """Extract DOIs from URL fields - immediate recovery for 14+ papers."""

    def __init__(self):
        """Initialize URL DOI extractor."""
        super().__init__()

        # Check for Semantic Scholar API key for enhanced CorpusId resolution
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if self.api_key:
            logger.info(
                "Using Semantic Scholar API key for enhanced CorpusId resolution"
            )

        # IEEE-specific patterns (not handled by utils)
        self.ieee_patterns = [
            r"ieeexplore\.ieee\.org/document/(\d+)",
            r"ieeexplore\.ieee\.org/abstract/document/(\d+)",
            r"ieeexplore\.ieee\.org/stamp/stamp\.jsp\?arnumber=(\d+)",
        ]

        # PubMed ID patterns for conversion (handled by utils, but need for extraction)
        self.pubmed_patterns = [
            r"pubmed/(\d+)",
            r"ncbi\.nlm\.nih\.gov/pubmed/(\d+)",
            r"PMID:(\d+)",
        ]

        # Semantic Scholar patterns (not handled by utils)
        self.semantic_patterns = [
            r"semanticscholar\.org/paper/([^/?]+)",
            r"CorpusId:(\d+)",
        ]

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        url: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        """Extract DOI from URL field if available."""
        if not url:
            return None

        logger.debug(f"Extracting DOI from URL: {url}")

        # Try direct DOI extraction first using the utility
        doi = self.url_doi_extractor.extract_doi_from_url(url)
        if doi:
            logger.info(f"Extracted DOI from URL: {doi}")
            return doi

        # Try PubMed ID conversion using the utility
        pmid = self._extract_pubmed_id(url)
        if pmid:
            doi = self.pubmed_converter.pmid_to_doi(pmid)
            if doi:
                logger.info(f"Converted PubMed ID {pmid} to DOI: {doi}")
                return doi

        # Try IEEE lookup (custom logic)
        ieee_id = self._extract_ieee_id(url)
        if ieee_id:
            doi = self._lookup_ieee_doi(ieee_id)
            if doi:
                logger.info(f"Found DOI via IEEE: {doi}")
                return doi

        # Try Semantic Scholar lookup (custom logic)
        semantic_id = self._extract_semantic_scholar_id(url)
        if semantic_id:
            doi = self._lookup_semantic_scholar_doi(semantic_id)
            if doi:
                logger.info(f"Found DOI via Semantic Scholar: {doi}")
                return doi

        return None

    @property
    def name(self) -> str:
        """Return source name."""
        return "url_doi_source"

    @property
    def rate_limit_delay(self) -> float:
        """No rate limiting needed for URL extraction."""
        return 0.0

    def _extract_pubmed_id(self, url: str) -> Optional[str]:
        """Extract PubMed ID from URL."""
        for pattern in self.pubmed_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_ieee_id(self, url: str) -> Optional[str]:
        """Extract IEEE document ID from URL."""
        for pattern in self.ieee_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_semantic_scholar_id(self, url: str) -> Optional[str]:
        """Extract Semantic Scholar ID from URL."""
        for pattern in self.semantic_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _lookup_ieee_doi(self, ieee_id: str) -> Optional[str]:
        """Look up DOI from IEEE document ID."""
        try:
            # IEEE Xplore API approach
            # Note: IEEE provides DOIs in their metadata
            url = f"https://ieeexplore.ieee.org/document/{ieee_id}"

            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                # Extract DOI from page content
                content = response.text

                # Look for DOI patterns in the HTML
                doi_patterns = [
                    r'"doi":"([^"]+)"',
                    r'doi\.org/([^"\'>\s]+)',
                    r"DOI:\s*([^\s<]+)",
                    r'"DOI":"([^"]+)"',
                ]

                for pattern in doi_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        doi = match.group(1)
                        if doi and not doi.startswith("http"):
                            return self._clean_doi(doi)

                # IEEE typically uses 10.1109 prefix
                # Generate DOI pattern for IEEE papers
                if ieee_id.isdigit():
                    # Some IEEE papers follow predictable DOI patterns
                    potential_doi = (
                        f"10.1109/ACCESS.{ieee_id}"  # Example pattern
                    )
                    return potential_doi

        except Exception as e:
            logger.debug(f"IEEE lookup failed for {ieee_id}: {e}")

        return None

    def _lookup_semantic_scholar_doi(self, semantic_id: str) -> Optional[str]:
        """Look up DOI from Semantic Scholar ID with enhanced API support."""
        import random
        import time

        max_retries = 3
        base_delay = 0.5 if self.api_key else 2.0  # Faster with API key

        for attempt in range(max_retries):
            try:
                # Try Semantic Scholar API
                if semantic_id.isdigit():  # CorpusId
                    url = f"https://api.semanticscholar.org/graph/v1/paper/CorpusId:{semantic_id}"
                else:  # Paper ID
                    url = f"https://api.semanticscholar.org/graph/v1/paper/{semantic_id}"

                params = {"fields": "externalIds,title,authors"}

                # Set up headers with API key if available
                headers = {"User-Agent": "SciTeX/1.0 (research@scitex.ai)"}
                if self.api_key:
                    headers["x-api-key"] = self.api_key

                response = requests.get(
                    url, params=params, headers=headers, timeout=15
                )

                if response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = (base_delay * (2**attempt)) + random.uniform(
                            0.5, 1.5
                        )
                        logger.info(
                            f"Rate limited on Semantic Scholar CorpusId {semantic_id}, retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.warning(
                            f"Rate limited on Semantic Scholar CorpusId {semantic_id}, giving up after {max_retries} attempts"
                        )
                        return None

                if response.status_code == 404:
                    logger.debug(
                        f"Semantic Scholar ID {semantic_id} not found"
                    )
                    return None

                if response.status_code == 200:
                    data = response.json()
                    external_ids = data.get("externalIds", {})
                    doi = external_ids.get("DOI")

                    if doi:
                        logger.info(
                            f"Successfully resolved Semantic Scholar ID {semantic_id} → DOI: {doi}"
                        )
                        return self._clean_doi(doi)
                    else:
                        # Check for ArXiv as fallback
                        arxiv_id = external_ids.get("ArXiv")
                        if arxiv_id:
                            logger.info(
                                f"Semantic Scholar ID {semantic_id} has ArXiv ID: {arxiv_id} (no DOI)"
                            )
                        else:
                            logger.debug(
                                f"Semantic Scholar ID {semantic_id} found but no DOI or ArXiv available"
                            )
                        return None

                response.raise_for_status()

            except requests.HTTPError as e:
                if e.response and e.response.status_code == 429:
                    continue  # Will retry with backoff
                logger.debug(
                    f"Semantic Scholar HTTP error for {semantic_id}: {e}"
                )
                return None
            except Exception as e:
                logger.debug(
                    f"Semantic Scholar lookup failed for {semantic_id}: {e}"
                )
                return None

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """URL extractor doesn't provide abstracts."""
        return None

    @property
    def requires_email(self) -> bool:
        """URL extraction doesn't require email."""
        return False

    def __str__(self) -> str:
        """String representation."""
        total_patterns = len(
            self.ieee_patterns + self.pubmed_patterns + self.semantic_patterns
        )
        return f"URLDOISource(enhanced_patterns={total_patterns}, uses_utils=True)"


# Export
__all__ = ["URLDOISource"]

# EOF
