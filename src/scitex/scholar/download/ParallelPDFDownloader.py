#!/usr/bin/env python3
"""Parallel PDF downloader with multiple Chrome instances for improved performance."""

import asyncio
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import random

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.local.ScholarBrowserManager import ScholarBrowserManager
from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader
from scitex.scholar.storage._LibraryManager import LibraryManager

# Try to import screenshot-enabled downloader
try:
    from scitex.scholar.download.ScholarPDFDownloaderWithScreenshots import ScholarPDFDownloaderWithScreenshots
    USE_SCREENSHOTS = True
except ImportError:
    USE_SCREENSHOTS = False

logger = logging.getLogger(__name__)

# Log screenshot availability at module load
if USE_SCREENSHOTS:
    logger.info("Screenshot-enabled PDF downloader is available")
else:
    logger.warning("Screenshot-enabled PDF downloader is NOT available")


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
    "default": {"max_parallel": 3, "delay": 10, "retry_delay": 20}
}


class ParallelPDFDownloader:
    """Download PDFs in parallel using multiple Chrome instances."""

    def __init__(
        self,
        config: Optional[ScholarConfig] = None,
        auth_manager: Optional['ScholarAuthManager'] = None,
        max_workers: Optional[int] = None,
        use_parallel: Optional[bool] = None,
        delay_between_starts: Optional[int] = None
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
        self.auth_manager = auth_manager
        self.library_manager = LibraryManager(config=self.config)

        # Use cascade configuration: direct params > config > defaults
        pdf_config = self.config.get("pdf_download") or {}

        # Ensure type conversion for numeric parameters
        self.max_workers = int(max_workers if max_workers is not None else pdf_config.get("max_parallel", self._get_optimal_worker_count()))
        self.use_parallel = use_parallel if use_parallel is not None else pdf_config.get("use_parallel", True)
        self.delay_between_starts = int(delay_between_starts if delay_between_starts is not None else pdf_config.get("delay_between_starts", 5))

        # Additional config parameters
        self.default_delay = pdf_config.get("default_delay", 10)
        self.retry_attempts = pdf_config.get("retry_attempts", 3)
        self.timeout = pdf_config.get("timeout", 60)

        # Check authentication status
        self.has_auth = self._check_authentication()

        # Disable parallel if no authentication
        if not self.has_auth:
            logger.warning("No authentication available - disabling parallel downloads")
            self.use_parallel = False
            self.max_workers = 1

        # Track download statistics
        self.stats = {
            "total": 0,
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
            "errors": {}
        }

    def _get_optimal_worker_count(self) -> int:
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

        # Check environment variable first
        if "SCITEX_SCHOLAR_N_JOBS" in os.environ:
            try:
                n_jobs = int(os.environ["SCITEX_SCHOLAR_N_JOBS"])
                logger.info(f"Using {n_jobs} workers from SCITEX_SCHOLAR_N_JOBS")
                return max(1, min(n_jobs, 8))
            except ValueError:
                logger.warning(f"Invalid SCITEX_SCHOLAR_N_JOBS value: {os.environ['SCITEX_SCHOLAR_N_JOBS']}")

        # Check SLURM environment
        if "SLURM_CPUS_PER_TASK" in os.environ:
            try:
                slurm_cpus = int(os.environ["SLURM_CPUS_PER_TASK"])
                n_workers = max(1, slurm_cpus // 2)
                n_workers = min(n_workers, 8)
                logger.info(f"Using {n_workers} workers (SLURM_CPUS_PER_TASK={slurm_cpus})")
                return n_workers
            except ValueError:
                pass

        # Default: use half of available CPUs, capped at 8
        try:
            cpu_count = multiprocessing.cpu_count()
            n_workers = max(1, cpu_count // 2)
            n_workers = min(n_workers, 8)
            logger.info(f"Using {n_workers} workers (CPU count: {cpu_count})")
            return n_workers
        except Exception:
            logger.warning("Could not determine CPU count, using 3 workers")
            return 3

    def _check_authentication(self) -> bool:
        """Check if authentication is available."""
        try:
            # Check for cached auth session
            auth_cache = self.config.get_auth_cache_dir() / "openathens.json"
            if auth_cache.exists():
                with open(auth_cache, 'r') as f:
                    auth_data = json.load(f)
                    # Check for expiry field (correct key name)
                    expiry_str = auth_data.get("expiry")
                    if expiry_str:
                        expires = datetime.fromisoformat(expiry_str)
                        if expires > datetime.now():
                            logger.info(f"Found valid authentication session (expires in {(expires - datetime.now()).total_seconds() / 3600:.1f}h)")
                            return True
                        else:
                            logger.warning(f"Authentication session expired at {expires}")
                    else:
                        logger.warning("No expiry field in authentication cache")
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

    async def download_batch(
        self,
        papers_with_metadata: List[Dict],
        project: str,
        library_dir: Optional[Path] = None
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
            formatter = stdlib_logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.log_file_handler.setFormatter(formatter)

            # Add handler to root logger to capture all logs
            stdlib_logging.getLogger().addHandler(self.log_file_handler)

            logger.info(f"Logging downloads to: {log_file}")

        # Analyze journals/publishers in the batch
        self._analyze_batch(papers_with_metadata)

        try:
            if self.use_parallel and self.max_workers > 1:
                logger.info(f"Starting parallel downloads with {self.max_workers} workers")
                return await self._download_parallel(papers_with_metadata, project, library_dir)
            else:
                logger.info("Using sequential downloads (no parallel)")
                return await self._download_sequential(papers_with_metadata, project, library_dir)
        finally:
            # Clean up log file handler
            if self.log_file_handler:
                import logging as stdlib_logging
                stdlib_logging.getLogger().removeHandler(self.log_file_handler)
                self.log_file_handler.close()
                self.log_file_handler = None

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
            identified_publisher = self._identify_publisher(doi, url, publisher)
            publisher_counts[identified_publisher] = publisher_counts.get(identified_publisher, 0) + 1

        # Log distribution for monitoring
        logger.info(f"Batch contains papers from {len(journal_counts)} journals")
        logger.info(f"Publisher distribution: {publisher_counts}")

        # Adjust workers based on publisher diversity (only if using parallel)
        unique_publishers = len([p for p in publisher_counts if p != "unknown"])
        if unique_publishers > 0 and self.use_parallel:
            # Don't use more workers than unique publishers to avoid hitting same publisher
            original_workers = self.max_workers
            self.max_workers = min(self.max_workers, unique_publishers)
            if self.max_workers != original_workers:
                logger.info(f"Adjusted max_workers from {original_workers} to {self.max_workers} based on {unique_publishers} unique publishers")
            else:
                logger.debug(f"Keeping max_workers at {self.max_workers} ({unique_publishers} unique publishers)")

    async def _download_parallel(
        self,
        papers: List[Dict],
        project: str,
        library_dir: Optional[Path]
    ) -> Dict:
        """Download papers in parallel using multiple workers."""

        # Group papers by publisher for better rate limiting
        publisher_groups = self._group_by_publisher(papers)

        # Create download queue with publisher-aware scheduling
        download_queue = self._create_optimized_queue(publisher_groups)

        # Split queue into chunks for workers
        chunks = [download_queue[i::self.max_workers] for i in range(min(self.max_workers, len(download_queue)))]

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
                    library_dir=library_dir
                )
                tasks.append(task)
                logger.info(f"Started worker {worker_id} with {len(chunk)} papers")

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
        library_dir: Optional[Path]
    ) -> None:
        """Worker function to download papers."""

        logger.info(f"Worker {worker_id}: Starting with {len(papers)} papers")

        # Create worker-specific browser manager
        browser_manager = ScholarBrowserManager(
            config=self.config,
            auth_manager=self.auth_manager,
            browser_mode="stealth",
            chrome_profile_name="system"
        )

        try:
            # Get authenticated browser for this worker
            browser, context = await browser_manager.get_authenticated_browser_and_context_async()

            # Initialize downloaders for this worker
            url_finder = ScholarURLFinder(context=context, config=self.config, use_cache=True)

            # Use screenshot-enabled downloader if available
            if USE_SCREENSHOTS:
                pdf_downloader = ScholarPDFDownloaderWithScreenshots(
                    context=context,
                    config=self.config,
                    use_cache=True,
                    screenshot_interval=2.0,
                    capture_on_failure=True,
                    capture_during_success=True  # Always capture screenshots for documentation
                )
            else:
                pdf_downloader = ScholarPDFDownloader(context=context, config=self.config, use_cache=True)

            # Process papers assigned to this worker
            for i, paper in enumerate(papers):
                try:
                    doi = paper.get("doi")
                    title = paper.get("title", "Unknown")[:50]

                    logger.info(f"Worker {worker_id} [{i+1}/{len(papers)}]: Processing {title}...")

                    # Get publisher-specific delays
                    if doi:
                        # Find URLs for the DOI
                        urls = await url_finder.find_urls(doi)
                        pdf_urls = urls.get("urls_pdf", [])

                        if pdf_urls:
                            # Get rate limits for first URL
                            first_url = pdf_urls[0].get("url") if isinstance(pdf_urls[0], dict) else pdf_urls[0]
                            limits = self._get_publisher_limits(first_url)

                            # Apply rate limiting delay
                            await asyncio.sleep(limits["delay"] + random.uniform(0, 3))  # Add jitter

                            # Download PDF with URL info
                            success = await self._download_single_pdf(
                                paper, pdf_urls, pdf_downloader,
                                project, library_dir, worker_id,
                                url_info=urls  # Pass all URL info including openurl_resolved
                            )

                            if success:
                                self.stats["downloaded"] += 1
                                logger.success(f"Worker {worker_id}: Downloaded {title}")
                            else:
                                # Save URL info even when download failed
                                self._save_url_info_only(paper, urls, project, library_dir)
                                self.stats["failed"] += 1

                        else:
                            logger.warning(f"Worker {worker_id}: No PDF URLs found for {title}")
                            # Save URL info even when no PDF URLs found
                            self._save_url_info_only(paper, urls, project, library_dir)
                            self.stats["skipped"] += 1
                    else:
                        logger.warning(f"Worker {worker_id}: No DOI for {title}")
                        self.stats["skipped"] += 1

                except Exception as e:
                    logger.error(f"Worker {worker_id}: Error processing paper: {e}")
                    self.stats["failed"] += 1

        finally:
            # Clean up browser for this worker
            await browser_manager.close()
            logger.info(f"Worker {worker_id}: Completed")

    async def _download_sequential(
        self,
        papers: List[Dict],
        project: str,
        library_dir: Optional[Path]
    ) -> Dict:
        """Download papers sequentially (fallback when no auth or parallel disabled)."""

        # Use single browser instance
        browser_manager = ScholarBrowserManager(
            config=self.config,
            auth_manager=self.auth_manager,
            browser_mode="stealth",
            chrome_profile_name="system"  # Use system profile for downloads
        )

        try:
            browser, context = await browser_manager.get_authenticated_browser_and_context_async()

            url_finder = ScholarURLFinder(context=context, config=self.config, use_cache=True)

            # Use screenshot-enabled downloader if available
            if USE_SCREENSHOTS:
                pdf_downloader = ScholarPDFDownloaderWithScreenshots(
                    context=context,
                    config=self.config,
                    use_cache=True,
                    screenshot_interval=2.0,
                    capture_on_failure=True,
                    capture_during_success=True  # Always capture screenshots for documentation
                )
            else:
                pdf_downloader = ScholarPDFDownloader(context=context, config=self.config, use_cache=True)

            for i, paper in enumerate(papers):
                try:
                    doi = paper.get("doi")
                    title = paper.get("title", "Unknown")[:50]

                    logger.info(f"[{i+1}/{len(papers)}]: Processing {title}...")

                    if doi:
                        urls = await url_finder.find_urls(doi)
                        pdf_urls = urls.get("urls_pdf", [])

                        if pdf_urls:
                            # Conservative delay for sequential mode
                            await asyncio.sleep(10)

                            success = await self._download_single_pdf(
                                paper, pdf_urls, pdf_downloader,
                                project, library_dir, worker_id=0,
                                url_info=urls  # Pass all URL info including openurl_resolved
                            )

                            if success:
                                self.stats["downloaded"] += 1
                            else:
                                self.stats["failed"] += 1
                        else:
                            self.stats["skipped"] += 1
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
        url_info: Dict = None
    ) -> bool:
        """Download a single PDF and save to library with metadata."""

        doi = paper.get("doi")
        # Use PathManager's consistent ID generation instead of local hash
        paper_id = self.config.path_manager._generate_paper_id(
            doi=doi,
            title=paper.get("title"),
            authors=paper.get("authors"),
            year=paper.get("year")
        ) if doi else None

        # Create .downloading marker to show download in progress (PDF_r status)
        downloading_marker = None
        if paper_id:
            master_dir = self.config.path_manager.get_library_master_dir()
            paper_dir = master_dir / paper_id
            paper_dir.mkdir(parents=True, exist_ok=True)
            downloading_marker = paper_dir / ".downloading"
            downloading_marker.touch()

        try:
            # Try each PDF URL until success
            for pdf_entry in pdf_urls:
                pdf_url = pdf_entry.get("url") if isinstance(pdf_entry, dict) else pdf_entry
                if not pdf_url:
                    continue

                # Download to temp location
                temp_output = Path("/tmp") / f"worker_{worker_id}_{doi.replace('/', '_').replace(':', '_')}.pdf"

                try:
                    # Use screenshot-enabled download if available
                    if USE_SCREENSHOTS and hasattr(pdf_downloader, 'download_from_url_with_screenshots'):
                        logger.info(f"Using screenshot-enabled download for {doi} (paper_id: {paper_id})")
                        result, screenshots = await pdf_downloader.download_from_url_with_screenshots(
                            pdf_url=pdf_url,
                            output_path=temp_output,
                            doi=doi,
                            paper_id=paper_id,
                            retry_with_screenshots=True
                        )
                        if screenshots:
                            logger.info(f"Worker {worker_id}: Captured {len(screenshots)} screenshots for {doi}")
                    else:
                        # Fallback to regular download
                        result = await pdf_downloader.download_from_url(
                            pdf_url=pdf_url,
                            output_path=temp_output
                        )

                    if result and result.exists():
                        # Remove .downloading marker BEFORE saving to library
                        # so symlink shows PDF_s (successful) not PDF_r (running)
                        if downloading_marker and downloading_marker.exists():
                            downloading_marker.unlink()

                        # Save to library with metadata including URL info
                        saved = self._save_to_library(paper, result, project, library_dir, url_info=url_info)

                        # Clean up temp file
                        temp_output.unlink(missing_ok=True)

                        return saved

                except Exception as e:
                    logger.debug(f"Worker {worker_id}: Failed to download from {pdf_url}: {e}")
                    continue

            return False

        finally:
            # Remove .downloading marker if still exists (download failed)
            if downloading_marker and downloading_marker.exists():
                downloading_marker.unlink()

    def _save_to_library(
        self,
        paper: Dict,
        pdf_path: Path,
        project: str,
        library_dir: Optional[Path],
        url_info: Dict = None
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
                year=paper.get("year")
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
                with open(metadata_file, 'r') as f:
                    existing_metadata = json.load(f)
            else:
                existing_metadata = paper.copy()

            # Update with PDF info
            pdf_info = {
                "pdf_path": f"MASTER/{paper_id}/{pdf_filename}",
                "pdf_downloaded_at": datetime.now().isoformat(),
                "pdf_size_bytes": master_pdf_path.stat().st_size
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
                if pdf_path_entry not in existing_metadata["metadata"]["path"]["pdfs"]:
                    existing_metadata["metadata"]["path"]["pdfs"].append(pdf_path_entry)
                    existing_metadata["metadata"]["path"]["pdfs_engines"] = "ParallelPDFDownloader"

                # Update container with PDF download info
                if "container" not in existing_metadata:
                    existing_metadata["container"] = {}
                existing_metadata["container"]["pdf_downloaded_at"] = pdf_info["pdf_downloaded_at"]
                existing_metadata["container"]["pdf_size_bytes"] = pdf_info["pdf_size_bytes"]

                # Add URL information to standardized structure
                if url_info:
                    if "url" not in existing_metadata["metadata"]:
                        existing_metadata["metadata"]["url"] = {}

                    if url_info.get("url_doi"):
                        existing_metadata["metadata"]["url"]["doi"] = url_info["url_doi"]
                        existing_metadata["metadata"]["url"]["doi_engines"] = "ScholarURLFinder"
                    if url_info.get("url_publisher"):
                        existing_metadata["metadata"]["url"]["publisher"] = url_info["url_publisher"]
                        existing_metadata["metadata"]["url"]["publisher_engines"] = "ScholarURLFinder"
                    if url_info.get("url_openurl_query"):
                        existing_metadata["metadata"]["url"]["openurl_query"] = url_info["url_openurl_query"]
                        existing_metadata["metadata"]["url"]["openurl_engines"] = "OpenURLResolver"
                    if url_info.get("url_openurl_resolved"):
                        # Handle both string and list formats
                        resolved = url_info["url_openurl_resolved"]
                        if isinstance(resolved, str):
                            existing_metadata["metadata"]["url"]["openurl_resolved"] = [resolved] if resolved != "skipped" else []
                        else:
                            existing_metadata["metadata"]["url"]["openurl_resolved"] = resolved if resolved else []
                        existing_metadata["metadata"]["url"]["openurl_resolved_engines"] = "OpenURLResolver"
                    if url_info.get("urls_pdf"):
                        existing_metadata["metadata"]["url"]["pdfs"] = url_info["urls_pdf"]
                        existing_metadata["metadata"]["url"]["pdfs_engines"] = "ScholarURLFinder"

                metadata = existing_metadata
            else:
                # Flat format fallback
                metadata = existing_metadata
                metadata.update(pdf_info)
                if url_info:
                    metadata["url_doi"] = url_info.get("url_doi")
                    metadata["url_publisher"] = url_info.get("url_publisher")
                    metadata["url_openurl_query"] = url_info.get("url_openurl_query")
                    metadata["url_openurl_resolved"] = url_info.get("url_openurl_resolved")
                    metadata["urls_pdf"] = url_info.get("urls_pdf", [])

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            # Delegate symlink creation to LibraryManager to maintain single source of truth
            if project:
                master_storage_path = library_dir / "MASTER" / paper_id

                # Use LibraryManager's centralized naming logic
                readable_name = self.library_manager._generate_readable_name(
                    comprehensive_metadata=metadata,
                    master_storage_path=master_storage_path,
                    authors=metadata.get("authors"),
                    year=metadata.get("year"),
                    journal=metadata.get("journal")
                )

                # Create symlink using LibraryManager's method
                self.library_manager._create_project_symlink(
                    master_storage_path=master_storage_path,
                    project=project,
                    readable_name=readable_name
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
        library_dir: Optional[Path]
    ) -> bool:
        """Save URL information to metadata even when PDF download fails."""
        try:
            library_dir = library_dir or self.config.get_library_dir()

            # Use PathManager's consistent ID generation
            doi = paper.get("doi", "")
            paper_id = self.config.path_manager._generate_paper_id(
                doi=doi,
                title=paper.get("title")
            )

            # Check if metadata already exists
            master_dir = library_dir / "MASTER" / paper_id
            metadata_file = master_dir / "metadata.json"

            if not metadata_file.exists():
                # No existing metadata - nothing to update
                logger.debug(f"No existing metadata for {paper_id}, cannot save URL info only")
                return False

            # Read existing standardized metadata
            with open(metadata_file, 'r') as f:
                existing_metadata = json.load(f)

            # Check if we have standardized structure
            if "metadata" not in existing_metadata:
                logger.debug(f"No standardized metadata structure for {paper_id}")
                return False

            # Update URL section in standardized structure
            if "url" not in existing_metadata["metadata"]:
                existing_metadata["metadata"]["url"] = {}

            if url_info:
                if url_info.get("url_doi"):
                    existing_metadata["metadata"]["url"]["doi"] = url_info["url_doi"]
                    if "ScholarURLFinder" not in existing_metadata["metadata"]["url"]["doi_engines"]:
                        existing_metadata["metadata"]["url"]["doi_engines"].append("ScholarURLFinder")
                if url_info.get("url_publisher"):
                    existing_metadata["metadata"]["url"]["publisher"] = url_info["url_publisher"]
                    if "ScholarURLFinder" not in existing_metadata["metadata"]["url"]["publisher_engines"]:
                        existing_metadata["metadata"]["url"]["publisher_engines"].append("ScholarURLFinder")
                if url_info.get("url_openurl_query"):
                    existing_metadata["metadata"]["url"]["openurl_query"] = url_info["url_openurl_query"]
                    if "OpenURLResolver" not in existing_metadata["metadata"]["url"]["openurl_engines"]:
                        existing_metadata["metadata"]["url"]["openurl_engines"].append("OpenURLResolver")
                if url_info.get("url_openurl_resolved"):
                    # Handle both string and list formats
                    resolved = url_info["url_openurl_resolved"]
                    if isinstance(resolved, str):
                        existing_metadata["metadata"]["url"]["openurl_resolved"] = [resolved] if resolved != "skipped" else []
                    else:
                        existing_metadata["metadata"]["url"]["openurl_resolved"] = resolved if resolved else []
                    if "OpenURLResolver" not in existing_metadata["metadata"]["url"]["openurl_resolved_engines"]:
                        existing_metadata["metadata"]["url"]["openurl_resolved_engines"].append("OpenURLResolver")
                if url_info.get("urls_pdf"):
                    existing_metadata["metadata"]["url"]["pdfs"] = url_info["urls_pdf"]
                    if "ScholarURLFinder" not in existing_metadata["metadata"]["url"]["pdfs_engines"]:
                        existing_metadata["metadata"]["url"]["pdfs_engines"].append("ScholarURLFinder")

            # Save updated metadata
            with open(metadata_file, 'w') as f:
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
                if publisher_domain in url_lower or publisher_domain in publisher_lower:
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
            identified_publisher = self._identify_publisher(doi, url, publisher)

            if identified_publisher not in groups:
                groups[identified_publisher] = []
            groups[identified_publisher].append(paper)

        # Log grouping results
        for pub, papers_list in groups.items():
            if papers_list:
                logger.debug(f"Publisher '{pub}': {len(papers_list)} papers")

        return groups

    def _create_optimized_queue(self, publisher_groups: Dict[str, List[Dict]]) -> List[Dict]:
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

    async def test():
        downloader = ParallelPDFDownloader(max_workers=3)

        # Test papers
        papers = [
            {"doi": "10.1038/nature12373", "title": "Test Paper 1"},
            {"doi": "10.1126/science.1234567", "title": "Test Paper 2"},
            {"doi": "10.1371/journal.pone.0123456", "title": "Test Paper 3"},
        ]

        results = await downloader.download_batch(papers, project="test")
        print(f"Download results: {results}")

    asyncio.run(test())