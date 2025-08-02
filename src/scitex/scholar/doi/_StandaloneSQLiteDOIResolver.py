#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 13:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/_StandaloneSQLiteDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/_StandaloneSQLiteDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Standalone SQLite DOI resolver with PDF storage.

A simple, focused implementation for scholar module with:
- Fixed schema optimized for DOI resolution
- WAL mode for concurrent access in HPC
- PDF storage as compressed BLOBs
- Full-text search capabilities
- Clean API focused on scholar workflow
"""

import gzip
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scitex import logging
from scitex.io import load, save

from ._DOIResolver import DOIResolver
from ..utils._progress_display import ProgressDisplay

logger = logging.getLogger(__name__)


class StandaloneSQLiteDOIResolver:
    """Lightweight SQLite-based DOI resolver for scholar module.
    
    Simple, focused implementation with:
    - Fixed schema for papers and DOIs
    - WAL mode for HPC environments
    - PDF storage (filesystem with DB references or BLOBs)
    - Full-text search capabilities
    - Progress tracking and resumability
    """
    
    def __init__(self, db_path: Optional[Path] = None, 
                 pdf_dir: Optional[Path] = None,
                 store_pdfs_in_db: bool = False):
        """Initialize standalone DOI resolver.
        
        Args:
            db_path: Database path (default: ~/.scitex/scholar/doi_resolver.db)
            pdf_dir: Directory for PDF storage (default: ~/.scitex/scholar/pdfs)
            store_pdfs_in_db: Store PDFs as BLOBs vs filesystem (default: False)
        """
        # Set default paths
        base_dir = Path.home() / ".scitex" / "scholar"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        if db_path is None:
            db_path = base_dir / "doi_resolver.db"
        if pdf_dir is None:
            pdf_dir = base_dir / "pdfs"
            
        self.db_path = Path(db_path)
        self.pdf_dir = Path(pdf_dir)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.store_pdfs_in_db = store_pdfs_in_db
        
        self.doi_resolver = DOIResolver()
        self._init_database()
        
    def _init_database(self):
        """Initialize database with fixed scholar schema including PDF storage."""
        with self._get_connection() as conn:
            # Enable WAL mode for concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=30000000000")
            
            # Papers table with PDF reference
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    title_norm TEXT NOT NULL,
                    year INTEGER,
                    authors TEXT,  -- JSON array
                    journal TEXT,
                    doi TEXT,
                    doi_source TEXT,
                    resolved_at TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    error TEXT,
                    pdf_hash TEXT,  -- SHA256 hash of PDF
                    pdf_source TEXT,  -- Where PDF came from
                    pdf_downloaded_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title_norm, year)
                )
            """)
            
            # PDF storage table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdfs (
                    hash TEXT PRIMARY KEY,  -- SHA256 hash as primary key
                    content BLOB NOT NULL,  -- Compressed PDF content
                    size_original INTEGER,  -- Original size in bytes
                    size_compressed INTEGER,  -- Compressed size
                    compression_ratio REAL,  -- Compression ratio
                    filename TEXT,  -- Original filename
                    mime_type TEXT DEFAULT 'application/pdf',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Full-text search table for PDF content
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdf_text (
                    pdf_hash TEXT PRIMARY KEY,
                    extracted_text TEXT,  -- Extracted text for search
                    page_count INTEGER,
                    extraction_method TEXT,  -- Method used (pdfplumber, pypdf2, etc.)
                    extracted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pdf_hash) REFERENCES pdfs(hash)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY,
                    paper_id INTEGER,
                    source TEXT,
                    success BOOLEAN,
                    doi TEXT,
                    error TEXT,
                    response_ms REAL,
                    attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paper_id) REFERENCES papers(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY,
                    started_at TEXT,
                    completed_at TEXT,
                    bibtex_path TEXT,
                    total INTEGER DEFAULT 0,
                    resolved INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doi ON papers(doi)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON papers(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON papers(title_norm)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pdf_hash ON papers(pdf_hash)")
            
            # Enable full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS pdf_search 
                USING fts5(pdf_hash, title, extracted_text)
            """)
            
            conn.commit()
            
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper settings."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def resolve_from_bibtex(self, 
                          bibtex_path: Path,
                          sources: Optional[List[str]] = None,
                          update_bibtex: bool = False,
                          update_interval: int = 10) -> Dict[str, str]:
        """Resolve DOIs from BibTeX file.
        
        Args:
            bibtex_path: Path to BibTeX file
            sources: DOI sources to use
            update_bibtex: Update BibTeX file incrementally
            update_interval: Papers between BibTeX updates
            
        Returns:
            Dict mapping titles to DOIs
        """
        start_time = time.time()
        
        # Load BibTeX
        logger.info(f"Loading BibTeX file: {bibtex_path}")
        try:
            entries = load(str(bibtex_path))
        except Exception as e:
            logger.error(f"Failed to load BibTeX: {e}")
            return {}
            
        # Start session
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (started_at, bibtex_path, total) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), str(bibtex_path), len(entries))
            )
            session_id = cursor.lastrowid
            conn.commit()
            
        # Process papers
        papers = []
        results = {}
        
        for entry in entries:
            fields = entry.get("fields", {})
            title = fields.get("title", "").strip()
            if not title:
                continue
                
            # Extract metadata
            year = None
            if "year" in fields:
                try:
                    year = int(fields["year"])
                except:
                    pass
                    
            authors = [a.strip() for a in fields.get("author", "").split(" and ") if a.strip()]
            journal = fields.get("journal", "")
            
            # Check if already processed
            paper_id, existing_doi, status = self._get_or_create_paper(
                title, year, authors, journal
            )
            
            if existing_doi:
                results[title] = existing_doi
                continue
                
            if status == "failed" and self._get_retry_count(paper_id) >= 3:
                logger.debug(f"Skipping after failures: {title[:50]}...")
                continue
                
            papers.append({
                "id": paper_id,
                "title": title,
                "year": year,
                "authors": authors
            })
            
        # Resolve DOIs
        logger.info(f"Resolving DOIs for {len(papers)} papers...")
        progress = ProgressDisplay(total=len(papers), description="Resolving DOIs")
        
        resolved_count = 0
        failed_count = 0
        
        for i, paper in enumerate(papers):
            logger.info(f"[{i+1}/{len(papers)}] {paper['title'][:60]}...")
            
            try:
                # Time the resolution
                resolve_start = time.time()
                doi = self.doi_resolver.title_to_doi(
                    title=paper["title"],
                    year=paper["year"],
                    authors=paper["authors"],
                    sources=sources
                )
                response_ms = (time.time() - resolve_start) * 1000
                
                # Update database
                with self._get_connection() as conn:
                    if doi:
                        conn.execute("""
                            UPDATE papers 
                            SET doi = ?, doi_source = 'scitex', 
                                resolved_at = ?, status = 'resolved'
                            WHERE id = ?
                        """, (doi, datetime.now().isoformat(), paper["id"]))
                        
                        conn.execute("""
                            INSERT INTO attempts (paper_id, source, success, doi, response_ms)
                            VALUES (?, 'combined', 1, ?, ?)
                        """, (paper["id"], doi, response_ms))
                        
                        results[paper["title"]] = doi
                        resolved_count += 1
                        logger.success(f"  ✓ Found: {doi}")
                        progress.update(success=True)
                    else:
                        conn.execute("""
                            UPDATE papers 
                            SET retry_count = retry_count + 1,
                                status = CASE 
                                    WHEN retry_count >= 2 THEN 'failed' 
                                    ELSE status 
                                END
                            WHERE id = ?
                        """, (paper["id"],))
                        
                        conn.execute("""
                            INSERT INTO attempts (paper_id, source, success, response_ms)
                            VALUES (?, 'combined', 0, ?)
                        """, (paper["id"], response_ms))
                        
                        failed_count += 1
                        logger.warning(f"  ✗ No DOI found")
                        progress.update(success=False)
                        
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                with self._get_connection() as conn:
                    conn.execute(
                        "UPDATE papers SET status = 'error', error = ? WHERE id = ?",
                        (str(e), paper["id"])
                    )
                    conn.commit()
                failed_count += 1
                progress.update(success=False)
                
            # Incremental BibTeX update
            if update_bibtex and resolved_count > 0 and resolved_count % update_interval == 0:
                self._update_bibtex(bibtex_path, results)
                logger.info(f"Updated BibTeX ({resolved_count} DOIs)")
                
        progress.finish()
        
        # Complete session
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE sessions 
                SET completed_at = ?, resolved = ?, failed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), resolved_count, failed_count, session_id))
            conn.commit()
            
        # Final BibTeX update
        if update_bibtex and resolved_count > 0:
            self._update_bibtex(bibtex_path, results)
            logger.success(f"Final update: {resolved_count} DOIs added")
            
        # Show summary
        duration = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("DOI Resolution Summary")
        logger.info("=" * 60)
        logger.info(f"Total papers: {len(entries)}")
        logger.info(f"Processed: {len(papers)}")
        logger.info(f"Resolved: {resolved_count} ({resolved_count/len(papers)*100:.1f}%)")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Duration: {duration:.1f}s")
        logger.info("=" * 60)
        
        return results
        
    def _get_or_create_paper(self, title: str, year: Optional[int],
                           authors: List[str], journal: str) -> Tuple[int, Optional[str], str]:
        """Get existing paper or create new."""
        title_norm = title.lower().strip()
        
        with self._get_connection() as conn:
            # Check existing
            cursor = conn.execute(
                "SELECT id, doi, status FROM papers WHERE title_norm = ? AND year IS ?",
                (title_norm, year)
            )
            row = cursor.fetchone()
            
            if row:
                return row["id"], row["doi"], row["status"]
                
            # Create new
            cursor = conn.execute("""
                INSERT INTO papers (title, title_norm, year, authors, journal)
                VALUES (?, ?, ?, ?, ?)
            """, (title, title_norm, year, json.dumps(authors), journal))
            
            conn.commit()
            return cursor.lastrowid, None, "pending"
            
    def _get_retry_count(self, paper_id: int) -> int:
        """Get retry count for paper."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT retry_count FROM papers WHERE id = ?",
                (paper_id,)
            )
            row = cursor.fetchone()
            return row["retry_count"] if row else 0
            
    def _update_bibtex(self, bibtex_path: Path, doi_mapping: Dict[str, str]):
        """Update BibTeX file with DOIs."""
        # Backup
        backup_path = bibtex_path.with_suffix('.bib.bak')
        import shutil
        shutil.copy2(bibtex_path, backup_path)
        
        # Update entries
        entries = load(str(bibtex_path))
        updated = 0
        
        for entry in entries:
            fields = entry.get("fields", {})
            title = fields.get("title", "").strip()
            
            if title in doi_mapping and not fields.get("doi"):
                fields["doi"] = doi_mapping[title]
                fields["doi_source"] = "scitex_resolver"
                fields["doi_resolved_at"] = datetime.now().isoformat()
                updated += 1
                
        # Save atomically
        if updated > 0:
            temp_path = bibtex_path.with_suffix('.bib.tmp')
            save(entries, str(temp_path))
            temp_path.replace(bibtex_path)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get resolution statistics."""
        with self._get_connection() as conn:
            # Paper stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN doi IS NOT NULL THEN 1 ELSE 0 END) as with_doi,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM papers
            """)
            paper_stats = dict(cursor.fetchone())
            
            # Source stats
            cursor = conn.execute("""
                SELECT doi_source, COUNT(*) as count 
                FROM papers 
                WHERE doi IS NOT NULL 
                GROUP BY doi_source
            """)
            source_stats = {row["doi_source"]: row["count"] for row in cursor}
            
            # Performance stats
            cursor = conn.execute("""
                SELECT 
                    source,
                    COUNT(*) as attempts,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                    AVG(response_ms) as avg_ms
                FROM attempts
                GROUP BY source
            """)
            perf_stats = [dict(row) for row in cursor]
            
            return {
                "papers": paper_stats,
                "sources": source_stats,
                "performance": perf_stats
            }
            
    def store_pdf(self, paper_id: int, pdf_path: Path, 
                  source: str = "manual") -> Optional[str]:
        """Store PDF file either in filesystem or database.
        
        Args:
            paper_id: ID of paper to attach PDF to
            pdf_path: Path to PDF file
            source: Source of PDF (e.g., 'manual', 'scihub', 'publisher')
            
        Returns:
            PDF hash if successful, None otherwise
        """
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        try:
            # Read PDF content
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                
            # Calculate hash
            pdf_hash = hashlib.sha256(pdf_content).hexdigest()
            
            # Get paper info for filename
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT title, year, authors FROM papers WHERE id = ?",
                    (paper_id,)
                )
                paper = cursor.fetchone()
                
                if not paper:
                    logger.error(f"Paper {paper_id} not found")
                    return None
                    
                # Generate filename: FIRSTAUTHOR-YEAR-JOURNAL.pdf
                authors = json.loads(paper["authors"]) if paper["authors"] else []
                first_author = authors[0].split(",")[0].strip() if authors else "Unknown"
                year = paper["year"] or "XXXX"
                
                # Clean filename
                safe_author = "".join(c for c in first_author if c.isalnum() or c in "- ")
                safe_filename = f"{safe_author}-{year}-{pdf_hash[:8]}.pdf"
                
            if self.store_pdfs_in_db:
                # Store in database as BLOB
                compressed_content = gzip.compress(pdf_content, compresslevel=9)
                size_original = len(pdf_content)
                size_compressed = len(compressed_content)
                compression_ratio = size_compressed / size_original
                
                with self._get_connection() as conn:
                    # Check if PDF already exists
                    cursor = conn.execute(
                        "SELECT hash FROM pdfs WHERE hash = ?",
                        (pdf_hash,)
                    )
                    
                    if not cursor.fetchone():
                        # Store new PDF
                        conn.execute("""
                            INSERT INTO pdfs 
                            (hash, content, size_original, size_compressed, 
                             compression_ratio, filename)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (pdf_hash, compressed_content, size_original,
                              size_compressed, compression_ratio, safe_filename))
                        
                    # Link PDF to paper
                    conn.execute("""
                        UPDATE papers 
                        SET pdf_hash = ?, pdf_source = ?, pdf_downloaded_at = ?
                        WHERE id = ?
                    """, (pdf_hash, source, datetime.now().isoformat(), paper_id))
                    
                    conn.commit()
                    
                logger.info(f"Stored PDF in DB: {safe_filename} "
                           f"({size_original/1024/1024:.1f}MB -> "
                           f"{size_compressed/1024/1024:.1f}MB)")
                           
            else:
                # Store in filesystem
                pdf_file_path = self.pdf_dir / safe_filename
                
                # Copy PDF to storage directory if not already there
                if not pdf_file_path.exists():
                    import shutil
                    shutil.copy2(pdf_path, pdf_file_path)
                    
                # Store reference in database
                with self._get_connection() as conn:
                    # Store PDF metadata
                    cursor = conn.execute(
                        "SELECT hash FROM pdfs WHERE hash = ?",
                        (pdf_hash,)
                    )
                    
                    if not cursor.fetchone():
                        conn.execute("""
                            INSERT INTO pdfs 
                            (hash, content, size_original, size_compressed, 
                             compression_ratio, filename)
                            VALUES (?, NULL, ?, ?, 1.0, ?)
                        """, (pdf_hash, len(pdf_content), len(pdf_content), 
                              safe_filename))
                        
                    # Link PDF to paper
                    conn.execute("""
                        UPDATE papers 
                        SET pdf_hash = ?, pdf_source = ?, pdf_downloaded_at = ?
                        WHERE id = ?
                    """, (pdf_hash, source, datetime.now().isoformat(), paper_id))
                    
                    conn.commit()
                    
                logger.info(f"Stored PDF in filesystem: {pdf_file_path}")
                
            return pdf_hash
            
        except Exception as e:
            logger.error(f"Failed to store PDF: {e}")
            return None
            
    def get_pdf(self, paper_id: Optional[int] = None, 
                pdf_hash: Optional[str] = None,
                output_path: Optional[Path] = None) -> Optional[bytes]:
        """Retrieve PDF from database.
        
        Args:
            paper_id: Paper ID to get PDF for
            pdf_hash: Direct PDF hash
            output_path: Path to save PDF to (optional)
            
        Returns:
            Decompressed PDF content as bytes, or None if not found
        """
        with self._get_connection() as conn:
            if paper_id:
                # Get hash from paper
                cursor = conn.execute(
                    "SELECT pdf_hash FROM papers WHERE id = ?",
                    (paper_id,)
                )
                row = cursor.fetchone()
                if not row or not row["pdf_hash"]:
                    return None
                pdf_hash = row["pdf_hash"]
                
            if not pdf_hash:
                return None
                
            # Get compressed content
            cursor = conn.execute(
                "SELECT content, filename FROM pdfs WHERE hash = ?",
                (pdf_hash,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Decompress
            pdf_content = gzip.decompress(row["content"])
            
            # Save to file if requested
            if output_path:
                output_path = Path(output_path)
                if output_path.is_dir():
                    output_path = output_path / row["filename"]
                    
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)
                    
                logger.info(f"Saved PDF to: {output_path}")
                
            return pdf_content
            
    def store_pdf_batch(self, pdf_mappings: List[Tuple[int, Path, str]]) -> int:
        """Store multiple PDFs in batch.
        
        Args:
            pdf_mappings: List of (paper_id, pdf_path, source) tuples
            
        Returns:
            Number of PDFs successfully stored
        """
        stored = 0
        
        for paper_id, pdf_path, source in pdf_mappings:
            if self.store_pdf(paper_id, pdf_path, source):
                stored += 1
                
        return stored
        
    def search_pdfs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search across PDF content.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching papers with snippets
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT p.id, p.title, p.doi, p.year, 
                       snippet(pdf_search, 2, '<mark>', '</mark>', '...', 50) as snippet
                FROM pdf_search ps
                JOIN papers p ON p.pdf_hash = ps.pdf_hash
                WHERE pdf_search MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            return [dict(row) for row in cursor]
            
    def get_pdf_statistics(self) -> Dict[str, Any]:
        """Get PDF storage statistics."""
        with self._get_connection() as conn:
            # Overall stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_pdfs,
                    SUM(size_original) as total_size_original,
                    SUM(size_compressed) as total_size_compressed,
                    AVG(compression_ratio) as avg_compression_ratio
                FROM pdfs
            """)
            pdf_stats = dict(cursor.fetchone())
            
            # Papers with PDFs
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_papers,
                    SUM(CASE WHEN pdf_hash IS NOT NULL THEN 1 ELSE 0 END) as with_pdf
                FROM papers
            """)
            paper_stats = dict(cursor.fetchone())
            
            # Source statistics
            cursor = conn.execute("""
                SELECT pdf_source, COUNT(*) as count
                FROM papers
                WHERE pdf_hash IS NOT NULL
                GROUP BY pdf_source
            """)
            source_stats = {row["pdf_source"]: row["count"] for row in cursor}
            
            return {
                "pdfs": pdf_stats,
                "papers": paper_stats,
                "sources": source_stats,
                "storage_saved_mb": (
                    (pdf_stats["total_size_original"] - pdf_stats["total_size_compressed"]) 
                    / 1024 / 1024
                ) if pdf_stats["total_size_original"] else 0
            }
            
    def export_to_json(self, output_path: Path):
        """Export all resolved DOIs to JSON."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT title, doi FROM papers WHERE doi IS NOT NULL"
            )
            results = {row["title"]: row["doi"] for row in cursor}
            
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Exported {len(results)} DOIs to {output_path}")


if __name__ == "__main__":
    print("Standalone SQLite DOI Resolver")
    print("=" * 60)
    print("\nMinimal, focused implementation:")
    print("- Fixed schema for scholar workflow")
    print("- WAL mode for HPC environments")
    print("- No complex inheritance")
    print("- Clean, simple API")
    
    print("\nExample:")
    print("""
    resolver = StandaloneSQLiteDOIResolver()
    results = resolver.resolve_from_bibtex(
        Path("papers.bib"),
        update_bibtex=True,
        update_interval=10
    )
    
    # Get statistics
    stats = resolver.get_statistics()
    print(f"Resolved: {stats['papers']['resolved']}")
    
    # Export results
    resolver.export_to_json(Path("dois.json"))
    """)

# EOF