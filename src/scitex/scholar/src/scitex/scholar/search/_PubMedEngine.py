#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:11:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_PubMedEngine.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/search/_PubMedEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PubMed search engine implementation.

This module provides search functionality for PubMed/MEDLINE database.
"""

"""Imports"""
import asyncio
from scitex import logging
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus
import aiohttp

from ._BaseSearchEngine import BaseSearchEngine
from .._Paper import Paper
from ...errors import SearchError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class PubMedEngine(BaseSearchEngine):
    """PubMed search engine implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize PubMed search engine.
        
        Args:
            api_key: NCBI API key for increased rate limits
        """
        super().__init__(api_key)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.rate_limit = 0.34 if not api_key else 0.1  # 3/sec without key, 10/sec with key
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
        Search PubMed for papers.
        
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
        
        # Build date range if specified
        date_range = ""
        if year_min or year_max:
            min_year = year_min or 1900
            max_year = year_max or 2100
            date_range = f"&mindate={min_year}/01/01&maxdate={max_year}/12/31"
        
        # Search for IDs first
        search_url = f"{self.base_url}/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json',
            'usehistory': 'y'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(search_url, params=search_params) as response:
                    if response.status != 200:
                        raise SearchError(f"PubMed search failed: {response.status}")
                    
                    search_data = await response.json()
                    
                if 'error' in search_data:
                    raise SearchError(f"PubMed error: {search_data['error']}")
                    
                id_list = search_data.get('esearchresult', {}).get('idlist', [])
                if not id_list:
                    return []
                    
                # Fetch details for found IDs
                webenv = search_data['esearchresult'].get('webenv')
                query_key = search_data['esearchresult'].get('querykey')
                
                fetch_url = f"{self.base_url}/efetch.fcgi"
                fetch_params = {
                    'db': 'pubmed',
                    'query_key': query_key,
                    'WebEnv': webenv,
                    'retmode': 'xml',
                    'retmax': limit
                }
                
                if self.api_key:
                    fetch_params['api_key'] = self.api_key
                    
                async with session.get(fetch_url, params=fetch_params) as response:
                    if response.status != 200:
                        raise SearchError(f"PubMed fetch failed: {response.status}")
                        
                    xml_data = await response.text()
                    
            except Exception as e:
                logger.error(f"PubMed search error: {e}")
                raise SearchError(f"PubMed search failed: {str(e)}")
                
        # Parse XML results
        return self._parse_pubmed_xml(xml_data)
        
    async def get_paper_by_id(
        self,
        paper_id: str,
        id_type: str = "pmid"
    ) -> Optional[Paper]:
        """
        Get a paper by its PubMed ID.
        
        Args:
            paper_id: The PubMed ID
            id_type: Type of ID (pmid or doi)
            
        Returns:
            Paper object or None
        """
        if id_type not in ["pmid", "doi"]:
            return None
            
        await self._rate_limit_async()
        
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': paper_id,
            'retmode': 'xml'
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(fetch_url, params=params) as response:
                    if response.status != 200:
                        return None
                        
                    xml_data = await response.text()
                    papers = self._parse_pubmed_xml(xml_data)
                    return papers[0] if papers else None
                    
            except Exception as e:
                logger.error(f"PubMed fetch error: {e}")
                return None
                
    def supports_field_search(self) -> bool:
        """PubMed supports field-specific searches."""
        return True
        
    def get_rate_limit(self) -> Dict[str, int]:
        """Get rate limit information."""
        if self.api_key:
            return {"requests_per_second": 10}
        else:
            return {"requests_per_second": 3}
            
    async def _rate_limit_async(self):
        """Enforce rate limiting."""
        import time
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()
        
    def _parse_pubmed_xml(self, xml_data: str) -> List[Paper]:
        """Parse PubMed XML response into Paper objects."""
        papers = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    paper = self._parse_single_article(article)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing PubMed article: {e}")
                    continue
                    
        except ET.ParseError as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            
        return papers
        
    def _parse_single_article(self, article: ET.Element) -> Optional[Paper]:
        """Parse a single PubMed article."""
        medline = article.find('.//MedlineCitation')
        if medline is None:
            return None
            
        # Extract basic info
        pmid = medline.findtext('.//PMID', '')
        
        article_elem = medline.find('.//Article')
        if article_elem is None:
            return None
            
        title = article_elem.findtext('.//ArticleTitle', '')
        abstract_elem = article_elem.find('.//Abstract/AbstractText')
        abstract = abstract_elem.text if abstract_elem is not None else ''
        
        # Extract authors
        authors = []
        for author in article_elem.findall('.//Author'):
            last_name = author.findtext('LastName', '')
            first_name = author.findtext('ForeName', '')
            if last_name:
                authors.append(f"{last_name}, {first_name}".strip(', '))
                
        # Extract journal info
        journal_elem = article_elem.find('.//Journal')
        journal = ''
        if journal_elem is not None:
            journal = journal_elem.findtext('.//Title', '')
            
        # Extract year
        year = None
        pub_date = article_elem.find('.//Journal/JournalIssue/PubDate')
        if pub_date is not None:
            year_text = pub_date.findtext('Year')
            if year_text:
                try:
                    year = int(year_text)
                except ValueError:
                    pass
                    
        # Extract DOI
        doi = ''
        for id_elem in article.findall('.//PubmedData/ArticleIdList/ArticleId'):
            if id_elem.get('IdType') == 'doi':
                doi = id_elem.text or ''
                break
                
        # Create Paper object
        paper = Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            year=year,
            journal=journal,
            doi=doi,
            source='pubmed'
        )
        
        # Add PubMed ID to metadata
        paper.metadata['pmid'] = pmid
        
        return paper

# EOF