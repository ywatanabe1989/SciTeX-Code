#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 13:50:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_ZoteroCompatibleDB.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_ZoteroCompatibleDB.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Zotero-compatible scholar database with enrichment workflow.

Implements the workflow:
1. Partial info (title, authors, year) → DOI resolution
2. DOI → Enrichment (metadata from multiple sources)
3. Storage in Zotero-compatible structure

Key features:
- Mimics Zotero's database schema for easy import/export
- Tracks metadata sources for all fields
- Supports incremental enrichment
- Maintains Zotero's storage structure
"""

import hashlib
import json
import os
import random
import re
import shutil
import sqlite3
import string
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scitex import logging

logger = logging.getLogger(__name__)


class ZoteroCompatibleDB:
    """Zotero-compatible database with enrichment workflow.
    
    Follows Zotero's schema and storage patterns for compatibility while
    adding source tracking and enrichment capabilities.
    """
    
    # Zotero-compatible item types
    ITEM_TYPES = {
        "journalArticle": 1,
        "book": 2,
        "bookSection": 3,
        "thesis": 4,
        "conferencePaper": 5,
        "preprint": 6,
        "report": 7,
        "webpage": 8
    }
    
    # Field mappings (Zotero fieldID to our field names)
    FIELD_MAP = {
        1: "title",
        2: "abstract", 
        3: "journal",
        4: "volume",
        5: "issue",
        6: "pages",
        7: "date",
        8: "DOI",
        9: "url",
        10: "accessDate",
        11: "extra",  # We use this for source tracking
        12: "publisher",
        13: "place",
        14: "series",
        15: "seriesNumber",
        16: "ISBN",
        17: "ISSN",
        18: "shortTitle",
        19: "archive",
        20: "archiveLocation",
        21: "libraryCatalog",
        22: "callNumber",
        23: "rights",
        24: "language",
        25: "dateAdded",
        26: "dateModified"
    }
    
    def __init__(self, base_dir: Optional[Path] = None, library_name: str = "default"):
        """Initialize Zotero-compatible database.
        
        Args:
            base_dir: Base directory (default: $SCITEX_DIR/scholar/library/<library_name>)
            library_name: Name of the library (default: "default")
        """
        # Determine base directory
        if base_dir is None:
            # Check environment variable first
            scitex_dir = os.getenv("SCITEX_DIR")
            if scitex_dir:
                base_dir = Path(scitex_dir) / "scholar" / "library" / library_name
            else:
                # Fallback to ~/.scitex
                base_dir = Path.home() / ".scitex" / "scholar" / "library" / library_name
                
            logger.info(f"Using library directory: {base_dir}")
            
        self.base_dir = Path(base_dir)
        self.library_name = library_name
        self.db_path = self.base_dir / "zotero.sqlite"
        self.storage_dir = self.base_dir / "storage"
        
        # Detect platform
        import platform
        self.is_windows = platform.system() == "Windows"
        self.is_wsl = "microsoft" in platform.uname().release.lower()
        
        # Create structure
        self._init_directories()
        self._init_database()
        
        # Create library config
        self._save_library_config()
        
    def _init_directories(self):
        """Create Zotero-style directory structure with human-readable organization."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Primary storage (Zotero-style)
        (self.storage_dir / "by_key").mkdir(parents=True, exist_ok=True)
        
        # Human-readable organization
        (self.storage_dir / "by_citation").mkdir(exist_ok=True)
        (self.storage_dir / "by_year").mkdir(exist_ok=True)
        (self.storage_dir / "by_journal").mkdir(exist_ok=True)
        (self.storage_dir / "by_topic").mkdir(exist_ok=True)
        
        # Windows shortcuts directory (separate from symlinks)
        if self.is_windows or self.is_wsl:
            (self.storage_dir / "shortcuts_windows").mkdir(exist_ok=True)
            
        # Zotero compatibility directories
        (self.base_dir / "translators").mkdir(exist_ok=True)
        (self.base_dir / "styles").mkdir(exist_ok=True)
        (self.base_dir / "locate").mkdir(exist_ok=True)
        
    def _init_database(self):
        """Initialize Zotero-compatible database schema."""
        with self._get_connection() as conn:
            # Zotero settings
            conn.execute("PRAGMA page_size=4096")
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Version info (Zotero compatibility)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS version (
                    schema TEXT PRIMARY KEY,
                    version INT NOT NULL
                )
            """)
            conn.execute("INSERT OR REPLACE INTO version VALUES ('userdata', 120)")
            
            # Libraries (simplified - we use single library)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS libraries (
                    libraryID INTEGER PRIMARY KEY,
                    type TEXT NOT NULL,
                    editable INT NOT NULL,
                    filesEditable INT NOT NULL
                )
            """)
            conn.execute("""
                INSERT OR IGNORE INTO libraries VALUES (1, 'user', 1, 1)
            """)
            
            # Items (main table)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    itemID INTEGER PRIMARY KEY,
                    itemTypeID INT NOT NULL,
                    dateAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dateModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clientDateModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    libraryID INT,
                    key TEXT NOT NULL,  -- 8-character key
                    version INT DEFAULT 0,
                    synced INT DEFAULT 0,
                    UNIQUE(libraryID, key),
                    FOREIGN KEY (libraryID) REFERENCES libraries(libraryID)
                )
            """)
            
            # Item data values
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemDataValues (
                    valueID INTEGER PRIMARY KEY,
                    value TEXT UNIQUE
                )
            """)
            
            # Item data (field values)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemData (
                    itemID INT,
                    fieldID INT,
                    valueID INT,
                    PRIMARY KEY (itemID, fieldID),
                    FOREIGN KEY (itemID) REFERENCES items(itemID),
                    FOREIGN KEY (valueID) REFERENCES itemDataValues(valueID)
                )
            """)
            
            # Creators
            conn.execute("""
                CREATE TABLE IF NOT EXISTS creators (
                    creatorID INTEGER PRIMARY KEY,
                    firstName TEXT,
                    lastName TEXT,
                    fieldMode INT,  -- 0=two fields, 1=single field
                    UNIQUE(firstName, lastName)
                )
            """)
            
            # Item creators
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemCreators (
                    itemID INT,
                    creatorID INT,
                    creatorTypeID INT DEFAULT 1,  -- 1=author
                    orderIndex INT,
                    PRIMARY KEY (itemID, orderIndex),
                    FOREIGN KEY (itemID) REFERENCES items(itemID),
                    FOREIGN KEY (creatorID) REFERENCES creators(creatorID)
                )
            """)
            
            # Collections
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collections (
                    collectionID INTEGER PRIMARY KEY,
                    collectionName TEXT,
                    parentCollectionID INT,
                    dateAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dateModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clientDateModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    libraryID INT,
                    key TEXT NOT NULL,
                    version INT DEFAULT 0,
                    synced INT DEFAULT 0,
                    UNIQUE(libraryID, key),
                    FOREIGN KEY (libraryID) REFERENCES libraries(libraryID),
                    FOREIGN KEY (parentCollectionID) REFERENCES collections(collectionID)
                )
            """)
            
            # Collection items
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collectionItems (
                    collectionID INT,
                    itemID INT,
                    orderIndex INT,
                    PRIMARY KEY (collectionID, itemID),
                    FOREIGN KEY (collectionID) REFERENCES collections(collectionID),
                    FOREIGN KEY (itemID) REFERENCES items(itemID)
                )
            """)
            
            # Tags
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tagID INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            # Item tags
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemTags (
                    itemID INT,
                    tagID INT,
                    type INT DEFAULT 0,
                    PRIMARY KEY (itemID, tagID),
                    FOREIGN KEY (itemID) REFERENCES items(itemID),
                    FOREIGN KEY (tagID) REFERENCES tags(tagID)
                )
            """)
            
            # Item attachments
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemAttachments (
                    itemID INTEGER PRIMARY KEY,
                    parentItemID INT,
                    linkMode INT,  -- 0=imported file, 1=linked file, 2=imported URL
                    contentType TEXT,
                    charsetID INT,
                    path TEXT,
                    syncState INT DEFAULT 0,
                    storageModTime INT,
                    storageHash TEXT,
                    FOREIGN KEY (itemID) REFERENCES items(itemID),
                    FOREIGN KEY (parentItemID) REFERENCES items(itemID)
                )
            """)
            
            # Item notes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itemNotes (
                    itemID INTEGER PRIMARY KEY,
                    parentItemID INT,
                    note TEXT,
                    title TEXT,
                    FOREIGN KEY (itemID) REFERENCES items(itemID),
                    FOREIGN KEY (parentItemID) REFERENCES items(itemID)
                )
            """)
            
            # Deleted items
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deletedItems (
                    itemID INTEGER PRIMARY KEY,
                    dateDeleted DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Full text content
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fulltextItems (
                    itemID INTEGER PRIMARY KEY,
                    indexedPages INT,
                    totalPages INT,
                    indexedChars INT,
                    totalChars INT,
                    version INT DEFAULT 0,
                    synced INT DEFAULT 0,
                    FOREIGN KEY (itemID) REFERENCES items(itemID)
                )
            """)
            
            # Full text words
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fulltextWords (
                    wordID INTEGER PRIMARY KEY,
                    word TEXT UNIQUE
                )
            """)
            
            # Full text item words
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fulltextItemWords (
                    wordID INT,
                    itemID INT,
                    PRIMARY KEY (wordID, itemID),
                    FOREIGN KEY (wordID) REFERENCES fulltextWords(wordID),
                    FOREIGN KEY (itemID) REFERENCES items(itemID)
                )
            """)
            
            # SciTeX extensions
            
            # Source tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scitex_field_sources (
                    itemID INT,
                    fieldName TEXT,
                    source TEXT,
                    confidence REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (itemID, fieldName),
                    FOREIGN KEY (itemID) REFERENCES items(itemID)
                )
            """)
            
            # Enrichment status
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scitex_enrichment_status (
                    itemID INTEGER PRIMARY KEY,
                    doi_resolved BOOLEAN DEFAULT 0,
                    metadata_enriched BOOLEAN DEFAULT 0,
                    pdf_downloaded BOOLEAN DEFAULT 0,
                    fulltext_extracted BOOLEAN DEFAULT 0,
                    last_enrichment TIMESTAMP,
                    enrichment_errors TEXT,  -- JSON
                    FOREIGN KEY (itemID) REFERENCES items(itemID)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_key ON items(key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_dateAdded ON items(dateAdded)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_dateModified ON items(dateModified)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_itemData_value ON itemData(itemID, valueID)")
            
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
            
    def _generate_key(self, length: int = 8) -> str:
        """Generate Zotero-style key."""
        # Zotero uses base32-like encoding
        chars = string.ascii_uppercase + string.digits
        # Avoid ambiguous characters
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(random.choice(chars) for _ in range(length))
        
    def _get_or_create_value(self, conn: sqlite3.Connection, value: Any) -> int:
        """Get or create value in itemDataValues table."""
        if value is None:
            return None
            
        value_str = str(value)
        
        cursor = conn.execute(
            "SELECT valueID FROM itemDataValues WHERE value = ?",
            (value_str,)
        )
        row = cursor.fetchone()
        
        if row:
            return row["valueID"]
        else:
            cursor = conn.execute(
                "INSERT INTO itemDataValues (value) VALUES (?)",
                (value_str,)
            )
            return cursor.lastrowid
            
    def _get_field_id(self, field_name: str) -> Optional[int]:
        """Get Zotero fieldID from field name."""
        # Reverse lookup in field map
        for field_id, name in self.FIELD_MAP.items():
            if name == field_name:
                return field_id
        # Handle special cases
        if field_name == "doi":
            return 8  # DOI fieldID
        return None
        
    def add_item_from_partial(self, partial_info: Dict[str, Any], 
                            item_type: str = "journalArticle") -> int:
        """Add item from partial information (step 1 of workflow).
        
        Args:
            partial_info: Dict with title, authors, year, etc.
            item_type: Zotero item type
            
        Returns:
            Item ID
        """
        with self._get_connection() as conn:
            # Create item
            key = self._generate_key()
            item_type_id = self.ITEM_TYPES.get(item_type, 1)
            
            cursor = conn.execute("""
                INSERT INTO items (itemTypeID, libraryID, key)
                VALUES (?, 1, ?)
            """, (item_type_id, key))
            item_id = cursor.lastrowid
            
            # Add basic fields
            fields_to_add = {
                "title": partial_info.get("title"),
                "date": str(partial_info.get("year")) if partial_info.get("year") else None,
                "DOI": partial_info.get("doi"),
                "url": partial_info.get("url"),
                "journal": partial_info.get("journal"),
                "abstract": partial_info.get("abstract")
            }
            
            for field_name, value in fields_to_add.items():
                if value:
                    self._set_item_field(conn, item_id, field_name, value)
                    
                    # Track source
                    source = partial_info.get(f"{field_name}_source", "initial_import")
                    self._track_field_source(conn, item_id, field_name, source)
                    
            # Add creators
            authors = partial_info.get("authors", [])
            for idx, author in enumerate(authors):
                self._add_creator(conn, item_id, author, idx)
                
            # Add tags/keywords
            keywords = partial_info.get("keywords", [])
            for keyword in keywords:
                self._add_tag(conn, item_id, keyword)
                
            # Initialize enrichment status
            conn.execute("""
                INSERT INTO scitex_enrichment_status (itemID)
                VALUES (?)
            """, (item_id,))
            
            conn.commit()
            
            # Create storage directory
            storage_path = self.storage_dir / key
            storage_path.mkdir(exist_ok=True)
            
            logger.info(f"Added item {item_id} with key {key}: {partial_info.get('title', '')[:50]}...")
            
            # Create human-readable links
            self._create_human_readable_links(item_id, key, partial_info)
            
            return item_id
            
    def _create_human_readable_links(self, item_id: int, key: str, 
                                    metadata: Dict[str, Any]):
        """Create human-readable symlinks and Windows shortcuts."""
        # Generate citation-style name
        citation_name = self._generate_citation_name(metadata)
        
        # Primary storage path
        primary_path = self.storage_dir / "by_key" / key
        
        # Create by_citation links
        citation_dir = self.storage_dir / "by_citation" / citation_name
        citation_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlinks (works on Linux/Mac/WSL)
        if not self.is_windows:
            self._create_symlink(
                primary_path,
                citation_dir / f"{citation_name}-{key}"
            )
            
        # Create Windows shortcuts
        if self.is_windows or self.is_wsl:
            self._create_windows_shortcut(
                primary_path,
                self.storage_dir / "shortcuts_windows" / citation_name / f"{citation_name}-{key}.lnk"
            )
            
        # Create by_year organization
        year = metadata.get("year")
        if year:
            year_dir = self.storage_dir / "by_year" / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)
            
            if not self.is_windows:
                self._create_symlink(
                    primary_path,
                    year_dir / f"{citation_name}-{key}"
                )
                
        # Create by_journal organization
        journal = metadata.get("journal")
        if journal:
            safe_journal = self._sanitize_filename(journal)[:50]
            journal_dir = self.storage_dir / "by_journal" / safe_journal
            journal_dir.mkdir(parents=True, exist_ok=True)
            
            if not self.is_windows:
                self._create_symlink(
                    primary_path,
                    journal_dir / f"{citation_name}-{key}"
                )
                
    def _generate_citation_name(self, metadata: Dict[str, Any]) -> str:
        """Generate human-readable citation name.
        
        Format: FIRSTAUTHOR-YEAR-SOURCE
        Where SOURCE can be journal abbreviation, conference, book publisher, etc.
        """
        # Get first author
        authors = metadata.get("authors", [])
        if authors:
            first_author = authors[0]
            if "," in first_author:
                author_name = first_author.split(",")[0].strip()
            else:
                author_name = first_author.split()[-1] if first_author else "Unknown"
        else:
            author_name = "Unknown"
            
        # Sanitize author name
        author_name = self._sanitize_filename(author_name)
        
        # Get year
        year = metadata.get("year", "XXXX")
        
        # Get source (journal, conference, publisher, etc.)
        source = None
        
        # Priority order for source
        if metadata.get("journal"):
            source = self._abbreviate_journal(metadata["journal"])
        elif metadata.get("booktitle"):  # Conference
            source = self._abbreviate_conference(metadata["booktitle"])
        elif metadata.get("publisher"):  # Book
            source = metadata["publisher"]
        elif metadata.get("school"):  # Thesis
            source = metadata["school"]
        elif metadata.get("institution"):  # Report
            source = metadata["institution"]
        elif "arxiv" in metadata.get("doi", "").lower():
            source = "arXiv"
        else:
            source = "Misc"
            
        source = self._sanitize_filename(source)[:30]  # Limit length
        
        return f"{author_name}-{year}-{source}"
        
    def _abbreviate_journal(self, journal_name: str) -> str:
        """Create journal abbreviation."""
        # Common journal abbreviations
        abbreviations = {
            "nature": "Nature",
            "science": "Science",
            "cell": "Cell",
            "proceedings of the national academy of sciences": "PNAS",
            "physical review letters": "PRL",
            "journal of the american chemical society": "JACS",
            "angewandte chemie": "AngChem",
            "new england journal of medicine": "NEJM",
            "the lancet": "Lancet",
            "ieee transactions": "IEEE-T",
            "acm transactions": "ACM-T",
            "neural information processing systems": "NeurIPS",
            "international conference on machine learning": "ICML",
            "conference on computer vision and pattern recognition": "CVPR"
        }
        
        # Check for exact matches
        journal_lower = journal_name.lower()
        for key, abbrev in abbreviations.items():
            if key in journal_lower:
                return abbrev
                
        # Create abbreviation from first letters of significant words
        words = journal_name.split()
        stop_words = {"of", "the", "and", "in", "on", "for", "a", "an"}
        significant_words = [w for w in words if w.lower() not in stop_words]
        
        if len(significant_words) <= 3:
            return "-".join(significant_words)
        else:
            # Use first letter of each significant word
            return "".join(w[0].upper() for w in significant_words[:6])
            
    def _abbreviate_conference(self, conference_name: str) -> str:
        """Create conference abbreviation."""
        # Extract year if present
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', conference_name)
        
        # Remove year for abbreviation
        name_without_year = re.sub(r'\b(19|20)\d{2}\b', '', conference_name).strip()
        
        # Common conference patterns
        if "workshop" in name_without_year.lower():
            return "Workshop"
        elif "symposium" in name_without_year.lower():
            return "Symposium"
        elif "conference" in name_without_year.lower():
            # Get words before "conference"
            words = name_without_year.lower().split("conference")[0].split()
            if words:
                return "".join(w[0].upper() for w in words if len(w) > 2)[:6] + "-Conf"
                
        return self._abbreviate_journal(name_without_year)
        
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename."""
        # Replace problematic characters
        replacements = {
            "/": "-",
            "\\": "-",
            ":": "-",
            "*": "-",
            "?": "",
            "\"": "",
            "<": "",
            ">": "",
            "|": "-",
            " ": "_",
            ".": "",
            ",": "",
            ";": "",
            "'": "",
            "!": "",
            "@": "at",
            "#": "num",
            "$": "S",
            "%": "pct",
            "^": "",
            "&": "and",
            "(": "",
            ")": "",
            "[": "",
            "]": "",
            "{": "",
            "}": "",
            "=": "-",
            "+": "plus",
            "~": "-",
            "`": ""
        }
        
        result = name
        for old, new in replacements.items():
            result = result.replace(old, new)
            
        # Remove multiple underscores/hyphens
        result = re.sub(r'[-_]+', '-', result)
        result = result.strip('-_')
        
        # Ensure it's not empty
        if not result:
            result = "Unknown"
            
        return result
        
    def _create_symlink(self, target: Path, link: Path):
        """Create symlink (Linux/Mac/WSL)."""
        try:
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.exists():
                link.unlink()
            link.symlink_to(target)
            logger.debug(f"Created symlink: {link} -> {target}")
        except Exception as e:
            logger.warning(f"Failed to create symlink: {e}")
            
    def _create_windows_shortcut(self, target: Path, shortcut_path: Path):
        """Create Windows .lnk shortcut file."""
        try:
            shortcut_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use Windows COM to create shortcut
            if self.is_windows:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(target)
                shortcut.WorkingDirectory = str(target.parent)
                shortcut.save()
                logger.debug(f"Created Windows shortcut: {shortcut_path}")
            elif self.is_wsl:
                # For WSL, create a simple text file with the path
                # (Real .lnk files need to be created from Windows side)
                info_file = shortcut_path.with_suffix('.txt')
                with open(info_file, 'w') as f:
                    f.write(f"Target: {target}\n")
                    f.write(f"This is a placeholder. Create real .lnk file from Windows.\n")
                logger.debug(f"Created shortcut info file: {info_file}")
                
        except Exception as e:
            logger.warning(f"Failed to create Windows shortcut: {e}")
            
    def _save_library_config(self):
        """Save library configuration for easy access."""
        config = {
            "library_name": self.library_name,
            "base_dir": str(self.base_dir),
            "created_at": datetime.now().isoformat(),
            "zotero_compatible": True,
            "scitex_version": "1.0",
            "features": {
                "human_readable_links": True,
                "metadata_source_tracking": True,
                "enrichment_workflow": True,
                "windows_shortcuts": self.is_windows or self.is_wsl
            }
        }
        
        config_path = self.base_dir / "library.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        # Also save to global library registry
        registry_dir = self.base_dir.parent.parent / "config"
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        registry_path = registry_dir / "libraries.json"
        
        # Load existing registry
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {"libraries": {}}
            
        # Update registry
        registry["libraries"][self.library_name] = {
            "path": str(self.base_dir),
            "created_at": config["created_at"],
            "last_accessed": datetime.now().isoformat()
        }
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
            
        logger.info(f"Library config saved: {config_path}")
            
    def _set_item_field(self, conn: sqlite3.Connection, item_id: int, 
                       field_name: str, value: Any):
        """Set field value for item."""
        field_id = self._get_field_id(field_name)
        if not field_id:
            logger.warning(f"Unknown field: {field_name}")
            return
            
        value_id = self._get_or_create_value(conn, value)
        if value_id:
            conn.execute("""
                INSERT OR REPLACE INTO itemData (itemID, fieldID, valueID)
                VALUES (?, ?, ?)
            """, (item_id, field_id, value_id))
            
    def _track_field_source(self, conn: sqlite3.Connection, item_id: int,
                          field_name: str, source: str, confidence: float = 1.0):
        """Track metadata source for field."""
        conn.execute("""
            INSERT OR REPLACE INTO scitex_field_sources 
            (itemID, fieldName, source, confidence)
            VALUES (?, ?, ?, ?)
        """, (item_id, field_name, source, confidence))
        
    def _add_creator(self, conn: sqlite3.Connection, item_id: int, 
                    author_name: str, order_index: int):
        """Add creator to item."""
        # Parse name
        if "," in author_name:
            parts = author_name.split(",", 1)
            last_name = parts[0].strip()
            first_name = parts[1].strip() if len(parts) > 1 else ""
            field_mode = 0
        else:
            # Single field mode
            first_name = author_name
            last_name = ""
            field_mode = 1
            
        # Get or create creator
        cursor = conn.execute(
            "SELECT creatorID FROM creators WHERE firstName = ? AND lastName = ?",
            (first_name, last_name)
        )
        row = cursor.fetchone()
        
        if row:
            creator_id = row["creatorID"]
        else:
            cursor = conn.execute(
                "INSERT INTO creators (firstName, lastName, fieldMode) VALUES (?, ?, ?)",
                (first_name, last_name, field_mode)
            )
            creator_id = cursor.lastrowid
            
        # Link to item
        conn.execute("""
            INSERT OR REPLACE INTO itemCreators 
            (itemID, creatorID, creatorTypeID, orderIndex)
            VALUES (?, ?, 1, ?)
        """, (item_id, creator_id, order_index))
        
    def _add_tag(self, conn: sqlite3.Connection, item_id: int, tag_name: str):
        """Add tag to item."""
        # Get or create tag
        cursor = conn.execute(
            "SELECT tagID FROM tags WHERE name = ?",
            (tag_name.lower(),)
        )
        row = cursor.fetchone()
        
        if row:
            tag_id = row["tagID"]
        else:
            cursor = conn.execute(
                "INSERT INTO tags (name) VALUES (?)",
                (tag_name.lower(),)
            )
            tag_id = cursor.lastrowid
            
        # Link to item
        conn.execute("""
            INSERT OR IGNORE INTO itemTags (itemID, tagID)
            VALUES (?, ?)
        """, (item_id, tag_id))
        
    def update_item_doi(self, item_id: int, doi: str, source: str) -> bool:
        """Update item with resolved DOI (step 2 of workflow)."""
        with self._get_connection() as conn:
            self._set_item_field(conn, item_id, "DOI", doi)
            self._track_field_source(conn, item_id, "DOI", source)
            
            # Update enrichment status
            conn.execute("""
                UPDATE scitex_enrichment_status
                SET doi_resolved = 1
                WHERE itemID = ?
            """, (item_id,))
            
            conn.commit()
            logger.info(f"Updated item {item_id} with DOI: {doi}")
            return True
            
    def enrich_item_metadata(self, item_id: int, metadata: Dict[str, Any]) -> bool:
        """Enrich item with metadata from various sources (step 3 of workflow)."""
        with self._get_connection() as conn:
            # Update all provided fields
            for field_name, value in metadata.items():
                if field_name.endswith("_source"):
                    continue
                    
                if value:
                    self._set_item_field(conn, item_id, field_name, value)
                    
                    # Track source
                    source = metadata.get(f"{field_name}_source", "enrichment")
                    self._track_field_source(conn, item_id, field_name, source)
                    
            # Update modified timestamp
            conn.execute("""
                UPDATE items 
                SET dateModified = CURRENT_TIMESTAMP
                WHERE itemID = ?
            """, (item_id,))
            
            # Update enrichment status
            conn.execute("""
                UPDATE scitex_enrichment_status
                SET metadata_enriched = 1, last_enrichment = CURRENT_TIMESTAMP
                WHERE itemID = ?
            """, (item_id,))
            
            conn.commit()
            logger.info(f"Enriched item {item_id} with {len(metadata)} fields")
            return True
            
    def attach_pdf(self, parent_item_id: int, pdf_path: Path, 
                  title: str = "Full Text PDF") -> int:
        """Attach PDF to item (Zotero-style)."""
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None
            
        with self._get_connection() as conn:
            # Get parent key for storage
            cursor = conn.execute(
                "SELECT key FROM items WHERE itemID = ?",
                (parent_item_id,)
            )
            parent = cursor.fetchone()
            if not parent:
                logger.error(f"Parent item {parent_item_id} not found")
                return None
                
            parent_key = parent["key"]
            
            # Create attachment item
            attachment_key = self._generate_key()
            cursor = conn.execute("""
                INSERT INTO items (itemTypeID, libraryID, key)
                VALUES (14, 1, ?)
            """, (attachment_key,))  # 14 = attachment
            attachment_id = cursor.lastrowid
            
            # Copy PDF to storage
            storage_path = self.storage_dir / parent_key
            storage_path.mkdir(exist_ok=True)
            
            dest_path = storage_path / f"{attachment_key}.pdf"
            shutil.copy2(pdf_path, dest_path)
            
            # Calculate hash
            with open(dest_path, 'rb') as f:
                content = f.read()
                storage_hash = hashlib.md5(content).hexdigest()
                
            # Create attachment record
            conn.execute("""
                INSERT INTO itemAttachments 
                (itemID, parentItemID, linkMode, contentType, path, storageHash)
                VALUES (?, ?, 0, 'application/pdf', ?, ?)
            """, (attachment_id, parent_item_id, f"storage:{attachment_key}.pdf", storage_hash))
            
            # Set title
            self._set_item_field(conn, attachment_id, "title", title)
            
            # Update enrichment status
            conn.execute("""
                UPDATE scitex_enrichment_status
                SET pdf_downloaded = 1
                WHERE itemID = ?
            """, (parent_item_id,))
            
            conn.commit()
            
            logger.info(f"Attached PDF to item {parent_item_id}")
            return attachment_id
            
    def get_items_needing_enrichment(self, stage: str = "doi") -> List[Dict[str, Any]]:
        """Get items that need enrichment at specific stage."""
        stage_conditions = {
            "doi": "doi_resolved = 0",
            "metadata": "doi_resolved = 1 AND metadata_enriched = 0",
            "pdf": "metadata_enriched = 1 AND pdf_downloaded = 0",
            "fulltext": "pdf_downloaded = 1 AND fulltext_extracted = 0"
        }
        
        condition = stage_conditions.get(stage, "1=1")
        
        with self._get_connection() as conn:
            cursor = conn.execute(f"""
                SELECT i.itemID, i.key,
                       (SELECT value FROM itemDataValues v 
                        JOIN itemData d ON v.valueID = d.valueID 
                        WHERE d.itemID = i.itemID AND d.fieldID = 1) as title,
                       (SELECT value FROM itemDataValues v 
                        JOIN itemData d ON v.valueID = d.valueID 
                        WHERE d.itemID = i.itemID AND d.fieldID = 8) as doi,
                       es.*
                FROM items i
                LEFT JOIN scitex_enrichment_status es ON i.itemID = es.itemID
                WHERE i.itemTypeID != 14  -- Not attachment
                  AND {condition}
                ORDER BY i.dateAdded
            """)
            
            return [dict(row) for row in cursor]
            
    def export_to_zotero_rdf(self, output_path: Path):
        """Export database in Zotero RDF format."""
        # Implementation would generate Zotero RDF/XML format
        # This is a placeholder for the full implementation
        logger.info(f"Exporting to Zotero RDF: {output_path}")
        
    def import_from_zotero(self, zotero_db_path: Path):
        """Import from existing Zotero database."""
        logger.info(f"Importing from Zotero: {zotero_db_path}")
        
        # This would copy relevant tables and data
        # Placeholder for full implementation
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            stats = {}
            
            # Item counts by type
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN itemTypeID = 1 THEN 1 ELSE 0 END) as articles,
                    SUM(CASE WHEN itemTypeID = 14 THEN 1 ELSE 0 END) as attachments
                FROM items
                WHERE itemID NOT IN (SELECT itemID FROM deletedItems)
            """)
            stats["items"] = dict(cursor.fetchone())
            
            # Enrichment status
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(doi_resolved) as doi_resolved,
                    SUM(metadata_enriched) as metadata_enriched,
                    SUM(pdf_downloaded) as pdf_downloaded
                FROM scitex_enrichment_status
            """)
            stats["enrichment"] = dict(cursor.fetchone())
            
            # Storage info
            pdf_count = len(list(self.storage_dir.glob("*/*.pdf")))
            stats["storage"] = {
                "pdf_count": pdf_count,
                "storage_path": str(self.storage_dir)
            }
            
            return stats


