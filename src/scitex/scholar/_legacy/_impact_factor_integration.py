#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 09:42:07 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_impact_factor_integration.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_impact_factor_integration.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-07-02 01:40:00"
# Author: Claude
# Filename: _impact_factor_integration.py

"""
Integration with impact_factor package for real journal impact factors.
https://github.com/suqingdong/impact_factor
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ### This is the correct usage
# from impact_factor.core import Factor

# fa = Factor()

# print(fa.dbfile)

# fa.search('nature')
# fa.search('nature c%')

# fa.filter(min_value=100, max_value=200)
# fa.filter(min_value=100, max_value=200, pubmed_filter=True)

# Try to import impact_factor package
try:
    from impact_factor import ImpactFactor

    IMPACT_FACTOR_AVAILABLE = True
except ImportError:
    IMPACT_FACTOR_AVAILABLE = False
    logger.warning(
        "impact_factor package not available. Install with: pip install impact-factor"
    )


class ImpactFactorService:
    """Service for retrieving real impact factors using impact_factor package."""

    def __init__(
        self, year: Optional[int] = None, cache_dir: Optional[Path] = None
    ):
        """
        Initialize impact factor service.

        Args:
            year: Year for impact factor data (default: latest available)
            cache_dir: Directory to cache impact factor database
        """
        self.year = year
        self.cache_dir = cache_dir
        self._if_instance = None

        if IMPACT_FACTOR_AVAILABLE:
            try:
                # Initialize the impact factor instance
                self._if_instance = ImpactFactor()
                logger.info("Impact factor service initialized successfully")
            except Exception as e:
                logger.error(
                    f"Failed to initialize impact factor service: {e}"
                )

    def is_available(self) -> bool:
        """Check if impact factor service is available."""
        return IMPACT_FACTOR_AVAILABLE and self._if_instance is not None

    def get_journal_metrics(self, journal_name: str) -> Dict[str, Any]:
        """
        Get journal metrics including impact factor.

        Args:
            journal_name: Name of the journal

        Returns:
            Dictionary with impact factor and other metrics
        """
        if not self.is_available():
            logger.debug("Impact factor service not available")
            return {}

        try:
            # Search for journal
            results = self._if_instance.search(journal_name)

            if not results:
                logger.debug(
                    f"No impact factor found for journal: {journal_name}"
                )
                return {}

            # Get the best match (usually first result)
            best_match = results[0]

            # Extract metrics
            metrics = {
                "impact_factor": float(best_match.get("factor", 0)),
                "journal_name": best_match.get("journal", journal_name),
                "issn": best_match.get("issn", ""),
                "year": best_match.get("year", self.year),
                "categories": best_match.get("categories", []),
                "rank": best_match.get("rank", None),
                "quartile": self._determine_quartile(best_match),
                "source": "impact_factor_package",
            }

            logger.info(
                f"Found IF={metrics['impact_factor']} for {journal_name}"
            )
            return metrics

        except Exception as e:
            logger.error(
                f"Error retrieving impact factor for {journal_name}: {e}"
            )
            return {}

    def _determine_quartile(self, journal_data: Dict) -> str:
        """Determine journal quartile from ranking data."""
        # The impact_factor package may provide quartile info
        quartile = journal_data.get("quartile")
        if quartile:
            return f"Q{quartile}"

        # Otherwise estimate from rank if available
        rank = journal_data.get("rank")
        total = journal_data.get("total_journals")

        if rank and total:
            percentile = (rank / total) * 100
            if percentile <= 25:
                return "Q1"
            elif percentile <= 50:
                return "Q2"
            elif percentile <= 75:
                return "Q3"
            else:
                return "Q4"

        return "Unknown"

    def batch_get_metrics(
        self, journal_names: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for multiple journals.

        Args:
            journal_names: List of journal names

        Returns:
            Dictionary mapping journal names to their metrics
        """
        results = {}

        for journal in journal_names:
            metrics = self.get_journal_metrics(journal)
            if metrics:
                results[journal] = metrics

        return results

    def update_database(self) -> bool:
        """
        Update the impact factor database to latest version.

        Returns:
            True if update successful
        """
        if not self.is_available():
            return False

        try:
            # The impact_factor package should have an update method
            # This depends on the package implementation
            logger.info("Updating impact factor database...")
            # self._if_instance.update()  # If available
            return True
        except Exception as e:
            logger.error(f"Failed to update impact factor database: {e}")
            return False


