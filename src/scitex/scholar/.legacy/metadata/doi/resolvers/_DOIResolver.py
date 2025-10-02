#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 19:22:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/resolvers/_DOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Optional, Tuple, Union

"""Unified DOI resolver with automatic input type detection."""

from pathlib import Path
from typing import Dict, List

import bibtexparser

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._LibraryManager import LibraryManager

from ._BatchDOIResolver import BatchDOIResolver
from ._BibTeXDOIResolver import BibTeXDOIResolver
from ._SingleDOIResolver import SingleDOIResolver

logger = logging.getLogger(__name__)


class DOIResolver:
    """Unified DOI resolver that automatically handles different input types."""

    def __init__(
        self,
        config: Optional[ScholarConfig] = None,
        project: str = None,
        sources: Optional[List[str]] = None,
        # SingleDOIResolver
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        semantic_scholar_api_key: str = None,
        crossref_api_key: str = None,
        # BatchDOIResolver
        doi_resolution_progress_file: Optional[Path] = None,
        max_worker: int = 4,
    ):
        """Initialize unified DOI resolver."""
        self.config = config or ScholarConfig()

        self._single_doi_resolver = SingleDOIResolver(
            project=project,
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            email_arxiv=email_arxiv,
            sources=sources,
            semantic_scholar_api_key=semantic_scholar_api_key,
            crossref_api_key=crossref_api_key,
            config=self.config,
        )

        self._bibtex_doi_resolver = BibTeXDOIResolver(
            project=project,
            config=self.config,
        )

        self._batch_doi_resolver = BatchDOIResolver(
            project=project,
            doi_resolution_progress_file=doi_resolution_progress_file,
            max_worker=max_worker,
            config=self.config,
        )

    # Single paper methods - delegate to SingleDOIResolver
    async def metadata2doi_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_entry: Optional[Dict] = None,
        skip_cache: bool = False,
    ) -> Optional[Dict[str, Any]]:
        return await self._single_doi_resolver.metadata2doi_async(
            title=title,
            year=year,
            authors=authors,
            bibtex_entry=bibtex_entry,
            skip_cache=skip_cache,
        )

    def text2dois(self, text: str):
        return self._single_doi_resolver.text2dois(text)

    # BibTeX methods - delegate to BibTeXDOIResolver
    async def bibtex_file2dois_async(
        self,
        bibtex_input_path: Union[str, Path],
        project: Optional[str] = None,
    ) -> Tuple[int, int, int]:
        """Resolve DOIs for all entries in BibTeX file."""
        return await self._bibtex_doi_resolver.bibtex_file2dois_async(
            bibtex_input_path,
            project=project,
        )

    # Batch methods - delegate to BatchDOIResolver
    async def papers2title_and_dois_async(
        self, papers: List[Dict[str, Any]], sources: Optional[List[str]] = None
    ) -> Dict[str, str]:
        return await self._batch_doi_resolver.papers2title_and_dois_async(
            papers, sources
        )


if __name__ == "__main__":
    import asyncio

    async def main():
        """Demonstrate DOIResolver usage patterns."""
        print("=" * 50)
        print("DOIResolver Usage Examples")
        print("=" * 50)

        # Initialize resolver
        resolver = DOIResolver(project="hippocampus")

        # # 1. Single paper resolution
        # print("\n1. Single Paper Resolution:")
        # result = await resolver.metadata2doi_async(
        #     title="Attention is All You Need",
        #     year=2017,
        #     authors=["Vaswani", "Shazeer"],
        # )
        # print(f"   Result: {result}")

        # # 2. Text DOI extraction
        # print("\n2. DOI Extraction from Text:")
        # sample_text = "See DOI: 10.1038/nature12373 for details"
        # dois = resolver.text2dois(sample_text)
        # print(f"   Found DOIs: {dois}")

        # # 3. Batch paper processing
        # print("\n3. Batch Paper Processing:")
        # papers = [
        #     {
        #         "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        #         "year": 2018,
        #         "authors": ["Devlin", "Chang"],
        #     },
        #     {
        #         "title": "Language Models are Few-Shot Learners",
        #         "year": 2020,
        #         "authors": ["Brown", "Mann"],
        #     },
        # ]

        # batch_results = await resolver.papers2title_and_dois_async(papers)
        # print(f"   Resolved {len(batch_results)} papers")
        # for title, doi in batch_results.items():
        #     print(f"   - {title[:40]}... → {doi}")

        # 4. BibTeX file processing
        total, resolved, failed = await resolver.bibtex_file2dois_async(
            # "/home/ywatanabe/win/downloads/papers.bib"
            "/home/ywatanabe/win/downloads/hippocampus.bib"
        )
        print("\n4. BibTeX File Processing:")
        print("   # For BibTeX files, use:")
        print(
            "   # total, resolved, failed = await resolver.bibtex_file2dois_async('papers.bib')"
        )

        print("\n" + "=" * 50)
        print("✅ DOIResolver demo completed")
        print("=" * 50)

    asyncio.run(main())

# rm ~/.scitex/scholar/workspace/logs/* -f
# rm ~/.scitex/scholar/cache/doi_resolution/* -f
# rm ~/.scitex/scholar/library/{hippocampus,MASTER} -rf

# python -m scitex.scholar.metadata.doi.resolvers._DOIResolver

# EOF
