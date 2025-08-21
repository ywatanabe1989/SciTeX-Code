#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:34:13 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/03_02-engine-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/03_02-engine-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Parses BibTeX files and extracts academic paper titles
- Uses ScholarEngine to search for metadata of papers in batch
- Supports caching and sampling for efficient processing
- Saves metadata results as JSON with symbolic linking

Dependencies:
- scripts:
  - None
- packages:
  - scitex, numpy, asyncio

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib
- ./data/scholar/pac.bib

Output:
- ./data/scholar/pac_metadata.json
- Console output of search results
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import numpy as _np

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def search_bibtex_metadata(
    bibtex_path: str, use_cache: bool = True, n_samples: int = None
) -> list:
    """Search for metadata of papers from BibTeX file."""
    from scitex.scholar import ScholarConfig, ScholarEngine
    from scitex.scholar.utils import parse_bibtex

    entries = parse_bibtex(bibtex_path)
    if n_samples:
        entries = _np.random.permutation(entries)[:n_samples].tolist()

    query_titles = [entry.get("title") for entry in entries]
    pprint(query_titles)

    config = ScholarConfig()
    engine = ScholarEngine(config=config, use_cache=use_cache)

    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")

    batched_metadata = await engine.search_batch_async(titles=query_titles)
    return batched_metadata


async def main_async(args):
    # Parameters
    bibtex_paths = [
        "./data/scholar/openaccess.bib",
        "./data/scholar/paywalled.bib",
        "./data/scholar/pac.bib",
    ]
    selected_path = bibtex_paths[args.bibtex_index]

    batched_metadata = await search_bibtex_metadata(
        bibtex_path=selected_path,
        use_cache=not args.no_cache,
        n_samples=args.n_samples,
    )

    pprint(batched_metadata)

    output_name = selected_path.split("/")[-1].replace(
        ".bib", "_metadata.json"
    )
    output_path = f"./data/scholar/{output_name}"

    stx.io.save(batched_metadata, output_path, symlink_from_cwd=True)

    return batched_metadata


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Search metadata for papers in BibTeX files"
    )
    parser.add_argument(
        "--bibtex_index",
        "-b",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="BibTeX file index (0: openaccess, 1: paywalled, 2: pac) (default: %(default)s)",
    )
    parser.add_argument(
        "--n_samples",
        "-n",
        type=int,
        default=None,
        help="Number of samples to process (default: %(default)s)",
    )
    parser.add_argument(
        "--no_cache",
        "-nc",
        action="store_true",
        default=False,
        help="Disable caching for search engines (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = asyncio.run(main_async(args))

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
