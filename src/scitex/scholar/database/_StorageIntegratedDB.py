#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 15:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_StorageIntegratedDB.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_StorageIntegratedDB.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Database with fully integrated enhanced storage structure.

This implementation properly uses the enhanced storage manager for all operations.
"""

import json
import sqlite3
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scitex import logging
from ..storage import EnhancedStorageManager
from ..lookup import get_default_lookup

logger = logging.getLogger(__name__)


class StorageIntegratedDB:
    """Scholar database with full enhanced storage integration."""
    
    def __init__(self, library_name: str = "default"):
        """Initialize database with enhanced storage.
        
        Args:
            library_name: Library name
        """
        self.library_name = library_name
        
        # Base paths
        scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
        self.base_dir = scitex_dir / "scholar" / "library" / library_name
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Database path
        self.db_path = self.base_dir / "scholar.sqlite"
        
        # Initialize components
        self.storage = EnhancedStorageManager(self.base_dir)
        self.lookup = get_default_lookup()
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            # Enable WAL mode
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Papers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    storage_key TEXT UNIQUE NOT NULL,
                    doi TEXT,
                    title TEXT,
                    authors_json TEXT,
                    journal TEXT,
                    year INTEGER,
                    abstract TEXT,
                    url TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # PDF attachments table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdf_attachments (
                    id INTEGER PRIMARY KEY,
                    paper_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    original_filename TEXT,
                    pdf_url TEXT,
                    size_bytes INTEGER,
                    hash TEXT,
                    download_asynced_at TEXT,
                    FOREIGN KEY (paper_id) REFERENCES papers(id)
                )
            """)
            
            # Screenshots table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY,
                    paper_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    description TEXT,
                    captured_at TEXT,
                    FOREIGN KEY (paper_id) REFERENCES papers(id)
                )
            """)
            
            # Enrichment tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enrichment_status (
                    paper_id INTEGER PRIMARY KEY,
                    doi_resolved BOOLEAN DEFAULT 0,
                    metadata_enriched BOOLEAN DEFAULT 0,
                    pdf_download_asynced BOOLEAN DEFAULT 0,
                    last_attempt TEXT,
                    FOREIGN KEY (paper_id) REFERENCES papers(id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_storage_key ON papers(storage_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doi ON papers(doi)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON papers(year)")
            
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
            
    def add_paper(self, metadata: Dict[str, Any], storage_key: Optional[str] = None) -> int:
        """Add paper to database.
        
        Args:
            metadata: Paper metadata
            storage_key: Optional storage key (generated if not provided)
            
        Returns:
            Paper ID
        """
        # Generate storage key if needed
        if not storage_key:
            import random
            import string
            storage_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
        with self._get_connection() as conn:
            # Insert paper
            cursor = conn.execute("""
                INSERT INTO papers (storage_key, doi, title, authors_json, journal, year, abstract, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                storage_key,
                metadata.get("doi"),
                metadata.get("title"),
                json.dumps(metadata.get("authors", [])),
                metadata.get("journal"),
                metadata.get("year"),
                metadata.get("abstract"),
                metadata.get("url")
            ))
            paper_id = cursor.lastrowid
            
            # Add enrichment status
            conn.execute("""
                INSERT INTO enrichment_status (paper_id)
                VALUES (?)
            """, (paper_id,))
            
            conn.commit()
            
        # Update lookup index
        self.lookup.add_entry(
            storage_key=storage_key,
            doi=metadata.get("doi"),
            title=metadata.get("title"),
            authors=metadata.get("authors", []),
            year=metadata.get("year")
        )
        
        # Create storage directory structure
        storage_dir = self.storage.storage_dir / storage_key
        storage_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata_path = storage_dir / "metadata.json"
        metadata["storage_key"] = storage_key
        metadata["paper_id"] = paper_id
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Added paper {paper_id} with key {storage_key}")
        return paper_id
        
    def attach_pdf(self, paper_id: int, pdf_path: Path,
                  original_filename: Optional[str] = None,
                  pdf_url: Optional[str] = None) -> bool:
        """Attach PDF to paper using enhanced storage.
        
        Args:
            paper_id: Paper ID
            pdf_path: Path to PDF file
            original_filename: Original filename from journal
            pdf_url: URL where PDF was download_asynced
            
        Returns:
            Success status
        """
        # Get paper info
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM papers WHERE id = ?",
                (paper_id,)
            )
            paper = cursor.fetchone()
            
            if not paper:
                logger.error(f"Paper {paper_id} not found")
                return False
                
            # Get paper metadata for human-readable link
            metadata = {
                "storage_key": paper["storage_key"],
                "doi": paper["doi"],
                "title": paper["title"],
                "authors": json.loads(paper["authors_json"]),
                "journal": paper["journal"],
                "year": paper["year"]
            }
            
        # Store PDF using enhanced storage
        stored_path = self.storage.store_pdf(
            storage_key=paper["storage_key"],
            pdf_path=pdf_path,
            original_filename=original_filename,
            pdf_url=pdf_url,
            paper_metadata=metadata
        )
        
        # Get PDF info
        pdf_info = self.storage.get_pdf_info(paper["storage_key"])
        
        # Update database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO pdf_attachments 
                (paper_id, filename, original_filename, pdf_url, size_bytes, hash, download_asynced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_id,
                pdf_info["filename"],
                pdf_info.get("original_filename"),
                pdf_url,
                pdf_info["size_bytes"],
                pdf_info["pdf_hash"],
                datetime.now().isoformat()
            ))
            
            # Update enrichment status
            conn.execute("""
                UPDATE enrichment_status
                SET pdf_download_asynced = 1
                WHERE paper_id = ?
            """, (paper_id,))
            
            conn.commit()
            
        # Update lookup index
        self.lookup.mark_pdf_download_asynced(
            storage_key=paper["storage_key"],
            pdf_size=pdf_info["size_bytes"],
            pdf_filename=pdf_info["filename"],
            original_filename=original_filename
        )
        
        logger.info(f"Attached PDF to paper {paper_id}: {pdf_info['filename']}")
        return True
        
    def capture_screenshot(self, paper_id: int, screenshot_path: Path,
                          description: str = "download_async-attempt") -> bool:
        """Capture screenshot for paper.
        
        Args:
            paper_id: Paper ID
            screenshot_path: Path to screenshot
            description: Screenshot description
            
        Returns:
            Success status
        """
        # Get storage key
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT storage_key FROM papers WHERE id = ?",
                (paper_id,)
            )
            paper = cursor.fetchone()
            
            if not paper:
                logger.error(f"Paper {paper_id} not found")
                return False
                
        # Store screenshot
        stored_path = self.storage.store_screenshot(
            storage_key=paper["storage_key"],
            screenshot_path=screenshot_path,
            description=description
        )
        
        # Update database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO screenshots (paper_id, filename, description, captured_at)
                VALUES (?, ?, ?, ?)
            """, (
                paper_id,
                stored_path.name,
                description,
                datetime.now().isoformat()
            ))
            conn.commit()
            
        logger.info(f"Captured screenshot for paper {paper_id}: {description}")
        return True
        
    def get_paper_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Get paper by DOI."""
        # Use lookup index first
        storage_key = self.lookup.lookup_by_doi(doi)
        if not storage_key:
            return None
            
        return self.get_paper_by_key(storage_key)
        
    def get_paper_by_key(self, storage_key: str) -> Optional[Dict[str, Any]]:
        """Get paper by storage key."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT p.*, 
                       es.doi_resolved, es.metadata_enriched, es.pdf_download_asynced,
                       COUNT(DISTINCT pa.id) as pdf_count,
                       COUNT(DISTINCT s.id) as screenshot_count
                FROM papers p
                LEFT JOIN enrichment_status es ON p.id = es.paper_id
                LEFT JOIN pdf_attachments pa ON p.id = pa.paper_id
                LEFT JOIN screenshots s ON p.id = s.paper_id
                WHERE p.storage_key = ?
                GROUP BY p.id
            """, (storage_key,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            paper = dict(row)
            paper["authors"] = json.loads(paper["authors_json"])
            
            # Get PDFs
            cursor = conn.execute("""
                SELECT * FROM pdf_attachments
                WHERE paper_id = ?
                ORDER BY download_asynced_at DESC
            """, (paper["id"],))
            paper["pdfs"] = [dict(pdf) for pdf in cursor]
            
            # Get screenshots
            cursor = conn.execute("""
                SELECT * FROM screenshots
                WHERE paper_id = ?
                ORDER BY captured_at DESC
            """, (paper["id"],))
            paper["screenshots"] = [dict(s) for s in cursor]
            
            # Add storage paths
            paper["storage_path"] = str(self.storage.storage_dir / storage_key)
            paper["human_readable_path"] = None
            
            # Find human-readable link
            for link in self.storage.human_readable_dir.iterdir():
                if link.is_symlink() and link.resolve().name == storage_key:
                    paper["human_readable_path"] = str(link)
                    break
                    
            return paper
            
    def get_papers_needing_pdf(self) -> List[Dict[str, Any]]:
        """Get papers without PDFs."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT p.*
                FROM papers p
                LEFT JOIN enrichment_status es ON p.id = es.paper_id
                WHERE es.pdf_download_asynced = 0 OR es.pdf_download_asynced IS NULL
                ORDER BY p.created_at
            """)
            
            papers = []
            for row in cursor:
                paper = dict(row)
                paper["authors"] = json.loads(paper["authors_json"])
                papers.append(paper)
                
            return papers
            
    def migrate_from_zotero(self, zotero_storage_path: Path,
                           zotero_db_path: Optional[Path] = None) -> Dict[str, int]:
        """Migrate from existing Zotero library.
        
        Args:
            zotero_storage_path: Path to Zotero storage directory
            zotero_db_path: Optional path to zotero.sqlite
            
        Returns:
            Migration statistics
        """
        stats = {"papers": 0, "pdfs": 0, "errors": 0}
        
        logger.info(f"Starting Zotero migration from {zotero_storage_path}")
        
        # Process each storage directory
        for storage_dir in zotero_storage_path.iterdir():
            if not storage_dir.is_dir() or len(storage_dir.name) != 8:
                continue
                
            storage_key = storage_dir.name
            
            try:
                # Look for PDFs
                pdfs = list(storage_dir.glob("*.pdf"))
                if not pdfs:
                    continue
                    
                # Create paper entry (minimal metadata for now)
                metadata = {
                    "title": f"Imported from Zotero - {storage_key}",
                    "source": "zotero_import"
                }
                
                paper_id = self.add_paper(metadata, storage_key=storage_key)
                stats["papers"] += 1
                
                # Copy PDFs
                for pdf_path in pdfs:
                    # Copy directly to our storage (preserving filename)
                    dest_dir = self.storage.storage_dir / storage_key
                    dest_dir.mkdir(exist_ok=True)
                    
                    dest_path = dest_dir / pdf_path.name
                    shutil.copy2(pdf_path, dest_path)
                    
                    # Create metadata
                    with open(dest_dir / "storage_metadata.json", 'w') as f:
                        json.dump({
                            "storage_key": storage_key,
                            "filename": pdf_path.name,
                            "original_filename": pdf_path.name,
                            "size_bytes": pdf_path.stat().st_size,
                            "stored_at": datetime.now().isoformat(),
                            "source": "zotero_import"
                        }, f, indent=2)
                        
                    # Update database
                    self.attach_pdf(
                        paper_id=paper_id,
                        pdf_path=dest_path,
                        original_filename=pdf_path.name
                    )
                    stats["pdfs"] += 1
                    
                logger.info(f"Migrated {storage_key}: {len(pdfs)} PDFs")
                
            except Exception as e:
                logger.error(f"Error migrating {storage_key}: {e}")
                stats["errors"] += 1
                
        # If Zotero database provided, enrich metadata
        if zotero_db_path and zotero_db_path.exists():
            logger.info("Enriching from Zotero database...")
            self._enrich_from_zotero_db(zotero_db_path)
            
        logger.info(f"Migration complete: {stats}")
        return stats
        
    def _enrich_from_zotero_db(self, zotero_db_path: Path):
        """Enrich imported papers from Zotero database."""
        # This would parse Zotero's SQLite database and update our papers
        # with proper metadata (title, authors, DOI, etc.)
        pass
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get database and storage statistics."""
        with self._get_connection() as conn:
            # Paper stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    SUM(CASE WHEN doi IS NOT NULL THEN 1 ELSE 0 END) as with_doi,
                    COUNT(DISTINCT journal) as unique_journals
                FROM papers
            """)
            paper_stats = dict(cursor.fetchone())
            
            # PDF stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_pdfs,
                    SUM(size_bytes) as total_size,
                    COUNT(DISTINCT paper_id) as papers_with_pdf
                FROM pdf_attachments
            """)
            pdf_stats = dict(cursor.fetchone())
            
            # Screenshot stats
            cursor = conn.execute("SELECT COUNT(*) as total FROM screenshots")
            screenshot_count = cursor.fetchone()["total"]
            
        # Storage stats
        storage_stats = self.storage.get_storage_stats()
        
        return {
            "papers": paper_stats,
            "pdfs": pdf_stats,
            "screenshots": screenshot_count,
            "storage": storage_stats
        }


if __name__ == "__main__":
    print("Storage-Integrated Scholar Database")
    print("=" * 60)
    
    # Example usage
    db = StorageIntegratedDB()
    
    print("\nKey features:")
    print("- Uses enhanced storage for all PDFs")
    print("- Preserves original filenames")
    print("- Captures screenshots during download_asyncs")
    print("- Creates human-readable links")
    print("- Direct Zotero migration support")
    
    print("\nExample workflow:")
    print("""
    # Add paper
    paper_id = db.add_paper({
        "doi": "10.1038/nature12373",
        "title": "Quantum teleportation",
        "authors": ["Bennett, C.H.", "Brassard, G."],
        "journal": "Nature",
        "year": 2023
    })
    
    # Attach PDF with original filename
    db.attach_pdf(
        paper_id=paper_id,
        pdf_path=Path("download_asynced.pdf"),
        original_filename="nature12373.pdf",
        pdf_url="https://nature.com/..."
    )
    
    # Capture screenshot
    db.capture_screenshot(
        paper_id=paper_id,
        screenshot_path=Path("screenshot.png"),
        description="download_async-success"
    )
    
    # Migrate from Zotero
    stats = db.migrate_from_zotero(
        Path("~/Zotero/storage"),
        Path("~/Zotero/zotero.sqlite")
    )
    """)

# EOF