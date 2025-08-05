#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 22:42:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download_async/_BaseDownloadStrategy.py
# ----------------------------------------
"""Base class for PDF download_async strategies.

This abstract base class defines the interface that all download_async strategies
must implement. Each strategy represents a different method of download_asyncing
PDFs (e.g., direct download_async, browser automation, API access).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class BaseDownloadStrategy(ABC):
    """Abstract base class for PDF download_async strategies."""
    
    def __init__(self):
        """Initialize base download_async strategy."""
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def can_download_async(self, url: str, metadata: Dict[str, Any]) -> bool:
        """Check if this strategy can handle the given URL.
        
        Args:
            url: URL to check
            metadata: Additional metadata (doi, title, etc.)
            
        Returns:
            True if this strategy can handle the URL
        """
        pass
        
    @abstractmethod
    async def download_async(
        self,
        url: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        session_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """Download PDF from the given URL.
        
        Args:
            url: URL to download_async from
            output_path: Where to save the PDF
            metadata: Additional metadata about the paper
            session_data: Authentication session data (cookies, headers)
            
        Returns:
            Path to download_asynced PDF or None if failed
        """
        pass
        
    def __str__(self) -> str:
        """String representation of the strategy."""
        return self.name