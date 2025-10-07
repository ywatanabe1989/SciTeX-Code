#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 22:04:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/generate_download_summary.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/generate_download_summary.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Generate summary table for PDF download overview."""

import sys
from pathlib import Path
from typing import Optional

import pandas as pd

import scitex as stx
from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


def generate_download_summary(
    project: str, output_path: Optional[Path] = None
) -> Path:
    """
    Generate CSV summary table of PDF download status.

    Args:
        project: Project name
        output_path: Output CSV path (default: library/project/download_summary.csv)

    Returns:
        Path to generated CSV file
    """
    config = ScholarConfig()
    master_dir = config.path_manager.get_library_master_dir()
    project_dir = config.path_manager.get_library_dir(project)

    logger.debug(f"Master dir: {master_dir}")
    logger.debug(f"Project dir: {project_dir}")

    if not master_dir.exists():
        logger.error(f"Master library directory does not exist: {master_dir}")
        return None

    # Default output path in project directory
    if output_path is None:
        output_path = project_dir / "summary.csv"

    # logger.info(f"Output path: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # logger.info(f"Scanning library: {project}")
    # logger.info(f"Master directory: {master_dir}")

    # Collect all paper directories
    paper_dirs = [
        d for d in master_dir.iterdir() if d.is_dir() and len(d.name) == 8
    ]

    # logger.info(f"Found {len(paper_dirs)} paper directories")

    dfs = []
    for paper_dir in sorted(paper_dirs):
        paper_id = paper_dir.name
        metadata_file = paper_dir / "metadata.json"

        dict_ = stx.io.load(metadata_file)
        dict_ = stx.dict.flatten(dict_)
        df = pd.DataFrame(pd.Series(dict_))

        dfs.append(df)
    df = pd.concat(dfs, axis=1).T

    fieldnames = [
        "container_scitex_id",
        "metadata_url_doi",
        "metadata_url_publisher",
        "metadata_url_openurl_query",
        "container_readable_name",
        "container_pdf_size_bytes",
        "metadata_url_pdfs_0",
        "metadata_path_pdfs_0",
        "metadata_url_doi_engines_0",
        "metadata_url_publisher_engines_0",
        "metadata_url_openurl_engines_0",
        "metadata_url_openurl_resolved_0",
        "metadata_url_openurl_resolved_engines_0",
        "metadata_url_pdfs_engines_0",
        "metadata_url_pdfs_1",
        "metadata_url_pdfs_2",
    ]
    df = df[fieldnames].reset_index().drop(columns="index")

    mapper = {
        "container_scitex_id": "scitex_id",
        "metadata_url_doi": "url_doi",
        "metadata_url_publisher": "url_publisher",
        "metadata_url_openurl_query": "url_openurl_query",
    }
    df = df.rename(mapper)

    print(df.head())

    return stx.io.save(df, output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate PDF download summary table"
    )
    parser.add_argument("project", help="Project name")
    parser.add_argument("-o", "--output", type=Path, help="Output CSV path")

    args = parser.parse_args()

    result = generate_download_summary(args.project, args.output)

    if result:
        print(f"\nSummary table generated: {result}")
        sys.exit(0)
    else:
        print("\nFailed to generate summary table")
        sys.exit(1)

# Usage:
# python -m scitex.scholar.utils.generate_download_summary neurovista
# python -m scitex.scholar.utils.generate_download_summary pac -o ~/pac_summary.csv

# EOF
