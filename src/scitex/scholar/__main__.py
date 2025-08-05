#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 16:35:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="python -m scitex.scholar",
        description="SciTeX Scholar - Academic paper management and metadata enrichment tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Available Commands:

resolve-and-enrich:
  Resolve DOIs and enrich metadata with project organization
  python -m scitex.scholar resolve-and-enrich --bibtex papers.bib --project myproject
  python -m scitex.scholar resolve-and-enrich --title "Paper Title" --project myproject
  python -m scitex.scholar resolve-and-enrich --project myproject --summary

enrich-bibtex:
  Enrich existing BibTeX files with metadata (impact factors, citations, abstracts)
  python -m scitex.scholar enrich-bibtex papers.bib
  python -m scitex.scholar enrich-bibtex papers.bib enriched.bib --no-abstracts
  python -m scitex.scholar enrich-bibtex papers.bib --verbose

For detailed help on each command:
  python -m scitex.scholar resolve-and-enrich -h
  python -m scitex.scholar enrich-bibtex -h

Data Sources:
  - DOI Resolution: CrossRef, PubMed, Semantic Scholar, OpenAlex, arXiv
  - Metadata: JCR 2024 impact factors, citation counts, abstracts, quartiles
  - Project organization in ~/.scitex/scholar/library/
""",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    subparsers.add_parser(
        "resolve-and-enrich",
        help="Resolve DOIs and enrich metadata with project support",
    )
    subparsers.add_parser("enrich-bibtex", help="Enrich BibTeX with metadata")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args, remaining = parser.parse_known_args()

    if args.command == "resolve-and-enrich":
        from .command_line.resolve_and_enrich import main as enhanced_main

        original_argv = sys.argv
        sys.argv = ["resolve-and-enrich"] + remaining
        try:
            enhanced_main()
        finally:
            sys.argv = original_argv
    elif args.command == "enrich-bibtex":
        from .command_line.enrich_bibtex import main as enrich_main

        original_argv = sys.argv
        sys.argv = ["enrich-bibtex"] + remaining
        try:
            enrich_main()
        finally:
            sys.argv = original_argv
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# EOF
