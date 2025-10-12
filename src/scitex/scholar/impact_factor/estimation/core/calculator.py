#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 18:01:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/externals/impact_factor/src/impact_factor/core/calculator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./impact_factor/core/calculator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from scitex.logging import getLogger
from ..fetchers import OpenAlexFetcher, CrossrefFetcher, SemanticScholarFetcher
from .journal_matcher import JournalMatcher
from .cache_manager import CacheManager

logger = getLogger(__name__)


class ImpactFactorCalculator:
    """
    Legal Impact Factor Calculator using open APIs
    
    This class provides transparent, legally compliant impact factor calculations
    using publicly available data from OpenAlex, Crossref, and Semantic Scholar.
    
    The impact factor is calculated as:
    IF = Total citations in year Y to articles published in years (Y-1) and (Y-2) /
         Total number of articles published in years (Y-1) and (Y-2)
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the calculator with data fetchers and cache"""
        self.openalex = OpenAlexFetcher()
        self.crossref = CrossrefFetcher()
        self.semantic_scholar = SemanticScholarFetcher()
        self.matcher = JournalMatcher()
        self.cache = CacheManager(cache_dir)
        
    def calculate_impact_factor(
        self,
        journal_name: str,
        calculation_year: int = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Calculate impact factor for a journal
        
        Args:
            journal_name: Name of the journal
            calculation_year: Year for calculation (default: current year - 1)
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary containing impact factor and supporting data
        """
        if calculation_year is None:
            calculation_year = datetime.now().year - 1
            
        logger.info(f"Calculating impact factor for '{journal_name}' for year {calculation_year}")
        
        # Check cache first
        cache_key = f"{journal_name}_{calculation_year}"
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info("Using cached impact factor data")
                return cached_result
        
        try:
            # Step 1: Find and match journal across sources
            journal_data = self._find_journal_data(journal_name)
            if not journal_data:
                return {"error": f"Journal '{journal_name}' not found in any data source"}
            
            # Step 2: Get publication and citation data
            metrics = self._calculate_metrics(journal_data, calculation_year)
            
            # Step 3: Calculate impact factors using different methodologies
            impact_factors = self._compute_impact_factors(metrics, calculation_year)
            
            # Step 4: Compile comprehensive result
            result = {
                "journal_name": journal_name,
                "calculation_year": calculation_year,
                "calculated_at": datetime.now().isoformat(),
                "journal_data": journal_data,
                "metrics": metrics,
                "impact_factors": impact_factors,
                "data_sources": self._get_data_source_info(),
                "methodology": self._get_methodology_info()
            }
            
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, result)
                
            logger.success(f"Impact factor calculation completed for '{journal_name}'")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating impact factor: {e}")
            return {"error": str(e)}
    
    def _find_journal_data(self, journal_name: str) -> Dict:
        """Find journal data across all sources"""
        logger.info(f"Searching for journal data: {journal_name}")
        
        journal_data = {}
        
        # Search OpenAlex
        try:
            openalex_journals = self.openalex.fetch_all_journals(limit=100)
            openalex_match = self.matcher.find_best_match(journal_name, openalex_journals, 'display_name')
            if openalex_match:
                journal_data['openalex'] = openalex_match
                logger.info("Found OpenAlex match")
        except Exception as e:
            logger.warning(f"OpenAlex search failed: {e}")
        
        # Search Crossref
        try:
            crossref_journals = self.crossref.fetch_all_journals(limit=100)
            crossref_match = self.matcher.find_best_match(journal_name, crossref_journals, 'title')
            if crossref_match:
                journal_data['crossref'] = crossref_match
                logger.info("Found Crossref match")
        except Exception as e:
            logger.warning(f"Crossref search failed: {e}")
        
        # Search Semantic Scholar
        try:
            semantic_metrics = self.semantic_scholar.get_journal_metrics_from_papers(journal_name)
            if semantic_metrics:
                journal_data['semantic_scholar'] = semantic_metrics
                logger.info("Found Semantic Scholar data")
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed: {e}")
        
        return journal_data
    
    def _calculate_metrics(self, journal_data: Dict, calculation_year: int) -> Dict:
        """Calculate publication and citation metrics"""
        logger.info("Calculating publication and citation metrics")
        
        metrics = {
            "total_papers_previous_2_years": 0,
            "total_citations_to_previous_2_years": 0,
            "citations_by_year": defaultdict(int),
            "papers_by_year": defaultdict(int),
            "h_index": 0,
            "total_citations": 0,
            "data_completeness": {}
        }
        
        # Calculate from OpenAlex data
        if 'openalex' in journal_data:
            openalex_data = journal_data['openalex']
            metrics['total_citations'] += openalex_data.get('cited_by_count', 0)
            metrics['h_index'] = max(metrics['h_index'], openalex_data.get('h_index', 0) or 0)
            
            # Estimate papers for previous 2 years (approximation)
            works_count = openalex_data.get('works_count', 0)
            if works_count > 0:
                # Rough estimation: assume even distribution over years
                estimated_papers_per_year = works_count / 10  # Assume 10 years of data
                metrics['total_papers_previous_2_years'] += int(estimated_papers_per_year * 2)
            
            metrics['data_completeness']['openalex'] = True
        
        # Calculate from Semantic Scholar data
        if 'semantic_scholar' in journal_data:
            ss_data = journal_data['semantic_scholar'].get('semantic_scholar_metrics', {})
            metrics['total_citations'] += ss_data.get('total_citations', 0)
            
            paper_count = ss_data.get('paper_count', 0)
            if paper_count > 0:
                # Estimate papers for previous 2 years
                metrics['total_papers_previous_2_years'] += int(paper_count * 0.2)  # 20% assumption
                
            metrics['data_completeness']['semantic_scholar'] = True
        
        # Estimate citations to papers from previous 2 years
        # This is an approximation since we don't have year-specific data
        if metrics['total_citations'] > 0 and metrics['total_papers_previous_2_years'] > 0:
            # Assume 60% of citations are to papers from previous 2 years
            metrics['total_citations_to_previous_2_years'] = int(metrics['total_citations'] * 0.6)
        
        return metrics
    
    def _compute_impact_factors(self, metrics: Dict, calculation_year: int) -> Dict:
        """Compute various impact factor measurements"""
        logger.info("Computing impact factor measurements")
        
        impact_factors = {}
        
        # Classical Impact Factor (2-year)
        if metrics['total_papers_previous_2_years'] > 0:
            classical_if = metrics['total_citations_to_previous_2_years'] / metrics['total_papers_previous_2_years']
            impact_factors['classical_2year'] = round(classical_if, 3)
        else:
            impact_factors['classical_2year'] = 0.0
        
        # H-Index based impact indicator
        if metrics['h_index'] > 0:
            impact_factors['h_index_based'] = round(metrics['h_index'] / 10, 3)  # Normalized
        else:
            impact_factors['h_index_based'] = 0.0
        
        # Citation per paper ratio (overall)
        if metrics['total_papers_previous_2_years'] > 0:
            citation_per_paper = metrics['total_citations'] / metrics['total_papers_previous_2_years']
            impact_factors['citation_per_paper'] = round(citation_per_paper, 3)
        else:
            impact_factors['citation_per_paper'] = 0.0
        
        # Confidence score based on data availability
        confidence_factors = []
        if 'openalex' in metrics.get('data_completeness', {}):
            confidence_factors.append(0.4)
        if 'crossref' in metrics.get('data_completeness', {}):
            confidence_factors.append(0.3)
        if 'semantic_scholar' in metrics.get('data_completeness', {}):
            confidence_factors.append(0.3)
        
        impact_factors['confidence_score'] = round(sum(confidence_factors), 2)
        
        return impact_factors
    
    def _get_data_source_info(self) -> Dict:
        """Get information about data sources"""
        return {
            "openalex": {
                "name": "OpenAlex",
                "description": "Open catalog of scholarly works",
                "url": "https://openalex.org",
                "api_url": "https://api.openalex.org"
            },
            "crossref": {
                "name": "Crossref",
                "description": "Digital Object Identifier (DOI) registration agency",
                "url": "https://crossref.org",
                "api_url": "https://api.crossref.org"
            },
            "semantic_scholar": {
                "name": "Semantic Scholar",
                "description": "AI-powered research tool for scientific literature",
                "url": "https://semanticscholar.org",
                "api_url": "https://api.semanticscholar.org"
            }
        }
    
    def _get_methodology_info(self) -> Dict:
        """Get information about calculation methodology"""
        return {
            "classical_2year": {
                "description": "Standard 2-year impact factor calculation",
                "formula": "Citations in year Y to papers from years (Y-1) and (Y-2) / Papers published in years (Y-1) and (Y-2)",
                "note": "Approximated from available data"
            },
            "h_index_based": {
                "description": "H-index normalized impact indicator",
                "formula": "H-index / 10 (normalized)",
                "note": "Alternative metric based on journal's h-index"
            },
            "citation_per_paper": {
                "description": "Overall citation per paper ratio",
                "formula": "Total citations / Total papers (estimated for 2-year window)",
                "note": "Broader view of journal impact"
            },
            "data_limitations": [
                "Year-specific citation data not always available",
                "Estimates used for temporal distribution",
                "Results approximate true impact factors",
                "Confidence score indicates data reliability"
            ]
        }

    def batch_calculate(self, journal_names: List[str], calculation_year: int = None) -> List[Dict]:
        """Calculate impact factors for multiple journals"""
        logger.info(f"Starting batch calculation for {len(journal_names)} journals")
        
        results = []
        for i, journal_name in enumerate(journal_names):
            logger.info(f"Processing journal {i+1}/{len(journal_names)}: {journal_name}")
            result = self.calculate_impact_factor(journal_name, calculation_year)
            results.append(result)
            
            # Be polite to APIs
            time.sleep(0.5)
        
        logger.success(f"Batch calculation completed for {len(journal_names)} journals")
        return results


def main():
    """Demonstration of ImpactFactorCalculator"""
    logger.info("Starting Impact Factor Calculator demonstration")
    
    calculator = ImpactFactorCalculator()
    
    # Test journals with different impact levels
    test_journals = [
        "Nature",
        "Science", 
        "Cell",
        "PLOS ONE",
        "Scientific Reports"
    ]
    
    logger.info(f"Testing impact factor calculation for {len(test_journals)} journals")
    
    for journal in test_journals:
        logger.info(f"Calculating impact factor for: {journal}")
        logger.info("=" * 50)
        
        result = calculator.calculate_impact_factor(journal)
        
        if 'error' in result:
            logger.error(f"Error: {result['error']}")
        else:
            impact_factors = result.get('impact_factors', {})
            logger.info(f"Results for {journal}:")
            logger.info(f"  Classical 2-year IF: {impact_factors.get('classical_2year', 'N/A')}")
            logger.info(f"  H-index based: {impact_factors.get('h_index_based', 'N/A')}")
            logger.info(f"  Citation per paper: {impact_factors.get('citation_per_paper', 'N/A')}")
            logger.info(f"  Confidence score: {impact_factors.get('confidence_score', 'N/A')}")
            
            # Show data sources used
            data_sources = []
            if 'openalex' in result.get('journal_data', {}):
                data_sources.append("OpenAlex")
            if 'crossref' in result.get('journal_data', {}):
                data_sources.append("Crossref") 
            if 'semantic_scholar' in result.get('journal_data', {}):
                data_sources.append("Semantic Scholar")
            
            logger.info(f"  Data sources: {', '.join(data_sources) if data_sources else 'None'}")
            
        logger.info("")
        time.sleep(1)  # Be polite to APIs
    
    logger.success("Impact Factor Calculator demonstration completed")


if __name__ == "__main__":
    main()

# EOF