#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-12 01:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/_ScholarPipelineBase.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/_ScholarPipelineBase.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Base class for all Scholar processing pipelines
  - Provides shared services (auth, browser, library, metadata engine)
  - Implements lazy initialization pattern for performance
  - Defines abstract run() method for pipeline execution

Dependencies:
  - packages:
    - scitex
    - pydantic

IO:
  - input-files:
    - None (base class, no direct I/O)
  - output-files:
    - None (subclasses define their own I/O)
"""

"""Imports"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)

"""Functions & Classes"""


class ScholarPipelineBase(ABC):
    """
    Base class for all Scholar pipelines.

    Provides common functionality:
    - Configuration management
    - Service initialization (lazy)
    - Logging
    - Error handling
    """

    def __init__(self, config: Optional[ScholarConfig] = None):
        """
        Initialize pipeline with configuration.

        Args:
            config: ScholarConfig instance (creates default if None)
        """
        self.config = config or ScholarConfig.load()
        self.name = self.__class__.__name__

        # Lazy-loaded services (initialized on first access)
        self._auth_manager = None
        self._browser_manager = None
        self._library_manager = None
        self._scholar_engine = None

    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        Execute the pipeline.

        Must be implemented by subclasses.

        Returns:
            Pipeline-specific result
        """
        pass

    # Service accessors (lazy initialization)
    @property
    def auth_manager(self):
        """Get authentication manager (lazy init)."""
        if self._auth_manager is None:
            from scitex.scholar.auth import ScholarAuthManager
            self._auth_manager = ScholarAuthManager()
        return self._auth_manager

    @property
    def browser_manager(self):
        """Get browser manager (lazy init)."""
        if self._browser_manager is None:
            from scitex.scholar.browser import ScholarBrowserManager
            self._browser_manager = ScholarBrowserManager(
                auth_manager=self.auth_manager,
                chrome_profile_name="system",
                browser_mode="stealth",
            )
        return self._browser_manager

    @property
    def library_manager(self):
        """Get library manager (lazy init)."""
        if self._library_manager is None:
            from scitex.scholar.storage import LibraryManager
            self._library_manager = LibraryManager(config=self.config)
        return self._library_manager

    @property
    def scholar_engine(self):
        """Get scholar engine for metadata (lazy init)."""
        if self._scholar_engine is None:
            from scitex.scholar.metadata_engines import ScholarEngine
            self._scholar_engine = ScholarEngine(config=self.config)
        return self._scholar_engine


# EOF
