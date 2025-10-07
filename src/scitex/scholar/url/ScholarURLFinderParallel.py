#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 08:40:15 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinderParallel.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/ScholarURLFinderParallel.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Parallel URL Finder for Scholar Module

Provides parallel processing for URL finding operations:
- Multiple browser contexts in parallel
- Shared authentication across workers
- Rate limiting and publisher-specific delays
- Progress tracking and statistics
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder

logger = logging.getLogger(__name__)


class ScholarURLFinderParallel:
    """
    Parallel URL finder with per-worker Chrome profiles.

    Enables true parallel URL finding by giving each worker its own Chrome profile:
    - Each worker syncs from system profile to get extensions and auth cookies
    - Workers run independently without browser context conflicts
    - Respects publisher rate limits per worker
    - Provides detailed progress tracking and statistics
    - Caches results for efficiency

    Architecture: Same as ScholarPDFDownloaderWithScreenshotsParallel
    - Per-worker Chrome profiles prevent conflicts
    - Profile syncing ensures authentication and extensions work
    - True parallelism significantly speeds up batch URL finding

    Worker Profiles:
    - URL finder workers: urlfinder_worker_0, urlfinder_worker_1, urlfinder_worker_2
    - PDF downloader workers: system_worker_0, system_worker_1, system_worker_2
    - Different prefixes prevent conflicts even if operations overlap
    """

    def __init__(
        self,
        auth_manager,  # ScholarAuthManager
        browser_manager,  # ScholarBrowserManager
        config: ScholarConfig = None,
        n_workers: Optional[int] = None,
    ):
        """
        Initialize parallel URL finder.

        Args:
            auth_manager: ScholarAuthManager instance
            browser_manager: ScholarBrowserManager instance
            config: ScholarConfig instance
            n_workers: Number of parallel workers (default: from config)
        """
        self.auth_manager = auth_manager
        self.browser_manager = browser_manager
        self.config = config or ScholarConfig()

        # Get number of workers from config or parameter
        pdf_config = self.config.get("pdf_download") or {}
        self.n_workers = n_workers or pdf_config.get("n_workers", 3)

        # Statistics
        self.stats = {
            "found": 0,
            "not_found": 0,
            "errors": 0,
        }

    def _get_publisher_limits(self, url: str) -> Dict[str, Any]:
        """Get rate limits for a publisher based on URL."""
        # Default limits
        default_limits = {"delay": 2.0, "timeout": 30000}

        if not url:
            return default_limits

        # Publisher-specific limits
        url_lower = url.lower()

        # IEEE tends to be slower
        if "ieee.org" in url_lower or "ieeexplore.ieee.org" in url_lower:
            return {"delay": 3.0, "timeout": 45000}

        # Springer can be slow
        if "springer.com" in url_lower or "link.springer.com" in url_lower:
            return {"delay": 2.5, "timeout": 40000}

        # Nature/Science tend to be fast
        if (
            "nature.com" in url_lower
            or "science.org" in url_lower
            or "sciencemag.org" in url_lower
        ):
            return {"delay": 1.5, "timeout": 25000}

        # Open access tends to be fast
        if "arxiv.org" in url_lower or "plos.org" in url_lower:
            return {"delay": 1.0, "timeout": 20000}

        return default_limits

    async def find_urls_batch(
        self,
        dois: List[str],
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Find URLs for multiple DOIs in parallel using per-worker Chrome profiles.

        Each worker gets its own Chrome profile synced from the system profile,
        enabling true parallel processing without conflicts.

        Args:
            dois: List of DOIs to process
            use_cache: Whether to use cached results

        Returns:
            List of URL dictionaries (same order as input DOIs)
        """
        if not dois:
            return []

        logger.info(
            f"Finding URLs for {len(dois)} DOIs using {self.n_workers} parallel workers"
        )

        # Split DOIs among workers
        workers_dois = [[] for _ in range(self.n_workers)]
        for i, doi in enumerate(dois):
            worker_idx = i % self.n_workers
            workers_dois[worker_idx].append((i, doi))  # (original_index, doi)

        # Create worker tasks - each gets its own Chrome profile
        tasks = []
        for worker_id, worker_dois in enumerate(workers_dois):
            if worker_dois:  # Only create task if worker has DOIs
                task = self._url_finder_worker(
                    worker_id=worker_id,
                    dois_with_indices=worker_dois,
                    use_cache=use_cache,
                )
                tasks.append(task)

        # Run workers in parallel
        worker_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results in original order
        results = [None] * len(dois)
        for worker_result in worker_results:
            if isinstance(worker_result, Exception):
                logger.error(f"Worker failed: {worker_result}")
                continue

            for idx, url_data in worker_result:
                results[idx] = url_data

        # Fill in any missing results with empty dicts
        results = [r if r is not None else {} for r in results]

        # Log statistics
        self._log_statistics(len(dois))

        return results

    async def _url_finder_worker(
        self,
        worker_id: int,
        dois_with_indices: List[tuple],  # [(index, doi), ...]
        use_cache: bool,
    ) -> List[tuple]:  # [(index, url_data), ...]
        """
        Worker process for finding URLs with its own Chrome profile.

        Each worker gets a unique Chrome profile synced from system profile,
        preventing conflicts and enabling true parallel processing.

        Args:
            worker_id: Worker identifier
            dois_with_indices: List of (original_index, doi) tuples
            use_cache: Whether to use cached results

        Returns:
            List of (index, url_data) tuples
        """
        from scitex.scholar.browser.local.ScholarBrowserManager import (
            ScholarBrowserManager,
        )
        from scitex.scholar.browser.local.utils._ChromeProfileManager import (
            ChromeProfileManager,
        )

        logger.info(
            f"Worker {worker_id} starting with {len(dois_with_indices)} DOIs"
        )

        # Create worker-specific Chrome profile for URL finding
        # Use "urlfinder_worker" prefix to avoid conflicts with PDF downloader workers
        worker_profile_name = f"urlfinder_worker_{worker_id}"
        logger.info(f"Worker {worker_id}: Using profile: {worker_profile_name}")

        # Sync from system profile to get extensions and auth cookies
        profile_manager = ChromeProfileManager(
            worker_profile_name, config=self.config
        )
        sync_success = profile_manager.sync_from_profile(
            source_profile_name="system"
        )

        if sync_success:
            logger.success(f"Worker {worker_id}: Profile synced from system")
        else:
            logger.warning(
                f"Worker {worker_id}: Profile sync failed, using empty profile"
            )

        results = []

        try:
            # Create browser manager with worker-specific profile
            browser_manager = ScholarBrowserManager(
                config=self.config,
                auth_manager=self.auth_manager,
                browser_mode="stealth",
                chrome_profile_name=worker_profile_name,
            )

            # Get authenticated browser for this worker
            browser, context = (
                await browser_manager.get_authenticated_browser_and_context_async()
            )

            # Initialize URL finder for this worker
            url_finder = ScholarURLFinder(
                context=context, config=self.config, use_cache=use_cache
            )

            for i, (original_idx, doi) in enumerate(dois_with_indices):
                try:
                    logger.info(
                        f"Worker {worker_id} [{i+1}/{len(dois_with_indices)}]: Finding URLs for {doi}"
                    )

                    # Apply rate limiting delay with jitter
                    if i > 0:  # Skip delay for first DOI
                        await asyncio.sleep(2.0 + random.uniform(0, 1))

                    # Find URLs
                    url_data = await url_finder.find_urls(doi)

                    if url_data.get("urls_pdf"):
                        self.stats["found"] += 1
                        logger.success(
                            f"Worker {worker_id}: Found {len(url_data['urls_pdf'])} PDF URLs for {doi}"
                        )
                    else:
                        self.stats["not_found"] += 1
                        logger.warning(
                            f"Worker {worker_id}: No PDF URLs found for {doi}"
                        )

                    results.append((original_idx, url_data))

                except Exception as e:
                    logger.error(
                        f"Worker {worker_id}: Failed to find URLs for {doi}: {e}"
                    )
                    self.stats["errors"] += 1
                    results.append((original_idx, {}))

            # Close browser after all DOIs processed
            await browser_manager.close()

        except Exception as e:
            logger.error(f"Worker {worker_id}: Failed to initialize: {e}")
            # Return empty results for all assigned DOIs
            for original_idx, doi in dois_with_indices:
                results.append((original_idx, {}))
                self.stats["errors"] += 1

        logger.info(
            f"Worker {worker_id} completed: {len(results)}/{len(dois_with_indices)} DOIs processed"
        )
        return results

    def _log_statistics(self, total: int):
        """Log final statistics."""
        logger.info(f"\n{'='*60}")
        logger.info("URL Finding Statistics:")
        logger.info(f"  Total DOIs: {total}")
        logger.info(f"  URLs Found: {self.stats['found']}")
        logger.info(f"  Not Found: {self.stats['not_found']}")
        logger.info(f"  Errors: {self.stats['errors']}")

        if total > 0:
            success_rate = (self.stats["found"] / total) * 100
            logger.info(f"  Success Rate: {success_rate:.1f}%")

        logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from scitex.scholar import ScholarAuthManager, ScholarBrowserManager
        from scitex.scholar.config import ScholarConfig

        # Initialize components
        config = ScholarConfig()
        auth_manager = ScholarAuthManager(config=config)
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            config=config,
            browser_mode="stealth",
            chrome_profile_name="system",
        )

        # Initialize parallel URL finder
        url_finder = ScholarURLFinderParallel(
            auth_manager=auth_manager,
            browser_manager=browser_manager,
            config=config,
            n_workers=3,
        )

        # Test DOIs - mix of paywalled and open access
        test_dois = [
            "10.1109/JBHI.2024.1234567",  # IEEE (paywalled)
            "10.1088/1741-2552/aaf92e",  # IOP Publishing (paywalled)
            "10.1038/s41467-020-12345-6",  # Nature Communications (open access)
            "10.1016/j.cell.2025.07.007",  # Cell (paywalled)
            "10.48550/arxiv.2201.11600",  # arXiv (open access)
        ]

        # Find URLs in parallel
        results = await url_finder.find_urls_batch(test_dois, use_cache=True)

        # Display results
        from pprint import pprint

        for doi, url_data in zip(test_dois, results):
            print(f"\n{'='*60}")
            print(f"DOI: {doi}")
            print(f"{'='*60}")
            pprint(url_data)

    asyncio.run(main_async())

# EOF
