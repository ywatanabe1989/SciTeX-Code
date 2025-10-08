#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 08:10:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ScholarPDFDownloaderWithScreenshotsParallel.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloaderWithScreenshotsParallel.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Parallel PDF downloader with multiple Chrome instances for improved performance."""

import asyncio
import json
import random
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.auth import AuthenticationGateway, ScholarAuthManager
from scitex.scholar.browser.local.ScholarBrowserManager import (
    ScholarBrowserManager,
)
from scitex.scholar.browser.local.utils._ChromeProfileManager import (
    ChromeProfileManager,
)
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader
from scitex.scholar.download.ScholarPDFDownloaderWithScreenshots import (
    ScholarPDFDownloaderWithScreenshots,
)
from scitex.scholar.storage._LibraryManager import LibraryManager

logger = logging.getLogger(__name__)

# Log screenshot availability at module load
logger.info("Screenshot-enabled PDF downloader is available")


# Publisher-specific rate limits to avoid detection
PUBLISHER_LIMITS = {
    "elsevier.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "sciencedirect.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "nature.com": {"max_parallel": 3, "delay": 10, "retry_delay": 20},
    "springer.com": {"max_parallel": 3, "delay": 10, "retry_delay": 20},
    "ieee.org": {"max_parallel": 2, "delay": 20, "retry_delay": 40},
    "wiley.com": {"max_parallel": 2, "delay": 15, "retry_delay": 30},
    "plos.org": {"max_parallel": 5, "delay": 5, "retry_delay": 10},
    "frontiersin.org": {"max_parallel": 4, "delay": 8, "retry_delay": 15},
    "mdpi.com": {"max_parallel": 4, "delay": 8, "retry_delay": 15},
    "arxiv.org": {"max_parallel": 5, "delay": 3, "retry_delay": 5},
    "biorxiv.org": {"max_parallel": 4, "delay": 5, "retry_delay": 10},
    "default": {"max_parallel": 3, "delay": 10, "retry_delay": 20},
}


