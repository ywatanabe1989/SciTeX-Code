#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 13:59:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/library/_CacheManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/library/_CacheManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Cache management for authentication sessions.

This module handles saving and loading authentication session data
to/from cache files with proper permissions and error handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from scitex import logging

from ...config import ScholarConfig
from ._SessionManager import SessionManager

logger = logging.getLogger(__name__)


class CacheManager:
    """Handles session cache operations for authentication providers."""

    def __init__(
        self,
        cache_name: str,
        config: ScholarConfig,
        email: Optional[str] = None,
    ):
        """Initialize cache manager.

        Args:
            cache_name: Name for the cache file (e.g., "openathens")
            config: ScholarConfig instance for path management
            email: User email for validation
        """
        self.cache_name = cache_name
        self.config = config
        self.email = email
        self.cache_file, self.lock_file = self._setup_cache_files()

    def _setup_cache_files(self) -> tuple[Path, Path]:
        """Setup cache and lock files using the config manager."""
        # Use simple, clear cache file structure: cache/auth/{cache_name}.json
        cache_file = self.config.paths.get_cache_file(self.cache_name, "auth")

        # Set proper permissions for auth directory
        auth_dir = cache_file.parent
        os.chmod(auth_dir, 0o700)

        # Create lock file path using config manager
        lock_file = self.config.paths.get_lock_file(cache_file)

        return cache_file, lock_file

    async def save_session_async(
        self, session_manager: SessionManager
    ) -> bool:
        """Save session data to cache file.

        Args:
            session_manager: SessionManager containing session data

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_data = self._create_cache_data(session_manager)

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            # Set secure permissions
            os.chmod(self.cache_file, 0o600)
            logger.success(f"Session saved to: {self.cache_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session cache: {e}")
            return False

    async def load_session_async(
        self, session_manager: SessionManager
    ) -> bool:
        """Load session data from cache file.

        Args:
            session_manager: SessionManager to populate with data

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.cache_file.exists():
            logger.debug(f"No session cache found at {self.cache_file}")
            return False

        try:
            cache_data = self._load_cache_data()
            if not cache_data:
                return False

            if not self._validate_cache_data(cache_data):
                return False

            self._populate_session_manager(session_manager, cache_data)
            logger.success(
                f"Loaded session from cache ({self.cache_file}): "
                f"{len(session_manager.get_cookies())} cookies"
                f"{session_manager.format_expiry_info()}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load session cache: {e}")
            return False

    def clear_cache(self) -> bool:
        """Clear cache file.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info(f"Cleared cache file: {self.cache_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_cache_file(self) -> Path:
        """Get cache file path."""
        return self.cache_file

    def get_lock_file(self) -> Path:
        """Get lock file path."""
        return self.lock_file

    def _create_cache_data(
        self, session_manager: SessionManager
    ) -> Dict[str, Any]:
        """Create cache data dictionary from session manager."""
        expiry = session_manager.get_session_async_expiry()
        return {
            "cookies": session_manager.get_cookies(),
            "full_cookies": session_manager.get_full_cookies(),
            "expiry": expiry.isoformat() if expiry else None,
            "email": self.email,
            "version": 2,
        }

    def _load_cache_data(self) -> Optional[Dict[str, Any]]:
        """Load cache data from file."""
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read cache file: {e}")
            return None

    def _validate_cache_data(self, cache_data: Dict[str, Any]) -> bool:
        """Validate cache data format and email match."""
        # Skip encrypted files
        if "encrypted" in cache_data:
            logger.warning(
                "Found encrypted session file - please re-authenticate_async"
            )
            return False

        # Check email match if specified
        if self.email:
            cached_email = cache_data.get("email", "")
            if cached_email and cached_email.lower() != self.email.lower():
                logger.debug(
                    f"Email mismatch: cached={cached_email}, current={self.email}"
                )
                return False

        return True

    def _populate_session_manager(
        self, session_manager: SessionManager, cache_data: Dict[str, Any]
    ) -> None:
        """Populate session manager with cache data."""
        cookies = cache_data.get("cookies", {})
        full_cookies = cache_data.get("full_cookies", [])

        expiry = None
        expiry_str = cache_data.get("expiry")
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)

        session_manager.set_session_data(cookies, full_cookies, expiry)

# EOF
