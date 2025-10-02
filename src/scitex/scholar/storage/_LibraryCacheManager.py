#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 14:26:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryCacheManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
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
        self,
        title: str,
        year: Optional[int] = None,
    ) -> Optional[str]:
        """Check if DOI already exists in master Scholar library before making API requests.

        Args:
            title: Paper title to search for
            year: Publication year (optional, for better matching)

        Returns:
            DOI string if found in library, None otherwise
        """
        try:
            if not title:
                return None

            master_dir = self.config.get_library_master_dir()
            if not master_dir.exists():
                return None

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
        force_symlink: Optional[bool] = True,
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
                title,
                doi,
                year,
                authors,
                source,
                metadata,
                bibtex_source,
                force_symlink,
            )
        else:
            return self._save_unresolved_entry(
                title,
                year,
                authors,
                bibtex_source,
                force_symlink,
            )

    # def _save_resolved_entry(
    #     self,
    #     title: str,
    #     doi: str,
    #     year: Optional[int] = None,
    #     authors: Optional[List[str]] = None,
    #     source: str = None,
    #     metadata: Optional[Dict] = None,
    #     bibtex_source: Optional[str] = None,
    #     force_symlink: Optional[bool] = True,
    # ) -> bool:
    #     try:
    #         # Extract metadata fields if available
    #         journal = metadata.get("journal") if metadata else None
    #         publisher = metadata.get("publisher") if metadata else None
    #         abstract = metadata.get("abstract") if metadata else None
    #         issn = metadata.get("issn") if metadata else None
    #         volume = metadata.get("volume") if metadata else None
    #         issue = metadata.get("issue") if metadata else None

    #         master_storage_path, master_readable_name, master_paper_id = (
    #             self.config.path_manager.get_paper_storage_paths(
    #                 doi=doi,
    #                 title=title,
    #                 authors=authors,
    #                 journal=journal,
    #                 year=year,
    #                 project="MASTER",
    #             )
    #         )

    #         # Ensure MASTER directory exists BEFORE writing metadata
    #         master_storage_path.mkdir(parents=True, exist_ok=True)

    #         master_metadata_file = master_storage_path / "metadata.json"
    #         existing_metadata = {}
    #         if master_metadata_file.exists():
    #             try:
    #                 with open(master_metadata_file, "r") as file_:
    #                     existing_metadata = json.load(file_)
    #             except Exception as exc_:
    #                 logger.warning(f"Error loading existing metadata: {exc_}")

    #         comprehensive_metadata = {
    #             **existing_metadata,
    #             "title": title,
    #             "title_source": source,
    #             "year": year,
    #             "year_source": source,
    #             "authors": authors or [],
    #             "authors_source": source,
    #             "doi": doi,
    #             "doi_source": source,
    #             "doi_resolved_at": datetime.now().isoformat(),
    #             "scholar_id": master_paper_id,
    #             "created_at": existing_metadata.get(
    #                 "created_at", datetime.now().isoformat()
    #             ),
    #             "updated_at": datetime.now().isoformat(),
    #             "journal": journal,
    #             "journal_source": source if journal else None,
    #             "publisher": publisher,
    #             "abstract": abstract,
    #             "issn": issn,
    #             "volume": volume,
    #             "issue": issue,
    #         }

    #         with open(master_metadata_file, "w") as file_:
    #             json.dump(comprehensive_metadata, file_, indent=2)

    #         logger.success(f"Saved to: {master_metadata_file} ({doi})")

    #         self._ensure_project_symlink(
    #             title,
    #             authors,
    #             year,
    #             journal,
    #             master_paper_id,
    #             force_symlink=force_symlink,
    #         )
    #         return True

    #     except Exception as exc_:
    #         logger.error(f"Error saving to Scholar library: {exc_}")
    #         return False

    def _save_resolved_entry(
        self,
        title: str,
        doi: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: str = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
        force_symlink: Optional[bool] = True,
    ) -> bool:
        try:
            # Extract metadata fields if available
            journal = metadata.get("journal") if metadata else None
            publisher = metadata.get("publisher") if metadata else None
            abstract = metadata.get("abstract") if metadata else None
            issn = metadata.get("issn") if metadata else None
            volume = metadata.get("volume") if metadata else None
            issue = metadata.get("issue") if metadata else None

            master_storage_path, master_readable_name, master_paper_id = (
                self.config.path_manager.get_paper_storage_paths(
                    doi=doi,
                    title=title,
                    authors=authors,
                    journal=journal,
                    year=year,
                    project="MASTER",
                )
            )

            # Ensure MASTER directory exists BEFORE writing metadata
            master_storage_path.mkdir(parents=True, exist_ok=True)
            master_metadata_file = master_storage_path / "metadata.json"

            existing_metadata = {}
            if master_metadata_file.exists():
                try:
                    with open(master_metadata_file, "r") as file_:
                        existing_metadata = json.load(file_)
                except Exception as exc_:
                    logger.warning(f"Error loading existing metadata: {exc_}")

            comprehensive_metadata = {
                **existing_metadata,
                "title": title,
                "title_source": source,
                "year": year,
                "year_source": source,
                "authors": authors or [],
                "authors_source": source,
                "doi": doi,
                "doi_source": source,
                "doi_resolved_at": datetime.now().isoformat(),
                "scholar_id": master_paper_id,
                "created_at": existing_metadata.get(
                    "created_at", datetime.now().isoformat()
                ),
                "updated_at": datetime.now().isoformat(),
                "journal": journal,
                "journal_source": source if journal else None,
                "publisher": publisher,
                "abstract": abstract,
                "issn": issn if issn else None,
                "volume": volume if volume else None,
                "issue": issue if issue else None,
            }

            # Check if content changed (excluding timestamps)
            is_new = not existing_metadata
            if not is_new:
                existing_copy = existing_metadata.copy()
                new_copy = comprehensive_metadata.copy()
                # Remove timestamps for comparison
                existing_copy.pop("updated_at", None)
                existing_copy.pop("doi_resolved_at", None)
                new_copy.pop("updated_at", None)
                new_copy.pop("doi_resolved_at", None)
                content_changed = existing_copy != new_copy
            else:
                content_changed = True

            with open(master_metadata_file, "w") as file_:
                json.dump(comprehensive_metadata, file_, indent=2)

            if is_new:
                logger.success(f"Saved to: {master_metadata_file} ({doi})")
            elif content_changed:
                logger.success(f"Updated: {master_metadata_file} ({doi})")

            self._ensure_project_symlink(
                title,
                authors,
                year,
                journal,
                master_paper_id,
                force_symlink=force_symlink,
            )
            return True

        except Exception as exc_:
            logger.error(f"Error saving to Scholar library: {exc_}")
            return False

    def _save_unresolved_entry(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_source: Optional[str] = None,
        force_symlink: Optional[bool] = True,
    ) -> bool:
        try:
            storage_path, readable_name, paper_id = (
                self.config.path_manager.get_paper_storage_paths(
                    title=title, year=year, authors=authors, project="MASTER"
                )
            )

            # Ensure MASTER directory exists BEFORE writing metadata
            storage_path.mkdir(parents=True, exist_ok=True)

            metadata_file = storage_path / "metadata.json"
            if metadata_file.exists():
                logger.debug(f"Unresolved entry already exists: {paper_id}")
                return True

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
                "journal": None,
            }

            with open(metadata_file, "w") as file_:
                json.dump(unresolved_metadata, file_, indent=2)

            logger.info(
                f"Saved unresolved entry: {paper_id} ({title[:50]}...)"
            )

            self._ensure_project_symlink(
                title,
                authors,
                year,
                None,
                paper_id,
                force_symlink=force_symlink,
            )
            return True

        except Exception as exc_:
            logger.error(f"Error saving unresolved entry: {exc_}")
            return False

    # # Loud
    # def _ensure_project_symlink(
    #     self,
    #     title: str,
    #     authors: Optional[List[str]] = None,
    #     year: Optional[int] = None,
    #     journal: Optional[str] = None,
    #     paper_id: Optional[str] = None,
    #     force_symlink: Optional[bool] = True,
    # ) -> bool:
    #     try:
    #         if not paper_id:
    #             _, _, paper_id = (
    #                 self.config.path_manager.get_paper_storage_paths(
    #                     title=title,
    #                     year=year,
    #                     authors=authors,
    #                     project="MASTER",
    #                 )
    #             )

    #         readable_name = self._generate_readable_name(
    #             authors, year, journal
    #         )
    #         project_dir = self.config.path_manager.get_library_dir(
    #             self.project
    #         )
    #         symlink_path = project_dir / readable_name
    #         relative_path = f"../MASTER/{paper_id}"

    #         if symlink_path.exists() or symlink_path.is_symlink():
    #             symlink_path.unlink()

    #         symlink_path.symlink_to(relative_path)
    #         logger.success(
    #             f"Created symlink:\n{symlink_path} -> {relative_path}"
    #         )
    #         return True

    #     except Exception as exc_:
    #         logger.error(f"Error ensuring project symlink: {exc_}")
    #         return False

    def _ensure_project_symlink(
        self,
        title: str,
        authors: Optional[List[str]] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
        paper_id: Optional[str] = None,
        force_symlink: Optional[bool] = True,
    ) -> bool:
        try:
            if not paper_id:
                _, _, paper_id = (
                    self.config.path_manager.get_paper_storage_paths(
                        title=title,
                        year=year,
                        authors=authors,
                        project="MASTER",
                    )
                )

            readable_name = self._generate_readable_name(
                authors, year, journal
            )
            project_dir = self.config.path_manager.get_library_dir(
                self.project
            )
            symlink_path = project_dir / readable_name
            relative_path = f"../MASTER/{paper_id}"

            # Check if symlink already points to correct target
            if symlink_path.is_symlink():
                existing_target = symlink_path.readlink()
                if str(existing_target) == relative_path:
                    return True
                symlink_path.unlink()
            elif symlink_path.exists():
                symlink_path.unlink()

            symlink_path.symlink_to(relative_path)
            logger.success(
                f"Created symlink:\n{symlink_path} -> {relative_path}"
            )
            return True

        except Exception as exc_:
            logger.error(f"Error ensuring project symlink: {exc_}")
            return False

    def _generate_readable_name(
        self,
        authors: Optional[List[str]] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
    ) -> str:
        """Generate human-readable name for symlink.

        Args:
            title: Paper title
            year: Publication year
            journal: Journal name

        Returns:
            Human-readable name
        """
        # Get first author's last name
        if authors and len(authors) > 0:
            author_parts = authors[0].split()
            if len(author_parts) > 1:
                first_author = author_parts[-1]  # Last name
            else:
                first_author = author_parts[0]
        else:
            first_author = "Unknown"

        # Year
        year_str = str(year) if year else "Unknown"

        # Journal (clean up for filename usage)
        if journal:
            # Clean journal name for filename usage, keep it as-is but remove problematic chars
            journal_cleaned = "".join(
                c for c in journal if c.isalnum() or c in "._-"
            )
            journal = journal_cleaned if journal_cleaned else "Unknown"
        else:
            journal = "Unknown"

        # Format: AUTHOR-YEAR-JOURNAL
        readable_name = f"{first_author}-{year_str}-{journal}"

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
            collection_dir = self.config.path_manager.get_library_dir(
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
            collection_dir = self.config.get_library_info_dir(collection_name)

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
            master_dir = self.config.get_library_master_dir()

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
