#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:12:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_SemanticScholarEngine.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/search/_SemanticScholarEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Semantic Scholar search engine implementation.

This module provides search functionality for Semantic Scholar API.
"""

"""Imports"""
import asyncio
from scitex import logging
from typing import List, Optional, Dict, Any
import aiohttp

from ._BaseSearchEngine import BaseSearchEngine
from .._Paper import Paper
from ...errors import SearchError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class SemanticScholarEngine(BaseSearchEngine):
    """Semantic Scholar search engine implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar search engine.
        
        Args:
            api_key: Semantic Scholar API key for increased rate limits
        """
        super().__init__(api_key)
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.rate_limit = 0.1 if api_key else 1.0  # Faster with API key
        self._last_request = 0
        
    async def search(
        self,
        query: str,
        limit: int = 20,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs
    ) -> List[Paper]:
        """
        Search Semantic Scholar for papers.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            year_min: Minimum publication year
            year_max: Maximum publication year
            **kwargs: Additional parameters
            
        Returns:
            List of Paper objects
        """
        await self._rate_limit_async()
        
        # Check if query is for a specific paper ID
        if query.startswith('CorpusId:'):
            corpus_id = query.replace('CorpusId:', '').strip()
            paper = await self._fetch_paper_by_id_async(f"CorpusId:{corpus_id}")
            return [paper] if paper else []
            
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
            
        params = {
            'query': query,
            'limit': min(limit, 100),
            'fields': 'title,authors,abstract,year,citationCount,journal,paperId,venue,fieldsOfStudy,isOpenAccess,url,tldr,doi,externalIds'
        }
        
        # Add year filters if provided
        if year_min:
            params['year'] = f"{year_min}-"
        if year_max:
            if 'year' in params:
                params['year'] = f"{year_min}-{year_max}"
            else:
                params['year'] = f"-{year_max}"
                
        url = f"{self.base_url}/paper/search"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 429:
                        raise SearchError("Semantic Scholar rate limit exceeded")
                    elif response.status != 200:
                        raise SearchError(f"Semantic Scholar search failed: {response.status}")
                        
                    data = await response.json()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Semantic Scholar request error: {e}")
                raise SearchError(f"Semantic Scholar request failed: {str(e)}")
                
        papers = []
        for item in data.get('data', []):
            paper = self._parse_paper(item)
            if paper:
                papers.append(paper)
                
        return papers
        
    async def get_paper_by_id(
        self,
        paper_id: str,
        id_type: str = "doi"
    ) -> Optional[Paper]:
        """
        Get a paper by its identifier.
        
        Args:
            paper_id: The paper identifier
            id_type: Type of ID (doi, arxiv, corpusid, etc.)
            
        Returns:
            Paper object or None
        """
        return await self._fetch_paper_by_id_async(paper_id, id_type)
        
    async def _fetch_paper_by_id_async(
        self,
        paper_id: str,
        id_type: str = "doi"
    ) -> Optional[Paper]:
        """Fetch a single paper by ID."""
        await self._rate_limit_async()
        
        # Format ID based on type
        if id_type == "doi":
            formatted_id = paper_id
        elif id_type == "arxiv":
            formatted_id = f"arXiv:{paper_id}"
        elif id_type == "corpusid":
            formatted_id = f"CorpusId:{paper_id}"
        else:
            formatted_id = paper_id
            
        url = f"{self.base_url}/paper/{formatted_id}"
        params = {
            'fields': 'title,authors,abstract,year,citationCount,journal,paperId,venue,fieldsOfStudy,isOpenAccess,url,tldr,doi,externalIds'
        }
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 404:
                        return None
                    elif response.status != 200:
                        logger.error(f"Failed to fetch paper {paper_id}: {response.status}")
                        return None
                        
                    data = await response.json()
                    return self._parse_paper(data)
                    
            except Exception as e:
                logger.error(f"Error fetching paper {paper_id}: {e}")
                return None
                
    def supports_field_search(self) -> bool:
        """Semantic Scholar supports field-specific searches."""
        return True
        
    def get_rate_limit(self) -> Dict[str, int]:
        """Get rate limit information."""
        if self.api_key:
            return {"requests_per_second": 10}
        else:
            return {"requests_per_second": 1}
            
    async def _rate_limit_async(self):
        """Enforce rate limiting."""
        import time
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()
        
    def _parse_paper(self, data: Dict[str, Any]) -> Optional[Paper]:
        """Parse Semantic Scholar API response into Paper object."""
        if not data.get('title'):
            return None
            
        # Extract authors
        authors = []
        for author in data.get('authors', []):
            name = author.get('name', '')
            if name:
                authors.append(name)
                
        # Extract year
        year = data.get('year')
        
        # Extract identifiers
        doi = data.get('doi', '')
        external_ids = data.get('externalIds', {})
        
        # Create Paper object
        paper = Paper(
            title=data.get('title', ''),
            authors=authors,
            abstract=data.get('abstract', ''),
            year=year,
            journal=data.get('journal', {}).get('name', '') or data.get('venue', ''),
            doi=doi,
            source='semantic_scholar'
        )
        
        # Add metadata
        paper.metadata['semantic_scholar_id'] = data.get('paperId', '')
        paper.metadata['citation_count'] = data.get('citationCount', 0)
        paper.metadata['is_open_access'] = data.get('isOpenAccess', False)
        paper.metadata['fields_of_study'] = data.get('fieldsOfStudy', [])
        paper.metadata['url'] = data.get('url', '')
        
        # Add external IDs
        if 'ArXiv' in external_ids:
            paper.metadata['arxiv_id'] = external_ids['ArXiv']
        if 'PubMed' in external_ids:
            paper.metadata['pmid'] = external_ids['PubMed']
            
        # Add TLDR if available
        tldr = data.get('tldr')
        if tldr and isinstance(tldr, dict):
            paper.metadata['tldr'] = tldr.get('text', '')
            
        return paper

# EOF