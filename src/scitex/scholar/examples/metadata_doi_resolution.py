#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-10 11:57:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/metadata_doi_resolution.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/metadata_doi_resolution.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from pprint import pprint


async def main_single_async():
    from scitex.scholar.metadata.doi.resolvers._SingleDOIResolver import (
        SingleDOIResolver,
    )

    single_resolver = SingleDOIResolver()
    # Single DOI
    result = await single_resolver.metadata2doi_async(
        title="Attention Is All You Need", skip_cache=True
    )
    pprint(result)

    # {'doi': '10.1007/978-3-031-84300-6_13',
    #  'metadata': {'abstract': None,
    #               'authors': ['Patrick Mineault'],
    #               'doi': '10.1007/978-3-031-84300-6_13',
    #               'issn': None,
    #               'issue': None,
    #               'journal': 'From Human Attention to Computational Attention',
    #               'journal_source': 'crossref',
    #               'publisher': 'Springer Nature Switzerland',
    #               'short_journal': None,
    #               'title': 'Is Attention All You Need?',
    #               'volume': None,
    #               'year': 2025},
    #  'source': 'crossref'}


asyncio.run(main_single_async())

# # Multiple DOIs
# results = await resolver.resolve_async(
#     ["10.1038/nature1", "10.1126/science.abc"]
# )
# print(results)


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
