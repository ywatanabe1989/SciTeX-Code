#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_LockManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_LockManager.py"
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


class LockError(ScholarError):
    """Raised when lock operations fail."""
    pass


class LockManager:
    """Manages file-based locks for authentication operations."""

    def __init__(self, lock_file: Path, max_wait_seconds: int = 300):
        """Initialize lock manager.
        
        Args:
            lock_file: Path to the lock file
            max_wait_seconds: Maximum time to wait for lock acquisition
        """
        self.lock_file = lock_file
        self.max_wait_seconds = max_wait_seconds
        self._lock_fd: Optional[int] = None
        self._is_locked = False

    async def acquire_lock_async(self) -> bool:
        """Acquire the file lock with timeout.
        
        Returns:
            True if lock acquired, False if timeout
            
        Raises:
            LockError: If lock acquisition fails unexpectedly
        """
        if self._is_locked:
            logger.warn("Lock already acquired")
            return True

        start_time = time.time()
        
        while time.time() - start_time < self.max_wait_seconds:
            if await self._try_acquire_lock_async():
                self._is_locked = True
                logger.info("Acquired authentication lock")
                return True
                
            logger.debug("Waiting for authentication lock...")
            await asyncio.sleep(2)

        logger.error(f"Could not acquire authentication lock after {self.max_wait_seconds} seconds")
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
            logger.debug("Released authentication lock")
            
        except Exception as e:
            logger.warn(f"Error releasing lock: {e}")

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
            fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
            
            # Try to acquire exclusive lock non-blocking
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            self._lock_fd = fd
            return True
            
        except (IOError, OSError):
            # Lock is held by another process
            if 'fd' in locals():
                try:
                    os.close(fd)
                except:
                    pass
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.acquire_lock_async():
            raise LockError(f"Could not acquire lock after {self.max_wait_seconds} seconds")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release_lock_async()


# EOF