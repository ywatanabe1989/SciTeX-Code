#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 12:07:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/_CacheManager.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/auth/_CacheManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
from pathlib import Path
from typing import Optional


class CacheManager:
    def __init__(
        self,
        provider: str,
        email: str,
        cache_dir: Optional[Path] = None,
    ):

        if not email:
            raise ValueError("Email is required for cache management")

        base_dir = cache_dir or Path.home() / ".scitex" / "scholar"
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()[:8]
        identifier = f"user_{email_hash}"

        self.cache_dir = base_dir / identifier
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.cache_dir, 0o700)

        self.cache_file = self.cache_dir / f"{provider}_session.json"
        self.lock_file = self.cache_dir / f"{provider}_{identifier}_auth.lock"


# class CacheManager:
#     """Manages cache directories and files for authenticators."""

#     @staticmethod
#     def get_user_cache_dir(
#         base_cache_dir: Optional[Path] = None,
#         user_id: Optional[str] = None,
#         email: Optional[str] = None,
#     ) -> Path:
#         """Get user-specific cache directory."""
#         base_dir = base_cache_dir or Path.home() / ".scitex" / "scholar"

#         if user_id:
#             cache_dir = base_dir / f"user_{user_id}"
#         elif email:
#             email_hash = hashlib.md5(email.lower().encode()).hexdigest()[:8]
#             cache_dir = base_dir / f"user_{email_hash}"
#         else:
#             cache_dir = base_dir

#         cache_dir.mkdir(parents=True, exist_ok=True)
#         os.chmod(cache_dir, 0o700)
#         return cache_dir

#     @staticmethod
#     def get_provider_cache_file(
#         cache_dir: Path, provider: str, identifier: Optional[str] = None
#     ) -> Path:
#         """Get provider-specific cache file."""
#         if identifier:
#             filename = f"{provider}_{identifier}.json"
#         else:
#             filename = f"{provider}_session.json"

#         return cache_dir / filename

# EOF
