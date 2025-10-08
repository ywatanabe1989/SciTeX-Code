#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry PDF downloads for neurovista entries that have PDF URLs but no downloaded files.

This script:
1. Scans neurovista library for entries without PDFs
2. Uses metadata to find PDF URLs
3. Attempts download using ScholarPDFDownloader
4. Reports success/failure for each entry
"""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scitex import logging
from scitex.scholar.browser.local import ScholarBrowserManager
from scitex.scholar.download import ScholarPDFDownloaderWithScreenshots
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


async def retry_failed_downloads_async(
    library_path: str = None,
    project: str = "neurovista",
    max_retries: int = 3
):
    """
    Retry downloading PDFs for entries that failed previously.

    Args:
        library_path: Path to library directory (defaults to neurovista)
        project: Project name
        max_retries: Maximum retry attempts per entry
    """
    # Setup
    if library_path is None:
        library_path = Path("/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/library/neurovista")
    else:
        library_path = Path(library_path)

    logger.info(f"Scanning library: {library_path}")

    # Find entries without PDFs
    entries = [d for d in library_path.iterdir() if d.is_dir() and d.name != "info"]

    failed_entries = []
    for entry_dir in entries:
        # Check for PDF files
        pdf_files = list(entry_dir.glob("*.pdf"))

        # Read metadata
        metadata_file = entry_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        if not pdf_files:
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Check if PDF URLs are available
            pdf_urls = metadata.get("metadata", {}).get("url", {}).get("pdfs", [])
            if pdf_urls:
                failed_entries.append({
                    "dir": entry_dir,
                    "metadata": metadata,
                    "pdf_urls": pdf_urls
                })

    logger.info(f"Found {len(failed_entries)} entries without PDFs but with PDF URLs")

    if not failed_entries:
        logger.success("No failed entries to retry!")
        return

    # Initialize browser and downloader
    config = ScholarConfig()
    browser_manager = ScholarBrowserManager(
        config=config,
        browser_mode="interactive"  # Use interactive mode (Cloudflare blocking is welcome)
    )

    try:
        await browser_manager.start_async()
        context = browser_manager.context

        downloader = ScholarPDFDownloaderWithScreenshots(
            context=context,
            config=config
        )

        # Retry each entry
        success_count = 0
        fail_count = 0

        for i, entry in enumerate(failed_entries, 1):
            entry_dir = entry["dir"]
            metadata = entry["metadata"]
            pdf_urls = entry["pdf_urls"]

            title = metadata.get("metadata", {}).get("basic", {}).get("title", "Unknown")[:60]
            doi = metadata.get("metadata", {}).get("id", {}).get("doi", "No DOI")

            logger.info(f"\n[{i}/{len(failed_entries)}] Retrying: {entry_dir.name}")
            logger.info(f"  Title: {title}")
            logger.info(f"  DOI: {doi}")
            logger.info(f"  PDF URLs: {len(pdf_urls)}")

            # Try each PDF URL
            downloaded = False
            for j, pdf_info in enumerate(pdf_urls, 1):
                pdf_url = pdf_info.get("url") if isinstance(pdf_info, dict) else pdf_info
                source = pdf_info.get("source", "unknown") if isinstance(pdf_info, dict) else "unknown"

                logger.info(f"  Trying URL {j}/{len(pdf_urls)} ({source}): {pdf_url[:80]}...")

                try:
                    # Attempt download
                    result = await downloader.download_pdf_async(
                        pdf_url=pdf_url,
                        output_dir=entry_dir,
                        filename=None,  # Will use default naming
                        max_retries=max_retries
                    )

                    if result and result.get("success"):
                        logger.success(f"  ✓ Downloaded successfully!")
                        success_count += 1
                        downloaded = True

                        # Update metadata
                        metadata["container"]["pdf_downloaded_at"] = result.get("downloaded_at")
                        metadata["container"]["pdf_size_bytes"] = result.get("size_bytes")

                        with open(entry_dir / "metadata.json", "w") as f:
                            json.dump(metadata, f, indent=2)

                        break  # Success, no need to try other URLs

                except Exception as e:
                    logger.warning(f"  ✗ Failed: {type(e).__name__}: {str(e)[:100]}")
                    continue

            if not downloaded:
                logger.fail(f"  ✗ All URLs failed for {entry_dir.name}")
                fail_count += 1

        # Summary
        logger.info("\n" + "="*70)
        logger.info("SUMMARY:")
        logger.success(f"  Successfully downloaded: {success_count}/{len(failed_entries)}")
        if fail_count > 0:
            logger.fail(f"  Failed: {fail_count}/{len(failed_entries)}")
        logger.info("="*70)

    finally:
        await browser_manager.stop_async()


def main():
    """Command-line entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Retry PDF downloads for failed neurovista entries"
    )
    parser.add_argument(
        "--library",
        type=str,
        default=None,
        help="Path to library directory (default: neurovista)"
    )
    parser.add_argument(
        "--project",
        type=str,
        default="neurovista",
        help="Project name (default: neurovista)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per entry (default: 3)"
    )

    args = parser.parse_args()

    # Run async function
    asyncio.run(retry_failed_downloads_async(
        library_path=args.library,
        project=args.project,
        max_retries=args.max_retries
    ))


if __name__ == "__main__":
    main()

# EOF
