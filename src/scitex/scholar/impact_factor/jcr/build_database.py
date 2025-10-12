#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-12 07:17:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/impact_factor/jcr/build_database.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/impact_factor/jcr/build_database.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Build SQLite database from JCR Excel files
  - Parse JCR Excel exports
  - Create indexed database for fast queries
  - Extract impact factors and quartiles

Dependencies:
  - packages:
    - openpyxl
    - sqlalchemy
    - sql_manager

IO:
  - input-files:
    - ../../data/impact_factor/JCR_IF_YYYY.xlsx
  - output-files:
    - ../../data/impact_factor/JCR_IF_YYYY.db
"""

"""Imports"""
import argparse
import re
from pathlib import Path
from typing import Dict, Iterator, Optional

import openpyxl

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Parameters"""
# Data paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # scholar/
DATA_DIR = BASE_DIR / "data" / "impact_factor"

"""Functions & Classes"""
def parse_jcr_excel(excel_path: Path) -> Iterator[Dict]:
    """
    Parse JCR Excel file and yield journal records.

    Args:
        excel_path: Path to JCR Excel file

    Yields:
        Dictionary with journal data (journal, factor, issn, etc.)
    """
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    for values in ws.values:
        if values[0] is None:
            continue
        if values[0] in ("Journal Name", "Name"):
            title = [v.upper() for v in values]
            continue

        context = dict(zip(title, values))
        data = {}
        raw_factor = context.get("2021 JIF") or context.get("JIF")
        data["factor"] = _parse_impact_factor(raw_factor)
        data["issn"] = context["ISSN"] if context["ISSN"] != "N/A" else ""
        data["eissn"] = context["EISSN"] if context["EISSN"] != "N/A" else ""
        data["jcr"] = _get_jcr_quartile(context["CATEGORY"])
        data["journal"] = context.get("JOURNAL NAME") or context.get("NAME")

        yield data


def _get_jcr_quartile(category: str) -> str:
    """Extract JCR quartile from category string."""
    res = re.findall(r"[|(](Q\d)[)|]", category)
    return res[0] if res else ""


def _parse_impact_factor(factor_str) -> Optional[float]:
    """
    Parse impact factor string to float.

    Handles special cases like '<0.1', '>100', 'N/A', None, etc.

    Args:
        factor_str: Impact factor value from Excel (can be str, float, or None)

    Returns:
        Float value or None if cannot be parsed
    """
    if factor_str is None or factor_str == "N/A":
        return None

    # Already a float
    if isinstance(factor_str, (int, float)):
        return float(factor_str)

    # Convert to string and clean
    factor_str = str(factor_str).strip()

    if not factor_str or factor_str == "N/A":
        return None

    # Handle '<0.1' -> 0.1
    if factor_str.startswith("<"):
        try:
            return float(factor_str[1:])
        except ValueError:
            logger.warning(f"Could not parse factor value: {factor_str}")
            return None

    # Handle '>100' -> 100
    if factor_str.startswith(">"):
        try:
            return float(factor_str[1:])
        except ValueError:
            logger.warning(f"Could not parse factor value: {factor_str}")
            return None

    # Try direct conversion
    try:
        return float(factor_str)
    except ValueError:
        logger.warning(f"Could not parse factor value: {factor_str}")
        return None


def build_database(excel_path: Path, output_db: Optional[Path] = None) -> Path:
    """
    Build SQLite database from JCR Excel file.

    Args:
        excel_path: Path to JCR Excel file
        output_db: Output database path (auto-generated if None)

    Returns:
        Path to created database
    """
    from .ImpactFactorJCREngine import FactorData, FactorManager

    # Auto-generate output path
    if output_db is None:
        year = re.search(r"20\d{2}", excel_path.name)
        year_str = year.group() if year else "2024"
        output_db = DATA_DIR / f"JCR_IF_{year_str}.db"

    logger.info(f"Building database from {excel_path}")
    logger.info(f"Output: {output_db}")

    # Create database
    manager = FactorManager(str(output_db))

    # Parse and insert data
    count = 0
    for record in parse_jcr_excel(excel_path):
        # Insert or update record
        manager.session.merge(FactorData(**record))
        count += 1

        if count % 100 == 0:
            logger.info(f"Processed {count} journals...")

    manager.session.commit()
    logger.success(f"Database built: {count} journals")
    logger.success(f"Saved to: {output_db}")

    return output_db


def main(args):
    """Main function to build JCR database from Excel file."""
    excel_path = Path(args.excel)

    if not excel_path.exists():
        logger.error(f"Excel file not found: {excel_path}")
        return 1

    output_db = Path(args.output) if args.output else None

    try:
        result_db = build_database(excel_path, output_db)
        logger.success(f"Database successfully built: {result_db}")
        return 0
    except Exception as e:
        logger.error(f"Failed to build database: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build SQLite database from JCR Excel files"
    )
    parser.add_argument(
        "--excel",
        "-e",
        type=str,
        required=True,
        help="Path to JCR Excel file (e.g., JCR_IF_2021.xlsx)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output database path (auto-generated if not specified)",
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
python -m scitex.scholar.impact_factor.jcr.build_database \
    -e ./data/scholar/impact_factor/JCR_IF_2024.xlsx \
    -o ./data/scholar/impact_factor/JCR_IF_2024.db
"""

# EOF
