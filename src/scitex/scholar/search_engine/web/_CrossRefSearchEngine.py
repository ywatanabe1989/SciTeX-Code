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
from ...config import ScholarConfig

logger = logging.getLogger(__name__)


class CrossRefSearchEngine(BaseSearchEngine):
    """CrossRef search engine for academic papers."""
    
    def __init__(self, config: Optional[ScholarConfig] = None, api_key: Optional[str] = None, email: Optional[str] = None):
        super().__init__(name="crossref", rate_limit=0.5)
        
        self.config = config or ScholarConfig()
        
        # Use sophisticated config resolution: direct → config → env → default
        self.api_key = self.config.resolve(
            key="crossref_api_key",
            direct_val=api_key,
            default=None,
            type=str
        )
        
        self.email = self.config.resolve(
            key="crossref_email", 
            direct_val=email,
            default="research@example.com",
            type=str
        )
        
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
                
                # Extract comprehensive journal information  
                container_titles = item.get('container-title', [])
                short_container_titles = item.get('short-container-title', [])
                
                journal = container_titles[0] if container_titles else None
                short_journal = short_container_titles[0] if short_container_titles else None
                
                # Get ISSN (can be a list)
                issn_list = item.get('ISSN', [])
                issn = issn_list[0] if issn_list else None
                
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
                        'issn': issn,
                        'issn_list': issn_list,
                        'short_journal': short_journal,
                        'volume': item.get('volume'),
                        'issue': item.get('issue'),
                        'type': item.get('type'),
                        'score': item.get('score'),
                        'journal_source': 'crossref'
                    }
                )
                
                papers.append(paper)
                
            except Exception as e:
                logger.warning(f"Failed to parse CrossRef item: {e}")
                continue
        
        return papers

    async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
        """Fetch single paper by DOI from CrossRef."""
        try:
            # Rate limiting
            await self._rate_limit_async()
            
            # CrossRef API URL for fetching by DOI
            url = f"https://api.crossref.org/works/{identifier}"
            
            headers = {
                'User-Agent': f'SciTeX/1.0 (mailto:{self.email})'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse the single work item
                        items = [data.get('message', {})]
                        papers = self._parse_crossref_response({'message': {'items': items}})
                        return papers[0] if papers else None
                    elif response.status == 404:
                        logger.debug(f"Paper not found for identifier: {identifier}")
                        return None
                    else:
                        logger.error(f"CrossRef fetch_by_id_async failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching paper by ID {identifier}: {e}")
            return None

    async def get_citation_count_async(self, doi: str) -> Optional[int]:
        """Get citation count for DOI from CrossRef."""
        try:
            # Fetch the paper by DOI
            paper = await self.fetch_by_id_async(doi)
            return paper.citation_count if paper else None
            
        except Exception as e:
            logger.error(f"Error getting citation count for {doi}: {e}")
            return None

    async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
        """Resolve title to DOI using CrossRef search."""
        try:
            # Search for the paper by title
            search_query = title
            if year:
                search_query += f" {year}"
                
            papers = await self.search_async(search_query, limit=5)
            
            # Look for exact or close title matches
            title_lower = title.lower().strip()
            for paper in papers:
                if paper.doi and paper.title:
                    paper_title_lower = paper.title.lower().strip()
                    # Simple matching - could be improved with fuzzy matching
                    if title_lower in paper_title_lower or paper_title_lower in title_lower:
                        # If year is specified, prefer papers from that year
                        if year and paper.year and abs(paper.year - year) <= 1:
                            return paper.doi
                        elif not year:
                            return paper.doi
            
            # If no exact match but we have results, return the first DOI
            if papers and papers[0].doi:
                return papers[0].doi
                
            return None
            
        except Exception as e:
            logger.error(f"Error resolving DOI for title '{title}': {e}")
            return None


async def main():
    """Test function for CrossRefSearchEngine."""
    from scitex.scholar.config import ScholarConfig
    
    config = ScholarConfig()
    engine = CrossRefSearchEngine(config=config)
    
    print("Testing CrossRef search engine...")
    print(f"Email: {engine.email}")
    print(f"API Key: {'Set' if engine.api_key else 'Not set'}")
    
    try:
        papers = await engine.search_async("deep learning", limit=5)
        print(f"Found {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   DOI: {paper.doi}")
            print(f"   Citations: {paper.citation_count}")
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


# EOF