#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/lookup/_LookupIndex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/lookup/_LookupIndex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Lightweight lookup index for DOI to storage key mapping.

Provides fast, concurrent-friendly lookups without database dependency.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from contextlib import contextmanager

from scitex import logging

logger = logging.getLogger(__name__)


class LookupIndex:
    """Fast lookup index for paper identifiers.
    
    Maintains bidirectional mappings:
    - DOI -> storage_key
    - storage_key -> metadata
    - title_hash -> storage_key (for deduplication)
    
    Uses both JSON files (for simple concurrent reads) and 
    SQLite (for complex queries).
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize lookup index.
        
        Args:
            base_dir: Base directory (default: $SCITEX_DIR/scholar)
        """
        if base_dir is None:
            scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
            base_dir = scitex_dir / "scholar"
            
        self.base_dir = Path(base_dir)
        self.lookup_dir = self.base_dir / "lookup"
        self.lookup_dir.mkdir(parents=True, exist_ok=True)
        
        # File-based indices for concurrent access
        self.doi_index_path = self.lookup_dir / "doi_to_key.json"
        self.key_index_path = self.lookup_dir / "key_to_metadata.json"
        self.title_index_path = self.lookup_dir / "title_to_key.json"
        
        # SQLite for complex queries
        self.db_path = self.lookup_dir / "lookup.sqlite"
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite lookup database."""
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Main lookup table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lookups (
                    storage_key TEXT PRIMARY KEY,
                    doi TEXT,
                    title TEXT,
                    title_hash TEXT,
                    first_author TEXT,
                    year INTEGER,
                    has_pdf BOOLEAN DEFAULT 0,
                    pdf_size INTEGER,
                    pdf_filename TEXT,
                    pdf_original_filename TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(doi),
                    UNIQUE(title_hash)
                )
            """)
            
            # Indexes for fast lookup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doi ON lookups(doi)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title_hash ON lookups(title_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_author_year ON lookups(first_author, year)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_has_pdf ON lookups(has_pdf)")
            
            conn.commit()
            
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def add_entry(self, storage_key: str, doi: Optional[str] = None,
                  title: Optional[str] = None, authors: Optional[List[str]] = None,
                  year: Optional[int] = None, has_pdf: bool = False,
                  pdf_size: Optional[int] = None) -> bool:
        """Add or update lookup entry.
        
        Args:
            storage_key: 8-character storage key
            doi: DOI if available
            title: Paper title
            authors: Author list
            year: Publication year
            has_pdf: Whether PDF exists
            pdf_size: PDF file size in bytes
            
        Returns:
            Success status
        """
        try:
            # Calculate title hash for deduplication
            title_hash = None
            if title:
                import hashlib
                title_normalized = title.lower().strip()
                title_hash = hashlib.md5(title_normalized.encode()).hexdigest()
                
            # Extract first author
            first_author = None
            if authors and len(authors) > 0:
                first_author = authors[0].split(",")[0].strip().lower()
                
            # Update SQLite
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO lookups 
                    (storage_key, doi, title, title_hash, first_author, year, has_pdf, pdf_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (storage_key, doi, title, title_hash, first_author, year, has_pdf, pdf_size))
                conn.commit()
                
            # Update JSON indices for fast concurrent access
            self._update_json_indices()
            
            logger.info(f"Added lookup entry: {storage_key} -> {doi or title[:30]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lookup entry: {e}")
            return False
            
    def _update_json_indices(self):
        """Update JSON index files from database."""
        with self._get_connection() as conn:
            # DOI to key mapping
            cursor = conn.execute("SELECT doi, storage_key FROM lookups WHERE doi IS NOT NULL")
            doi_map = {row["doi"]: row["storage_key"] for row in cursor}
            
            with open(self.doi_index_path, 'w') as f:
                json.dump(doi_map, f, indent=2)
                
            # Key to metadata mapping
            cursor = conn.execute("""
                SELECT storage_key, doi, title, first_author, year, has_pdf 
                FROM lookups
            """)
            key_map = {}
            for row in cursor:
                key_map[row["storage_key"]] = {
                    "doi": row["doi"],
                    "title": row["title"],
                    "first_author": row["first_author"],
                    "year": row["year"],
                    "has_pdf": bool(row["has_pdf"])
                }
                
            with open(self.key_index_path, 'w') as f:
                json.dump(key_map, f, indent=2)
                
            # Title hash to key mapping
            cursor = conn.execute("SELECT title_hash, storage_key FROM lookups WHERE title_hash IS NOT NULL")
            title_map = {row["title_hash"]: row["storage_key"] for row in cursor}
            
            with open(self.title_index_path, 'w') as f:
                json.dump(title_map, f, indent=2)
                
    def lookup_by_doi(self, doi: str) -> Optional[str]:
        """Fast lookup by DOI.
        
        Args:
            doi: DOI to lookup
            
        Returns:
            Storage key if found
        """
        # Try JSON first (fastest for concurrent access)
        if self.doi_index_path.exists():
            with open(self.doi_index_path, 'r') as f:
                doi_map = json.load(f)
                return doi_map.get(doi)
                
        # Fallback to database
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT storage_key FROM lookups WHERE doi = ?", (doi,))
            row = cursor.fetchone()
            return row["storage_key"] if row else None
            
    def lookup_by_title(self, title: str) -> Optional[str]:
        """Lookup by title (using hash for exact match).
        
        Args:
            title: Paper title
            
        Returns:
            Storage key if found
        """
        import hashlib
        title_hash = hashlib.md5(title.lower().strip().encode()).hexdigest()
        
        # Try JSON first
        if self.title_index_path.exists():
            with open(self.title_index_path, 'r') as f:
                title_map = json.load(f)
                return title_map.get(title_hash)
                
        # Fallback to database
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT storage_key FROM lookups WHERE title_hash = ?", (title_hash,))
            row = cursor.fetchone()
            return row["storage_key"] if row else None
            
    def lookup_by_key(self, storage_key: str) -> Optional[Dict]:
        """Get metadata by storage key.
        
        Args:
            storage_key: 8-character storage key
            
        Returns:
            Metadata dict if found
        """
        # Try JSON first
        if self.key_index_path.exists():
            with open(self.key_index_path, 'r') as f:
                key_map = json.load(f)
                return key_map.get(storage_key)
                
        # Fallback to database
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT doi, title, first_author, year, has_pdf 
                FROM lookups WHERE storage_key = ?
            """, (storage_key,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    def find_duplicates(self, title: str, authors: Optional[List[str]] = None,
                       year: Optional[int] = None) -> List[Tuple[str, float]]:
        """Find potential duplicate papers.
        
        Args:
            title: Paper title
            authors: Author list
            year: Publication year
            
        Returns:
            List of (storage_key, similarity_score) tuples
        """
        candidates = []
        
        # First try exact title match
        exact_key = self.lookup_by_title(title)
        if exact_key:
            candidates.append((exact_key, 1.0))
            
        # Then try fuzzy matching with database
        with self._get_connection() as conn:
            # Build query based on available info
            conditions = []
            params = []
            
            if authors and len(authors) > 0:
                first_author = authors[0].split(",")[0].strip().lower()
                conditions.append("first_author LIKE ?")
                params.append(f"%{first_author}%")
                
            if year:
                conditions.append("(year = ? OR year = ? OR year = ?)")
                params.extend([year, year-1, year+1])  # Allow 1 year difference
                
            if conditions:
                query = f"SELECT storage_key, title FROM lookups WHERE {' AND '.join(conditions)}"
                cursor = conn.execute(query, params)
                
                # Calculate similarity scores
                from difflib import SequenceMatcher
                for row in cursor:
                    if row["storage_key"] not in [c[0] for c in candidates]:
                        similarity = SequenceMatcher(None, title.lower(), row["title"].lower()).ratio()
                        if similarity > 0.8:  # 80% threshold
                            candidates.append((row["storage_key"], similarity))
                            
        # Sort by similarity score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
        
    def get_papers_without_pdf(self) -> List[str]:
        """Get storage keys for papers without PDFs."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT storage_key FROM lookups WHERE has_pdf = 0")
            return [row["storage_key"] for row in cursor]
            
    def get_papers_without_doi(self) -> List[str]:
        """Get storage keys for papers without DOIs."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT storage_key FROM lookups WHERE doi IS NULL")
            return [row["storage_key"] for row in cursor]
            
    def mark_pdf_download(self, storage_key: str, pdf_size: int,
                          pdf_filename: Optional[str] = None,
                          original_filename: Optional[str] = None) -> bool:
        """Mark that PDF has been download.
        
        Args:
            storage_key: Storage key
            pdf_size: PDF file size in bytes
            pdf_filename: Actual filename stored
            original_filename: Original filename from journal
            
        Returns:
            Success status
        """
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE lookups 
                    SET has_pdf = 1, pdf_size = ?, pdf_filename = ?, 
                        pdf_original_filename = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE storage_key = ?
                """, (pdf_size, pdf_filename, original_filename, storage_key))
                conn.commit()
                
            # Update JSON indices
            self._update_json_indices()
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark PDF download: {e}")
            return False
            
    def get_statistics(self) -> Dict:
        """Get lookup index statistics."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    SUM(CASE WHEN doi IS NOT NULL THEN 1 ELSE 0 END) as with_doi,
                    SUM(CASE WHEN has_pdf THEN 1 ELSE 0 END) as with_pdf,
                    SUM(pdf_size) as total_pdf_size
                FROM lookups
            """)
            stats = dict(cursor.fetchone())
            
            # Add file sizes
            stats["index_sizes"] = {
                "doi_index": self.doi_index_path.stat().st_size if self.doi_index_path.exists() else 0,
                "key_index": self.key_index_path.stat().st_size if self.key_index_path.exists() else 0,
                "title_index": self.title_index_path.stat().st_size if self.title_index_path.exists() else 0,
                "database": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
            
            return stats


def get_default_lookup() -> LookupIndex:
    """Get default lookup index instance."""
    return LookupIndex()


if __name__ == "__main__":
    print("SciTeX Scholar Lookup Index")
    print("=" * 60)
    
    # Example usage
    lookup = LookupIndex()
    
    # Add entry
    lookup.add_entry(
        storage_key="ABCD1234",
        doi="10.1234/example",
        title="Example Paper Title",
        authors=["Smith, John", "Doe, Jane"],
        year=2023,
        has_pdf=False
    )
    
    # Lookup by DOI
    key = lookup.lookup_by_doi("10.1234/example")
    print(f"DOI lookup: {key}")
    
    # Find papers without PDFs
    no_pdf = lookup.get_papers_without_pdf()
    print(f"Papers without PDFs: {len(no_pdf)}")
    
    # Get statistics
    stats = lookup.get_statistics()
    print(f"Statistics: {stats}")

# EOF