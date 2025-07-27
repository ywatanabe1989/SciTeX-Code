#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 19:33:51 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_EnricherPipeline.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_EnricherPipeline.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Simplified enrichment pipeline that starts with DOI resolution."""

import logging
from typing import List, Optional

from .._Paper import Paper
from ._AbstractEnricher import AbstractEnricher
from ._CitationEnricher import CitationEnricher
from ._DOIEnricher import DOIEnricher
from ._ImpactFactorEnricher import ImpactFactorEnricher
from ._KeywordEnricher import KeywordEnricher

logger = logging.getLogger(__name__)


class EnricherPipeline:
    """Simple enrichment pipeline: DOI -> Citations -> Impact Factors -> Abstracts -> Keywords."""

    def __init__(
        self,
        email_crossref: str = "research@example.com",
        email_pubmed: str = "research@example.com",
        email_openalex: str = "research@example.com",
        email_semantic_scholar: str = "research@example.com",
        semantic_scholar_api_key: Optional[str] = None,
    ):
        # Order matters: DOI first
        self.doi_enricher = DOIEnricher(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
        )
        self.citation_enricher = CitationEnricher(
            crossref_email=email_crossref,
            semantic_scholar_api_key=semantic_scholar_api_key,
        )
        self.impact_enricher = ImpactFactorEnricher()
        self.abstract_enricher = AbstractEnricher(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
        )
        self.keyword_enricher = KeywordEnricher(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
        )

    def enrich(self, papers: List[Paper]) -> None:
        """Run enrichment in order: DOI -> Citations -> Impact Factors -> Abstracts -> Keywords."""
        if not papers:
            return
        logger.info(f"Enriching {len(papers)} papers")

        # Step 1: Ensure all papers have DOIs FIRST
        self.doi_enricher.enrich(papers)
        # Step 2: Get citations (requires DOI)
        self.citation_enricher.enrich(papers)
        # Step 3: Get impact factors (requires journal)
        self.impact_enricher.enrich(papers)
        # Step 4: Get abstracts (requires DOI)
        self.abstract_enricher.enrich(papers)
        # Step 5: Get keywords
        self.keyword_enricher.enrich(papers)

        # Summary
        papers_with_doi = sum(1 for p in papers if p.doi)
        papers_with_citations = sum(
            1 for p in papers if p.citation_count is not None
        )
        papers_with_if = sum(1 for p in papers if p.impact_factor is not None)
        papers_with_abstract = sum(1 for p in papers if p.abstract)
        papers_with_keywords = sum(1 for p in papers if p.keywords)

        logger.info(
            f"Enrichment complete: "
            f"{papers_with_doi} DOIs, "
            f"{papers_with_citations} citations, "
            f"{papers_with_if} impact factors, "
            f"{papers_with_abstract} abstracts, "
            f"{papers_with_keywords} keywords"
        )


# class EnricherPipeline:
#     """Simple enrichment pipeline: DOI -> Citations -> Impact Factors."""

#     def __init__(
#         self,
#         email_crossref: str = "research@example.com",
#         email_pubmed: str = "research@example.com",
#         email_openalex: str = "research@example.com",
#         email_semantic_scholar: str = "research@example.com",
#         semantic_scholar_api_key: Optional[str] = None,
#     ):
#         # Order matters: DOI first
#         self.doi_enricher = DOIEnricher(
#             email_crossref=email_crossref,
#             email_pubmed=email_pubmed,
#             email_openalex=email_openalex,
#             email_semantic_scholar=email_semantic_scholar,
#         )
#         self.citation_enricher = CitationEnricher(
#             crossref_email=email_crossref,
#             semantic_scholar_api_key=semantic_scholar_api_key,
#         )
#         self.impact_enricher = ImpactFactorEnricher()
#         self.abstract_enricher = AbstractEnricher(
#             email_crossref=email_crossref,
#             email_pubmed=email_pubmed,
#             email_openalex=email_openalex,
#             email_semantic_scholar=email_semantic_scholar,
#         )

#     # def enrich(self, papers: List[Paper]) -> None:
#     #     """Run enrichment in order: DOI -> Citations -> Impact Factors -> Abstracts."""
#     #     if not papers:
#     #         return

#     #     logger.info(f"Enriching {len(papers)} papers")

#     #     # Step 1: Ensure all papers have DOIs
#     #     self.doi_enricher.enrich(papers)

#     #     # Step 2: Get citations (requires DOI)
#     #     self.citation_enricher.enrich(papers)

#     #     # Step 3: Get impact factors (requires journal)
#     #     self.impact_enricher.enrich(papers)

#     #     # Step 4: Get abstracts (requires DOI)
#     #     self.abstract_enricher.enrich(papers)

#     #     # Summary
#     #     papers_with_doi = sum(1 for p in papers if p.doi)
#     #     papers_with_citations = sum(
#     #         1 for p in papers if p.citation_count is not None
#     #     )
#     #     papers_with_if = sum(1 for p in papers if p.impact_factor is not None)
#     #     papers_with_abstract = sum(1 for p in papers if p.abstract)

#     #     logger.info(
#     #         f"Enrichment complete: "
#     #         f"{papers_with_doi} DOIs, "
#     #         f"{papers_with_citations} citations, "
#     #         f"{papers_with_if} impact factors, "
#     #         f"{papers_with_abstract} abstracts"
#     #     )

#     def enrich(self, papers: List[Paper]) -> None:
#         """Run enrichment in order: DOI -> Citations -> Impact Factors -> Abstracts."""
#         if not papers:
#             return

#         logger.info(f"Enriching {len(papers)} papers")

#         # Step 1: Ensure all papers have DOIs FIRST
#         self.doi_enricher.enrich(papers)

#         # Step 2: Get citations (requires DOI)
#         self.citation_enricher.enrich(papers)

#         # Step 3: Get impact factors (requires journal)
#         self.impact_enricher.enrich(papers)

#         # Step 4: Get abstracts (requires DOI)
#         self.abstract_enricher.enrich(papers)

#         # Summary
#         papers_with_doi = sum(1 for p in papers if p.doi)
#         papers_with_citations = sum(
#             1 for p in papers if p.citation_count is not None
#         )
#         papers_with_if = sum(1 for p in papers if p.impact_factor is not None)
#         papers_with_abstract = sum(1 for p in papers if p.abstract)

#         logger.info(
#             f"Enrichment complete: "
#             f"{papers_with_doi} DOIs, "
#             f"{papers_with_citations} citations, "
#             f"{papers_with_if} impact factors, "
#             f"{papers_with_abstract} abstracts"
#         )

# EOF
