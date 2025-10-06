#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_EnhancedStorageManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Enhanced storage manager that preserves original filenames.

Storage structure:
- storage/ABCD1234/original-filename-from-journal.pdf
- storage/ABCD1234/screenshots/20250801_141500-login-page.jpg
- storage-human-readable/Smith-2023-Nature -> ../storage/ABCD1234
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import hashlib

from scitex import logging

logger = logging.getLogger(__name__)

# Try to import PIL for image conversion
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.debug("Pillow not available - screenshots will be saved as PNG")


class EnhancedStorageManager:
    """Manages paper storage with original filename preservation."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize storage manager.
        
        Args:
            base_dir: Base directory (default: $SCITEX_DIR/scholar/library/default)
        """
        if base_dir is None:
            scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
            base_dir = scitex_dir / "scholar" / "library" / "default"
            
        self.base_dir = Path(base_dir)
        self.storage_dir = self.base_dir / "storage"
        self.human_readable_dir = self.base_dir / "storage-human-readable"
        
        # Create directories
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.human_readable_dir.mkdir(parents=True, exist_ok=True)
        
    def store_pdf(self, storage_key: str, pdf_path: Path,
                  original_filename: Optional[str] = None,
                  pdf_url: Optional[str] = None,
                  paper_metadata: Optional[Dict] = None) -> Path:
        """Store PDF with original filename.
        
        Args:
            storage_key: 8-character unique key
            pdf_path: Path to PDF file to store
            original_filename: Original filename from journal
            pdf_url: URL where PDF was download
            paper_metadata: Paper metadata for human-readable link
            
        Returns:
            Path to stored PDF
        """
        # Create storage directory
        key_dir = self.storage_dir / storage_key
        key_dir.mkdir(exist_ok=True)
        
        # Determine filename
        if original_filename:
            # Sanitize but preserve structure
            safe_filename = self._sanitize_filename(original_filename)
            # Ensure .pdf extension
            if not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'
        else:
            safe_filename = "paper.pdf"
            
        # Copy PDF
        dest_path = key_dir / safe_filename
        shutil.copy2(pdf_path, dest_path)
        
        # Calculate hash for verification
        with open(dest_path, 'rb') as f:
            pdf_hash = hashlib.sha256(f.read()).hexdigest()
            
        # Store metadata
        metadata = {
            "storage_key": storage_key,
            "filename": safe_filename,
            "original_filename": original_filename,
            "pdf_url": pdf_url,
            "pdf_hash": pdf_hash,
            "size_bytes": dest_path.stat().st_size,
            "stored_at": datetime.now().isoformat()
        }
        
        metadata_path = key_dir / "storage_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        # Create human-readable link if metadata provided
        if paper_metadata:
            self._create_human_readable_link(storage_key, paper_metadata)
            
        logger.info(f"Stored PDF: {storage_key}/{safe_filename}")
        return dest_path
        
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename while preserving useful characters."""
        # Replace problematic characters but keep useful ones
        replacements = {
            '/': '-',
            '\\': '-',
            ':': '-',
            '*': '',
            '?': '',
            '"': '',
            '<': '',
            '>': '',
            '|': '-',
            '\n': ' ',
            '\r': ' ',
            '\t': ' '
        }
        
        result = filename
        for old, new in replacements.items():
            result = result.replace(old, new)
            
        # Collapse multiple spaces/dashes
        result = ' '.join(result.split())
        result = result.replace('--', '-')
        
        # Limit length but keep extension
        if len(result) > 255:
            base, ext = os.path.splitext(result)
            result = base[:250] + ext
            
        return result.strip()
        
    def _create_human_readable_link(self, storage_key: str, metadata: Dict):
        """Create human-readable symlink to storage directory."""
        # Generate citation name
        citation_name = self._generate_citation_name(metadata)
        
        # Source and target paths
        source = Path("../storage") / storage_key
        target = self.human_readable_dir / citation_name
        
        # Remove existing link if present
        if target.exists() or target.is_symlink():
            target.unlink()
            
        # Create symlink
        try:
            target.symlink_to(source)
            logger.debug(f"Created link: {citation_name} -> {storage_key}")
        except Exception as e:
            logger.warning(f"Failed to create symlink: {e}")
            # Fall back to junction on Windows
            if os.name == 'nt':
                self._create_windows_junction(source, target)
                
    def _generate_citation_name(self, metadata: Dict) -> str:
        """Generate AUTHOR-YEAR-SOURCE format name."""
        # Extract components
        authors = metadata.get("authors", [])
        year = metadata.get("year", "XXXX")
        journal = metadata.get("journal", "")
        
        # First author
        if authors:
            first_author = authors[0]
            # Handle "Last, First" format
            if "," in first_author:
                last_name = first_author.split(",")[0].strip()
            else:
                # Handle "First Last" format
                parts = first_author.strip().split()
                last_name = parts[-1] if parts else "Unknown"
            # Clean the name
            last_name = "".join(c for c in last_name if c.isalnum())
        else:
            last_name = "Unknown"
            
        # Source (journal/conference)
        if journal:
            # Try to extract abbreviation
            source = self._abbreviate_journal(journal)
        else:
            source = "Unknown"
            
        # Combine
        citation_name = f"{last_name}-{year}-{source}"
        
        # Ensure uniqueness by adding storage key if needed
        storage_key = metadata.get("storage_key", "")
        if storage_key:
            citation_name = f"{citation_name}-{storage_key[:4]}"
            
        return citation_name
        
    def _abbreviate_journal(self, journal: str) -> str:
        """Create journal abbreviation."""
        # Common journal abbreviations
        abbreviations = {
            "Nature": "Nature",
            "Science": "Science",
            "Cell": "Cell",
            "Physical Review Letters": "PRL",
            "Journal of Machine Learning Research": "JMLR",
            "Proceedings of the National Academy of Sciences": "PNAS",
            "IEEE Transactions on Pattern Analysis and Machine Intelligence": "IEEE-TPAMI",
            "Conference on Neural Information Processing Systems": "NeurIPS",
            "International Conference on Machine Learning": "ICML",
            "Computer Vision and Pattern Recognition": "CVPR"
        }
        
        # Check for known abbreviations
        for full_name, abbrev in abbreviations.items():
            if full_name.lower() in journal.lower():
                return abbrev
                
        # Create abbreviation from first letters of significant words
        words = journal.split()
        stop_words = {"of", "the", "and", "in", "on", "for", "to", "a", "an"}
        significant_words = [w for w in words if w.lower() not in stop_words]
        
        if len(significant_words) <= 3:
            # Use full significant words
            abbrev = "-".join(w[:8] for w in significant_words)
        else:
            # Use first letters
            abbrev = "".join(w[0].upper() for w in significant_words[:6])
            
        # Clean and limit length
        abbrev = "".join(c for c in abbrev if c.isalnum() or c == "-")
        return abbrev[:20]
        
    def get_pdf_info(self, storage_key: str) -> Optional[Dict]:
        """Get information about stored PDF.
        
        Args:
            storage_key: Storage key
            
        Returns:
            PDF metadata if found
        """
        metadata_path = self.storage_dir / storage_key / "storage_metadata.json"
        
        if not metadata_path.exists():
            return None
            
        with open(metadata_path, 'r') as f:
            return json.load(f)
            
    def list_pdfs(self, storage_key: str) -> List[str]:
        """List all PDFs in a storage directory.
        
        Args:
            storage_key: Storage key
            
        Returns:
            List of PDF filenames
        """
        key_dir = self.storage_dir / storage_key
        
        if not key_dir.exists():
            return []
            
        return [f.name for f in key_dir.glob("*.pdf")]
        
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        stats = {
            "total_keys": 0,
            "total_pdfs": 0,
            "total_size_mb": 0,
            "pdfs_with_original_names": 0,
            "human_readable_links": 0
        }
        
        # Count storage directories
        if self.storage_dir.exists():
            storage_keys = [d for d in self.storage_dir.iterdir() if d.is_dir()]
            stats["total_keys"] = len(storage_keys)
            
            for key_dir in storage_keys:
                pdfs = list(key_dir.glob("*.pdf"))
                stats["total_pdfs"] += len(pdfs)
                
                for pdf in pdfs:
                    stats["total_size_mb"] += pdf.stat().st_size / 1024 / 1024
                    
                    # Check if using original filename
                    if pdf.name != "paper.pdf":
                        stats["pdfs_with_original_names"] += 1
                        
        # Count human-readable links
        if self.human_readable_dir.exists():
            stats["human_readable_links"] = len(list(self.human_readable_dir.iterdir()))
            
        return stats
        
    def store_screenshot(self, storage_key: str, screenshot_path: Path,
                        description: str = "screenshot",
                        convert_to_jpg: bool = True,
                        quality: int = 85) -> Path:
        """Store screenshot for a paper.
        
        Args:
            storage_key: 8-character storage key
            screenshot_path: Path to screenshot file
            description: Description for the screenshot
            convert_to_jpg: Convert PNG to JPG to save space
            quality: JPG quality (1-100)
            
        Returns:
            Path to stored screenshot
        """
        # Create screenshots directory
        screenshots_dir = self.storage_dir / storage_key / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize description
        safe_description = self._sanitize_filename(description)
        safe_description = safe_description.replace(" ", "-").lower()
        
        # Determine filename and extension
        if convert_to_jpg and PILLOW_AVAILABLE and screenshot_path.suffix.lower() == ".png":
            # Convert PNG to JPG
            filename = f"{timestamp}-{safe_description}.jpg"
            dest_path = screenshots_dir / filename
            
            try:
                # Open PNG and convert to RGB (JPG doesn't support transparency)
                with Image.open(screenshot_path) as img:
                    # Convert RGBA to RGB with white background
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                        
                    # Save as JPG with specified quality
                    img.save(dest_path, 'JPEG', quality=quality, optimize=True)
                    
                logger.info(f"Converted screenshot to JPG: {filename} (quality={quality})")
                
            except Exception as e:
                logger.warning(f"Failed to convert to JPG: {e}, saving as PNG")
                # Fall back to PNG
                filename = f"{timestamp}-{safe_description}.png"
                dest_path = screenshots_dir / filename
                shutil.copy2(screenshot_path, dest_path)
        else:
            # Keep original format
            extension = screenshot_path.suffix.lower() or ".png"
            filename = f"{timestamp}-{safe_description}{extension}"
            dest_path = screenshots_dir / filename
            shutil.copy2(screenshot_path, dest_path)
            
        # Store screenshot metadata
        metadata = {
            "filename": filename,
            "timestamp": timestamp,
            "description": description,
            "size_bytes": dest_path.stat().st_size,
            "format": dest_path.suffix[1:].upper()
        }
        
        # Update screenshots log
        screenshots_log_path = screenshots_dir / "screenshots.json"
        if screenshots_log_path.exists():
            with open(screenshots_log_path, 'r') as f:
                screenshots_log = json.load(f)
        else:
            screenshots_log = {"screenshots": []}
            
        screenshots_log["screenshots"].append(metadata)
        
        with open(screenshots_log_path, 'w') as f:
            json.dump(screenshots_log, f, indent=2)
            
        logger.info(f"Stored screenshot: {storage_key}/screenshots/{filename}")
        return dest_path
        
    def list_screenshots(self, storage_key: str) -> List[Dict]:
        """List all screenshots for a paper.
        
        Args:
            storage_key: Storage key
            
        Returns:
            List of screenshot metadata
        """
        screenshots_log_path = self.storage_dir / storage_key / "screenshots" / "screenshots.json"
        
        if not screenshots_log_path.exists():
            return []
            
        with open(screenshots_log_path, 'r') as f:
            data = json.load(f)
            return data.get("screenshots", [])
            
    def clean_old_screenshots(self, storage_key: str, keep_last: int = 5) -> int:
        """Clean old screenshots, keeping only the most recent ones.
        
        Args:
            storage_key: Storage key
            keep_last: Number of screenshots to keep
            
        Returns:
            Number of screenshots deleted
        """
        screenshots_dir = self.storage_dir / storage_key / "screenshots"
        if not screenshots_dir.exists():
            return 0
            
        # Get all screenshots
        screenshots = self.list_screenshots(storage_key)
        
        if len(screenshots) <= keep_last:
            return 0
            
        # Sort by timestamp (newest first)
        screenshots.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Delete old screenshots
        deleted = 0
        screenshots_to_keep = screenshots[:keep_last]
        screenshots_to_delete = screenshots[keep_last:]
        
        for screenshot in screenshots_to_delete:
            screenshot_path = screenshots_dir / screenshot["filename"]
            if screenshot_path.exists():
                screenshot_path.unlink()
                deleted += 1
                
        # Update log
        screenshots_log_path = screenshots_dir / "screenshots.json"
        with open(screenshots_log_path, 'w') as f:
            json.dump({"screenshots": screenshots_to_keep}, f, indent=2)
            
        logger.info(f"Cleaned {deleted} old screenshots from {storage_key}")
        return deleted
        
    def get_latest_screenshot(self, storage_key: str, 
                            description_filter: Optional[str] = None) -> Optional[Path]:
        """Get path to latest screenshot.
        
        Args:
            storage_key: Storage key
            description_filter: Optional filter by description
            
        Returns:
            Path to latest screenshot if found
        """
        screenshots = self.list_screenshots(storage_key)
        
        if not screenshots:
            return None
            
        # Filter by description if specified
        if description_filter:
            screenshots = [s for s in screenshots 
                          if description_filter.lower() in s["description"].lower()]
            
        if not screenshots:
            return None
            
        # Sort by timestamp and get latest
        screenshots.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = screenshots[0]
        
        screenshot_path = self.storage_dir / storage_key / "screenshots" / latest["filename"]
        return screenshot_path if screenshot_path.exists() else None
        
    def migrate_flat_storage(self):
        """Migrate from flat paper.pdf storage to original filenames."""
        logger.info("Starting storage migration...")
        
        migrated = 0
        for key_dir in self.storage_dir.iterdir():
            if not key_dir.is_dir():
                continue
                
            old_pdf = key_dir / "paper.pdf"
            if not old_pdf.exists():
                continue
                
            # Check for metadata
            metadata_path = key_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    
                # Look for original filename info
                original_filename = None
                if "pdf_url" in metadata:
                    # Try to extract from URL
                    url = metadata["pdf_url"]
                    if "/" in url:
                        potential_filename = url.split("/")[-1]
                        if potential_filename.endswith(".pdf"):
                            original_filename = potential_filename
                            
                if original_filename and original_filename != "paper.pdf":
                    # Rename file
                    safe_filename = self._sanitize_filename(original_filename)
                    new_path = key_dir / safe_filename
                    
                    if not new_path.exists():
                        old_pdf.rename(new_path)
                        logger.info(f"Migrated {key_dir.name}: paper.pdf -> {safe_filename}")
                        migrated += 1
                        
        logger.info(f"Migration complete: {migrated} files renamed")


if __name__ == "__main__":
    print("Enhanced Storage Manager")
    print("=" * 60)
    
    # Example usage
    storage = EnhancedStorageManager()
    
    print("\nComplete storage structure:")
    print("""
    storage/
    ├── ABCD1234/                                  # 8-char unique key
    │   ├── s41586-023-06312-0.pdf               # Original filename from Nature
    │   ├── storage_metadata.json                 # PDF metadata
    │   └── screenshots/                          # Download attempt screenshots
    │       ├── 20250801_141500-attempt-1-initial.jpg
    │       ├── 20250801_141502-attempt-1-login-required.jpg
    │       ├── 20250801_141510-attempt-2-initial.jpg
    │       ├── 20250801_141515-attempt-2-success.jpg
    │       └── screenshots.json                  # Screenshot log
    ├── EFGH5678/
    │   ├── 2023.acl-long.123.pdf               # Original filename from ACL
    │   ├── storage_metadata.json
    │   └── screenshots/
    │       ├── 20250801_142000-attempt-1-initial.jpg
    │       ├── 20250801_142005-attempt-1-captcha.jpg
    │       └── screenshots.json
    └── IJKL9012/
        ├── PhysRevLett.130.123456.pdf           # Original filename from PRL
        ├── storage_metadata.json
        └── screenshots/
            ├── 20250801_143000-attempt-1-initial.jpg
            ├── 20250801_143002-attempt-1-success.jpg
            └── screenshots.json
        
    storage-human-readable/
    ├── Smith-2023-Nature-ABCD -> ../storage/ABCD1234
    ├── Jones-2023-ACL-EFGH -> ../storage/EFGH5678
    └── Brown-2023-PRL-IJKL -> ../storage/IJKL9012
    """)
    
    print("\nScreenshot features:")
    print("- Automatic PNG to JPG conversion (85% quality)")
    print("- Timestamped filenames with descriptions")
    print("- Screenshot log tracking all captures")
    print("- Easy cleanup of old screenshots")
    print("- Filter by description (e.g., 'login', 'captcha', 'success')")
    
    # Get statistics
    stats = storage.get_storage_stats()
    print(f"\nStorage statistics: {stats}")

# EOF