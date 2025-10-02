#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 09:31:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/resolvers/_BatchDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from pathlib import Path

import time
from typing import Tuple

"""Enhanced resumable DOI resolver with focused single-responsibility components."""

import asyncio
from difflib import SequenceMatcher
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage import LibraryManager
from scitex.scholar.utils._progress_display import ProgressDisplay

from ..batch import MetadataHandlerForBatchDOIResolution
from ..batch import ProgressManagerForBatchDOIResolution
from ..batch import SourceStatsManagerForBatchDOIResolution
from ._SingleDOIResolver import SingleDOIResolver

logger = logging.getLogger(__name__)


class BatchDOIResolver:
    """Enhanced DOI resolver with better performance and user experience.

    Features:
    - Smart rate limiting with adaptive delays
    - Concurrent resolution with configurable worker_asyncs
    - Deduplication of similar titles
    - Intelligent retry strategies
    - Real-time rsync-like progress with accurate ETA
    - Automatic resume from any interruption
    - Memory of successful sources per paper type

    Now uses focused single-responsibility components:
    - ProgressManagerForBatchDOIResolution: Progress tracking and persistence
    - MetadataHandlerForBatchDOIResolution: Paper metadata processing and validation
    - SourceStatsManagerForBatchDOIResolution: Configuration resolution and validation
    - LibraryManager: Scholar library organization and management
    """

    def __init__(
        self,
        project: str = None,
        doi_resolution_progress_file: Optional[Path] = None,
        max_worker: Optional[int] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize enhanced resolver with dependency injection.

        Args:
            doi_resolution_progress_file: Path to progress file (auto-generated if None)
            max_worker: Number of concurrent worker_asyncs
            config: ScholarConfig instance
            progress_manager: ProgressManagerForBatchDOIResolution instance (created if None)
            metadata_enhancer: MetadataHandlerForBatchDOIResolution instance (created if None)
            source_stats_manager: SourceStatsManagerForBatchDOIResolution instance (created if None)
            library_manager: LibraryManager instance (created if None)
        """
        # Initialize configuration manager first
        self.config = config or ScholarConfig()
        self.source_stats_manager = SourceStatsManagerForBatchDOIResolution(
            config
        )

        # Use SingleDOIResolver composition for core DOI resolution
        self.single_doi_resolver = SingleDOIResolver(
            config=self.config, project=project
        )

        # Project
        self.project = self.config.resolve("project", project)

        # Resolve max worker_asyncs using configuration manager
        self.max_worker = self.config.resolve("max_worker", max_worker)

        # Initialize metadata enhancer first (needed for title normalizer)
        self.metadata_handler = MetadataHandlerForBatchDOIResolution()

        # Initialize progress manager
        doi_resolution_progress_path = (
            self.config.get_doi_resolution_progress_path(
                doi_resolution_progress_file
            )
        )

        self.progress_manager = ProgressManagerForBatchDOIResolution(
            doi_resolution_progress_path,
            title_normalizer=self.metadata_handler.normalize_title,
        )

        # Initialize library manager
        self.library_manager = LibraryManager(
            project=self.project,
            single_doi_resolver=self.single_doi_resolver,
            config=self.config,
        )

        # Set up backward compatibility properties
        self.doi_resolution_progress_file = (
            self.progress_manager.doi_resolution_progress_file
        )
        self.progress_data = self.progress_manager.progress_data
        self._start_time = self.progress_manager._start_time

        # Performance tracking (delegated to config manager)
        self._source_success_rates = (
            self.source_stats_manager._source_success_rates
        )

    # def bibtex2dois(
    #     self, bibtex_path: Path, sources: Optional[List[str]] = None
    # ) -> Dict[str, str]:
    #     """Resolve DOIs with enhanced performance."""

    #     # Load BibTeX
    #     bibtex_path = Path(bibtex_path)
    #     logger.info(f"Loading: {bibtex_path}")

    #     entries = load(str(bibtex_path))

    #     # Extract papers using metadata enhancer
    #     papers_metadata = []
    #     for entry in entries:
    #         fields = entry.get("fields", {})
    #         title = fields.get("title", "").strip()
    #         if not title:
    #             continue

    #         papers_metadata.append(
    #             {
    #                 "title": title,
    #                 "authors": self.metadata_handler.parse_authors(
    #                     fields.get("author", "")
    #                 ),
    #                 "year": self.metadata_handler.parse_year(
    #                     fields.get("year", "")
    #                 ),
    #                 "journal": fields.get("journal", ""),
    #                 "doi": fields.get("doi", ""),
    #             }
    #         )

    #     # Find duplicates using metadata enhancer
    #     # duplicate_groups = self.metadata_handler.find_similar_papers(
    #     duplicate_groups = self.find_similar_papers(papers_metadata)
    #     if duplicate_groups:
    #         self.progress_manager.progress_data["duplicate_groups"] = (
    #             duplicate_groups
    #         )

    #     # Update total
    #     self.progress_manager.set_total_papers(len(papers_metadata))
    #     self.progress_manager.save_progress()

    #     # Resolve DOIs
    #     return self.resolve_batch(papers_metadata, sources)

    async def papers2title_and_dois_async(
        self, papers: List[Dict[str, Any]], sources: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Resolve DOIs with enhanced batch processing."""
        results = {}

        # Filter out already processed papers using progress manager
        papers_to_process = []
        for paper in papers:
            title = paper.get("title", "")
            if not title:
                continue

            title_50 = title if len(title) < 50 else f"{title[:50]}..."
            if self.progress_manager.is_paper_processed(title):
                status = self.progress_manager.get_paper_status(title)
                if status and status.get("status") == "resolved":
                    results[title] = status["doi"]
                    logger.success(
                        f"DOI resolution for '{title_50}' was already resolved"
                    )
                else:
                    logger.success(
                        f"Skipping already resolved paper: {title_50}..."
                    )
                continue

            papers_to_process.append(paper)

        if not papers_to_process:
            logger.success("All papers already processed!")
            return results

        logger.info(
            f"Processing {len(papers_to_process)}/{len(papers)} papers "
            f"({len(papers) - len(papers_to_process)} already done)"
        )

        # Display progress during processing
        progress_display = ProgressDisplay(
            description="DOI Resolution Progress",
            total=len(papers_to_process),
        )

        tasks = []
        for ii_, paper in enumerate(papers_to_process):
            # Use metadata enhancer for duplicate detection
            similar_papers = [
                p_
                for p_ in papers_to_process
                if self.metadata_handler.get_paper_key(p_)
                == self.metadata_handler.get_paper_key(paper)
            ]
            if len(similar_papers) > 1:
                logger.warning(
                    f"Potential duplicate: {paper.get('title', '')[:50]}..."
                )

            tasks.append((paper, ii_, len(papers_to_process)))

        semaphore = asyncio.Semaphore(self.max_worker)

        async def bounded_resolve(paper, index):
            async with semaphore:
                # Use unified rate limiting system with adaptive delays
                delay = (
                    self.single_doi_resolver._rate_limit_handler.get_adaptive_delay()
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                    self.progress_manager.update_rate_limited()

                # Resolve single paper
                title, doi = await self._single_paper2title_and_doi_async(
                    paper, index, len(papers_to_process)
                )

                # Update progress display
                progress_display.update(1)

                # Save progress periodically
                if index % 5 == 0:
                    self.progress_manager.save_progress()
                    self.source_stats_manager.save_source_stats()

                return title, doi

        # Execute all tasks concurrently
        batch_results = await asyncio.gather(
            *[bounded_resolve(paper, ii_) for paper, ii_, _ in tasks]
        )

        # Collect results
        for title, doi in batch_results:
            if doi:
                results[title] = doi

        # Final progress save
        self.progress_manager.save_progress()
        self.source_stats_manager.save_source_stats()

        # Show summary using progress manager
        self._show_async_final_summary()

        return results

    def _get_title_normalizer(self):
        """Get title normalizer function for progress manager (deprecated - kept for compatibility)."""
        return (
            self.metadata_handler.normalize_title
            if hasattr(self, "metadata_enhancer")
            else None
        )

    def _get_optimal_sources(self, paper: Dict[str, Any]) -> List[str]:
        """Get sources ordered by likelihood of success."""
        # Start with default order
        sources = self.single_doi_resolver.sources.copy()

        # Use historical performance if available
        journal = paper.get("journal", "").lower()
        success_rate = self.source_stats_manager.get_source_success_rate(
            journal
        )
        if success_rate > 0:
            # Sort by success rate for this journal
            sources.sort(
                key=lambda s: self.source_stats_manager.get_source_success_rate(
                    s
                ),
                reverse=True,
            )

        return sources

    async def _single_paper2title_and_doi_async(
        self, paper: Dict[str, Any], index: int, total: int
    ) -> Tuple[str, Optional[str]]:
        """Resolve single paper asynchronously using SingleDOIResolver composition."""
        title = paper.get("title", "")
        if not title:
            return title, None

        # Get optimal source order
        sources = self._get_optimal_sources(paper)

        # Try resolution with adaptive timeout using SingleDOIResolver's caching
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                self.single_doi_resolver.metadata2doi_async(
                    title=title,
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                ),
                timeout=30,  # 30 second timeout
            )

            # Track success
            if result and isinstance(result, dict) and result.get("doi"):
                doi = result["doi"]
                elapsed = time.time() - start_time
                # Record success in unified rate limiting system
                self.single_doi_resolver._rate_limit_handler.record_request_outcome(
                    "batch_resolver", success=True
                )
                self.progress_manager.add_processing_time(elapsed)

                # Update source stats via config manager
                journal = paper.get("journal", "").lower()
                if result.get("source"):
                    self.source_stats_manager.update_source_stats(
                        result["source"], True
                    )

                # Update progress
                self.progress_manager.update_progress_success(title, doi)
                logger.success(f"DOI resolved: {title} -> {doi}")
                return title, doi
            else:
                # Record failure in unified rate limiting system
                self.single_doi_resolver._rate_limit_handler.record_request_outcome(
                    "batch_resolver", success=False
                )
                self.progress_manager.update_progress_failure(title)
                return title, None

        except asyncio.TimeoutError:
            logger.warning(f"Timeout resolving: {title[:50]}...")
            self.progress_manager.update_progress_failure(title)
            return title, None
        except Exception as e:
            logger.error(f"Error resolving '{title[:30]}...': {e}")
            self.progress_manager.update_progress_failure(title)
            return title, None

    def _show_async_final_summary(self):
        """Show enhanced final summary using progress manager."""
        summary = self.progress_manager.get_progress_summary()
        stats = self.progress_manager.progress_data["statistics"]

        logger.info("\n" + "=" * 50)
        logger.info("BATCH DOI RESOLUTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total papers: {stats['total']}")
        logger.info(f"Processed: {stats['processed']}")
        logger.info(f"Resolved: {stats['resolved']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Skipped: {stats['skipped']}")

        if stats["processed"] > 0:
            success_rate = stats["resolved"] / stats["processed"]
            logger.success(f"Success rate: {success_rate:.1%}")

        if stats["rate_limited"] > 0:
            logger.info(f"Rate limited: {stats['rate_limited']} times")

        eta = summary.get("eta")
        if eta:
            logger.info(f"ETA: {eta}")

        logger.success(
            f"Progress saved to: {self.progress_manager.doi_resolution_progress_file}"
        )
        logger.info("=" * 50)

    # Delegate methods to maintain backward compatibility

    def _get_paper_key(self, paper: Dict[str, Any]) -> str:
        """Generate unique key for paper (delegated to metadata enhancer)."""
        return self.metadata_handler.get_paper_key(paper)

    def _update_progress_success(self, title: str, doi: str):
        """Update progress for successful resolution (delegated)."""
        self.progress_manager.update_progress_success(title, doi)

    def _update_progress_failure(self, title: str):
        """Update progress for failed resolution (delegated)."""
        self.progress_manager.update_progress_failure(title)

    def _save_progress(self):
        """Save progress atomically (delegated)."""
        self.progress_manager.save_progress()

    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse BibTeX author string (delegated to metadata enhancer)."""
        return self.metadata_handler.parse_authors(authors_str)

    def _parse_year(self, year_str: str) -> Optional[int]:
        """Parse year from string (delegated to metadata enhancer)."""
        return self.metadata_handler.parse_year(year_str)

    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication (delegated to metadata enhancer)."""
        return self.metadata_handler.normalize_title(title)

    # def _find_similar_papers(
    #     self, papers: List[Dict[str, Any]]
    # ) -> Dict[str, List[int]]:
    #     """Find potentially duplicate papers (delegated to metadata enhancer)."""
    #     return self.metadata_handler.find_similar_papers(papers)

    # DOI validation methods (delegate to doi_resolver)
    def validate_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        return self.single_doi_resolver._validate_doi(doi)

    def text2dois(self, text: str) -> List[str]:
        """Extract DOI from text."""
        return self.single_doi_resolver.text2dois(text)

    # Library structure methods (delegate to library creator)
    def update_library_metadata(
        self,
        paper_id: str,
        project: str,
        doi: str,
        metadata: Dict[str, Any],
        create_structure: bool = True,
    ) -> bool:
        """Update Scholar library metadata.json with resolved DOI."""
        return self.library_manager.update_library_metadata(
            paper_id, project, doi, metadata, create_structure
        )

    def resolve_and_update_library(
        self,
        papers_with_ids: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Resolve DOIs and update Scholar library metadata.json files."""
        return self.library_manager.resolve_and_update_library(
            papers_with_ids, project, sources
        )

    async def resolve_and_create_library_structure_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Resolve DOIs and create full Scholar library structure with proper paths."""
        return await self.library_manager.resolve_and_create_library_structure_async(
            papers, project, sources
        )

    def resolve_and_create_library_structure(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Synchronous wrapper for resolve_and_create_library_structure_async."""
        return self.library_manager.resolve_and_create_library_structure(
            papers, project, sources
        )

    def find_similar_papers(
        self, papers: List[Dict[str, Any]], similarity_threshold: float = 0.85
    ) -> Dict[str, List[int]]:
        """Find potentially duplicate papers based on title similarity.

        Args:
            papers: List of paper dictionaries with 'title' field

        Returns:
            Dictionary mapping group IDs to lists of paper indices
        """
        duplicated_groups = {}
        processed = set()

        for i, paper1 in enumerate(papers):
            if i in processed:
                continue

            title1 = self._normalize_title(paper1.get("title", ""))
            if not title1:
                continue

            group = [i]
            for j, paper2 in enumerate(papers[i + 1 :], start=i + 1):
                if j in processed:
                    continue

                title2 = self._normalize_title(paper2.get("title", ""))
                if not title2:
                    continue

                # Check similarity
                similarity = SequenceMatcher(None, title1, title2).ratio()
                if similarity > similarity_threshold:
                    group.append(j)
                    processed.add(j)

            if len(group) > 1:
                group_key = f"group_{len(duplicated_groups) + 1}"
                duplicated_groups[group_key] = group
                logger.warning(
                    f"Found potential duplicates ({len(group)} papers): "
                    f"{[papers[idx].get('title', '')[:50] + '...' for idx in group[:2]]}"
                )

            processed.add(i)

        logger.info(
            f"Found {len(duplicated_groups)} duplicated_groups of similar papers"
        )
        return duplicated_groups


if __name__ == "__main__":
    import argparse
    import asyncio

    async def main():
        """Example usage of refactored BatchDOIResolver with comprehensive features."""

        from pathlib import Path

        from scitex.scholar.metadata.doi.resolvers._BatchDOIResolver import (
            BatchDOIResolver,
        )

        # Initialize resolver with custom configuration
        batch_doi_resolver = BatchDOIResolver(
            max_worker=3,  # Use 3 concurrent worker_asyncs
        )

        # Test papers
        test_papers = [
            {
                "title": "Machine Learning for Natural Language Processing",
                "year": "2023",
                "authors": "Smith, J. and Doe, A. and Johnson, B.",
                "journal": "Nature Machine Intelligence",
            },
            {
                "title": "Deep Learning Approaches in Computer Vision",
                "year": "2022",
                "authors": "Brown, C. and Davis, E.",
                "journal": "IEEE Computer Vision",
            },
        ]

        # Test batch resolution
        results = await batch_doi_resolver.papers2title_and_dois_async(
            test_papers[:1]
        )  # Test with 1 paper
        print(f"\nResults:\n{results}")

        # Show configuration summary
        config_summary = (
            batch_doi_resolver.source_stats_manager.get_configuration_summary()
        )
        print(f"\nConfig Summary:\n{config_summary}")

        # Show progress summary
        progress_summary = (
            batch_doi_resolver.progress_manager.get_progress_summary()
        )
        print(f"\nProgress Summary:\n{progress_summary}")

    asyncio.run(main())

# python -m scitex.scholar.metadata.doi.resolvers._BatchDOIResolver

# EOF
