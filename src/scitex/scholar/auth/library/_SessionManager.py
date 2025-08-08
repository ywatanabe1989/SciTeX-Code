#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:43:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_SessionManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_SessionManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Session management for authentication providers.

This module handles session state, validation, and expiry management
for authentication providers like OpenAthens.
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Handles session state and validation for authentication providers."""

    def __init__(self, default_expiry_hours: int = 8):
        """Initialize session manager.
        
        Args:
            default_expiry_hours: Default session expiry time in hours
        """
        self.default_expiry_hours = default_expiry_hours
        self.reset_session()
        
        # Live verification cache
        self._last_live_verified_at: Optional[float] = None
        self._live_verification_cache_seconds = 300  # 5 minutes

    def reset_session(self) -> None:
        """Reset all session data."""
        self._cookies: Dict[str, str] = {}
        self._full_cookies: List[Dict[str, Any]] = []
        self._session_expiry: Optional[datetime] = None

    def set_session_data(
        self, 
        cookies: Dict[str, str], 
        full_cookies: List[Dict[str, Any]], 
        expiry: Optional[datetime] = None
    ) -> None:
        """Set session data from authentication.
        
        Args:
            cookies: Simple cookie name-value pairs
            full_cookies: Full cookie objects with all attributes
            expiry: Session expiry time (defaults to current time + default_expiry_hours)
        """
        self._cookies = cookies
        self._full_cookies = full_cookies
        self._session_expiry = expiry or datetime.now() + timedelta(hours=self.default_expiry_hours)

    def has_valid_session_data(self) -> bool:
        """Check if session has basic required data."""
        return bool(self._cookies and self._session_expiry)

    def is_session_expired(self) -> bool:
        """Check if session is expired based on expiry time."""
        if not self._session_expiry:
            return True
        return datetime.now() > self._session_expiry

    def get_cookies(self) -> Dict[str, str]:
        """Get simple cookie dictionary."""
        return self._cookies.copy()

    def get_full_cookies(self) -> List[Dict[str, Any]]:
        """Get full cookie objects."""
        return self._full_cookies.copy()

    def get_session_async_expiry(self) -> Optional[datetime]:
        """Get session expiry time."""
        return self._session_expiry

    def get_session_info_async(self) -> Dict[str, Any]:
        """Get comprehensive session information."""
        return {
            "has_cookies": bool(self._cookies),
            "cookie_count": len(self._cookies),
            "expiry": self._session_expiry.isoformat() if self._session_expiry else None,
            "expired": self.is_session_expired(),
            "time_remaining": self._get_time_remaining(),
        }

    def format_expiry_info(self) -> str:
        """Format expiry information for display."""
        if not self._session_expiry:
            return ""

        now = datetime.now()
        remaining = self._session_expiry - now
        
        if remaining.total_seconds() <= 0:
            return " (expired)"
            
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return f" (expires in {hours}h {minutes}m)"

    def _get_time_remaining(self) -> Optional[Dict[str, int]]:
        """Get time remaining until expiry."""
        if not self._session_expiry:
            return None
            
        remaining = self._session_expiry - datetime.now()
        if remaining.total_seconds() <= 0:
            return {"hours": 0, "minutes": 0, "seconds": 0}
            
        return {
            "hours": int(remaining.total_seconds() // 3600),
            "minutes": int((remaining.total_seconds() % 3600) // 60),
            "seconds": int(remaining.total_seconds() % 60),
        }

    def mark_live_verification(self) -> None:
        """Mark that live verification was recently performed."""
        self._last_live_verified_at = time.time()

    def needs_live_verification(self) -> bool:
        """Check if live verification is needed (cache expired)."""
        if self._last_live_verified_at is None:
            return True
            
        elapsed = time.time() - self._last_live_verified_at
        return elapsed >= self._live_verification_cache_seconds

    def create_auth_response(self) -> Dict[str, Any]:
        """Create authentication response dictionary."""
        return {
            "cookies": self._full_cookies,
            "simple_cookies": self._cookies,
            "expiry": self._session_expiry,
        }


# EOF