#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 11:23:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/core/_PathManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/config/core/_PathManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PathManager with complete PATH_STRUCTURE integration.

All directory paths are defined in PATH_STRUCTURE at the top.
All get_ methods use PATH_STRUCTURE consistently.
No direct path concatenation (self.*_dir / "subdir").
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


# Directory structure definition
# All paths are relative to SCHOLAR_DIR (default: ~/.scitex/scholar)
# Only SCITEX_DIR is configurable via environment variable
PATH_STRUCTURE = {
    # Base
    "config_dir": "config",
    "backup_dir": "backup",
    "log_dir": "log",
    # Cache
    "cache_dir": "cache",
    "cache_auth_dir": "cache/auth",
    "cache_auth_json": "cache/auth/{auth_name}.json",
    "cache_auth_json_lock": "cache/auth/{auth_name}.json.lock",
    "cache_chrome_dir": "cache/chrome",
    "cache_engine_dir": "cache/engine",
    "cache_url_dir": "cache/url",
    "cache_download_dir": "cache/pdf_downloader",
    # Library
    "library_dir": "library",
    "library_downloads_dir": "library/downloads",  # STAGING
    "library_master_dir": "library/MASTER",  # STORAGE
    "library_project_dir": "library/{project_name}",
    "library_project_info_dir": "library/{project_name}/info",
    "library_project_info_bibtex_dir": "library/{project_name}/info/bibtex",
    "library_project_logs_dir": "library/{project_name}/logs",
    "library_project_screenshots_dir": "library/{project_name}/screenshots",
    "library_master_paper_dir": "library/MASTER/{paper_id}",
    "library_master_paper_screenshots_dir": "library/MASTER/{paper_id}/screenshots",
    # Individual Entry
    "entry_name": "PDF-{pdf_state}-CC-{citation_count:06d}_IF-{impact_factor_of_the_journal:03d}_{year:04d}_{first_author}_{journal_name}",
    "library_project_entry_dir": "library/{project_name}/{entry_name}",
    "library_project_entry_metadata_json": "library/{project_name}/{entry_name}/metadata.json",
    "library_project_entry_logs_dir": "library/{project_name}/{entry_name}/logs",
    # Workspace
    "workspace_dir": "workspace",
    "workspace_logs_dir": "workspace/logs",
    "workspace_screenshots_dir": "workspace/screenshots",
    "workspace_screenshots_category_dir": "workspace/screenshots/{category}",
}


@dataclass
class TidinessConstraints:
    """Configuration for directory tidiness constraints."""

    max_filename_length: int = 100
    allowed_filename_chars: str = r"[a-zA-Z0-9._-]"
    forbidden_filename_patterns: List[str] = field(
        default_factory=lambda: [r"^\.", r"^~", r"\s{2,}", r"[<>:\"/\\|?*]"]
    )

    max_cache_size_mb: int = 1000
    max_workspace_size_mb: int = 2000
    max_screenshots_size_mb: int = 500
    max_downloads_size_mb: int = 1000

    cache_retention_days: int = 30
    workspace_retention_days: int = 7
    screenshots_retention_days: int = 14
    downloads_retention_days: int = 3

    max_directory_depth: int = 8
    max_collection_name_length: int = 50
    allowed_collection_chars: str = r"[a-zA-Z0-9_-]"


