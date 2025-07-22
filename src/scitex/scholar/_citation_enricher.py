#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/_citation_enricher.py

"""
Citation count enricher for papers without citation data.

This module provides functionality to enrich papers (especially from PubMed)
with citation counts by cross-referencing with other databases.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from ._core import Paper

logger = logging.getLogger(__name__)


class CitationEnricher:
    """
    Enriches papers with citation counts from multiple sources.
    
    Useful for PubMed papers which don't include citation data.
    """
    
    def __init__(self, semantic_scholar_api_key: Optional[str] = None):
        """Initialize citation enricher."""
        self.semantic_scholar_api_key = semantic_scholar_api_key
        
    def enrich_citations(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich papers with citation counts.
        
        Args:
            papers: List of papers to enrich
            
        Returns:
            Same list with citation counts added where possible
        """
        # Run async enrichment
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._enrich_citations_async(papers))
    
    async def _enrich_citations_async(self, papers: List[Paper]) -> List[Paper]:
        """Async implementation of citation enrichment."""
        enriched_count = 0
        
        for paper in papers:
            # Skip if already has citation count
            if paper.citation_count is not None:
                continue
            
            # Try CrossRef first if DOI is available
            if paper.doi:
                citation_count, source = self._get_citation_count_crossref(paper)
                if citation_count is not None:
                    paper.citation_count = citation_count
                    paper.citation_count_source = source
                    paper.metadata['citation_count_source'] = source
                    enriched_count += 1
                    logger.debug(f"Added citation count {citation_count} (from {source}) to: {paper.title[:50]}...")
                    continue
                
            # Try to get citation count from Semantic Scholar
            citation_count = await self._get_citation_count_s2(paper)
            
            if citation_count is not None:
                paper.citation_count = citation_count
                paper.citation_count_source = "Semantic Scholar"
                paper.metadata['citation_count_source'] = "Semantic Scholar"
                enriched_count += 1
                logger.debug(f"Added citation count {citation_count} (from Semantic Scholar) to: {paper.title[:50]}...")
        
        logger.info(f"Enriched {enriched_count}/{len(papers)} papers with citation counts")
        return papers
    
    def _get_citation_count_crossref(self, paper: Paper) -> tuple[Optional[int], Optional[str]]:
        """Get citation count from CrossRef."""
        try:
            # Import here to avoid circular dependency
            from ..web import get_crossref_metrics
            
            if not paper.doi:
                return None, None
                
            metrics = get_crossref_metrics(paper.doi)
            if metrics and 'citations' in metrics:
                return metrics['citations'], "CrossRef"
            
            return None, None
            
        except Exception as e:
            logger.debug(f"CrossRef lookup failed for DOI {paper.doi}: {e}")
            return None, None
    
    async def _get_citation_count_s2(self, paper: Paper) -> Optional[int]:
        """Get citation count from Semantic Scholar."""
        # Import here to avoid circular dependency
        from ._search import SemanticScholarEngine
        
        # Use DOI or title for lookup
        query = None
        if paper.doi:
            query = f"doi:{paper.doi}"
        elif paper.title:
            query = paper.title
        else:
            return None
        
        try:
            # Create Semantic Scholar engine
            semantic_scholar_engine = SemanticScholarEngine(api_key=self.semantic_scholar_api_key)
            
            # Search for the paper
            results = await semantic_scholar_engine.search(query, limit=3)
            
            # Find best match
            for result in results:
                # Check if titles match (fuzzy match)
                if self._titles_match(paper.title, result.title):
                    return result.citation_count
                    
                # Check if DOIs match
                if paper.doi and result.doi and paper.doi.lower() == result.doi.lower():
                    return result.citation_count
            
        except Exception as e:
            logger.debug(f"Failed to get citation count for '{paper.title[:50]}...': {e}")
        
        return None
    
    def _titles_match(self, title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles match using fuzzy matching."""
        if not title1 or not title2:
            return False
            
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Exact match
        if t1 == t2:
            return True
        
        # Use difflib for fuzzy matching
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, t1, t2).ratio()
        
        return similarity >= threshold


def enrich_with_citations(papers: List[Paper], semantic_scholar_api_key: Optional[str] = None) -> List[Paper]:
    """
    Convenience function to enrich papers with citation counts.
    
    Args:
        papers: List of papers to enrich
        semantic_scholar_api_key: Optional Semantic Scholar API key
        
    Returns:
        Papers with citation counts added
    """
    enricher = CitationEnricher(semantic_scholar_api_key=semantic_scholar_api_key)
    return enricher.enrich_citations(papers)