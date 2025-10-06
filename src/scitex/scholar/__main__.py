#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 10:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from scitex import logging

logger = logging.getLogger(__name__)


def create_parser():
    """Create the unified argument parser with flexible combinations."""
    epilog_text = """
EXAMPLES:
  # Basic workflow - enrich and download papers
  python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download

  # Download single paper by DOI
  python -m scitex.scholar --doi "10.1038/nature12373" --project myresearch --download

  # Filter high-impact papers before download
  python -m scitex.scholar --bibtex papers.bib --project important \\
      --min-citations 100 --min-impact-factor 10.0 --download

  # Create project and list papers
  python -m scitex.scholar --project myresearch --create-project --description "My research"
  python -m scitex.scholar --project myresearch --list

  # Search and export
  python -m scitex.scholar --project myresearch --search "neural" --export bibtex

STORAGE: ~/.scitex/scholar/library/
  MASTER/8DIGITID/  - Centralized storage (no duplicates)
  project_name/     - Project symlinks to MASTER

DOCUMENTATION: https://github.com/ywatanabe1989/SciTeX-Code/tree/main/src/scitex/scholar
"""

    parser = argparse.ArgumentParser(
        prog="python -m scitex.scholar",
        description="""
SciTeX Scholar - Unified Scientific Literature Management System
═════════════════════════════════════════════════════════════════

A comprehensive tool for managing academic papers with automatic enrichment,
PDF downloads, and persistent storage organization. Combines multiple operations
in flexible, chainable commands.

KEY FEATURES:
  • Automatic metadata enrichment (DOIs, abstracts, citations, impact factors)
  • Authenticated PDF downloads via institutional access
  • MASTER storage architecture prevents duplicates
  • Project-based organization with human-readable symlinks
  • Smart filtering by year, citations, and impact factor
  • Resume capability for interrupted operations
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text,
    )

    # Input sources
    input_group = parser.add_argument_group("Input Sources",
                                             "Specify papers to process (can combine with operations)")
    input_group.add_argument(
        "--bibtex",
        type=str,
        metavar="FILE",
        help="Path to BibTeX file containing paper references"
    )
    input_group.add_argument(
        "--doi",
        type=str,
        metavar="DOI",
        help='Single DOI to process (e.g., "10.1038/nature12373")'
    )
    input_group.add_argument(
        "--dois",
        type=str,
        nargs="+",
        metavar="DOI",
        help='Multiple DOIs to process (space-separated)'
    )
    input_group.add_argument(
        "--title",
        type=str,
        help="Paper title for DOI resolution or library search"
    )

    # Project management
    project_group = parser.add_argument_group("Project Management",
                                               "Organize papers in persistent project libraries")
    project_group.add_argument(
        "--project",
        "-p",
        type=str,
        metavar="NAME",
        help="Project name for organizing papers (stored in ~/.scitex/scholar/library/PROJECT)"
    )
    project_group.add_argument(
        "--create-project",
        action="store_true",
        help="Create a new project directory with metadata"
    )
    project_group.add_argument(
        "--description",
        type=str,
        help="Project description (use with --create-project)"
    )

    # Operations
    ops_group = parser.add_argument_group("Operations",
                                           "Actions to perform (can combine multiple)")
    ops_group.add_argument(
        "--enrich",
        "-e",
        action="store_true",
        help="Enrich papers with metadata (DOIs, abstracts, citations, impact factors)"
    )
    ops_group.add_argument(
        "--download",
        "-d",
        action="store_true",
        help="Download PDFs to MASTER library with project symlinks"
    )
    ops_group.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all papers in specified project"
    )
    ops_group.add_argument(
        "--search",
        "-s",
        type=str,
        metavar="QUERY",
        help="Search papers by title, author, or keyword"
    )
    ops_group.add_argument(
        "--stats",
        action="store_true",
        help="Display library statistics (projects, papers, storage)"
    )

    # Export options
    export_group = parser.add_argument_group("Export Options",
                                              "Save results in various formats")
    export_group.add_argument(
        "--export",
        choices=["bibtex", "csv", "json"],
        help="Export format for project papers (bibtex, csv, or json)"
    )
    export_group.add_argument(
        "--output",
        "-o",
        type=str,
        metavar="FILE",
        help="Output file path for enriched data or exports"
    )

    # Filtering options
    filter_group = parser.add_argument_group("Filtering Options",
                                              "Filter papers before operations")
    filter_group.add_argument(
        "--year-min",
        type=int,
        help="Minimum publication year (e.g., 2020)"
    )
    filter_group.add_argument(
        "--year-max",
        type=int,
        help="Maximum publication year (e.g., 2024)"
    )
    filter_group.add_argument(
        "--min-citations",
        type=int,
        help="Minimum citation count required"
    )
    filter_group.add_argument(
        "--min-impact-factor",
        type=float,
        help="Minimum journal impact factor (JCR 2024)"
    )
    filter_group.add_argument(
        "--has-pdf",
        action="store_true",
        help="Only include papers with downloaded PDFs"
    )

    # System options
    system_group = parser.add_argument_group("System Options",
                                              "Control execution behavior")
    system_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed debug output and error traces"
    )
    system_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable URL caching (forces fresh lookups)"
    )
    system_group.add_argument(
        "--browser",
        choices=["stealth", "interactive"],
        default="stealth",
        help="Browser mode for PDF downloads (stealth=hidden, interactive=visible)"
    )

    return parser


async def handle_bibtex_operations(args, scholar):
    """Handle operations on BibTeX files."""
    from pathlib import Path

    bibtex_path = Path(args.bibtex)
    if not bibtex_path.exists():
        logger.error(f"BibTeX file not found: {bibtex_path}")
        return 1

    # Load papers from BibTeX
    logger.info(f"Loading BibTeX: {bibtex_path}")
    papers = scholar.load_bibtex(bibtex_path)
    logger.info(f"Loaded {len(papers)} papers")

    # Apply filters if specified
    if any([args.year_min, args.year_max, args.min_citations, args.min_impact_factor, args.has_pdf]):
        papers = papers.filter(
            year_min=args.year_min,
            year_max=args.year_max,
            min_citations=args.min_citations,
            min_impact_factor=args.min_impact_factor,
            has_pdf=args.has_pdf if args.has_pdf else None
        )
        logger.info(f"After filtering: {len(papers)} papers")

    # Enrich if requested
    if args.enrich:
        logger.info("Enriching papers...")
        papers = scholar.enrich_papers(papers)

        # Save enriched BibTeX
        if args.output:
            output_path = Path(args.output)
        else:
            # Auto-generate enriched filename
            output_path = bibtex_path.parent / f"{bibtex_path.stem}_enriched.bib"

        scholar.save_papers_as_bibtex(papers, output_path)
        logger.success(f"Saved enriched BibTeX to: {output_path}")

    # Download PDFs if requested
    if args.download:
        dois = [p.doi for p in papers if p.doi]
        if dois:
            logger.info(f"Downloading PDFs for {len(dois)} papers...")
            results = await scholar.download_pdfs_from_dois_async(dois)
            logger.info(f"Downloaded: {results['downloaded']}, Failed: {results['failed']}")
        else:
            logger.warning("No DOIs found for PDF download")

    # Save to library if project specified
    if args.project and not args.download:  # download already saves to library
        logger.info(f"Saving to project: {args.project}")
        saved_ids = scholar.save_papers_to_library(papers)
        logger.info(f"Saved {len(saved_ids)} papers to library")

    return 0


async def handle_doi_operations(args, scholar):
    """Handle operations on DOIs."""
    # Collect all DOIs
    dois = []
    if args.doi:
        dois.append(args.doi)
    if args.dois:
        dois.extend(args.dois)

    if not dois:
        logger.error("No DOIs specified")
        return 1

    logger.info(f"Processing {len(dois)} DOIs")

    # Download PDFs if requested
    if args.download:
        results = await scholar.download_pdfs_from_dois_async(dois)
        logger.info(f"Downloaded: {results['downloaded']}, Failed: {results['failed']}")

    # Enrich if requested (create Papers from DOIs first)
    if args.enrich:
        from scitex.scholar.core.Paper import Paper
        from scitex.scholar.core.Papers import Papers

        papers_list = [Paper(doi=doi) for doi in dois]
        papers = Papers(papers_list, project=args.project)

        logger.info("Enriching papers from DOIs...")
        papers = scholar.enrich_papers(papers)

        # Save enriched data
        if args.output:
            output_path = Path(args.output)
            scholar.save_papers_as_bibtex(papers, output_path)
            logger.success(f"Saved enriched papers to: {output_path}")

        # Save to library if project specified
        if args.project:
            saved_ids = scholar.save_papers_to_library(papers)
            logger.info(f"Saved {len(saved_ids)} papers to library")

    return 0


async def handle_project_operations(args, scholar):
    """Handle project-specific operations."""

    # Create project if requested
    if args.create_project:
        project_dir = scholar._create_project_metadata(
            args.project,
            description=args.description
        )
        logger.success(f"Created project: {args.project} at {project_dir}")
        return 0

    # List papers in project
    if args.list:
        papers = scholar.load_project(args.project)
        logger.info(f"\nProject: {args.project}")
        logger.info(f"Papers: {len(papers)}")

        for i, paper in enumerate(papers[:20], 1):  # Show first 20
            title = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title
            info = []
            if paper.year:
                info.append(str(paper.year))
            if paper.doi:
                info.append(paper.doi)

            print(f"{i:3d}. {title}")
            if info:
                print(f"     {' | '.join(info)}")

        if len(papers) > 20:
            print(f"\n... and {len(papers) - 20} more papers")

    # Search in project/library
    if args.search:
        if args.project:
            results = scholar.search_library(args.search, project=args.project)
        else:
            results = scholar.search_across_projects(args.search)

        logger.info(f"\nSearch results for: {args.search}")
        logger.info(f"Found: {len(results)} papers")

        for i, paper in enumerate(results[:10], 1):  # Show first 10
            title = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title
            print(f"{i:3d}. {title} ({paper.year or 'n/a'})")

    # Export project
    if args.export:
        papers = scholar.load_project(args.project)

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path(f"{args.project}_export.{args.export}")

        if args.export == "bibtex":
            scholar.save_papers_as_bibtex(papers, output_path)
        elif args.export == "csv":
            # TODO: Implement CSV export
            logger.warning("CSV export not yet implemented")
            return 1
        elif args.export == "json":
            import json
            with open(output_path, 'w') as f:
                json.dump([p.to_dict() for p in papers], f, indent=2, default=str)

        logger.success(f"Exported to: {output_path}")

    return 0


async def main_async():
    """Main async entry point for the unified CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    # Set up logging
    if args.debug:
        logging.set_level(logging.DEBUG)

    # Initialize Scholar
    from scitex.scholar.core.Scholar import Scholar

    scholar = Scholar(project=args.project) if args.project else Scholar()

    try:
        # Route to appropriate handler based on input
        if args.bibtex:
            return await handle_bibtex_operations(args, scholar)

        elif args.doi or args.dois:
            return await handle_doi_operations(args, scholar)

        elif args.project:
            return await handle_project_operations(args, scholar)

        elif args.stats:
            # Show library statistics
            stats = scholar.get_library_statistics()
            print("\n📊 Scholar Library Statistics")
            print("=" * 40)
            print(f"Total projects: {stats['total_projects']}")
            print(f"Total papers: {stats['total_papers']}")
            print(f"Storage: {stats['storage_mb']:.1f} MB")
            print(f"Library path: {stats['library_path']}")

            if stats['projects']:
                print("\n📁 Projects:")
                for project in stats['projects']:
                    print(f"  - {project['name']}: {project['papers_count']} papers")

            return 0

        else:
            logger.error("No valid input or operation specified")
            parser.print_help()
            return 1

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    try:
        sys.exit(asyncio.run(main_async()))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF