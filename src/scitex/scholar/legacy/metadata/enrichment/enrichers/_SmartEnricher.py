#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 14:22:25 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/enrichers/_SmartEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/enrichment/enrichers/_SmartEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from datetime import datetime

import json
from pathlib import Path
from typing import Any
from typing import Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ..sources._UnifiedMetadataSource import UnifiedMetadataSource
from ._ImpactFactorEnricher import ImpactFactorEnricher

logger = logging.getLogger(__name__)


class SmartEnricher:
    """Smart enricher that checks JSON contents before making API calls."""

    def __init__(self, config: Optional[ScholarConfig] = None):
        self.config = config or ScholarConfig()
        self.unified_source = UnifiedMetadataSource(config)
        self.impact_enricher = ImpactFactorEnricher(config)

    # def enrich_metadata_json(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
    #     """Enrich metadata only for missing fields."""
    #     doi = metadata.get("doi")
    #     if not doi:
    #         return metadata

    #     # Check what's missing before making any API calls
    #     missing_fields = self._check_missing_fields(metadata)
    #     if not missing_fields:
    #         logger.debug(
    #             "All metadata fields already present, skipping API calls"
    #         )
    #         return metadata

    #     logger.debug(f"Missing fields for enrichment: {missing_fields}")

    #     # Only fetch if we need API-based fields
    #     api_fields = ["abstract", "citation_count", "keywords"]
    #     needs_api = any(field in missing_fields for field in api_fields)

    #     if needs_api:
    #         comprehensive_data = (
    #             self.unified_source.get_comprehensive_metadata(doi)
    #         )
    #         if comprehensive_data:
    #             # Only update missing fields
    #             for field in missing_fields:
    #                 if field in comprehensive_data:
    #                     metadata[field] = comprehensive_data[field]
    #                     source_field = f"{field}_source"
    #                     if source_field in comprehensive_data:
    #                         metadata[source_field] = comprehensive_data[
    #                             source_field
    #                         ]

    #     # Add impact factor only if journal is present and impact_factor is missing
    #     if "impact_factor" in missing_fields and metadata.get("journal"):
    #         metadata = self.impact_enricher.enrich_metadata_json(metadata)

    #     # Set enrichment timestamp only if we actually enriched something
    #     # if any(
    #     #     field not in missing_fields or field in metadata
    #     #     for field in missing_fields
    #     # ):
    #     #     if "enriched_at" not in metadata:
    #     #         metadata["enriched_at"] = datetime.now().isoformat()
    #     if any(field in metadata for field in missing_fields):
    #         if "enriched_at" not in metadata:
    #             metadata["enriched_at"] = datetime.now().isoformat()

    #     return metadata

    def enrich_metadata_json(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich metadata only for missing fields."""
        doi = metadata.get("doi")
        if not doi:
            return metadata

        missing_fields = self._check_missing_fields(metadata)
        if not missing_fields:
            return metadata

        logger.info(f"Enriching DOI {doi} - missing: {missing_fields}")

        api_fields = ["abstract", "citation_count", "keywords"]
        needs_api = any(field in missing_fields for field in api_fields)

        if needs_api:
            comprehensive_data = (
                self.unified_source.get_comprehensive_metadata(doi)
            )
            if comprehensive_data:
                logger.info(
                    f"Got comprehensive data with keys: {list(comprehensive_data.keys())}"
                )

                # Only update missing fields with non-null values
                for field in missing_fields:
                    if (
                        field in comprehensive_data
                        and comprehensive_data[field]
                    ):
                        metadata[field] = comprehensive_data[field]
                        logger.debug(
                            f"Updated {field}: {comprehensive_data[field]}"
                        )

        # Add impact factor only if journal is present and impact_factor is missing
        if "impact_factor" in missing_fields and metadata.get("journal"):
            metadata = self.impact_enricher.enrich_metadata_json(metadata)

        if any(field in metadata for field in missing_fields):
            if "enriched_at" not in metadata:
                metadata["enriched_at"] = datetime.now().isoformat()

        return metadata

        # Continue with impact factor enrichment...

    def _check_missing_fields(self, metadata: Dict[str, Any]) -> List[str]:
        """Check which metadata fields are missing or empty."""
        required_fields = [
            "title",
            "journal",
            "abstract",
            "citation_count",
            "keywords",
            "impact_factor",
            "journal_quartile",
            "issn",
            "volume",
            "issue",
            "publisher",
        ]
        missing = []
        for field in required_fields:
            value = metadata.get(field)
            if value is None or (isinstance(value, (str, list)) and not value):
                missing.append(field)
        return missing

    def enrich_metadata_file(self, json_path: Path) -> bool:
        """Enrich a single metadata.json file in place."""
        with open(json_path) as f:
            metadata = json.load(f)

        enriched = self.enrich_metadata_json(metadata)

        if enriched != metadata:
            with open(json_path, "w") as f:
                json.dump(enriched, f, indent=2)
            return True
        return False

# EOF
