#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 11:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/PaperIO.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/PaperIO.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Provides simple IO interface for Paper objects
  - Handles save/load/check operations for Paper data in MASTER directory
  - Each Paper gets structured directory: MASTER/{8-digit-ID}/
  - Supports incremental data addition (check → process → save pattern)
  - All operations work with Paper object fields

Dependencies:
  - packages:
    - pydantic
    - scitex

IO:
  - input-files:
    - library/MASTER/{paper_id}/metadata.json
    - library/MASTER/{paper_id}/main.pdf
    - library/downloads/{UUID} (for PDF import)

  - output-files:
    - library/MASTER/{paper_id}/metadata.json
    - library/MASTER/{paper_id}/main.pdf
    - library/MASTER/{paper_id}/content.txt
    - library/MASTER/{paper_id}/tables.json
    - library/MASTER/{paper_id}/images/
    - library/MASTER/{paper_id}/screenshots/
"""

"""Imports"""
import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.core import Paper

logger = logging.getLogger(__name__)


class PaperIO:
    """Simple IO interface for Paper objects.

    Handles all file operations for a Paper in its MASTER directory.
    """

    def __init__(self, paper: Paper, base_dir: Optional[Path] = None):
        """Initialize PaperIO for a Paper.

        Args:
            paper: Paper object to manage
            base_dir: Base directory (default: ~/.scitex/scholar/library/MASTER)
        """
        self.paper = paper
        self.name = self.__class__.__name__

        if base_dir is None:
            from scitex.scholar import ScholarConfig
            config = ScholarConfig()
            base_dir = config.get_library_master_dir()

        # Get paper ID from container
        paper_id = paper.container.library_id
        if not paper_id:
            raise ValueError("Paper must have container.library_id set")

        self.paper_dir = Path(base_dir) / paper_id
        self.paper_dir.mkdir(parents=True, exist_ok=True)

    # ========================================
    # Path Getters
    # ========================================
    def get_metadata_path(self) -> Path:
        """Get path to metadata.json"""
        return self.paper_dir / "metadata.json"

    def get_pdf_path(self) -> Path:
        """Get path to main.pdf"""
        return self.paper_dir / "main.pdf"

    def get_text_path(self) -> Path:
        """Get path to content.txt"""
        return self.paper_dir / "content.txt"

    def get_tables_path(self) -> Path:
        """Get path to tables.json"""
        return self.paper_dir / "tables.json"

    def get_images_dir(self) -> Path:
        """Get path to images/ directory"""
        images_dir = self.paper_dir / "images"
        images_dir.mkdir(exist_ok=True)
        return images_dir

    def get_screenshots_dir(self) -> Path:
        """Get path to screenshots/ directory"""
        screenshots_dir = self.paper_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        return screenshots_dir

    def get_entry_name_for_project(self) -> str:
        """Generate entry/symlink name using PathManager format.

        Returns formatted name like:
        PDF-3s_CC-000113_IF-010_2017_Baldassano_Brain
        """
        from scitex.scholar import ScholarConfig

        config = ScholarConfig()

        # Determine PDF status
        pdf_status = "3s" if self.has_pdf() else "0p"

        # Extract metadata
        citation_count = self.paper.metadata.citation_count.total or 0
        impact_factor = int(self.paper.metadata.publication.impact_factor or 0)
        year = self.paper.metadata.basic.year or 0
        first_author = (
            self.paper.metadata.basic.authors[0].split()[-1]
            if self.paper.metadata.basic.authors
            else "Unknown"
        )
        journal_name = (
            self.paper.metadata.publication.short_journal
            or self.paper.metadata.publication.journal
            or "Unknown"
        )

        # Use PathManager to format
        return config.path_manager.get_library_project_entry_dirname(
            pdf_state=pdf_status,
            citation_count=citation_count,
            impact_factor_of_the_journal=impact_factor,
            year=year,
            first_author=first_author,
            journal_name=journal_name,
        )

    # ========================================
    # Check Methods
    # ========================================
    def has_metadata(self) -> bool:
        """Check if metadata.json exists"""
        return self.get_metadata_path().exists()

    def has_pdf(self) -> bool:
        """Check if main.pdf exists"""
        return self.get_pdf_path().exists()

    def has_content(self) -> bool:
        """Check if content.txt exists"""
        return self.get_text_path().exists()

    def has_tables(self) -> bool:
        """Check if tables.json exists"""
        return self.get_tables_path().exists()

    # ========================================
    # Save Methods
    # ========================================
    def save_metadata(self) -> Path:
        """Save Paper metadata to metadata.json

        Returns:
            Path to saved metadata.json
        """
        path = self.get_metadata_path()
        with open(path, 'w') as f:
            json.dump(self.paper.to_dict(), f, indent=2)
        logger.info(f"{self.name}: Saved metadata: {path}")
        return path

    def save_pdf(self, pdf_path: Path) -> Path:
        """Copy PDF to paper directory as main.pdf

        Args:
            pdf_path: Source PDF file path

        Returns:
            Path to main.pdf in paper directory
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        dest = self.get_pdf_path()
        shutil.copy2(pdf_path, dest)

        # Update paper object
        self.paper.metadata.path.pdfs = [str(dest)]
        self.paper.container.pdf_size_bytes = dest.stat().st_size

        logger.info(f"{self.name}: Saved PDF: {dest}")
        return dest

    def save_text(self, text: str) -> Path:
        """Save extracted text to content.txt

        Args:
            text: Extracted text content

        Returns:
            Path to content.txt
        """
        path = self.get_text_path()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"{self.name}: Saved text: {path}")
        return path

    def save_tables(self, tables: List[Any]) -> Path:
        """Save extracted tables to tables.json

        Args:
            tables: List of table data

        Returns:
            Path to tables.json
        """
        path = self.get_tables_path()
        with open(path, 'w') as f:
            json.dump(tables, f, indent=2)
        logger.info(f"{self.name}: Saved {len(tables)} tables: {path}")
        return path

    def save_image(self, image_data: bytes, filename: str) -> Path:
        """Save extracted image to images/ directory

        Args:
            image_data: Image bytes
            filename: Image filename (e.g., "fig1.png")

        Returns:
            Path to saved image
        """
        images_dir = self.get_images_dir()
        path = images_dir / filename
        with open(path, 'wb') as f:
            f.write(image_data)
        logger.info(f"{self.name}: Saved image: {path}")
        return path

    # ========================================
    # Load Methods
    # ========================================
    def load_metadata(self) -> Paper:
        """Load Paper from metadata.json and update internal reference.

        Returns:
            Paper object
        """
        path = self.get_metadata_path()
        if not path.exists():
            raise FileNotFoundError(f"Metadata not found: {path}")

        with open(path, 'r') as f:
            data = json.load(f)

        paper = Paper.from_dict(data)
        # Update internal reference so save_metadata() uses the loaded paper
        self.paper = paper
        logger.info(f"{self.name}: Loaded metadata: {path}")
        return paper

    def load_text(self) -> str:
        """Load extracted text from content.txt

        Returns:
            Text content
        """
        path = self.get_text_path()
        if not path.exists():
            raise FileNotFoundError(f"Text not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        logger.info(f"{self.name}: Loaded text: {path}")
        return text

    def load_tables(self) -> List[Any]:
        """Load extracted tables from tables.json

        Returns:
            List of tables
        """
        path = self.get_tables_path()
        if not path.exists():
            raise FileNotFoundError(f"Tables not found: {path}")

        with open(path, 'r') as f:
            tables = json.load(f)
        logger.info(f"{self.name}: Loaded {len(tables)} tables: {path}")
        return tables

    # ========================================
    # Utility Methods
    # ========================================
    def get_all_files(self) -> Dict[str, bool]:
        """Get status of all expected files

        Returns:
            Dictionary of filename: exists
        """
        return {
            "metadata.json": self.has_metadata(),
            "main.pdf": self.has_pdf(),
            "content.txt": self.has_content(),
            "tables.json": self.has_tables(),
            "images/": self.get_images_dir().exists(),
            "screenshots/": self.get_screenshots_dir().exists(),
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"PaperIO({self.paper.container.library_id}, {self.paper_dir})"


def main(args):
    """Demo: PaperIO usage with worker pattern"""
    from scitex.scholar.core import Paper

    logger.info("PaperIO Demo - Worker Pattern")

    # Create paper
    paper = Paper()
    paper.metadata.id.doi = "10.1212/WNL.0000000000200348"
    paper.metadata.id.doi_engines = ["demo"]
    paper.container.library_id = "A1B2C3D4"

    logger.info(f"Paper DOI: {paper.metadata.id.doi}")
    logger.info(f"Library ID: {paper.container.library_id}")

    # Initialize IO
    io = PaperIO(paper)
    logger.info(f"Paper directory: {io.paper_dir}")

    # Worker 1: Metadata
    if not io.has_metadata():
        paper.metadata.basic.title = "Demo Paper"
        paper.metadata.basic.title_engines = ["demo"]
        io.save_metadata()
        logger.success("Metadata saved")
    else:
        logger.info("Metadata exists, loading...")
        paper = io.load_metadata()

    # Worker 2: PDF
    if not io.has_pdf():
        logger.info("No PDF found (would download here)")
    else:
        logger.success(f"PDF exists: {io.get_pdf_path().stat().st_size / 1e6:.2f} MB")

    # Status
    status = io.get_all_files()
    logger.info("File status:")
    for filename, exists in status.items():
        logger.info(f"  {'✓' if exists else '✗'} {filename}")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PaperIO - Simple IO interface for Paper objects"
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF

