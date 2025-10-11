#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 22:56:36 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/ScholarPipelineBibTeX.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/ScholarPipelineBibTeX.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Processes BibTeX files through parallel paper acquisition pipeline
  - Loads papers from BibTeX parallel download update BibTeX with results
  - Supports resumable processing (skips already downloaded papers)
  - Updates BibTeX with enriched metadata and download status

Dependencies:
  - packages:
    - playwright
    - asyncio

IO:
  - input-files:
    - BibTeX files (.bib)

  - output-files:
    - library/MASTER/{paper_id}/metadata.json (multiple papers)
    - library/MASTER/{paper_id}/main.pdf (multiple papers)
    - library/{project}/{paper_id} -> ../MASTER/{paper_id} (multiple symlinks)
    - {input_bibtex}_processed.bib (enriched BibTeX with download status)
"""

"""Imports"""
import argparse
import asyncio
from pathlib import Path
from typing import Optional, Union

from scitex import logging
from scitex.scholar.core import Papers
from scitex.scholar.core.ScholarPipelineParallel import ScholarPipelineParallel
from scitex.scholar.storage import BibTeXHandler

logger = logging.getLogger(__name__)

"""Functions & Classes"""
class ScholarPipelineBibTeX:
    """Processes BibTeX files through parallel paper acquisition pipeline"""

    def __init__(
        self,
        num_workers: int = 4,
        browser_mode: str = "stealth",
        base_chrome_profile: str = "system",
    ):
        """Initialize BibTeX pipeline.

        Args:
            num_workers: Number of parallel workers (default: 4)
            browser_mode: Browser mode for all workers ('stealth' or 'interactive')
            base_chrome_profile: Base chrome profile to sync from (default: 'system')
        """
        self.name = self.__class__.__name__
        self.num_workers = num_workers
        self.browser_mode = browser_mode
        self.base_chrome_profile = base_chrome_profile

        # Initialize parallel pipeline
        self.parallel_pipeline = ScholarPipelineParallel(
            num_workers=num_workers,
            browser_mode=browser_mode,
            base_chrome_profile=base_chrome_profile,
        )

        logger.info(
            f"{self.name}: Initialized with {num_workers} workers, mode={browser_mode}"
        )

    async def process_bibtex_file_async(
        self,
        bibtex_path: Union[str, Path],
        project: Optional[str] = None,
        output_bibtex_path: Optional[Union[str, Path]] = None,
    ) -> Papers:
        """Process all papers from a BibTeX file in parallel.

        Args:
            bibtex_path: Path to input BibTeX file
            project: Project name for symlinking (optional)
            output_bibtex_path: Path to save enriched BibTeX (optional, defaults to {input}_processed.bib)

        Returns:
            Papers collection with processed papers
        """
        bibtex_path = Path(bibtex_path)
        if not bibtex_path.exists():
            raise FileNotFoundError(f"BibTeX file not found: {bibtex_path}")

        logger.info(f"{self.name}: Processing BibTeX file: {bibtex_path}")

        # Step 1: Load papers from BibTeX
        bibtex_handler = BibTeXHandler(project=project)
        papers = bibtex_handler.papers_from_bibtex(bibtex_path)

        if not papers:
            logger.warning(f"{self.name}: No papers found in BibTeX file")
            return Papers([], project=project)

        logger.info(f"{self.name}: Loaded {len(papers)} papers from BibTeX")

        # Step 2: Process papers in parallel using ScholarPipelineParallel
        papers_collection = Papers(papers, project=project)
        processed_papers = (
            await self.parallel_pipeline.process_papers_from_collection_async(
                papers=papers_collection,
                project=project,
            )
        )

        # Step 3: Save enriched BibTeX with processing results
        if output_bibtex_path is None:
            # Default: save as {input}_processed.bib
            output_bibtex_path = (
                bibtex_path.parent / f"{bibtex_path.stem}_processed.bib"
            )
        else:
            output_bibtex_path = Path(output_bibtex_path)

        # Convert processed papers to Papers collection
        processed_collection = Papers(processed_papers, project=project)

        # Save enriched BibTeX
        bibtex_handler.papers_to_bibtex(
            processed_collection,
            output_path=output_bibtex_path,
        )

        logger.success(
            f"{self.name}: Processed {len(processed_papers)}/{len(papers)} papers"
        )
        logger.success(
            f"{self.name}: Saved enriched BibTeX: {output_bibtex_path}"
        )

        return processed_collection

    async def process_bibtex_text_async(
        self,
        bibtex_text: str,
        project: Optional[str] = None,
        output_bibtex_path: Optional[Union[str, Path]] = None,
    ) -> Papers:
        """Process papers from BibTeX text content in parallel.

        Args:
            bibtex_text: BibTeX content as string
            project: Project name for symlinking (optional)
            output_bibtex_path: Path to save enriched BibTeX (optional)

        Returns:
            Papers collection with processed papers
        """
        logger.info(f"{self.name}: Processing BibTeX text content")

        # Step 1: Load papers from BibTeX text
        bibtex_handler = BibTeXHandler(project=project)
        papers = bibtex_handler.papers_from_bibtex(bibtex_text)

        if not papers:
            logger.warning(f"{self.name}: No papers found in BibTeX text")
            return Papers([], project=project)

        logger.info(
            f"{self.name}: Loaded {len(papers)} papers from BibTeX text"
        )

        # Step 2: Process papers in parallel
        papers_collection = Papers(papers, project=project)
        processed_papers = (
            await self.parallel_pipeline.process_papers_from_collection_async(
                papers=papers_collection,
                project=project,
            )
        )

        # Step 3: Save enriched BibTeX if path provided
        processed_collection = Papers(processed_papers, project=project)

        if output_bibtex_path:
            output_bibtex_path = Path(output_bibtex_path)
            bibtex_handler.papers_to_bibtex(
                processed_collection,
                output_path=output_bibtex_path,
            )
            logger.success(
                f"{self.name}: Saved enriched BibTeX: {output_bibtex_path}"
            )

        logger.success(
            f"{self.name}: Processed {len(processed_papers)}/{len(papers)} papers"
        )

        return processed_collection


def main(args):
    """Run BibTeX pipeline"""

    if not args.bibtex:
        logger.error("No BibTeX file provided. Use --bibtex")
        return 1

    bibtex_path = Path(args.bibtex)
    if not bibtex_path.exists():
        logger.error(f"BibTeX file not found: {bibtex_path}")
        return 1

    logger.info(f"Processing BibTeX file: {bibtex_path}")
    logger.info(f"Workers: {args.num_workers}")
    logger.info(f"Project: {args.project or 'None'}")

    # Create BibTeX pipeline
    bibtex_pipeline = ScholarPipelineBibTeX(
        num_workers=args.num_workers,
        browser_mode=args.browser_mode,
        base_chrome_profile=args.chrome_profile,
    )

    # Run pipeline
    papers = asyncio.run(
        bibtex_pipeline.process_bibtex_file_async(
            bibtex_path=bibtex_path,
            project=args.project,
            output_bibtex_path=args.output,
        )
    )

    logger.success(
        f"BibTeX processing complete: {len(papers)} papers processed"
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process BibTeX files through parallel paper acquisition pipeline"
    )
    parser.add_argument(
        "--bibtex",
        type=str,
        required=True,
        help="Path to BibTeX file",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for symlinking (optional)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output BibTeX path (default: {input}_processed.bib)",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["stealth", "interactive"],
        default="stealth",
        help="Browser mode (default: stealth)",
    )
    parser.add_argument(
        "--chrome-profile",
        type=str,
        default="system",
        help="Base Chrome profile name to sync from (default: system)",
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
Usage:
    # Process BibTeX file with 4 workers
    python -m scitex.scholar.core.ScholarPipelineBibTeX \
        --bibtex src/scitex/scholar/data/neurovista.bib \
        --project neurovista \
        --num-workers 8 \
        --browser-mode stealth \
        --chrome-profile system

    # Process with custom output path (8 workers)
    python -m scitex.scholar.core.ScholarPipelineBibTeX \
        --bibtex papers.bib \
        --project my_project \
        --output papers_enriched.bib \
        --num-workers 8 \
        --browser-mode stealth \
        --chrome-profile system

    # Process with 2 workers (interactive mode for debugging)
    python -m scitex.scholar.core.ScholarPipelineBibTeX \
        --bibtex papers.bib \
        --project test \
        --num-workers 2 \
        --browser-mode interactive \
        --chrome-profile system
"""

# EOF
