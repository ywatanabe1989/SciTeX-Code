#!/usr/bin/env python3
"""JCR Impact Factor Engine using local SQLite database."""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from scitex import logging

logger = logging.getLogger(__name__)

class JCRImpactFactorEngine:
    """Fast impact factor lookups using JCR database."""

    def __init__(self):
        """Initialize with JCR database path."""
        self.name = "JCR Impact Factor"

        # Path to the JCR database
        self.db_path = Path(__file__).parent.parent / "externals" / "impact_factor_jcr" / "impact_factor" / "data" / "impact_factor.sqlite3"

        if not self.db_path.exists():
            logger.warning(f"JCR database not found at {self.db_path}")
            self.db_path = None

    def get_impact_factor(self, journal_name: str) -> Optional[float]:
        """Get impact factor for a journal.

        Args:
            journal_name: Journal name to search for

        Returns:
            Impact factor if found, None otherwise
        """
        if not self.db_path:
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Try exact match first (case-insensitive)
                cursor.execute(
                    "SELECT factor FROM factor WHERE LOWER(journal) = LOWER(?) LIMIT 1",
                    (journal_name,)
                )
                result = cursor.fetchone()

                if result:
                    return float(result[0]) if result[0] else None

                # Try partial match
                cursor.execute(
                    "SELECT journal, factor FROM factor WHERE LOWER(journal) LIKE LOWER(?) ORDER BY LENGTH(journal) LIMIT 1",
                    (f"%{journal_name}%",)
                )
                result = cursor.fetchone()

                if result:
                    logger.info(f"Found impact factor for '{result[0]}' (searched: '{journal_name}')")
                    return float(result[1]) if result[1] else None

        except Exception as e:
            logger.warning(f"Error querying JCR database: {e}")

        return None

    def enrich_papers(self, papers: "Papers") -> "Papers":
        """Add impact factors to papers.

        Args:
            papers: Papers collection to enrich

        Returns:
            Papers with impact factors added
        """
        from scitex.scholar.core import Papers

        if not self.db_path:
            logger.warning("JCR database not available")
            return papers

        enriched_count = 0
        journal_cache = {}  # Cache to avoid repeated lookups

        for paper in papers:
            if paper.journal and not paper.journal_impact_factor:
                # Use cache if available
                if paper.journal in journal_cache:
                    if journal_cache[paper.journal]:
                        paper.journal_impact_factor = journal_cache[paper.journal]
                        enriched_count += 1
                else:
                    # Look up and cache
                    if_value = self.get_impact_factor(paper.journal)
                    journal_cache[paper.journal] = if_value
                    if if_value:
                        paper.journal_impact_factor = if_value
                        enriched_count += 1

        if enriched_count > 0:
            logger.success(f"Added impact factors to {enriched_count} papers using JCR database")
        else:
            logger.info("No impact factors added (already present or not found)")

        return papers