#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 13:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/migrate_pdfs_to_master.py
# ----------------------------------------
"""
Migrate PDFs from old project/pdfs directories to MASTER storage architecture.

This script:
1. Moves PDFs from project/pdfs/ to MASTER/8DIGITID/
2. Creates proper Author-Year-Journal symlinks
3. Updates metadata.json files

Usage:
    python -m scitex.scholar.utils.migrate_pdfs_to_master --project neurovista
"""

import argparse
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from scitex import logging
from scitex.scholar.core.Scholar import Scholar
from scitex.scholar.core.Paper import Paper

logger = logging.getLogger(__name__)


def migrate_project_pdfs(project_name: str, dry_run: bool = False):
    """Migrate PDFs from project/pdfs to MASTER storage.

    Args:
        project_name: Name of project to migrate
        dry_run: If True, only show what would be done
    """
    library_dir = Path.home() / ".scitex/scholar/library"
    project_dir = library_dir / project_name
    pdfs_dir = project_dir / "pdfs"
    master_dir = library_dir / "MASTER"

    if not pdfs_dir.exists():
        logger.info(f"No pdfs directory found at {pdfs_dir}")
        return

    logger.info(f"Migrating PDFs from {pdfs_dir}")
    if dry_run:
        logger.warning("DRY RUN - No changes will be made")

    # Initialize Scholar for enrichment
    scholar = Scholar(project=project_name)

    # Process each PDF
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDFs to migrate")

    for pdf_path in pdf_files:
        # Extract DOI from filename (format: 10.xxxx_xxxx.pdf)
        filename = pdf_path.stem
        doi = filename.replace("_", "/", 1)  # First underscore is /

        logger.info(f"\nProcessing: {filename}")
        logger.info(f"  DOI: {doi}")

        # Generate paper ID from DOI
        paper_id = hashlib.md5(doi.encode()).hexdigest()[:8].upper()

        # Create MASTER directory
        storage_path = master_dir / paper_id
        if not dry_run:
            storage_path.mkdir(parents=True, exist_ok=True)

        # Try to get metadata for readable name
        readable_name = None
        try:
            # Create Paper and enrich it using public methods
            from scitex.scholar.core.Papers import Papers
            paper = Paper(doi=doi)
            papers = Papers([paper])
            enriched = scholar.enrich_papers(papers)
            if enriched and len(enriched) > 0:
                paper = enriched[0]

            # Generate readable name
            first_author = "Unknown"
            if paper.authors and len(paper.authors) > 0:
                author_parts = paper.authors[0].split()
                if len(author_parts) > 1:
                    first_author = author_parts[-1]
                else:
                    first_author = author_parts[0]

            year_str = str(paper.year) if paper.year else "Unknown"

            journal_clean = "Unknown"
            if paper.journal:
                journal_clean = "".join(
                    c for c in paper.journal
                    if c.isalnum() or c in " "
                ).replace(" ", "")
                if not journal_clean:
                    journal_clean = "Unknown"

            readable_name = f"{first_author}-{year_str}-{journal_clean}"
            logger.success(f"  Generated name: {readable_name}")

        except Exception as e:
            logger.warning(f"  Could not enrich metadata: {e}")
            readable_name = f"DOI_{doi.replace('/', '_').replace(':', '_')}"

        # Move PDF to MASTER
        master_pdf_path = storage_path / f"{readable_name}.pdf"

        if not dry_run:
            if master_pdf_path.exists():
                logger.warning(f"  PDF already exists in MASTER: {master_pdf_path}")
            else:
                shutil.copy2(pdf_path, master_pdf_path)
                logger.success(f"  Copied to MASTER: {master_pdf_path}")

        # Create/update metadata.json
        metadata_file = storage_path / "metadata.json"
        if not dry_run:
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {
                    "doi": doi,
                    "scitex_id": paper_id,
                    "created_at": datetime.now().isoformat(),
                    "created_by": "Migration Script"
                }

            # Add PDF information
            metadata["pdf_path"] = f"MASTER/{paper_id}/{readable_name}.pdf"
            metadata["pdf_migrated_at"] = datetime.now().isoformat()
            metadata["pdf_size_bytes"] = pdf_path.stat().st_size
            metadata["updated_at"] = datetime.now().isoformat()

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info("  Updated metadata.json")

        # Create project symlink
        project_link = project_dir / readable_name

        if not dry_run:
            # Remove old DOI-based symlinks if they exist
            old_link = project_dir / f"DOI_{doi.replace('/', '_').replace(':', '_')}"
            if old_link.exists() and old_link.is_symlink():
                old_link.unlink()
                logger.info(f"  Removed old symlink: {old_link.name}")

            if not project_link.exists():
                project_link.symlink_to(f"../MASTER/{paper_id}")
                logger.success(f"  Created symlink: {readable_name} -> ../MASTER/{paper_id}")
            else:
                logger.info(f"  Symlink already exists: {readable_name}")

    # After migration, optionally remove the pdfs directory
    if not dry_run:
        logger.info(f"\nMigration complete! Old PDFs are still in {pdfs_dir}")
        logger.info("To remove the old pdfs directory, run:")
        logger.info(f"  rm -rf {pdfs_dir}")
    else:
        logger.info("\nDry run complete. Run without --dry-run to perform migration")


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate PDFs to MASTER storage architecture"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name to migrate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    if args.debug:
        logging.set_level(logging.DEBUG)

    migrate_project_pdfs(args.project, args.dry_run)


if __name__ == "__main__":
    main()

# EOF