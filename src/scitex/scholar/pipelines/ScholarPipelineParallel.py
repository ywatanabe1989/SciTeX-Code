#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 06:13:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelineParallel.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelineParallel.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Orchestrates parallel paper acquisition using multiple browser profiles
  - Distributes DOI/title queries across N workers (default: 4)
  - Each worker uses ScholarPipelineSingle with dedicated chrome profile
  - Supports resumable processing (skips completed papers)
  - Pre-authenticates once before spawning workers

Dependencies:
  - packages:
    - playwright
    - asyncio

IO:
  - input-files:
    - None (starts from queries or Papers collection)

  - output-files:
    - library/MASTER/{paper_id}/metadata.json (multiple papers)
    - library/MASTER/{paper_id}/main.pdf (multiple papers)
    - library/{project}/{paper_id} -> ../MASTER/{paper_id} (multiple symlinks)
"""

"""Imports"""
import argparse
import asyncio
from typing import List, Optional

from scitex import logging
from scitex.browser.core import ChromeProfileManager
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.core import Paper
from scitex.scholar.pipelines.ScholarPipelineSingle import (
    ScholarPipelineSingle,
)

logger = logging.getLogger(__name__)

"""Functions & Classes"""
class ScholarPipelineParallel:
    """Orchestrates parallel paper acquisition using multiple workers"""

    def __init__(
        self,
        num_workers: int = 4,
        browser_mode: str = "stealth",
        base_chrome_profile: str = "system",
    ):
        """Initialize parallel pipeline.

        Args:
            num_workers: Number of parallel workers (default: 4)
            browser_mode: Browser mode for all workers ('stealth' or 'interactive')
            base_chrome_profile: Base chrome profile to sync from (default: 'system')
        """
        self.name = self.__class__.__name__
        self.num_workers = num_workers
        self.browser_mode = browser_mode
        self.base_chrome_profile = base_chrome_profile

        logger.info(
            f"{self.name}: Initialized with {num_workers} workers, mode={browser_mode}"
        )

    async def _verify_authentication_async(self) -> bool:
        """Pre-verify authentication once before spawning workers.

        Returns:
            True if authenticated, False otherwise
        """
        logger.info(f"{self.name}: Verifying authentication...")
        auth_manager = ScholarAuthManager()

        try:
            await auth_manager.ensure_authenticate_async()
            is_authenticated = await auth_manager.is_authenticate_async(
                verify_live=True
            )

            if is_authenticated:
                logger.success(f"{self.name}: Authentication verified")
                return True
            else:
                logger.error(
                    f"{self.name}: Authentication failed - workers will not have access"
                )
                return False

        except Exception as e:
            logger.error(
                f"{self.name}: Authentication verification failed: {e}"
            )
            return False

    def _prepare_worker_profiles(self, num_workers: int = None) -> List[str]:
        """Prepare chrome profiles for each worker by syncing from base profile.

        Args:
            num_workers: Number of workers to prepare (defaults to self.num_workers)

        Returns:
            List of worker profile names
        """
        workers_to_prepare = (
            num_workers if num_workers is not None else self.num_workers
        )

        logger.info(
            f"{self.name}: Preparing {workers_to_prepare} worker profiles from '{self.base_chrome_profile}'..."
        )

        worker_profiles = []
        for i in range(workers_to_prepare):
            worker_profile_name = f"{self.base_chrome_profile}_worker_{i}"
            worker_profiles.append(worker_profile_name)

            # Sync from base profile using ChromeProfileManager
            profile_manager = ChromeProfileManager(worker_profile_name)
            success = profile_manager.sync_from_profile(
                self.base_chrome_profile
            )

            if success:
                logger.debug(
                    f"{self.name}: Worker {i}: Profile synced successfully"
                )
            else:
                logger.warning(
                    f"{self.name}: Worker {i}: Profile sync failed, will create fresh profile"
                )

        logger.success(
            f"{self.name}: All worker profiles prepared: {', '.join(worker_profiles)}"
        )
        return worker_profiles

    async def _process_paper_with_worker_async(
        self,
        doi_or_title: str,
        project: Optional[str],
        worker_id: int,
        worker_profile: str,
    ) -> Optional[Paper]:
        """Process a single paper using a dedicated worker.

        Args:
            doi_or_title: DOI or title string
            project: Project name for symlinking
            worker_id: Worker ID for logging
            worker_profile: Chrome profile name for this worker

        Returns:
            Paper object if successful, None otherwise
        """
        logger.info(
            f"{self.name}: Worker {worker_id}: Processing '{doi_or_title[:50]}...'"
        )

        try:
            # Create dedicated pipeline for this worker
            pipeline = ScholarPipelineSingle(
                browser_mode=self.browser_mode,
                chrome_profile=worker_profile,
            )

            # Process paper using single pipeline
            paper = await pipeline.process_single_paper(
                doi_or_title=doi_or_title,
                project=project,
            )

            logger.success(
                f"{self.name}: Worker {worker_id}: Completed '{doi_or_title[:50]}...'"
            )
            return paper

        except Exception as e:
            logger.error(
                f"{self.name}: Worker {worker_id}: Failed '{doi_or_title[:50]}...': {e}"
            )
            return None

    async def process_papers_from_list_async(
        self,
        doi_or_title_list: List[str],
        project: Optional[str] = None,
    ) -> List[Paper]:
        """Process multiple papers in parallel from a list of DOIs/titles.

        Args:
            doi_or_title_list: List of DOI or title strings
            project: Project name for symlinking (optional)

        Returns:
            List of successfully processed Paper objects
        """
        if not doi_or_title_list:
            logger.warning(
                f"{self.name}: Empty input list, nothing to process"
            )
            return []

        total = len(doi_or_title_list)

        # Cap workers by number of papers (no point having more workers than papers)
        effective_workers = min(self.num_workers, total)

        logger.info(
            f"{self.name}: Starting parallel processing of {total} papers with {effective_workers} workers"
        )

        # Step 1: Verify authentication once
        authenticated = await self._verify_authentication_async()
        if not authenticated:
            logger.error(
                f"{self.name}: Authentication failed - aborting parallel processing"
            )
            return []

        # Step 2: Prepare worker profiles (only as many as needed)
        worker_profiles = self._prepare_worker_profiles(
            num_workers=effective_workers
        )

        # Step 3: Create task queue with semaphore for concurrency control
        semaphore = asyncio.Semaphore(effective_workers)

        async def process_with_semaphore(
            doi_or_title: str, index: int
        ) -> Optional[Paper]:
            """Process one paper with semaphore control."""
            async with semaphore:
                worker_id = index % self.num_workers
                worker_profile = worker_profiles[worker_id]

                logger.info(
                    f"{self.name}: [{index + 1}/{total}] Assigned to Worker {worker_id}"
                )

                return await self._process_paper_with_worker_async(
                    doi_or_title=doi_or_title,
                    project=project,
                    worker_id=worker_id,
                    worker_profile=worker_profile,
                )

        # Step 4: Create tasks for all papers
        tasks = [
            process_with_semaphore(doi_or_title, i)
            for i, doi_or_title in enumerate(doi_or_title_list)
        ]

        # Step 5: Process with controlled parallelism
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Step 6: Filter successful results
        processed_papers = []
        errors = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"{self.name}: Paper {i + 1} raised exception: {result}"
                )
                errors += 1
            elif result is not None:
                processed_papers.append(result)

        # Summary
        logger.info(f"\n{'=' * 60}")
        logger.info(f"{self.name}: Parallel Processing Complete")
        logger.info(f"  Total: {total}")
        logger.info(f"  Successful: {len(processed_papers)}")
        logger.info(f"  Failed: {total - len(processed_papers)}")
        logger.info(f"  Errors: {errors}")
        logger.info(f"  Workers: {self.num_workers}")
        logger.info(f"{'=' * 60}\n")

        return processed_papers

    async def process_papers_from_collection_async(
        self,
        papers: "Papers",
        project: Optional[str] = None,
    ) -> List[Paper]:
        """Process multiple papers in parallel from a Papers collection.

        Args:
            papers: Papers collection
            project: Project name for symlinking (optional, uses papers.project if None)

        Returns:
            List of successfully processed Paper objects
        """
        # Extract DOIs or titles from papers
        doi_or_title_list = []
        for paper in papers:
            if paper.metadata.id.doi:
                doi_or_title_list.append(paper.metadata.id.doi)
            elif paper.metadata.basic.title:
                doi_or_title_list.append(paper.metadata.basic.title)
            else:
                logger.warning(
                    f"{self.name}: Paper has no DOI or title, skipping"
                )

        # Use project from Papers collection if not specified
        if project is None and hasattr(papers, "project"):
            project = papers.project

        return await self.process_papers_from_list_async(
            doi_or_title_list=doi_or_title_list,
            project=project,
        )


def main(args):
    """Run parallel pipeline"""

    # Parse input queries
    queries = []
    if args.dois:
        queries.extend(args.dois.split(","))
    if args.titles:
        queries.extend(args.titles.split(","))

    if not queries:
        logger.error("No queries provided. Use --dois or --titles")
        return 1

    logger.info(
        f"Processing {len(queries)} queries with {args.num_workers} workers"
    )

    # Create parallel pipeline
    parallel_pipeline = ScholarPipelineParallel(
        num_workers=args.num_workers,
        browser_mode=args.browser_mode,
        base_chrome_profile=args.chrome_profile,
    )

    # Run pipeline
    papers = asyncio.run(
        parallel_pipeline.process_papers_from_list_async(
            doi_or_title_list=queries,
            project=args.project,
        )
    )

    logger.success(
        f"Parallel processing complete: {len(papers)} papers processed"
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Orchestrate parallel paper acquisition pipeline"
    )
    parser.add_argument(
        "--dois",
        type=str,
        default=None,
        help="Comma-separated DOIs (e.g., '10.1038/...,10.1016/...')",
    )
    parser.add_argument(
        "--titles",
        type=str,
        default=None,
        help="Comma-separated paper titles",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for symlinking (optional)",
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
    # With DOIs (4 workers)
    python -m scitex.scholar.pipelines.ScholarPipelineParallel \
        --dois "10.1212/wnl.0000000000200348,10.1038/s41598-017-02626-y" \
        --project neurovista \
        --num-workers 4 \
        --browser-mode stealth \
        --chrome-profile system

    # With titles (2 workers)
    python -m scitex.scholar.pipelines.ScholarPipelineParallel \
        --titles "Attention Is All You Need,BERT: Pre-training of Deep Bidirectional Transformers" \
        --project transformers \
        --num-workers 2 \
        --browser-mode stealth \
        --chrome-profile system

    # Mixed DOIs and titles (8 workers)
    python -m scitex.scholar.pipelines.ScholarPipelineParallel \
        --dois "10.1038/s41593-025-01990-7" \
        --titles "Neural State Monitoring in the Treatment of Epilepsy" \
        --project epilepsy \
        --num-workers 8 \
        --browser-mode stealth \
        --chrome-profile system
"""

# EOF
