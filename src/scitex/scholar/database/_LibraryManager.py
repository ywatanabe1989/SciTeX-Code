#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_LibraryManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_LibraryManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Library manager for SciTeX Scholar.

Manages multiple Zotero-compatible libraries with easy switching and discovery.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scitex import logging
from ._ZoteroCompatibleDB import ZoteroCompatibleDB

logger = logging.getLogger(__name__)


class LibraryManager:
    """Manages multiple scholar libraries."""
    
    def __init__(self):
        """Initialize library manager."""
        # Determine base directory
        self.scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
        self.scholar_dir = self.scitex_dir / "scholar"
        self.library_base = self.scholar_dir / "library"
        self.config_dir = self.scholar_dir / "config"
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.library_base.mkdir(parents=True, exist_ok=True)
        
        # Registry path
        self.registry_path = self.config_dir / "libraries.json"
        
    def list_libraries(self) -> Dict[str, Dict]:
        """List all available libraries."""
        if not self.registry_path.exists():
            return {}
            
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
            
        return data.get("libraries", {})
        
    def create_library(self, name: str, description: str = "") -> ZoteroCompatibleDB:
        """Create a new library.
        
        Args:
            name: Library name (used in path)
            description: Human-readable description
            
        Returns:
            ZoteroCompatibleDB instance
        """
        # Check if library already exists
        libraries = self.list_libraries()
        if name in libraries:
            raise ValueError(f"Library '{name}' already exists")
            
        # Create library
        db = ZoteroCompatibleDB(library_name=name)
        
        # Add description to config
        config_path = db.base_dir / "library.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        config["description"] = description
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Created library: {name}")
        return db
        
    def open_library(self, name: str = "default") -> ZoteroCompatibleDB:
        """Open an existing library.
        
        Args:
            name: Library name (default: "default")
            
        Returns:
            ZoteroCompatibleDB instance
        """
        return ZoteroCompatibleDB(library_name=name)
        
    def delete_library(self, name: str) -> bool:
        """Delete a library (moves to .deleted directory).
        
        Args:
            name: Library name
            
        Returns:
            Success status
        """
        if name == "default":
            logger.error("Cannot delete the default library")
            return False
            
        library_path = self.library_base / name
        if not library_path.exists():
            logger.error(f"Library '{name}' not found")
            return False
            
        # Move to deleted directory
        deleted_dir = self.library_base / ".deleted"
        deleted_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deleted_path = deleted_dir / f"{name}_{timestamp}"
        
        import shutil
        shutil.move(str(library_path), str(deleted_path))
        
        # Update registry
        libraries = self.list_libraries()
        if name in libraries:
            del libraries[name]
            
            registry = {"libraries": libraries}
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
                
        logger.info(f"Deleted library: {name} (moved to {deleted_path})")
        return True
        
    def import_from_zotero(self, zotero_path: Path, library_name: str = None) -> ZoteroCompatibleDB:
        """Import existing Zotero library.
        
        Args:
            zotero_path: Path to Zotero directory
            library_name: Name for imported library (default: based on path)
            
        Returns:
            ZoteroCompatibleDB instance
        """
        zotero_path = Path(zotero_path)
        
        if not (zotero_path / "zotero.sqlite").exists():
            raise ValueError(f"No Zotero database found at {zotero_path}")
            
        # Generate library name
        if library_name is None:
            library_name = f"imported_{zotero_path.name}_{datetime.now().strftime('%Y%m%d')}"
            
        # Create new library
        db = self.create_library(library_name, f"Imported from {zotero_path}")
        
        # Copy Zotero files
        import shutil
        
        # Copy database
        shutil.copy2(zotero_path / "zotero.sqlite", db.db_path)
        
        # Copy storage
        if (zotero_path / "storage").exists():
            shutil.copytree(
                zotero_path / "storage",
                db.storage_dir / "by_key",
                dirs_exist_ok=True
            )
            
        # Copy other directories
        for subdir in ["styles", "translators", "locate"]:
            if (zotero_path / subdir).exists():
                shutil.copytree(
                    zotero_path / subdir,
                    db.base_dir / subdir,
                    dirs_exist_ok=True
                )
                
        logger.info(f"Imported Zotero library to: {library_name}")
        
        # Create human-readable links for all items
        db._create_all_human_readable_links()
        
        return db
        
    def get_current_library(self) -> Optional[str]:
        """Get the current/default library name."""
        config_path = self.config_dir / "current_library.txt"
        
        if config_path.exists():
            return config_path.read_text().strip()
        else:
            return "default"
            
    def set_current_library(self, name: str):
        """Set the current/default library."""
        libraries = self.list_libraries()
        if name not in libraries and name != "default":
            raise ValueError(f"Library '{name}' not found")
            
        config_path = self.config_dir / "current_library.txt"
        config_path.write_text(name)
        
        logger.info(f"Set current library to: {name}")
        
    def get_library_stats(self, name: str = None) -> Dict:
        """Get statistics for a library."""
        if name is None:
            name = self.get_current_library()
            
        db = self.open_library(name)
        return db.get_statistics()


def get_default_library() -> ZoteroCompatibleDB:
    """Get the default library (convenience function)."""
    manager = LibraryManager()
    current = manager.get_current_library()
    return manager.open_library(current)


if __name__ == "__main__":
    print("SciTeX Scholar Library Manager")
    print("=" * 60)
    
    # Check environment
    scitex_dir = os.getenv("SCITEX_DIR")
    if scitex_dir:
        print(f"SCITEX_DIR: {scitex_dir}")
    else:
        print(f"SCITEX_DIR not set, using: ~/.scitex")
        
    print("\nLibrary structure:")
    print("""
    $SCITEX_DIR/scholar/
    ├── config/
    │   ├── libraries.json      # Registry of all libraries
    │   └── current_library.txt # Current default library
    └── library/
        ├── default/            # Default library
        │   ├── zotero.sqlite
        │   ├── library.json
        │   └── storage/
        ├── research_2025/      # Custom library
        └── imported_zotero/    # Imported from Zotero
    """)
    
    print("\nUsage:")
    print("""
    # Create manager
    manager = LibraryManager()
    
    # List libraries
    libraries = manager.list_libraries()
    
    # Create new library
    db = manager.create_library("research_2025", "2025 research papers")
    
    # Open existing library
    db = manager.open_library("default")
    
    # Import from Zotero
    db = manager.import_from_zotero(Path("~/Documents/Zotero"))
    
    # Get default library
    db = get_default_library()
    """)

# EOF