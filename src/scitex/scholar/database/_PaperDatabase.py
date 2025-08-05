#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_PaperDatabase.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_PaperDatabase.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Paper database for organizing research papers."""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import hashlib
from collections import defaultdict

from scitex import logging
from scitex.errors import ScholarError
from ._DatabaseEntry import DatabaseEntry
from ._DatabaseIndex import DatabaseIndex

logger = logging.getLogger(__name__)


class PaperDatabase:
    """Database for organizing and managing research papers.
    
    Features:
    - Store paper metadata and file locations
    - Organize PDFs by year/journal/author
    - Fast search by various fields
    - Import from BibTeX
    - Export to various formats
    - Track download_async and validation status
    """
    
    def __init__(self, database_dir: Optional[Union[str, Path]] = None):
        """Initialize paper database.
        
        Args:
            database_dir: Root directory for database
        """
        if database_dir is None:
            database_dir = Path.home() / ".scitex" / "scholar" / "database"
        
        self.database_dir = Path(database_dir)
        self.database_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.data_dir = self.database_dir / "data"
        self.pdfs_dir = self.database_dir / "pdfs"
        self.exports_dir = self.database_dir / "exports"
        
        for dir_path in [self.data_dir, self.pdfs_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Database files
        self.db_file = self.data_dir / "papers.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
        # Initialize
        self.entries: Dict[str, DatabaseEntry] = {}
        self.index = DatabaseIndex(self.database_dir / "indices")
        
        # Load existing database
        self._load_database()
    
    def _generate_entry_id(self, entry: DatabaseEntry) -> str:
        """Generate unique ID for entry."""
        # Use DOI if available
        if entry.doi:
            return f"doi_{entry.doi.replace('/', '_')}"
        
        # Otherwise use hash of title + authors
        content = f"{entry.title}:{':'.join(entry.authors)}"
        hash_id = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"hash_{hash_id}"
    
    def add_entry(self, entry: DatabaseEntry) -> str:
        """Add new entry to database.
        
        Args:
            entry: Database entry to add
            
        Returns:
            Entry ID
        """
        # Generate ID
        entry_id = self._generate_entry_id(entry)
        
        # Check for duplicates
        if entry_id in self.entries:
            logger.warning(f"Entry already exists: {entry_id}")
            return entry_id
        
        # Check for duplicate DOI
        if entry.doi and self.index.find_by_doi(entry.doi):
            existing_id = self.index.find_by_doi(entry.doi)
            logger.warning(f"DOI already exists: {entry.doi} -> {existing_id}")
            return existing_id
        
        # Add to database
        self.entries[entry_id] = entry
        self.index.add_entry(entry_id, entry)
        
        # Save
        self._save_database()
        
        logger.info(f"Added entry: {entry_id} - {entry.title[:50]}...")
        return entry_id
    
    def update_entry(self, entry_id: str, updates: Dict[str, Any]):
        """Update existing entry.
        
        Args:
            entry_id: Entry ID to update
            updates: Dictionary of field updates
        """
        if entry_id not in self.entries:
            raise ScholarError(f"Entry not found: {entry_id}")
        
        entry = self.entries[entry_id]
        
        # Remove from index
        self.index.remove_entry(entry_id, entry)
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(entry, field):
                setattr(entry, field, value)
        
        # Re-add to index
        self.index.add_entry(entry_id, entry)
        
        # Save
        self._save_database()
        
        logger.debug(f"Updated entry: {entry_id}")
    
    def get_entry(self, entry_id: str) -> Optional[DatabaseEntry]:
        """Get entry by ID."""
        return self.entries.get(entry_id)
    
    def remove_entry(self, entry_id: str, delete_pdf: bool = False):
        """Remove entry from database.
        
        Args:
            entry_id: Entry ID to remove
            delete_pdf: Whether to delete associated PDF
        """
        if entry_id not in self.entries:
            logger.warning(f"Entry not found: {entry_id}")
            return
        
        entry = self.entries[entry_id]
        
        # Remove from index
        self.index.remove_entry(entry_id, entry)
        
        # Delete PDF if requested
        if delete_pdf and entry.pdf_path:
            pdf_path = Path(entry.pdf_path)
            if pdf_path.exists():
                pdf_path.unlink()
                logger.info(f"Deleted PDF: {pdf_path}")
        
        # Remove from database
        del self.entries[entry_id]
        
        # Save
        self._save_database()
        
        logger.info(f"Removed entry: {entry_id}")
    
    def import_from_papers(self, papers: List['Paper'], update_existing: bool = True) -> List[str]:
        """Import from Paper objects.
        
        Args:
            papers: List of Paper objects
            update_existing: Update existing entries
            
        Returns:
            List of entry IDs
        """
        entry_ids = []
        
        for paper in papers:
            # Convert to database entry
            entry = DatabaseEntry.from_paper(paper)
            
            # Check if exists
            existing_id = None
            if entry.doi:
                existing_id = self.index.find_by_doi(entry.doi)
            
            if existing_id and update_existing:
                # Update existing
                updates = entry.to_dict()
                self.update_entry(existing_id, updates)
                entry_ids.append(existing_id)
            elif not existing_id:
                # Add new
                entry_id = self.add_entry(entry)
                entry_ids.append(entry_id)
            else:
                # Skip
                entry_ids.append(existing_id)
        
        logger.info(f"Imported {len(papers)} papers")
        return entry_ids
    
    def organize_pdf(self, entry_id: str, pdf_path: Union[str, Path], 
                    organization: str = "year_journal") -> Path:
        """Organize PDF file in database structure.
        
        Args:
            entry_id: Entry ID
            pdf_path: Current PDF path
            organization: Organization scheme (year_journal, year_author, flat)
            
        Returns:
            New PDF path
        """
        if entry_id not in self.entries:
            raise ScholarError(f"Entry not found: {entry_id}")
        
        entry = self.entries[entry_id]
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise ScholarError(f"PDF not found: {pdf_path}")
        
        # Determine target directory
        if organization == "year_journal":
            year_dir = str(entry.year) if entry.year else "unknown_year"
            journal_dir = entry.journal.replace("/", "_") if entry.journal else "unknown_journal"
            target_dir = self.pdfs_dir / year_dir / journal_dir
        elif organization == "year_author":
            year_dir = str(entry.year) if entry.year else "unknown_year"
            author_dir = entry.authors[0].split()[-1] if entry.authors else "unknown_author"
            target_dir = self.pdfs_dir / year_dir / author_dir
        else:  # flat
            target_dir = self.pdfs_dir
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        filename = entry.get_suggested_filename()
        target_path = target_dir / filename
        
        # Handle duplicates
        if target_path.exists() and target_path != pdf_path:
            counter = 1
            while target_path.exists():
                stem = filename.rsplit(".", 1)[0]
                target_path = target_dir / f"{stem}_{counter}.pdf"
                counter += 1
        
        # Move/copy file
        if pdf_path != target_path:
            shutil.copy2(pdf_path, target_path)
            logger.info(f"Organized PDF: {target_path}")
        
        # Update entry
        self.update_entry(entry_id, {"pdf_path": str(target_path)})
        
        return target_path
    
    def search(self, **kwargs) -> List[Tuple[str, DatabaseEntry]]:
        """Search database with various criteria.
        
        Supported criteria:
        - doi: Exact DOI match
        - title: Title search (fuzzy)
        - author: Author name search
        - year: Publication year
        - journal: Journal name
        - tag: Tag search
        - collection: Collection name
        - status: Download status
        
        Returns:
            List of (entry_id, entry) tuples
        """
        # Use index to find matching IDs
        matching_ids = self.index.search(kwargs)
        
        # Return entries
        results = []
        for entry_id in matching_ids:
            if entry_id in self.entries:
                results.append((entry_id, self.entries[entry_id]))
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            "total_entries": len(self.entries),
            "index_stats": self.index.get_stats(),
            "pdf_stats": {
                "total": 0,
                "valid": 0,
                "complete": 0,
                "searchable": 0,
            },
            "download_async_stats": defaultdict(int),
            "journal_distribution": defaultdict(int),
            "year_distribution": defaultdict(int),
        }
        
        # Calculate statistics
        for entry in self.entries.values():
            # PDF stats
            if entry.pdf_path:
                stats["pdf_stats"]["total"] += 1
                if entry.pdf_valid:
                    stats["pdf_stats"]["valid"] += 1
                if entry.pdf_complete:
                    stats["pdf_stats"]["complete"] += 1
                if entry.pdf_searchable:
                    stats["pdf_stats"]["searchable"] += 1
            
            # Download stats
            stats["download_async_stats"][entry.download_async_status] += 1
            
            # Journal distribution
            if entry.journal:
                stats["journal_distribution"][entry.journal] += 1
            
            # Year distribution
            if entry.year:
                stats["year_distribution"][entry.year] += 1
        
        # Convert defaultdicts to regular dicts
        stats["download_async_stats"] = dict(stats["download_async_stats"])
        stats["journal_distribution"] = dict(stats["journal_distribution"])
        stats["year_distribution"] = dict(stats["year_distribution"])
        
        return stats
    
    def export_to_bibtex(self, output_path: Union[str, Path], 
                        entry_ids: Optional[List[str]] = None) -> Path:
        """Export entries to BibTeX format.
        
        Args:
            output_path: Output file path
            entry_ids: Specific entries to export (None for all)
            
        Returns:
            Path to exported file
        """
        from scitex.scholar import Papers
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get entries to export
        if entry_ids:
            entries = [self.entries[eid] for eid in entry_ids if eid in self.entries]
        else:
            entries = list(self.entries.values())
        
        # Convert to Papers
        papers = Papers()
        for entry in entries:
            # Create Paper object from entry
            paper_data = {
                "doi": entry.doi,
                "title": entry.title,
                "authors": entry.authors,
                "year": entry.year,
                "journal": entry.journal,
                "volume": entry.volume,
                "pages": entry.pages,
                "abstract": entry.abstract,
                "keywords": entry.keywords,
                "url": entry.url,
                "pdf_url": entry.pdf_url,
            }
            
            # Add impact factor
            if entry.impact_factor:
                paper_data["impact_factor"] = entry.impact_factor
            
            papers.append(paper_data)
        
        # Export
        papers.to_bibtex(output_path)
        
        logger.info(f"Exported {len(papers)} entries to: {output_path}")
        return output_path
    
    def export_to_json(self, output_path: Union[str, Path], 
                      entry_ids: Optional[List[str]] = None) -> Path:
        """Export entries to JSON format.
        
        Args:
            output_path: Output file path
            entry_ids: Specific entries to export (None for all)
            
        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get entries to export
        if entry_ids:
            entries = {eid: self.entries[eid] for eid in entry_ids if eid in self.entries}
        else:
            entries = self.entries
        
        # Convert to serializable format
        export_data = {
            "metadata": {
                "exported_date": datetime.now().isoformat(),
                "total_entries": len(entries),
                "database_version": "1.0"
            },
            "entries": {
                entry_id: entry.to_dict() for entry_id, entry in entries.items()
            }
        }
        
        # Write
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(entries)} entries to: {output_path}")
        return output_path
    
    def _save_database(self):
        """Save database to disk."""
        try:
            # Convert entries to serializable format
            data = {
                entry_id: entry.to_dict() 
                for entry_id, entry in self.entries.items()
            }
            
            # Write atomically
            temp_file = self.db_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Replace original
            temp_file.replace(self.db_file)
            
            # Save indices
            self.index.save_indices()
            
            # Update metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(self.entries),
                "statistics": self.get_statistics()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise ScholarError(f"Could not save database: {e}")
    
    def _load_database(self):
        """Load database from disk."""
        if not self.db_file.exists():
            logger.info("No existing database found")
            return
        
        try:
            with open(self.db_file) as f:
                data = json.load(f)
            
            # Load entries
            for entry_id, entry_data in data.items():
                entry = DatabaseEntry.from_dict(entry_data)
                self.entries[entry_id] = entry
                self.index.add_entry(entry_id, entry)
            
            logger.info(f"Loaded {len(self.entries)} entries from database")
            
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise ScholarError(f"Could not load database: {e}")
    
    def cleanup_orphaned_pdfs(self, dry_run: bool = True) -> List[Path]:
        """Find and optionally remove PDFs not in database.
        
        Args:
            dry_run: If True, only report orphans without deleting
            
        Returns:
            List of orphaned PDF paths
        """
        # Get all PDFs in database
        db_pdfs = set()
        for entry in self.entries.values():
            if entry.pdf_path:
                db_pdfs.add(Path(entry.pdf_path).resolve())
        
        # Find all PDFs in directory
        all_pdfs = set()
        for pdf_path in self.pdfs_dir.rglob("*.pdf"):
            all_pdfs.add(pdf_path.resolve())
        
        # Find orphans
        orphans = all_pdfs - db_pdfs
        
        if orphans:
            logger.info(f"Found {len(orphans)} orphaned PDFs")
            
            if not dry_run:
                for pdf_path in orphans:
                    pdf_path.unlink()
                    logger.info(f"Deleted orphan: {pdf_path}")
        
        return list(orphans)


# EOF