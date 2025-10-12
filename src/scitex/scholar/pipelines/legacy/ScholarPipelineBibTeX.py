#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 05:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelineBibTeX.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelineBibTeX.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Processes BibTeX files through parallel paper acquisition pipeline
  - Loads papers from BibTeX file
  - Processes papers in parallel (metadata, URLs, PDFs)
  - Updates BibTeX with processing results
  - Manages project bibliography structure

Dependencies:
  - packages:
    - scitex
    - playwright
    - asyncio
  - scripts:
    - ./BatchProcessingPipeline.py

IO:
  - input-files:
    - BibTeX files (.bib)
  - output-files:
    - library/MASTER/{paper_id}/metadata.json (multiple papers)
    - library/MASTER/{paper_id}/main.pdf (multiple papers)
    - library/{project}/{paper_id} -> ../MASTER/{paper_id} (multiple symlinks)
    - {input_bibtex}_processed.bib (enriched BibTeX)
    - library/{project}/info/bibliography/combined.bib
"""

"""Imports"""
import asyncio
from pathlib import Path
from typing import Optional, Union

from scitex import logging

from ._ScholarPipelineBase import ScholarPipelineBase
from .ScholarPipelinePapers import ScholarPipelinePapers

logger = logging.getLogger(__name__)

"""Functions & Classes"""


class ScholarPipelineBibTeX(ScholarPipelineBase):
    """
    Process BibTeX files through parallel paper acquisition pipeline.

    Workflow:
      1. Load papers from BibTeX file
      2. Process papers in parallel (metadata, URLs, PDFs)
      3. Save enriched BibTeX with results
      4. Update project bibliography structure

    This pipeline combines BibTeX import with parallel paper processing.
    """

    def __init__(
        self,
        config=None,
        num_workers: int = 4,
        browser_mode: str = "stealth",
    ):
        """Initialize BibTeX import pipeline.

        Args:
            config: ScholarConfig instance
            num_workers: Number of parallel workers (default: 4)
            browser_mode: Browser mode ('stealth' or 'interactive')
        """
        super().__init__(config=config)
        self.num_workers = num_workers
        self.browser_mode = browser_mode

    async def run(
        self,
        bibtex_path: Union[str, Path],
        project: Optional[str] = None,
        output_bibtex_path: Optional[Union[str, Path]] = None,
    ) -> "Papers":
        """Process all papers from a BibTeX file in parallel.

        Args:
            bibtex_path: Path to input BibTeX file
            project: Project name for library organization
            output_bibtex_path: Path for enriched BibTeX (default: {input}_processed.bib)

        Returns:
            Papers collection with processed papers

        Examples:
            pipeline = BibTeXImportPipeline(num_workers=8)
            papers = await pipeline.run(
                bibtex_path="papers.bib",
                project="my_project"
            )
        """
        from scitex.scholar.core import Papers
        from scitex.scholar.storage import BibTeXHandler

        bibtex_path = Path(bibtex_path)
        if not bibtex_path.exists():
            raise FileNotFoundError(f"BibTeX file not found: {bibtex_path}")

        logger.info(f"{self.name}: Processing BibTeX file: {bibtex_path}")
        logger.info(f"Workers: {self.num_workers}")
        logger.info(f"Project: {project or 'None'}")

        # Step 1: Load papers from BibTeX
        bibtex_handler = BibTeXHandler(project=project, config=self.config)
        papers = bibtex_handler.papers_from_bibtex(bibtex_path)

        if not papers:
            logger.warning(f"{self.name}: No papers found in BibTeX file")
            return Papers([], project=project)

        logger.info(f"{self.name}: Loaded {len(papers)} papers from BibTeX")

        # Step 2: Process papers in parallel using ScholarPipelinePapers
        papers_collection = Papers(papers, project=project)
        papers_pipeline = ScholarPipelinePapers(config=self.config)

        processed_papers = await papers_pipeline.run(
            papers=papers_collection,
            project=project,
            max_concurrent=self.num_workers,
        )

        # Step 3: Save enriched BibTeX with processing results
        if output_bibtex_path is None:
            output_bibtex_path = (
                bibtex_path.parent / f"{bibtex_path.stem}_processed.bib"
            )
        else:
            output_bibtex_path = Path(output_bibtex_path)

        bibtex_handler.papers_to_bibtex(
            processed_papers,
            output_path=output_bibtex_path,
        )

        logger.success(
            f"{self.name}: Processed {len(processed_papers)}/{len(papers)} papers"
        )
        logger.success(
            f"{self.name}: Saved enriched BibTeX: {output_bibtex_path}"
        )

        # Step 4: Update project bibliography structure
        if project:
            try:
                bibtex_handler.setup_project_bibliography(
                    project=project,
                    bibtex_files=[bibtex_path, output_bibtex_path]
                )
                logger.success(
                    f"{self.name}: Updated project bibliography: {project}"
                )
            except Exception as e:
                logger.warning(f"Failed to update bibliography: {e}")

        return processed_papers


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
    pipeline = ScholarPipelineBibTeX(
        num_workers=args.num_workers,
        browser_mode=args.browser_mode,
    )

    # Run pipeline
    papers = asyncio.run(
        pipeline.run(
            bibtex_path=bibtex_path,
            project=args.project,
            output_bibtex_path=args.output,
        )
    )

    logger.success(
        f"BibTeX processing complete: {len(papers)} papers processed"
    )
    return 0


def parse_args() -> "argparse.Namespace":
    """Parse command line arguments."""
    import argparse

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
    # Process BibTeX file with 8 workers
    python -m scitex.scholar.pipelines.ScholarPipelineBibTeX \
        --bibtex ./data/scholar/bib_files/neurovista.bib \
        --project neurovista \
        --num-workers 8 \
        --browser-mode stealth

    # Process with custom output path
    python -m scitex.scholar.pipelines.ScholarPipelineBibTeX \
        --bibtex papers.bib \
        --project my_project \
        --output papers_enriched.bib \
        --num-workers 8

    # Process with 2 workers for debugging
    python -m scitex.scholar.pipelines.ScholarPipelineBibTeX \
        --bibtex papers.bib \
        --project test \
        --num-workers 2 \
        --browser-mode interactive
"""

# EOF
