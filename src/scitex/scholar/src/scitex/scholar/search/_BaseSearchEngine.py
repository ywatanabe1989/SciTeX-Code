#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:10:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_BaseSearchEngine.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/search/_BaseSearchEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Abstract base class for search engines.

This module provides the base interface that all search engines
(PubMed, Semantic Scholar, arXiv, etc.) must implement.
"""

"""Imports"""
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from .._Paper import Paper
from ...errors import SearchError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class BaseSearchEngine(ABC):
    """
    Abstract base class for academic search engines.
    
    All search engines should inherit from this class and
    implement the required methods.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize search engine.
        
        Args:
            api_key: Optional API key for the search service
        """
        self.api_key = api_key
        self.name = self.__class__.__name__.replace("Engine", "")
        
    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs
    ) -> List[Paper]:
        """
        Search for papers matching the query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            year_min: Minimum publication year filter
            year_max: Maximum publication year filter
            **kwargs: Additional engine-specific parameters
            
        Returns:
            List of Paper objects
            
        Raises:
            SearchError: If search fails
        """
        pass
        
    @abstractmethod
    async def get_paper_by_id(
        self,
        paper_id: str,
        id_type: str = "doi"
    ) -> Optional[Paper]:
        """
        Get a specific paper by its identifier.
        
        Args:
            paper_id: The paper identifier
            id_type: Type of identifier (doi, pmid, arxiv, etc.)
            
        Returns:
            Paper object or None if not found
        """
        pass
        
    @abstractmethod
    def supports_field_search(self) -> bool:
        """
        Check if engine supports field-specific searches.
        
        Returns:
            True if field search is supported
        """
        pass
        
    @abstractmethod
    def get_rate_limit(self) -> Dict[str, int]:
        """
        Get rate limit information for this engine.
        
        Returns:
            Dictionary with rate limit details
            (e.g., {"requests_per_second": 10})
        """
        pass
        
    def validate_query(self, query: str) -> bool:
        """
        Validate that query is valid for this engine.
        
        Args:
            query: Query to validate
            
        Returns:
            True if query is valid
        """
        if not query or not query.strip():
            return False
        return True
        
    def __str__(self) -> str:
        """String representation of engine."""
        return f"{self.name}SearchEngine"
        
    def __repr__(self) -> str:
        """Detailed representation of engine."""
        return f"<{self.name}SearchEngine(api_key={'***' if self.api_key else None})>"

# EOF