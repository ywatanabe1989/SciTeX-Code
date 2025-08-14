#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 03:31:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/validation/_ValidationResult.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/validation/_ValidationResult.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Validation result container for PDF validation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class ValidationResult:
    """Result of PDF validation.
    
    Attributes:
        path: Path to the PDF file
        is_valid: Whether the PDF is valid
        file_size: Size in bytes
        page_count: Number of pages (if readable)
        has_text: Whether text can be extracted
        metadata: PDF metadata (title, author, etc.)
        errors: List of validation errors
        warnings: List of validation warnings
        timestamp: When validation was performed
    """
    
    path: str
    is_valid: bool
    file_size: int = 0
    page_count: Optional[int] = None
    has_text: bool = False
    metadata: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def is_complete(self) -> bool:
        """Check if PDF appears to be complete (not truncated)."""
        # Basic heuristics
        if not self.is_valid:
            return False
        if self.file_size < 1000:  # Less than 1KB is suspicious
            return False
        if self.page_count == 0:
            return False
        return True
    
    @property
    def is_text_searchable(self) -> bool:
        """Check if PDF has searchable text (not just scanned images)."""
        return self.has_text and self.page_count and self.page_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "is_valid": self.is_valid,
            "is_complete": self.is_complete,
            "is_text_searchable": self.is_text_searchable,
            "file_size": self.file_size,
            "file_size_mb": round(self.file_size / (1024 * 1024), 2) if self.file_size else 0,
            "page_count": self.page_count,
            "has_text": self.has_text,
            "metadata": self.metadata,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        """String representation."""
        status = "✓ Valid" if self.is_valid else "✗ Invalid"
        details = []
        
        if self.page_count:
            details.append(f"{self.page_count} pages")
        if self.file_size:
            size_mb = self.file_size / (1024 * 1024)
            details.append(f"{size_mb:.1f}MB")
        if self.has_text:
            details.append("searchable")
        
        detail_str = f" ({', '.join(details)})" if details else ""
        return f"{status} - {os.path.basename(self.path)}{detail_str}"


# EOF