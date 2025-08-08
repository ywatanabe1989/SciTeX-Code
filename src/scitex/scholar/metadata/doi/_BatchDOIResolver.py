#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 17:57:36 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/_BatchDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/_BatchDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Enhanced resumable DOI resolver with focused single-responsibility components."""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scitex import logging

from ...config import ScholarConfig
from ...utils._progress_display import ProgressDisplay
from ._SingleDOIResolver import SingleDOIResolver
from .batch import (
    BatchConfigurationManager,
    BatchProgressManager,
    LibraryStructureCreator,
    MetadataEnhancer,
)

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
    - BatchProgressManager: Progress tracking and persistence
    - MetadataEnhancer: Paper metadata processing and validation
    - BatchConfigurationManager: Configuration resolution and validation
    - LibraryStructureCreator: Scholar library organization and management
    """

    def __init__(
        self,
        progress_file: Optional[Path] = None,
        max_worker_asyncs: int = 4,
        cache_dir: Optional[Path] = None,
        config: Optional[ScholarConfig] = None,
        project: str = "default",
        # Dependency injection for testability and modularity
        progress_manager: Optional[BatchProgressManager] = None,
        metadata_enhancer: Optional[MetadataEnhancer] = None,
        config_manager: Optional[BatchConfigurationManager] = None,
        library_creator: Optional[LibraryStructureCreator] = None,
    ):
        """Initialize enhanced resolver with dependency injection.

        Args:
            progress_file: Path to progress file (auto-generated if None)
            max_worker_asyncs: Number of concurrent worker_asyncs
            cache_dir: Directory for caching DOI lookups
            config: ScholarConfig instance
            progress_manager: BatchProgressManager instance (created if None)
            metadata_enhancer: MetadataEnhancer instance (created if None)
            config_manager: BatchConfigurationManager instance (created if None)
            library_creator: LibraryStructureCreator instance (created if None)
        """
        # Initialize configuration manager first
        self.config_manager = config_manager or BatchConfigurationManager(
            config
        )
        self.config = self.config_manager.config

        # Use SingleDOIResolver composition for core DOI resolution
        self.doi_resolver = SingleDOIResolver(
            config=self.config, project=project
        )

        # Project
        self.project = project

        # Resolve max worker_asyncs using configuration manager
        self.max_worker_asyncs = self.config_manager.get_max_worker_asyncs(max_worker_asyncs)

        # Initialize metadata enhancer first (needed for title normalizer)
        self.metadata_enhancer = metadata_enhancer or MetadataEnhancer()

        # Initialize progress manager
        progress_file_path = self.config_manager.get_progress_file_path(
            progress_file
        )
        self.progress_manager = progress_manager or BatchProgressManager(
            progress_file_path,
            title_normalizer=self.metadata_enhancer.normalize_title,
        )

        # Initialize library creator
        self.library_creator = library_creator or LibraryStructureCreator(
            self.config, self.doi_resolver
        )

        # Set up backward compatibility properties
        self.progress_file = self.progress_manager.progress_file
        self.progress_data = self.progress_manager.progress_data
        self._start_time = self.progress_manager._start_time

        # Performance tracking (delegated to config manager)
        self._source_success_rates = self.config_manager._source_success_rates

    def _get_title_normalizer(self):
        """Get title normalizer function for progress manager (deprecated - kept for compatibility)."""
        return (
            self.metadata_enhancer.normalize_title
            if hasattr(self, "metadata_enhancer")
            else None
        )

    def _get_optimal_sources(self, paper: Dict[str, Any]) -> List[str]:
        """Get sources ordered by likelihood of success."""
        # Start with default order
        sources = self.doi_resolver.sources.copy()

        # Use historical performance if available
        journal = paper.get("journal", "").lower()
        success_rate = self.config_manager.get_source_success_rate(journal)
        if success_rate > 0:
            # Sort by success rate for this journal
            sources.sort(
                key=lambda s: self.config_manager.get_source_success_rate(s),
                reverse=True,
            )

        return sources

    async def _resolve_single_async(
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
                self.doi_resolver.resolve_async(
                    title=title,
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                    sources=sources[:3],  # Try top 3 sources only
                ),
                timeout=30,  # 30 second timeout
            )

            # Track success
            if result and isinstance(result, dict) and result.get("doi"):
                doi = result["doi"]
                elapsed = time.time() - start_time
                # Record success in unified rate limiting system
                self.doi_resolver.rate_limit_handler.record_request_outcome(
                    "batch_resolver", success=True
                )
                self.progress_manager.add_processing_time(elapsed)

                # Update source stats via config manager
                journal = paper.get("journal", "").lower()
                if result.get("source"):
                    self.config_manager.update_source_stats(
                        result["source"], True
                    )

                # Update progress
                self.progress_manager.update_progress_success(title, doi)
                logger.success(f"DOI resolved: {title} -> {doi}")
                return title, doi
            else:
                # Record failure in unified rate limiting system
                self.doi_resolver.rate_limit_handler.record_request_outcome(
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

    def resolve_from_bibtex(
        self, bibtex_path: Path, sources: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Resolve DOIs with enhanced performance."""
        from scitex.io import load

        # Load BibTeX
        bibtex_path = Path(bibtex_path)
        logger.info(f"Loading: {bibtex_path}")

        try:
            entries = load(str(bibtex_path))
            logger.info(
                f"Loaded {len(entries)} BibTeX entries from {bibtex_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load BibTeX: {e}")
            return {}

        # Extract papers using metadata enhancer
        papers_metadata = []
        for entry in entries:
            fields = entry.get("fields", {})
            title = fields.get("title", "").strip()
            if not title:
                continue

            papers_metadata.append(
                {
                    "title": title,
                    "authors": self.metadata_enhancer.parse_bibtex_authors(
                        fields.get("author", "")
                    ),
                    "year": self.metadata_enhancer.parse_year(
                        fields.get("year", "")
                    ),
                    "journal": fields.get("journal", ""),
                    "doi": fields.get("doi", ""),
                }
            )

        # Find duplicates using metadata enhancer
        duplicate_groups = self.metadata_enhancer.find_similar_papers(
            papers_metadata
        )
        if duplicate_groups:
            logger.info(
                f"Found {len(duplicate_groups)} groups of similar papers"
            )
            self.progress_manager.progress_data["duplicate_groups"] = (
                duplicate_groups
            )

        # Update total
        self.progress_manager.set_total_papers(len(papers_metadata))
        self.progress_manager.save_progress()

        # Resolve DOIs
        return self.resolve_batch(papers_metadata, sources)

    def resolve_batch(
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
                    logger.warn(f"Fixme: Skipping failed paper: {title_50}...")
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

        async def process_all():
            tasks = []
            for i, paper in enumerate(papers_to_process):
                # Use metadata enhancer for duplicate detection
                similar_papers = [
                    p
                    for p in papers_to_process
                    if self.metadata_enhancer.get_paper_key(p)
                    == self.metadata_enhancer.get_paper_key(paper)
                ]
                if len(similar_papers) > 1:
                    logger.warning(
                        f"Potential duplicate: {paper.get('title', '')[:50]}..."
                    )

                tasks.append((paper, i, len(papers_to_process)))

            semaphore = asyncio.Semaphore(self.max_worker_asyncs)

            async def bounded_resolve(paper, index):
                async with semaphore:
                    # Use unified rate limiting system with adaptive delays
                    delay = (
                        self.doi_resolver.rate_limit_handler.get_adaptive_delay()
                    )
                    if delay > 0:
                        await asyncio.sleep(delay)
                        self.progress_manager.update_rate_limited()

                    # Resolve single paper
                    title, doi = await self._resolve_single_async(
                        paper, index, len(papers_to_process)
                    )

                    # Update progress display
                    progress_display.update(
                        1,
                    )

                    # Save progress periodically
                    if index % 5 == 0:
                        self.progress_manager.save_progress()
                        self.config_manager.save_source_stats()

                    return title, doi

            # Execute all tasks concurrently
            batch_results = await asyncio.gather(
                *[bounded_resolve(paper, i) for paper, i, _ in tasks]
            )

            # Collect results
            for title, doi in batch_results:
                if doi:
                    results[title] = doi

        # Run async processing
        asyncio.run(process_all())

        # Final progress save
        self.progress_manager.save_progress()
        self.config_manager.save_source_stats()

        # Show summary using progress manager
        self._show_async_final_summary()

        return results

    def _show_async_final_summary(self):
        """Show enhanced final summary using progress manager."""
        summary = self.progress_manager.get_progress_summary()
        stats = self.progress_manager.progress_data["statistics"]

        logger.success("\n" + "=" * 50)
        logger.success("BATCH DOI RESOLUTION SUMMARY")
        logger.success("=" * 50)
        logger.success(f"Total papers: {stats['total']}")
        logger.success(f"Processed: {stats['processed']}")
        logger.success(f"Resolved: {stats['resolved']}")
        logger.success(f"Failed: {stats['failed']}")
        logger.success(f"Skipped: {stats['skipped']}")

        if stats["processed"] > 0:
            success_rate = stats["resolved"] / stats["processed"]
            logger.success(f"Success rate: {success_rate:.1%}")

        if stats["rate_limited"] > 0:
            logger.info(f"Rate limited: {stats['rate_limited']} times")

        eta = summary.get("eta")
        if eta:
            logger.info(f"ETA: {eta}")

        logger.success(
            f"Progress saved to: {self.progress_manager.progress_file}"
        )
        logger.success("=" * 50)

    # Delegate methods to maintain backward compatibility

    def _get_paper_key(self, paper: Dict[str, Any]) -> str:
        """Generate unique key for paper (delegated to metadata enhancer)."""
        return self.metadata_enhancer.get_paper_key(paper)

    def _update_progress_success(self, title: str, doi: str):
        """Update progress for successful resolution (delegated)."""
        self.progress_manager.update_progress_success(title, doi)

    def _update_progress_failure(self, title: str):
        """Update progress for failed resolution (delegated)."""
        self.progress_manager.update_progress_failure(title)

    def _save_progress(self):
        """Save progress atomically (delegated)."""
        self.progress_manager.save_progress()

    def _parse_bibtex_authors(self, authors_str: str) -> List[str]:
        """Parse BibTeX author string (delegated to metadata enhancer)."""
        return self.metadata_enhancer.parse_bibtex_authors(authors_str)

    def _parse_year(self, year_str: str) -> Optional[int]:
        """Parse year from string (delegated to metadata enhancer)."""
        return self.metadata_enhancer.parse_year(year_str)

    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication (delegated to metadata enhancer)."""
        return self.metadata_enhancer.normalize_title(title)

    def _find_similar_papers(
        self, papers: List[Dict[str, Any]]
    ) -> Dict[str, List[int]]:
        """Find potentially duplicate papers (delegated to metadata enhancer)."""
        return self.metadata_enhancer.find_similar_papers(papers)

    # DOI validation methods (delegate to doi_resolver)
    def validate_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        return self.doi_resolver.validate_doi(doi)

    def extract_dois_from_text(self, text: str) -> List[str]:
        """Extract DOIs from text."""
        return self.doi_resolver.extract_dois_from_text(text)

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
        return self.library_creator.update_library_metadata(
            paper_id, project, doi, metadata, create_structure
        )

    def resolve_and_update_library(
        self,
        papers_with_ids: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Resolve DOIs and update Scholar library metadata.json files."""
        return self.library_creator.resolve_and_update_library(
            papers_with_ids, project, sources
        )

    async def resolve_and_create_library_structure_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Resolve DOIs and create full Scholar library structure with proper paths."""
        return await self.library_creator.resolve_and_create_library_structure_async(
            papers, project, sources
        )

    def resolve_and_create_library_structure(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Synchronous wrapper for resolve_and_create_library_structure_async."""
        return self.library_creator.resolve_and_create_library_structure(
            papers, project, sources
        )


if __name__ == "__main__":
    import argparse
    import asyncio

    async def main():
        """Example usage of refactored BatchDOIResolver with comprehensive features."""

        from pathlib import Path

        from scitex.scholar import BatchDOIResolver

        # Initialize resolver with custom configuration
        resolver = BatchDOIResolver(
            max_worker_asyncs=3,  # Use 3 concurrent worker_asyncs
            progress_file=Path("./example_doi_progress.json"),
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
        results = resolver.resolve_batch(test_papers[:1])  # Test with 1 paper
        print(f"\nResults:\n{results}")

        # Show configuration summary
        config_summary = resolver.config_manager.get_configuration_summary()
        print(f"\nConfig Summary:\n{config_summary}")

        # Show progress summary
        progress_summary = resolver.progress_manager.get_progress_summary()
        print(f"\nProgress Summary:\n{progress_summary}")

    asyncio.run(main())

# python -m scitex.scholar.doi._BatchDOIResolver

# EOF
