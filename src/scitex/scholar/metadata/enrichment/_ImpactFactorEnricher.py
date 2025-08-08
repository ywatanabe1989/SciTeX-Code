#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 15:37:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/_ImpactFactorEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/enrichment/_ImpactFactorEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Impact factor enricher using impact_factor package."""

from functools import lru_cache
from typing import Dict, List, Optional

from scitex import logging

from ..._Paper import Paper
from ._BaseEnricher import BaseEnricher

logger = logging.getLogger(__name__)


class ImpactFactorEnricher(BaseEnricher):
    """Enriches papers with journal impact factors."""

    def __init__(self, cache_size: int = 1000):
        self._factor_instance = None
        self._init_package()
        self._get_metrics = lru_cache(maxsize=cache_size)(
            self._get_metrics_uncached
        )

    @property
    def name(self) -> str:
        return "ImpactFactorEnricher"

    def _init_package(self) -> None:
        """Initialize impact_factor package."""
        try:
            from impact_factor.core import Factor

            self._factor_instance = Factor()
            logger.info("Impact factor package initialized")
        except ImportError:
            logger.warning("impact_factor package not available")

    def can_enrich(self, paper: Paper) -> bool:
        """Check if paper can be enriched."""
        return bool(paper.journal and paper.impact_factor is None)

    # def enrich(self, papers: List[Paper]) -> None:
    #     """Add impact factors to papers."""
    #     if not self._factor_instance:
    #         return

    #     count = 0
    #     for paper in papers:
    #         if not self.can_enrich(paper):
    #             continue

    #         metrics = self._get_metrics(paper.journal)
    #         if metrics and "impact_factor" in metrics:
    #             paper.impact_factor = metrics["impact_factor"]
    #             paper.impact_factor_source = "JCR 2024"
    #             paper.metadata["impact_factor_source"] = "JCR 2024"

    #             if "quartile" in metrics:
    #                 paper.journal_quartile = metrics["quartile"]
    #                 paper.quartile_source = "JCR 2024"

    #             count += 1

    #     if count:
    #         logger.info(f"Enriched {count} papers with impact factors")

    def enrich(self, papers: List[Paper]) -> None:
        """Add impact factors to papers."""
        if not self._factor_instance:
            return

        count = 0
        for paper in papers:
            if not self.can_enrich(paper):
                continue

            metrics = self._get_metrics(paper.journal)
            if metrics and "impact_factor" in metrics:
                paper.update_field_with_source(
                    "impact_factor", metrics["impact_factor"], "JCR 2024"
                )

                if "quartile" in metrics:
                    paper.update_field_with_source(
                        "journal_quartile", metrics["quartile"], "JCR 2024"
                    )
                count += 1

        if count:
            logger.info(f"Enriched {count} papers with impact factors")

    def _get_metrics_uncached(
        self, journal_name: str
    ) -> Optional[Dict[str, float]]:
        """Get journal metrics."""
        try:
            results = self._factor_instance.search(journal_name)
            if results:
                # Simple match - take first result
                result = results[0]
                return {
                    "impact_factor": float(result.get("factor", 0)),
                    "quartile": result.get("jcr", "Unknown"),
                }
        except Exception as exc:
            logger.debug(f"Impact factor lookup failed: {exc}")

        return None

# EOF
