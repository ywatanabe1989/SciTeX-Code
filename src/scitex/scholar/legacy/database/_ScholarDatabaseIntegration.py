#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 17:58:22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/database/_ScholarDatabaseIntegration.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/database/_ScholarDatabaseIntegration.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-08-01 14:20:00"
# Author: Claude

"""
Integration layer for Scholar workflow with database.

This module provides seamless integration between the Scholar workflow
(tasks 1-8) and the database organization system (task 9).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging

from scitex.scholar.core import Paper
from ..download import SmartPDFDownloader
from ..utils import PDFContentValidator, PDFQualityAnalyzer
from ._DatabaseEntry import DatabaseEntry
from .core._PaperDatabase import PaperDatabase

logger = logging.getLogger(__name__)


class ScholarDatabaseIntegration:
    """Integrate Scholar workflow with database."""

    def __init__(self, database_dir: Optional[Path] = None):
        """
        Initialize database integration.

        Args:
            database_dir: Database directory path
        """
        self.database = PaperDatabase(database_dir)
        self.validator = PDFContentValidator()
        self.analyzer = PDFQualityAnalyzer()

        # Workflow state tracking
        self.workflow_state_file = (
            self.database.database_dir / "workflow_state.json"
        )
        self.workflow_state = self._load_workflow_state()

    def _load_workflow_state(self) -> Dict[str, Any]:
        """Load workflow state."""
        if self.workflow_state_file.exists():
            try:
                with open(self.workflow_state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load workflow state: {e}")

        return {
            "bibtex_loaded": {},
            "dois_resolved": {},
            "urls_resolved": {},
            "metadata_enriched": {},
            "pdfs_download": {},
            "pdfs_validated": {},
            "database_entries": {},
        }

    def _save_workflow_state(self):
        """Save workflow state."""
        try:
            with open(self.workflow_state_file, "w") as f:
                json.dump(self.workflow_state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workflow state: {e}")

    async def process_bibtex_workflow(
        self,
        bibtex_path: Path,
        download_pdf_asyncs: bool = True,
        validate_pdfs: bool = True,
    ) -> Dict[str, Any]:
        """
        Process complete workflow from BibTeX to database.

        Args:
            bibtex_path: Path to BibTeX file
            download_pdf_asyncs: Whether to download PDFs
            validate_pdfs: Whether to validate PDFs

        Returns:
            Dict with processing results
        """
        import bibtexparser

        results = {
            "total_entries": 0,
            "database_added": 0,
            "pdfs_download": 0,
            "pdfs_validated": 0,
            "errors": [],
        }

        # Load BibTeX
        logger.info(f"Loading BibTeX from: {bibtex_path}")
        with open(bibtex_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        results["total_entries"] = len(bib_db.entries)

        # Process each entry
        for bib_entry in bib_db.entries:
            try:
                # Convert to Paper object
                paper = self._bibtex_to_paper(bib_entry)

                # Create database entry
                db_entry = self._paper_to_database_entry(paper, bib_entry)

                # Add to database
                entry_id = self.database.add_entry(db_entry)
                results["database_added"] += 1

                # Download PDF if requested
                if download_pdf_asyncs and paper.doi:
                    pdf_path = await self._download_pdf_async_for_entry(
                        entry_id, paper
                    )
                    if pdf_path:
                        results["pdfs_download"] += 1

                        # Validate PDF if requested
                        if validate_pdfs:
                            validation = self._validate_pdf_for_entry(
                                entry_id, pdf_path, paper
                            )
                            if validation["valid"]:
                                results["pdfs_validated"] += 1

            except Exception as e:
                logger.error(
                    f"Error processing entry {bib_entry.get('ID', 'unknown')}: {e}"
                )
                results["errors"].append(
                    {"entry": bib_entry.get("ID", "unknown"), "error": str(e)}
                )

        # Save workflow state
        self._save_workflow_state()

        return results

    def _bibtex_to_paper(self, bib_entry: Dict[str, str]) -> Paper:
        """Convert BibTeX entry to Paper object."""
        return Paper(
            title=bib_entry.get("title", "").strip("{}"),
            authors=bib_entry.get("author", "").split(" and "),
            year=(
                int(bib_entry.get("year", 0))
                if bib_entry.get("year", "").isdigit()
                else None
            ),
            journal=bib_entry.get("journal"),
            venue=bib_entry.get("booktitle"),
            doi=bib_entry.get("doi"),
            url=bib_entry.get("url"),
            abstract=bib_entry.get("abstract"),
            keywords=(
                bib_entry.get("keywords", "").split(";")
                if bib_entry.get("keywords")
                else []
            ),
        )

    def _paper_to_database_entry(
        self, paper: Paper, bib_entry: Dict[str, str]
    ) -> DatabaseEntry:
        """Convert Paper to DatabaseEntry."""
        # Extract additional metadata
        metadata = {
            "citation_count": getattr(paper, "citation_count", None),
            "pmid": getattr(paper, "pmid", None),
            "semantic_scholar_id": getattr(paper, "semantic_scholar_id", None),
            "metadata_sources": getattr(paper, "metadata_sources", None),
            "enriched_date": getattr(paper, "enriched_date", None),
            "bibtex_key": bib_entry.get("ID"),
        }

        return DatabaseEntry(
            title=paper.title,
            authors=paper.authors,
            year=paper.year,
            journal=paper.journal or paper.venue,
            doi=paper.doi,
            abstract=paper.abstract,
            keywords=paper.keywords if hasattr(paper, "keywords") else [],
            url=paper.url,
            metadata=metadata,
        )

    async def _download_pdf_async_for_entry(
        self, entry_id: str, paper: Paper
    ) -> Optional[Path]:
        """Download PDF for database entry."""
        try:
            # Get entry
            entry = self.database.get_entry(entry_id)
            if not entry:
                return None

            # Check if PDF already exists
            if entry.pdf_path and Path(entry.pdf_path).exists():
                logger.info(f"PDF already exists for {entry_id}")
                return Path(entry.pdf_path)

            # Download PDF
            downloader = SmartPDFDownloader()
            success, pdf_path = await downloader.download_single(paper)

            if success and pdf_path:
                # Move to database directory
                target_path = self._organize_pdf(entry, pdf_path)

                # Update database
                entry.pdf_path = str(target_path)
                entry.pdf_hash = self.database._calculate_pdf_hash(target_path)
                entry.download_date = datetime.now()
                self.database.update_entry(entry_id, entry)

                return target_path

        except Exception as e:
            logger.error(f"Failed to download PDF for {entry_id}: {e}")

        return None

    def _organize_pdf(self, entry: DatabaseEntry, source_path: Path) -> Path:
        """Organize PDF in database directory structure."""
        # Create directory structure: year/journal/filename
        year_dir = self.database.pdfs_dir / str(entry.year or "unknown")
        journal_dir = year_dir / (entry.journal or "unknown").replace("/", "_")
        journal_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        first_author = (
            entry.authors[0].split(",")[0].split()[-1]
            if entry.authors
            else "Unknown"
        )
        filename = (
            f"{first_author}_{entry.year or '0000'}_{entry.entry_id}.pdf"
        )
        target_path = journal_dir / filename

        # Move file
        import shutil

        shutil.move(str(source_path), str(target_path))

        return target_path

    def _validate_pdf_for_entry(
        self, entry_id: str, pdf_path: Path, paper: Paper
    ) -> Dict[str, Any]:
        """Validate PDF and update database."""
        try:
            # Get entry
            entry = self.database.get_entry(entry_id)
            if not entry:
                return {"valid": False, "reason": "Entry not found"}

            # Validate PDF
            validation = self.validator.validate_pdf(pdf_path, paper)

            # Analyze quality
            quality = self.analyzer.analyze_pdf_quality(pdf_path)

            # Update database
            entry.validation_status = (
                "valid" if validation["valid"] else "invalid"
            )
            entry.validation_reason = validation["reason"]
            entry.quality_score = quality.get("quality_score", 0)
            entry.page_count = quality.get("page_count", 0)
            entry.validated_at = datetime.now()

            # Extract sections if valid
            if validation["valid"] and "sections" in quality:
                entry.sections = quality["sections"]

            self.database.update_entry(entry_id, entry)

            return validation

        except Exception as e:
            logger.error(f"Failed to validate PDF for {entry_id}: {e}")
            return {"valid": False, "reason": str(e)}

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of workflow progress."""
        # Get database statistics
        db_stats = self.database.get_statistics()

        # Count workflow progress
        workflow_stats = {
            "bibtex_entries": len(
                self.workflow_state.get("bibtex_loaded", {})
            ),
            "dois_resolved": len(self.workflow_state.get("dois_resolved", {})),
            "urls_resolved": len(self.workflow_state.get("urls_resolved", {})),
            "metadata_enriched": len(
                self.workflow_state.get("metadata_enriched", {})
            ),
            "pdfs_download": len(
                self.workflow_state.get("pdfs_download", {})
            ),
            "pdfs_validated": len(
                self.workflow_state.get("pdfs_validated", {})
            ),
        }

        # Combine
        return {
            "database": db_stats,
            "workflow": workflow_stats,
            "last_updated": datetime.now().isoformat(),
        }

    def export_validated_papers(
        self, output_path: Path, format: str = "bibtex"
    ):
        """Export validated papers to file."""
        # Get validated entries
        validated_entries = self.database.search_entries(
            filters={"validation_status": "valid"}
        )

        if format == "bibtex":
            self._export_to_bibtex(validated_entries, output_path)
        elif format == "json":
            self._export_to_json(validated_entries, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(
            f"Exported {len(validated_entries)} validated papers to {output_path}"
        )

    def _export_to_bibtex(
        self, entries: List[DatabaseEntry], output_path: Path
    ):
        """Export entries to BibTeX."""
        import bibtexparser
        from bibtexparser.bibdatabase import BibDatabase
        from bibtexparser.bwriter import BibTexWriter

        db = BibDatabase()

        for entry in entries:
            bib_entry = {
                "ENTRYTYPE": "article",
                "ID": entry.metadata.get("bibtex_key", entry.entry_id),
                "title": entry.title,
                "author": " and ".join(entry.authors),
                "year": str(entry.year) if entry.year else "",
                "journal": entry.journal or "",
            }

            if entry.doi:
                bib_entry["doi"] = entry.doi
            if entry.abstract:
                bib_entry["abstract"] = entry.abstract
            if entry.keywords:
                bib_entry["keywords"] = "; ".join(entry.keywords)
            if entry.url:
                bib_entry["url"] = entry.url

            db.entries.append(bib_entry)

        writer = BibTexWriter()
        with open(output_path, "w") as f:
            f.write(writer.write(db))

    def _export_to_json(self, entries: List[DatabaseEntry], output_path: Path):
        """Export entries to JSON."""
        data = []

        for entry in entries:
            entry_dict = entry.to_dict()
            # Add validation info
            entry_dict["validation"] = {
                "status": entry.validation_status,
                "reason": entry.validation_reason,
                "quality_score": entry.quality_score,
                "validated_at": (
                    entry.validated_at.isoformat()
                    if entry.validated_at
                    else None
                ),
            }
            data.append(entry_dict)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

# EOF
