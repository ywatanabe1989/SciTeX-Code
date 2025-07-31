#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 01:42:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/resolve_dois.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/resolve_dois.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio

from ._DOIResolver import DOIResolver


async def resolve_dois(args):
    resolver = DOIResolver()

    if args.title:
        doi = await resolver.title_to_doi_async(args.title)
        if doi:
            print(f"\nFound DOI: {doi}")
            print(f"URL: https://doi.org/{doi}")
        else:
            print("\nNo DOI found")


def main():
    parser = argparse.ArgumentParser(
        description="Resolve DOIs from paper titles"
    )
    parser.add_argument(
        "--title",
        "-t",
        type=str,
        required=True,
        help="Paper title to search for DOI",
    )

    args = parser.parse_args()
    asyncio.run(resolve_dois(args))


if __name__ == "__main__":
    main()

# python -m scitex.scholar.doi.resolve_dois --title "Attention is All You Need"

# EOF
