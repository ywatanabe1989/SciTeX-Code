#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:28:40 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_DOIEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_DOIEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""DOI-first enricher that adds DOIs before other enrichment."""

import logging
from typing import List

from .._Paper import Paper
from ..doi._DOIResolver import DOIResolver
from ._BaseEnricher import BaseEnricher

logger = logging.getLogger(__name__)


class DOIEnricher(BaseEnricher):
    """Ensures papers have DOIs before other enrichment."""

    def __init__(
        self,
        email_crossref: str = "research@example.com",
        email_pubmed: str = "research@example.com",
        email_openalex: str = "research@example.com",
        email_semantic_scholar: str = "research@example.com",
    ):
        self.resolver = DOIResolver(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
        )

    @property
    def name(self) -> str:
        return "DOIEnricher"

    def can_enrich(self, paper: Paper) -> bool:
        """Check if paper needs DOI."""
        return paper.doi is None and paper.title is not None

    # def enrich(self, papers: List[Paper]) -> None:
    #     """Add DOIs to papers that don't have them."""
    #     count = 0

    #     for paper in papers:
    #         if not self.can_enrich(paper):
    #             continue

    #         # Resolve DOI from title
    #         doi = self.resolver.title_to_doi(
    #             title=paper.title,
    #             year=paper.year,
    #             authors=tuple(paper.authors) if paper.authors else None,
    #         )

    #         if doi:
    #             paper.doi = doi
    #             paper.metadata["doi_source"] = "resolved"
    #             count += 1
    #             logger.debug(f"Found DOI for '{paper.title[:50]}...': {doi}")

    #     if count:
    #         logger.info(f"Resolved {count} DOIs from titles")

    # def enrich(self, papers: List[Paper]) -> None:
    #     """Add DOIs and comprehensive metadata to papers."""
    #     count = 0
    #     for paper in papers:
    #         if not self.can_enrich(paper):
    #             continue

    #         # Get comprehensive metadata from DOI resolver
    #         metadata = self.resolver.get_comprehensive_metadata(
    #             title=paper.title,
    #             year=paper.year,
    #             authors=tuple(paper.authors) if paper.authors else None,
    #         )

    #         if metadata and metadata.get("doi"):
    #             # Update DOI
    #             paper.doi = metadata["doi"]
    #             paper.metadata["doi_source"] = "resolved"

    #             # Update all available metadata fields
    #             if metadata.get("journal") and not paper.journal:
    #                 paper.journal = metadata["journal"]

    #             if metadata.get("year") and not paper.year:
    #                 paper.year = str(metadata["year"])

    #             if metadata.get("abstract") and not paper.abstract:
    #                 paper.abstract = metadata["abstract"]

    #             if metadata.get("authors") and not paper.authors:
    #                 paper.authors = metadata["authors"]

    #             # Add any other metadata found
    #             for key, value in metadata.items():
    #                 if (
    #                     key
    #                     not in [
    #                         "doi",
    #                         "journal",
    #                         "year",
    #                         "abstract",
    #                         "authors",
    #                     ]
    #                     and value
    #                 ):
    #                     paper.metadata[f"resolved_{key}"] = value

    #             count += 1
    #             logger.debug(
    #                 f"Enriched '{paper.title[:50]}...' with metadata from {metadata.get('source', 'unknown')}"
    #             )

    #     if count:
    #         logger.info(
    #             f"Enriched {count} papers with DOIs and comprehensive metadata"
    #         )

    def enrich(self, papers: List[Paper]) -> None:
        """Add DOIs and comprehensive metadata with source tracking."""
        count = 0
        for paper in papers:
            if not self.can_enrich(paper):
                continue

            metadata = self.resolver.get_comprehensive_metadata(
                title=paper.title,
                year=paper.year,
                authors=tuple(paper.authors) if paper.authors else None,
            )

            if metadata and metadata.get("doi"):
                source_name = metadata.get("source", "unknown")

                # Update fields using the tracking method
                paper.update_field_with_source(
                    "doi", metadata["doi"], source_name
                )

                if metadata.get("journal") and not paper.journal:
                    paper.update_field_with_source(
                        "journal", metadata["journal"], source_name
                    )

                if metadata.get("year") and not paper.year:
                    paper.update_field_with_source(
                        "year", str(metadata["year"]), source_name
                    )

                if metadata.get("abstract") and not paper.abstract:
                    paper.update_field_with_source(
                        "abstract", metadata["abstract"], source_name
                    )

                if metadata.get("authors") and not paper.authors:
                    paper.update_field_with_source(
                        "authors", metadata["authors"], source_name
                    )

                if metadata.get("title") and metadata["title"] != paper.title:
                    paper._additional_metadata["original_title"] = paper.title
                    paper.update_field_with_source(
                        "title", metadata["title"], source_name
                    )

                count += 1
                logger.debug(
                    f"Enriched '{paper.title[:50]}...' with metadata from {source_name}"
                )

        if count:
            logger.info(
                f"Enriched {count} papers with DOIs and comprehensive metadata"
            )

# EOF
