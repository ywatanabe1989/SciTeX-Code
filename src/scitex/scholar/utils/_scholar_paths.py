#!/usr/bin/env python3
"""
SciTeX Scholar Path Management with Backward Compatibility

This module provides path resolution that supports both:
1. New organized directory structure (Zotero-inspired)
2. Existing legacy structure (backward compatibility)

Ensures zero regression while enabling gradual migration to better organization.
"""

import os
from pathlib import Path
from typing import Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


class ScholarPaths:
    """
    Provides backward-compatible path resolution for SciTeX Scholar.
    
    This class ensures that existing functionality continues to work
    while providing access to the new organized directory structure.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize with scholar base directory."""
        self.base_dir = base_dir or Path.home() / ".scitex" / "scholar"
        
        # Check if new structure exists
        self.has_new_structure = self._check_new_structure()
        
        if self.has_new_structure:
            logger.info("📁 Using organized directory structure")
        else:
            logger.info("📁 Using legacy directory structure")
    
    def _check_new_structure(self) -> bool:
        """Check if new organized structure is available."""
        new_dirs = ["library", "cache", "profiles", "workspace", "config"]
        return all((self.base_dir / dirname).exists() for dirname in new_dirs)
    
    def get_pdfs_dir(self) -> Path:
        """Get PDFs directory with backward compatibility."""
        
        # Try new structure first (Zotero-style storage)
        if self.has_new_structure:
            new_storage = self.base_dir / "library" / "storage"
            if new_storage.exists() and any(new_storage.iterdir()):
                return new_storage
        
        # Fall back to existing structure
        legacy_pdfs = self.base_dir / "pdfs"
        legacy_pdfs.mkdir(parents=True, exist_ok=True)
        return legacy_pdfs
    
    def get_screenshots_dir(self) -> Path:
        """Get screenshots directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_screenshots = self.base_dir / "workspace" / "screenshots"
            if new_screenshots.exists():
                return new_screenshots
        
        # Fall back to existing structure
        legacy_screenshots = self.base_dir / "screenshots"
        legacy_screenshots.mkdir(parents=True, exist_ok=True)
        return legacy_screenshots
    
    def get_doi_cache_dir(self) -> Path:
        """Get DOI cache directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_cache = self.base_dir / "cache" / "doi_cache"
            if new_cache.exists():
                return new_cache
        
        # Fall back to existing structure
        legacy_cache = self.base_dir / "doi_cache"
        legacy_cache.mkdir(parents=True, exist_ok=True)
        return legacy_cache
    
    def get_database_dir(self) -> Path:
        """Get database directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_db = self.base_dir / "library"
            if new_db.exists():
                return new_db
        
        # Fall back to existing structure
        legacy_db = self.base_dir / "database"
        legacy_db.mkdir(parents=True, exist_ok=True)
        return legacy_db
    
    def get_translators_dir(self) -> Path:
        """Get Zotero translators directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_translators = self.base_dir / "config" / "translators"
            if new_translators.exists():
                return new_translators
        
        # Fall back to existing structure
        legacy_translators = self.base_dir / "zotero_translators"
        if legacy_translators.exists():
            return legacy_translators
        
        # Create in new location if neither exists
        new_translators = self.base_dir / "config" / "translators"
        new_translators.mkdir(parents=True, exist_ok=True)
        return new_translators
    
    def get_chrome_profiles_dir(self) -> Path:
        """Get Chrome profiles directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_profiles = self.base_dir / "profiles" / "chrome"
            if new_profiles.exists():
                return new_profiles
        
        # Fall back to existing structure (use main chrome_profiles)
        legacy_profiles = self.base_dir / "chrome_profiles"
        if legacy_profiles.exists():
            return legacy_profiles
        
        # Create in new location if neither exists
        new_profiles = self.base_dir / "profiles" / "chrome"
        new_profiles.mkdir(parents=True, exist_ok=True)
        return new_profiles
    
    def get_user_sessions_dir(self) -> Path:
        """Get user sessions directory with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_sessions = self.base_dir / "cache" / "sessions"
            if new_sessions.exists():
                return new_sessions
        
        # For backward compatibility, return base dir where user_* folders exist
        return self.base_dir
    
    def find_user_session_dirs(self) -> list[Path]:
        """Find all user session directories."""
        
        # Check new structure first
        if self.has_new_structure:
            sessions_dir = self.base_dir / "cache" / "sessions"
            if sessions_dir.exists():
                return list(sessions_dir.glob("user_*"))
        
        # Fall back to base directory
        return list(self.base_dir.glob("user_*"))
    
    def get_config_file(self, filename: str) -> Path:
        """Get configuration file path with backward compatibility."""
        
        # Try new structure first
        if self.has_new_structure:
            new_config = self.base_dir / "config" / "settings" / filename
            if new_config.exists():
                return new_config
        
        # Fall back to base directory
        legacy_config = self.base_dir / filename
        return legacy_config
    
    def get_library_storage_dir(self) -> Path:
        """Get Zotero-style storage directory (new structure only)."""
        storage_dir = self.base_dir / "library" / "storage"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir
    
    def get_paper_storage_dir(self, paper_id: str) -> Path:
        """Get storage directory for specific paper."""
        return self.get_library_storage_dir() / paper_id
    
    def create_paper_storage(self, paper_id: str) -> Path:
        """Create and return paper storage directory."""
        paper_dir = self.get_paper_storage_dir(paper_id)
        paper_dir.mkdir(parents=True, exist_ok=True)
        return paper_dir
    
    def get_download_asyncs_dir(self) -> Path:
        """Get temporary download_asyncs directory."""
        download_asyncs_dir = self.base_dir / "workspace" / "download_asyncs"
        download_asyncs_dir.mkdir(parents=True, exist_ok=True)
        return download_asyncs_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory."""
        logs_dir = self.base_dir / "workspace" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    def get_backups_dir(self) -> Path:
        """Get database backups directory."""
        backups_dir = self.base_dir / "library" / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        return backups_dir
    
    def get_collections_dir(self) -> Path:
        """Get collections directory."""
        collections_dir = self.base_dir / "library" / "collections"
        collections_dir.mkdir(parents=True, exist_ok=True)
        return collections_dir


# Global instance for easy access
scholar_paths = ScholarPaths()


# Convenience functions for backward compatibility
def get_scholar_home() -> Path:
    """Get scholar home directory."""
    return scholar_paths.base_dir

def get_pdfs_directory() -> Path:
    """Get PDFs directory (backward compatible)."""
    return scholar_paths.get_pdfs_dir()

def get_screenshots_directory() -> Path:
    """Get screenshots directory (backward compatible)."""
    return scholar_paths.get_screenshots_dir()

def get_doi_cache_directory() -> Path:
    """Get DOI cache directory (backward compatible).""" 
    return scholar_paths.get_doi_cache_dir()

def get_database_directory() -> Path:
    """Get database directory (backward compatible)."""
    return scholar_paths.get_database_dir()

def get_chrome_profiles_directory() -> Path:
    """Get Chrome profiles directory (backward compatible)."""
    return scholar_paths.get_chrome_profiles_dir()


if __name__ == "__main__":
    # Test the path resolution system
    print("🧪 Testing ScholarPaths")
    
    paths = ScholarPaths()
    
    print(f"📁 Has new structure: {paths.has_new_structure}")
    print(f"📄 PDFs directory: {paths.get_pdfs_dir()}")
    print(f"📸 Screenshots directory: {paths.get_screenshots_dir()}")
    print(f"💾 DOI cache directory: {paths.get_doi_cache_dir()}")
    print(f"🗄️  Database directory: {paths.get_database_dir()}")
    print(f"🌐 Chrome profiles directory: {paths.get_chrome_profiles_dir()}")
    print(f"📋 Translators directory: {paths.get_translators_dir()}")
    
    # Test user sessions
    user_sessions = paths.find_user_session_dirs()
    print(f"👤 User sessions found: {len(user_sessions)}")
    
    # Test new structure directories
    print(f"📚 Library storage: {paths.get_library_storage_dir()}")
    print(f"⬇️  Downloads directory: {paths.get_download_asyncs_dir()}")
    print(f"📝 Logs directory: {paths.get_logs_dir()}")
    
    print("✅ ScholarPaths test complete")