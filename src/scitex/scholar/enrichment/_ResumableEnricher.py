#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:28:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_ResumableEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_ResumableEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Resumable enrichment tracking for BibTeX files."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from scitex import logging

logger = logging.getLogger(__name__)


class ResumableEnricher:
    """Tracks enrichment progress to allow resuming interrupted operations.
    
    Creates a .progress.json file alongside the BibTeX file to track:
    - Which papers have been processed
    - Which enrichment steps completed for each paper
    - Timestamps and statistics
    
    Similar to rsync's approach but simpler.
    """
    
    def __init__(self, bibtex_path: Path):
        """Initialize resumable enricher for a BibTeX file.
        
        Args:
            bibtex_path: Path to the BibTeX file being enriched
        """
        self.bibtex_path = Path(bibtex_path)
        self.progress_file = self.bibtex_path.with_suffix('.bib.progress.json')
        self.progress_data = self._load_progress()
        self._start_time = time.time()
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load existing progress data or create new."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Resuming from previous progress: {self.progress_file}")
                return data
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
                
        # Create new progress data
        return {
            "version": 1,
            "bibtex_file": str(self.bibtex_path),
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completed": False,
            "papers_processed": {},  # paper_id -> enrichment status
            "statistics": {
                "total_papers": 0,
                "processed": 0,
                "enriched_doi": 0,
                "enriched_impact_factor": 0,
                "enriched_citations": 0,
                "enriched_abstract": 0,
                "errors": 0
            }
        }
    
    def _save_progress(self):
        """Save current progress to disk."""
        self.progress_data["last_updated"] = datetime.now().isoformat()
        
        # Write to temp file first then rename (atomic on most systems)
        temp_file = self.progress_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            temp_file.replace(self.progress_file)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
            if temp_file.exists():
                temp_file.unlink()
    
    def set_total_papers(self, count: int):
        """Set the total number of papers to process."""
        self.progress_data["statistics"]["total_papers"] = count
        self._save_progress()
    
    def is_paper_processed(self, paper_id: str) -> bool:
        """Check if a paper has already been processed."""
        return paper_id in self.progress_data["papers_processed"]
    
    def get_processed_papers(self) -> Set[str]:
        """Get set of all processed paper IDs."""
        return set(self.progress_data["papers_processed"].keys())
    
    def mark_paper_started(self, paper_id: str):
        """Mark a paper as started processing."""
        if paper_id not in self.progress_data["papers_processed"]:
            self.progress_data["papers_processed"][paper_id] = {
                "started_at": datetime.now().isoformat(),
                "completed": False,
                "enrichments": {}
            }
    
    def mark_enrichment_complete(self, paper_id: str, enrichment_type: str, 
                                success: bool = True, value: Any = None):
        """Mark a specific enrichment as complete for a paper.
        
        Args:
            paper_id: Identifier for the paper
            enrichment_type: Type of enrichment (doi, impact_factor, citations, abstract)
            success: Whether enrichment succeeded
            value: The enriched value (optional)
        """
        if paper_id not in self.progress_data["papers_processed"]:
            self.mark_paper_started(paper_id)
            
        paper_data = self.progress_data["papers_processed"][paper_id]
        paper_data["enrichments"][enrichment_type] = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "value": value if success else None
        }
        
        # Update statistics
        if success and enrichment_type == "doi":
            self.progress_data["statistics"]["enriched_doi"] += 1
        elif success and enrichment_type == "impact_factor":
            self.progress_data["statistics"]["enriched_impact_factor"] += 1
        elif success and enrichment_type == "citations":
            self.progress_data["statistics"]["enriched_citations"] += 1
        elif success and enrichment_type == "abstract":
            self.progress_data["statistics"]["enriched_abstract"] += 1
            
        self._save_progress()
    
    def mark_paper_complete(self, paper_id: str, success: bool = True):
        """Mark a paper as fully processed."""
        if paper_id in self.progress_data["papers_processed"]:
            self.progress_data["papers_processed"][paper_id]["completed"] = success
            self.progress_data["papers_processed"][paper_id]["completed_at"] = datetime.now().isoformat()
            
            self.progress_data["statistics"]["processed"] += 1
            if not success:
                self.progress_data["statistics"]["errors"] += 1
                
            self._save_progress()
    
    def mark_all_complete(self):
        """Mark the entire enrichment process as complete."""
        self.progress_data["completed"] = True
        self.progress_data["completed_at"] = datetime.now().isoformat()
        self.progress_data["duration_seconds"] = time.time() - self._start_time
        self._save_progress()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the enrichment progress."""
        stats = self.progress_data["statistics"]
        total = stats["total_papers"]
        processed = stats["processed"]
        
        return {
            "total_papers": total,
            "processed": processed,
            "remaining": total - processed,
            "progress_percent": (processed / total * 100) if total > 0 else 0,
            "enriched": {
                "doi": stats["enriched_doi"],
                "impact_factor": stats["enriched_impact_factor"],
                "citations": stats["enriched_citations"],
                "abstract": stats["enriched_abstract"]
            },
            "errors": stats["errors"]
        }
    
    def cleanup(self):
        """Remove progress file after successful completion."""
        if self.progress_file.exists():
            self.progress_file.unlink()
            logger.info("Removed progress tracking file")


# EOF