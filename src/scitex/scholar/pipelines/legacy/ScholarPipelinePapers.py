#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-12 01:22:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelinePapers.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelinePapers.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Process multiple papers with controlled parallelism
  - Each paper goes through complete PaperProcessingPipeline
  - Semaphore controls concurrent paper processing
  - Storage-first approach (checks before each stage)
  - Provides batch processing statistics

Dependencies:
  - packages:
    - scitex
    - playwright
    - pydantic
  - scripts:
    - ./paper_processing.py (PaperProcessingPipeline)

IO:
  - input-files:
    - Papers collection or list of DOIs
    - ~/.scitex/scholar/library/MASTER/{paper_id}/metadata.json (per paper, if exists)
  - output-files:
    - ~/.scitex/scholar/library/MASTER/{paper_id}/metadata.json (per paper)
    - ~/.scitex/scholar/library/MASTER/{paper_id}/main.pdf (per paper)
    - ~/.scitex/scholar/library/{project}/{readable_name} -> ../MASTER/{paper_id} (per paper)
"""

"""Imports"""
import asyncio
from typing import List, Optional, Union

from scitex import logging

from ._ScholarPipelineBase import ScholarPipelineBase
from .ScholarPipelinePaper import ScholarPipelinePaper

logger = logging.getLogger(__name__)

"""Functions & Classes"""


class ScholarPipelinePapers(ScholarPipelineBase):
    """
    Process multiple papers with controlled parallelism.

    Architecture:
      - Parallel papers (max_concurrent at a time)
      - Sequential stages per paper
      - Storage checks before each stage

    Each paper goes through the complete PaperProcessingPipeline.
    Semaphore controls how many papers process concurrently.
    """

    async def run(
        self,
        papers: Union["Papers", List[str]],
        project: Optional[str] = None,
        max_concurrent: int = 3,
    ) -> "Papers":
        """
        Process multiple papers with controlled parallelism.

        Args:
            papers: Papers collection or list of DOIs
            project: Project name for symlink creation
            max_concurrent: Maximum concurrent papers (default: 3)
                           Set to 1 for purely sequential processing

        Returns:
            Papers collection with processed papers

        Examples:
            # Process Papers collection (parallel)
            pipeline = BatchProcessingPipeline()
            papers = Papers.from_bibtex("papers.bib")
            processed = await pipeline.run(papers, max_concurrent=3)

            # Process DOI list (sequential)
            dois = ["10.1038/...", "10.1016/...", "10.1109/..."]
            processed = await pipeline.run(dois, max_concurrent=1)
        """
        from scitex.scholar.core.Papers import Papers
        from scitex.scholar.core.Paper import Paper

        # Convert input to Papers collection
        if isinstance(papers, list):
            # List of DOI strings
            papers_list = []
            for doi in papers:
                p = Paper()
                p.metadata.set_doi(doi)
                papers_list.append(p)
            papers = Papers(papers_list, project=project, config=self.config)

        total = len(papers)
        logger.info(f"\n{'='*60}")
        logger.info(
            f"{self.name}: Processing {total} papers (max_concurrent={max_concurrent})"
        )
        logger.info(f"Project: {project}")
        logger.info(f"{'='*60}\n")

        # Use semaphore for controlled parallelism
        semaphore = asyncio.Semaphore(max_concurrent)

        # Create single paper pipeline instance
        paper_pipeline = ScholarPipelinePaper(config=self.config)

        async def process_with_semaphore(paper, index):
            """Process one paper with semaphore control."""
            async with semaphore:
                logger.info(f"\n[{index}/{total}] Starting paper...")
                try:
                    result = await paper_pipeline.run(
                        title=paper.metadata.basic.title,
                        doi=paper.metadata.id.doi,
                        project=project,
                    )
                    logger.success(f"[{index}/{total}] Completed")
                    return result
                except Exception as e:
                    logger.error(f"[{index}/{total}] Failed: {e}")
                    return None

        # Create tasks for all papers
        tasks = [
            process_with_semaphore(paper, i + 1)
            for i, paper in enumerate(papers)
        ]

        # Process with controlled parallelism
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        processed_papers = []
        errors = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Paper {i+1} raised exception: {result}")
                errors += 1
            elif result is not None:
                processed_papers.append(result)

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"{self.name}: Batch Processing Complete")
        logger.info(f"  Total: {total}")
        logger.info(f"  Successful: {len(processed_papers)}")
        logger.info(f"  Failed: {total - len(processed_papers)}")
        logger.info(f"  Errors: {errors}")
        logger.info(f"{'='*60}\n")

        return Papers(processed_papers, project=project, config=self.config)


def main(args):
    """Run batch paper processing pipeline"""
    import asyncio
    from scitex.scholar.core.Paper import Paper
    from scitex.scholar.core.Papers import Papers

    if not args.dois:
        logger.error("No DOIs provided. Use --dois")
        return 1

    dois = args.dois.split(",")
    logger.info(f"Processing {len(dois)} papers:")
    logger.info(f"  DOIs: {len(dois)} papers")
    logger.info(f"  Project: {args.project or 'None'}")
    logger.info(f"  Max concurrent: {args.max_concurrent}")

    # Create Papers collection from DOIs
    papers_list = []
    for doi in dois:
        p = Paper()
        p.metadata.set_doi(doi.strip())
        papers_list.append(p)

    papers = Papers(papers_list, project=args.project)

    # Create pipeline
    pipeline = ScholarPipelinePapers()

    # Run pipeline
    processed = asyncio.run(
        pipeline.run(
            papers=papers,
            project=args.project,
            max_concurrent=args.max_concurrent,
        )
    )

    logger.success(
        f"Papers processing complete: {len(processed)}/{len(papers)} papers"
    )
    return 0


def parse_args() -> "argparse.Namespace":
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process multiple papers with controlled parallelism"
    )
    parser.add_argument(
        "--dois",
        type=str,
        required=True,
        help="Comma-separated list of DOIs",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for symlink creation",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent papers (default: 3)",
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
    # Process multiple papers with parallelism
    python -m scitex.scholar.pipelines.ScholarPipelinePapers \
        --dois "10.1038/...,10.1016/...,10.1109/..." \
        --project my_project \
        --max-concurrent 3

    # Sequential processing (max-concurrent=1)
    python -m scitex.scholar.pipelines.ScholarPipelinePapers \
        --dois "10.1038/...,10.1016/..." \
        --project test \
        --max-concurrent 1

    # Library usage (recommended)
    from scitex.scholar.pipelines import ScholarPipelinePapers
    pipeline = ScholarPipelinePapers()
    papers = await pipeline.run(dois=["10.1038/...", "10.1016/..."])
"""

# EOF
