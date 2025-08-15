#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 00:59:12 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/urls/_URLMetadataHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/urls/_URLMetadataHandler.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL Metadata Handler

This module manages different types of URLs in the metadata:
1. Article URL - The original article page URL
2. DOI URL - The DOI resolver URL (doi.org/...)
3. Publisher URL - The final publisher URL after authentication
4. PDF URLs - Direct PDF download URLs
5. OpenURL - The library resolver URL
6. Supplementary URLs - URLs for supplementary materials
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class URLMetadataHandler:
    """Handler for URL metadata in the Scholar library system."""

    def __init__(self, config: ScholarConfig = None):
        """Initialize the URL metadata handler."""
        self.config = config or ScholarConfig()
        self.library_path = self.config.get_library_dir()

    def add_urls_to_metadata(
        self,
        metadata_path: Path,
        urls: Dict[str, any],
        source: str = "URLMetadataHandler",
    ) -> bool:
        """
        Add URL information to existing metadata file.

        Args:
            metadata_path: Path to metadata.json file
            urls: Dictionary of URLs to add
            source: Source of the URL information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing metadata
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
            else:
                logger.warning(f"Metadata file not found: {metadata_path}")
                return False

            # Add URL information
            updated = False

            # Article URL (original URL)
            if "article_url" in urls and urls["article_url"]:
                if not metadata.get("article_url"):
                    metadata["article_url"] = urls["article_url"]
                    metadata["article_url_source"] = source
                    updated = True

            # DOI URL
            if "url_doi" in urls and urls["url_doi"]:
                if not metadata.get("url_doi"):
                    metadata["url_doi"] = urls["url_doi"]
                    metadata["url_doi_source"] = source
                    updated = True

            # Publisher URL (final URL after authentication)
            if "url_publisher" in urls and urls["url_publisher"]:
                if not metadata.get("url_publisher"):
                    metadata["url_publisher"] = urls["url_publisher"]
                    metadata["url_publisher_source"] = source
                    updated = True

            # OpenURL (library resolver URL)
            if "openurl" in urls and urls["openurl"]:
                if not metadata.get("openurl"):
                    metadata["openurl"] = urls["openurl"]
                    metadata["openurl_source"] = source
                    updated = True

            # PDF URLs (can be multiple)
            if "pdf_urls" in urls and urls["pdf_urls"]:
                if not metadata.get("pdf_urls"):
                    metadata["pdf_urls"] = []

                # Add new PDF URLs that aren't already in the list
                for pdf_url in urls["pdf_urls"]:
                    if pdf_url not in metadata["pdf_urls"]:
                        metadata["pdf_urls"].append(pdf_url)
                        updated = True

                if updated and not metadata.get("pdf_urls_source"):
                    metadata["pdf_urls_source"] = source

            # Supplementary URLs
            if "supplementary_urls" in urls and urls["supplementary_urls"]:
                if not metadata.get("supplementary_urls"):
                    metadata["supplementary_urls"] = []

                # Add supplementary URLs
                for supp in urls["supplementary_urls"]:
                    # Check if this URL is already recorded
                    existing_urls = [
                        s.get("url") for s in metadata["supplementary_urls"]
                    ]
                    if supp.get("url") and supp["url"] not in existing_urls:
                        metadata["supplementary_urls"].append(supp)
                        updated = True

                if updated and not metadata.get("supplementary_urls_source"):
                    metadata["supplementary_urls_source"] = source

            # Update timestamps if changes were made
            if updated:
                metadata["urls_updated_at"] = datetime.now().isoformat()
                metadata["urls_updated_by"] = source

                # Save updated metadata
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                logger.success(
                    f"Updated URLs in metadata: {metadata_path.name}"
                )
                return True
            else:
                logger.info("No new URLs to add")
                return True

        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False

    def get_pdf_urls_from_metadata(self, metadata_path: Path) -> List[str]:
        """
        Get PDF URLs from metadata file.

        Args:
            metadata_path: Path to metadata.json file

        Returns:
            List of PDF URLs
        """
        try:
            if not metadata_path.exists():
                return []

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            return metadata.get("pdf_urls", [])

        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return []

    def get_all_urls_from_metadata(self, metadata_path: Path) -> Dict:
        """
        Get all URL information from metadata file.

        Args:
            metadata_path: Path to metadata.json file

        Returns:
            Dictionary of all URL types
        """
        try:
            if not metadata_path.exists():
                return {}

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            urls = {
                "article_url": metadata.get("article_url"),
                "url_doi": metadata.get("url_doi"),
                "url_publisher": metadata.get("url_publisher"),
                "openurl": metadata.get("openurl"),
                "pdf_urls": metadata.get("pdf_urls", []),
                "supplementary_urls": metadata.get("supplementary_urls", []),
            }

            # Add sources
            for url_type in [
                "article_url",
                "url_doi",
                "url_publisher",
                "openurl",
                "pdf_urls",
                "supplementary_urls",
            ]:
                source_key = f"{url_type}_source"
                if metadata.get(source_key):
                    urls[source_key] = metadata[source_key]

            return urls

        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return {}

    def update_pdf_download_status(
        self,
        metadata_path: Path,
        pdf_url: str,
        status: str,
        file_path: str = None,
        error: str = None,
    ) -> bool:
        """
        Update the download status of a PDF URL.

        Args:
            metadata_path: Path to metadata.json file
            pdf_url: The PDF URL that was attempted
            status: Status of download ('success', 'failed', 'pending')
            file_path: Path to downloaded file (if successful)
            error: Error message (if failed)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing metadata
            if not metadata_path.exists():
                return False

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Initialize download status if not present
            if "pdf_download_status" not in metadata:
                metadata["pdf_download_status"] = {}

            # Update status for this URL
            metadata["pdf_download_status"][pdf_url] = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "error": error,
            }

            # Update overall PDF status
            if status == "success" and file_path:
                metadata["pdf_file"] = file_path
                metadata["pdf_downloaded"] = True
                metadata["pdf_downloaded_at"] = datetime.now().isoformat()

            # Save updated metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.info(f"Updated PDF download status: {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update download status: {e}")
            return False

    def get_undownloaded_papers(self, project: str = None) -> List[Dict]:
        """
        Get list of papers that don't have PDFs downloaded yet.

        Args:
            project: Project name (e.g., 'pac')

        Returns:
            List of papers with their metadata and PDF URLs
        """
        undownloaded = []

        try:
            # Determine search path
            if project:
                search_path = self.library_path / project
            else:
                search_path = self.library_path / "MASTER"

            if not search_path.exists():
                logger.warning(f"Path not found: {search_path}")
                return []

            # Iterate through all paper directories
            for paper_dir in search_path.iterdir():
                if not paper_dir.is_dir():
                    continue

                metadata_file = paper_dir / "metadata.json"
                if not metadata_file.exists():
                    continue

                with open(metadata_file, "r") as f:
                    metadata = json.load(f)

                # Check if PDF is downloaded
                if not metadata.get("pdf_downloaded", False):
                    paper_info = {
                        "scitex_id": metadata.get("scitex_id"),
                        "title": metadata.get("title"),
                        "year": metadata.get("year"),
                        "doi": metadata.get("doi"),
                        "pdf_urls": metadata.get("pdf_urls", []),
                        "metadata_path": str(metadata_file),
                        "paper_dir": str(paper_dir),
                    }
                    undownloaded.append(paper_info)

            logger.info(f"Found {len(undownloaded)} papers without PDFs")
            return undownloaded

        except Exception as e:
            logger.error(f"Failed to get undownloaded papers: {e}")
            return []


# Convenience functions
def add_urls_to_paper(scitex_id: str, urls: Dict, project: str = None) -> bool:
    """
    Add URLs to a paper's metadata by SciTeX ID.

    Args:
        scitex_id: The paper's SciTeX ID
        urls: Dictionary of URLs to add
        project: Project name (optional)

    Returns:
        True if successful
    """
    handler = URLMetadataHandler()

    # Find metadata file
    if project:
        base_path = handler.library_path / project
    else:
        base_path = handler.library_path / "MASTER"

    # Look for the paper directory
    for paper_dir in base_path.iterdir():
        if paper_dir.is_dir():
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                if metadata.get("scitex_id") == scitex_id:
                    return handler.add_urls_to_metadata(metadata_file, urls)

    logger.error(f"Paper not found: {scitex_id}")
    return False


def get_papers_for_download(project: str = None) -> List[Dict]:
    """
    Get list of papers that need PDF downloads.

    Args:
        project: Project name (e.g., 'pac')

    Returns:
        List of papers with their PDF URLs
    """
    handler = URLMetadataHandler()
    return handler.get_undownloaded_papers(project)

# EOF
