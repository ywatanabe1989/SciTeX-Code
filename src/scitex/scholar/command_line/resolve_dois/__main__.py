#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 18:20:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/resolve_dois/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/resolve_dois/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for resumable DOI resolution.

Usage:
    # Resolve single paper by title
    python -m scitex.scholar.resolve_dois --title "Attention is All You Need"

    # Resolve from BibTeX file
    python -m scitex.scholar.resolve_dois --bibtex papers.bib

    # Resume interrupted resolution
    python -m scitex.scholar.resolve_dois --bibtex papers.bib --resume

    # Use specific progress file
    python -m scitex.scholar.resolve_dois --bibtex papers.bib --progress my_progress.json

Examples:
    # Resolve single paper with year
    python -m scitex.scholar.resolve_dois --title "Attention is All You Need" --year 2017

    # Resolve with specific sources
    python -m scitex.scholar.resolve_dois --bibtex papers.bib --sources crossref semantic_scholar

    # Save results to JSON
    python -m scitex.scholar.resolve_dois --bibtex papers.bib --output resolved_dois.json

    # Use more workers for faster processing
    python -m scitex.scholar.resolve_dois --bibtex papers.bib --workers 8
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from scitex import logging

from ..doi._BatchDOIResolver import BatchDOIResolver

# from ..doi._BatchDOIResolver import BatchDOIResolver

logger = logging.getLogger(__name__)


def resolve_single_title(
    title: str,
    year: Optional[int] = None,
    authors: Optional[str] = None,
    sources: Optional[list] = None,
) -> Optional[str]:
    """Resolve DOI for a single paper title."""
    from ..doi import DOIResolver

    resolver = DOIResolver()

    # Parse authors if provided
    author_list = None
    if authors:
        author_list = [a.strip() for a in authors.split(",")]

    logger.info(f"Resolving DOI for: {title}")
    if year:
        logger.info(f"Year: {year}")
    if author_list:
        logger.info(f"Authors: {', '.join(author_list)}")

    doi = resolver.title_to_doi(
        title=title, year=year, authors=author_list, sources=sources
    )

    if doi:
        logger.success(f"Found DOI: {doi}")
        logger.info(f"URL: https://doi.org/{doi}")
    else:
        logger.warning("No DOI found")

    return doi


