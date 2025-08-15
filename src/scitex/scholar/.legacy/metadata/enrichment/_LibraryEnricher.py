#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 19:24:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/_LibraryEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/enrichment/_LibraryEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
from typing import Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

from .enrichers._SmartEnricher import SmartEnricher

logger = logging.getLogger(__name__)


class LibraryEnricher:
    def __init__(self, config: Optional[ScholarConfig] = None):
        self.config = config or ScholarConfig()
        self.smart_enricher = SmartEnricher(config=self.config)

    async def enrich_project_async(self, project: str) -> Dict[str, int]:
        """Enrich all papers in a project library."""
        library_dir = self.config.path_manager.library_dir / project
        master_dir = library_dir.parent / "MASTER"
        results = {"processed": 0, "enriched": 0, "errors": 0}

        for paper_dir in master_dir.iterdir():
            if not paper_dir.is_dir():
                continue

            metadata_path = paper_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                original_metadata = metadata.copy()

                # Apply smart enricher
                metadata = self.smart_enricher.enrich_metadata_json(metadata)

                # Save if changed
                if metadata != original_metadata:
                    with open(metadata_path, "w") as f:
                        json.dump(metadata, f, indent=2)
                    results["enriched"] += 1
                    logger.success(f"Enriched {paper_dir.name}")

                results["processed"] += 1
            except Exception as e:
                logger.error(f"Error enriching {metadata_path}: {e}")
                results["errors"] += 1

        return results


if __name__ == "__main__":
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
        pprint(
            f"Enriched {results['enriched']} of {results['processed']} papers"
        )

    asyncio.run(main_async())

# python -m scitex.scholar.metadata.enrichment._LibraryEnricher

# EOF
