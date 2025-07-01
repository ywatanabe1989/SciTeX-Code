#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-01 22:25:00 (ywatanabe)"
# File: src/scitex_scholar/semantic_scholar_client.py

"""
Semantic Scholar API client for enhanced paper access and citation analysis.

This module provides comprehensive access to Semantic Scholar's Academic Graph API,
offering access to 200M+ papers with 50M+ open access PDFs.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import time
import json

logger = logging.getLogger(__name__)

@dataclass
class S2Paper:
    """Semantic Scholar paper representation with rich metadata."""
    
    paperId: str
    title: str
    authors: List[Dict[str, str]]
    year: Optional[int]
    abstract: Optional[str]
    openAccessPdf: Optional[Dict[str, str]]
    citationCount: int
    influentialCitationCount: int
    references: List[str]
    citations: List[str]
    venue: Optional[str]
    doi: Optional[str]
    arxivId: Optional[str]
    pmid: Optional[str]
    fieldsOfStudy: List[str]
    s2FieldsOfStudy: List[Dict[str, str]]
    
    @property
    def has_open_access(self) -> bool:
        """Check if paper has open access PDF."""
        return self.openAccessPdf is not None
    
    @property
    def pdf_url(self) -> Optional[str]:
        """Get PDF URL if available."""
        return self.openAccessPdf['url'] if self.openAccessPdf else None
    
    @property
    def author_names(self) -> List[str]:
        """Get list of author names."""
        return [author.get('name', '') for author in self.authors]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'paperId': self.paperId,
            'title': self.title,
            'authors': self.author_names,
            'year': self.year,
            'abstract': self.abstract,
            'doi': self.doi,
            'arxivId': self.arxivId,
            'pmid': self.pmid,
            'venue': self.venue,
            'citationCount': self.citationCount,
            'influentialCitationCount': self.influentialCitationCount,
            'fieldsOfStudy': self.fieldsOfStudy,
            'pdf_url': self.pdf_url,
            'has_open_access': self.has_open_access
        }


class SemanticScholarClient:
    """
    Client for Semantic Scholar Academic Graph API.
    
    Provides access to:
    - Paper search across 200M+ papers
    - Citation network analysis
    - Open access PDF discovery
    - Research trend analysis
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RATE_LIMIT = 100  # requests per 5 minutes for free tier
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Semantic Scholar client.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times = []
        
        # Enhanced rate limits with API key
        if api_key:
            self.RATE_LIMIT = 1000  # 1000 requests per 5 minutes with key
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement Semantic Scholar rate limiting."""
        now = time.time()
        # Remove requests older than 5 minutes
        self._request_times = [t for t in self._request_times if now - t < 300]
        
        if len(self._request_times) >= self.RATE_LIMIT:
            sleep_time = 300 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(now)
    
    async def search_papers(self, 
                          query: str,
                          limit: int = 20,
                          fields: Optional[List[str]] = None,
                          year_filter: Optional[str] = None,
                          open_access_only: bool = False,
                          venue_filter: Optional[str] = None) -> List[S2Paper]:
        """
        Search for papers using Semantic Scholar.
        
        Args:
            query: Search query
            limit: Maximum results (max 100)
            fields: Fields to return
            year_filter: Year range (e.g., "2020-2025")
            open_access_only: Only return papers with PDFs
            venue_filter: Filter by venue/journal
            
        Returns:
            List of S2Paper objects
        """
        await self._rate_limit()
        
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year',
                'openAccessPdf', 'citationCount', 'influentialCitationCount',
                'venue', 'doi', 'arxivId', 'pmid', 'fieldsOfStudy',
                's2FieldsOfStudy'
            ]
        
        params = {
            'query': query,
            'limit': min(limit, 100),  # API limit
            'fields': ','.join(fields)
        }
        
        if year_filter:
            params['year'] = year_filter
        
        if open_access_only:
            params['openAccessPdf'] = ''
        
        if venue_filter:
            params['venue'] = venue_filter
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        url = f"{self.BASE_URL}/paper/search"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 400:
                    logger.warning(f"Bad request for query: {query}. Trying simplified query.")
                    # Retry with simplified query
                    simple_params = {
                        'query': query.split()[0],  # Use first word only
                        'limit': min(limit, 100),
                        'fields': 'paperId,title,authors,year,citationCount'
                    }
                    async with self.session.get(url, params=simple_params, headers=headers) as retry_response:
                        if retry_response.status != 200:
                            logger.error(f"Retry also failed: {retry_response.status}")
                            return []
                        data = await retry_response.json()
                else:
                    response.raise_for_status()
                    data = await response.json()
                
            papers = []
            for paper_data in data.get('data', []):
                try:
                    # Handle missing fields gracefully
                    paper_data.setdefault('references', [])
                    paper_data.setdefault('citations', [])
                    paper_data.setdefault('fieldsOfStudy', [])
                    paper_data.setdefault('s2FieldsOfStudy', [])
                    
                    papers.append(S2Paper(**paper_data))
                except Exception as e:
                    logger.warning(f"Failed to parse paper: {e}")
                    continue
                    
            return papers
            
        except aiohttp.ClientError as e:
            logger.error(f"Search request failed: {e}")
            return []
    
    async def get_paper(self,
                       paper_id: str,
                       fields: Optional[List[str]] = None) -> Optional[S2Paper]:
        """
        Get details for a specific paper by ID, DOI, arxiv ID, etc.
        
        Args:
            paper_id: Paper identifier (DOI, arXiv ID, S2 paper ID, etc.)
            fields: Fields to return
            
        Returns:
            S2Paper object or None if not found
        """
        await self._rate_limit()
        
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year',
                'openAccessPdf', 'citationCount', 'influentialCitationCount',
                'references', 'citations', 'venue', 'doi', 'arxivId', 'pmid',
                'fieldsOfStudy', 's2FieldsOfStudy'
            ]
        
        params = {'fields': ','.join(fields)}
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/paper/{paper_id}"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                data = await response.json()
                
                # Handle missing fields
                data.setdefault('references', [])
                data.setdefault('citations', [])
                data.setdefault('fieldsOfStudy', [])
                data.setdefault('s2FieldsOfStudy', [])
                
                return S2Paper(**data)
                
        except aiohttp.ClientError as e:
            logger.error(f"Paper lookup failed for {paper_id}: {e}")
            return None
    
    async def get_paper_citations(self,
                                 paper_id: str,
                                 limit: int = 100,
                                 fields: Optional[List[str]] = None) -> List[S2Paper]:
        """
        Get papers that cite this paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum results
            fields: Fields to return
            
        Returns:
            List of citing papers
        """
        await self._rate_limit()
        
        if fields is None:
            fields = ['paperId', 'title', 'authors', 'year', 'openAccessPdf', 'citationCount']
        
        params = {
            'fields': ','.join(fields),
            'limit': min(limit, 1000)  # API limit
        }
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/paper/{paper_id}/citations"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                
            citations = []
            for cite_data in data.get('data', []):
                citing_paper = cite_data.get('citingPaper', {})
                if citing_paper:
                    # Handle missing fields
                    citing_paper.setdefault('references', [])
                    citing_paper.setdefault('citations', [])
                    citing_paper.setdefault('fieldsOfStudy', [])
                    citing_paper.setdefault('s2FieldsOfStudy', [])
                    
                    try:
                        citations.append(S2Paper(**citing_paper))
                    except Exception as e:
                        logger.warning(f"Failed to parse citing paper: {e}")
                        continue
                        
            return citations
            
        except aiohttp.ClientError as e:
            logger.error(f"Citations lookup failed: {e}")
            return []
    
    async def get_paper_references(self,
                                  paper_id: str,
                                  limit: int = 100,
                                  fields: Optional[List[str]] = None) -> List[S2Paper]:
        """
        Get papers referenced by this paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum results
            fields: Fields to return
            
        Returns:
            List of referenced papers
        """
        await self._rate_limit()
        
        if fields is None:
            fields = ['paperId', 'title', 'authors', 'year', 'openAccessPdf', 'citationCount']
        
        params = {
            'fields': ','.join(fields),
            'limit': min(limit, 1000)
        }
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/paper/{paper_id}/references"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                
            references = []
            for ref_data in data.get('data', []):
                cited_paper = ref_data.get('citedPaper', {})
                if cited_paper:
                    # Handle missing fields
                    cited_paper.setdefault('references', [])
                    cited_paper.setdefault('citations', [])
                    cited_paper.setdefault('fieldsOfStudy', [])
                    cited_paper.setdefault('s2FieldsOfStudy', [])
                    
                    try:
                        references.append(S2Paper(**cited_paper))
                    except Exception as e:
                        logger.warning(f"Failed to parse referenced paper: {e}")
                        continue
                        
            return references
            
        except aiohttp.ClientError as e:
            logger.error(f"References lookup failed: {e}")
            return []
    
    async def get_recommendations(self,
                                paper_id: str,
                                limit: int = 20) -> List[S2Paper]:
        """
        Get recommended papers based on a paper.
        
        Args:
            paper_id: Paper identifier
            limit: Maximum results
            
        Returns:
            List of recommended papers
        """
        await self._rate_limit()
        
        params = {
            'fields': 'paperId,title,abstract,authors,year,openAccessPdf,citationCount',
            'limit': min(limit, 500)
        }
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                
            papers = []
            for paper_data in data.get('recommendedPapers', []):
                # Handle missing fields
                paper_data.setdefault('references', [])
                paper_data.setdefault('citations', [])
                paper_data.setdefault('fieldsOfStudy', [])
                paper_data.setdefault('s2FieldsOfStudy', [])
                
                try:
                    papers.append(S2Paper(**paper_data))
                except Exception as e:
                    logger.warning(f"Failed to parse recommended paper: {e}")
                    continue
                    
            return papers
            
        except aiohttp.ClientError as e:
            logger.error(f"Recommendations lookup failed: {e}")
            return []
    
    async def find_open_access_version(self, 
                                     title: str = None,
                                     doi: str = None,
                                     arxiv_id: str = None) -> Optional[str]:
        """
        Find open access PDF URL for a paper.
        
        Args:
            title: Paper title
            doi: DOI
            arxiv_id: arXiv ID
            
        Returns:
            PDF URL if available
        """
        paper_id = None
        
        # Try different identifiers
        if doi:
            paper_id = doi
        elif arxiv_id:
            paper_id = f"arXiv:{arxiv_id}"
        elif title:
            # Search by title
            papers = await self.search_papers(
                query=title,
                limit=5,
                open_access_only=True
            )
            
            # Find best match
            for paper in papers:
                if paper.title.lower().strip() == title.lower().strip():
                    return paper.pdf_url
        
        if paper_id:
            paper = await self.get_paper(paper_id)
            if paper and paper.has_open_access:
                return paper.pdf_url
        
        return None
    
    async def analyze_research_trends(self,
                                    topic: str,
                                    years: int = 5) -> Dict[str, Any]:
        """
        Analyze research trends in a topic over time.
        
        Args:
            topic: Research topic
            years: Number of years to analyze
            
        Returns:
            Trend analysis data
        """
        current_year = datetime.now().year
        trends = {}
        
        for year in range(current_year - years, current_year + 1):
            papers = await self.search_papers(
                query=topic,
                year_filter=f"{year}-{year}",
                limit=100
            )
            
            if papers:
                avg_citations = sum(p.citationCount for p in papers) / len(papers)
                venues = [p.venue for p in papers if p.venue]
                fields = []
                for p in papers:
                    fields.extend([f['category'] for f in p.s2FieldsOfStudy])
                
                # Count top venues and fields
                venue_counts = {}
                field_counts = {}
                
                for venue in venues:
                    venue_counts[venue] = venue_counts.get(venue, 0) + 1
                
                for field in fields:
                    field_counts[field] = field_counts.get(field, 0) + 1
                
                trends[year] = {
                    'paper_count': len(papers),
                    'avg_citations': avg_citations,
                    'top_venues': sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                    'top_fields': sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                    'open_access_ratio': sum(1 for p in papers if p.has_open_access) / len(papers)
                }
            else:
                trends[year] = {
                    'paper_count': 0,
                    'avg_citations': 0,
                    'top_venues': [],
                    'top_fields': [],
                    'open_access_ratio': 0
                }
        
        return {
            'topic': topic,
            'years_analyzed': years,
            'trends': trends,
            'summary': {
                'total_papers': sum(t['paper_count'] for t in trends.values()),
                'growth_trend': self._calculate_growth_trend(trends),
                'avg_open_access': sum(t['open_access_ratio'] for t in trends.values()) / len(trends)
            }
        }
    
    def _calculate_growth_trend(self, trends: Dict[int, Dict]) -> str:
        """Calculate if topic is growing, stable, or declining."""
        years = sorted(trends.keys())
        if len(years) < 2:
            return "insufficient_data"
        
        recent_count = sum(trends[y]['paper_count'] for y in years[-2:])
        early_count = sum(trends[y]['paper_count'] for y in years[:2])
        
        if recent_count > early_count * 1.2:
            return "growing"
        elif recent_count < early_count * 0.8:
            return "declining"
        else:
            return "stable"


# Convenience functions
async def search_semantic_scholar(query: str, **kwargs) -> List[S2Paper]:
    """Quick search function."""
    async with SemanticScholarClient() as client:
        return await client.search_papers(query, **kwargs)


async def find_open_access_pdf(title: str = None, doi: str = None, arxiv_id: str = None) -> Optional[str]:
    """Quick open access finder."""
    async with SemanticScholarClient() as client:
        return await client.find_open_access_version(title=title, doi=doi, arxiv_id=arxiv_id)


# EOF