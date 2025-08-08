#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 15:00:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/resolve_doi.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/resolve_doi.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Demonstration of the unified DOI resolver interface."""

import argparse
import asyncio
import sys

from ..metadata.doi import DOIResolver


def create_parser():
    parser = argparse.ArgumentParser(
        description="Find DOIs from titles, BibTeX files, or DOI strings"
    )

    parser.add_argument(
        "--project",
        type=str,
        default="default",
        help="Project name for Scholar library (default: default)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum concurrent workers for batch processing (default: 4)",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        help="Specific DOI sources to use (e.g., crossref pubmed)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous progress file",
    )
    parser.add_argument(
        "input", nargs="?", help="DOI, file path, or BibTeX content to resolve"
    )
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.input:
        resolver = DOIResolver()
        try:
            kwargs = {
                "project": args.project,
                "max_workers": args.max_workers,
                "resume": args.resume,
            }
            if args.sources:
                kwargs["sources"] = args.sources
            result = await resolver.resolve_async(args.input, **kwargs)
            print(f"Resolved: {result}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())

# EOF
