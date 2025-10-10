#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 09:04:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/_PathManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


@dataclass
class TidinessConstraints:
    """Configuration for directory tidiness constraints."""

    # File naming constraints
    max_filename_length: int = 100
    allowed_filename_chars: str = r"[a-zA-Z0-9._-]"
    forbidden_filename_patterns: List[str] = field(
        default_factory=lambda: [
            r"^\.",  # No hidden files in main directories
            r"^~",  # No temporary files
            r"\s{2,}",  # No multiple spaces
            r"[<>:\"/\\|?*]",  # No Windows forbidden chars
        ]
    )

    # Directory size constraints (in MB)
    max_cache_size_mb: int = 1000  # 1GB cache
    max_workspace_size_mb: int = 2000  # 2GB workspace
    max_screenshots_size_mb: int = 500  # 500MB screenshots
    max_downloads_size_mb: int = 1000  # 1GB downloads

    # File age constraints (in days)
    cache_retention_days: int = 30
    workspace_retention_days: int = 7
    screenshots_retention_days: int = 14
    downloads_retention_days: int = 3

    # Directory depth constraints
    max_directory_depth: int = 8

    # Collection naming constraints
    max_collection_name_length: int = 50
    allowed_collection_chars: str = r"[a-zA-Z0-9_-]"