class EnhancedJournalMetrics:
    """
    Enhanced journal metrics that combines built-in data with impact_factor package.
    """

    def __init__(
        self,
        custom_db_path: Optional[str] = None,
        use_impact_factor_package: bool = True,
    ):
        """
        Initialize enhanced journal metrics.

        Args:
            custom_db_path: Path to custom journal database
            use_impact_factor_package: Whether to use impact_factor package
        """
        # Import the original JournalMetrics
        from ._journal_metrics import JournalMetrics

        # Initialize base metrics service
        self.base_metrics = JournalMetrics(custom_db_path=custom_db_path)

        # Initialize impact factor service if requested
        self.if_service = None
        if use_impact_factor_package:
            self.if_service = ImpactFactorService()

    def lookup_journal_metrics(self, journal_name: str) -> Dict[str, Any]:
        """
        Look up journal metrics, trying multiple sources.

        Args:
            journal_name: Journal name

        Returns:
            Combined metrics from all available sources
        """
        # First try base metrics (built-in database)
        metrics = self.base_metrics.lookup_journal_metrics(journal_name)

        # Then try impact_factor package if available
        if self.if_service and self.if_service.is_available():
            if_metrics = self.if_service.get_journal_metrics(journal_name)

            # Merge metrics, preferring real data from impact_factor package
            if if_metrics:
                # Update with real impact factor
                if (
                    "impact_factor" in if_metrics
                    and if_metrics["impact_factor"] > 0
                ):
                    metrics["impact_factor"] = if_metrics["impact_factor"]
                    metrics["impact_factor_year"] = if_metrics.get(
                        "year", 2024
                    )
                    metrics["source"] = "impact_factor_package"

                # Update other fields if available
                for field in ["issn", "quartile", "categories"]:
                    if field in if_metrics and if_metrics[field]:
                        metrics[field] = if_metrics[field]

        return metrics


# Installation helper
def install_impact_factor_package():
    """Helper to install the impact_factor package."""
    import subprocess
    import sys

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "impact_factor"]
        )
        print("Successfully installed impact_factor package")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install impact_factor package")
        print("Please install manually: pip install impact_factor")
        return False


# Example usage
def example_usage():
    """Example of using the impact factor integration."""

    # Check if package is available
    if not IMPACT_FACTOR_AVAILABLE:
        print("impact_factor package not installed.")
        print("Install with: pip install impact_factor")
        return

    # Initialize service
    if_service = ImpactFactorService()

    # Test journals
    test_journals = [
        "Nature",
        "Science",
        "Nature Neuroscience",
        "Trends in Cognitive Sciences",
        "Journal of Neuroscience",
    ]

    print("Impact Factor Lookup Results:")
    print("-" * 60)

    for journal in test_journals:
        metrics = if_service.get_journal_metrics(journal)
        if metrics:
            print(f"\nJournal: {journal}")
            print(f"  Impact Factor: {metrics.get('impact_factor', 'N/A')}")
            print(f"  Quartile: {metrics.get('quartile', 'N/A')}")
            print(f"  ISSN: {metrics.get('issn', 'N/A')}")
        else:
            print(f"\nJournal: {journal} - No data found")

    # Test enhanced metrics
    print("\n\nEnhanced Metrics (combining sources):")
    print("-" * 60)

    enhanced = EnhancedJournalMetrics()
    metrics = enhanced.lookup_journal_metrics("Nature")
    print(f"Nature metrics: {metrics}")


if __name__ == "__main__":
    example_usage()

# EOF
