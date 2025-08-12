#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 19:24:25 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/enrich_library.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/enrich_library.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_async():
    from pprint import pprint

    from scitex.scholar.metadata.enrichment import (
        LibraryEnricher,
        SmartEnricher,
    )

    # 1. Enrich single metadata file
    enricher = SmartEnricher()
    metadata = {
        "doi": "10.1038/nature12373",
        "title": None,
        "journal": None,
    }
    enriched = enricher.enrich_metadata_json(metadata)
    pprint(
        enriched
    )  # Now includes abstract, citation_count, keywords, impact_factor

    # 2. Enrich entire project library
    library_enricher = LibraryEnricher()
    results = await library_enricher.enrich_project_async("hippocampus")
    pprint(f"Enriched {results['enriched']} of {results['processed']} papers")


asyncio.run(main_async())

# EOF
