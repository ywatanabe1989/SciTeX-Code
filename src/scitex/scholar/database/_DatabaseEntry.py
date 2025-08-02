#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_DatabaseEntry.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_DatabaseEntry.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Database entry for a research paper."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import json


@dataclass
class DatabaseEntry:
    """Represents a paper entry in the database.
    
    Stores metadata, file locations, and validation status.
    """
    
    # Identifiers
    doi: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    
    # Basic metadata
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    
    # Enhanced metadata
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    impact_factor: Optional[float] = None
    impact_factor_source: Optional[str] = None
    citation_count: Optional[int] = None
    
    # URLs
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    openurl: Optional[str] = None
    
    # File information
    pdf_path: Optional[str] = None
    pdf_size: Optional[int] = None
    pdf_pages: Optional[int] = None
    pdf_valid: Optional[bool] = None
    pdf_complete: Optional[bool] = None
    pdf_searchable: Optional[bool] = None
    
    # Timestamps
    added_date: datetime = field(default_factory=datetime.now)
    downloaded_date: Optional[datetime] = None
    validated_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    # Organization
    tags: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    # Status
    download_status: str = "pending"  # pending, downloaded, failed, skipped
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            # Identifiers
            "doi": self.doi,
            "pmid": self.pmid,
            "arxiv_id": self.arxiv_id,
            "semantic_scholar_id": self.semantic_scholar_id,
            
            # Basic metadata
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "volume": self.volume,
            "pages": self.pages,
            
            # Enhanced metadata
            "abstract": self.abstract,
            "keywords": self.keywords,
            "impact_factor": self.impact_factor,
            "impact_factor_source": self.impact_factor_source,
            "citation_count": self.citation_count,
            
            # URLs
            "url": self.url,
            "pdf_url": self.pdf_url,
            "openurl": self.openurl,
            
            # File information
            "pdf_path": self.pdf_path,
            "pdf_size": self.pdf_size,
            "pdf_pages": self.pdf_pages,
            "pdf_valid": self.pdf_valid,
            "pdf_complete": self.pdf_complete,
            "pdf_searchable": self.pdf_searchable,
            
            # Timestamps
            "added_date": self.added_date.isoformat() if self.added_date else None,
            "downloaded_date": self.downloaded_date.isoformat() if self.downloaded_date else None,
            "validated_date": self.validated_date.isoformat() if self.validated_date else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            
            # Organization
            "tags": self.tags,
            "collections": self.collections,
            "notes": self.notes,
            
            # Status
            "download_status": self.download_status,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            
            # Custom fields
            "custom_fields": self.custom_fields,
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseEntry':
        """Create from dictionary."""
        # Handle datetime fields
        for field_name in ['added_date', 'downloaded_date', 'validated_date', 'last_accessed']:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)
    
    @classmethod
    def from_paper(cls, paper: 'Paper') -> 'DatabaseEntry':
        """Create from Paper object."""
        entry = cls(
            doi=paper.doi,
            pmid=paper.pmid,
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            journal=paper.journal,
            volume=paper.volume,
            pages=paper.pages,
            abstract=paper.abstract,
            keywords=paper.keywords,
            impact_factor=paper.impact_factor,
            citation_count=paper.citation_count,
            url=paper.url,
            pdf_url=paper.pdf_url,
        )
        
        # Set impact factor source if available
        if hasattr(paper, 'impact_factor_source'):
            entry.impact_factor_source = paper.impact_factor_source
        
        return entry
    
    def update_from_validation(self, validation_result: 'ValidationResult'):
        """Update entry with validation results."""
        self.pdf_valid = validation_result.is_valid
        self.pdf_complete = validation_result.is_complete
        self.pdf_searchable = validation_result.has_text
        self.pdf_size = validation_result.file_size
        self.pdf_pages = validation_result.page_count
        self.validation_errors = validation_result.errors
        self.validation_warnings = validation_result.warnings
        self.validated_date = datetime.now()
    
    def get_filename_safe_title(self) -> str:
        """Get filename-safe version of title."""
        if not self.title:
            return "untitled"
        
        # Remove special characters
        safe_title = "".join(c for c in self.title if c.isalnum() or c in " -_")
        safe_title = safe_title.strip().replace(" ", "_")
        
        # Limit length
        return safe_title[:100]
    
    def get_suggested_filename(self) -> str:
        """Get suggested PDF filename."""
        parts = []
        
        # Year
        if self.year:
            parts.append(str(self.year))
        
        # First author
        if self.authors:
            first_author = self.authors[0].split()[-1]  # Last name
            parts.append(first_author)
        
        # Title
        parts.append(self.get_filename_safe_title())
        
        return "_".join(parts) + ".pdf"
    
    def __str__(self) -> str:
        """String representation."""
        authors_str = self.authors[0] if self.authors else "Unknown"
        if len(self.authors) > 1:
            authors_str += " et al."
        
        return f"{authors_str} ({self.year}). {self.title}"


# EOF