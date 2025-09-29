#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 04:32:57 (ywatanabe)"
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
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scitex import logging
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

    parser.add_argument(
        "input",
        type=str,
        nargs="+",
        help="Input BibTeX file(s) to enrich (multiple files will be merged)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (defaults to input file with backup, or auto-generated for merge)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup when overwriting input file",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge multiple input files (implied when multiple inputs provided)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="enrich_cli",
        help="Project name for library storage",
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

    # Handle multiple files (merge mode)
    input_paths = [Path(p) for p in args.input]

    # Validate all input files exist
    for input_path in input_paths:
        if not input_path.exists():
            logger.fail(f"Input file not found: {input_path}")
            sys.exit(1)
        if not input_path.suffix.lower() == ".bib":
            logger.warning(f"Input file does not have .bib extension: {input_path}")

    # Determine if we need to merge
    needs_merge = len(input_paths) > 1 or args.merge

    # Set output path
    if args.output:
        output_path = Path(args.output)
    elif needs_merge:
        # Auto-generate filename for merged output
        base_names = [p.stem for p in input_paths]
        output_path = Path("-".join(base_names) + ".bib")
        logger.info(f"Auto-generated output filename: {output_path}")
    else:
        output_path = None

    input_path = input_paths[0]  # For single file mode

    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    try:
        # Create scholar instance
        scholar = Scholar(project=args.project)

        # Handle merge mode
        if needs_merge:
            from scitex.scholar.storage import BibTeXHandler

            if not args.quiet:
                logger.info(f"Merging {len(input_paths)} BibTeX files...")

            handler = BibTeXHandler()
            merge_result = handler.merge_bibtex_files(
                file_paths=input_paths,
                dedup_strategy="smart",
                return_details=True
            )

            papers = merge_result["papers"]
            if not args.quiet:
                logger.info(f"Merged {len(papers)} unique papers")
        else:
            # Single file mode
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

            # Create backup if enriching in-place
            backup_path = None
            if not output_path or output_path == input_path:
                if not args.no_backup:
                    # Create timestamped backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = input_path.parent / f"{input_path.stem}.{timestamp}.bak.bib"
                    shutil.copy2(input_path, backup_path)
                    if not args.quiet:
                        logger.info(f"Created backup: {backup_path}")

            # Load papers from BibTeX
            if not args.quiet:
                logger.info("Loading papers from BibTeX...")
            papers = scholar.load_bibtex(input_path)
            if not args.quiet:
                logger.info(f"Loaded {len(papers)} papers")

        # Check current state
        original_doi_count = sum(1 for p in papers if p.doi)
        original_abstract_count = sum(1 for p in papers if p.abstract)
        original_citation_count = sum(1 for p in papers if p.citation_count)

        # Perform enrichment
        if not args.quiet:
            logger.info("Enriching papers with metadata...")
        enriched_papers = scholar.enrich_papers(papers)

        # Save enriched papers to BibTeX
        final_output = output_path or input_path
        bibtex_content = scholar.save_papers_as_bibtex(enriched_papers, final_output)

        # Show summary
        if not args.quiet:
            logger.success(f"\nSuccessfully enriched {len(enriched_papers)} papers")

            # Count enriched fields
            with_doi = sum(1 for p in enriched_papers if p.doi)
            with_abstract = sum(1 for p in enriched_papers if p.abstract)
            with_citations = sum(
                1 for p in enriched_papers if p.citation_count
            )

            # Show improvements
            logger.info("\nEnrichment results:")
            logger.info(f"  Papers with DOI: {with_doi}/{len(enriched_papers)} "
                       f"(+{with_doi - original_doi_count} new)")
            logger.info(f"  Papers with abstract: {with_abstract}/{len(enriched_papers)} "
                       f"(+{with_abstract - original_abstract_count} new)")
            logger.info(f"  Papers with citations: {with_citations}/{len(enriched_papers)} "
                       f"(+{with_citations - original_citation_count} new)")

            # Show output location
            logger.info(f"\nEnriched file saved to: {final_output}")
            if backup_path:
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
