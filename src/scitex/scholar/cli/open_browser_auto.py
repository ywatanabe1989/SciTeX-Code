#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open browser with automatic PDF download tracking and linking.

This CLI tool uses Playwright's download API to track which paper each
download belongs to, enabling automatic organization without filesystem monitoring.

Usage:
    # Auto-track and link downloads
    python -m scitex.scholar.cli.open_browser_auto --project neurovista

    # Include pending papers
    python -m scitex.scholar.cli.open_browser_auto --project neurovista --all
"""

import argparse
import json
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.utils.url_utils import get_best_url
from scitex.logging import getLogger

logger = getLogger(__name__)


def get_failed_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with failed downloads."""
    from scitex.scholar.cli.open_browser import get_failed_papers as _get_failed
    return _get_failed(project, config)


def get_pending_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get papers with pending downloads."""
    from scitex.scholar.cli.open_browser import get_pending_papers as _get_pending
    return _get_pending(project, config)


def generate_proper_filename(metadata: dict) -> str:
    """Generate proper filename from metadata.

    Args:
        metadata: Paper metadata dict

    Returns:
        Proper filename like "Author-2024-Journal.pdf"
    """
    meta = metadata.get("metadata", {})
    basic = meta.get("basic", {})

    year = basic.get("year", "XXXX")
    first_author = basic.get("first_author_lastname", "Unknown")
    journal = basic.get("journal", "Unknown")

    # Clean journal name
    journal_clean = "".join(c for c in journal if c.isalnum() or c in (' ', '-', '_'))[:50]
    journal_clean = journal_clean.strip()

    return f"{first_author}-{year}-{journal_clean}.pdf"


def handle_download(download, paper_id: str, paper_title: str, config: ScholarConfig):
    """Handle a download event and link to library.

    Args:
        download: Playwright download object
        paper_id: Paper ID (8-digit hex)
        paper_title: Paper title for logging
        config: Scholar configuration
    """
    try:
        # Get paper directory
        master_dir = config.path_manager.get_library_master_dir()
        paper_dir = master_dir / paper_id

        if not paper_dir.exists():
            logger.error(f"Paper directory not found: {paper_dir}")
            return

        # Read metadata for proper filename
        metadata_file = paper_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            proper_name = generate_proper_filename(metadata)
        else:
            # Fallback to download filename
            proper_name = download.suggested_filename

        # Save to paper directory
        dest_path = paper_dir / proper_name

        # Download and save
        download.save_as(str(dest_path))

        logger.success(f"Downloaded: {proper_name}")
        logger.info(f"  Paper: {paper_title[:60]}...")
        logger.info(f"  ID: {paper_id}")
        logger.info(f"  Location: {dest_path}")

        # Remove screenshots directory (download succeeded)
        screenshot_dir = paper_dir / "screenshots"
        if screenshot_dir.exists():
            import shutil
            shutil.rmtree(screenshot_dir)
            logger.info(f"  Removed screenshots (download succeeded)")

        # Update metadata with download timestamp
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)

            if "container" not in metadata:
                metadata["container"] = {}

            metadata["container"]["pdf_downloaded_at"] = datetime.now().isoformat()
            metadata["container"]["pdf_download_method"] = "manual_browser_auto"

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        logger.success(f"Successfully linked PDF for {paper_id}")

    except Exception as e:
        logger.error(f"Failed to handle download for {paper_id}: {e}")


def open_browser_with_auto_tracking(
    papers: List[Dict],
    project: str,
    config: ScholarConfig,
    profile: str = None
) -> None:
    """Open browser with automatic download tracking.

    Each tab knows which paper it belongs to, so downloads are automatically
    linked to the correct library location.

    Args:
        papers: List of paper metadata dicts
        project: Project name
        config: Scholar configuration
        profile: Browser profile name
    """
    from playwright.sync_api import sync_playwright

    if not papers:
        logger.info("No papers to open")
        return

    # Build list of papers with URLs
    papers_to_open = []
    for paper in papers:
        paper_id = paper.get("paper_id")
        if not paper_id:
            continue

        # Get best URL using standardized utility
        url = get_best_url(
            openurl_resolved=paper.get("openurl_resolved"),
            url_publisher=paper.get("url_publisher"),
            url_doi=paper.get("url_doi"),
            doi=paper.get("doi")
        )

        if url:
            papers_to_open.append({
                "paper_id": paper_id,
                "title": paper.get("title", "Unknown"),
                "url": url,
                "doi": paper.get("doi", ""),
            })
        else:
            logger.warning(f"No URL for {paper.get('title', 'Unknown')[:50]}...")

    if not papers_to_open:
        logger.warning("No papers with URLs to open")
        return

    logger.info(f"Opening {len(papers_to_open)} URLs with auto-tracking...")

    # Get browser profile
    if profile:
        profile_dir = config.path_manager.get_chrome_cache_dir(profile)
    else:
        profile_dir = config.path_manager.get_chrome_cache_dir("system")

    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser with profile
        browser = p.chromium.launch_persistent_context(
            str(profile_dir),
            headless=False,
            accept_downloads=True,  # Enable download tracking
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=UserAgentClientHint',
            ]
        )

        # Track which page belongs to which paper
        page_to_paper = {}
        download_count = 0

        def create_download_handler(paper_info: dict):
            """Create download handler for specific paper."""
            def on_download(download):
                nonlocal download_count
                download_count += 1

                logger.info(f"\nDownload {download_count} detected:")
                logger.info(f"  File: {download.suggested_filename}")
                logger.info(f"  Paper: {paper_info['title'][:60]}...")

                handle_download(
                    download,
                    paper_info["paper_id"],
                    paper_info["title"],
                    config
                )

            return on_download

        # Open first paper
        if browser.pages:
            page = browser.pages[0]
        else:
            page = browser.new_page()

        paper_info = papers_to_open[0]
        page.on("download", create_download_handler(paper_info))
        page_to_paper[page] = paper_info

        try:
            page.goto(paper_info["url"], timeout=30000)
            logger.success(f"[{paper_info['paper_id']}] {paper_info['title'][:60]}...")
        except Exception as e:
            logger.warning(f"Failed to load: {e}")

        # Open remaining papers in new tabs
        for paper_info in papers_to_open[1:]:
            new_page = browser.new_page()
            new_page.on("download", create_download_handler(paper_info))
            page_to_paper[new_page] = paper_info

            try:
                new_page.goto(paper_info["url"], timeout=30000)
                logger.success(f"[{paper_info['paper_id']}] {paper_info['title'][:60]}...")
            except Exception as e:
                logger.warning(f"Failed to load: {e}")

        # Also track new tabs created by user (e.g., clicking links)
        def on_page_created(new_page):
            """Track new tabs created during session."""
            # Try to determine which paper this new tab belongs to
            # by checking the opener page
            opener = new_page.opener
            if opener and opener in page_to_paper:
                parent_paper = page_to_paper[opener]
                logger.info(f"New tab opened from: {parent_paper['title'][:40]}...")

                # Inherit download handler from parent
                new_page.on("download", create_download_handler(parent_paper))
                page_to_paper[new_page] = parent_paper
            else:
                # Orphan tab - log but don't track
                logger.warning("New tab opened (no parent tracking)")

        browser.on("page", on_page_created)

        # Show instructions
        logger.info(f"\n{'='*70}")
        logger.info(f"Browser opened with {len(papers_to_open)} papers")
        logger.info("Download tracking ACTIVE - PDFs will auto-link to library")
        logger.info("")
        logger.info("Instructions:")
        logger.info("  1. Use Zotero Connector to download PDFs")
        logger.info("  2. Or click 'Download PDF' / 'Save PDF' on publisher sites")
        logger.info("  3. PDFs will automatically save to correct library location")
        logger.info("  4. Symlinks will update to show PDF_s status")
        logger.info("")
        logger.info("Tips:")
        logger.info("  - Each tab tracks its own paper")
        logger.info("  - New tabs from links inherit parent paper tracking")
        logger.info("  - Multiple downloads per paper are supported")
        logger.info("")
        logger.info("Press Ctrl+C when done")
        logger.info(f"{'='*70}\n")

        try:
            # Keep browser open
            page.wait_for_event("close", timeout=0)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        finally:
            logger.info(f"\nSession summary:")
            logger.info(f"  Papers opened: {len(papers_to_open)}")
            logger.info(f"  PDFs downloaded: {download_count}")

            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Open browser with automatic download tracking and linking"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name (e.g., neurovista, pac)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Open both failed and pending PDFs"
    )
    parser.add_argument(
        "--pending",
        action="store_true",
        help="Open only pending (not attempted) PDFs"
    )
    parser.add_argument(
        "--profile",
        help="Browser profile name to use (default: system)"
    )

    args = parser.parse_args()

    # Initialize config
    config = ScholarConfig()

    # Get papers based on flags
    papers = []

    if args.all or args.pending:
        pending = get_pending_papers(args.project, config)
        logger.info(f"Found {len(pending)} pending papers")
        papers.extend(pending)

    if args.all or not args.pending:
        failed = get_failed_papers(args.project, config)
        logger.info(f"Found {len(failed)} failed papers")
        papers.extend(failed)

    if not papers:
        logger.warning(f"No papers found for project: {args.project}")
        return

    # Show summary
    logger.info(f"\nPreparing {len(papers)} papers with auto-tracking:")
    for i, paper in enumerate(papers[:10], 1):
        title = paper.get("title", "Unknown")[:60]
        paper_id = paper.get("paper_id", "Unknown")
        logger.info(f"  {i}. [{paper_id}] {title}...")
    if len(papers) > 10:
        logger.info(f"  ... and {len(papers) - 10} more")

    # Open browser with auto-tracking
    open_browser_with_auto_tracking(
        papers,
        args.project,
        config,
        profile=args.profile
    )


if __name__ == "__main__":
    main()
