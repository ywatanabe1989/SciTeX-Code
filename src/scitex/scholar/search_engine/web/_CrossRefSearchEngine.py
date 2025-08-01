#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 15:35:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_CrossRefSearchEngine.py
# ----------------------------------------
from __future__ import annotations

"""
CrossRef search engine for academic papers.

This module provides search functionality using the CrossRef API.
"""

import asyncio
from scitex import logging
from typing import List, Dict, Any, Optional

import aiohttp

from .._BaseSearchEngine import BaseSearchEngine
from ..._Paper import Paper
from ....errors import SearchError

logger = logging.getLogger(__name__)


class CrossRefSearchEngine(BaseSearchEngine):
    """CrossRef search engine for academic papers."""
    
    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        super().__init__(name="crossref", rate_limit=0.5)
        self.api_key = api_key
        self.email = email or "research@example.com"
        self.base_url = "https://api.crossref.org/works"
        
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search CrossRef for papers."""
        await self._rate_limit_async()
        
        # Build query parameters
        params = {
            'query': query,
            'rows': min(limit, 1000),
            'sort': 'relevance',
            'order': 'desc'
        }
        
        # Add filters for year if provided
        filters = []
        if 'year_min' in kwargs and kwargs['year_min'] is not None:
            filters.append(f"from-pub-date:{kwargs['year_min']}")
        if 'year_max' in kwargs and kwargs['year_max'] is not None:
            filters.append(f"until-pub-date:{kwargs['year_max']}")
        
        if filters:
            params['filter'] = ','.join(filters)
        
        # Add API key if available
        if self.api_key:
            params['key'] = self.api_key
            
        # Headers with user agent
        headers = {
            'User-Agent': f'SciTeX/1.0 (mailto:{self.email})'
        }
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = self._parse_crossref_response(data)
                    else:
                        error_text = await response.text()
                        logger.error(f"CrossRef search failed: {response.status} - {error_text}")
                        raise SearchError(
                            query=query,
                            source="crossref",
                            reason=f"API returned status {response.status}"
                        )
                        
        except asyncio.TimeoutError:
            logger.error("CrossRef search timed out")
            raise SearchError(
                query=query,
                source="crossref", 
                reason="Search timed out"
            )
        except Exception as e:
            logger.error(f"CrossRef search error: {e}")
            raise SearchError(
                query=query,
                source="crossref",
                reason=str(e)
            )
        
        return papers
    
    def _parse_crossref_response(self, data: Dict[str, Any]) -> List[Paper]:
        """Parse CrossRef API response into Paper objects."""
        papers = []
        
        items = data.get('message', {}).get('items', [])
        
        for item in items:
            try:
                # Extract basic metadata
                title = ' '.join(item.get('title', ['No title']))
                
                # Authors
                authors = []
                for author in item.get('author', []):
                    given = author.get('given', '')
                    family = author.get('family', '')
                    if given and family:
                        authors.append(f"{given} {family}")
                    elif family:
                        authors.append(family)
                
                # Abstract - CrossRef doesn't always have abstracts
                abstract = item.get('abstract', '')
                
                # Year from published-print or published-online
                year = None
                published = item.get('published-print') or item.get('published-online')
                if published and 'date-parts' in published:
                    date_parts = published['date-parts']
                    if date_parts and date_parts[0]:
                        year = str(date_parts[0][0])
                
                # Journal
                journal = None
                container_title = item.get('container-title', [])
                if container_title:
                    journal = container_title[0]
                
                # DOI
                doi = item.get('DOI')
                
                # Citation count
                citation_count = item.get('is-referenced-by-count', 0)
                
                # Keywords/subjects
                keywords = item.get('subject', [])
                
                # URL
                url = item.get('URL')
                
                paper = Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    source='crossref',
                    year=year,
                    doi=doi,
                    journal=journal,
                    keywords=keywords,
                    citation_count=citation_count,
                    metadata={
                        'citation_count_source': 'CrossRef',
                        'url': url,
                        'publisher': item.get('publisher'),
                        'issn': item.get('ISSN', []),
                        'type': item.get('type'),
                        'score': item.get('score')
                    }
                )
                
                papers.append(paper)
                
            except Exception as e:
                logger.warning(f"Failed to parse CrossRef item: {e}")
                continue
        
        return papers

# EOF