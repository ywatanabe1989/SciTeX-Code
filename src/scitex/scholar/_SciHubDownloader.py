#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 15:37:05 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_scihub_downloader.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_scihub_downloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Sci-Hub PDF downloader integration for SciTeX Scholar.

This module provides parallel PDF downloading from Sci-Hub using Selenium
for papers that are not available through open access channels.

⚖️ IMPORTANT: This tool should only be used for legitimate academic purposes.
Please read ETHICAL_USAGE.md for guidelines on responsible use.
"""

import asyncio
import logging
import re
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..errors import PDFDownloadError, ScholarError
from ._Paper import Paper

logger = logging.getLogger(__name__)

# Thread-local storage for drivers
thread_local = threading.local()

# Track if we've shown the ethical usage warning
_ethical_warning_shown = False


def _show_ethical_warning():
    """Display ethical usage warning once per session."""
    global _ethical_warning_shown
    if not _ethical_warning_shown:
        warnings.warn(
            "\n⚖️  ETHICAL USAGE NOTICE: "
            "Please use this tool responsibly and only for legitimate academic purposes. "
            "Ensure you have proper access rights and comply with copyright laws. "
            "See ETHICAL_USAGE.md for guidelines.",
            UserWarning,
            stacklevel=3,
        )
        _ethical_warning_shown = True


class SciHubDownloader:
    """
    Downloads PDFs from Sci-Hub using headless Chrome.
    """

    def __init__(
        self,
        download_dir: Union[str, Path] = "./scihub_pdfs",
        timeout: int = 30,
        max_workers: int = 4,
        max_retries: int = 3,
        mirrors: Optional[List[str]] = None,
    ):
        """
        Initialize Sci-Hub downloader.

        Args:
            download_dir: Directory to save PDFs
            timeout: Download timeout in seconds
            max_workers: Maximum parallel workers
            max_retries: Maximum retry attempts per DOI
            mirrors: List of Sci-Hub mirrors to try
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.mirrors = mirrors or [
            "https://sci-hub.se/",
            "https://sci-hub.st/",
            "https://sci-hub.ru/",
        ]

    def setup_driver(self) -> webdriver.Chrome:
        """Setup headless Chrome driver with options to avoid detection."""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            raise ScholarError(
                "webdriver-manager not installed",
                context={"module": "webdriver-manager"},
                suggestion="Install with: pip install webdriver-manager selenium",
            )

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Reduce memory usage
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute script to remove webdriver property
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return driver

    def get_driver(self) -> webdriver.Chrome:
        """Get or create a driver for the current thread."""
        if not hasattr(thread_local, "driver"):
            thread_local.driver = self.setup_driver()
        return thread_local.driver

    def cleanup_driver(self) -> None:
        """Cleanup driver for the current thread."""
        if hasattr(thread_local, "driver"):
            thread_local.driver.quit()
            delattr(thread_local, "driver")

    def _extract_pdf_url(self, doi: str) -> Optional[str]:
        """Extract PDF URL from Sci-Hub page using Selenium."""
        driver = self.get_driver()

        for mirror in self.mirrors:
            try:
                url = mirror + doi
                driver.set_page_load_timeout(self.timeout)
                driver.get(url)

                # Wait for dynamic content to load
                time.sleep(3)

                # Method 1: Look for embed element with PDF
                try:
                    embed_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "embed[src*='.pdf']")
                        )
                    )
                    pdf_url = embed_element.get_attribute("src")
                    if pdf_url:
                        if pdf_url.startswith("//"):
                            pdf_url = "https:" + pdf_url
                        return pdf_url.split("#")[0]
                except:
                    pass

                # Method 2: Look for iframe with PDF
                try:
                    iframe_element = driver.find_element(
                        By.CSS_SELECTOR, "iframe[src*='.pdf']"
                    )
                    pdf_url = iframe_element.get_attribute("src")
                    if pdf_url:
                        if pdf_url.startswith("//"):
                            pdf_url = "https:" + pdf_url
                        return pdf_url.split("#")[0]
                except:
                    pass

                # Method 3: Look for download button onclick
                try:
                    save_button = driver.find_element(
                        By.XPATH, "//button[contains(@onclick, '.pdf')]"
                    )
                    onclick = save_button.get_attribute("onclick")
                    if onclick:
                        match = re.search(
                            r"location\.href='([^']*\.pdf[^']*)'", onclick
                        )
                        if match:
                            pdf_url = match.group(1)
                            if pdf_url.startswith("//"):
                                pdf_url = "https:" + pdf_url
                            return pdf_url.split("#")[0]
                except:
                    pass

                # Method 4: Regex search in page source
                page_source = driver.page_source

                # Look for embed src
                embed_matches = re.findall(
                    r'<embed[^>]*src="([^"]*\.pdf[^"]*)"', page_source
                )
                if embed_matches:
                    pdf_url = embed_matches[0]
                    if pdf_url.startswith("//"):
                        pdf_url = "https:" + pdf_url
                    return pdf_url.split("#")[0]

                # Look for button onclick
                onclick_matches = re.findall(
                    r'location\.href=[\'"]([^\'\"]*\.pdf[^\'\"]*)[\'"]',
                    page_source,
                )
                if onclick_matches:
                    pdf_url = onclick_matches[0]
                    if pdf_url.startswith("//"):
                        pdf_url = "https:" + pdf_url
                    return pdf_url.split("#")[0]

                # Look for any PDF URLs
                pdf_matches = re.findall(
                    r'https?://[^\s"\']*\.pdf[^\s"\']*', page_source
                )
                if pdf_matches:
                    return pdf_matches[0].split("#")[0]

            except Exception as e:
                logger.debug(f"Error with {mirror}: {e}")
                continue

        return None

    def _download_pdf(self, pdf_url: str, filepath: Path) -> Tuple[bool, str]:
        """Download PDF from URL."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            response = requests.get(
                pdf_url, headers=headers, stream=True, timeout=self.timeout
            )
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True, f"Downloaded: {filepath.name}"

        except Exception as e:
            return False, f"Download failed: {str(e)}"

    def _process_single_doi(
        self, doi: str, custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a single DOI."""
        try:
            logger.info(f"Processing DOI: {doi}")

            # Extract PDF URL from Sci-Hub
            pdf_url = self._extract_pdf_url(doi)

            if pdf_url:
                # Generate filename
                if custom_filename:
                    filename = self.download_dir / custom_filename
                else:
                    safe_doi = re.sub(r'[/\\:*?"<>|]', "_", doi)
                    filename = self.download_dir / f"{safe_doi}.pdf"

                # Download PDF
                success, message = self._download_pdf(pdf_url, filename)

                return {
                    "doi": doi,
                    "success": success,
                    "pdf_url": pdf_url,
                    "filename": str(filename),
                    "message": message,
                }
            else:
                return {
                    "doi": doi,
                    "success": False,
                    "pdf_url": None,
                    "filename": None,
                    "message": f"No PDF found on Sci-Hub for {doi}",
                }

        except Exception as e:
            return {
                "doi": doi,
                "success": False,
                "pdf_url": None,
                "filename": None,
                "message": f"Error processing {doi}: {str(e)}",
            }

    def download_dois(
        self, dois: List[str], show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Download PDFs for multiple DOIs in parallel.

        Args:
            dois: List of DOIs to download
            show_progress: Show download progress

        Returns:
            List of download results
        """
        results = []

        if show_progress:
            print(
                f"Processing {len(dois)} DOIs with {self.max_workers} workers..."
            )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_doi = {
                executor.submit(self._process_single_doi, doi): doi
                for doi in dois
            }

            # Process completed tasks
            for future in as_completed(future_to_doi):
                result = future.result()
                results.append(result)

                if show_progress:
                    if result["success"]:
                        print(f"✓ {result['doi']}: {result['message']}")
                    else:
                        print(f"✗ {result['doi']}: {result['message']}")

        # Cleanup drivers
        self.cleanup_driver()

        # Summary
        if show_progress:
            successful = sum(1 for r in results if r["success"])
            print(
                f"\nSummary: {successful}/{len(results)} papers downloaded successfully"
            )

        return results

    async def download_papers(
        self, papers: List[Paper], show_progress: bool = True
    ) -> Dict[str, Path]:
        """
        Download PDFs for a list of Paper objects.

        Args:
            papers: List of Paper objects with DOIs
            show_progress: Show download progress

        Returns:
            Dictionary mapping paper identifiers to downloaded file paths
        """
        # Extract DOIs from papers
        dois_to_papers = {}
        for paper in papers:
            if paper.doi:
                dois_to_papers[paper.doi] = paper

        if not dois_to_papers:
            logger.info("No papers with DOIs to download")
            return {}

        # Download PDFs using thread pool
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            self.download_dois,
            list(dois_to_papers.keys()),
            show_progress,
        )

        # Map results back to papers
        downloaded = {}
        for result in results:
            if result["success"] and result["doi"] in dois_to_papers:
                paper = dois_to_papers[result["doi"]]
                downloaded[paper.get_identifier()] = Path(result["filename"])

        return downloaded


async def dois_to_local_pdfs_async(
    dois: Union[List[str], List[Paper]],
    download_dir: Union[str, Path] = "./scihub_pdfs",
    max_workers: int = 4,
    show_progress: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """
    Asynchronously download PDFs from Sci-Hub for a list of DOIs or Paper objects.

    This function provides a simple interface to download PDFs that may not be
    available through open access channels. It uses Selenium with headless Chrome
    to extract PDF URLs from Sci-Hub and downloads them in parallel.

    ⚖️ ETHICAL USAGE NOTICE:
    This tool should only be used for legitimate academic purposes. Please ensure you:
    - Have legitimate access rights to the papers
    - Comply with your institution's policies
    - Respect copyright and intellectual property laws
    - Use for research/educational purposes only

    See ETHICAL_USAGE.md for detailed guidelines.

    Args:
        dois: List of DOI strings or Paper objects with DOIs
        download_dir: Directory to save PDFs (default: "./scihub_pdfs")
        max_workers: Number of parallel download workers (default: 4)
        show_progress: Show download progress (default: True)
        **kwargs: Additional arguments for SciHubDownloader

    Returns:
        Dictionary with download statistics and results:
        - 'successful': Number of successful downloads
        - 'failed': Number of failed downloads
        - 'results': List of detailed results for each DOI
        - 'downloaded_files': Dict mapping DOIs to file paths

    Examples:
        >>> # Download from DOI strings
        >>> dois = ["10.1162/jocn.2008.21020", "10.1093/brain/awt276"]
        >>> results = await dois_to_local_pdfs_async(dois)

        >>> # Download from Paper objects
        >>> from scitex.scholar import Scholar
        >>> scholar = Scholar()
        >>> papers = scholar.search("deep learning", limit=10)
        >>> results = await dois_to_local_pdfs_async(papers.papers)

        >>> # Custom configuration
        >>> results = await dois_to_local_pdfs_async(
        ...     dois,
        ...     download_dir="./my_pdfs",
        ...     max_workers=8,
        ...     timeout=60
        ... )
    """
    # Show ethical warning once per session
    _show_ethical_warning()

    # Handle both DOI strings and Paper objects
    if dois and isinstance(dois[0], Paper):
        # Extract DOIs from Paper objects
        doi_list = [p.doi for p in dois if p.doi]
        paper_map = {p.doi: p for p in dois if p.doi}
    else:
        doi_list = [d for d in dois if d]  # Filter out empty strings
        paper_map = {}

    if not doi_list:
        return {
            "successful": 0,
            "failed": 0,
            "results": [],
            "downloaded_files": {},
        }

    # Initialize downloader
    downloader = SciHubDownloader(
        download_dir=download_dir, max_workers=max_workers, **kwargs
    )

    # Download PDFs
    if paper_map:
        # Download using Paper objects
        downloaded = await downloader.download_papers(
            [paper_map[doi] for doi in doi_list], show_progress=show_progress
        )

        # Get detailed results
        results = []
        for doi in doi_list:
            paper = paper_map[doi]
            if paper.get_identifier() in downloaded:
                results.append(
                    {
                        "doi": doi,
                        "success": True,
                        "filename": str(downloaded[paper.get_identifier()]),
                        "message": "Downloaded successfully",
                    }
                )
            else:
                results.append(
                    {
                        "doi": doi,
                        "success": False,
                        "filename": None,
                        "message": "Download failed",
                    }
                )
    else:
        # Download using DOI strings
        results = downloader.download_dois(
            doi_list, show_progress=show_progress
        )

    # Compile statistics
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    # Create DOI to file mapping
    downloaded_files = {
        r["doi"]: r["filename"]
        for r in results
        if r["success"] and r["filename"]
    }

    return {
        "successful": successful,
        "failed": failed,
        "results": results,
        "downloaded_files": downloaded_files,
    }


def dois_to_local_pdfs(
    dois: Union[List[str], List[Paper]],
    download_dir: Union[str, Path] = "./scihub_pdfs",
    max_workers: int = 4,
    show_progress: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """
    Download PDFs from Sci-Hub for a list of DOIs or Paper objects.

    This function provides a simple interface to download PDFs that may not be
    available through open access channels. It uses Selenium with headless Chrome
    to extract PDF URLs from Sci-Hub and downloads them in parallel.

    ⚖️ ETHICAL USAGE NOTICE:
    This tool should only be used for legitimate academic purposes. Please ensure you:
    - Have legitimate access rights to the papers
    - Comply with your institution's policies
    - Respect copyright and intellectual property laws
    - Use for research/educational purposes only

    See ETHICAL_USAGE.md for detailed guidelines.

    Args:
        dois: List of DOI strings or Paper objects with DOIs
        download_dir: Directory to save PDFs (default: "./scihub_pdfs")
        max_workers: Number of parallel download workers (default: 4)
        show_progress: Show download progress (default: True)
        **kwargs: Additional arguments for SciHubDownloader

    Returns:
        Dictionary with download statistics and results:
        - 'successful': Number of successful downloads
        - 'failed': Number of failed downloads
        - 'results': List of detailed results for each DOI
        - 'downloaded_files': Dict mapping DOIs to file paths

    Examples:
        >>> from scitex.scholar import dois_to_local_pdfs
        >>> dois = ["10.1162/jocn.2008.21020", "10.1093/brain/awt276"]
        >>> results = dois_to_local_pdfs(dois)

        >>> # With custom settings
        >>> results = dois_to_local_pdfs(
        ...     dois,
        ...     download_dir="./my_pdfs",
        ...     max_workers=8
        ... )
    """
    # Show ethical warning once per session
    _show_ethical_warning()

    # Create event loop if needed
    try:
        loop = asyncio.get_running_loop()
        # If we're already in an event loop, we can't use asyncio.run
        raise RuntimeError(
            "Cannot use synchronous version inside an async context. "
            "Use 'await dois_to_local_pdfs_async()' instead."
        )
    except RuntimeError:
        # No event loop running, safe to create one
        return asyncio.run(
            dois_to_local_pdfs_async(
                dois,
                download_dir=download_dir,
                max_workers=max_workers,
                show_progress=show_progress,
                **kwargs,
            )
        )


# Export classes and functions
__all__ = [
    "SciHubDownloader",
    "dois_to_local_pdfs",
    "dois_to_local_pdfs_async",
]

# EOF
