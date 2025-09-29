#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/bibtex.py
# ----------------------------------------
"""Unified CLI for BibTeX operations (merge and enrich).

Usage:
    # Enrich single file
    python -m scitex.scholar.cli.bibtex --bibtex file.bib --enrich

    # Merge multiple files
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

    # Merge and enrich in one step
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich

    # Specify output
    python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge --enrich -o output.bib
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.storage import BibTeXHandler

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Unified BibTeX operations: merge and enrich",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Enrich single file
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich

# Merge multiple files
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

# Merge and enrich
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib file3.bib --merge --enrich -o output.bib
""",
    )

    parser.add_argument(
        "--bibtex",
        nargs="+",
        required=True,
        help="Input BibTeX file(s)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (auto-generated if not specified)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge multiple input files (implied when >1 file)"
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Enrich papers with metadata"
    )
    parser.add_argument(
        "--dedup",
        choices=["smart", "keep_first", "keep_all"],
        default="smart",
        help="Deduplication strategy for merge (default: smart)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup when modifying files"
    )
    parser.add_argument(
        "--project",
        type=str,
        default="bibtex_cli",
        help="Project name for library storage"
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
    """Main CLI function for unified BibTeX operations."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate input files
    input_paths = [Path(p) for p in args.bibtex]
    for input_path in input_paths:
        if not input_path.exists():
            logger.fail(f"Input file not found: {input_path}")
            sys.exit(1)
        if not input_path.suffix.lower() == ".bib":
            logger.warning(f"Input file does not have .bib extension: {input_path}")

    # Determine operations
    needs_merge = len(input_paths) > 1 or args.merge
    needs_enrich = args.enrich

    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    # Set output path
    if args.output:
        output_path = Path(args.output)
    elif needs_merge:
        # Auto-generate filename for merged output
        base_names = [p.stem for p in input_paths]
        merged_name = "-".join(base_names)
        if needs_enrich:
            output_path = Path(f"{merged_name}_enriched.bib")
        else:
            output_path = Path(f"{merged_name}.bib")
        if not args.quiet:
            logger.info(f"Auto-generated output filename: {output_path}")
    elif needs_enrich:
        # Single file with enrichment: add _enriched suffix
        input_path = input_paths[0]
        output_path = input_path.parent / f"{input_path.stem}_enriched.bib"
        if not args.quiet:
            logger.info(f"Auto-generated output filename: {output_path}")
    else:
        # Single file: enrich in-place
        output_path = input_paths[0]

    try:
        scholar = Scholar(project=args.project)
        handler = BibTeXHandler()

        # Step 1: Load or merge papers
        if needs_merge:
            if not args.quiet:
                logger.info(f"Merging {len(input_paths)} BibTeX files...")

            merge_result = handler.merge_bibtex_files(
                file_paths=input_paths,
                dedup_strategy=args.dedup,
                return_details=True
            )

            papers = merge_result["papers"]
            file_papers = merge_result.get("file_papers", {})
            stats = merge_result.get("stats", {})

            if not args.quiet:
                logger.info(f"Merged {len(papers)} unique papers")
        else:
            # Single file mode
            input_path = input_paths[0]

            # Create backup if modifying in-place
            if not args.no_backup and output_path == input_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = input_path.parent / f"{input_path.stem}.{timestamp}.bak.bib"
                shutil.copy2(input_path, backup_path)
                if not args.quiet:
                    logger.info(f"Created backup: {backup_path}")

            if not args.quiet:
                logger.info(f"Loading papers from: {input_path}")

            papers = scholar.load_bibtex(input_path)
            file_papers = None
            stats = None

            if not args.quiet:
                logger.info(f"Loaded {len(papers)} papers")

        # Step 2: Enrich if requested
        if needs_enrich:
            if not args.quiet:
                # Track original state
                original_doi_count = sum(1 for p in papers if p.doi)
                original_abstract_count = sum(1 for p in papers if p.abstract)
                original_citation_count = sum(1 for p in papers if p.citation_count)

                logger.info("\nEnriching papers with metadata...")

            enriched_papers = scholar.enrich_papers(papers)

            if not args.quiet:
                # Show enrichment results
                with_doi = sum(1 for p in enriched_papers if p.doi)
                with_abstract = sum(1 for p in enriched_papers if p.abstract)
                with_citations = sum(1 for p in enriched_papers if p.citation_count)

                logger.success(f"Enriched {len(enriched_papers)} papers")
                logger.info("\nEnrichment results:")
                logger.info(f"  Papers with DOI: {with_doi}/{len(enriched_papers)} "
                           f"(+{with_doi - original_doi_count} new)")
                logger.info(f"  Papers with abstract: {with_abstract}/{len(enriched_papers)} "
                           f"(+{with_abstract - original_abstract_count} new)")
                logger.info(f"  Papers with citations: {with_citations}/{len(enriched_papers)} "
                           f"(+{with_citations - original_citation_count} new)")

            papers = enriched_papers

        # Step 3: Save output
        if needs_merge:
            handler.papers_to_bibtex_with_sources(
                papers=papers,
                output_path=output_path,
                source_files=input_paths,
                file_papers=file_papers,
                stats=stats
            )
        else:
            scholar.save_papers_as_bibtex(papers, output_path)

        if not args.quiet:
            logger.success(f"\nOutput saved to: {output_path}")
            logger.info(f"Total papers: {len(papers)}")

    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.fail(f"Operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF