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
from scitex.scholar.core import Paper
from scitex.errors import SearchError
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class ArxivSearchEngine(BaseSearchEngine):
    """arXiv search engine using the arXiv API."""
    
    def __init__(self, config: Optional[ScholarConfig] = None):
        """Initialize arXiv search engine.
        
        Parameters
        ----------
        config : ScholarConfig, optional
            Scholar configuration object
        """
        super().__init__(name="arxiv", rate_limit=0.5)
        self.config = config or ScholarConfig()
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

    async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
        """Fetch single paper by arXiv ID."""
        try:
            # Rate limiting
            await self._rate_limit_async()
            
            # arXiv API URL for fetching by ID
            url = f"{self.base_url}query"
            params = {
                'id_list': identifier,
                'max_results': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        papers = self._parse_arxiv_response(xml_data)
                        return papers[0] if papers else None
                    else:
                        logger.error(f"arXiv fetch_by_id_async failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching paper by ID {identifier}: {e}")
            return None

    async def get_citation_count_async(self, doi: str) -> Optional[int]:
        """Get citation count for DOI (arXiv doesn't provide citation counts directly)."""
        # arXiv doesn't provide citation counts directly
        # This would require integration with a service like Google Scholar or Semantic Scholar
        logger.debug("arXiv doesn't provide citation counts directly")
        return None

    async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
        """Resolve title to DOI using arXiv search (note: many arXiv papers don't have DOIs)."""
        try:
            # Search for the paper by title
            papers = await self.search_async(title, limit=5)
            
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
            
            # If no exact match but we have results with DOI, return the first DOI
            for paper in papers:
                if paper.doi:
                    return paper.doi
            
            # Note: Many arXiv papers don't have DOIs
            logger.debug(f"No DOI found for arXiv paper: {title}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving DOI for title '{title}': {e}")
            return None


async def main():
    """Test function for ArxivSearchEngine."""
    from scitex.scholar.config import ScholarConfig
    
    config = ScholarConfig()
    engine = ArxivSearchEngine(config=config)
    
    print("Testing arXiv search engine...")
    
    try:
        papers = await engine.search_async("quantum computing", limit=5)
        print(f"Found {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   DOI: {paper.doi}")
            print(f"   Keywords: {', '.join(paper.keywords[:3])}")
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


# EOF