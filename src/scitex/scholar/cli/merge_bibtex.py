#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/merge_bibtex.py
# ----------------------------------------
"""Command-line interface for merging multiple BibTeX files.

Usage:
    python -m scitex.scholar.merge_bibtex input1.bib input2.bib [...] -o merged.bib

Examples:
    # Merge two files
    python -m scitex.scholar.merge_bibtex papers1.bib papers2.bib -o merged.bib

    # Merge multiple files
    python -m scitex.scholar.merge_bibtex *.bib -o all_papers.bib

    # Merge and enrich
    python -m scitex.scholar.merge_bibtex *.bib -o merged.bib --enrich
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.storage import BibTeXHandler

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Merge multiple BibTeX files intelligently handling duplicates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Merge two files
python -m scitex.scholar.merge_bibtex papers1.bib papers2.bib -o merged.bib

# Merge all .bib files in directory
python -m scitex.scholar.merge_bibtex *.bib -o all_papers.bib

# Merge and enrich the result
python -m scitex.scholar.merge_bibtex *.bib -o merged.bib --enrich""",
    )

    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input BibTeX files to merge"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output merged BibTeX file (default: auto-generated from input names)"
    )
    parser.add_argument(
        "--dedup",
        choices=["smart", "keep_first", "keep_all"],
        default="smart",
        help="Deduplication strategy (default: smart)"
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Enrich papers after merging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )

    return parser


def main():
    """Main CLI function for BibTeX merging."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    # Validate input files
    input_paths = []
    for input_pattern in args.inputs:
        # Check if it's an absolute path first
        path = Path(input_pattern)
        if path.is_absolute():
            if path.exists():
                input_paths.append(path)
            else:
                logger.warning(f"File not found: {input_pattern}")
        else:
            # Try glob for relative paths
            paths = list(Path().glob(input_pattern))
            if paths:
                input_paths.extend(paths)
            else:
                # Try as direct relative path
                if path.exists():
                    input_paths.append(path)
                else:
                    logger.warning(f"No files found for: {input_pattern}")

    if not input_paths:
        logger.fail("No input files found")
        sys.exit(1)

    # Remove duplicates and sort
    input_paths = sorted(list(set(input_paths)))

    # Generate output filename if not specified
    if args.output:
        output_path = Path(args.output)
    else:
        # Create filename from input filenames: "file1-file2-file3.bib"
        base_names = [p.stem for p in input_paths]
        output_filename = "-".join(base_names) + ".bib"
        output_path = Path(output_filename)
        if not args.quiet:
            logger.info(f"Auto-generated output filename: {output_filename}")

    try:
        if not args.quiet:
            logger.info(f"Merging {len(input_paths)} BibTeX files...")
            logger.info(f"Deduplication strategy: {args.dedup}")

        # Use BibTeXHandler to merge files
        handler = BibTeXHandler()
        merge_result = handler.merge_bibtex_files(
            file_paths=input_paths,
            dedup_strategy=args.dedup,
            return_details=True
        )

        # Extract results
        merged_papers = merge_result["papers"]
        file_papers = merge_result.get("file_papers", {})
        stats = merge_result.get("stats", {})

        if not args.quiet:
            logger.info(f"\nMerged {len(merged_papers)} unique papers")

        # Optionally enrich
        if args.enrich:
            if not args.quiet:
                logger.info("\nEnriching merged papers...")
            scholar = Scholar(project="merge_cli")
            merged_papers = scholar.enrich_papers(merged_papers)
            if not args.quiet:
                logger.success("Enrichment complete")

        # Save merged result with enhanced format
        handler.papers_to_bibtex_with_sources(
            papers=merged_papers,
            output_path=output_path,
            source_files=input_paths,
            file_papers=file_papers,
            stats=stats
        )

        if not args.quiet:
            logger.success(f"\nMerged BibTeX saved to: {output_path}")
            logger.info(f"Total papers in output: {len(merged_papers)}")

    except KeyboardInterrupt:
        logger.warning("\nMerge cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.fail(f"Merge failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF