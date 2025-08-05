#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 22:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/strategies/_ScholarLibraryStrategy.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/strategies/_ScholarLibraryStrategy.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Scholar library management strategy.

This module handles all interactions with the Scholar library system including
DOI lookup, paper storage, project symlink management, and unresolved entry tracking.
Extracted from SingleDOIResolver to follow Single Responsibility Principle.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from scitex import logging
from scitex.scholar.utils import TextNormalizer

logger = logging.getLogger(__name__)


class ScholarLibraryStrategy:
    """Strategy for managing Scholar library interactions and paper storage."""

    def __init__(self, config: Any, project: str = "master"):
        """Initialize Scholar library strategy.
        
        Args:
            config: ScholarConfig object for path management
            project: Project name for library organization
        """
        self.config = config
        self.project = project

    def check_library_for_doi(
        self, 
        title: str, 
        year: Optional[int] = None
    ) -> Optional[str]:
        """Check if DOI already exists in master Scholar library.
        
        Args:
            title: Paper title to search for
            year: Publication year (optional)
            
        Returns:
            DOI if found in library, None otherwise
        """
        try:
            master_dir = self.config.path_manager.get_scholar_library_path() / "MASTER"
            
            if not master_dir.exists():
                return None
            
            # Search through all paper directories in master
            for paper_dir in master_dir.iterdir():
                if not paper_dir.is_dir():
                    continue
                    
                metadata_file = paper_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        stored_title = metadata.get('title', '')
                        stored_year = metadata.get('year')
                        stored_doi = metadata.get('doi')
                        
                        # Title similarity check
                        title_match = self._is_title_similar(title, stored_title)
                        
                        # Year match check (if both available)
                        year_match = (
                            not year or not stored_year or 
                            abs(int(stored_year) - int(year)) <= 1 if 
                            isinstance(stored_year, (int, str)) and str(stored_year).isdigit()
                            else stored_year == year
                        )
                        
                        if title_match and year_match and stored_doi:
                            logger.info(f"DOI found in master Scholar library: {stored_doi} (paper_id: {paper_dir.name})")
                            return stored_doi
                            
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.debug(f"Error reading metadata from {metadata_file}: {e}")
                        continue
            
            return None
        except Exception as e:
            logger.debug(f"Error checking master Scholar library: {e}")
            return None

    def save_resolved_paper(
        self,
        title: str,
        doi: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: str = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None
    ) -> str:
        """Save successfully resolved paper to Scholar library.
        
        Args:
            title: Paper title
            doi: Resolved DOI
            year: Publication year
            authors: Author list
            source: Resolution source name
            metadata: Additional metadata from resolution
            bibtex_source: Original BibTeX source
            
        Returns:
            Paper ID (unique identifier) for the saved paper
        """
        try:
            # Create paper info with enhanced metadata
            paper_info = {
                'title': title,
                'year': year,
                'authors': authors or [],
                'doi': doi,
            }
            
            # Add journal info from metadata if available
            if metadata:
                if metadata.get('journal'):
                    paper_info['journal'] = metadata['journal']
                if not year and metadata.get('year'):
                    paper_info['year'] = metadata['year']
                if not authors and metadata.get('authors'):
                    paper_info['authors'] = metadata['authors']
            
            # Save to MASTER collection (single source of truth)
            master_storage_paths = self.config.path_manager.get_paper_storage_paths(
                paper_info=paper_info,
                collection_name="MASTER"
            )
            
            paper_id = master_storage_paths['unique_id']
            master_storage_path = master_storage_paths['storage_path']
            master_metadata_file = master_storage_path / "metadata.json"
            
            # Check for existing metadata to avoid overwriting
            existing_metadata = {}
            if master_metadata_file.exists():
                try:
                    with open(master_metadata_file, 'r') as f:
                        existing_metadata = json.load(f)
                except (json.JSONDecodeError, IOError):
                    existing_metadata = {}
            
            # Create comprehensive metadata with proper source tracking and cleaning
            # Clean text fields to remove HTML/XML tags
            clean_title = TextNormalizer.clean_metadata_text(existing_metadata.get('title', title))
            clean_abstract = None
            if metadata and metadata.get('abstract'):
                clean_abstract = TextNormalizer.clean_metadata_text(metadata['abstract'])
            elif existing_metadata.get('abstract'):
                clean_abstract = TextNormalizer.clean_metadata_text(existing_metadata['abstract'])
            
            # Determine DOI source with API name clarification
            doi_source_value = existing_metadata.get('doi_source')
            if not doi_source_value and source:
                if 'crossref' in source.lower():
                    doi_source_value = 'crossref'
                elif 'semantic' in source.lower():
                    doi_source_value = 'semantic_scholar'
                elif 'pubmed' in source.lower():
                    doi_source_value = 'pubmed'
                elif 'openalex' in source.lower():
                    doi_source_value = 'openalex'
                else:
                    doi_source_value = source
            
            comprehensive_metadata = {
                # Core bibliographic data (preserve existing if available)
                'title': clean_title,
                'title_source': existing_metadata.get('title_source', 'input'),
                'doi': existing_metadata.get('doi', doi),
                'doi_source': doi_source_value,
                'year': existing_metadata.get('year', paper_info.get('year')),
                'year_source': existing_metadata.get('year_source', 'input' if year is not None else (metadata.get('journal_source', source) if metadata and metadata.get('year') else None)),
                'authors': existing_metadata.get('authors', paper_info.get('authors', [])),
                'authors_source': existing_metadata.get('authors_source', 'input' if authors else (metadata.get('journal_source', source) if metadata and metadata.get('authors') else None)),
                
                # Journal information (only add if not already present)
                'journal': existing_metadata.get('journal', metadata.get('journal') if metadata else None),
                'journal_source': existing_metadata.get('journal_source', metadata.get('journal_source') if metadata else None),
                'short_journal': existing_metadata.get('short_journal', metadata.get('short_journal') if metadata else None),
                'publisher': existing_metadata.get('publisher', metadata.get('publisher') if metadata else None),
                'volume': existing_metadata.get('volume', metadata.get('volume') if metadata else None),
                'issue': existing_metadata.get('issue', metadata.get('issue') if metadata else None),
                'issn': existing_metadata.get('issn', metadata.get('issn') if metadata else None),
                
                # Abstract (only add if not already present, cleaned of HTML tags)
                'abstract': existing_metadata.get('abstract', clean_abstract),
                'abstract_source': existing_metadata.get('abstract_source', metadata.get('journal_source') if metadata and metadata.get('abstract') else None),
                
                # System identifiers (updated field names)
                'scitex_id': existing_metadata.get('scitex_id', existing_metadata.get('scholar_id', paper_id)),  # Renamed from scholar_id
                'created_at': existing_metadata.get('created_at', datetime.now().isoformat()),
                'created_by': existing_metadata.get('created_by', 'SciTeX Scholar'),  # Updated value
                'updated_at': datetime.now().isoformat(),
                
                # Project tracking
                'projects': existing_metadata.get('projects', [] if self.project == "master" else [self.project]),
                
                # Path information (no nesting - flattened structure)
                'master_storage_path': str(master_storage_path),
                'readable_name': master_storage_paths['readable_name'],
                'metadata_file': str(master_metadata_file),
            }
            
            # Ensure master storage directory exists
            master_storage_path.mkdir(parents=True, exist_ok=True)
            
            # Save comprehensive metadata
            with open(master_metadata_file, 'w') as f:
                json.dump(comprehensive_metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved paper to master Scholar library: {paper_id}")
            
            # Create project symlink if not master project
            if self.project != "master":
                self._ensure_project_symlink(title, year, authors, paper_id, master_storage_path)
            
            return paper_id
            
        except Exception as e:
            logger.error(f"Error saving paper to Scholar library: {e}")
            raise

    def save_unresolved_paper(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        reason: str = "DOI not found",
        bibtex_source: Optional[str] = None
    ) -> None:
        """Save paper that couldn't be resolved to unresolved directory.
        
        Args:
            title: Paper title
            year: Publication year
            authors: Author list
            reason: Reason for resolution failure
            bibtex_source: Original BibTeX source
        """
        try:
            # Create unresolved entry info with cleaned title
            clean_title = TextNormalizer.clean_metadata_text(title) if title else ""
            unresolved_info = {
                'title': clean_title,
                'year': year,
                'authors': authors or [],
                'reason': reason,
                'bibtex_source': bibtex_source,
                'project': self.project,
                'created_at': datetime.now().isoformat(),
                'created_by': 'SciTeX Scholar'  # Updated value
            }
            
            # Get project-specific unresolved directory
            project_lib_path = self.config.path_manager.get_scholar_library_path() / self.project
            unresolved_dir = project_lib_path / "unresolved"
            unresolved_dir.mkdir(parents=True, exist_ok=True)
            
            # Create safe filename from title
            safe_title = title or "untitled"
            safe_title = re.sub(r'[^\w\s-]', '', safe_title)[:50]
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            unresolved_file = unresolved_dir / f"{safe_title}_{timestamp}.json"
            
            # Save unresolved entry
            with open(unresolved_file, 'w') as f:
                json.dump(unresolved_info, f, indent=2, ensure_ascii=False)
            
            logger.warning(f"Saved unresolved entry: {unresolved_file.name}")
            
        except Exception as e:
            logger.error(f"Error saving unresolved entry: {e}")

    def _ensure_project_symlink(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        paper_id: str = None,
        master_storage_path: Path = None
    ) -> None:
        """Ensure project symlink exists for paper in master library.
        
        Args:
            title: Paper title
            year: Publication year
            authors: Author list
            paper_id: Master paper ID
            master_storage_path: Path to master storage
        """
        try:
            if not paper_id or not master_storage_path:
                return
                
            # Get project directory
            project_lib_path = self.config.path_manager.get_scholar_library_path() / self.project
            project_lib_path.mkdir(parents=True, exist_ok=True)
            
            # Create readable symlink name
            paper_info = {
                'title': title,
                'year': year,
                'authors': authors or []
            }
            
            readable_paths = self.config.path_manager.get_paper_storage_paths(
                paper_info=paper_info,
                collection_name=self.project
            )
            
            readable_name = readable_paths['readable_name']
            symlink_path = project_lib_path / readable_name
            
            # Create relative symlink to MASTER
            relative_path = f"../MASTER/{paper_id}"
            
            if not symlink_path.exists():
                symlink_path.symlink_to(relative_path)
                logger.info(f"Created project symlink: {readable_name} -> {relative_path}")
            
        except Exception as e:
            logger.debug(f"Error creating project symlink: {e}")

    def _is_title_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """Check if two titles are similar enough to be considered the same paper.
        
        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            True if titles are similar enough
        """
        if not title1 or not title2:
            return False
        
        # Normalize titles for comparison
        def normalize_title(title: str) -> str:
            title = title.lower()
            title = re.sub(r'[^\w\s]', ' ', title)
            title = re.sub(r'\s+', ' ', title)
            return title.strip()
        
        norm_title1 = normalize_title(title1)
        norm_title2 = normalize_title(title2)
        
        # Simple word-based Jaccard similarity
        words1 = set(norm_title1.split())
        words2 = set(norm_title2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0.0
        
        return similarity >= threshold


# Export
__all__ = ["ScholarLibraryStrategy"]

# EOF