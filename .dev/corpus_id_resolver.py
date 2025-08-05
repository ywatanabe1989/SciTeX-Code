#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 09:00:00 (ywatanabe)"
# File: ./.dev/corpus_id_resolver.py
# ----------------------------------------
"""
Specialized CorpusId to DOI resolution utility.

This script targets the two remaining unresolved CorpusId papers:
- CorpusId:263829747 - Statistical Inference for Modulation Index in Phase-Amplitude Coupling
- CorpusId:263786486 - Complex network modelling of EEG band coupling in dyslexia
"""

import requests
import time
from typing import Optional, Dict, Any
import json

from scitex.logging import getLogger
logger = getLogger(__name__)

class CorpusIdResolver:
    """Specialized resolver for Semantic Scholar CorpusId to DOI conversion."""
    
    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"SciTeX/1.0 (mailto:{self.email})"
        })
    
    def resolve_corpus_id(self, corpus_id: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a CorpusId to DOI and metadata using Semantic Scholar API.
        
        Args:
            corpus_id: The CorpusId (e.g., "263829747")
            
        Returns:
            Dictionary with DOI and metadata if found, None otherwise
        """
        # Clean the corpus_id if it has the full URL format
        if "CorpusId:" in corpus_id:
            corpus_id = corpus_id.split("CorpusId:")[-1]
        
        logger.info(f"Resolving CorpusId: {corpus_id}")
        
        # Method 1: Direct CorpusId lookup
        url = f"{self.base_url}/paper/CorpusId:{corpus_id}"
        params = {
            "fields": "title,year,externalIds,authors,abstract,venue,citationCount"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved data for CorpusId: {corpus_id}")
                
                # Extract DOI from externalIds
                external_ids = data.get("externalIds", {})
                doi = external_ids.get("DOI")
                
                if doi:
                    logger.info(f"Found DOI: {doi}")
                else:
                    logger.warning(f"No DOI found for CorpusId: {corpus_id}")
                
                # Extract authors
                authors = []
                for author in data.get("authors", []):
                    if author.get("name"):
                        authors.append(author["name"])
                
                result = {
                    "corpus_id": corpus_id,
                    "doi": doi,
                    "title": data.get("title"),
                    "year": data.get("year"),
                    "journal": data.get("venue"),
                    "authors": authors,
                    "abstract": data.get("abstract"),
                    "citation_count": data.get("citationCount"),
                    "external_ids": external_ids
                }
                
                return result
                
            elif response.status_code == 404:
                logger.warning(f"CorpusId not found: {corpus_id}")
                return None
            elif response.status_code == 429:
                logger.warning("Rate limited by Semantic Scholar")
                time.sleep(5)
                return None
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving CorpusId {corpus_id}: {e}")
            return None
    
    def find_alternative_doi(self, title: str, authors: list, year: int) -> Optional[str]:
        """
        Try alternative methods to find DOI using title/author/year.
        This uses CrossRef, arXiv, and other identifiers from Semantic Scholar.
        """
        logger.info(f"Searching alternative sources for: {title}")
        
        # Method 2: Search by title in Semantic Scholar
        url = f"{self.base_url}/paper/search"
        params = {
            "query": title,
            "fields": "title,year,externalIds,authors",
            "limit": 10
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get("data", [])
                
                for paper in papers:
                    paper_title = paper.get("title", "")
                    paper_year = paper.get("year")
                    
                    # Check if this is likely the same paper
                    if (self._title_similarity(title, paper_title) > 0.8 and
                        paper_year and abs(paper_year - year) <= 1):
                        
                        external_ids = paper.get("externalIds", {})
                        doi = external_ids.get("DOI")
                        
                        if doi:
                            logger.info(f"Found alternative DOI: {doi}")
                            return doi
                            
                        # Check for arXiv
                        arxiv_id = external_ids.get("ArXiv")
                        if arxiv_id:
                            logger.info(f"Found arXiv ID: {arxiv_id}")
                            # Could convert arXiv to DOI if needed
                            
        except Exception as e:
            logger.error(f"Error in alternative DOI search: {e}")
        
        return None
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Simple title similarity check."""
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Simple word overlap ratio
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


def main():
    """Test the CorpusId resolver on the two target papers."""
    
    resolver = CorpusIdResolver()
    
    # Target CorpusIds
    target_papers = [
        {
            "corpus_id": "263829747",
            "title": "Statistical Inference for Modulation Index in Phase-Amplitude Coupling",
            "authors": ["Marco Pinto-Orellana", "H. Ombao", "Beth A. Lopour"],
            "year": 2023
        },
        {
            "corpus_id": "263786486", 
            "title": "Complex network modelling of EEG band coupling in dyslexia",
            "authors": ["N. Gallego-Molina"],
            "year": 2021
        }
    ]
    
    results = []
    
    for paper in target_papers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {paper['title']}")
        logger.info(f"CorpusId: {paper['corpus_id']}")
        
        # Try direct CorpusId resolution
        result = resolver.resolve_corpus_id(paper['corpus_id'])
        
        if result and result.get('doi'):
            logger.info(f"SUCCESS: Found DOI {result['doi']}")
            results.append(result)
        else:
            logger.warning("Direct CorpusId resolution failed")
            
            # Try alternative methods
            alt_doi = resolver.find_alternative_doi(
                paper['title'], 
                paper['authors'], 
                paper['year']
            )
            
            if alt_doi:
                logger.info(f"SUCCESS (alternative): Found DOI {alt_doi}")
                result = result or {}
                result['doi'] = alt_doi
                result['corpus_id'] = paper['corpus_id']
                results.append(result)
            else:
                logger.error("All resolution methods failed")
                results.append({
                    "corpus_id": paper['corpus_id'],
                    "title": paper['title'],
                    "status": "FAILED"
                })
        
        # Rate limiting
        time.sleep(1)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("RESOLUTION SUMMARY")
    logger.info(f"{'='*60}")
    
    for result in results:
        corpus_id = result.get('corpus_id', 'Unknown')
        doi = result.get('doi', 'NOT FOUND')
        status = "SUCCESS" if doi != 'NOT FOUND' else "FAILED"
        
        logger.info(f"CorpusId {corpus_id}: {status}")
        if doi != 'NOT FOUND':
            logger.info(f"  DOI: {doi}")
        logger.info("")
    
    # Save results
    output_file = "/home/ywatanabe/proj/SciTeX-Code/.dev/corpus_id_resolution_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    main()