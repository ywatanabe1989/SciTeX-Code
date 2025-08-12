#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 19:23:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/resolve_dois.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/resolve_dois.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import asyncio

from scitex.scholar.metadata import DOIResolver


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

# EOF