def main():
    """Main CLI function for DOI resolution."""
    parser = argparse.ArgumentParser(
        description="Resolve DOIs from paper titles or BibTeX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve single paper
  python -m scitex.scholar.resolve_dois --title "Attention is All You Need"

  # Resolve from BibTeX file
  python -m scitex.scholar.resolve_dois --bibtex papers.bib

  # Resume interrupted resolution
  python -m scitex.scholar.resolve_dois --bibtex papers.bib --resume

  # Use enhanced resolver with better performance
  python -m scitex.scholar.resolve_dois --bibtex papers.bib --enhanced --workers 8

This command will:
- Resolve DOIs using multiple sources (CrossRef, PubMed, Semantic Scholar, etc.)
- Show real-time progress with ETA (like rsync)
- Save progress automatically (resume if interrupted)
- Handle rate limits gracefully
- Cache results for faster re-runs
        """,
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "--title", "-t", type=str, help="Single paper title to resolve"
    )

    input_group.add_argument(
        "--bibtex", "-b", type=str, help="BibTeX file containing papers"
    )

    # Additional metadata for single title
    parser.add_argument(
        "--year", "-y", type=int, help="Publication year (for single title)"
    )

    parser.add_argument(
        "--authors",
        "-a",
        type=str,
        help="Comma-separated author names (for single title)",
    )

    # Resolution options
    parser.add_argument(
        "--sources",
        "-s",
        nargs="+",
        choices=[
            "crossref",
            "pubmed",
            "semantic_scholar",
            "openalex",
            "arxiv",
        ],
        help="DOI sources to use (default: all)",
    )

    parser.add_argument(
        "--resume",
        "-r",
        action="store_true",
        help="Resume from last progress (auto-finds progress file)",
    )

    parser.add_argument(
        "--progress", "-p", type=str, help="Specific progress file to use"
    )

    parser.add_argument(
        "--enhanced",
        "-e",
        action="store_true",
        help="Use enhanced resolver with better performance",
    )

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)",
    )

    # Output options
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for results (JSON format)",
    )

    parser.add_argument(
        "--update-bibtex",
        "-u",
        action="store_true",
        help="Update the original BibTeX file with resolved DOIs",
    )

    parser.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Update BibTeX file incrementally as DOIs are found (safer for large files)",
    )

    parser.add_argument(
        "--update-interval",
        type=int,
        default=5,
        help="Update BibTeX file every N resolved DOIs (default: 5)",
    )

    # Display options
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed progress"
    )

    args = parser.parse_args()

    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    try:
        # Single title resolution
        if args.title:
            doi = resolve_single_title(
                title=args.title,
                year=args.year,
                authors=args.authors,
                sources=args.sources,
            )

            # Save result if requested
            if args.output and doi:
                with open(args.output, "w") as f:
                    json.dump({args.title: doi}, f, indent=2)
                logger.info(f"Result saved to: {args.output}")

            sys.exit(0 if doi else 1)

        # BibTeX file resolution
        else:
            bibtex_path = Path(args.bibtex)
            if not bibtex_path.exists():
                logger.fail(f"BibTeX file not found: {bibtex_path}")
                sys.exit(1)

            # Determine progress file
            progress_file = None
            if args.progress:
                progress_file = Path(args.progress)
            elif args.resume:
                # Auto-find most recent progress file
                progress_files = list(
                    Path.cwd().glob("doi_resolution_*.progress.json")
                )
                if progress_files:
                    progress_file = max(
                        progress_files, key=lambda p: p.stat().st_mtime
                    )
                    logger.info(f"Found progress file: {progress_file}")
                else:
                    logger.warning("No progress file found, starting fresh")

            # Create resolver
            if args.enhanced:
                logger.info(
                    "Using enhanced resolver with performance optimizations"
                )
                resolver = BatchDOIResolver(
                    progress_file=progress_file, max_workers=args.workers
                )
            else:
                resolver = BatchDOIResolver(progress_file=progress_file)

            # Show status
            if progress_file and progress_file.exists():
                stats = resolver.progress_data["statistics"]
                logger.info(
                    f"Resuming: {stats['processed']}/{stats['total']} processed, "
                    f"{stats['resolved']} resolved"
                )

            # Configure incremental updates
            if args.incremental and (args.update_bibtex or args.incremental):
                # Use standalone SQLite resolver for incremental updates
                from ..doi._StandaloneSQLiteDOIResolver import (
                    StandaloneSQLiteDOIResolver,
                )

                logger.info(
                    f"Using SQLite resolver with incremental updates (every {args.update_interval} papers)"
                )
                sqlite_resolver = StandaloneSQLiteDOIResolver()

                results = sqlite_resolver.resolve_from_bibtex(
                    bibtex_path=bibtex_path,
                    sources=args.sources,
                    update_bibtex=True,
                    update_interval=args.update_interval,
                )

                # Skip the normal update_bibtex since it's already done incrementally
                args.update_bibtex = False

                # Show statistics
                stats = sqlite_resolver.get_statistics()
                logger.info(
                    f"\nDatabase statistics: {stats['papers']['total']} papers, "
                    f"{stats['papers']['with_doi']} with DOIs"
                )
            else:
                # Normal batch resolution
                results = resolver.resolve_from_bibtex(
                    bibtex_path=bibtex_path, sources=args.sources
                )

            # Save results if requested
            if args.output:
                output_path = Path(args.output)
                with open(output_path, "w") as f:
                    json.dump(results, f, indent=2)
                logger.success(f"Results saved to: {output_path}")

            # Update BibTeX if requested
            if args.update_bibtex:
                _update_bibtex_file(bibtex_path, results)
                logger.success(f"Updated BibTeX file: {bibtex_path}")

            # Show sample results
            if not args.quiet and results:
                logger.info("\nSample results:")
                for i, (title, doi) in enumerate(list(results.items())[:5]):
                    logger.info(f"  {title[:60]}... -> {doi}")
                if len(results) > 5:
                    logger.info(f"  ... and {len(results) - 5} more")

    except KeyboardInterrupt:
        logger.warning("\nDOI resolution interrupted - progress saved")
        logger.info(
            "Resume with: python -m scitex.scholar.resolve_dois --bibtex <file> --resume"
        )
        sys.exit(1)
    except Exception as e:
        logger.fail(f"DOI resolution failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def _update_bibtex_file(bibtex_path: Path, doi_mapping: dict):
    """Update BibTeX file with resolved DOIs."""
    from scitex.io import load, save

    # Create backup
    backup_path = bibtex_path.with_suffix(".bib.bak")
    import shutil

    shutil.copy2(bibtex_path, backup_path)
    logger.info(f"Created backup: {backup_path}")

    # Load entries
    entries = load(str(bibtex_path))

    # Update DOIs
    updated_count = 0
    for entry in entries:
        fields = entry.get("fields", {})
        title = fields.get("title", "").strip()

        if title in doi_mapping and not fields.get("doi"):
            fields["doi"] = doi_mapping[title]
            fields["doi_source"] = "scitex_resolver"
            fields["doi_resolved_at"] = (
                __import__("datetime").datetime.now().isoformat()
            )
            updated_count += 1

    # Save updated entries
    if updated_count > 0:
        save(entries, str(bibtex_path))
        logger.info(f"Updated {updated_count} entries with DOIs")
    else:
        logger.info("No updates needed - all entries already have DOIs")


if __name__ == "__main__":
    main()

# EOF
