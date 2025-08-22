#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 16:49:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/extra/JournalMetrics.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/extra/JournalMetrics.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Retrieves journal impact factors and quartiles
- Provides standalone journal metrics lookup
- Caches results for performance optimization

Dependencies:
- packages:
  - impact_factor

Input:
- Journal names as strings

Output:
- Dictionary containing impact factor and quartile data
"""

"""Imports"""
from functools import lru_cache
from typing import Dict, Optional

from impact_factor.core import Factor

"""Parameters"""

"""Functions & Classes"""
class JournalMetrics:
    """Standalone journal metrics retrieval using impact_factor package."""

    def __init__(self, cache_size: int = 1000):
        """Initialize with optional cache size."""
        self.factor_instance = Factor()
        self.get_metrics = lru_cache(maxsize=cache_size)(
            self._get_metrics_uncached
        )

    def _get_jcr_year(self) -> str:
        """Extract JCR year from database or package metadata."""
        try:
            import sqlite3

            with sqlite3.connect(self.factor_instance.dbfile) as conn:
                cursor = conn.cursor()

                # Check if there's a metadata table with year info
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in cursor.fetchall()]

                if "metadata" in tables:
                    cursor.execute(
                        "SELECT value FROM metadata WHERE key='year' OR key='jcr_year'"
                    )
                    year_result = cursor.fetchone()
                    if year_result:
                        return f"JCR {year_result[0]}"

                # Try to extract year from package version or other sources
                try:
                    import impact_factor

                    if hasattr(impact_factor, "__version__"):
                        version = impact_factor.__version__
                        # Extract year from version if present
                        import re

                        year_match = re.search(r"20\d{2}", version)
                        if year_match:
                            return f"JCR {year_match.group()}"
                except:
                    pass

        except Exception:
            pass

        return "Source Unknown"

    def _get_metrics_uncached(self, journal_name: str) -> Optional[Dict]:
        """Get journal metrics without caching."""
        if not self.factor_instance or not journal_name:
            return None

        try:
            results = self.factor_instance.search(journal_name)
            if results:
                result = results[0]
                return {
                    "impact_factor": float(result.get("factor", 0)),
                    "quartile": result.get("jcr", "Unknown"),
                    "source": self._get_jcr_year(),
                }
        except Exception:
            pass

        return None

    def get_database_info(self) -> Dict:
        """Get information about the impact factor database."""
        if not self.factor_instance:
            return {"error": "Database not available"}

        import sqlite3

        db_path = self.factor_instance.dbfile

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            info = {
                "database_path": str(db_path),
                "tables": tables,
                "total_journals": 0,
                "data_year": self._get_jcr_year(),
            }

            if tables:
                main_table = tables[0]
                cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                info["total_journals"] = cursor.fetchone()[0]

                cursor.execute(f"PRAGMA table_info({main_table})")
                columns = [row[1] for row in cursor.fetchall()]
                info["columns"] = columns

                cursor.execute(f"SELECT * FROM {main_table} LIMIT 3")
                sample_data = cursor.fetchall()
                info["sample_data"] = sample_data

            return info


def get_journal_metrics(journal_name: str) -> Optional[Dict]:
    """Standalone function to get journal metrics.

    Parameters
    ----------
    journal_name : str
        Name of the journal

    Returns
    -------
    Optional[Dict]
        Dictionary with impact_factor, quartile, and source keys

    Example
    -------
    >>> metrics = get_journal_metrics("Nature")
    >>> print(metrics["impact_factor"])
    64.8
    """
    metrics_instance = JournalMetrics()
    return metrics_instance.get_metrics(journal_name)


if __name__ == "__main__":

    def main():
        """Demonstrate journal metrics lookup."""
        metrics_instance = JournalMetrics()

        # Show database info
        print("Database Information")
        print("=" * 50)
        db_info = metrics_instance.get_database_info()
        for key, value in db_info.items():
            print(f"{key}: {value}")

        print("\nJournal Metrics Lookup Demo")
        print("=" * 50)

        test_journals = ["Nature", "Science", "Cell"]

        for journal in test_journals:
            print(f"\nJournal: {journal}")
            metrics = get_journal_metrics(journal)
            if metrics:
                for key, value in metrics.items():
                    print(f"  {key}: {value}")
            else:
                print("  No metrics found")

    main()
# python -m scitex.scholar.extra.JournalMetrics

# EOF
