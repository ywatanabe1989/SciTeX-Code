#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 20:23:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_AbstractEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_AbstractEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging
from typing import List, Optional

from ..._Paper import Paper
from ..doi._SingleDOIResolver import SingleDOIResolver
from ._BaseEnricher import BaseEnricher

logger = logging.getLogger(__name__)


class AbstractEnricher(BaseEnricher):
    """Enriches papers with abstracts from various sources."""

    def __init__(
        self,
        email_crossref: str = "research@example.com",
        email_pubmed: str = "research@example.com",
        email_openalex: str = "research@example.com",
        email_semantic_scholar: str = "research@example.com",
        sources: Optional[List[str]] = None,
    ):
        # Order sources by abstract coverage quality
        # Try all available sources for better coverage
        self.resolver = SingleDOIResolver(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            sources=sources or ["semantic_scholar", "pubmed", "crossref", "openalex", "arxiv"],
        )

    @property
    def name(self) -> str:
        return "AbstractEnricher"

    def can_enrich(self, paper: Paper) -> bool:
        """Check if paper needs abstract."""
        return not paper.abstract and paper.doi is not None

    # def enrich(self, papers: List[Paper]) -> None:
    #     """Add abstracts to papers."""
    #     papers_to_enrich = [p for p in papers if self.can_enrich(p)]
    #     if not papers_to_enrich:
    #         return

    #     count = 0
    #     for paper in papers_to_enrich:
    #         abstract_found = False

    #         # First try comprehensive metadata which may include abstract
    #         if not abstract_found:
    #             try:
    #                 metadata = self.resolver.get_comprehensive_metadata(
    #                     title=paper.title,
    #                     year=paper.year,
    #                     authors=paper.authors,
    #                 )
    #                 if metadata and metadata.get("abstract"):
    #                     source_name = metadata.get("source", "unknown")
    #                     paper.update_field_with_source(
    #                         "abstract", metadata["abstract"], source_name
    #                     )
    #                     count += 1
    #                     abstract_found = True
    #                     logger.debug(
    #                         f"Found abstract for '{paper.title[:50]}...' from {source_name}"
    #                     )
    #             except Exception as exc:
    #                 logger.debug(
    #                     f"Failed to get comprehensive metadata: {exc}"
    #                 )

    #         # If still no abstract, try direct abstract lookup
    #         if not abstract_found:
    #             abstract = self.resolver.get_abstract(paper.doi)
    #             if abstract:
    #                 paper.update_field_with_source(
    #                     "abstract", abstract, "DOI lookup"
    #                 )
    #                 count += 1
    #                 logger.debug(
    #                     f"Found abstract for '{paper.title[:50]}...' via DOI lookup"
    #                 )

    #     if count:
    #         logger.info(f"Enriched {count} papers with abstracts")
    def enrich(self, papers: List[Paper]) -> None:
        """Add abstracts to papers."""
        papers_to_enrich = [p for p in papers if self.can_enrich(p)]
        if not papers_to_enrich:
            return

        count = 0
        for paper in papers_to_enrich:
            abstract_found = False
            logger.info(
                f"Trying to get abstract for: {paper.title[:50]}... (DOI: {paper.doi})"
            )

            if not abstract_found:
                try:
                    metadata = self.resolver.get_comprehensive_metadata(
                        title=paper.title,
                        year=paper.year,
                        authors=paper.authors,
                    )
                    if metadata:
                        logger.info(
                            f"Got metadata from {metadata.get('source')}: {list(metadata.keys())}"
                        )
                        if metadata.get("abstract"):
                            source_name = metadata.get("source", "unknown")
                            paper.update_field_with_source(
                                "abstract", metadata["abstract"], source_name
                            )
                            count += 1
                            abstract_found = True
                            logger.info(
                                f"Found abstract for '{paper.title[:50]}...' from {source_name}"
                            )
                        else:
                            logger.info(
                                f"No abstract in metadata from {metadata.get('source')}"
                            )
                    else:
                        logger.info("No metadata found")
                except Exception as exc:
                    logger.error(
                        f"Failed to get comprehensive metadata: {exc}"
                    )

            if not abstract_found:
                logger.info(
                    f"Trying direct abstract lookup for DOI: {paper.doi}"
                )
                abstract = self.resolver.get_abstract(paper.doi)
                if abstract:
                    paper.update_field_with_source(
                        "abstract", abstract, "DOI lookup"
                    )
                    count += 1
                    logger.info(
                        f"Found abstract for '{paper.title[:50]}...' via DOI lookup"
                    )
                else:
                    logger.info("No abstract found via direct lookup")

        if count:
            logger.info(f"Enriched {count} papers with abstracts")
        else:
            logger.warning("No abstracts were found for any papers")

# EOF
