#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 06:01:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelinePaper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelinePaper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import argparse

"""
Functionalities:
  - Complete sequential pipeline for processing a single paper
  - Resolves DOI from title if needed
  - Creates/loads Paper object from storage (storage-first approach)
  - Finds PDF URLs for the paper
  - Downloads PDF from discovered URLs
  - Updates project symlinks

Dependencies:
  - packages:
    - scitex
    - playwright
    - pydantic

IO:
  - input-files:
    - ~/.scitex/scholar/library/MASTER/{paper_id}/metadata.json (if exists)
  - output-files:
    - ~/.scitex/scholar/library/MASTER/{paper_id}/metadata.json
    - ~/.scitex/scholar/library/MASTER/{paper_id}/main.pdf
    - ~/.scitex/scholar/library/{project}/{readable_name} -> ../MASTER/{paper_id}
"""

"""Imports"""
from typing import Optional

from scitex import logging

from ._ScholarPipelineBase import ScholarPipelineBase

logger = logging.getLogger(__name__)

"""Functions & Classes"""
class ScholarPipelinePaper(ScholarPipelineBase):
    """
    Complete sequential pipeline for processing a single paper.

    Workflow:
      Stage 0: Resolve DOI from title (if needed)
      Stage 1: Load or create Paper from storage
      Stage 2: Find PDF URLs → save to storage
      Stage 3: Download PDF → save to storage
      Stage 4: Update project symlinks

    Uses storage-first approach: checks storage before each stage.
    """

    async def run(
        self,
        title: Optional[str] = None,
        doi: Optional[str] = None,
        project: Optional[str] = None,
    ) -> "Paper":
        """
        Process a single paper through complete workflow.

        Args:
            title: Paper title (will resolve DOI using engine)
            doi: DOI of the paper (preferred if available)
            project: Project name for symlink creation

        Returns:
            Fully processed Paper object

        Examples:
            # With DOI (direct)
            pipeline = PaperProcessingPipeline()
            paper = await pipeline.run(doi="10.1038/s41598-017-02626-y")

            # With title (resolves DOI first)
            paper = await pipeline.run(title="Attention Is All You Need")
        """
        from scitex.scholar.core.Paper import Paper
        from scitex.scholar.url_finder import ScholarURLFinder
        from scitex.scholar.pdf_download import ScholarPDFDownloader

        # Validate input
        if not title and not doi:
            raise ValueError("Must provide either title or doi")

        logger.info(f"{'='*60}")
        logger.info(f"{self.name}: Processing paper")
        if title:
            logger.info(f"Title: {title[:50]}...")
        if doi:
            logger.info(f"DOI: {doi}")
        logger.info(f"{'='*60}")

        # Stage 0: Resolve DOI from title (if needed)
        if not doi and title:
            logger.info(f"Stage 0: Resolving DOI from title...")
            results = await self.scholar_engine.search_async(title=title)

            if results and results.get("id", {}).get("doi"):
                doi = results["id"]["doi"]
                logger.success(f"Resolved DOI: {doi}")
            else:
                logger.error(f"Could not resolve DOI from title: {title}")
                raise ValueError(f"Could not resolve DOI from title: {title}")

        # Generate paper ID from DOI
        paper_id = self.config.path_manager._generate_paper_id(doi=doi)
        storage_path = self.config.get_library_master_dir() / paper_id

        logger.info(f"Paper ID: {paper_id}")
        logger.info(f"Storage: {storage_path}")

        # Stage 1: Load or create Paper from storage
        logger.info(f"\nStage 1: Loading/creating metadata...")
        if self.library_manager.has_metadata(paper_id):
            paper = self.library_manager.load_paper_from_id(paper_id)
            logger.info(f"Loaded existing metadata from storage")
        else:
            paper = Paper()
            paper.metadata.set_doi(doi)
            paper.container.scitex_id = paper_id

            if title:
                paper.metadata.basic.title = title

            self.library_manager.save_paper_incremental(paper_id, paper)
            logger.success(f"Created new paper entry in storage")

        # Stage 2: Check/find URLs
        logger.info(f"\nStage 2: Checking/finding PDF URLs...")
        if not self.library_manager.has_urls(paper_id):
            logger.info(f"Finding PDF URLs for DOI: {doi}")
            browser, context = (
                await self.browser_manager.get_authenticated_browser_and_context_async()
            )
            try:
                url_finder = ScholarURLFinder(context, config=self.config)
                urls = await url_finder.find_pdf_urls(doi)

                paper.metadata.url.pdfs = urls
                self.library_manager.save_paper_incremental(paper_id, paper)
                logger.success(f"Found {len(urls)} PDF URLs, saved to storage")
            finally:
                await self.browser_manager.close()
        else:
            logger.info(
                f"PDF URLs already in storage ({len(paper.metadata.url.pdfs)} URLs)"
            )

        # Stage 3: Check/download PDF
        logger.info(f"\nStage 3: Checking/downloading PDF...")
        if not self.library_manager.has_pdf(paper_id):
            logger.info(f"Downloading PDF...")
            if paper.metadata.url.pdfs:
                browser, context = (
                    await self.browser_manager.get_authenticated_browser_and_context_async()
                )
                try:
                    downloader = ScholarPDFDownloader(
                        context, config=self.config
                    )

                    pdf_url = (
                        paper.metadata.url.pdfs[0]["url"]
                        if isinstance(paper.metadata.url.pdfs[0], dict)
                        else paper.metadata.url.pdfs[0]
                    )
                    temp_path = storage_path / "main.pdf"

                    result = await downloader.download_from_url(
                        pdf_url, temp_path, doi=doi
                    )
                    if result and result.exists():
                        paper.metadata.path.pdfs.append(str(result))
                        self.library_manager.save_paper_incremental(
                            paper_id, paper
                        )
                        logger.success(f"Downloaded PDF, saved to storage")
                    else:
                        logger.warning(f"Failed to download PDF")
                finally:
                    await self.browser_manager.close()
            else:
                logger.warning(f"No PDF URLs available for download")
        else:
            logger.info(f"PDF already in storage")

        # Stage 4: Update project symlinks
        if project and project not in ["master", "MASTER"]:
            logger.info(f"\nStage 4: Updating project symlinks...")
            self.library_manager.update_symlink(
                master_storage_path=storage_path,
                project=project,
            )
            logger.success(f"Updated symlink in project: {project}")

        logger.info(f"\n{'='*60}")
        logger.success(f"Paper processing complete")
        logger.info(f"{'='*60}\n")

        return paper


