#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:02:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_ArxivSearchEngine.py
# ----------------------------------------

"""
arXiv search engine implementation for SciTeX Scholar.

This module provides search functionality through the arXiv API
for preprint papers in physics, mathematics, computer science, and other fields.
"""

from scitex import logging
import xml.etree.ElementTree as ET
from typing import List, Optional

import aiohttp

from .._BaseSearchEngine import BaseSearchEngine
from ..._Paper import Paper
from ....errors import SearchError

logger = logging.getLogger(__name__)


class ArxivSearchEngine(BaseSearchEngine):
    """arXiv search engine using the arXiv API."""
    
    def __init__(self):
        """Initialize arXiv search engine."""
        super().__init__(name="arxiv", rate_limit=0.5)
        self.base_url = "http://export.arxiv.org/api/query"
    
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search arXiv for papers.
        
        Parameters
        ----------
        query : str
            Search query
        limit : int
            Maximum number of results
        **kwargs : dict
            Additional parameters (currently unused for arXiv)
            
        Returns
        -------
        List[Paper]
            List of papers from arXiv
        """
        await self._rate_limit_async()
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        papers = self._parse_xml(xml_data)
                    else:
                        logger.error(f"arXiv search failed: {response.status}")
                        raise SearchError(query, "arxiv", f"HTTP {response.status}")
                        
        except SearchError:
            raise
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            raise SearchError(query, "arxiv", str(e))
        
        return papers
    
    def _parse_xml(self, xml_data: str) -> List[Paper]:
        """Parse arXiv XML response into Paper objects.
        
        Parameters
        ----------
        xml_data : str
            XML response from arXiv API
            
        Returns
        -------
        List[Paper]
            Parsed Paper objects
        """
        papers = []
        
        try:
            # Parse XML with namespace
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                try:
                    # Extract title
                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text.strip() if title_elem is not None else ''
                    
                    # Extract authors
                    authors = []
                    for author_elem in entry.findall('atom:author', ns):
                        name_elem = author_elem.find('atom:name', ns)
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text)
                    
                    # Extract abstract
                    summary_elem = entry.find('atom:summary', ns)
                    abstract = summary_elem.text.strip() if summary_elem is not None else ''
                    
                    # Extract year from published date
                    published_elem = entry.find('atom:published', ns)
                    year = None
                    if published_elem is not None and published_elem.text:
                        year = published_elem.text[:4]
                    
                    # Extract arXiv ID and create PDF URL
                    id_elem = entry.find('atom:id', ns)
                    arxiv_id = None
                    pdf_url = None
                    if id_elem is not None and id_elem.text:
                        # Extract ID from URL (format: http://arxiv.org/abs/1234.5678)
                        arxiv_id = id_elem.text.split('/')[-1]
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    # Extract categories as keywords
                    keywords = []
                    for cat_elem in entry.findall('atom:category', ns):
                        term = cat_elem.get('term')
                        if term:
                            keywords.append(term)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        source='arxiv',
                        year=year,
                        arxiv_id=arxiv_id,
                        keywords=keywords,
                        pdf_url=pdf_url,
                        metadata={
                            'arxiv_categories': keywords,
                            'arxiv_url': f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None
                        }
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse arXiv entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse arXiv XML: {e}")
        
        return papers


# EOF