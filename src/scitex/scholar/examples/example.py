#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 15:23:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/example.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/examples/example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionality:
- Demonstrates the Scholar class for academic literature search and enrichment
- Shows how to search for papers with automatic impact factor and citation enrichment
- Provides examples of saving papers in multiple formats

Input:
- Environment variables for API keys and email addresses
- Search query parameters and filters

Output:
- Enriched paper collection with impact factors and citations
- Saved files in BibTeX, CSV, and JSON formats

Prerequisites:
- scitex package with Scholar module
- Environment variables for API access
- Internet connection for paper search and enrichment
"""

import argparse

import scitex as stx


def main(args):
    """Main function to demonstrate Scholar usage."""

    # Initialize Scholar with API keys
    scholar = stx.scholar.Scholar(
        email_pubmed=os.getenv("SCITEX_PUBMED_EMAIL"),
        email_crossref=os.getenv("SCITEX_CROSSREF_EMAIL"),
        api_key_semantic_scholar=os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY"),
        api_key_crossref=os.getenv("SCITEX_CROSSREF_API_KEY"),
        workspace_dir="~/.scitex/scholar",
        impact_factors=True,
        citations=True,
        auto_download=False,
    )

    # Search for papers
    papers = scholar.search(
        query=args.query,
        limit=args.limit,
        sources=args.sources,
        year_min=args.year_min,
        year_max=args.year_max,
    )

    stx.str.printc(f"Found {len(papers)} papers", c="green")

    # Display sample papers
    for paper in papers[: args.display_count]:
        print(f"{paper.title}")
        print(f"  Journal: {paper.journal} (IF: {paper.impact_factor})")
        print(f"  Citations: {paper.citation_count}")
        print(f"  Year: {paper.year}")
        print()

    # Save papers in multiple formats
    if args.save:
        papers.save(os.path.join(__DIR__, "papers.bib"))
        papers.save(os.path.join(__DIR__, "papers.csv"))
        papers.save(os.path.join(__DIR__, "papers.json"))

        stx.str.printc(f"Saved papers to {__DIR__}", c="cyan")

    return 0


def parse_args():
    """Parse command line arguments."""
    script_mode = stx.gen.is_script()

    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar functionality for academic literature search"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=(
            "epilepsy detection machine learning" if not script_mode else None
        ),
        required=script_mode,
        help="Search query for papers",
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=50,
        help="Maximum number of papers to retrieve (default: %(default)s)",
    )

    parser.add_argument(
        "--sources",
        "-s",
        nargs="+",
        default=["pubmed"],
        choices=["pubmed", "arxiv", "semantic_scholar"],
        help="Sources to search (default: %(default)s)",
    )

    parser.add_argument(
        "--year-min",
        type=int,
        default=2020,
        help="Minimum publication year (default: %(default)s)",
    )

    parser.add_argument(
        "--year-max",
        type=int,
        default=2024,
        help="Maximum publication year (default: %(default)s)",
    )

    parser.add_argument(
        "--display-count",
        "-d",
        type=int,
        default=3,
        help="Number of sample papers to display (default: %(default)s)",
    )

    parser.add_argument(
        "--save", action="store_true", help="Save papers to output files"
    )

    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main():
    """Initialize scitex framework and run main function."""
    global CONFIG, CC, sys, plt
    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
        fig_scale=2,
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/example.py --query 'epilepsy prediction' --save

# EOF
