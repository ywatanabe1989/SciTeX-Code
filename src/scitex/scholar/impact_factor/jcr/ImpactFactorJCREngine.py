#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-12 07:23:17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/impact_factor/jcr/ImpactFactorJCREngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/impact_factor/jcr/ImpactFactorJCREngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Query JCR database for journal impact factors
  - Fast SQLite-based lookup
  - Returns impact factor, quartile, ISSN information
  - Handles missing data gracefully

Dependencies:
  - packages:
    - sqlalchemy
    - sql_manager

IO:
  - input-files:
    - ../../data/impact_factor/impact_factor.db (SQLite database)
  - output-files:
    - None (read-only queries)
"""

"""Imports"""
import argparse
import functools
from pathlib import Path
from typing import Dict, List, Optional

from sql_manager import DynamicModel, Manager
from sqlalchemy import Column, Float, String, func

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Parameters"""
DEFAULT_DB = (
    Path(".") / "data" / "scholar" / "impact_factor" / "JCR_IF_2024.db"
)

"""Functions & Classes"""
# Database model
columns = {
    "nlm_id": Column(String, comment="the unique ID of NLM", default="."),
    "factor": Column(Float(3), comment="the IF of journal"),
    "jcr": Column(String, comment="the partition of JCR", default="."),
    "journal": Column(
        String, comment="the title of journal", primary_key=True
    ),
    "journal_abbr": Column(
        String, comment="the abbreviation of journal", default="."
    ),
    "issn": Column(String, comment="the ISSN of journal", default="."),
    "eissn": Column(String, comment="the eISSN of journal", default="."),
}

FactorData = DynamicModel("Factor", columns, "factor")
FactorManager = functools.partial(Manager, FactorData)


# Utility functions
def record_to_dict(record) -> Dict:
    """Convert SQLAlchemy record to dictionary."""
    return {
        "journal": record.journal,
        "journal_abbr": record.journal_abbr,
        "issn": record.issn,
        "eissn": record.eissn,
        "factor": record.factor,
        "jcr": record.jcr,
        "nlm_id": record.nlm_id,
    }


class ImpactFactorJCREngine:
    """
    JCR database engine for impact factor lookup.

    Fast SQLite-based queries for journal metrics.
    """

    def __init__(self, dbfile=None):
        """
        Initialize JCR engine.

        Args:
            dbfile: Path to SQLite database (uses DEFAULT_DB if None)
        """
        self.dbfile = dbfile or DEFAULT_DB
        # Disable SQL echo to reduce log verbosity
        self.manager = FactorManager(self.dbfile, echo=False)
        self.query = self.manager.session.query(FactorData)

    def search(self, value: str, key: Optional[str] = None) -> List[Dict]:
        """
        Search for journal in database.

        Args:
            value: Search value (journal name, ISSN, etc.)
            key: Specific field to search (None for all fields)

        Returns:
            List of matching journal records as dictionaries
        """
        from scitex.contextmanager import suppress_output

        default_keys = ["issn", "eissn", "nlm_id", "journal", "journal_abbr"]
        keys = [key] if key else default_keys

        # Suppress SQLAlchemy echo output during queries
        with suppress_output():
            for field in keys:
                if "%" in value:
                    result = self.query.filter(
                        FactorData.__dict__[field].like(value)
                    )
                else:
                    result = self.query.filter(
                        func.lower(FactorData.__dict__[field]) == func.lower(value)
                    )

                if result.count():
                    data = [record_to_dict(record) for record in result]
                    return data

        return []

    def filter(self, min_value=None, max_value=None, limit=None):
        """
        Filter journals by impact factor range.

        Args:
            min_value: Minimum impact factor
            max_value: Maximum impact factor
            limit: Maximum number of results

        Returns:
            List of matching journal records
        """
        from scitex.contextmanager import suppress_output

        # Suppress SQLAlchemy echo output during queries
        with suppress_output():
            query = self.query

            if min_value is not None:
                query = query.filter(FactorData.factor >= min_value)

            if max_value is not None:
                query = query.filter(FactorData.factor <= max_value)

            if limit and query.count() > limit:
                query = query.limit(limit)

            return [record_to_dict(record) for record in query]


def main(args):
    """Main function for CLI usage."""
    engine = ImpactFactorJCREngine(args.database)

    if args.search:
        results = engine.search(args.search, args.key)
        if results:
            logger.info(f"Found {len(results)} result(s):")
            for result in results:
                logger.info(f"  Journal: {result['journal']}")
                logger.info(f"  Factor: {result['factor']}")
                logger.info(f"  JCR: {result['jcr']}")
                logger.info(f"  ISSN: {result['issn']}")
                logger.info(f"  eISSN: {result['eissn']}")
                logger.info("")
        else:
            logger.warning(f"No results found for: {args.search}")
        return 0

    if args.filter:
        results = engine.filter(
            min_value=args.min_factor,
            max_value=args.max_factor,
            limit=args.limit,
        )
        logger.info(f"Found {len(results)} journal(s)")
        for result in results[:10]:  # Show first 10
            logger.info(f"  {result['journal']}: {result['factor']}")
        if len(results) > 10:
            logger.info(f"  ... and {len(results) - 10} more")
        return 0

    logger.error("No action specified. Use --search or --filter")
    return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Query JCR database for journal impact factors"
    )
    parser.add_argument(
        "--database",
        "-d",
        type=str,
        default=None,
        help=f"Path to JCR database (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--search",
        "-s",
        type=str,
        default=None,
        help="Search for journal by name, ISSN, or other fields",
    )
    parser.add_argument(
        "--key",
        "-k",
        type=str,
        default=None,
        choices=["issn", "eissn", "nlm_id", "journal", "journal_abbr"],
        help="Specific field to search (default: all fields)",
    )
    parser.add_argument(
        "--filter",
        "-f",
        action="store_true",
        default=False,
        help="Filter journals by impact factor range",
    )
    parser.add_argument(
        "--min-factor",
        type=float,
        default=None,
        help="Minimum impact factor for filtering",
    )
    parser.add_argument(
        "--max-factor",
        type=float,
        default=None,
        help="Maximum impact factor for filtering",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Maximum number of results",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()


"""
Examples:

# Search for a specific journal
python -m scitex.scholar.impact_factor.jcr.ImpactFactorJCREngine \
    --search "Nature"

# Search by ISSN
python -m scitex.scholar.impact_factor.jcr.ImpactFactorJCREngine \
    --search "0028-0836" --key issn

# Filter journals by impact factor range
python -m scitex.scholar.impact_factor.jcr.ImpactFactorJCREngine \
    --filter --min-factor 10.0 --max-factor 50.0 --limit 20
"""

# EOF
