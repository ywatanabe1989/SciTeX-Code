#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 23:54:23 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/_BaseDOIEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
from typing import Dict

"""
Abstract base class for DOI engines with enhanced rate limit handling.

This module defines the interface that all DOI engines must implement,
including automatic rate limit detection and retry mechanisms.
"""

import asyncio
import re
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import requests

from scitex import logging

from ..utils import (
    PubMedConverter,
    TextNormalizer,
    URLDOIExtractor,
    standardize_metadata,
)

logger = logging.getLogger(__name__)


class BaseDOIEngine(ABC):
    """Abstract base class for DOI engines with enhanced rate limit handling."""

    def __init__(self, email: str = "research@example.com"):
        """Initialize base engine."""
        self.email = email
        self.rate_limit_handler = None  # Will be injected by SingleDOIResolver
        self.last_request_time = 0.0
        self._request_count = 0

        # Lazy-loaded utilities - will be initialized when first accessed
        self._url_doi_extractor = None
        self._pubmed_converter = None
        self._session = None

    @abstractmethod
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search for DOI by title."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Engine name for logging."""
        pass

    @property
    def rate_limit_delay(self) -> float:
        return 1.0

    def set_rate_limit_handler(self, handler):
        """Set the rate limit handler for this engine."""
        self.rate_limit_handler = handler

    @property
    def text_normalizer(self):
        """Get TextNormalizer utility (class-based, no instantiation needed)."""
        return TextNormalizer

    @property
    def url_doi_extractor(self):
        """Get URLDOIEngine utility with lazy loading."""
        if self._url_doi_extractor is None:
            self._url_doi_extractor = URLDOIExtractor()
        return self._url_doi_extractor

    @property
    def pubmed_converter(self):
        """Get PubMedConverter utility with lazy loading."""
        if self._pubmed_converter is None:
            self._pubmed_converter = PubMedConverter()
        return self._pubmed_converter

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": self._get_user_agent()}
            )
        return self._session

    def _get_user_agent(self) -> str:
        """Get user agent string. Override in subclasses if needed."""
        return f"SciTeX/1.0 (mailto:{self.email})"

    def _clean_query(self, query: str) -> str:
        """Clean query string by removing meta characters that might interfere with API search.

        Meta characters like parentheses, brackets, special symbols can cause search issues
        in various APIs. This strips them while preserving the core searchable text.

        Args:
            query: Raw query string (e.g., title with special characters)

        Returns:
            Cleaned query string suitable for API search

        Example:
            >>> engine._clean_query("Memory (LSTM) neural networks")
            'Memory LSTM neural networks'
        """
        if not query:
            return query

        # Remove common meta characters but keep alphanumeric, spaces, and basic punctuation
        # Keep: letters, numbers, spaces, hyphens, periods, commas
        # Remove: ()[]{}!@#$%^&*+=<>?/\|~`"':;
        cleaned = re.sub(r'[()[\]{}!@#$%^&*+=<>?/\\|~`"\':;]', ' ', query)

        # Collapse multiple spaces into one
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def _make_request_with_retry(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> Optional[requests.Response]:
        """Make HTTP request with automatic rate limit handling and retries.

        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout
            max_retries: Maximum number of retries

        Returns:
            Response object or None if all retries failed
        """
        session = getattr(self, "session", requests)

        for attempt in range(max_retries + 1):
            try:
                # Apply rate limiting before request
                self._apply_rate_limiting()

                # Make the request
                self._request_count += 1
                self.last_request_time = time.time()

                response = session.get(
                    url, params=params, headers=headers, timeout=timeout
                )

                # Check for rate limits
                if self.rate_limit_handler:
                    rate_limit_info = (
                        self.rate_limit_handler.detect_rate_limit(
                            engine=self.name.lower(), response=response
                        )
                    )

                    if rate_limit_info:
                        self.rate_limit_handler.record_rate_limit(
                            rate_limit_info
                        )

                        # If this isn't the last attempt, wait and retry
                        if attempt < max_retries:
                            logger.info(
                                f"Rate limited on attempt {attempt + 1}/{max_retries + 1} "
                                f"for {self.name}, waiting {rate_limit_info.wait_time:.1f}s"
                            )
                            time.sleep(rate_limit_info.wait_time)
                            continue
                        else:
                            logger.warning(
                                f"Max retries exceeded for {self.name} due to rate limiting"
                            )
                            return None

                # Check for successful response
                if response.status_code == 200:
                    if self.rate_limit_handler:
                        self.rate_limit_handler.record_success(
                            self.name.lower()
                        )
                        # Record success for adaptive rate limiting
                        self.rate_limit_handler.record_request_outcome(
                            self.name.lower(), success=True
                        )
                    return response
                elif response.status_code in [429, 503, 502, 504]:
                    # Server errors that might be temporary
                    if attempt < max_retries:
                        wait_time = min(
                            2**attempt, 30
                        )  # Exponential backoff, max 30s
                        logger.info(
                            f"Server error {response.status_code} on attempt {attempt + 1}, "
                            f"waiting {wait_time}s before retry"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning(
                            f"Server error {response.status_code} after max retries"
                        )
                        return response  # Return for caller to handle
                else:
                    # Other HTTP errors
                    logger.debug(
                        f"HTTP {response.status_code} from {self.name}: {url}"
                    )
                    return response

            except requests.exceptions.Timeout as e:
                if self.rate_limit_handler:
                    rate_limit_info = (
                        self.rate_limit_handler.detect_rate_limit(
                            engine=self.name.lower(), exception=e
                        )
                    )
                    if rate_limit_info and attempt < max_retries:
                        self.rate_limit_handler.record_rate_limit(
                            rate_limit_info
                        )
                        logger.info(
                            f"Timeout on attempt {attempt + 1}, waiting {rate_limit_info.wait_time:.1f}s"
                        )
                        time.sleep(rate_limit_info.wait_time)
                        continue

                if attempt < max_retries:
                    wait_time = min(2**attempt, 15)
                    logger.info(
                        f"Timeout on attempt {attempt + 1}, waiting {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(
                        f"Timeout after {max_retries + 1} attempts for {self.name}"
                    )
                    if self.rate_limit_handler:
                        self.rate_limit_handler.record_failure(
                            self.name.lower(), e
                        )
                        # Record failure for adaptive rate limiting
                        self.rate_limit_handler.record_request_outcome(
                            self.name.lower(), success=False
                        )
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = min(2**attempt, 15)
                    logger.info(
                        f"Request error on attempt {attempt + 1}: {e}, waiting {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(
                        f"Request failed after {max_retries + 1} attempts: {e}"
                    )
                    if self.rate_limit_handler:
                        self.rate_limit_handler.record_failure(
                            self.name.lower(), e
                        )
                        # Record failure for adaptive rate limiting
                        self.rate_limit_handler.record_request_outcome(
                            self.name.lower(), success=False
                        )
                    return None

            except Exception as e:
                logger.error(f"Unexpected error in {self.name}: {e}")
                if self.rate_limit_handler:
                    self.rate_limit_handler.record_failure(
                        self.name.lower(), e
                    )
                    # Record failure for adaptive rate limiting
                    self.rate_limit_handler.record_request_outcome(
                        self.name.lower(), success=False
                    )
                return None

        return None

    def _apply_rate_limiting(self):
        """Apply rate limiting before making a request."""
        if not self.rate_limit_handler:
            logger.error(
                f"No rate limit handler set for {self.name}. This should not happen!"
            )
            return

        # Use advanced rate limiting with adaptive delays
        wait_time = self.rate_limit_handler.get_wait_time_for_engine(
            self.name.lower()
        )
        if wait_time > 0:
            logger.debug(
                f"Rate limiting {self.name}: waiting {wait_time:.1f}s"
            )
            time.sleep(wait_time)

    async def _apply_rate_limiting_async(self):
        """Apply rate limiting before making a request (async version)."""
        if not self.rate_limit_handler:
            logger.error(
                f"No rate limit handler set for {self.name}. This should not happen!"
            )
            return

        # Use advanced rate limiting with countdown and adaptive delays
        wait_time = self.rate_limit_handler.get_wait_time_for_engine(
            self.name.lower()
        )
        if wait_time > 0:
            await self.rate_limit_handler.wait_with_countdown_async(
                wait_time, self.name
            )

    async def search_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Async version of search method."""
        # Apply rate limiting
        await self._apply_rate_limiting_async()

        # Run sync search in executor
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, self.search, title, year, authors
            )
            return result
        except Exception as e:
            logger.error(f"Error in async search for {self.name}: {e}")
            if self.rate_limit_handler:
                self.rate_limit_handler.record_failure(self.name.lower(), e)
            return None

    def get_request_stats(self) -> dict:
        """Get request statistics for this engine."""
        return {
            "total_requests": self._request_count,
            "last_request_time": self.last_request_time,
            "rate_limit_delay": self.rate_limit_delay,
        }

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from URL if present."""
        if not url:
            return None

        # Direct DOI URLs
        if "doi.org/" in url:
            match = re.search(r"doi\.org/(.+?)(?:\?|$|#)", url)
            if match:
                return match.group(1).strip()

        # DOI pattern in URL
        doi_pattern = r"10\.\d{4,}/[-._;()/:\w]+"
        match = re.search(doi_pattern, url)
        if match:
            return match.group(0)

        return None

    def _is_title_match(
        self, title1: str, title2: str, threshold: float = 0.95
    ) -> bool:
        """
        Check if two titles match using the enhanced TextNormalizer utility.

        DEPRECATED: Use self.text_normalizer.is_likely_same_title() directly in new code.
        This method is kept for backward compatibility.
        """
        return self.text_normalizer.is_likely_same_title(title1, title2, threshold)

    def _create_minimal_metadata(
        self,
        doi=None,
        pmid=None,
        corpus_id=None,
        ieee_id=None,
        semantic_id=None,
        title=None,
        year=None,
        authors=None,
        return_as: str = "dict",
    ) -> Optional[Dict]:
        """Create empty result structure with tracking information when no metadata is found."""

        # Add system tracking
        metadata = {
            "id": {
                "doi": doi,
                "doi_engines": [self.name] if doi else None,
                "pmid": pmid,
                "pmid_engines": [self.name] if pmid else None,
                "corpus_id": corpus_id,
                "corpus_id_engines": [self.name] if corpus_id else None,
                "semantic_id": semantic_id,
                "semantic_id_engines": ([self.name] if semantic_id else None),
                "ieee_id": ieee_id,
                "ieee_id_engines": [self.name] if ieee_id else None,
            },
            "basic": {
                "title": title if title else None,
                "title_engines": [self.name] if title else None,
                "year": year if year else None,
                "year_engines": [self.name] if year else None,
                "authors": authors if authors else None,
                "authors_engines": [self.name] if authors else None,
            },
        }

        metadata = standardize_metadata(metadata)

        if return_as == "dict":
            return metadata
        elif return_as == "json":
            return json.dumps(metadata, indent=2)
        else:
            return metadata


if __name__ == "__main__":

    def main():
        class MockEngine(BaseDOIEngine):
            @property
            def name(self) -> str:
                return "MockEngine"

            def search(
                self,
                title: str,
                year: Optional[int] = None,
                authors: Optional[List[str]] = None,
            ) -> Optional[str]:
                return None

        engine = MockEngine()
        result = engine._create_minimal_metadata(
            # doi="10.1234/test",
            # title="Test Paper",
            # year=2023,
            # authors=["John Doe"],
        )
        print("Mock engine metadata:")
        print(json.dumps(result, indent=2))

    main()

# python -m scitex.scholar.engines.individual._BaseDOIEngine

# EOF