class PathManager:
    """PathManager with all paths defined in PATH_STRUCTURE."""

    def __init__(
        self,
        scholar_dir: Optional[Path] = None,
        constraints: Optional[TidinessConstraints] = None,
    ):
        # Root directory (only configurable path)
        if scholar_dir is None:
            scitex_dir = os.getenv("SCITEX_DIR", Path.home() / ".scitex")
            scholar_dir = Path(scitex_dir) / "scholar"
        self.scholar_dir = Path(scholar_dir).expanduser()

        # Build all fixed directory paths from PATH_STRUCTURE
        self.dirs = {}
        for key, relative_path in PATH_STRUCTURE.items():
            if "{" not in relative_path:  # Skip placeholders
                self.dirs[key] = self.scholar_dir / relative_path

        self.constraints = constraints or TidinessConstraints()

    def _ensure_directory(self, path: Path, mode: int = 0o755) -> Path:
        """Helper to ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True, mode=mode)
        return path

    # ========================================
    # Base Directory Properties
    # ========================================
    @property
    def cache_dir(self) -> Path:
        return self._ensure_directory(self.dirs["cache_dir"])

    @property
    def config_dir(self) -> Path:
        return self._ensure_directory(self.dirs["config_dir"])

    @property
    def library_dir(self) -> Path:
        return self._ensure_directory(self.dirs["library_dir"])

    @property
    def log_dir(self) -> Path:
        return self._ensure_directory(self.dirs["log_dir"])

    @property
    def workspace_dir(self) -> Path:
        return self._ensure_directory(self.dirs["workspace_dir"])

    @property
    def backup_dir(self) -> Path:
        return self._ensure_directory(self.dirs["backup_dir"])

    # ========================================
    # Cache Directories
    # ========================================
    def get_cache_auth_dir(self) -> Path:
        """cache/auth"""
        return self._ensure_directory(self.dirs["cache_auth_dir"])

    def get_cache_auth_json(self, auth_name) -> Path:
        """cache/auth/{auth_name}.json"""
        return self.scholar_dir / PATH_STRUCTURE["cache_auth_json"].format(
            auth_name=auth_name
        )

    def get_cache_auth_json_lock(self, auth_name) -> Path:
        """cache/auth/{auth_name}.json.lock"""
        return self.scholar_dir / PATH_STRUCTURE[
            "cache_auth_json_lock"
        ].format(auth_name=auth_name)

    def get_cache_chrome_dir(self, profile_name: str) -> Path:
        """cache/chrome/{profile_name}"""
        return self._ensure_directory(
            self.dirs["cache_chrome_dir"] / profile_name
        )

    def get_cache_engine_dir(self) -> Path:
        """cache/engine"""
        return self._ensure_directory(self.dirs["cache_engine_dir"])

    def get_cache_url_dir(self) -> Path:
        """cache/url"""
        return self._ensure_directory(self.dirs["cache_url_dir"])

    def get_cache_download_dir(self) -> Path:
        """cache/pdf_downloader"""
        return self._ensure_directory(self.dirs["cache_download_dir"])

    # ========================================
    # Library Directories
    # ========================================
    def get_library_downloads_dir(self) -> Path:
        """library/downloads - STAGING for browser downloads"""
        return self._ensure_directory(self.dirs["library_downloads_dir"])

    def get_library_master_dir(self) -> Path:
        """library/MASTER - STORAGE for papers"""
        return self._ensure_directory(self.dirs["library_master_dir"])

    def get_library_project_dir(self, project: str) -> Path:
        """library/{project_name}"""
        project = self._sanitize_collection_name(project)
        assert project.upper() != "MASTER", "MASTER is reserved"

        path_template = PATH_STRUCTURE["library_project_dir"]
        relative_path = path_template.format(project_name=project)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_project_info_dir(self, project: str) -> Path:
        """library/{project_name}/info"""
        project = self._sanitize_collection_name(project)
        path_template = PATH_STRUCTURE["library_project_info_dir"]
        relative_path = path_template.format(project_name=project)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_project_info_bibtex_dir(self, project: str) -> Path:
        """library/{project_name}/info/bibtex"""
        project = self._sanitize_collection_name(project)
        path_template = PATH_STRUCTURE["library_project_info_bibtex_dir"]
        relative_path = path_template.format(project_name=project)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_project_logs_dir(self, project: str) -> Path:
        """library/{project_name}/logs"""
        project = self._sanitize_collection_name(project)
        path_template = PATH_STRUCTURE["library_project_logs_dir"]
        relative_path = path_template.format(project_name=project)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_project_screenshots_dir(self, project: str) -> Path:
        """library/{project_name}/screenshots"""
        project = self._sanitize_collection_name(project)
        path_template = PATH_STRUCTURE["library_project_screenshots_dir"]
        relative_path = path_template.format(project_name=project)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_master_paper_dir(self, paper_id: str) -> Path:
        """library/MASTER/{paper_id}"""
        path_template = PATH_STRUCTURE["library_master_paper_dir"]
        relative_path = path_template.format(paper_id=paper_id)
        return self._ensure_directory(self.scholar_dir / relative_path)

    def get_library_master_paper_screenshots_dir(self, paper_id: str) -> Path:
        """library/MASTER/{paper_id}/screenshots"""
        path_template = PATH_STRUCTURE["library_master_paper_screenshots_dir"]
        relative_path = path_template.format(paper_id=paper_id)
        return self._ensure_directory(self.scholar_dir / relative_path)

    # ========================================
    # Workspace Directories
    # ========================================
    def get_workspace_logs_dir(self) -> Path:
        """workspace/logs"""
        return self._ensure_directory(self.dirs["workspace_logs_dir"])

    def get_workspace_screenshots_dir(
        self, category: Optional[str] = None
    ) -> Path:
        """workspace/screenshots or workspace/screenshots/{category}"""
        if category:
            category = self._sanitize_filename(category)
            path_template = PATH_STRUCTURE[
                "workspace_screenshots_category_dir"
            ]
            relative_path = path_template.format(category=category)
            return self._ensure_directory(self.scholar_dir / relative_path)
        else:
            return self._ensure_directory(
                self.dirs["workspace_screenshots_dir"]
            )

    # ========================================
    # Helper Methods
    # ========================================
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename."""
        for pattern in self.constraints.forbidden_filename_patterns:
            filename = re.sub(pattern, "", filename)

        filename = re.sub(
            f"[^{self.constraints.allowed_filename_chars}]", "_", filename
        )
        filename = re.sub(r"_{2,}", "_", filename)

        if len(filename) > self.constraints.max_filename_length:
            name, ext = os.path.splitext(filename)
            max_name_len = self.constraints.max_filename_length - len(ext)
            filename = name[:max_name_len] + ext

        filename = filename.strip("._")

        if not filename:
            filename = f"unnamed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return filename

    def _sanitize_collection_name(self, collection_name: str) -> str:
        """Sanitize collection/project name."""
        collection_name = re.sub(
            f"[^{self.constraints.allowed_collection_chars}]",
            "_",
            collection_name,
        )
        collection_name = re.sub(r"_{2,}", "_", collection_name)

        if len(collection_name) > self.constraints.max_collection_name_length:
            collection_name = collection_name[
                : self.constraints.max_collection_name_length
            ]

        collection_name = collection_name.strip("_")

        if not collection_name:
            collection_name = f"collection_{datetime.now().strftime('%Y%m%d')}"

        return collection_name

    def _generate_paper_id(
        self, doi=None, title=None, authors=None, year=None
    ) -> str:
        """Generate unique 8-digit paper ID."""
        doi = doi.strip() if isinstance(doi, str) and doi else None
        title = title.strip() if isinstance(title, str) and title else ""
        year = str(year) if year else ""

        if doi:
            clean_doi = doi.replace("https://doi.org/", "").replace(
                "http://dx.doi.org/", ""
            )
            content = f"DOI:{clean_doi}"
        else:
            first_author = "unknown"
            if authors and len(authors) > 0:
                author_parts = str(authors[0]).strip().split()
                if author_parts:
                    first_author = author_parts[-1].lower()

            title_clean = re.sub(
                r"\b(the|and|of|in|on|at|to|for|with|by)\b", "", title.lower()
            )
            title_clean = re.sub(r"[^\w\s]", "", title_clean)
            title_clean = re.sub(r"\s+", " ", title_clean).strip()

            content = f"META:{title_clean}:{first_author}:{year}"

        hash_obj = hashlib.md5(content.encode("utf-8"))
        paper_id = hash_obj.hexdigest()[:8].upper()
        return self._sanitize_filename(paper_id)

    # ========================================
    # Maintenance
    # ========================================
    def perform_maintenance(self) -> Dict[str, int]:
        """Perform directory maintenance using get_ methods."""
        results = {
            "cache_cleaned": 0,
            "workspace_cleaned": 0,
            "screenshots_cleaned": 0,
            "downloads_cleaned": 0,
        }

        results["cache_cleaned"] = self._cleanup_old_files(
            self.get_cache_dir(), self.constraints.cache_retention_days
        )
        results["workspace_cleaned"] = self._cleanup_old_files(
            self.get_workspace_logs_dir(),
            self.constraints.workspace_retention_days,
        )
        results["screenshots_cleaned"] = self._cleanup_old_files(
            self.get_workspace_screenshots_dir(),
            self.constraints.screenshots_retention_days,
        )
        results["downloads_cleaned"] = self._cleanup_old_files(
            self.get_library_downloads_dir(),
            self.constraints.downloads_retention_days,
        )

        return results

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
        except (PermissionError, OSError) as e:
            logger.warning(f"Error during cleanup: {e}")

        return cleaned_count

# EOF
