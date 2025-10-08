#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/cli/handlers/project_handler.py

"""Handler for project library operations."""

from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)


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


# EOF
