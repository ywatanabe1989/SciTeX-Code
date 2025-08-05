#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:29:57 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_CitationEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_CitationEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Citation count enricher using CrossRef and Semantic Scholar."""

import asyncio
from scitex import logging
from typing import List, Optional

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .._Paper import Paper
from ._BaseEnricher import BaseEnricher

logger = logging.getLogger(__name__)


class CitationEnricher(BaseEnricher):
    """Enriches papers with citation counts."""

    def __init__(
        self,
        crossref_email: str = "research@example.com",
        semantic_scholar_api_key: Optional[str] = None,
    ):
        self.crossref_email = crossref_email
        self.ss_api_key = semantic_scholar_api_key

    @property
    def name(self) -> str:
        return "CitationEnricher"

    def can_enrich(self, paper: Paper) -> bool:
        """Check if paper needs citation count."""
        return paper.citation_count is None and paper.doi is not None

    def enrich(self, papers: List[Paper]) -> None:
        """Add citation counts to papers."""
        papers_to_enrich = [p for p in papers if self.can_enrich(p)]

        if not papers_to_enrich:
            return

        # Run async enrichment
        asyncio.run(self._enrich_async(papers_to_enrich))

    # async def _enrich_async(self, papers: List[Paper]) -> None:
    #     """Async enrichment implementation."""
    #     import aiohttp

    #     # Create session once
    #     async with aiohttp.ClientSession() as session:
    #         tasks = [self._get_citations_async(p, session) for p in papers]
    #         results = await asyncio.gather(*tasks, return_exceptions=True)

    #     tasks = [self._get_citations_async(p) for p in papers]
    #     results = await asyncio.gather(*tasks, return_exceptions=True)

    #     count = 0
    #     for paper, result in zip(papers, results):
    #         if isinstance(result, int):
    #             paper.citation_count = result
    #             paper.citation_count_source = "CrossRef"
    #             paper.metadata["citation_count_source"] = "CrossRef"
    #             count += 1

    #     if count:
    #         logger.info(f"Enriched {count} papers with citation counts")

    # async def _enrich_async(self, papers):
    #     async with aiohttp.ClientSession() as session:
    #         tasks = [self._get_citations_async(p, session) for p in papers]
    #         results = await asyncio.gather(*tasks, return_exceptions=True)

    #     count = 0
    #     for paper, result in zip(papers, results):
    #         if isinstance(result, Exception):
    #             logger.warning(
    #                 f"Failed to get citations for {paper.title}: {result}"
    #             )
    #         elif isinstance(result, int):
    #             paper.citation_count = result
    #             paper.citation_count_source = "CrossRef"
    #             paper.metadata["citation_count_source"] = "CrossRef"
    #             count += 1

    #     if count:
    #         logger.info(f"Enriched {count} papers with citation counts")

    async def _enrich_async(self, papers):
        async with aiohttp.ClientSession() as session:
            tasks = [self._get_citations_async(p, session) for p in papers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        count = 0
        for paper, result in zip(papers, results):
            if isinstance(result, Exception):
                logger.warning(
                    f"Failed to get citations for {paper.title}: {result}"
                )
            elif isinstance(result, int):
                paper.update_field_with_source(
                    "citation_count", result, "CrossRef"
                )
                count += 1

        if count:
            logger.info(f"Enriched {count} papers with citation counts")

    async def _get_citations_async(
        self, paper: Paper, session: aiohttp.ClientSession
    ) -> Optional[int]:
        """Get citation count for single paper."""
        if not paper.doi:
            return None

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            retry=retry_if_exception_type(
                (aiohttp.ClientError, asyncio.TimeoutError)
            ),
        )
        async def fetch_crossref_async():
            url = f"https://api.crossref.org/works/{paper.doi}"
            headers = {
                "User-Agent": f"SciTeX Scholar (mailto:{self.crossref_email})"
            }

            async with session.get(
                url, headers=headers, timeout=30
            ) as response:
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(
                        f"CrossRef rate limited, retry after {retry_after}s"
                    )
                    raise aiohttp.ClientError("Rate limited")

                if response.status == 200:
                    data = await response.json()
                    return data.get("message", {}).get(
                        "is-referenced-by-count"
                    )

        try:
            return await fetch_crossref_async()
        except Exception as exc:
            logger.debug(f"CrossRef lookup failed for {paper.doi}: {exc}")
            return None

# EOF