class ScholarPDFDownloaderWithScreenshotsParallel:
    """Download PDFs in parallel using multiple Chrome instances."""

    def __init__(
        self,
        config: Optional[ScholarConfig] = None,
        auth_manager: Optional["ScholarAuthManager"] = None,
        max_workers: Optional[int] = None,
        use_parallel: Optional[bool] = None,
        delay_between_starts: Optional[int] = 1,
    ):
        """Initialize parallel downloader.

        Args:
            config: Scholar configuration
            auth_manager: Authentication manager for browser sessions
            max_workers: Maximum number of parallel Chrome instances (overrides config)
            use_parallel: Whether to use parallel downloads (overrides config)
            delay_between_starts: Delay in seconds between starting workers (overrides config)
        """
        self.config = config or ScholarConfig()
        self.auth_manager = auth_manager or ScholarAuthManager(config=config)
        self.library_manager = LibraryManager(config=self.config)

        # Ensure type conversion for numeric parameters
        self.max_workers = int(
            self.config.resolve(
                "max_parallel",
                max_workers,
                default=self._get_optimal_worker_count(),
            )
        )

        self.use_parallel = int(
            self.config.resolve(
                "use_parallel",
                use_parallel,
                default=True,
            )
        )

        self.delay_between_starts = self.config.resolve(
            "delay_between_starts",
            None,
            default=0.1,
        )

        self.default_delay = int(
            self.config.resolve(
                "default_delay",
                None,
                default=10,
            )
        )

        self.retry_attempts = int(
            self.config.resolve(
                "retry_attempts",
                None,
                default=3,
            )
        )

        self.timeout = int(
            self.config.resolve(
                "timeout",
                None,
                default=60,
            )
        )

        # Check authentication status
        self.has_auth = self._check_authentication()

        # Disable parallel if no authentication
        if not self.has_auth:
            logger.warning(
                "No authentication available - disabling parallel downloads"
            )
            self.use_parallel = False
            self.max_workers = 1

        # Track download statistics
        self.stats = {
            "total": 0,
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
            "errors": {},
        }

    @property
    def name(self) -> str:
        """Return class name for logging."""
        return self.__class__.__name__

    def _get_optimal_worker_count(self, pdf_max_parallel=None) -> int:
        """Calculate optimal number of workers based on environment.

        Priority order:
        1. SCITEX_SCHOLAR_N_JOBS env var
        2. SLURM_CPUS_PER_TASK (if in SLURM environment)
        3. CPU count / 2 (default heuristic)
        4. Cap at 8 workers max

        Returns:
            Optimal number of workers (1-8)
        """
        import multiprocessing

        n_workers = self.config.resolve(
            "pdf_max_parallel", pdf_max_parallel, 4
        )
        cpu_count = os.getenv(
            "SLURM_CPUS_PER_TASK", multiprocessing.cpu_count()
        )

        return min(int(n_workers), int(cpu_count))

    def _check_authentication(self) -> bool:
        """Check if authentication is available."""
        try:
            # Check for cached auth session
            auth_cache = self.config.get_auth_cache_dir() / "openathens.json"
            if auth_cache.exists():
                with open(auth_cache, "r") as f:
                    auth_data = json.load(f)
                    # Check for expiry field (correct key name)
                    expiry_str = auth_data.get("expiry")
                    if expiry_str:
                        expires = datetime.fromisoformat(expiry_str)
                        if expires > datetime.now():
                            logger.info(
                                f"Found valid authentication session "
                                f"(expires in {(expires - datetime.now()).total_seconds() / 3600:.1f}h)"
                            )
                            return True
                        else:
                            logger.warning(
                                f"Authentication session expired at {expires}"
                            )
                    else:
                        logger.warning(
                            "No expiry field in authentication cache"
                        )
            else:
                logger.warning("No authentication cache file found")
            return False
        except Exception as e:
            logger.warning(f"Error checking authentication: {e}")
            return False

    def _get_publisher_limits(self, url: str) -> Dict:
        """Get rate limits for a specific publisher."""
        if not url:
            return PUBLISHER_LIMITS["default"]
        url_lower = url.lower()
        for publisher, limits in PUBLISHER_LIMITS.items():
            if publisher in url_lower:
                return limits
        return PUBLISHER_LIMITS["default"]

    def _filter_papers_by_pdf_status(
        self, papers: List[Dict], library_dir: Path, project: str
    ) -> List[Dict]:
        """Filter papers to only include those needing download.

        Checks actual PDF status on disk (not just metadata) to avoid
        wasting workers on papers that already have PDFs.

        Args:
            papers: List of paper dicts with metadata
            library_dir: Library directory path
            project: Project name

        Returns:
            Filtered list of papers that need downloading
        """
        papers_to_download = []
        master_dir = library_dir / "MASTER"

        for paper in papers:
            doi = paper.get("doi")
            if not doi:
                print("No DOI Found. Skipping")
                # No DOI, can't download
                continue

            # Get paper ID and check for existing PDF
            paper_id = self.config.path_manager._generate_paper_id(doi=doi)
            paper_dir = master_dir / paper_id

            if not paper_dir.exists():
                # Paper directory doesn't exist, needs download
                papers_to_download.append(paper)
                continue

            # Check for actual PDF files
            pdf_files = list(paper_dir.glob("*.pdf"))

            if pdf_files:
                # PDF already exists, skip
                logger.debug(f"Skipping {paper_id}: PDF already exists")
                self.stats["skipped"] += 1
                continue

            # Check for .downloading marker (download in progress)
            downloading_marker = paper_dir / ".downloading"
            if downloading_marker.exists():
                logger.debug(
                    f"Skipping {paper_id}: Download already in progress"
                )
                self.stats["skipped"] += 1
                continue

            # Paper needs download
            papers_to_download.append(paper)

        return papers_to_download

    async def download_batch(
        self,
        papers_with_metadata: List[Dict],
        project: str,
        library_dir: Optional[Path] = None,
    ) -> Dict:
        """Download PDFs for a batch of papers in parallel.

        Args:
            papers_with_metadata: List of paper dicts with enriched metadata
            project: Project name for organizing downloads
            library_dir: Library directory path

        Returns:
            Dictionary with download statistics
        """
        if not papers_with_metadata:
            return self.stats

        self.stats["total"] = len(papers_with_metadata)

        # Log stage clearly
        logger.info(
            f"PDF Download: Starting for {len(papers_with_metadata)} papers ({self.n_workers} workers)",
            sep="-", n_sep=50, indent=2
        )

        # Setup logging to library
        library_dir = library_dir or self.config.get_library_dir()
        self.log_file_handler = None

        if project:
            log_dir = library_dir / project / "info" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"download_{timestamp}.log"

            # Add file handler to logger
            import logging as stdlib_logging

            self.log_file_handler = stdlib_logging.FileHandler(log_file)
            self.log_file_handler.setLevel(stdlib_logging.INFO)
            formatter = stdlib_logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.log_file_handler.setFormatter(formatter)

            # Add handler to root logger to capture all logs
            stdlib_logging.getLogger().addHandler(self.log_file_handler)

            logger.info(f"Logging downloads to: {log_file}")

        # Filter papers by PDF status before worker allocation
        papers_to_download = self._filter_papers_by_pdf_status(
            papers_with_metadata, library_dir, project
        )

        if not papers_to_download:
            logger.success("All papers already have PDFs", indent=3)
            return self.stats

        # Update stats with filtered count
        self.stats["total"] = len(papers_to_download)
        logger.info(
            f"Downloading {len(papers_to_download)} papers (skipped {len(papers_with_metadata) - len(papers_to_download)} with existing PDFs)",
            indent=3
        )

        # Analyze journals/publishers in the batch
        self._analyze_batch(papers_to_download)

        try:
            if self.use_parallel and self.max_workers > 1:
                # Preemptively create worker profiles to avoid crashes
                await self._prepare_worker_profiles_async(self.max_workers)

                logger.info(
                    f"Starting parallel downloads with {self.max_workers} workers"
                )
                result = await self._download_parallel(
                    papers_to_download, project, library_dir
                )
            else:
                logger.info("Using sequential downloads (no parallel)")
                result = await self._download_sequential(
                    papers_to_download, project, library_dir
                )

            # Log final statistics
            logger.info("=" * 60)
            logger.info("Download Statistics:")
            logger.info(f"  Total papers:      {self.stats['total']}")
            logger.info(f"  Downloaded:        {self.stats['downloaded']}")
            logger.info(f"  Failed:            {self.stats['failed']}")
            logger.info(f"  Skipped:           {self.stats['skipped']}")
            if self.stats["downloaded"] > 0:
                success_rate = (
                    self.stats["downloaded"] / self.stats["total"]
                ) * 100
                logger.info(f"  Success rate:      {success_rate:.1f}%")
            logger.info("=" * 60)

            return result
        finally:
            # Clean up log file handler
            if self.log_file_handler:
                import logging as stdlib_logging

                stdlib_logging.getLogger().removeHandler(self.log_file_handler)
                self.log_file_handler.close()
                self.log_file_handler = None

    async def _prepare_worker_profiles_async(self, num_workers: int) -> None:
        """Preemptively create worker profiles to avoid browser crashes.

        Creates worker profiles for all potential workers BEFORE starting downloads.
        This prevents crashes from multiple Chrome instances trying to use the same profile.

        Args:
            num_workers: Number of worker profiles to create
        """
        from scitex.scholar.browser.local.utils._ChromeProfileManager import (
            ChromeProfileManager,
        )

        logger.info(f"Preparing {num_workers} worker profiles...")

        for worker_id in range(num_workers):
            worker_profile_name = f"system_worker_{worker_id}"
            profile_manager = ChromeProfileManager(
                worker_profile_name, config=self.config
            )

            # Check if profile already exists and is valid
            if profile_manager.profile_dir.exists():
                # Verify profile has extensions
                if profile_manager.check_extensions_installed(verbose=False):
                    logger.debug(
                        f"Worker profile {worker_id}: Already exists with extensions"
                    )
                    continue
                else:
                    logger.debug(
                        f"Worker profile {worker_id}: Exists but missing extensions, resyncing"
                    )

            # Sync from system profile (creates profile if doesn't exist)
            sync_success = profile_manager.sync_from_profile(
                source_profile_name="system"
            )

            if sync_success:
                logger.debug(
                    f"Worker profile {worker_id}: Created successfully"
                )
            else:
                logger.warn(
                    f"Worker profile {worker_id}: Sync failed, will use empty profile"
                )

        logger.success(f"All {num_workers} worker profiles prepared")

    def _analyze_batch(self, papers: List[Dict]) -> None:
        """Analyze batch to understand publisher distribution."""
        publisher_counts = {}
        journal_counts = {}

        for paper in papers:
            # Count by journal
            journal = paper.get("journal", "Unknown")
            journal_counts[journal] = journal_counts.get(journal, 0) + 1

            # Try to identify publisher
            doi = paper.get("doi", "")
            url = paper.get("url", "")
            publisher = paper.get("publisher", "")

            # Identify publisher from DOI, URL, or metadata
            identified_publisher = self._identify_publisher(
                doi, url, publisher
            )
            publisher_counts[identified_publisher] = (
                publisher_counts.get(identified_publisher, 0) + 1
            )

        # Log distribution for monitoring
        logger.info(
            f"Batch contains papers from {len(journal_counts)} journals"
        )
        logger.info(f"Publisher distribution: {publisher_counts}")

        # Adjust workers based on publisher diversity (only if using parallel)
        unique_publishers = len(
            [p for p in publisher_counts if p != "unknown"]
        )
        if unique_publishers > 0 and self.use_parallel:
            # Don't use more workers than unique publishers to avoid hitting same publisher
            original_workers = self.max_workers
            self.max_workers = min(self.max_workers, unique_publishers)
            if self.max_workers != original_workers:
                logger.info(
                    f"Adjusted max_workers from {original_workers} to {self.max_workers} based on {unique_publishers} unique publishers"
                )
            else:
                logger.debug(
                    f"Keeping max_workers at {self.max_workers} ({unique_publishers} unique publishers)"
                )

    async def _download_parallel(
        self, papers: List[Dict], project: str, library_dir: Optional[Path]
    ) -> Dict:
        """Download papers in parallel using multiple workers."""

        # Group papers by publisher for better rate limiting
        publisher_groups = self._group_by_publisher(papers)

        # Create download queue with publisher-aware scheduling
        download_queue = self._create_optimized_queue(publisher_groups)

        # Split queue into chunks for workers
        chunks = [
            download_queue[i :: self.max_workers]
            for i in range(min(self.max_workers, len(download_queue)))
        ]

        # Create worker tasks
        tasks = []
        for worker_id, chunk in enumerate(chunks):
            if chunk:  # Only create worker if there's work
                # Stagger worker starts to avoid simultaneous connections
                await asyncio.sleep(worker_id * self.delay_between_starts)

                task = self._download_worker(
                    chunk,
                    worker_id=worker_id,
                    project=project,
                    library_dir=library_dir,
                )
                tasks.append(task)
                now = datetime.now()
                logger.info(
                    f"{now} - Started worker {worker_id} with {len(chunk)} papers"
                )

        # Wait for all workers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results from all workers
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Worker failed: {result}")
                self.stats["errors"]["worker_error"] = str(result)

        return self.stats

    async def _download_worker(
        self,
        papers: List[Dict],
        worker_id: int,
        project: str,
        library_dir: Optional[Path],
    ) -> None:
        """Worker function to download papers."""

        logger.info(f"Worker {worker_id}: Starting with {len(papers)} papers")

        # Create worker-specific browser manager with unique profile per worker
        # This prevents Chrome from crashing due to multiple instances sharing same user-data-dir
        # Profile name format: system_worker_0, system_worker_1, etc.
        worker_profile_name = f"system_worker_{worker_id}"
        logger.info(
            f"Worker {worker_id}: Using profile name: {worker_profile_name}"
        )

        # Sync extensions and cookies from system profile to worker profile using rsync
        # Always sync to ensure completeness (rsync only copies changed files, so it's fast)
        profile_manager = ChromeProfileManager(
            worker_profile_name, config=self.config
        )

        sync_success = profile_manager.sync_from_profile(
            source_profile_name="system"
        )

        if sync_success:
            logger.success(
                f"Worker {worker_id}: Profile synced from system profile"
            )
        else:
            logger.warn(
                f"Worker {worker_id}: Profile sync failed, proceeding with empty profile"
            )

        try:
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

            # Process papers assigned to this worker
            for i, paper in enumerate(papers):
                try:
                    doi = paper.get("doi")
                    title = paper.get("title", "Unknown")[:50]

                    # Visit gateway and acquire publisher-specific authentication cookies
                    auth_gateway = AuthenticationGateway(
                        auth_manager=self.auth_manager,
                        browser_manager=browser_manager,
                    )
                    _url_context = await auth_gateway.prepare_context_async(
                        doi=doi, context=context
                    )

                    # Use screenshot-enabled downloader for this worker
                    # Authentication and URL finding already done by Scholar.py preprocessing
                    pdf_downloader = ScholarPDFDownloaderWithScreenshots(
                        context=context,
                        config=self.config,
                        use_cache=True,
                        screenshot_interval=2.0,
                        capture_on_failure=True,
                        capture_during_success=True,  # Always capture screenshots for documentation
                    )

                    logger.info(
                        f"Worker {worker_id} [{i+1}/{len(papers)}]: Processing {title}..."
                    )

                    # Get PDF URLs from paper dict (already resolved by Scholar.py)
                    pdf_urls = paper.get("pdf_urls", [])
                    urls = paper.get(
                        "url_info", {}
                    )  # Full URL info for logging

                    if pdf_urls:
                        # Get rate limits for first URL
                        first_url = (
                            pdf_urls[0].get("url")
                            if isinstance(pdf_urls[0], dict)
                            else pdf_urls[0]
                        )
                        limits = self._get_publisher_limits(first_url)

                        # Apply rate limiting delay
                        await asyncio.sleep(
                            limits["delay"] + random.uniform(0, 3)
                        )  # Add jitter

                        # Download PDF with URL info
                        success = await self._download_single_pdf(
                            paper,
                            pdf_urls,
                            pdf_downloader,
                            project,
                            library_dir,
                            worker_id,
                            url_info=urls,  # Pass all URL info including openurl_resolved
                        )

                        if success:
                            self.stats["downloaded"] += 1
                            logger.success(
                                f"Worker {worker_id}: Downloaded {title}"
                            )
                        else:
                            # Save URL info even when download failed
                            self._save_url_info_only(
                                paper, urls, project, library_dir
                            )
                            self.stats["failed"] += 1

                    else:
                        logger.warning(
                            f"Worker {worker_id}: No PDF URLs found for {title}"
                        )

                        # Mark as attempted so it shows as failed (PDF_f) not pending (PDF_p)
                        paper_id = self.config.path_manager._generate_paper_id(
                            doi=doi
                        )
                        master_dir = (
                            self.config.path_manager.get_library_master_dir()
                        )
                        paper_dir = master_dir / paper_id
                        paper_dir.mkdir(parents=True, exist_ok=True)
                        attempted_marker = paper_dir / ".download_attempted"
                        download_log = paper_dir / "download_log.txt"

                        if not attempted_marker.exists():
                            attempted_marker.touch()
                            from datetime import datetime

                            with open(attempted_marker, "w") as f:
                                f.write(
                                    f"Download attempted at: {datetime.now().isoformat()}\n"
                                )

                        # Write to download log
                        if not download_log.exists():
                            from datetime import datetime

                            with open(download_log, "w") as f:
                                f.write(f"Download Log for {doi}\n")
                                f.write(f"{'=' * 60}\n")
                                f.write(
                                    f"Started at: {datetime.now().isoformat()}\n"
                                )
                                f.write(f"Worker ID: {worker_id}\n")
                                f.write(f"Paper ID: {paper_id}\n")

                                # Log all URLs found by URL finder
                                f.write(f"\n{'=' * 60}\n")
                                f.write(f"URL FINDER RESULTS:\n")
                                f.write(f"{'=' * 60}\n")
                                for key, value in urls.items():
                                    if value:
                                        f.write(f"{key}: {value}\n")

                                f.write(f"\n{'=' * 60}\n")
                                f.write(f"STATUS: NO PDF URLS FOUND\n")
                                f.write(
                                    f"The URL finder could not locate any PDF download links.\n"
                                )
                                f.write(f"{'=' * 60}\n")

                        # Save URL info even when no PDF URLs found
                        self._save_url_info_only(
                            paper, urls, project, library_dir
                        )
                        self.stats["failed"] += 1

                except Exception as e:
                    logger.error(
                        f"Worker {worker_id}: Error processing paper: {e}"
                    )
                    self.stats["failed"] += 1

        except Exception as e:
            import traceback

            logger.error(f"Worker {worker_id}: Fatal error - {e}")
            logger.error(traceback.format_exc())
            raise

        finally:
            # Clean up browser for this worker
            await browser_manager.close()
            logger.info(f"Worker {worker_id}: Completed")

    async def _download_sequential(
        self, papers: List[Dict], project: str, library_dir: Optional[Path]
    ) -> Dict:
        """Download papers sequentially (fallback when no auth or parallel disabled)."""

        # Use single browser instance
        browser_manager = ScholarBrowserManager(
            config=self.config,
            auth_manager=self.auth_manager,
            browser_mode="stealth",
            chrome_profile_name="system",  # Use system profile for downloads
        )

        try:
            browser, context = (
                await browser_manager.get_authenticated_browser_and_context_async()
            )

            for i, paper in enumerate(papers):
                try:
                    doi = paper.get("doi")
                    title = paper.get("title", "Unknown")[:50]

                    # Visit gateway and acquire publisher-specific authentication cookies
                    auth_gateway = AuthenticationGateway(
                        auth_manager=self.auth_manager,
                        browser_manager=browser_manager,
                    )
                    _url_context = await auth_gateway.prepare_context_async(
                        doi=doi, context=context
                    )
                    # Use screenshot-enabled downloader
                    # Authentication and URL finding already done by Scholar.py preprocessing
                    pdf_downloader = ScholarPDFDownloaderWithScreenshots(
                        context=context,
                        config=self.config,
                        use_cache=True,
                        screenshot_interval=2.0,
                        capture_on_failure=True,
                        capture_during_success=True,  # Always capture screenshots for documentation
                    )

                    logger.info(
                        f"[{i+1}/{len(papers)}]: Processing {title}..."
                    )

                    # Get PDF URLs from paper dict (already resolved by Scholar.py)
                    pdf_urls = paper.get("pdf_urls", [])
                    urls = paper.get(
                        "url_info", {}
                    )  # Full URL info for logging

                    if pdf_urls:
                        # Conservative delay for sequential mode
                        await asyncio.sleep(10)

                        success = await self._download_single_pdf(
                            paper,
                            pdf_urls,
                            pdf_downloader,
                            project,
                            library_dir,
                            worker_id=0,
                            url_info=urls,  # Pass all URL info including openurl_resolved
                        )

                        if success:
                            self.stats["downloaded"] += 1
                        else:
                            self.stats["failed"] += 1
                    else:
                        self.stats["skipped"] += 1

                except Exception as e:
                    logger.error(f"Error processing paper: {e}")
                    self.stats["failed"] += 1

        finally:
            await browser_manager.close()

        return self.stats

    async def _download_single_pdf(
        self,
        paper: Dict,
        pdf_urls: List,
        pdf_downloader: ScholarPDFDownloader,
        project: str,
        library_dir: Optional[Path],
        worker_id: int,
        url_info: Dict = None,
    ) -> bool:
        """Download a single PDF and save to library with metadata."""

        doi = paper.get("doi")
        # Use PathManager's consistent ID generation instead of local hash
        paper_id = (
            self.config.path_manager._generate_paper_id(
                doi=doi,
                title=paper.get("title"),
                authors=paper.get("authors"),
                year=paper.get("year"),
            )
            if doi
            else None
        )

        # Create .downloading marker to show download in progress (PDF_r status)
        downloading_marker = None
        attempted_marker = None
        download_log = None
        if paper_id:
            master_dir = self.config.path_manager.get_library_master_dir()
            paper_dir = master_dir / paper_id
            paper_dir.mkdir(parents=True, exist_ok=True)
            downloading_marker = paper_dir / ".downloading"
            attempted_marker = paper_dir / ".download_attempted"
            download_log = paper_dir / "download_log.txt"
            downloading_marker.touch()

            # Update symlink to PDF_r (running) status to show download in progress
            from scitex.scholar.storage._LibraryManager import LibraryManager

            library_manager = LibraryManager(
                config=self.config, project=project
            )
            library_manager.update_symlink(
                master_storage_path=paper_dir, project=project
            )

        try:
            # Create .download_attempted marker at the start of first download attempt
            # This tracks that we tried, even if we fail before screenshots
            if attempted_marker and not attempted_marker.exists():
                attempted_marker.touch()
                # Write timestamp for debugging
                with open(attempted_marker, "w") as f:
                    from datetime import datetime

                    f.write(
                        f"Download attempted at: {datetime.now().isoformat()}\n"
                    )

            # Initialize download log
            if download_log:
                from datetime import datetime

                with open(download_log, "w") as f:
                    f.write(f"Download Log for {doi}\n")
                    f.write(f"{'=' * 60}\n")
                    f.write(f"Started at: {datetime.now().isoformat()}\n")
                    f.write(f"Worker ID: {worker_id}\n")
                    f.write(f"Paper ID: {paper_id}\n")

                    # Log all URLs found by URL finder
                    if url_info:
                        f.write(f"\n{'=' * 60}\n")
                        f.write(f"URL FINDER RESULTS:\n")
                        f.write(f"{'=' * 60}\n")
                        for key, value in url_info.items():
                            if value:
                                f.write(f"{key}: {value}\n")

                    f.write(f"\n{'=' * 60}\n")
                    f.write(f"Attempting {len(pdf_urls)} PDF URL(s):\n")
                    f.write(f"{'=' * 60}\n")

            # Try each PDF URL until success
            for i, pdf_entry in enumerate(pdf_urls, 1):
                pdf_url = (
                    pdf_entry.get("url")
                    if isinstance(pdf_entry, dict)
                    else pdf_entry
                )
                if not pdf_url:
                    if download_log:
                        with open(download_log, "a") as f:
                            f.write(f"\nURL {i}: Empty/invalid URL, skipped\n")
                    continue

                # Log URL attempt
                if download_log:
                    with open(download_log, "a") as f:
                        f.write(f"\n{'-' * 60}\n")
                        f.write(f"URL {i}/{len(pdf_urls)}: {pdf_url}\n")

                # Download to temp location
                temp_output = (
                    Path("/tmp")
                    / f"worker_{worker_id}_{doi.replace('/', '_').replace(':', '_')}.pdf"
                )

                try:
                    # Use screenshot-enabled download if available
                    if hasattr(
                        pdf_downloader, "download_from_url_with_screenshots"
                    ):
                        if download_log:
                            with open(download_log, "a") as f:
                                f.write(
                                    "Method: Screenshot-enabled download\n"
                                )

                        logger.info(
                            f"Using screenshot-enabled download for {doi} (paper_id: {paper_id})"
                        )
                        result, screenshots = (
                            await pdf_downloader.download_from_url_with_screenshots(
                                pdf_url=pdf_url,
                                output_path=temp_output,
                                doi=doi,
                                paper_id=paper_id,
                                retry_with_screenshots=True,
                            )
                        )
                        if screenshots:
                            logger.info(
                                f"Worker {worker_id}: Captured {len(screenshots)} screenshots for {doi}"
                            )
                            if download_log:
                                with open(download_log, "a") as f:
                                    f.write(
                                        f"Screenshots captured: {len(screenshots)}\n"
                                    )
                    else:
                        # Fallback to regular download
                        if download_log:
                            with open(download_log, "a") as f:
                                f.write(
                                    "Method: Regular download (no screenshots)\n"
                                )

                        result = await pdf_downloader.download_from_url(
                            pdf_url=pdf_url, output_path=temp_output
                        )

                    if result and result.exists():
                        # Log success with detailed information
                        if download_log:
                            with open(download_log, "a") as f:
                                from datetime import datetime

                                f.write(f"\n{'=' * 60}\n")
                                f.write(f"FINAL STATUS: SUCCESS\n")
                                f.write(f"{'=' * 60}\n")
                                f.write(
                                    f"Completed at: {datetime.now().isoformat()}\n"
                                )
                                f.write(
                                    f"PDF size: {result.stat().st_size:,} bytes ({result.stat().st_size / (1024*1024):.2f} MB)\n"
                                )
                                f.write(f"PDF path: {result}\n")
                                if url_info:
                                    f.write(f"\nURL Information:\n")
                                    for key, value in url_info.items():
                                        if value:
                                            f.write(f"  {key}: {value}\n")

                        # Remove .downloading marker BEFORE updating symlink
                        # so symlink shows PDF_s (successful) not PDF_r (running)
                        if downloading_marker and downloading_marker.exists():
                            downloading_marker.unlink()

                        # Remove .download_attempted marker on success
                        # (we only keep it for failed attempts)
                        if attempted_marker and attempted_marker.exists():
                            attempted_marker.unlink()

                        # Keep download_log.txt for both success and failure

                        # Save to library with metadata including URL info
                        # Note: _save_to_library() handles symlink update to PDF_s status
                        saved = self._save_to_library(
                            paper,
                            result,
                            project,
                            library_dir,
                            url_info=url_info,
                        )

                        # Clean up temp file
                        temp_output.unlink(missing_ok=True)

                        return saved

                except Exception as e:
                    error_msg = str(e)
                    logger.debug(
                        f"Worker {worker_id}: Failed to download from {pdf_url}: {error_msg}"
                    )

                    # Log failure reason
                    if download_log:
                        with open(download_log, "a") as f:
                            f.write(f"Status: FAILED\n")
                            f.write(f"Error: {error_msg}\n")
                    continue

            # All URLs failed
            if download_log:
                with open(download_log, "a") as f:
                    from datetime import datetime

                    f.write(f"\n{'=' * 60}\n")
                    f.write(f"FINAL STATUS: ALL ATTEMPTS FAILED\n")
                    f.write(f"Completed at: {datetime.now().isoformat()}\n")

            # Update symlink to PDF_f (failed) status
            if paper_id:
                # Remove .downloading marker first so symlink shows PDF_f not PDF_r
                if downloading_marker and downloading_marker.exists():
                    downloading_marker.unlink()

                library_manager = LibraryManager(
                    config=self.config, project=project
                )
                library_manager.update_symlink(
                    master_storage_path=paper_dir, project=project
                )

            return False

        finally:
            # Remove .downloading marker if still exists (download failed/error)
            if downloading_marker and downloading_marker.exists():
                downloading_marker.unlink()

    def _save_to_library(
        self,
        paper: Dict,
        pdf_path: Path,
        project: str,
        library_dir: Optional[Path],
        url_info: Dict = None,
    ) -> bool:
        """Save downloaded PDF to library with proper structure and metadata."""

        try:
            library_dir = library_dir or self.config.get_library_dir()

            # Use PathManager's consistent ID generation instead of local hash
            doi = paper.get("doi", "")
            paper_id = self.config.path_manager._generate_paper_id(
                doi=doi,
                title=paper.get("title"),
                authors=paper.get("authors"),
                year=paper.get("year"),
            )

            # Create MASTER storage directory
            master_dir = library_dir / "MASTER" / paper_id
            master_dir.mkdir(parents=True, exist_ok=True)

            # Copy PDF to MASTER
            pdf_filename = f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
            master_pdf_path = master_dir / pdf_filename
            shutil.copy2(pdf_path, master_pdf_path)

            # Update metadata with PDF info and URLs
            metadata_file = master_dir / "metadata.json"

            # Read existing metadata if it exists
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    existing_metadata = json.load(f)
            else:
                existing_metadata = paper.copy()

            # Update with PDF info
            pdf_info = {
                "pdf_path": f"MASTER/{paper_id}/{pdf_filename}",
                "pdf_downloaded_at": datetime.now().isoformat(),
                "pdf_size_bytes": master_pdf_path.stat().st_size,
            }

            # Check if we have standardized structure
            if "metadata" in existing_metadata:
                # Standardized format - update the nested structure
                if "path" not in existing_metadata["metadata"]:
                    existing_metadata["metadata"]["path"] = {}
                if "pdfs" not in existing_metadata["metadata"]["path"]:
                    existing_metadata["metadata"]["path"]["pdfs"] = []

                # Add PDF path to path.pdfs list if not already there
                pdf_path_entry = f"MASTER/{paper_id}/{pdf_filename}"
                if (
                    pdf_path_entry
                    not in existing_metadata["metadata"]["path"]["pdfs"]
                ):
                    existing_metadata["metadata"]["path"]["pdfs"].append(
                        pdf_path_entry
                    )
                    existing_metadata["metadata"]["path"][
                        "pdfs_engines"
                    ] = "ScholarPDFDownloaderWithScreenshotsParallel"

                # Update container with PDF download info
                if "container" not in existing_metadata:
                    existing_metadata["container"] = {}
                existing_metadata["container"]["pdf_downloaded_at"] = pdf_info[
                    "pdf_downloaded_at"
                ]
                existing_metadata["container"]["pdf_size_bytes"] = pdf_info[
                    "pdf_size_bytes"
                ]

                # Add URL information to standardized structure
                if url_info:
                    if "url" not in existing_metadata["metadata"]:
                        existing_metadata["metadata"]["url"] = {}

                    if url_info.get("url_doi"):
                        existing_metadata["metadata"]["url"]["doi"] = url_info[
                            "url_doi"
                        ]
                        existing_metadata["metadata"]["url"][
                            "doi_engines"
                        ] = "ScholarURLFinder"
                    if url_info.get("url_publisher"):
                        existing_metadata["metadata"]["url"]["publisher"] = (
                            url_info["url_publisher"]
                        )
                        existing_metadata["metadata"]["url"][
                            "publisher_engines"
                        ] = "ScholarURLFinder"
                    if url_info.get("url_openurl_query"):
                        existing_metadata["metadata"]["url"][
                            "openurl_query"
                        ] = url_info["url_openurl_query"]
                        existing_metadata["metadata"]["url"][
                            "openurl_engines"
                        ] = "OpenURLResolver"
                    if url_info.get("url_openurl_resolved"):
                        # Handle both string and list formats
                        resolved = url_info["url_openurl_resolved"]
                        if isinstance(resolved, str):
                            existing_metadata["metadata"]["url"][
                                "openurl_resolved"
                            ] = ([resolved] if resolved != "skipped" else [])
                        else:
                            existing_metadata["metadata"]["url"][
                                "openurl_resolved"
                            ] = (resolved if resolved else [])
                        existing_metadata["metadata"]["url"][
                            "openurl_resolved_engines"
                        ] = "OpenURLResolver"
                    if url_info.get("urls_pdf"):
                        existing_metadata["metadata"]["url"]["pdfs"] = (
                            url_info["urls_pdf"]
                        )
                        existing_metadata["metadata"]["url"][
                            "pdfs_engines"
                        ] = "ScholarURLFinder"

                metadata = existing_metadata
            else:
                # Flat format fallback
                metadata = existing_metadata
                metadata.update(pdf_info)
                if url_info:
                    metadata["url_doi"] = url_info.get("url_doi")
                    metadata["url_publisher"] = url_info.get("url_publisher")
                    metadata["url_openurl_query"] = url_info.get(
                        "url_openurl_query"
                    )
                    metadata["url_openurl_resolved"] = url_info.get(
                        "url_openurl_resolved"
                    )
                    metadata["urls_pdf"] = url_info.get("urls_pdf", [])

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            # Update symlink to reflect PDF_s (success) status
            # This uses LibraryManager.update_symlink() which re-generates the readable name
            # based on current state (PDF exists, no .downloading marker)
            if project:
                master_storage_path = library_dir / "MASTER" / paper_id
                self.library_manager.update_symlink(
                    master_storage_path=master_storage_path, project=project
                )

                logger.info(f"Saved PDF to library: {paper_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to save to library: {e}")
            return False

    def _save_url_info_only(
        self,
        paper: Dict,
        url_info: Dict,
        project: str,
        library_dir: Optional[Path],
    ) -> bool:
        """Save URL information to metadata even when PDF download fails."""
        try:
            library_dir = library_dir or self.config.get_library_dir()

            # Use PathManager's consistent ID generation
            doi = paper.get("doi", "")
            paper_id = self.config.path_manager._generate_paper_id(
                doi=doi, title=paper.get("title")
            )

            # Check if metadata already exists
            master_dir = library_dir / "MASTER" / paper_id
            metadata_file = master_dir / "metadata.json"

            if not metadata_file.exists():
                # No existing metadata - nothing to update
                logger.debug(
                    f"No existing metadata for {paper_id}, cannot save URL info only"
                )
                return False

            # Read existing standardized metadata
            with open(metadata_file, "r") as f:
                existing_metadata = json.load(f)

            # Check if we have standardized structure
            if "metadata" not in existing_metadata:
                logger.debug(
                    f"No standardized metadata structure for {paper_id}"
                )
                return False

            # Update URL section in standardized structure
            if "url" not in existing_metadata["metadata"]:
                existing_metadata["metadata"]["url"] = {}

            if url_info:
                if url_info.get("url_doi"):
                    existing_metadata["metadata"]["url"]["doi"] = url_info[
                        "url_doi"
                    ]
                    if (
                        "ScholarURLFinder"
                        not in existing_metadata["metadata"]["url"][
                            "doi_engines"
                        ]
                    ):
                        existing_metadata["metadata"]["url"][
                            "doi_engines"
                        ].append("ScholarURLFinder")
                if url_info.get("url_publisher"):
                    existing_metadata["metadata"]["url"]["publisher"] = (
                        url_info["url_publisher"]
                    )
                    if (
                        "ScholarURLFinder"
                        not in existing_metadata["metadata"]["url"][
                            "publisher_engines"
                        ]
                    ):
                        existing_metadata["metadata"]["url"][
                            "publisher_engines"
                        ].append("ScholarURLFinder")
                if url_info.get("url_openurl_query"):
                    existing_metadata["metadata"]["url"]["openurl_query"] = (
                        url_info["url_openurl_query"]
                    )
                    if (
                        "OpenURLResolver"
                        not in existing_metadata["metadata"]["url"][
                            "openurl_engines"
                        ]
                    ):
                        existing_metadata["metadata"]["url"][
                            "openurl_engines"
                        ].append("OpenURLResolver")
                if url_info.get("url_openurl_resolved"):
                    # Handle both string and list formats
                    resolved = url_info["url_openurl_resolved"]
                    if isinstance(resolved, str):
                        existing_metadata["metadata"]["url"][
                            "openurl_resolved"
                        ] = ([resolved] if resolved != "skipped" else [])
                    else:
                        existing_metadata["metadata"]["url"][
                            "openurl_resolved"
                        ] = (resolved if resolved else [])
                    if (
                        "OpenURLResolver"
                        not in existing_metadata["metadata"]["url"][
                            "openurl_resolved_engines"
                        ]
                    ):
                        existing_metadata["metadata"]["url"][
                            "openurl_resolved_engines"
                        ].append("OpenURLResolver")
                if url_info.get("urls_pdf"):
                    existing_metadata["metadata"]["url"]["pdfs"] = url_info[
                        "urls_pdf"
                    ]
                    if (
                        "ScholarURLFinder"
                        not in existing_metadata["metadata"]["url"][
                            "pdfs_engines"
                        ]
                    ):
                        existing_metadata["metadata"]["url"][
                            "pdfs_engines"
                        ].append("ScholarURLFinder")

            # Save updated metadata
            with open(metadata_file, "w") as f:
                json.dump(existing_metadata, f, indent=2, default=str)

            logger.debug(f"Saved URL info for {paper_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save URL info: {e}")
            logger.error(traceback.format_exc())
            return False

    def _identify_publisher(self, doi: str, url: str, publisher: str) -> str:
        """Identify publisher from DOI, URL, or metadata."""
        # Check DOI patterns
        doi_lower = doi.lower() if doi else ""
        url_lower = url.lower() if url else ""
        publisher_lower = publisher.lower() if publisher else ""

        # Common DOI prefixes and their publishers
        doi_patterns = {
            "10.1038": "nature.com",
            "10.1126": "sciencemag.org",
            "10.1016": "elsevier.com",
            "10.1007": "springer.com",
            "10.1109": "ieee.org",
            "10.1002": "wiley.com",
            "10.1371": "plos.org",
            "10.3389": "frontiersin.org",
            "10.3390": "mdpi.com",
            "10.48550": "arxiv.org",
            "10.1101": "biorxiv.org",
            "10.1093": "oxford.com",
        }

        # Check DOI prefix
        for prefix, pub in doi_patterns.items():
            if doi_lower.startswith(prefix):
                return pub

        # Check URL domain
        for publisher_domain in PUBLISHER_LIMITS.keys():
            if publisher_domain != "default":
                if (
                    publisher_domain in url_lower
                    or publisher_domain in publisher_lower
                ):
                    return publisher_domain

        return "unknown"

    def _group_by_publisher(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """Group papers by publisher domain for better scheduling."""
        groups = {"unknown": []}

        for paper in papers:
            doi = paper.get("doi", "")
            url = paper.get("url", "")
            publisher = paper.get("publisher", "")

            # Identify publisher
            identified_publisher = self._identify_publisher(
                doi, url, publisher
            )

            if identified_publisher not in groups:
                groups[identified_publisher] = []
            groups[identified_publisher].append(paper)

        # Log grouping results
        for pub, papers_list in groups.items():
            if papers_list:
                logger.debug(f"Publisher '{pub}': {len(papers_list)} papers")

        return groups

    def _create_optimized_queue(
        self, publisher_groups: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """Create download queue optimized for rate limits."""
        queue = []

        # Interleave papers from different publishers to minimize rate limit hits
        max_papers = max(len(papers) for papers in publisher_groups.values())

        for i in range(max_papers):
            for publisher, papers in publisher_groups.items():
                if i < len(papers):
                    queue.append(papers[i])

        return queue


if __name__ == "__main__":
    # Test parallel downloader
    import asyncio

    async def main_async():
        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )

        auth_manager = ScholarAuthManager()
        downloader = ScholarPDFDownloaderWithScreenshotsParallel(
            auth_manager=auth_manager, max_workers=3
        )

        # Test papers
        papers = [
            {"doi": "10.1038/nature12373", "title": "Test Paper 1"},
            {"doi": "10.1126/science.1234567", "title": "Test Paper 2"},
            {"doi": "10.1371/journal.pone.0123456", "title": "Test Paper 3"},
            {"doi": "10.48550/arxiv.2201.11600", "title": "Test Paper 4"},
        ]

        results = await downloader.download_batch(papers, project="test")
        print(f"Download results: {results}")

    asyncio.run(main_async())

# EOF
