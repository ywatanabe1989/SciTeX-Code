#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 14:18:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/enrichers/_ImpactFactorEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/enrichment/enrichers/_ImpactFactorEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class ImpactFactorEnricher:
    def __init__(
        self, config: Optional[ScholarConfig] = None, cache_size: int = 1000
    ):
        self.config = config or ScholarConfig()
        self._factor_instance = None
        self._init_package()
        self._get_metrics = lru_cache(maxsize=cache_size)(
            self._get_metrics_uncached
        )

    def _init_package(self) -> None:
        """Initialize impact_factor package."""
        try:
            from impact_factor.core import Factor

            self._factor_instance = Factor()
            logger.info("Impact factor package initialized")
        except ImportError:
            logger.warning("impact_factor package not available")

    def enrich_metadata_json(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich JSON metadata with impact factors."""
        if not self._factor_instance:
            return metadata

        journal = metadata.get("journal")
        if not journal or metadata.get("impact_factor") is not None:
            return metadata

        metrics = self._get_metrics(journal)
        if metrics and "impact_factor" in metrics:
            metadata["impact_factor"] = metrics["impact_factor"]
            metadata["impact_factor_source"] = "JCR 2024"

            if "quartile" in metrics:
                metadata["journal_quartile"] = metrics["quartile"]
                metadata["quartile_source"] = "JCR 2024"

            if "enriched_at" not in metadata:
                metadata["enriched_at"] = datetime.now().isoformat()

            logger.info(
                f"Found impact factor {metrics['impact_factor']} for {journal}"
            )

        return metadata

    def _get_metrics_uncached(
        self, journal_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get journal metrics."""
        try:
            with suppress_db_logs():
                results = self._factor_instance.search(journal_name)
            if results:
                result = results[0]
                return {
                    "impact_factor": float(result.get("factor", None)),
                    "quartile": result.get("jcr", "Unknown"),
                }
        except Exception as exc:
            logger.debug(f"Impact factor lookup failed: {exc}")
        return None

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


@contextmanager
def suppress_db_logs():
    old_level = logging.getLogger("sqlalchemy.engine").level
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    try:
        yield
    finally:
        logging.getLogger("sqlalchemy.engine").setLevel(old_level)

# EOF
