#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 20:07:34 (ywatanabe)"
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
from pathlib import Path
from typing import Dict, Optional


class PathManager:
    def __init__(self, scholar_dir: Optional[Path] = None):
        if scholar_dir is None:
            scholar_dir = (
                Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
                / "scholar"
            )

        self.scholar_dir = scholar_dir
        self._ensure_directories()

    def _ensure_directories(self):
        for dir_path in [
            self.cache_dir,
            self.config_dir,
            self.library_dir,
            self.log_dir,
            self.workspace_dir,
            self.backups_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @property
    def cache_dir(self) -> Path:
        return self.scholar_dir / "cache"

    @property
    def config_dir(self) -> Path:
        return self.scholar_dir / "config"

    @property
    def library_dir(self) -> Path:
        return self.scholar_dir / "library"

    @property
    def log_dir(self) -> Path:
        return self.scholar_dir / "log"

    @property
    def workspace_dir(self) -> Path:
        return self.scholar_dir / "workspace"

    @property
    def backup_dir(self) -> Path:
        return self.scholar_dir / "backup"

    def get_chrome_cache_dir(self) -> Path:
        return self.cache_dir / "chrome"

    def get_auth_cache_dir(self, auth_type: str) -> Path:
        return self.cache_dir / "auth" / auth_type

    def get_collection_dir(self, collection_name: str) -> Path:
        collection_dir = self.library_dir / collection_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        return collection_dir

    def get_collection_readable_dir(self, collection_name: str) -> Path:
        readable_dir = self.library_dir / f"{collection_name}-human-readable"
        readable_dir.mkdir(parents=True, exist_ok=True)
        return readable_dir

    def get_indexes_dir(self) -> Path:
        indexes_dir = self.library_dir / "indexes"
        indexes_dir.mkdir(parents=True, exist_ok=True)
        return indexes_dir

    def get_paper_storage_paths(
        self, paper_info: Dict, collection_name: str = "default"
    ) -> Dict[str, Path]:
        unique_id = self._generate_paper_id(
            paper_info["url"], paper_info["title"]
        )
        collection_dir = self.get_collection_dir(collection_name)
        storage_path = collection_dir / unique_id

        first_author = (
            paper_info["authors"][0].split()[-1]
            if paper_info["authors"]
            else "Unknown"
        )
        readable_name = (
            f"{first_author}-{paper_info['year']}-{paper_info['journal']}"
        )
        readable_dir = self.get_collection_readable_dir(collection_name)
        readable_path = readable_dir / readable_name

        return {
            "storage_path": storage_path,
            "readable_path": readable_path,
            "unique_id": unique_id,
        }

    def get_screenshots_dir(self, screenshot_type: str = "general") -> Path:
        screenshots_dir = self.workspace_dir / "screenshots" / screenshot_type
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        return screenshots_dir

    def get_downloads_dir(self) -> Path:
        downloads_dir = self.workspace_dir / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        return downloads_dir

    def get_workspace_logs_dir(self) -> Path:
        logs_dir = self.workspace_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    def get_cache_file(
        self, cache_name: str, cache_type: str = "general"
    ) -> Path:
        cache_file = self.cache_dir / cache_type / f"{cache_name}.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        return cache_file

    def get_lock_file(self, file_path: Path) -> Path:
        return Path(str(file_path) + ".lock")

    def get_config_file(self, config_name: str) -> Path:
        return self.config_dir / f"{config_name}.yaml"

    def _generate_paper_id(self, url: str, title: str) -> str:
        content = f"{url}:{title}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:8].upper()

    def print_expected_structure(self):
        """Print expected directory tree structure with methods and arguments"""
        base = str(self.scholar_dir)
        print(
            f"""{base}/
├── cache/ (.cache_dir)
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
├── workspace/ (.workspace_dir)
│   ├── downloads/ (get_downloads_dir())
│   ├── logs/ (get_workspace_logs_dir())
│   └── screenshots/
│       └── <screenshot_type>/ (get_screenshots_dir(screenshot_type))
└── backup/ (.backup_dir)"""
        )

# EOF