def main(args):
    """Run single paper processing pipeline"""
    import asyncio

    if not args.doi and not args.title:
        logger.error("Must provide either --doi or --title")
        return 1

    logger.info(f"Processing paper:")
    if args.doi:
        logger.info(f"  DOI: {args.doi}")
    if args.title:
        logger.info(f"  Title: {args.title}")
    logger.info(f"  Project: {args.project or 'None'}")

    # Create pipeline
    pipeline = ScholarPipelinePaper()

    # Run pipeline
    paper = asyncio.run(
        pipeline.run(
            title=args.title,
            doi=args.doi,
            project=args.project,
        )
    )

    logger.success(f"Paper processing complete")
    return 0


def parse_args() -> "argparse.Namespace":
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process a single paper through complete workflow"
    )
    parser.add_argument(
        "--doi",
        type=str,
        default=None,
        help="DOI of the paper",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Title of the paper (will resolve DOI)",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for symlink creation",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

"""
Usage Examples:
    # Process paper by DOI
    python -m scitex.scholar.pipelines.ScholarPipelinePaper \
        --doi 10.1038/s41598-017-02626-y \
        --project my_project

    # Process paper by title (resolves DOI first)
    python -m scitex.scholar.pipelines.ScholarPipelinePaper \
        --title "Attention Is All You Need" \
        --project ml_papers

    # Library usage (recommended)
    from scitex.scholar.pipelines import ScholarPipelinePaper
    pipeline = ScholarPipelinePaper()
    paper = await pipeline.run(doi="10.1038/...")
"""

# EOF
