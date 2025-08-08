#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 17:50:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_ProjectAwareEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_ProjectAwareEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Project-aware metadata enricher with source tracking and field preservation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging

from ._MetadataEnricher import MetadataEnricher
from ..._Paper import Paper

logger = logging.getLogger(__name__)


class ProjectAwareEnricher(MetadataEnricher):
    """Enhanced metadata enricher with project-based JSON storage."""

    def __init__(self, project_name: str = "default", config: Optional[Any] = None):
        """Initialize project-aware enricher.
        
        Args:
            project_name: Project name for organizing metadata
            config: ScholarConfig object
        """
        super().__init__(config)
        self.project_name = project_name
        
        # Set up project structure
        from ..database._LibraryManager import LibraryManager
        self.library_manager = LibraryManager()
        self.project_base = self.library_manager.library_base / self.project_name
        self.project_metadata = self.project_base / "metadata"
        self.project_metadata.mkdir(parents=True, exist_ok=True)

    def enrich_paper_with_preservation(
        self,
        paper: Paper,
        preserve_existing: bool = True,
        save_to_json: bool = True
    ) -> Paper:
        """Enrich paper with field preservation and source tracking.
        
        Args:
            paper: Paper object to enrich
            preserve_existing: Skip fields that already have values
            save_to_json: Save enriched metadata to JSON file
            
        Returns:
            Enriched Paper object
        """
        # Load existing metadata if available
        existing_metadata = self._load_existing_metadata(paper)
        
        # Track what we're going to enrich
        enrichment_plan = self._create_enrichment_plan(paper, preserve_existing)
        
        # Perform enrichment based on plan
        enriched_paper = self._execute_enrichment_plan(paper, enrichment_plan)
        
        # Save enriched metadata to JSON
        if save_to_json:
            self._save_enrichment_metadata(enriched_paper, enrichment_plan, existing_metadata)
        
        return enriched_paper

    def _load_existing_metadata(self, paper: Paper) -> Dict[str, Any]:
        """Load existing metadata for a paper if available."""
        paper_id = paper.get_identifier()
        metadata_file = self.project_metadata / f"{paper_id.replace(':', '_')}.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading existing metadata for {paper_id}: {e}")
        
        return {}

    def _create_enrichment_plan(
        self, 
        paper: Paper, 
        preserve_existing: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """Create enrichment plan based on existing fields and preferences.
        
        Returns:
            Dictionary mapping field names to enrichment actions
        """
        plan = {}
        
        # Abstract enrichment
        if not preserve_existing or not paper.abstract:
            plan["abstract"] = {
                "action": "enrich",
                "method": "doi_lookup",
                "reason": "missing" if not paper.abstract else "force_update"
            }
        else:
            plan["abstract"] = {
                "action": "skip",
                "reason": "already_exists",
                "current_value": paper.abstract[:50] + "..." if len(paper.abstract) > 50 else paper.abstract
            }
        
        # Citation count enrichment
        if not preserve_existing or paper.citation_count is None:
            plan["citation_count"] = {
                "action": "enrich",
                "method": "semantic_scholar",
                "reason": "missing" if paper.citation_count is None else "force_update"
            }
        else:
            plan["citation_count"] = {
                "action": "skip",
                "reason": "already_exists",
                "current_value": paper.citation_count
            }
        
        # Impact factor enrichment
        if not preserve_existing or paper.impact_factor is None:
            plan["impact_factor"] = {
                "action": "enrich", 
                "method": "jcr_lookup",
                "reason": "missing" if paper.impact_factor is None else "force_update"
            }
        else:
            plan["impact_factor"] = {
                "action": "skip",
                "reason": "already_exists", 
                "current_value": paper.impact_factor
            }
        
        # Journal quartile enrichment
        if not preserve_existing or not paper.journal_quartile:
            plan["journal_quartile"] = {
                "action": "enrich",
                "method": "jcr_lookup",
                "reason": "missing" if not paper.journal_quartile else "force_update"
            }
        else:
            plan["journal_quartile"] = {
                "action": "skip",
                "reason": "already_exists",
                "current_value": paper.journal_quartile
            }
        
        return plan

    def _execute_enrichment_plan(
        self, 
        paper: Paper, 
        enrichment_plan: Dict[str, Dict[str, Any]]
    ) -> Paper:
        """Execute the enrichment plan on the paper."""
        enrichment_results = {}
        
        # Abstract enrichment
        if enrichment_plan["abstract"]["action"] == "enrich":
            try:
                if paper.doi:
                    abstract = self._fetch_abstract_from_doi(paper.doi)
                    if abstract:
                        paper.update_field_with_source("abstract", abstract, "doi_crossref")
                        enrichment_results["abstract"] = {"success": True, "source": "doi_crossref"}
                    else:
                        enrichment_results["abstract"] = {"success": False, "reason": "not_found"}
                else:
                    enrichment_results["abstract"] = {"success": False, "reason": "no_doi"}
            except Exception as e:
                logger.warning(f"Abstract enrichment failed: {e}")
                enrichment_results["abstract"] = {"success": False, "error": str(e)}
        
        # Citation count enrichment
        if enrichment_plan["citation_count"]["action"] == "enrich":
            try:
                citation_count = self._fetch_citation_count(paper)
                if citation_count is not None:
                    paper.update_field_with_source("citation_count", citation_count, "semantic_scholar")
                    enrichment_results["citation_count"] = {"success": True, "source": "semantic_scholar"}
                else:
                    enrichment_results["citation_count"] = {"success": False, "reason": "not_found"}
            except Exception as e:
                logger.warning(f"Citation count enrichment failed: {e}")
                enrichment_results["citation_count"] = {"success": False, "error": str(e)}
        
        # Impact factor enrichment
        if enrichment_plan["impact_factor"]["action"] == "enrich":
            try:
                if paper.journal:
                    impact_factor, quartile = self._fetch_journal_metrics(paper.journal)
                    if impact_factor:
                        from ._MetadataEnricher import JCR_YEAR
                        paper.update_field_with_source("impact_factor", impact_factor, f"JCR_{JCR_YEAR}")
                        enrichment_results["impact_factor"] = {"success": True, "source": f"JCR_{JCR_YEAR}"}
                        
                        if quartile and enrichment_plan["journal_quartile"]["action"] == "enrich":
                            paper.update_field_with_source("journal_quartile", quartile, f"JCR_{JCR_YEAR}")
                            enrichment_results["journal_quartile"] = {"success": True, "source": f"JCR_{JCR_YEAR}"}
                    else:
                        enrichment_results["impact_factor"] = {"success": False, "reason": "journal_not_found"}
                else:
                    enrichment_results["impact_factor"] = {"success": False, "reason": "no_journal"}
            except Exception as e:
                logger.warning(f"Impact factor enrichment failed: {e}")
                enrichment_results["impact_factor"] = {"success": False, "error": str(e)}
        
        # Store enrichment results for later saving
        paper._enrichment_results = enrichment_results
        
        return paper

    def _fetch_abstract_from_doi(self, doi: str) -> Optional[str]:
        """Fetch abstract using DOI from CrossRef or other sources."""
        try:
            import requests
            
            # Try CrossRef first
            url = f"https://api.crossref.org/works/{doi}"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                work = data.get("message", {})
                abstract = work.get("abstract")
                if abstract:
                    # Clean up HTML tags if present
                    import re
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                    return abstract.strip()
                    
        except Exception as e:
            logger.debug(f"CrossRef abstract fetch failed: {e}")
        
        return None

    def _fetch_citation_count(self, paper: Paper) -> Optional[int]:
        """Fetch citation count from Semantic Scholar or other sources."""
        try:
            import requests
            
            # Use DOI if available
            if paper.doi:
                url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{paper.doi}"
                params = {"fields": "citationCount"}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("citationCount")
            
            # Fallback to title search
            if paper.title:
                url = "https://api.semanticscholar.org/graph/v1/paper/search"
                params = {
                    "query": paper.title,
                    "fields": "citationCount,title",
                    "limit": 1
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    papers = data.get("data", [])
                    if papers:
                        return papers[0].get("citationCount")
                        
        except Exception as e:
            logger.debug(f"Semantic Scholar citation fetch failed: {e}")
        
        return None

    def _fetch_journal_metrics(self, journal_name: str) -> tuple[Optional[float], Optional[str]]:
        """Fetch journal impact factor and quartile from JCR data."""
        try:
            # Use the existing MetadataEnricher logic
            impact_factor = self._get_journal_impact_factor(journal_name)
            quartile = self._get_journal_quartile(journal_name)
            return impact_factor, quartile
        except Exception as e:
            logger.debug(f"Journal metrics fetch failed: {e}")
            return None, None

    def _save_enrichment_metadata(
        self,
        paper: Paper,
        enrichment_plan: Dict[str, Dict[str, Any]],
        existing_metadata: Dict[str, Any]
    ):
        """Save enrichment metadata to JSON file."""
        paper_id = paper.get_identifier()
        safe_id = paper_id.replace(":", "_")
        metadata_file = self.project_metadata / f"{safe_id}.json"
        
        # Get enrichment results from paper
        enrichment_results = getattr(paper, '_enrichment_results', {})
        
        # Create comprehensive metadata
        metadata = {
            "paper_id": paper_id,
            "title": paper.title,
            "project": self.project_name,
            "last_enrichment": {
                "timestamp": datetime.now().isoformat(),
                "plan": enrichment_plan,
                "results": enrichment_results,
            },
            "current_fields": {
                "doi": {
                    "value": paper.doi,
                    "source": getattr(paper, "doi_source", "unknown")
                },
                "abstract": {
                    "value": paper.abstract[:100] + "..." if paper.abstract and len(paper.abstract) > 100 else paper.abstract,
                    "source": getattr(paper, "abstract_source", "unknown"),
                    "full_length": len(paper.abstract) if paper.abstract else 0
                },
                "citation_count": {
                    "value": paper.citation_count,
                    "source": getattr(paper, "citation_count_source", "unknown")
                },
                "impact_factor": {
                    "value": paper.impact_factor,
                    "source": getattr(paper, "impact_factor_source", "unknown")
                },
                "journal_quartile": {
                    "value": paper.journal_quartile,
                    "source": getattr(paper, "journal_quartile_source", "unknown")
                }
            },
            "enrichment_history": existing_metadata.get("enrichment_history", [])
        }
        
        # Add current enrichment to history
        metadata["enrichment_history"].append({
            "timestamp": datetime.now().isoformat(),
            "plan": enrichment_plan,
            "results": enrichment_results
        })
        
        # Save to file
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved enrichment metadata: {metadata_file}")

    def batch_enrich_from_metadata_files(
        self,
        preserve_existing: bool = True
    ) -> Dict[str, Any]:
        """Enrich all papers in project based on existing metadata files.
        
        Args:
            preserve_existing: Skip fields that already have values
            
        Returns:
            Summary of enrichment results
        """
        metadata_files = list(self.project_metadata.glob("*.json"))
        
        results = {
            "total_files": len(metadata_files),
            "processed": 0,
            "errors": [],
            "enrichment_summary": {
                "abstract": {"attempted": 0, "successful": 0, "skipped": 0},
                "citation_count": {"attempted": 0, "successful": 0, "skipped": 0},
                "impact_factor": {"attempted": 0, "successful": 0, "skipped": 0},
                "journal_quartile": {"attempted": 0, "successful": 0, "skipped": 0},
            }
        }
        
        for metadata_file in metadata_files:
            try:
                # Load metadata and create Paper object
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                paper = self._create_paper_from_metadata(metadata)
                if paper:
                    # Enrich the paper
                    enriched_paper = self.enrich_paper_with_preservation(
                        paper, preserve_existing=preserve_existing, save_to_json=True
                    )
                    
                    # Update summary statistics
                    self._update_enrichment_summary(results["enrichment_summary"], enriched_paper)
                    results["processed"] += 1
                    
            except Exception as e:
                error_msg = f"Error processing {metadata_file}: {str(e)}"
                logger.warning(error_msg)
                results["errors"].append(error_msg)
        
        return results

    def _create_paper_from_metadata(self, metadata: Dict[str, Any]) -> Optional[Paper]:
        """Create Paper object from stored metadata."""
        try:
            current_fields = metadata.get("current_fields", {})
            
            paper = Paper(
                title=metadata.get("title"),
                doi=current_fields.get("doi", {}).get("value"),
                abstract=current_fields.get("abstract", {}).get("value"),
                citation_count=current_fields.get("citation_count", {}).get("value"),
                impact_factor=current_fields.get("impact_factor", {}).get("value"),
                journal_quartile=current_fields.get("journal_quartile", {}).get("value"),
            )
            
            # Set source information
            for field_name, field_data in current_fields.items():
                if isinstance(field_data, dict) and "source" in field_data:
                    setattr(paper, f"{field_name}_source", field_data["source"])
            
            return paper
            
        except Exception as e:
            logger.warning(f"Error creating paper from metadata: {e}")
            return None

    def _update_enrichment_summary(
        self, 
        summary: Dict[str, Dict[str, int]], 
        paper: Paper
    ):
        """Update enrichment summary statistics."""
        enrichment_results = getattr(paper, '_enrichment_results', {})
        
        for field_name in ["abstract", "citation_count", "impact_factor", "journal_quartile"]:
            if field_name in enrichment_results:
                result = enrichment_results[field_name]
                if result.get("success"):
                    summary[field_name]["successful"] += 1
                summary[field_name]["attempted"] += 1
            else:
                summary[field_name]["skipped"] += 1


# Export
__all__ = ["ProjectAwareEnricher"]

# EOF