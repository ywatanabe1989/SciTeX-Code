#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 10:13:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryCacheManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/_LibraryCacheManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Result caching and Scholar library management for DOI resolution."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class LibraryCacheManager:
    """Handles DOI caching, result persistence, and retrieval.

    Responsibilities:
    - Scholar library checking and DOI retrieval
    - DOI caching and result persistence
    - Unresolved entry tracking
    - Project symlink management
    - Library integration and file management
    """

    def __init__(
        self,
        project: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize result cache manager.

        Args:
            config: ScholarConfig instance
            project: Project name for library organization
        """
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        logger.debug(f"LibraryCacheManager initialized for project: {project}")

    def is_doi_stored(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Check if DOI already exists in master Scholar library before making API requests.

        Args:
            title: Paper title to search for
            year: Publication year (optional, for better matching)

        Returns:
            DOI string if found in library, None otherwise
        """
        try:
            # Check for null/empty title
            if not title:
                return None

            # Strategy: Search through all papers in master collection by title match
            # since we don't know the DOI yet (chicken-and-egg problem with paper ID generation)
            master_dir = self.config.path_manager.get_collection_dir("master")

            if not master_dir.exists():
                return None

            # Search through all 8-digit paper directories
            title_lower = title.lower().strip()
            for paper_dir in master_dir.iterdir():
                if paper_dir.is_dir() and len(paper_dir.name) == 8:
                    metadata_file = paper_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)
                                stored_title = (
                                    metadata.get("title", "").lower().strip()
                                )
                                stored_year = metadata.get("year")
                                stored_doi = metadata.get("doi")

                                # Match by title (and optionally year)
                                title_match = stored_title == title_lower
                                year_match = (
                                    year is None
                                    or stored_year is None
                                    or stored_year == year
                                )

                                if title_match and year_match and stored_doi:
                                    logger.info(
                                        f"DOI found in master Scholar library: {stored_doi} (paper_id: {paper_dir.name})"
                                    )
                                    return stored_doi

                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(
                                f"Error reading metadata from {metadata_file}: {e}"
                            )
                            continue

            return None
        except Exception as e:
            logger.debug(f"Error checking master Scholar library: {e}")
            return None

    def save_entry(
        self,
        title: str,
        doi: Optional[str] = None,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
    ) -> bool:
        """Save paper entry - automatically routes to resolved or unresolved.

        Args:
            title: Paper title
            doi: DOI if resolved (None for unresolved)
            year: Publication year
            authors: List of authors
            source: DOI resolution source
            metadata: Additional metadata
            bibtex_source: BibTeX source information

        Returns:
            True if saved successfully
        """
        if doi:
            return self._save_resolved_entry(
                title, doi, year, authors, source, metadata, bibtex_source
            )
        else:
            return self._save_unresolved_entry(
                title, year, authors, bibtex_source
            )

    # def save_to_scholar_library(
    def _save_resolved_entry(
        self,
        title: str,
        doi: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: str = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
    ) -> bool:
        """Save resolved DOI to master Scholar library + create project symlink.

        Args:
            title: Paper title
            doi: Resolved DOI
            year: Publication year
            authors: List of authors
            source: DOI resolution source
            metadata: Additional metadata
            bibtex_source: BibTeX source information

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create paper info with enhanced metadata if available
            paper_info = {
                "title": title,
                "year": year,
                "authors": authors or [],
                "doi": doi,
            }

            # Add journal info from metadata if available
            if metadata:
                if metadata.get("journal"):
                    paper_info["journal"] = metadata["journal"]
                # Use metadata year if not provided directly
                if not year and metadata.get("year"):
                    paper_info["year"] = metadata["year"]
                # Use metadata authors if not provided directly
                if not authors and metadata.get("authors"):
                    paper_info["authors"] = metadata["authors"]

            # 1. Save to master collection (single source of truth)
            master_storage_paths = (
                self.config.path_manager.get_paper_storage_paths(
                    paper_info=paper_info, collection_name="MASTER"
                )
            )

            paper_id = master_storage_paths["unique_id"]
            master_storage_path = master_storage_paths["storage_path"]
            master_metadata_file = master_storage_path / "metadata.json"

            # Load existing metadata if exists
            existing_metadata = {}
            if master_metadata_file.exists():
                try:
                    with open(master_metadata_file, "r") as f:
                        existing_metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading existing metadata: {e}")

            # Create comprehensive metadata with sources
            comprehensive_metadata = {
                **existing_metadata,  # Preserve existing data
                "title": title,
                "title_source": (source),
                "year": paper_info.get("year"),
                "year_source": source,
                "authors": paper_info.get("authors", []),
                "authors_source": source,
                "doi": doi,
                "doi_source": source,
                "doi_resolved_at": datetime.now().isoformat(),
                "scholar_id": paper_id,
                "created_at": existing_metadata.get(
                    "created_at", datetime.now().isoformat()
                ),
                "updated_at": datetime.now().isoformat(),
            }

            # Add journal information with source tracking
            if paper_info.get("journal"):
                comprehensive_metadata["journal"] = paper_info["journal"]
                comprehensive_metadata["journal_source"] = source

            # Add any additional metadata from DOI source
            if metadata:
                for field, value in metadata.items():
                    if (
                        field
                        not in ["title", "year", "authors", "journal", "doi"]
                        and value is not None
                    ):
                        comprehensive_metadata[field] = value
                        comprehensive_metadata[f"{field}_source"] = source

            # Save comprehensive metadata
            with open(master_metadata_file, "w") as f:
                json.dump(comprehensive_metadata, f, indent=2)

            logger.success(
                f"Saved to master Scholar library: {paper_id} ({doi})"
            )

            # 2. Create project symlink if not master project
            # if self.project != "master":
            #     self._ensure_project_symlink(title, year, authors, paper_id)
            self._ensure_project_symlink(title, year, authors, paper_id)

            return True

        except Exception as e:
            logger.error(f"Error saving to Scholar library: {e}")
            return False

    def _save_unresolved_entry(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_source: Optional[str] = None,
    ) -> bool:
        """Save unresolved entry to master Scholar library for future resolution.

        Args:
            title: Paper title
            year: Publication year
            authors: List of authors
            bibtex_source: BibTeX source information

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create paper info for unresolved entry
            paper_info = {
                "title": title,
                "year": year,
                "authors": authors or [],
                "doi": None,  # No DOI available
            }

            # Get storage paths
            storage_paths = self.config.path_manager.get_paper_storage_paths(
                paper_info=paper_info, collection_name="MASTER"
            )

            paper_id = storage_paths["unique_id"]
            storage_path = storage_paths["storage_path"]
            metadata_file = storage_path / "metadata.json"

            # Don't overwrite if already exists
            if metadata_file.exists():
                logger.debug(f"Unresolved entry already exists: {paper_id}")
                return True

            # Create metadata for unresolved entry
            unresolved_metadata = {
                "title": title,
                "title_source": bibtex_source if bibtex_source else "input",
                "year": year,
                "year_source": (
                    bibtex_source if bibtex_source and year else "input"
                ),
                "authors": authors or [],
                "authors_source": (
                    bibtex_source if bibtex_source and authors else "input"
                ),
                "doi": None,
                "doi_source": None,
                "doi_resolution_failed": True,
                "doi_last_attempt": datetime.now().isoformat(),
                "scholar_id": paper_id,
                "created_at": datetime.now().isoformat(),
                "resolution_status": "unresolved",
            }

            # Save metadata
            with open(metadata_file, "w") as f:
                json.dump(unresolved_metadata, f, indent=2)

            logger.info(
                f"Saved unresolved entry: {paper_id} ({title[:50]}...)"
            )

            # Create project symlink if not master project
            # if self.project != "master":
            #     self._ensure_project_symlink(title, year, authors, paper_id)
            self._ensure_project_symlink(title, year, authors, paper_id)

            return True

        except Exception as e:
            logger.error(f"Error saving unresolved entry: {e}")
            return False

    # def _create_project_symlink(
    #     self,
    #     paper_id: str,
    #     readable_name: str,
    #     project: Optional[str] = None,
    # ) -> bool:
    #     """Create project symlink to master paper directory.

    #     Args:
    #         paper_id: 8-digit paper ID
    #         readable_name: Human-readable paper name

    #     Returns:
    #         True if symlink created successfully, False otherwise
    #     """
    #     try:
    #         # Get paths
    #         master_paper_dir = (
    #             self.config.path_manager.get_collection_dir("master")
    #             / paper_id
    #         )
    #         project = project or self.project
    #         if project in ["master", "MASTER"]:
    #             project = project + "-human-readable"
    #         project_dir = self.config.path_manager.get_collection_dir(project)

    #         # Create symlink
    #         symlink_path = project_dir / readable_name
    #         if not symlink_path.exists():
    #             symlink_path.symlink_to(master_paper_dir)
    #             logger.success(
    #                 f"Created project symlink: {symlink_path} -> {master_paper_dir}"
    #             )
    #             return True

    #         return True

    #     except Exception as e:
    #         logger.warn(f"Error creating project symlink: {e}")
    #         return False

    def _create_project_symlink(
        self,
        paper_id: str,
        readable_name: str,
        project: Optional[str] = None,
    ) -> bool:
        """Create project symlink to master paper directory.

        Args:
            paper_id: 8-digit paper ID
            readable_name: Human-readable paper name

        Returns:
            True if symlink created successfully, False otherwise
        """
        try:
            # Get paths
            master_paper_dir = (
                self.config.path_manager.get_collection_dir("master")
                / paper_id
            )
            project = project or self.project
            if project in ["master", "MASTER"]:
                project = project + "-human-readable"
            project_dir = self.config.path_manager.get_collection_dir(project)

            # Create symlink
            symlink_path = project_dir / readable_name
            if symlink_path.exists():
                return True

            try:
                symlink_path.symlink_to(master_paper_dir)
                logger.success(
                    f"Created project symlink:\n{symlink_path} ->\n{master_paper_dir}"
                )
            except FileExistsError:
                return True

            return True

        except Exception as e:
            logger.warning(f"Error creating project symlink: {e}")
            return False

    def _ensure_project_symlink(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        paper_id: Optional[str] = None,
    ) -> bool:
        """Ensure project symlink exists for a paper.

        Args:
            title: Paper title
            year: Publication year
            authors: List of authors
            paper_id: Paper ID (will be generated if not provided)

        Returns:
            True if symlink exists or was created successfully, False otherwise
        """
        try:
            # Generate paper ID if not provided
            if not paper_id:
                paper_info = {
                    "title": title,
                    "year": year,
                    "authors": authors or [],
                }
                storage_paths = (
                    self.config.path_manager.get_paper_storage_paths(
                        paper_info=paper_info, collection_name="MASTER"
                    )
                )
                paper_id = storage_paths["unique_id"]

            # Generate readable name
            readable_name = self._generate_readable_name(title, year, authors)

            return self._create_project_symlink(paper_id, readable_name)

        except Exception as e:
            logger.error(f"Error ensuring project symlink: {e}")
            return False

    def _generate_readable_name(
        self, title: str, year: Optional[int], authors: Optional[List[str]]
    ) -> str:
        """Generate human-readable name for symlink.

        Args:
            title: Paper title
            year: Publication year
            authors: List of authors

        Returns:
            Human-readable name
        """
        # Get first author's last name
        first_author = "Unknown"
        if authors and len(authors) > 0:
            author_parts = authors[0].split()
            if len(author_parts) > 1:
                first_author = author_parts[-1]  # Last name
            else:
                first_author = author_parts[0]

        # Clean title (first few words)
        if title:
            title_words = title.split()[:3]  # First 3 words
            clean_title = "_".join(
                word.strip().replace(" ", "_")
                for word in title_words
                if word.strip()
            )
        else:
            clean_title = "Untitled"

        # Format: AUTHOR-YEAR-TITLE
        year_str = str(year) if year else "Unknown"
        readable_name = f"{first_author}-{year_str}-{clean_title}"

        # Clean up filename
        readable_name = "".join(
            c for c in readable_name if c.isalnum() or c in "._-"
        )
        return readable_name

    def get_unresolved_entries(
        self, project_name: Optional[str] = None
    ) -> List[Dict]:
        """Get list of unresolved entries from Scholar library.

        Args:
            project_name: Project name (None for current project)

        Returns:
            List of unresolved entry dictionaries
        """
        try:
            collection_name = project_name or self.project
            collection_dir = self.config.path_manager.get_collection_dir(
                collection_name
            )

            if not collection_dir.exists():
                return []

            unresolved_entries = []

            # Search through all paper directories
            for paper_dir in collection_dir.iterdir():
                if paper_dir.is_dir() and len(paper_dir.name) == 8:
                    metadata_file = paper_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)

                                # Check if entry is unresolved
                                if (
                                    metadata.get("doi_resolution_failed")
                                    or metadata.get("resolution_status")
                                    == "unresolved"
                                    or not metadata.get("doi")
                                ):

                                    unresolved_entries.append(
                                        {
                                            "paper_id": paper_dir.name,
                                            "title": metadata.get(
                                                "title", "Unknown"
                                            ),
                                            "year": metadata.get("year"),
                                            "authors": metadata.get(
                                                "authors", []
                                            ),
                                            "last_attempt": metadata.get(
                                                "doi_last_attempt"
                                            ),
                                            "metadata_file": str(
                                                metadata_file
                                            ),
                                        }
                                    )

                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(
                                f"Error reading metadata from {metadata_file}: {e}"
                            )
                            continue

            logger.info(
                f"Found {len(unresolved_entries)} unresolved entries in {collection_name}"
            )
            return unresolved_entries

        except Exception as e:
            logger.error(f"Error getting unresolved entries: {e}")
            return []

    def copy_bibtex_to_library(
        self, bibtex_path: str, project_name: Optional[str] = None
    ) -> str:
        """Copy BibTeX file to Scholar library for reference.

        Args:
            bibtex_path: Path to BibTeX file
            project_name: Project name (None for current project)

        Returns:
            Path to copied BibTeX file in library
        """
        try:
            collection_name = project_name or self.project
            collection_dir = self.config.path_manager.get_collection_info_dir(
                collection_name
            )

            # Copy BibTeX file to collection directory
            bibtex_source = Path(bibtex_path)
            bibtex_dest = collection_dir / f"{bibtex_source.name}"

            shutil.copy2(bibtex_source, bibtex_dest)
            logger.info(f"Copied BibTeX to library: {bibtex_dest}")

            return str(bibtex_dest)

        except Exception as e:
            logger.error(f"Error copying BibTeX to library: {e}")
            return ""

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            master_dir = self.config.path_manager.get_collection_dir("master")

            if not master_dir.exists():
                return {
                    "total_papers": 0,
                    "resolved_papers": 0,
                    "unresolved_papers": 0,
                }

            total_papers = 0
            resolved_papers = 0
            unresolved_papers = 0

            for paper_dir in master_dir.iterdir():
                if paper_dir.is_dir() and len(paper_dir.name) == 8:
                    total_papers += 1
                    metadata_file = paper_dir / "metadata.json"

                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)

                                if metadata.get("doi"):
                                    resolved_papers += 1
                                else:
                                    unresolved_papers += 1
                        except:
                            unresolved_papers += 1
                    else:
                        unresolved_papers += 1

            return {
                "total_papers": total_papers,
                "resolved_papers": resolved_papers,
                "unresolved_papers": unresolved_papers,
                "resolution_rate": (
                    resolved_papers / total_papers if total_papers > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    print("LibraryCacheManager Test:")

    # This would require a real config in practice
    # manager = LibraryCacheManager(config, "test_project")

    print("Note: Full testing requires ScholarConfig instance")
    print("Core functionality:")
    print("- is_doi_stored(): Search for existing DOIs")
    print("- save_to_scholar_library(): Cache resolved DOIs")
    print("- save_unresolved_entry(): Track failed resolutions")
    print("- get_unresolved_entries(): List papers needing resolution")
    print("- get_cache_statistics(): Get cache metrics")

# EOF
