#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 06:04:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

""

import argparse
import asyncio
import sys
from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)

from .utils._cleanup_scholar_processes import cleanup_scholar_processes


def create_parser():
    """Create the unified argument parser with flexible combinations."""
    epilog_text = """
EXAMPLES:
  # RECOMMENDED: Two-step workflow for reliability
  # Step 1: Enrich metadata (DOIs, abstracts, citations, impact factors)
  python -m scitex.scholar --bibtex papers.bib \\
      --output papers_enriched.bib --project myresearch --enrich

  # Step 2: Download PDFs from enriched metadata
  python -m scitex.scholar --bibtex papers_enriched.bib \\
      --project myresearch --download

  # Single-step (works but less reliable for large batches)
  python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download

  # Manual browser download with auto-linking (for failed PDFs)
  python -m scitex.scholar --browser --project neurovista

  # Download single paper by DOI
  python -m scitex.scholar --doi "10.1038/nature12373" --project myresearch --download

  # Filter high-impact papers before download
  python -m scitex.scholar --bibtex papers.bib --project important \\
      --min-citations 100 --min-impact-factor 10.0 --download

  # Force re-download all PDFs (refresh)
  python -m scitex.scholar --bibtex papers.bib --project myresearch --download-force

  # List papers in a project
  python -m scitex.scholar --project myresearch --list

  # Search and export
  python -m scitex.scholar --project myresearch --search "neural" --export neural_papers.bib

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
    input_group = parser.add_argument_group(
        "Input Sources",
        "Specify papers to process (can combine with operations)",
    )
    input_group.add_argument(
        "--bibtex",
        type=str,
        metavar="FILE",
        help="Path to BibTeX file containing paper references",
    )
    input_group.add_argument(
        "--doi",
        type=str,
        metavar="DOI",
        help='Single DOI to process (e.g., "10.1038/nature12373")',
    )
    input_group.add_argument(
        "--dois",
        type=str,
        nargs="+",
        metavar="DOI",
        help="Multiple DOIs to process (space-separated)",
    )
    input_group.add_argument(
        "--title",
        type=str,
        help="Paper title for DOI resolution or library search",
    )

    # Project management
    project_group = parser.add_argument_group(
        "Project Management", "Organize papers in persistent project libraries"
    )
    project_group.add_argument(
        "--project",
        "-p",
        type=str,
        metavar="NAME",
        help="Project name for organizing papers (stored in ~/.scitex/scholar/library/PROJECT)",
    )
    project_group.add_argument(
        "--project-description",
        type=str,
        help="Optional project description (project created automatically when needed)",
    )

    # Operations
    ops_group = parser.add_argument_group(
        "Operations", "Actions to perform (can combine multiple)"
    )
    ops_group.add_argument(
        "--enrich",
        "-e",
        action="store_true",
        default=True,
        help="Enrich papers with metadata (DOIs, abstracts, citations, impact factors) [Default: True when loading BibTeX]",
    )
    ops_group.add_argument(
        "--no-enrich",
        dest="enrich",
        action="store_false",
        help="Skip enrichment step (not recommended if you need DOIs for download)",
    )
    ops_group.add_argument(
        "--download",
        "-d",
        action="store_true",
        help="Download PDFs to MASTER library with project symlinks (skips already downloaded PDFs)",
    )
    ops_group.add_argument(
        "--download-force",
        action="store_true",
        help="Force re-download all PDFs, even if already downloaded (refresh)",
    )
    ops_group.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all papers in specified project",
    )
    ops_group.add_argument(
        "--search",
        "-s",
        type=str,
        metavar="QUERY",
        help="Search papers by title, author, or keyword",
    )
    ops_group.add_argument(
        "--stats",
        action="store_true",
        help="Display library statistics (projects, papers, storage)",
    )
    ops_group.add_argument(
        "--deduplicate",
        action="store_true",
        help="Find and merge duplicate papers in MASTER library",
    )
    ops_group.add_argument(
        "--deduplicate-dry-run",
        action="store_true",
        help="Preview what deduplication would do without making changes",
    )

    # Export options
    export_group = parser.add_argument_group(
        "Export Options", "Save results in various formats"
    )
    export_group.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export project papers to file (format inferred from extension: .bib, .csv, .json)",
    )
    export_group.add_argument(
        "--output",
        "-o",
        type=str,
        metavar="FILE",
        help="Output file path for enriched data",
    )

    # Filtering options
    filter_group = parser.add_argument_group(
        "Filtering Options", "Filter papers before operations"
    )
    filter_group.add_argument(
        "--year-min", type=int, help="Minimum publication year (e.g., 2020)"
    )
    filter_group.add_argument(
        "--year-max", type=int, help="Maximum publication year (e.g., 2024)"
    )
    filter_group.add_argument(
        "--min-citations", type=int, help="Minimum citation count required"
    )
    filter_group.add_argument(
        "--min-impact-factor",
        type=float,
        help="Minimum journal impact factor (JCR 2024)",
    )
    filter_group.add_argument(
        "--has-pdf",
        action="store_true",
        help="Only include papers with downloaded PDFs",
    )

    # System options
    system_group = parser.add_argument_group(
        "System Options", "Control execution behavior"
    )
    system_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed debug output and error traces",
    )
    system_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable URL caching (forces fresh lookups)",
    )
    system_group.add_argument(
        "--browser",
        nargs="?",
        const="manual",
        choices=["stealth", "interactive", "manual"],
        default="stealth",
        help="Browser mode: 'stealth'=hidden downloads, 'interactive'=visible downloads, 'manual'=open browser for manual downloading with auto-linking (use alone without --download)",
    )
    system_group.add_argument(
        "--stop-download",
        action="store_true",
        help="Stop all running Scholar downloads and browser instances",
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

    # Warn if using both enrich and download together
    if args.enrich and (args.download or args.download_force):
        logger.warning("Using --enrich and --download together")
        logger.warning(
            "RECOMMENDED: Run as two separate steps for better reliability:"
        )
        logger.warning(
            "  Step 1: python -m scitex.scholar --bibtex input.bib --output enriched.bib --project PROJECT --enrich"
        )
        logger.warning(
            "  Step 2: python -m scitex.scholar --bibtex enriched.bib --project PROJECT --download"
        )

    # Set download flag if download_force is used
    if args.download_force:
        args.download = True

        # Disable URL finder cache when forcing downloads to retry previously failed URLs
        import os

        os.environ["SCITEX_SCHOLAR_USE_CACHE_PDF_DOWNLOADER"] = "false"
        logger.info("Download force enabled: URL finder cache disabled")

    # Apply filters if specified
    if any(
        [
            args.year_min,
            args.year_max,
            args.min_citations,
            args.min_impact_factor,
            args.has_pdf,
        ]
    ):
        papers = papers.filter(
            year_min=args.year_min,
            year_max=args.year_max,
            min_citations=args.min_citations,
            min_impact_factor=args.min_impact_factor,
            has_pdf=args.has_pdf if args.has_pdf else None,
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
            output_path = (
                bibtex_path.parent / f"{bibtex_path.stem}_enriched.bib"
            )

        scholar.save_papers_as_bibtex(papers, output_path)
        logger.success(f"Saved enriched BibTeX to: {output_path}")

    # Save to library if project specified (creates symlinks before download)
    if args.project:
        logger.info(f"Saving to project: {args.project}")
        saved_ids = scholar.save_papers_to_library(papers)
        logger.info(
            f"Saved {len(saved_ids)} papers to library with symlinks created"
        )

    # Download PDFs if requested (after library save so symlinks exist)
    if args.download:
        dois = [p.metadata.id.doi for p in papers if p.metadata.id.doi]
        if dois:
            logger.info(f"Downloading PDFs for {len(dois)} papers...")
            results = await scholar.download_pdfs_from_dois_async(dois)
            logger.info(
                f"Downloaded: {results['downloaded']}, Failed: {results['failed']}"
            )
        else:
            logger.warning("No DOIs found for PDF download")

    # Save BibTeX files to project's info directory if needed
    if args.project:
        # Save BibTeX files to the project's info/bibtex directory
        library_dir = scholar.config.get_library_dir()
        project_bibtex_dir = library_dir / args.project / "info" / "bibtex"
        project_bibtex_dir.mkdir(parents=True, exist_ok=True)

        import shutil

        # Save the original input BibTeX
        if bibtex_path and bibtex_path.exists():
            original_filename = bibtex_path.name
            project_original_path = project_bibtex_dir / original_filename
            if (
                not project_original_path.exists()
                or project_original_path.samefile(bibtex_path) == False
            ):
                shutil.copy2(bibtex_path, project_original_path)
                logger.info(
                    f"Saved original BibTeX to project library: {project_original_path}"
                )

        # Save the enriched output BibTeX
        if args.output:
            output_filename = Path(args.output).name
            project_output_path = project_bibtex_dir / output_filename
            if (
                not project_output_path.exists()
                or project_output_path.samefile(Path(args.output)) == False
            ):
                shutil.copy2(args.output, project_output_path)
                logger.info(
                    f"Saved enriched BibTeX to project library: {project_output_path}"
                )

        # Create/update merged.bib with all BibTeX files in the project
        from scitex.scholar.storage.BibTeXHandler import BibTeXHandler

        bibtex_handler = BibTeXHandler(
            project=args.project, config=scholar.config
        )

        # Get all BibTeX files in the project directory
        bibtex_files = list(project_bibtex_dir.glob("*.bib"))
        # Exclude merged.bib itself if it exists
        bibtex_files = [f for f in bibtex_files if f.name != "merged.bib"]

        if bibtex_files:
            merged_path = project_bibtex_dir / "merged.bib"
            # Use the merge_bibtex_files method which handles duplicates and adds separators
            merged_papers = bibtex_handler.merge_bibtex_files(bibtex_files)
            bibtex_handler.papers_to_bibtex(merged_papers, merged_path)
            logger.info(
                f"Created merged.bib from {len(bibtex_files)} BibTeX files with {len(merged_papers)} unique papers: {merged_path}"
            )

            # Create bibliography.bib symlink at project root pointing to merged.bib
            bibliography_link = library_dir / args.project / "bibliography.bib"
            if bibliography_link.exists():
                bibliography_link.unlink()  # Remove existing link/file

            # Create relative symlink: bibliography.bib -> info/bibtex/merged.bib
            bibliography_link.symlink_to("info/bibtex/merged.bib")
            logger.info(f"Created bibliography.bib symlink at project root")

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
        logger.info(
            f"Downloaded: {results['downloaded']}, Failed: {results['failed']}"
        )

    # Enrich if requested (create Papers from DOIs first)
    if args.enrich:
        from scitex.scholar.core.Paper import Paper
        from scitex.scholar.core.Papers import Papers

        papers_list = []
        for doi in dois:
            p = Paper()
            p.metadata.id.doi = doi
            papers_list.append(p)
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

    # Projects are auto-created when needed, no need for explicit creation

    # Open manual browser for downloading with auto-linking
    if args.browser == "manual" and not args.download:
        # Run in subprocess to avoid asyncio event loop conflict
        import subprocess
        import sys

        cmd = [
            sys.executable,
            "-m",
            "scitex.scholar.cli.open_browser_auto",
            "--project",
            args.project,
        ]

        # Add flags based on args
        if args.has_pdf is False:
            cmd.append("--all")

        logger.info(
            f"Opening browser with auto-tracking for project: {args.project}"
        )
        result = subprocess.run(cmd)
        return result.returncode

    # Download PDFs for papers in project
    if args.download:
        papers = scholar.load_project(args.project)
        logger.info(f"Loading papers from project: {args.project}")
        logger.info(f"Found {len(papers)} papers")

        # Filter to papers with DOIs that don't already have PDFs (unless --download-force)
        dois_to_download = []
        for paper in papers:
            # Check if DOI exists (non-empty string)
            if paper.metadata.id.doi and paper.metadata.id.doi.strip():
                # Check if PDF already exists
                has_pdf = (
                    paper.metadata.path.pdfs
                    and len(paper.metadata.path.pdfs) > 0
                )

                # Download if: no PDF OR download_force flag is set
                if not has_pdf or args.download_force:
                    dois_to_download.append(paper.metadata.id.doi)
            elif (
                not paper.metadata.path.pdfs
                or len(paper.metadata.path.pdfs) == 0
            ):
                # Paper has no DOI and no PDF - mark as failed with explanation
                from scitex.scholar.storage._LibraryManager import (
                    LibraryManager,
                )

                library_manager = LibraryManager(
                    config=scholar.config, project=args.project
                )

                paper_id = paper.container.scitex_id
                master_dir = (
                    scholar.config.path_manager.get_library_master_dir()
                )
                paper_dir = master_dir / paper_id
                paper_dir.mkdir(parents=True, exist_ok=True)

                # Create marker and log
                attempted_marker = paper_dir / ".download_attempted"
                download_log = paper_dir / "download_log.txt"

                if not attempted_marker.exists():
                    attempted_marker.touch()
                    from datetime import datetime

                    with open(attempted_marker, "w") as f:
                        f.write(
                            f"Download attempted at: {datetime.now().isoformat()}\n"
                        )

                if not download_log.exists():
                    from datetime import datetime

                    title = paper.metadata.basic.title or "Unknown"
                    with open(download_log, "w") as f:
                        f.write(f"Download Log\n")
                        f.write(f"{'=' * 60}\n")
                        f.write(f"Paper: {title}\n")
                        f.write(f"Paper ID: {paper_id}\n")
                        f.write(f"Started at: {datetime.now().isoformat()}\n")
                        f.write(f"\nSTATUS: NO DOI AVAILABLE\n")
                        f.write(f"Cannot download PDF without a DOI.\n")
                        f.write(f"{'=' * 60}\n")

                logger.warning(f"Skipping paper {paper_id}: No DOI available")

        if dois_to_download:
            if args.download_force:
                logger.info(
                    f"Force re-downloading PDFs for {len(dois_to_download)} papers..."
                )
            else:
                logger.info(
                    f"Downloading PDFs for {len(dois_to_download)} papers without PDFs..."
                )
            results = await scholar.download_pdfs_from_dois_async(
                dois_to_download
            )
            logger.info(
                f"Download complete: {results['downloaded']} downloaded, {results['failed']} failed"
            )
        else:
            logger.info(
                "    All papers in project already have PDFs or no DOIs available"
            )

        return 0

    # List papers in project
    if args.list:
        papers = scholar.load_project(args.project)

        # Count PDF statuses by checking symlinks
        library_dir = scholar.config.get_library_dir()
        project_dir = library_dir / args.project

        # Count different PDF statuses from symlinks
        pdf_counts = {
            "PDF-0p": 0,  # Pending
            "PDF-1r": 0,  # Running
            "PDF-2f": 0,  # Failed
            "PDF-3s": 0,  # Success
        }

        if project_dir.exists():
            for item in project_dir.iterdir():
                if item.is_symlink():
                    symlink_name = item.name
                    # Extract PDF status from symlink name (format: CC_XXXXXX-PDF-X-IF_XXX-...)
                    if "PDF-0p" in symlink_name:
                        pdf_counts["PDF-0p"] += 1
                    elif "PDF-1r" in symlink_name:
                        pdf_counts["PDF-1r"] += 1
                    elif "PDF-2f" in symlink_name:
                        pdf_counts["PDF-2f"] += 1
                    elif "PDF-3s" in symlink_name:
                        pdf_counts["PDF-3s"] += 1

        total_papers = len(papers)

        # Display summary statistics
        logger.info(f"\nProject: {args.project}")
        logger.info(f"Papers: {total_papers}")
        logger.info("")
        logger.info("PDF Status:")
        logger.success(f"  ✓ Downloaded (PDF-3s): {pdf_counts['PDF-3s']}")
        logger.error(f"  ✗ Failed (PDF-2f):     {pdf_counts['PDF-2f']}")
        logger.warning(f"  ⧗ Pending (PDF-0p):    {pdf_counts['PDF-0p']}")
        logger.info(f"  ⟳ Running (PDF-1r):    {pdf_counts['PDF-1r']}")

        # Calculate coverage
        if total_papers > 0:
            coverage = (pdf_counts["PDF-3s"] / total_papers) * 100
            logger.info(
                f"\nCoverage: {pdf_counts['PDF-3s']}/{total_papers} ({coverage:.1f}%)"
            )

        logger.info("")

        # Show paper details
        for i, paper in enumerate(papers[:20], 1):  # Show first 20
            title = paper.metadata.basic.title or "No title"
            title = title[:60] + "..." if len(title) > 60 else title
            info = []
            if paper.metadata.basic.year:
                info.append(str(paper.metadata.basic.year))
            if paper.metadata.id.doi:
                info.append(paper.metadata.id.doi)

            # Determine PDF status from symlink in project directory
            pdf_status = "✗ No status"
            scholar_id = paper.container.scitex_id

            # Find symlink containing this scholar_id
            if project_dir.exists():
                for item in project_dir.iterdir():
                    if item.is_symlink() and item.resolve().name == scholar_id:
                        symlink_name = item.name
                        if "PDF-3s" in symlink_name:
                            pdf_status = "✓ PDF"
                        elif "PDF-2f" in symlink_name:
                            pdf_status = "✗ Failed"
                        elif "PDF-0p" in symlink_name:
                            pdf_status = "⧗ Pending"
                        elif "PDF-1r" in symlink_name:
                            pdf_status = "⟳ Running"
                        break

            info.append(pdf_status)

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
            title = paper.metadata.basic.title or "No title"
            if len(title) > 60:
                title = title[:60] + "..."
            year = paper.metadata.basic.year or "n/a"
            print(f"{i:3d}. {title} ({year})")

    # Export project
    if args.export:
        papers = scholar.load_project(args.project)

        # Export path is the value of --export argument
        output_path = Path(args.export)

        # Infer format from extension
        extension = output_path.suffix.lower()

        if extension in [".bib", ".bibtex"]:
            scholar.save_papers_as_bibtex(papers, output_path)
        elif extension == ".csv":
            # TODO: Implement CSV export
            logger.warning("CSV export not yet implemented")
            return 1
        elif extension == ".json":
            import json

            with open(output_path, "w") as f:
                json.dump(
                    [p.to_dict() for p in papers], f, indent=2, default=str
                )
        else:
            logger.error(f"Unsupported export format: {extension}")
            logger.info(
                "    Supported formats: .bib, .bibtex, .json, .csv (coming soon)"
            )
            return 1

        logger.success(f"Exported {len(papers)} papers to: {output_path}")

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

    # Handle stop-download command
    if args.stop_download:
        import subprocess
        import signal
        import os

        logger.info(
            "    Stopping all Scholar downloads and browser instances..."
        )

        # Kill Chrome/Chromium processes (redirect stderr to suppress permission warnings)
        try:
            result = subprocess.run(
                ["pkill", "-f", "chrome"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=False,
            )
            # Only warn if there was a real error (not just permission denied)
            if result.returncode not in [
                0,
                1,
            ]:  # 0=killed, 1=no processes found
                stderr_text = result.stderr.decode("utf-8", errors="ignore")
                if (
                    stderr_text
                    and "Operation not permitted" not in stderr_text
                ):
                    logger.warning(
                        f"Issue stopping Chrome: {stderr_text.strip()}"
                    )

            result = subprocess.run(
                ["pkill", "-f", "chromium"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=False,
            )
            logger.info("✓ Stopped browser instances")
        except Exception as e:
            logger.debug(f"Error stopping browsers: {e}")

        # Kill python processes running scholar download
        try:
            result = subprocess.run(
                ["pkill", "-f", "python.*scholar.*download"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=False,
            )
            if result.returncode not in [0, 1]:
                stderr_text = result.stderr.decode("utf-8", errors="ignore")
                if (
                    stderr_text
                    and "Operation not permitted" not in stderr_text
                ):
                    logger.warning(
                        f"Issue stopping Scholar processes: {stderr_text.strip()}"
                    )
            logger.info("✓ Stopped Scholar download processes")
        except Exception as e:
            logger.debug(f"Error stopping scholar processes: {e}")

        # Kill Xvfb displays
        try:
            result = subprocess.run(
                ["pkill", "Xvfb"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=False,
            )
            if result.returncode not in [0, 1]:
                stderr_text = result.stderr.decode("utf-8", errors="ignore")
                if (
                    stderr_text
                    and "Operation not permitted" not in stderr_text
                ):
                    logger.warning(
                        f"Issue stopping Xvfb: {stderr_text.strip()}"
                    )
            logger.info("✓ Stopped virtual displays")
        except Exception as e:
            logger.debug(f"Error stopping Xvfb: {e}")

        logger.success("All Scholar processes stopped")
        return 0

    # Initialize Scholar
    from scitex.scholar.core.Scholar import Scholar

    # Initialize Scholar with project and optional description
    scholar = (
        Scholar(
            project=args.project,
            project_description=(
                args.project_description
                if hasattr(args, "project_description")
                else None
            ),
        )
        if args.project
        else Scholar()
    )

    # Update symlinks when project is specified (ensures metadata is current)
    if args.project:
        try:
            from scitex.scholar.storage._LibraryManager import LibraryManager

            library_manager = LibraryManager(
                config=scholar.config, project=args.project
            )

            # Quick symlink update (only regenerates if needed)
            master_dir = scholar.config.path_manager.get_library_master_dir()
            project_dir = scholar.config.path_manager.get_library_dir(
                args.project
            )

            if master_dir.exists() and project_dir.exists():
                # Get all papers in this project
                paper_dirs = [d for d in master_dir.iterdir() if d.is_dir()]
                updated = 0

                for paper_dir in paper_dirs:
                    metadata_file = paper_dir / "metadata.json"
                    if not metadata_file.exists():
                        continue

                    # Check if this paper belongs to the project
                    import json

                    with open(metadata_file) as f:
                        metadata = json.load(f)

                    projects = metadata.get("container", {}).get(
                        "projects", []
                    )
                    if args.project not in projects:
                        continue

                    # Extract metadata for readable name generation
                    meta_section = metadata.get("metadata", {})
                    basic = meta_section.get("basic", {})
                    publication = meta_section.get("publication", {})

                    authors = basic.get("authors")
                    year = basic.get("year")
                    journal = publication.get("journal")

                    # Generate and update symlink
                    readable_name = library_manager._generate_readable_name(
                        comprehensive_metadata=metadata,
                        master_storage_path=paper_dir,
                        authors=authors,
                        year=year,
                        journal=journal,
                    )

                    library_manager._create_project_symlink(
                        master_storage_path=paper_dir,
                        project=args.project,
                        readable_name=readable_name,
                    )
                    updated += 1

                # Only log if symlinks were updated (silent if no changes)
                # Moved to Scholar class in the future for cleaner separation
        except Exception as e:
            logger.debug(f"Symlink update skipped: {e}")

    try:
        # Route to appropriate handler based on input
        if args.bibtex:
            return await handle_bibtex_operations(args, scholar)

        elif args.doi or args.dois:
            return await handle_doi_operations(args, scholar)

        elif args.project:
            return await handle_project_operations(args, scholar)

        elif args.deduplicate or args.deduplicate_dry_run:
            # Run deduplication
            from scitex.scholar.storage._DeduplicationManager import (
                DeduplicationManager,
            )

            dedup_manager = DeduplicationManager(config=scholar.config)
            dry_run = args.deduplicate_dry_run

            if dry_run:
                logger.info(
                    "    Running deduplication in DRY RUN mode - no changes will be made"
                )

            stats = dedup_manager.deduplicate_library(dry_run=dry_run)

            # Report results
            logger.info("\nDeduplication Summary:")
            logger.info(f"  Duplicate groups found: {stats['groups_found']}")
            logger.info(f"  Total duplicates: {stats['duplicates_found']}")

            if not dry_run:
                logger.info(
                    f"  Duplicates merged: {stats['duplicates_merged']}"
                )
                logger.info(f"  Directories removed: {stats['dirs_removed']}")
                if stats.get("broken_symlinks_removed", 0) > 0:
                    logger.info(
                        f"  Broken symlinks cleaned: {stats['broken_symlinks_removed']}"
                    )
                if stats["errors"] > 0:
                    logger.warning(f"  Errors encountered: {stats['errors']}")

            if stats["duplicates_found"] == 0:
                logger.success("✓ No duplicates found - library is clean!")
            elif dry_run:
                logger.info(
                    f"\nRun with --deduplicate to merge {stats['duplicates_found']} duplicates"
                )
            else:
                logger.success(
                    f"✓ Successfully merged {stats['duplicates_merged']} duplicates"
                )

        elif args.stats:
            # Show library statistics
            stats = scholar.get_library_statistics()
            print("\n📊 Scholar Library Statistics")
            print("=" * 40)
            print(f"Total projects: {stats['total_projects']}")
            print(f"Total papers: {stats['total_papers']}")
            print(f"Storage: {stats['storage_mb']:.1f} MB")
            print(f"Library path: {stats['library_path']}")

            if stats["projects"]:
                print("\n📁 Projects:")
                for project in stats["projects"]:
                    print(
                        f"  - {project['name']}: {project['papers_count']} papers"
                    )

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
    import signal
    import atexit

    # Register cleanup handlers
    atexit.register(cleanup_scholar_processes)
    signal.signal(signal.SIGINT, cleanup_scholar_processes)
    signal.signal(signal.SIGTERM, cleanup_scholar_processes)

    try:
        sys.exit(asyncio.run(main_async()))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        cleanup_scholar_processes()
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        cleanup_scholar_processes()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF
