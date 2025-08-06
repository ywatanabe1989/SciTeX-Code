#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:05:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_DatabaseIndex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_DatabaseIndex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Database index for fast paper lookups."""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
from datetime import datetime

from scitex import logging

logger = logging.getLogger(__name__)


class DatabaseIndex:
    """Indexes papers for fast lookup by various fields.
    
    Maintains indices for:
    - DOI
    - Title (fuzzy matching)
    - Authors
    - Year
    - Journal
    - Tags
    - Collections
    """
    
    def __init__(self, index_dir: Optional[Path] = None):
        """Initialize database index.
        
        Args:
            index_dir: Directory to store index files
        """
        if index_dir is None:
            index_dir = Path.home() / ".scitex" / "scholar" / "database" / "indices"
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Primary indices
        self.doi_index: Dict[str, str] = {}  # doi -> entry_id
        self.title_index: Dict[str, List[str]] = defaultdict(list)  # normalized_title -> entry_ids
        self.author_index: Dict[str, List[str]] = defaultdict(list)  # author -> entry_ids
        self.year_index: Dict[int, List[str]] = defaultdict(list)  # year -> entry_ids
        self.journal_index: Dict[str, List[str]] = defaultdict(list)  # journal -> entry_ids
        
        # Organization indices
        self.tag_index: Dict[str, List[str]] = defaultdict(list)  # tag -> entry_ids
        self.collection_index: Dict[str, List[str]] = defaultdict(list)  # collection -> entry_ids
        
        # Status indices
        self.status_index: Dict[str, List[str]] = defaultdict(list)  # status -> entry_ids
        
        # Load existing indices
        self._load_indices()
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for fuzzy matching."""
        # Convert to lowercase and remove punctuation
        normalized = title.lower()
        for char in ".,;:!?()[]{}\"'":
            normalized = normalized.replace(char, " ")
        
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def _normalize_author(self, author: str) -> str:
        """Normalize author name."""
        # Simple normalization - could be enhanced
        return author.lower().strip()
    
    def add_entry(self, entry_id: str, entry: 'DatabaseEntry'):
        """Add entry to indices."""
        # DOI index
        if entry.doi:
            self.doi_index[entry.doi] = entry_id
        
        # Title index
        if entry.title:
            normalized_title = self._normalize_title(entry.title)
            self.title_index[normalized_title].append(entry_id)
        
        # Author index
        for author in entry.authors:
            normalized_author = self._normalize_author(author)
            self.author_index[normalized_author].append(entry_id)
        
        # Year index
        if entry.year:
            self.year_index[entry.year].append(entry_id)
        
        # Journal index
        if entry.journal:
            normalized_journal = entry.journal.lower()
            self.journal_index[normalized_journal].append(entry_id)
        
        # Tag index
        for tag in entry.tags:
            self.tag_index[tag.lower()].append(entry_id)
        
        # Collection index
        for collection in entry.collections:
            self.collection_index[collection].append(entry_id)
        
        # Status index
        self.status_index[entry.download_status].append(entry_id)
    
    def remove_entry(self, entry_id: str, entry: 'DatabaseEntry'):
        """Remove entry from indices."""
        # DOI index
        if entry.doi and entry.doi in self.doi_index:
            del self.doi_index[entry.doi]
        
        # Title index
        if entry.title:
            normalized_title = self._normalize_title(entry.title)
            if entry_id in self.title_index[normalized_title]:
                self.title_index[normalized_title].remove(entry_id)
        
        # Author index
        for author in entry.authors:
            normalized_author = self._normalize_author(author)
            if entry_id in self.author_index[normalized_author]:
                self.author_index[normalized_author].remove(entry_id)
        
        # Year index
        if entry.year and entry_id in self.year_index[entry.year]:
            self.year_index[entry.year].remove(entry_id)
        
        # Journal index
        if entry.journal:
            normalized_journal = entry.journal.lower()
            if entry_id in self.journal_index[normalized_journal]:
                self.journal_index[normalized_journal].remove(entry_id)
        
        # Tag index
        for tag in entry.tags:
            if entry_id in self.tag_index[tag.lower()]:
                self.tag_index[tag.lower()].remove(entry_id)
        
        # Collection index
        for collection in entry.collections:
            if entry_id in self.collection_index[collection]:
                self.collection_index[collection].remove(entry_id)
        
        # Status index
        if entry_id in self.status_index[entry.download_status]:
            self.status_index[entry.download_status].remove(entry_id)
    
    def find_by_doi(self, doi: str) -> Optional[str]:
        """Find entry by DOI."""
        return self.doi_index.get(doi)
    
    def find_by_title(self, title: str, fuzzy: bool = True) -> List[str]:
        """Find entries by title.
        
        Args:
            title: Title to search for
            fuzzy: Use fuzzy matching
            
        Returns:
            List of matching entry IDs
        """
        if fuzzy:
            normalized_title = self._normalize_title(title)
            
            # Exact match
            if normalized_title in self.title_index:
                return list(self.title_index[normalized_title])
            
            # Fuzzy match - find titles containing all words
            title_words = set(normalized_title.split())
            matches = []
            
            for indexed_title, entry_ids in self.title_index.items():
                indexed_words = set(indexed_title.split())
                if title_words.issubset(indexed_words):
                    matches.extend(entry_ids)
            
            return list(set(matches))  # Remove duplicates
        else:
            # Exact match only
            return list(self.title_index.get(title, []))
    
    def find_by_author(self, author: str) -> List[str]:
        """Find entries by author."""
        normalized_author = self._normalize_author(author)
        
        # Exact match
        matches = list(self.author_index.get(normalized_author, []))
        
        # Partial match (last name only)
        if not matches and " " in author:
            last_name = author.split()[-1].lower()
            for indexed_author, entry_ids in self.author_index.items():
                if last_name in indexed_author:
                    matches.extend(entry_ids)
        
        return list(set(matches))
    
    def find_by_year(self, year: int) -> List[str]:
        """Find entries by year."""
        return list(self.year_index.get(year, []))
    
    def find_by_journal(self, journal: str) -> List[str]:
        """Find entries by journal."""
        return list(self.journal_index.get(journal.lower(), []))
    
    def find_by_tag(self, tag: str) -> List[str]:
        """Find entries by tag."""
        return list(self.tag_index.get(tag.lower(), []))
    
    def find_by_collection(self, collection: str) -> List[str]:
        """Find entries by collection."""
        return list(self.collection_index.get(collection, []))
    
    def find_by_status(self, status: str) -> List[str]:
        """Find entries by download status."""
        return list(self.status_index.get(status, []))
    
    def search(self, query: Dict[str, Any]) -> Set[str]:
        """Search with multiple criteria.
        
        Args:
            query: Dictionary of search criteria
            
        Returns:
            Set of matching entry IDs
        """
        results = None
        
        # Search by each criterion
        if "doi" in query:
            doi_result = self.find_by_doi(query["doi"])
            if doi_result:
                results = {doi_result}
            else:
                return set()
        
        if "title" in query:
            title_results = set(self.find_by_title(query["title"]))
            results = title_results if results is None else results.intersection(title_results)
        
        if "author" in query:
            author_results = set(self.find_by_author(query["author"]))
            results = author_results if results is None else results.intersection(author_results)
        
        if "year" in query:
            year_results = set(self.find_by_year(query["year"]))
            results = year_results if results is None else results.intersection(year_results)
        
        if "journal" in query:
            journal_results = set(self.find_by_journal(query["journal"]))
            results = journal_results if results is None else results.intersection(journal_results)
        
        if "tag" in query:
            tag_results = set(self.find_by_tag(query["tag"]))
            results = tag_results if results is None else results.intersection(tag_results)
        
        if "collection" in query:
            collection_results = set(self.find_by_collection(query["collection"]))
            results = collection_results if results is None else results.intersection(collection_results)
        
        if "status" in query:
            status_results = set(self.find_by_status(query["status"]))
            results = status_results if results is None else results.intersection(status_results)
        
        return results or set()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_dois": len(self.doi_index),
            "unique_titles": len(self.title_index),
            "unique_authors": len(self.author_index),
            "years": sorted(self.year_index.keys()),
            "journals": len(self.journal_index),
            "tags": sorted(self.tag_index.keys()),
            "collections": sorted(self.collection_index.keys()),
            "status_counts": {
                status: len(entries) for status, entries in self.status_index.items()
            }
        }
    
    def save_indices(self):
        """Save indices to disk."""
        try:
            # Save each index
            indices = {
                "doi": self.doi_index,
                "title": dict(self.title_index),
                "author": dict(self.author_index),
                "year": {str(k): v for k, v in self.year_index.items()},
                "journal": dict(self.journal_index),
                "tag": dict(self.tag_index),
                "collection": dict(self.collection_index),
                "status": dict(self.status_index),
            }
            
            for name, index in indices.items():
                index_file = self.index_dir / f"{name}_index.json"
                with open(index_file, 'w') as f:
                    json.dump(index, f, indent=2)
            
            # Save metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "stats": self.get_stats()
            }
            
            with open(self.index_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
                
            logger.debug("Saved database indices")
            
        except Exception as e:
            logger.error(f"Error saving indices: {e}")
    
    def _load_indices(self):
        """Load indices from disk."""
        try:
            # Load DOI index
            doi_file = self.index_dir / "doi_index.json"
            if doi_file.exists():
                with open(doi_file) as f:
                    self.doi_index = json.load(f)
            
            # Load title index
            title_file = self.index_dir / "title_index.json"
            if title_file.exists():
                with open(title_file) as f:
                    self.title_index = defaultdict(list, json.load(f))
            
            # Load author index
            author_file = self.index_dir / "author_index.json"
            if author_file.exists():
                with open(author_file) as f:
                    self.author_index = defaultdict(list, json.load(f))
            
            # Load year index
            year_file = self.index_dir / "year_index.json"
            if year_file.exists():
                with open(year_file) as f:
                    year_data = json.load(f)
                    self.year_index = defaultdict(list, {int(k): v for k, v in year_data.items()})
            
            # Load journal index
            journal_file = self.index_dir / "journal_index.json"
            if journal_file.exists():
                with open(journal_file) as f:
                    self.journal_index = defaultdict(list, json.load(f))
            
            # Load tag index
            tag_file = self.index_dir / "tag_index.json"
            if tag_file.exists():
                with open(tag_file) as f:
                    self.tag_index = defaultdict(list, json.load(f))
            
            # Load collection index
            collection_file = self.index_dir / "collection_index.json"
            if collection_file.exists():
                with open(collection_file) as f:
                    self.collection_index = defaultdict(list, json.load(f))
            
            # Load status index
            status_file = self.index_dir / "status_index.json"
            if status_file.exists():
                with open(status_file) as f:
                    self.status_index = defaultdict(list, json.load(f))
            
            logger.debug("Loaded database indices")
            
        except Exception as e:
            logger.warning(f"Could not load indices: {e}")


# EOF