class PathManager:
    """Enhanced PathManager with directory tidiness constraints and cleanup policies."""

    def __init__(
        self,
        scholar_dir: Optional[Path] = None,
        constraints: Optional[TidinessConstraints] = None,
    ):
        if scholar_dir is None:
            scholar_dir = (
                Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
                / "scholar"
            )

        self.scholar_dir = scholar_dir
        self.constraints = constraints or TidinessConstraints()

        # Create base structure
        self._ensure_directories()

        # Validate existing structure
        self._validate_structure()

    def _ensure_directories(self):
        """Create base directory structure with proper permissions."""
        base_dirs = [
            self.cache_dir,
            self.config_dir,
            self.library_dir,
            self.log_dir,
            self.workspace_dir,
            self.backup_dir,
        ]

        for dir_path in base_dirs:
            dir_path.mkdir(parents=True, exist_ok=True, mode=0o755)

        # Create subdirectories
        subdirs = [
            self.cache_dir / "chrome",
            self.cache_dir / "auth",
            self.cache_dir / "engine",
            self.cache_dir / "url",
            self.cache_dir / "pdf_downloader",
            self.workspace_dir / "downloads",
            self.workspace_dir / "logs",
            self.workspace_dir / "screenshots",
        ]

        for subdir in subdirs:
            subdir.mkdir(parents=True, exist_ok=True, mode=0o755)

    def _validate_structure(self):
        """Validate directory structure and fix issues."""
        issues = []

        # Check if directories exist
        required_dirs = [
            self.cache_dir,
            self.config_dir,
            self.library_dir,
            self.log_dir,
            self.workspace_dir,
            self.backup_dir,
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                issues.append(f"Missing directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)

        # Check directory permissions
        for dir_path in required_dirs:
            if not os.access(dir_path, os.R_OK | os.W_OK):
                issues.append(f"Permission issue: {dir_path}")

        if issues:
            logger.warning(f"Directory structure issues fixed: {issues}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename according to constraints."""
        # Remove forbidden patterns
        for pattern in self.constraints.forbidden_filename_patterns:
            filename = re.sub(pattern, "", filename)

        # Keep only allowed characters
        filename = re.sub(
            f"[^{self.constraints.allowed_filename_chars}]", "_", filename
        )

        # Remove multiple underscores
        filename = re.sub(r"_{2,}", "_", filename)

        # Trim to max length
        if len(filename) > self.constraints.max_filename_length:
            name, ext = os.path.splitext(filename)
            max_name_len = self.constraints.max_filename_length - len(ext)
            filename = name[:max_name_len] + ext

        # Ensure it doesn't start/end with dots or underscores
        filename = filename.strip("._")

        # Ensure it's not empty
        if not filename:
            filename = f"unnamed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return filename

    def _hyphenate_for_symlinks(self, text: str) -> str:
        """Convert text to hyphenated format suitable for symlinks.

        This method aggressively converts spaces, punctuation, and special
        characters to hyphens for better readability in symlink names.

        Args:
            text: Input text to hyphenate

        Returns:
            Hyphenated text suitable for symlinks
        """
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Remove common punctuation that should be eliminated entirely
        # (parentheses, quotes, etc.)
        text = re.sub(r'[()"\'\[\]{}]', "", text)

        # Convert spaces, commas, periods, and other separators to hyphens
        text = re.sub(r"[\s,\.;:&/\\]+", "-", text)

        # Remove any remaining non-alphanumeric characters except hyphens
        text = re.sub(r"[^a-zA-Z0-9\-]", "", text)

        # Remove multiple consecutive hyphens
        text = re.sub(r"-{2,}", "-", text)

        # Remove leading/trailing hyphens
        text = text.strip("-")

        # Ensure it's not empty
        if not text:
            text = "Unknown"

        return text

    def _expand_journal_name(self, journal: str) -> str:
        """Expand common journal abbreviations to more readable names."""
        if not journal or journal == "Unknown":
            return journal

        # Dictionary of common journal abbreviations and their expansions
        # Based on your PAC research collection abbreviations
        journal_expansions = {
            # Nature family
            "N": "Nature",
            "NC": "Nature Communications",
            "NBR": "Nature Biomedical Research",
            "Nature": "Nature",
            # Neuroscience journals
            "FN": "Frontiers in Neuroscience",
            "FHN": "Frontiers in Human Neuroscience",
            "FIN": "Frontiers in Neuroscience",
            "FBN": "Frontiers in Behavioral Neuroscience",
            "eNeuro": "eNeuro",
            "JNE": "Journal of Neural Engineering",
            "JNM": "Journal of Neuroscience Methods",
            "JCN": "Journal of Cognitive Neuroscience",
            "CN": "Computational Neuroscience",
            "CON": "Consciousness and Cognition",
            "TJN": "The Journal of Neuroscience",
            "BB": "Biological and Biomedical",
            "BT": "Brain Topography",
            "BRI": "Brain Research International",
            # Computing and Signal Processing
            "PCB": "PLOS Computational Biology",
            "TCS": "Theoretical Computer Science",
            "IICASSP": "IEEE International Conference on Acoustics Speech and Signal Processing",
            "IIEMBS": "IEEE Engineering in Medicine and Biology Society",
            "AICIEMBS": "AI Conference IEEE Engineering in Medicine and Biology Society",
            "ITNSRE": "IEEE Transactions on Neural Systems and Rehabilitation Engineering",
            "ITM": "IEEE Transactions on Medicine",
            "IJBHI": "International Journal of Biomedical and Health Informatics",
            "IICBB": "IEEE International Conference on Bioinformatics and Biomedicine",
            "CEN": "Computational and Engineering Networks",
            # Medical and Life Sciences
            "PR": "Pattern Recognition",
            "H": "Hippocampus",
            "HBM": "Human Brain Mapping",
            "PO": "PLOS ONE",
            "S": "Science",
            "SR": "Scientific Reports",
            "BS": "Brain Sciences",
            "E": "Entropy",
            "IA": "Intelligence and Applications",
            "A": "Applications",
            "C": "Communications",
            "KS": "Knowledge Systems",
            "J": "Journal",
            "JSR": "Journal of Sleep Research",
            # Preprint servers
            "bioRxiv": "bioRxiv Preprint",
            "arXiv": "arXiv Preprint",
        }

        # Try exact match first
        if journal in journal_expansions:
            expanded = journal_expansions[journal]
            logger.debug(f"Expanded journal: {journal} -> {expanded}")
            return expanded

        # Try case-insensitive match
        for abbrev, full_name in journal_expansions.items():
            if journal.lower() == abbrev.lower():
                logger.debug(f"Expanded journal: {journal} -> {full_name}")
                return full_name

        # If no expansion found, return original (might already be expanded)
        logger.debug(f"Journal not expanded: {journal}")
        return journal

    def _sanitize_collection_name(self, collection_name: str) -> str:
        """Sanitize collection name according to constraints."""
        # Keep only allowed characters
        collection_name = re.sub(
            f"[^{self.constraints.allowed_collection_chars}]",
            "_",
            collection_name,
        )

        # Remove multiple underscores
        collection_name = re.sub(r"_{2,}", "_", collection_name)

        # Trim to max length
        if len(collection_name) > self.constraints.max_collection_name_length:
            collection_name = collection_name[
                : self.constraints.max_collection_name_length
            ]

        # Ensure it doesn't start/end with underscores
        collection_name = collection_name.strip("_")

        # Ensure it's not empty
        if not collection_name:
            collection_name = f"collection_{datetime.now().strftime('%Y%m%d')}"

        return collection_name

    def _get_directory_size_mb(self, directory: Path) -> float:
        """Get directory size in MB."""
        if not directory.exists():
            return 0.0

        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (PermissionError, OSError) as e:
            logger.warning(f"Error calculating size for {directory}: {e}")

        return total_size / (1024 * 1024)  # Convert to MB

    def _cleanup_old_files(self, directory: Path, retention_days: int) -> int:
        """Clean up files older than retention period."""
        if not directory.exists():
            return 0

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cleaned_count = 0

        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    )
                    if file_time < cutoff_date:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned old file: {file_path}")
        except (PermissionError, OSError) as e:
            logger.warning(f"Error during cleanup in {directory}: {e}")

        return cleaned_count

    def _enforce_size_limits(self, directory: Path, max_size_mb: int) -> bool:
        """Enforce directory size limits by removing oldest files."""
        current_size = self._get_directory_size_mb(directory)

        if current_size <= max_size_mb:
            return True

        logger.info(
            f"Directory {directory} exceeds limit ({current_size:.1f}MB > {max_size_mb}MB)"
        )

        # Get all files with modification times
        files_with_times = []
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    size = file_path.stat().st_size
                    files_with_times.append((mtime, size, file_path))
        except (PermissionError, OSError) as e:
            logger.warning(f"Error accessing files in {directory}: {e}")
            return False

        # Sort by modification time (oldest first)
        files_with_times.sort(key=lambda x: x[0])

        # Remove oldest files until under limit
        removed_size = 0
        removed_count = 0

        for mtime, size, file_path in files_with_times:
            try:
                file_path.unlink()
                removed_size += size
                removed_count += 1

                current_size = self._get_directory_size_mb(directory)
                if current_size <= max_size_mb:
                    break

            except (PermissionError, OSError) as e:
                logger.warning(f"Could not remove {file_path}: {e}")

        logger.info(
            f"Removed {removed_count} files ({removed_size/1024/1024:.1f}MB)"
        )
        return True

    def perform_maintenance(self) -> Dict[str, int]:
        """Perform comprehensive directory maintenance."""
        logger.info("🧹 Starting directory maintenance")

        results = {
            "cache_cleaned": 0,
            "workspace_cleaned": 0,
            "screenshots_cleaned": 0,
            "downloads_cleaned": 0,
            "size_violations_fixed": 0,
        }

        # Clean old files
        results["cache_cleaned"] = self._cleanup_old_files(
            self.cache_dir, self.constraints.cache_retention_days
        )
        results["workspace_cleaned"] = self._cleanup_old_files(
            self.workspace_dir / "logs",
            self.constraints.workspace_retention_days,
        )
        results["screenshots_cleaned"] = self._cleanup_old_files(
            self.workspace_dir / "screenshots",
            self.constraints.screenshots_retention_days,
        )
        results["downloads_cleaned"] = self._cleanup_old_files(
            self.workspace_dir / "downloads",
            self.constraints.downloads_retention_days,
        )

        # Enforce size limits
        directories_to_check = [
            (self.cache_dir, self.constraints.max_cache_size_mb),
            (self.workspace_dir, self.constraints.max_workspace_size_mb),
            (
                self.workspace_dir / "screenshots",
                self.constraints.max_screenshots_size_mb,
            ),
            (
                self.workspace_dir / "downloads",
                self.constraints.max_downloads_size_mb,
            ),
        ]

        for directory, max_size in directories_to_check:
            if self._enforce_size_limits(directory, max_size):
                results["size_violations_fixed"] += 1

        # Clean empty directories
        self._remove_empty_directories(self.workspace_dir)
        self._remove_empty_directories(self.cache_dir)

        logger.info(f"🧹 Maintenance complete: {results}")
        return results

    def _remove_empty_directories(self, base_dir: Path):
        """Remove empty directories recursively."""
        if not base_dir.exists():
            return

        try:
            for dir_path in sorted(base_dir.rglob("*"), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    # Don't remove base structure directories
                    if dir_path not in [
                        self.cache_dir,
                        self.workspace_dir,
                        self.library_dir,
                    ]:
                        dir_path.rmdir()
                        logger.debug(f"Removed empty directory: {dir_path}")
        except (PermissionError, OSError) as e:
            logger.warning(f"Error removing empty directories: {e}")

    def _ensure_directory(self, path: Path, mode: int = 0o755) -> Path:
        """Helper method to ensure directory exists with proper permissions."""
        path.mkdir(parents=True, exist_ok=True, mode=mode)
        return path

    # Properties for base directories (automatically ensure they exist)
    @property
    def cache_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "cache")

    @property
    def config_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "config")

    @property
    def library_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "library")

    @property
    def log_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "log")

    @property
    def workspace_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "workspace")

    @property
    def backup_dir(self) -> Path:
        return self._ensure_directory(self.scholar_dir / "backup")

    # Library directory methods with project support
    def get_scholar_library_path(self) -> Path:
        """Get the base Scholar library path (backward compatibility method)."""
        return self.library_dir

    def get_chrome_cache_dir(self, profile_name: str) -> Path:
        """Get Chrome cache directory, syncing system profile if needed."""
        if profile_name == "system":
            self._sync_system_chrome_profile(profile_name)

        return self._ensure_directory(self.cache_dir / "chrome" / profile_name)

    def _sync_system_chrome_profile(self, profile_name: str) -> bool:
        """Sync system Chrome profile to cache directory with time-based preservation."""
        if profile_name != "system":
            return True

        system_profile = Path(os.getenv("HOME")) / ".config" / "google-chrome"
        cache_profile = self.cache_dir / "chrome" / "system"

        if not system_profile.exists():
            logger.warning("System Chrome profile not found")
            return False

        # Check if cache is newer than system profile
        if cache_profile.exists():
            system_mtime = system_profile.stat().st_mtime
            cache_mtime = cache_profile.stat().st_mtime

            if cache_mtime > system_mtime:
                logger.debug(
                    "Cache is newer than system profile, skipping sync"
                )
                return True

        logger.info(
            f"Syncing system profile to cache: {system_profile} -> {cache_profile}"
        )

        try:
            subprocess.run(
                [
                    "rsync",
                    "-av",
                    "--delete",
                    f"{system_profile}/",
                    f"{cache_profile}/",
                ],
                check=True,
                capture_output=True,
            )
            logger.info("System Chrome profile synced successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Chrome profile sync failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("rsync not found - please install rsync")
            return False

    def get_auth_cache_dir(
        self,
    ) -> Path:
        return self._ensure_directory(self.cache_dir / "auth")

    def get_engine_cache_dir(
        self,
    ) -> Path:
        return self._ensure_directory(self.cache_dir / "engine")

    def get_search_cache_dir(
        self,
    ) -> Path:
        """DEPRECATED: Use get_engine_cache_dir() instead."""
        return self.get_engine_cache_dir()

    def get_cache_url_dir(
        self,
    ) -> Path:
        return self._ensure_directory(self.cache_dir / "url")

    def get_cache_dowload_dir(
        self,
    ) -> Path:
        return self._ensure_directory(self.cache_dir / "pdf_downloader")

    # def get_doi_resolution_cache_dir(
    #     self,
    # ) -> Path:
    #     return self._ensure_directory(self.cache_dir / "doi_resolution")

    def get_doi_resolution_progress_path(
        self, provided_path: Optional[Path] = None
    ) -> Path:
        """Resolve progress file path with automatic generation if needed.

        Args:
            provided_path: Explicitly provided progress file path

        Returns:
            Resolved progress file path
        """
        if provided_path:
            return Path(str(provided_path))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return (
            self.get_workspace_logs_dir()
            / f"doi_resolution_{timestamp}.progress.json"
        )

    # def get_library_dir(self, collection_name: str) -> Path:
    #     collection_name = self._sanitize_collection_name(collection_name)
    #     return self._ensure_directory(self.library_dir / collection_name)

    # def get_library_info_dir(self, collection_name: str) -> Path:
    #     correction_dir = self.get_library_dir(collection_name)
    #     return self._ensure_directory(correction_dir / "info")

    def get_library_info_dir(self, project: str) -> Path:
        library_dir = self.get_library_dir(project)
        return self._ensure_directory(library_dir / "info")

    def get_library_dir(
        self,
        project: Optional[str] = None,
    ) -> Path:
        """Get library directory"""
        if not project:
            return self._ensure_directory(self.library_dir)
        else:
            assert (
                project.upper() != "MASTER"
            ), f"Project name '{project}' is reserved for internal storage use. Please choose a different name."

            return self._ensure_directory(self.library_dir / project)

    def get_library_master_dir(self) -> Path:
        """Get the MASTER directory for internal storage.

        Returns:
            Path to the MASTER storage directory where actual papers are stored
        """
        return self._ensure_directory(self.library_dir / "MASTER")

    def get_paper_storage_paths(
        self,
        doi: Optional[str] = None,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        journal: Optional[str] = None,
        year: Optional[int] = None,
        project: str = "default",
    ) -> tuple[Path, str, str]:

        # Sanitize inputs
        project_name = self._sanitize_collection_name(project)

        # Generate unique ID using DOI if available, otherwise metadata
        paper_id = self._generate_paper_id(
            doi=doi, title=title, authors=authors, year=year
        )

        # Create storage path
        project_dir = (
            self.get_library_master_dir()
            if project.upper() == "MASTER"
            else self.get_library_dir(project)
        )
        storage_path = self._ensure_directory(project_dir / paper_id)

        # Generate readable name for potential symlinks
        first_author = "Unknown"
        if authors and len(authors) > 0:
            author_str = str(authors[0])
            if "," in author_str:
                first_author = author_str.split(",")[0].strip()
            else:
                first_author = author_str.split()[-1]

        first_author = self._hyphenate_for_symlinks(first_author)

        # Handle journal and year
        journal_safe = journal or "Unknown"
        year_safe = str(year) if year else "Unknown"

        journal_expanded = self._expand_journal_name(journal_safe)
        journal_clean = self._hyphenate_for_symlinks(journal_expanded)

        readable_name = f"{first_author}-{year_safe}-{journal_clean}"
        readable_name = self._hyphenate_for_symlinks(readable_name)

        return storage_path, readable_name, paper_id

    def get_screenshots_dir(self, category: Optional[str] = None) -> Path:
        if category:
            category = self._sanitize_filename(category)
            return self._ensure_directory(
                self.workspace_dir / "screenshots" / category
            )
        else:
            return self._ensure_directory(self.workspace_dir / "screenshots")

    def get_downloads_dir(self) -> Path:
        return self._ensure_directory(self.workspace_dir / "downloads")

    def get_library_downloads_dir(self) -> Path:
        """Get downloads directory under library (for manual browser downloads)."""
        return self._ensure_directory(self.library_dir / "downloads")

    def get_library_pdfs_dir(self) -> Path:
        """Get PDFs directory under library (for organized PDF storage)."""
        return self._ensure_directory(self.library_dir / "pdfs")

    def get_workspace_dir(self) -> Path:
        return self._ensure_directory(self.workspace_dir)

    def get_workspace_logs_dir(self) -> Path:
        return self._ensure_directory(self.workspace_dir / "logs")

    def get_cache_file(
        self, cache_name: str, cache_type: str = "general"
    ) -> Path:
        cache_name = self._sanitize_filename(cache_name)
        cache_type = self._sanitize_filename(cache_type)

        cache_file = self.cache_dir / cache_type / f"{cache_name}.json"
        self._ensure_directory(cache_file.parent)
        return cache_file

    def get_lock_file(self, file_path: Path) -> Path:
        return Path(str(file_path) + ".lock")

    def get_config_file(self, config_name: str) -> Path:
        config_name = self._sanitize_filename(config_name)
        return self.config_dir / f"{config_name}.yaml"

    def get_project_bibtex_dir(self, collection_name: str = "default") -> Path:
        """Get directory for storing project bibtex files."""
        collection_name = self._sanitize_collection_name(collection_name)
        return self._ensure_directory(
            self.library_dir / collection_name / "bibtex"
        )

    def get_unresolved_entries_dir(
        self, collection_name: str = "default"
    ) -> Path:
        """Get directory for tracking unresolved DOI entries."""
        collection_name = self._sanitize_collection_name(collection_name)
        return self._ensure_directory(
            self.library_dir / collection_name / "unresolved"
        )

    def get_project_logs_dir(self, collection_name: str = "default") -> Path:
        """Get directory for project-specific logs."""
        collection_name = self._sanitize_collection_name(collection_name)
        return self._ensure_directory(
            self.library_dir / collection_name / "logs"
        )

    def _generate_paper_id(
        self, doi=None, title=None, authors=None, year=None
    ) -> str:
        """Generate unique 8-digit paper ID using deterministic strategy."""

        # Normalize inputs
        doi = doi.strip() if isinstance(doi, str) and doi else None
        title = title.strip() if isinstance(title, str) and title else ""
        year = str(year) if year else ""

        if doi:
            clean_doi = doi.replace("https://doi.org/", "").replace(
                "http://dx.doi.org/", ""
            )
            content = f"DOI:{clean_doi}"
            logger.debug(f"Generating ID from DOI: {clean_doi}")
        else:
            # Get first author's last name
            first_author = "unknown"
            if authors and len(authors) > 0:
                author_parts = str(authors[0]).strip().split()
                if author_parts:
                    first_author = author_parts[-1].lower()

            # Clean title
            title_clean = re.sub(
                r"\b(the|and|of|in|on|at|to|for|with|by)\b", "", title.lower()
            )
            title_clean = re.sub(r"[^\w\s]", "", title_clean)
            title_clean = re.sub(r"\s+", " ", title_clean).strip()

            content = f"META:{title_clean}:{first_author}:{year}"
            logger.debug(
                f"Generating ID from metadata: {first_author}-{year}-{title_clean[:30]}..."
            )

        hash_obj = hashlib.md5(content.encode("utf-8"))
        paper_id = hash_obj.hexdigest()[:8].upper()

        return self._sanitize_filename(paper_id)

    def get_storage_stats(self) -> Dict[str, Dict[str, Union[float, int]]]:
        """Get comprehensive storage statistics."""
        stats = {}

        directories = {
            "cache": self.cache_dir,
            "library": self.library_dir,
            "workspace": self.workspace_dir,
            "screenshots": self.workspace_dir / "screenshots",
            "downloads": self.workspace_dir / "downloads",
        }

        for name, directory in directories.items():
            if directory.exists():
                size_mb = self._get_directory_size_mb(directory)
                file_count = (
                    len(list(directory.rglob("*")))
                    if directory.exists()
                    else 0
                )

                stats[name] = {
                    "size_mb": round(size_mb, 2),
                    "file_count": file_count,
                    "path": str(directory),
                }
            else:
                stats[name] = {
                    "size_mb": 0.0,
                    "file_count": 0,
                    "path": str(directory),
                }

        return stats

    def print_expected_structure(self):
        """Print expected directory tree structure with methods and constraints."""
        base = str(self.scholar_dir)
        constraints_info = f"""
Tidiness Constraints:
- Max filename length: {self.constraints.max_filename_length} chars
- Cache retention: {self.constraints.cache_retention_days} days
- Workspace retention: {self.constraints.workspace_retention_days} days
- Max cache size: {self.constraints.max_cache_size_mb} MB
- Max workspace size: {self.constraints.max_workspace_size_mb} MB
"""

        structure = f"""{base}/
├── cache/ (.cache_dir) [Max: {self.constraints.max_cache_size_mb}MB, {self.constraints.cache_retention_days}d retention]
│   ├── chrome/
│   │   └── <profile_name>/ (get_chrome_cache_dir(auth_type))
│   ├── auth/
│   │   └── <auth_type>/ (get_auth_cache_dir(auth_type))
│   └── <cache_type>/
│       └── <cache_name>.json (get_cache_file(cache_name, cache_type))
├── config/ (.config_dir)
│   └── <config_name>.yaml (get_config_file(config_name))
├── library/ (.library_dir)
│   ├── MASTER/ (master storage - real 8-digit directories)
│   │   └── <8-digit-id>/ (paper storage with metadata.json)
│   └── <project_name>/ (project directories with human-readable symlinks)
│       ├── <Author-Year-Journal> -> ../MASTER/<8-digit-id>/
│       └── info/
│           └── <filename>/
│               └── <filename>.bib
├── log/ (.log_dir)
├── workspace/ (.workspace_dir) [Max: {self.constraints.max_workspace_size_mb}MB, {self.constraints.workspace_retention_days}d retention]
│   ├── downloads/ (get_downloads_dir()) [Max: {self.constraints.max_downloads_size_mb}MB, {self.constraints.downloads_retention_days}d retention]
│   ├── logs/ (get_workspace_logs_dir())
│   └── screenshots/ [Max: {self.constraints.max_screenshots_size_mb}MB, {self.constraints.screenshots_retention_days}d retention]
│       └── <category>/ (get_screenshots_dir(category))
└── backup/ (.backup_dir)"""

        print(structure)
        print(constraints_info)

# EOF
