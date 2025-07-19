#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-01 23:07:00 (ywatanabe)"
# File: src/scitex/scholar/semantic_scholar_client.py

"""
Enhanced Semantic Scholar API client for comprehensive literature search.

Provides access to 200M+ papers from Semantic Scholar Academic Graph API
with citation network analysis, research trend detection, and PDF discovery.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import time
import json
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


@dataclass
class S2Paper:
    """Semantic Scholar paper data structure."""
    paperId: str
    title: str
    abstract: Optional[str]
    year: Optional[int]
    authors: List[Dict[str, Any]]
    venue: Optional[str]
    citationCount: int
    influentialCitationCount: int
    fieldsOfStudy: List[str]
    s2FieldsOfStudy: List[Dict[str, str]]
    doi: Optional[str]
    pmid: Optional[str]
    arxivId: Optional[str]
    pdf_url: Optional[str] = None
    
    @property
    def author_names(self) -> List[str]:
        """Extract author names from author objects."""
        return [author.get('name', 'Unknown') for author in self.authors if author]
    
    @property
    def has_open_access(self) -> bool:
        """Check if paper has open access PDF."""
        return bool(self.pdf_url)


class SemanticScholarClient:
    """
    Enhanced Semantic Scholar API client with comprehensive literature search capabilities.
    
    Features:
    - Access to 200M+ papers vs traditional 1M from PubMed/arXiv
    - Citation network analysis and recommendations  
    - Research trend detection over time
    - Automatic open access PDF discovery (50M+ papers)
    - Rate limiting and error handling
    - Async/await support for concurrent requests
    """
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: float = 0.1):
        """
        Initialize Semantic Scholar client.
        
        Args:
            api_key: Optional API key for higher rate limits (100 requests/second vs 1)
            rate_limit: Time between requests in seconds (default: 0.1s = 10 req/sec)
        """
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.rate_limit = rate_limit
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        
        # Standard fields for paper queries
        self.paper_fields = [
            'paperId', 'title', 'abstract', 'year', 'authors', 'venue',
            'citationCount', 'influentialCitationCount', 'fieldsOfStudy',
            's2FieldsOfStudy', 'publicationTypes', 'publicationDate',
            'journal', 'doi', 'pmid', 'arxivId', 'openAccessPdf'
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {'User-Agent': 'SciTeX-Scholar/1.0'}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_request(self):
        """Implement rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make rate-limited API request with error handling."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        await self._rate_limit_request()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limited, wait and retry once
                    logger.warning("Rate limited, waiting 2 seconds...")
                    await asyncio.sleep(2)
                    async with self.session.get(url, params=params) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=retry_response.request_info,
                                history=retry_response.history,
                                status=retry_response.status
                            )
                else:
                    response.raise_for_status()
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout for request: {url}")
            raise
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    async def search_papers(self, 
                          query: str,
                          limit: int = 20,
                          year_filter: Optional[str] = None,
                          open_access_only: bool = False,
                          fields_of_study: Optional[List[str]] = None) -> List[S2Paper]:
        """
        Search for papers using Semantic Scholar's 200M+ paper database.
        
        Args:
            query: Search query (natural language or structured)
            limit: Maximum number of results (1-100, default 20)
            year_filter: Year range like "2020-2023" or single year "2022"
            open_access_only: Only return papers with free PDFs
            fields_of_study: Filter by fields like ["Computer Science", "Medicine"]
            
        Returns:
            List of S2Paper objects with rich metadata
        """
        # Build search parameters - minimal for API compatibility
        params = {
            'query': query,
            'limit': min(limit, 100),
            'fields': 'paperId,title,abstract,year,authors,venue,citationCount,influentialCitationCount,fieldsOfStudy,doi,arxivId,openAccessPdf'
        }
        
        # Add filters
        if year_filter:
            params['year'] = year_filter
        
        if fields_of_study:
            params['fieldsOfStudy'] = ','.join(fields_of_study)
        
        if open_access_only:
            # This will be filtered after the response since API doesn't support this directly
            pass
        
        result = await self._make_request('paper/search', params)
        
        papers = []
        for paper_data in result.get('data', []):
            # Extract PDF URL from openAccessPdf
            pdf_url = None
            if paper_data.get('openAccessPdf'):
                pdf_url = paper_data['openAccessPdf'].get('url')
            
            # Skip if open access only and no PDF
            if open_access_only and not pdf_url:
                continue
            
            # Create S2Paper object
            paper = S2Paper(
                paperId=paper_data.get('paperId', ''),
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract'),
                year=paper_data.get('year'),
                authors=paper_data.get('authors', []),
                venue=paper_data.get('venue'),
                citationCount=paper_data.get('citationCount', 0),
                influentialCitationCount=paper_data.get('influentialCitationCount', 0),
                fieldsOfStudy=paper_data.get('fieldsOfStudy', []),
                s2FieldsOfStudy=paper_data.get('s2FieldsOfStudy', []),
                doi=paper_data.get('doi'),
                pmid=paper_data.get('pmid'),
                arxivId=paper_data.get('arxivId'),
                pdf_url=pdf_url
            )
            papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers for query: {query[:50]}...")
        return papers
    
    async def get_paper_citations(self, paper_id: str, limit: int = 50) -> List[S2Paper]:
        """Get papers that cite the given paper."""
        params = {
            'fields': ','.join(self.paper_fields),
            'limit': min(limit, 100)
        }
        
        result = await self._make_request(f'paper/{paper_id}/citations', params)
        
        papers = []
        for citation_data in result.get('data', []):
            citing_paper = citation_data.get('citingPaper', {})
            if citing_paper:
                paper = self._parse_paper_data(citing_paper)
                papers.append(paper)
        
        return papers
    
    async def get_paper_references(self, paper_id: str, limit: int = 50) -> List[S2Paper]:
        """Get papers referenced by the given paper."""
        params = {
            'fields': ','.join(self.paper_fields),
            'limit': min(limit, 100)
        }
        
        result = await self._make_request(f'paper/{paper_id}/references', params)
        
        papers = []
        for reference_data in result.get('data', []):
            cited_paper = reference_data.get('citedPaper', {})
            if cited_paper:
                paper = self._parse_paper_data(cited_paper)
                papers.append(paper)
        
        return papers
    
    async def get_recommendations(self, paper_id: str, limit: int = 20) -> List[S2Paper]:
        """Get recommended papers based on the given paper."""
        params = {
            'fields': ','.join(self.paper_fields),
            'limit': min(limit, 100)
        }
        
        result = await self._make_request(f'recommendations/v1/papers/forpaper/{paper_id}', params)
        
        papers = []
        for rec_data in result.get('recommendedPapers', []):
            paper = self._parse_paper_data(rec_data)
            papers.append(paper)
        
        return papers
    
    async def find_open_access_version(self, 
                                     title: str = None,
                                     doi: str = None,
                                     arxiv_id: str = None) -> Optional[str]:
        """Find open access PDF URL for a paper."""
        # Try different search strategies
        search_queries = []
        
        if doi:
            search_queries.append(f'doi:{doi}')
        if arxiv_id:
            search_queries.append(f'arxiv:{arxiv_id}')
        if title:
            # Clean title for search
            clean_title = title.replace('"', '').replace("'", "")[:100]
            search_queries.append(clean_title)
        
        for query in search_queries:
            try:
                papers = await self.search_papers(query, limit=5, open_access_only=True)
                if papers:
                    return papers[0].pdf_url
            except Exception as e:
                logger.debug(f"Open access search failed for '{query}': {e}")
                continue
        
        return None
    
    async def analyze_research_trends(self, topic: str, years: int = 5) -> Dict[str, Any]:
        """
        Analyze research trends for a topic over time.
        
        Args:
            topic: Research topic to analyze
            years: Number of years to analyze (from current year backwards)
            
        Returns:
            Dictionary with trend data including paper counts, top venues, key authors
        """
        from datetime import datetime
        current_year = datetime.now().year
        start_year = current_year - years
        
        # Get papers for each year
        yearly_data = {}
        total_papers = 0
        all_venues = {}
        all_authors = {}
        
        for year in range(start_year, current_year + 1):
            try:
                papers = await self.search_papers(
                    query=topic,
                    limit=100,
                    year_filter=str(year)
                )
                
                yearly_data[year] = {
                    'count': len(papers),
                    'avg_citations': sum(p.citationCount for p in papers) / len(papers) if papers else 0,
                    'top_papers': sorted(papers, key=lambda p: p.citationCount, reverse=True)[:3]
                }
                
                total_papers += len(papers)
                
                # Track venues and authors
                for paper in papers:
                    if paper.venue:
                        all_venues[paper.venue] = all_venues.get(paper.venue, 0) + 1
                    
                    for author in paper.author_names:
                        all_authors[author] = all_authors.get(author, 0) + 1
                
            except Exception as e:
                logger.warning(f"Failed to get trend data for {year}: {e}")
                yearly_data[year] = {'count': 0, 'avg_citations': 0, 'top_papers': []}
        
        # Compile results
        top_venues = sorted(all_venues.items(), key=lambda x: x[1], reverse=True)[:10]
        top_authors = sorted(all_authors.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'topic': topic,
            'years_analyzed': years,
            'total_papers': total_papers,
            'yearly_data': yearly_data,
            'top_venues': top_venues,
            'top_authors': top_authors,
            'trend_direction': self._calculate_trend_direction(yearly_data)
        }
    
    def _calculate_trend_direction(self, yearly_data: Dict[int, Dict]) -> str:
        """Calculate if research trend is increasing, decreasing, or stable."""
        years = sorted(yearly_data.keys())
        if len(years) < 3:
            return 'insufficient_data'
        
        # Look at paper counts over time
        counts = [yearly_data[year]['count'] for year in years]
        
        # Simple trend calculation
        early_avg = sum(counts[:len(counts)//2]) / (len(counts)//2)
        late_avg = sum(counts[len(counts)//2:]) / (len(counts) - len(counts)//2)
        
        if late_avg > early_avg * 1.2:
            return 'increasing'
        elif late_avg < early_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _parse_paper_data(self, paper_data: Dict[str, Any]) -> S2Paper:
        """Parse paper data from API response into S2Paper object."""
        pdf_url = None
        if paper_data.get('openAccessPdf'):
            pdf_url = paper_data['openAccessPdf'].get('url')
        
        return S2Paper(
            paperId=paper_data.get('paperId', ''),
            title=paper_data.get('title', ''),
            abstract=paper_data.get('abstract'),
            year=paper_data.get('year'),
            authors=paper_data.get('authors', []),
            venue=paper_data.get('venue'),
            citationCount=paper_data.get('citationCount', 0),
            influentialCitationCount=paper_data.get('influentialCitationCount', 0),
            fieldsOfStudy=paper_data.get('fieldsOfStudy', []),
            s2FieldsOfStudy=paper_data.get('s2FieldsOfStudy', []),
            doi=paper_data.get('doi'),
            pmid=paper_data.get('pmid'),
            arxivId=paper_data.get('arxivId'),
            pdf_url=pdf_url
        )


# Convenience functions for quick usage
async def search_papers(query: str, limit: int = 20, **kwargs) -> List[S2Paper]:
    """Quick paper search function."""
    async with SemanticScholarClient() as client:
        return await client.search_papers(query, limit, **kwargs)


async def get_paper_info(paper_id: str) -> Optional[S2Paper]:
    """Get detailed information for a specific paper."""
    async with SemanticScholarClient() as client:
        try:
            result = await client._make_request(f'paper/{paper_id}', {
                'fields': ','.join(client.paper_fields)
            })
            return client._parse_paper_data(result)
        except Exception as e:
            logger.error(f"Failed to get paper info: {e}")
            return None


# EOF