if __name__ == "__main__":
    print("Zotero-Compatible Scholar Database")
    print("=" * 60)
    print("\nWorkflow:")
    print("1. Add item with partial info (title, authors, year)")
    print("2. Resolve DOI from partial info")
    print("3. Enrich metadata using DOI")
    print("4. Download and attach PDF")
    print("5. Extract full text for search")
    
    print("\nExample usage:")
    print("""
    # Initialize
    db = ZoteroCompatibleDB()
    
    # Step 1: Add item with partial info
    item_id = db.add_item_from_partial({
        "title": "Attention is All You Need",
        "authors": ["Vaswani, A.", "Shazeer, N."],
        "year": 2017,
        "journal": "NeurIPS"
    })
    
    # Step 2: Update with resolved DOI
    db.update_item_doi(item_id, "10.48550/arXiv.1706.03762", "crossref")
    
    # Step 3: Enrich with metadata
    db.enrich_item_metadata(item_id, {
        "abstract": "The dominant sequence transduction models...",
        "abstract_source": "semantic_scholar",
        "pages": "5998-6008",
        "pages_source": "crossref"
    })
    
    # Step 4: Attach PDF
    db.attach_pdf(item_id, Path("attention.pdf"))
    
    # Get items needing enrichment
    needs_doi = db.get_items_needing_enrichment("doi")
    needs_metadata = db.get_items_needing_enrichment("metadata")
    """)

# EOF