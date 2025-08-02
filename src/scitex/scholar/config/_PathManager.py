#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 05:07:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/_PathManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/config/_PathManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
import re
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
            self.library_dir / "indexes",
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

    # Enhanced methods with tidiness constraints (automatically ensure directories exist)
    def get_chrome_cache_dir(self) -> Path:
        return self._ensure_directory(self.cache_dir / "chrome")

    def get_auth_cache_dir(self, auth_type: str) -> Path:
        auth_type = self._sanitize_filename(auth_type)
        return self._ensure_directory(self.cache_dir / "auth" / auth_type)

    def get_collection_dir(self, collection_name: str) -> Path:
        collection_name = self._sanitize_collection_name(collection_name)
        return self._ensure_directory(self.library_dir / collection_name)

    def get_collection_readable_dir(self, collection_name: str) -> Path:
        collection_name = self._sanitize_collection_name(collection_name)
        return self._ensure_directory(
            self.library_dir / f"{collection_name}-human-readable"
        )

    def get_indexes_dir(self) -> Path:
        return self._ensure_directory(self.library_dir / "indexes")

    def get_paper_storage_paths(
        self, paper_info: Dict, collection_name: str = "default"
    ) -> Dict[str, Path]:
        # Sanitize inputs
        collection_name = self._sanitize_collection_name(collection_name)

        # Generate unique ID using DOI if available, otherwise metadata
        unique_id = self._generate_paper_id(paper_info)

        # Create storage path
        collection_dir = self.get_collection_dir(collection_name)
        storage_path = self._ensure_directory(collection_dir / unique_id)

        # Create readable name
        first_author = "Unknown"
        if paper_info.get("authors"):
            first_author = (
                paper_info["authors"][0].split()[-1]
                if paper_info["authors"]
                else "Unknown"
            )
            first_author = self._sanitize_filename(first_author)

        year = paper_info.get("year", "Unknown")
        journal = paper_info.get("journal", "Unknown")
        journal = self._sanitize_filename(journal)

        readable_name = f"{first_author}-{year}-{journal}"
        readable_name = self._sanitize_filename(readable_name)

        readable_dir = self.get_collection_readable_dir(collection_name)
        readable_path = readable_dir / readable_name

        # Create symlink if both paths exist
        if storage_path.exists() and not readable_path.exists():
            try:
                readable_path.symlink_to(storage_path)
            except OSError:
                # Fall back to creating a regular directory
                self._ensure_directory(readable_path)

        return {
            "storage_path": storage_path,
            "readable_path": readable_path,
            "unique_id": unique_id,
        }

    def get_screenshots_dir(self, screenshot_type: str = "general") -> Path:
        screenshot_type = self._sanitize_filename(screenshot_type)
        return self._ensure_directory(
            self.workspace_dir / "screenshots" / screenshot_type
        )

    def get_downloads_dir(self) -> Path:
        return self._ensure_directory(self.workspace_dir / "downloads")

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

    def _generate_paper_id(self, paper_info: Dict) -> str:
        """
        Generate unique 8-digit paper ID using deterministic strategy.
        
        Priority:
        1. If DOI exists: Use DOI for consistent identification
        2. If no DOI: Use title + first author + year for deterministic hash
        
        Args:
            paper_info: Dictionary containing paper metadata
            
        Returns:
            8-character uppercase hexadecimal string
        """
        doi = paper_info.get("doi", "").strip()
        
        if doi:
            # Use DOI for consistent identification across systems
            # Remove common DOI prefixes and normalize
            clean_doi = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
            content = f"DOI:{clean_doi}"
            logger.debug(f"Generating ID from DOI: {clean_doi}")
        else:
            # Use deterministic metadata combination
            title = paper_info.get("title", "").strip().lower()
            authors = paper_info.get("authors", [])
            year = paper_info.get("year", "")
            
            # Get first author's last name
            first_author = "unknown"
            if authors and len(authors) > 0:
                author_parts = str(authors[0]).strip().split()
                if author_parts:
                    # Take last part as last name
                    first_author = author_parts[-1].lower()
            
            # Clean title (remove common words and normalize)
            title_clean = re.sub(r'\b(the|and|of|in|on|at|to|for|with|by)\b', '', title)
            title_clean = re.sub(r'[^\w\s]', '', title_clean)  # Remove punctuation
            title_clean = re.sub(r'\s+', ' ', title_clean).strip()  # Normalize spaces
            
            content = f"META:{title_clean}:{first_author}:{year}"
            logger.debug(f"Generating ID from metadata: {first_author}-{year}-{title_clean[:30]}...")
        
        # Generate hash and take first 8 characters
        hash_obj = hashlib.md5(content.encode('utf-8'))
        paper_id = hash_obj.hexdigest()[:8].upper()
        
        # Ensure it's a valid directory name
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
│   ├── chrome/ (get_chrome_cache_dir())
│   ├── auth/
│   │   └── <auth_type>/ (get_auth_cache_dir(auth_type))
│   └── <cache_type>/
│       └── <cache_name>.json (get_cache_file(cache_name, cache_type))
├── config/ (.config_dir)
│   └── <config_name>.yaml (get_config_file(config_name))
├── library/ (.library_dir)
│   ├── indexes/ (get_indexes_dir())
│   ├── <collection_name>/ (get_collection_dir(collection_name))
│   │   └── <unique_id>/ (get_paper_storage_paths(paper_info, collection_name))
│   └── <collection_name>-human-readable/ (get_collection_readable_dir(collection_name))
│       └── <Author>-<Year>-<Journal>/ (get_paper_storage_paths(paper_info, collection_name))
├── log/ (.log_dir)
├── workspace/ (.workspace_dir) [Max: {self.constraints.max_workspace_size_mb}MB, {self.constraints.workspace_retention_days}d retention]
│   ├── downloads/ (get_downloads_dir()) [Max: {self.constraints.max_downloads_size_mb}MB, {self.constraints.downloads_retention_days}d retention]
│   ├── logs/ (get_workspace_logs_dir())
│   └── screenshots/ [Max: {self.constraints.max_screenshots_size_mb}MB, {self.constraints.screenshots_retention_days}d retention]
│       └── <screenshot_type>/ (get_screenshots_dir(screenshot_type))
└── backup/ (.backup_dir)"""

        print(structure)
        print(constraints_info)

# EOF
