#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:13:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_ArxivEngine.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/search/_ArxivEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
arXiv search engine implementation.

This module provides search functionality for arXiv preprint repository.
"""

"""Imports"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
from urllib.parse import quote
import aiohttp
import re

from ._BaseSearchEngine import BaseSearchEngine
from .._Paper import Paper
from ...errors import SearchError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class ArxivEngine(BaseSearchEngine):
    """arXiv search engine implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize arXiv search engine.
        
        Args:
            api_key: Not used for arXiv (kept for interface compatibility)
        """
        super().__init__(api_key)
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limit = 0.5  # Be respectful to arXiv
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
        Search arXiv for papers.
        
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
        
        # Build search query
        search_query = self._build_query(query, year_min, year_max)
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': limit,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        raise SearchError(f"arXiv search failed: {response.status}")
                        
                    xml_data = await response.text()
                    
            except aiohttp.ClientError as e:
                logger.error(f"arXiv request error: {e}")
                raise SearchError(f"arXiv request failed: {str(e)}")
                
        return self._parse_arxiv_xml(xml_data)
        
    async def get_paper_by_id(
        self,
        paper_id: str,
        id_type: str = "arxiv"
    ) -> Optional[Paper]:
        """
        Get a paper by its arXiv ID.
        
        Args:
            paper_id: The arXiv ID
            id_type: Type of ID (arxiv or doi)
            
        Returns:
            Paper object or None
        """
        if id_type != "arxiv":
            return None
            
        await self._rate_limit_async()
        
        # Clean arXiv ID
        arxiv_id = paper_id.replace('arXiv:', '').strip()
        
        params = {
            'id_list': arxiv_id,
            'max_results': 1
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        return None
                        
                    xml_data = await response.text()
                    papers = self._parse_arxiv_xml(xml_data)
                    return papers[0] if papers else None
                    
            except Exception as e:
                logger.error(f"arXiv fetch error: {e}")
                return None
                
    def supports_field_search(self) -> bool:
        """arXiv supports field-specific searches."""
        return True
        
    def get_rate_limit(self) -> Dict[str, int]:
        """Get rate limit information."""
        return {"requests_per_second": 2}
        
    async def _rate_limit_async(self):
        """Enforce rate limiting."""
        import time
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()
        
    def _build_query(
        self,
        query: str,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None
    ) -> str:
        """Build arXiv search query with date filters."""
        # Basic query
        search_terms = []
        
        # Check if it's a field-specific search
        if ':' in query:
            search_terms.append(query)
        else:
            # Search in title and abstract
            search_terms.append(f'all:{query}')
            
        # Add date range if specified
        if year_min or year_max:
            # arXiv uses submittedDate in YYYYMMDD format
            if year_min:
                search_terms.append(f'submittedDate:[{year_min}0101 TO *]')
            if year_max:
                search_terms.append(f'submittedDate:[* TO {year_max}1231]')
                
        return ' AND '.join(search_terms)
        
    def _parse_arxiv_xml(self, xml_data: str) -> List[Paper]:
        """Parse arXiv XML response into Paper objects."""
        papers = []
        
        try:
            # Parse XML with namespace handling
            root = ET.fromstring(xml_data)
            
            # Define namespaces
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            for entry in root.findall('atom:entry', ns):
                try:
                    paper = self._parse_single_entry(entry, ns)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing arXiv entry: {e}")
                    continue
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing arXiv XML: {e}")
            
        return papers
        
    def _parse_single_entry(self, entry: ET.Element, ns: Dict[str, str]) -> Optional[Paper]:
        """Parse a single arXiv entry."""
        # Extract basic info
        title = entry.findtext('atom:title', '', ns).strip()
        if not title:
            return None
            
        abstract = entry.findtext('atom:summary', '', ns).strip()
        
        # Extract authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.findtext('atom:name', '', ns).strip()
            if name:
                authors.append(name)
                
        # Extract arXiv ID from id URL
        id_url = entry.findtext('atom:id', '', ns)
        arxiv_id = ''
        if id_url:
            match = re.search(r'arxiv.org/abs/(.+)$', id_url)
            if match:
                arxiv_id = match.group(1)
                
        # Extract publication date
        published = entry.findtext('atom:published', '', ns)
        year = None
        if published:
            try:
                year = int(published[:4])
            except (ValueError, IndexError):
                pass
                
        # Extract categories
        categories = []
        for category in entry.findall('arxiv:primary_category', ns):
            term = category.get('term')
            if term:
                categories.append(term)
                
        # Extract DOI if available
        doi = ''
        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'doi':
                doi_url = link.get('href', '')
                match = re.search(r'doi.org/(.+)$', doi_url)
                if match:
                    doi = match.group(1)
                    break
                    
        # Create Paper object
        paper = Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            journal='arXiv',
            doi=doi,
            source='arxiv'
        )
        
        # Add metadata
        paper.metadata['arxiv_id'] = arxiv_id
        paper.metadata['categories'] = categories
        paper.metadata['url'] = f"https://arxiv.org/abs/{arxiv_id}"
        paper.metadata['pdf_url'] = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        return paper

# EOF