#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:06:00 (ywatanabe)"
# File: ./src/scitex/scholar/download/_BaseDownloadStrategy.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/download/_BaseDownloadStrategy.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Abstract base class for PDF download strategies.

This module provides the base interface that all download strategies
(Direct, Sci-Hub, Browser-based, etc.) must implement.
"""

"""Imports"""
from scitex import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from ...errors import PDFDownloadError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class BaseDownloadStrategy(ABC):
    """
    Abstract base class for PDF download strategies.
    
    All download strategies should inherit from this class and
    implement the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize download strategy.
        
        Args:
            config: Strategy-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__.replace("DownloadStrategy", "")
        
    @abstractmethod
    async def can_handle(self, url: str) -> bool:
        """
        Check if this strategy can handle the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if strategy can handle this URL
        """
        pass
        
    @abstractmethod
    async def download(
        self,
        url: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
        **kwargs
    ) -> bool:
        """
        Download PDF from URL.
        
        Args:
            url: URL to download from
            save_path: Path to save the PDF
            progress_callback: Optional callback for progress updates
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            True if download successful
            
        Raises:
            PDFDownloadError: If download fails
        """
        pass
        
    @abstractmethod
    async def validate_pdf(self, file_path: Path) -> bool:
        """
        Validate that downloaded file is a valid PDF.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is a valid PDF
        """
        pass
        
    def get_priority(self) -> int:
        """
        Get the priority of this strategy.
        
        Higher priority strategies are tried first.
        
        Returns:
            Priority value (higher = higher priority)
        """
        return self.config.get("priority", 50)
        
    def __str__(self) -> str:
        """String representation of strategy."""
        return f"{self.name}DownloadStrategy"
        
    def __repr__(self) -> str:
        """Detailed representation of strategy."""
        return f"<{self.name}DownloadStrategy(priority={self.get_priority()})>"

# EOF