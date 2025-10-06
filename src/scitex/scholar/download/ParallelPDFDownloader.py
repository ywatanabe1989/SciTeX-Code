#!/usr/bin/env python3
"""Parallel PDF downloader with multiple Chrome instances for improved performance."""

import asyncio
import hashlib
import json
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

logger = logging.getLogger(__name__)


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
        max_workers: Optional[int] = None,
        use_parallel: Optional[bool] = None,
        delay_between_starts: Optional[int] = None
    ):
        """Initialize parallel downloader.

        Args:
            config: Scholar configuration
            max_workers: Maximum number of parallel Chrome instances (overrides config)
            use_parallel: Whether to use parallel downloads (overrides config)
            delay_between_starts: Delay in seconds between starting workers (overrides config)
        """
        self.config = config or ScholarConfig()

        # Use cascade configuration: direct params > config > defaults
        pdf_config = self.config.get("pdf_download") or {}

        self.max_workers = max_workers if max_workers is not None else pdf_config.get("max_parallel", 3)
        self.use_parallel = use_parallel if use_parallel is not None else pdf_config.get("use_parallel", True)
        self.delay_between_starts = delay_between_starts if delay_between_starts is not None else pdf_config.get("delay_between_starts", 5)

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

    def _check_authentication(self) -> bool:
        """Check if authentication is available."""
        try:
            # Check for cached auth session
            auth_cache = self.config.get_auth_cache_dir() / "openathens.json"
            if auth_cache.exists():
                with open(auth_cache, 'r') as f:
                    auth_data = json.load(f)
                    expires = datetime.fromisoformat(auth_data.get("expires", "1970-01-01"))
                    if expires > datetime.now():
                        logger.info("Found valid authentication session")
                        return True
            logger.warning("No valid authentication found")
            return False
        except Exception as e:
            logger.warning(f"Error checking authentication: {e}")
            return False

    def _get_publisher_limits(self, url: str) -> Dict:
        """Get rate limits for a specific publisher."""
        for publisher, limits in PUBLISHER_LIMITS.items():
            if publisher in url.lower():
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

        # Analyze journals/publishers in the batch
        self._analyze_batch(papers_with_metadata)

        if self.use_parallel and self.max_workers > 1:
            logger.info(f"Starting parallel downloads with {self.max_workers} workers")
            return await self._download_parallel(papers_with_metadata, project, library_dir)
        else:
            logger.info("Using sequential downloads (no parallel)")
            return await self._download_sequential(papers_with_metadata, project, library_dir)

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

        # Adjust workers based on publisher diversity
        unique_publishers = len([p for p in publisher_counts if p != "unknown"])
        if unique_publishers > 0:
            # Don't use more workers than unique publishers to avoid hitting same publisher
            self.max_workers = min(self.max_workers, unique_publishers)
            logger.info(f"Adjusted max_workers to {self.max_workers} based on {unique_publishers} unique publishers")

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
            browser_mode="stealth",
            profile_suffix=f"_worker_{worker_id}"
        )

        try:
            # Get authenticated browser for this worker
            browser, context = await browser_manager.get_authenticated_browser_and_context_async()

            # Initialize downloaders for this worker
            url_finder = ScholarURLFinder(context=context, config=self.config, use_cache=True)
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

                            # Download PDF
                            success = await self._download_single_pdf(
                                paper, pdf_urls, pdf_downloader,
                                project, library_dir, worker_id
                            )

                            if success:
                                self.stats["downloaded"] += 1
                                logger.success(f"Worker {worker_id}: Downloaded {title}")
                            else:
                                self.stats["failed"] += 1

                        else:
                            logger.warning(f"Worker {worker_id}: No PDF URLs found for {title}")
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
        browser_manager = ScholarBrowserManager(config=self.config, browser_mode="stealth")

        try:
            browser, context = await browser_manager.get_authenticated_browser_and_context_async()

            url_finder = ScholarURLFinder(context=context, config=self.config, use_cache=True)
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
                                project, library_dir, worker_id=0
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
        worker_id: int
    ) -> bool:
        """Download a single PDF and save to library with metadata."""

        doi = paper.get("doi")

        # Try each PDF URL until success
        for pdf_entry in pdf_urls:
            pdf_url = pdf_entry.get("url") if isinstance(pdf_entry, dict) else pdf_entry
            if not pdf_url:
                continue

            # Download to temp location
            temp_output = Path("/tmp") / f"worker_{worker_id}_{doi.replace('/', '_').replace(':', '_')}.pdf"

            try:
                result = await pdf_downloader.download_from_url(
                    pdf_url=pdf_url,
                    output_path=temp_output
                )

                if result and result.exists():
                    # Save to library with metadata
                    saved = self._save_to_library(paper, result, project, library_dir)

                    # Clean up temp file
                    temp_output.unlink(missing_ok=True)

                    return saved

            except Exception as e:
                logger.debug(f"Worker {worker_id}: Failed to download from {pdf_url}: {e}")
                continue

        return False

    def _save_to_library(
        self,
        paper: Dict,
        pdf_path: Path,
        project: str,
        library_dir: Optional[Path]
    ) -> bool:
        """Save downloaded PDF to library with proper structure and metadata."""

        try:
            library_dir = library_dir or self.config.get_library_dir()

            # Generate unique ID from DOI
            doi = paper.get("doi", "")
            paper_id = hashlib.md5(doi.encode()).hexdigest()[:8].upper()

            # Create MASTER storage directory
            master_dir = library_dir / "MASTER" / paper_id
            master_dir.mkdir(parents=True, exist_ok=True)

            # Copy PDF to MASTER
            pdf_filename = f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
            master_pdf_path = master_dir / pdf_filename
            shutil.copy2(pdf_path, master_pdf_path)

            # Update metadata with PDF info
            metadata_file = master_dir / "metadata.json"
            metadata = paper.copy()
            metadata.update({
                "pdf_path": f"MASTER/{paper_id}/{pdf_filename}",
                "pdf_downloaded_at": datetime.now().isoformat(),
                "pdf_size_bytes": master_pdf_path.stat().st_size
            })

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)

            # Create project symlink with enhanced naming
            if project:
                self._create_project_symlink(paper, paper_id, project, library_dir)

            return True

        except Exception as e:
            logger.error(f"Failed to save to library: {e}")
            return False

    def _create_project_symlink(
        self,
        paper: Dict,
        paper_id: str,
        project: str,
        library_dir: Path
    ) -> None:
        """Create project symlink with CC-IF-Year-Author-Journal naming."""

        try:
            project_dir = library_dir / project
            project_dir.mkdir(parents=True, exist_ok=True)

            # Generate readable name
            cc = paper.get("citation_count", 0) or 0
            if_val = paper.get("journal_impact_factor", 0.0) or 0.0
            year = paper.get("year", 0) or 0

            first_author = "Unknown"
            authors = paper.get("authors", [])
            if authors and len(authors) > 0:
                author_parts = authors[0].split()
                first_author = author_parts[-1] if len(author_parts) > 1 else author_parts[0]
                first_author = "".join(c for c in first_author if c.isalnum() or c == "-")[:20]

            journal = paper.get("journal", "Unknown")
            journal_clean = "".join(c for c in journal if c.isalnum() or c in " ").replace(" ", "")[:30]
            if not journal_clean:
                journal_clean = "Unknown"

            readable_name = f"CC{cc:06d}-IF{int(if_val):03d}-{year:04d}-{first_author}-{journal_clean}"

            # Create symlink
            symlink_path = project_dir / readable_name
            if not symlink_path.exists():
                symlink_path.symlink_to(f"../MASTER/{paper_id}")

        except Exception as e:
            logger.debug(f"Failed to create project symlink: {e}")

    def _identify_publisher(self, doi: str, url: str, publisher: str) -> str:
        """Identify publisher from DOI, URL, or metadata."""
        # Check DOI patterns
        doi_lower = doi.lower()
        url_lower = url.lower()
        publisher_lower = publisher.lower()

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