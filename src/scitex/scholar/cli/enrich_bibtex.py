#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 04:21:31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/enrich_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/enrich_bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for BibTeX enrichment.

Usage:
    python -m scitex.scholar.enrich_bibtex input.bib [output.bib]

Examples:
    # Enrich in-place (creates backup)
    python -m scitex.scholar.enrich_bibtex pac.bib

    # Save to new file
    python -m scitex.scholar.enrich_bibtex pac.bib papers_enriched.bib
"""

import argparse
import sys
from pathlib import Path

from scitex import log, logging
from scitex.scholar import Scholar

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Add impact factors, citations, and metadata to BibTeX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Enrich in-place (creates backup)
python -m scitex.scholar enrich_bibtex pac.bib

# Save to new file
python -m scitex.scholar enrich_bibtex pac.bib papers_enriched.bib""",
    )

    parser.add_argument("input", type=str, help="Input BibTeX file to enrich")
    parser.add_argument(
        "output",
        type=str,
        nargs="?",
        help="Output file (defaults to input file with backup)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup when overwriting input file",
    )
    parser.add_argument(
        "--no-preserve",
        action="store_true",
        help="Don't preserve original BibTeX fields",
    )
    parser.add_argument(
        "--no-abstracts",
        action="store_true",
        help="Don't fetch missing abstracts",
    )
    parser.add_argument(
        "--no-urls", action="store_true", help="Don't fetch missing URLs"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )

    return parser


def main():
    """Main CLI function for BibTeX enrichment."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.fail(f"Input file not found: {input_path}")
        sys.exit(1)

    if not input_path.suffix.lower() == ".bib":
        logger.warning(
            f"Input file does not have .bib extension: {input_path}"
        )

    # Set output path
    output_path = Path(args.output) if args.output else None

    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        log.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    try:
        # Create scholar instance
        scholar = Scholar()

        # Show configuration
        if not args.quiet:
            logger.info(f"Enriching BibTeX file: {input_path}")
            if output_path and output_path != input_path:
                logger.info(f"Output will be saved to: {output_path}")
            else:
                logger.info(
                    "Enriching in-place"
                    + (
                        " (with backup)"
                        if not args.no_backup
                        else " (no backup)"
                    )
                )

        # Perform enrichment
        papers = scholar.enrich_bibtex(
            bibtex_path=input_path,
            output_path=output_path,
            backup=not args.no_backup,
            preserve_original_fields=not args.no_preserve,
            add_missing_abstracts=not args.no_abstracts,
            add_missing_urls=not args.no_urls,
        )

        # Show summary
        if not args.quiet:
            logger.success(f"\nSuccessfully enriched {len(papers)} papers")

            # Count enriched fields
            with_doi = sum(1 for p in papers if p.doi)
            with_impact = sum(1 for p in papers if p.impact_factor is not None)
            with_citations = sum(
                1 for p in papers if p.citation_count is not None
            )

            logger.info(f"  Papers with DOI: {with_doi}/{len(papers)}")
            logger.info(
                f"  Papers with impact factor: {with_impact}/{len(papers)}"
            )
            logger.info(
                f"  Papers with citation count: {with_citations}/{len(papers)}"
            )

            # Show output location
            final_output = output_path or input_path
            logger.info(f"\nEnriched file saved to: {final_output}")

            if not args.no_backup and (
                output_path is None or output_path == input_path
            ):
                backup_path = input_path.with_suffix(".bib.bak")
                logger.info(f"Original file backed up to: {backup_path}")

    except KeyboardInterrupt:
        logger.warning("\nEnrichment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.fail(f"Enrichment failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF
