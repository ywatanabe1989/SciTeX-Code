#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 03:25:28 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/metadata_doi_resolution.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/metadata_doi_resolution.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_single_async():
    from scitex.scholar.metadata.doi.resolvers._SingleDOIResolver import (
        SingleDOIResolver,
    )

    single_resolver = SingleDOIResolver(project="MASTER", sources=["arxiv"])

    # Single DOI
    result = await single_resolver.resolve_async(
        title="Attention Is All You Need", skip_cache=True
    )
    print(result)
    # {'doi': '10.1007/978-3-031-84300-6_13',
    #  'source': 'crossref',
    #  'metadata': {'doi': '10.1007/978-3-031-84300-6_13',
    #   'title': 'Is Attention All You Need?',
    #   'journal': 'From Human Attention to Computational Attention',
    #   'journal_source': 'crossref',
    #   'short_journal': None,
    #   'publisher': 'Springer Nature Switzerland',
    #   'volume': None,
    #   'issue': None,
    #   'issn': None,
    #   'year': 2025,
    #   'abstract': None,
    #   'authors': ['Patrick Mineault']},
    #  'paper_id': '8716AA35'}


asyncio.run(main_single_async())

# Single DOI
result = await resolver.resolve_async("10.1038/nature1")
print(result)

# Multiple DOIs
results = await resolver.resolve_async(
    ["10.1038/nature1", "10.1126/science.abc"]
)
print(results)


# # BibTeX file
# results = await resolver.resolve_async("papers.bib")

# # BibTeX content string
# bibtex_content = """
# @article{smith2023,
#     title={Machine Learning},
#     author={Smith, J.},
#     year={2023}
# }
# """
# results = await resolver.resolve_async(bibtex_content)

# EOF
