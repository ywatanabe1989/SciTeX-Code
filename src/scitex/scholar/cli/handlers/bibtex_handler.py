#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/cli/handlers/bibtex_handler.py

"""Handler for BibTeX file operations."""

from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)


async def handle_bibtex_operations(args, scholar):
    """Handle operations on BibTeX files."""
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

        os.environ["SCITEX_SCHOLAR_USE_CACHE_DOWNLOAD"] = "false"
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
        library_dir = scholar.config.get_library_project_dir()
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


# EOF
