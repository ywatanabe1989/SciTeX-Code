#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 07:35:36 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/utils/AuthLockManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/utils/AuthLockManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""File-based locking for authentication operations.

This module provides file-based locking to prevent concurrent
authentication attempts that could interfere with each other.
"""

import asyncio
import fcntl
import time
from pathlib import Path
from typing import Optional

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class AuthLockError(ScholarError):
    """Raised when lock operations fail."""

    pass


class AuthLockManager:
    """Manages file-based locks for authentication operations."""

    def __init__(self, lock_file: Path, max_wait_seconds: int = 300):
        """Initialize lock manager.

        Args:
            lock_file: Path to the lock file
            max_wait_seconds: Maximum time to wait for lock acquisition
        """
        self.name = self.__class__.__name__
        self.lock_file = lock_file
        self.max_wait_seconds = max_wait_seconds
        self._lock_fd: Optional[int] = None
        self._is_locked = False

    def _is_lock_stale(self, max_age_seconds: int = 600) -> bool:
        """Check if lock file is stale (older than max_age).

        A stale lock indicates a crashed process that didn't clean up.

        Args:
            max_age_seconds: Maximum age before considering lock stale (default: 10 min)

        Returns:
            True if lock exists and is stale
        """
        if not self.lock_file.exists():
            return False

        lock_age = time.time() - self.lock_file.stat().st_mtime
        return lock_age > max_age_seconds

    def _clean_stale_lock(self) -> bool:
        """Remove stale lock file.

        Returns:
            True if stale lock was removed
        """
        if self._is_lock_stale():
            try:
                self.lock_file.unlink()
                logger.warning(f"{self.name}: Removed stale lock file: {self.lock_file}")
                return True
            except Exception as e:
                logger.error(f"{self.name}: Could not remove stale lock: {e}")
        return False

    async def acquire_lock_async(self) -> bool:
        """Acquire the file lock with timeout.

        Automatically cleans stale locks before attempting acquisition.

        Returns:
            True if lock acquired, False if timeout

        Raises:
            AuthLockError: If lock acquisition fails unexpectedly
        """
        if self._is_locked:
            logger.warning(f"{self.name}: Lock already acquired")
            return True

        # Clean stale lock before attempting
        if self._clean_stale_lock():
            logger.info(f"{self.name}: Cleaned stale lock, retrying acquisition")

        start_time = time.time()

        while time.time() - start_time < self.max_wait_seconds:
            if await self._try_acquire_lock_async():
                self._is_locked = True
                logger.info(f"{self.name}: Acquired authentication lock")
                return True

            # Check for stale lock every 10 seconds
            if (time.time() - start_time) % 10 < 2:
                if self._clean_stale_lock():
                    logger.info(f"{self.name}: Cleaned stale lock during wait")
                    continue

            logger.info(
                f"{self.name}: Waiting for authentication lock ({self.lock_file})..."
            )
            await asyncio.sleep(2)

        logger.error(
            f"{self.name}: Could not acquire authentication lock after {self.max_wait_seconds} seconds"
        )
        return False

    async def release_lock_async(self) -> None:
        """Release the file lock."""
        if not self._is_locked:
            return

        try:
            if self._lock_fd is not None:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
                self._lock_fd = None

            # Clean up lock file
            try:
                self.lock_file.unlink()
            except FileNotFoundError:
                pass

            self._is_locked = False
            logger.debug(f"{self.name}: Released authentication lock")

        except Exception as e:
            logger.warning(f"{self.name}: Error releasing lock: {e}")

    def is_locked(self) -> bool:
        """Check if lock is currently held."""
        return self._is_locked

    async def _try_acquire_lock_async(self) -> bool:
        """Try to acquire lock once.

        Returns:
            True if acquired, False if failed
        """
        try:
            # Open lock file
            fd = os.open(
                self.lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600
            )

            # Try to acquire exclusive lock non-blocking
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            self._lock_fd = fd
            return True

        except (IOError, OSError):
            # Lock is held by another process
            if "fd" in locals():
                try:
                    os.close(fd)
                except:
                    pass
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.acquire_lock_async():
            raise AuthLockError(
                f"Could not acquire lock after {self.max_wait_seconds} seconds"
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release_lock_async()

# EOF
