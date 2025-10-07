#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open browser with failed PDF URLs for manual download.

This CLI tool opens a visible browser with tabs for all papers that failed
to download automatically, allowing manual download with Zotero connector
or other browser extensions.

Usage:
    # Open failed PDFs for a project
    python -m scitex.scholar.cli.open_browser --project neurovista

    # Open only pending (not attempted) PDFs
    python -m scitex.scholar.cli.open_browser --project neurovista --pending

    # Open all PDFs (failed + pending)
    python -m scitex.scholar.cli.open_browser --project neurovista --all

    # Use specific browser profile
    python -m scitex.scholar.cli.open_browser --project neurovista --profile myprofile
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.cli._url_utils import get_best_url
from scitex.logging import getLogger

logger = getLogger(__name__)


def get_failed_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get list of papers with failed PDF downloads.

    Args:
        project: Project name
        config: Scholar configuration

    Returns:
        List of paper metadata dicts with DOI, title, URL info
    """
    library_dir = config.path_manager.get_library_master_dir()
    failed_papers = []

    for paper_dir in library_dir.iterdir():
        if not paper_dir.is_dir():
            continue

        metadata_file = paper_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        # Load metadata
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Check if paper belongs to project
        projects = metadata.get("container", {}).get("projects", [])
        if project not in projects:
            continue

        # Check if PDF download failed (has screenshots but no PDF)
        pdf_files = list(paper_dir.glob("*.pdf"))
        screenshot_dir = paper_dir / "screenshots"
        has_screenshots = screenshot_dir.exists() and any(screenshot_dir.iterdir())

        if not pdf_files and has_screenshots:
            # Failed download
            meta = metadata.get("metadata", {})
            failed_papers.append({
                "paper_id": paper_dir.name,
                "doi": meta.get("id", {}).get("doi"),
                "title": meta.get("basic", {}).get("title"),
                "url_doi": meta.get("url", {}).get("doi"),
                "url_publisher": meta.get("url", {}).get("publisher"),
                "openurl_resolved": meta.get("url", {}).get("openurl_resolved", []),
                "pdf_urls": meta.get("url", {}).get("pdfs", []),
            })

    return failed_papers


def get_pending_papers(project: str, config: ScholarConfig) -> List[Dict]:
    """Get list of papers with pending PDF downloads (not attempted).

    Args:
        project: Project name
        config: Scholar configuration

    Returns:
        List of paper metadata dicts with DOI, title, URL info
    """
    library_dir = config.path_manager.get_library_master_dir()
    pending_papers = []

    for paper_dir in library_dir.iterdir():
        if not paper_dir.is_dir():
            continue

        metadata_file = paper_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        # Load metadata
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Check if paper belongs to project
        projects = metadata.get("container", {}).get("projects", [])
        if project not in projects:
            continue

        # Check if PDF download is pending (no PDF, no screenshots)
        pdf_files = list(paper_dir.glob("*.pdf"))
        screenshot_dir = paper_dir / "screenshots"
        has_screenshots = screenshot_dir.exists() and any(screenshot_dir.iterdir())

        if not pdf_files and not has_screenshots:
            # Pending download
            meta = metadata.get("metadata", {})
            pending_papers.append({
                "paper_id": paper_dir.name,
                "doi": meta.get("id", {}).get("doi"),
                "title": meta.get("basic", {}).get("title"),
                "url_doi": meta.get("url", {}).get("doi"),
                "url_publisher": meta.get("url", {}).get("publisher"),
                "openurl_resolved": meta.get("url", {}).get("openurl_resolved", []),
                "pdf_urls": meta.get("url", {}).get("pdfs", []),
            })

    return pending_papers


def open_browser_with_urls(
    papers: List[Dict],
    profile: str = None,
    headless: bool = False
) -> None:
    """Open browser with URL tabs for papers.

    Args:
        papers: List of paper metadata dicts
        profile: Browser profile name to use
        headless: Whether to run in headless mode (for testing)
    """
    from playwright.sync_api import sync_playwright

    if not papers:
        logger.info("No papers to open")
        return

    # Collect URLs to open using standardized utility
    urls_to_open = []
    for paper in papers:
        url = get_best_url(
            openurl_resolved=paper.get("openurl_resolved"),
            url_publisher=paper.get("url_publisher"),
            url_doi=paper.get("url_doi"),
            doi=paper.get("doi")
        )

        if url:
            urls_to_open.append(url)
        else:
            logger.warning(f"No valid URL found for paper: {paper.get('title', 'Unknown')[:50]}...")

    if not urls_to_open:
        logger.warning("No URLs to open")
        return

    logger.info(f"Opening {len(urls_to_open)} URLs in browser...")

    # Get cache directory for browser profile
    from scitex.scholar.config import ScholarConfig
    config = ScholarConfig()

    if profile:
        profile_dir = config.path_manager.get_chrome_cache_dir(profile)
    else:
        profile_dir = config.path_manager.get_chrome_cache_dir("system")

    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser with profile
        browser = p.chromium.launch_persistent_context(
            str(profile_dir),
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=UserAgentClientHint',
            ] if not headless else []
        )

        # Open first URL in first tab
        if browser.pages:
            page = browser.pages[0]
        else:
            page = browser.new_page()

        if urls_to_open:
            page.goto(urls_to_open[0])
            logger.success(f"Opened: {urls_to_open[0]}")

        # Open remaining URLs in new tabs
        for url in urls_to_open[1:]:
            new_page = browser.new_page()
            new_page.goto(url)
            logger.success(f"Opened: {url}")

        logger.info(f"\nBrowser opened with {len(urls_to_open)} tabs")
        logger.info("Use Zotero connector or other extensions to download PDFs")
        logger.info("Press Ctrl+C to close the browser when done")

        try:
            # Keep browser open until user closes it
            page.wait_for_event("close", timeout=0)
        except KeyboardInterrupt:
            logger.info("\nClosing browser...")
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Open browser with failed/pending PDF URLs for manual download"
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
        help="Open only pending (not attempted) PDFs instead of failed"
    )
    parser.add_argument(
        "--profile",
        help="Browser profile name to use (default: system)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (for testing)"
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
        logger.warning(f"No {'pending' if args.pending else 'failed'} papers found for project: {args.project}")
        return

    # Show summary
    logger.info(f"\nOpening {len(papers)} papers in browser:")
    for i, paper in enumerate(papers[:10], 1):
        title = paper.get("title", "Unknown")[:60]
        logger.info(f"  {i}. {title}...")
    if len(papers) > 10:
        logger.info(f"  ... and {len(papers) - 10} more")

    # Open browser
    open_browser_with_urls(papers, profile=args.profile, headless=args.headless)


if __name__ == "__main__":
    main()
