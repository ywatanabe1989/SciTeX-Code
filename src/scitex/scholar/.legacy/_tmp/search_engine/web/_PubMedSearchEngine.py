#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:01:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_PubMedSearchEngine.py
# ----------------------------------------

"""
PubMed search engine implementation for SciTeX Scholar.

This module provides search functionality through NCBI's PubMed database
using the E-utilities API.
"""

from scitex import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import aiohttp

from .._BaseSearchEngine import BaseSearchEngine
from scitex.scholar.core import Paper
from scitex.errors import SearchError
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class PubMedSearchEngine(BaseSearchEngine):
    """PubMed search engine using NCBI E-utilities."""
    
    def __init__(self, config: Optional[ScholarConfig] = None, email: Optional[str] = None):
        """Initialize PubMed search engine.
        
        Parameters
        ----------
        config : ScholarConfig, optional
            Scholar configuration object
        email : str, optional
            Email address for NCBI E-utilities (required by NCBI policy)
            Uses sophisticated config resolution: direct → config → env → default
        """
        super().__init__(name="pubmed", rate_limit=0.4)  # NCBI rate limit
        
        self.config = config or ScholarConfig()
        
        # Use sophisticated config resolution: direct → config → env → default
        self.email = self.config.resolve(
            key="pubmed_email",
            direct_val=email,
            default="research@example.com",
            type=str
        )
        
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search PubMed for papers.
        
        Parameters
        ----------
        query : str
            Search query
        limit : int
            Maximum number of results
        **kwargs : dict
            Additional parameters (year_min, year_max)
            
        Returns
        -------
        List[Paper]
            List of papers from PubMed
        """
        await self._rate_limit_async()
        
        # Build search parameters
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json',
            'email': self.email,
            'sort': 'relevance'
        }
        
        # Add date filters
        year_min = kwargs.get('year_min')
        year_max = kwargs.get('year_max')
        if year_min is not None or year_max is not None:
            min_date = f"{year_min or 1900}/01/01"
            max_date = f"{year_max or datetime.now().year}/12/31"
            search_params['mindate'] = min_date
            search_params['maxdate'] = max_date
            search_params['datetype'] = 'pdat'
        else:
            # Default to last 20 years
            current_year = datetime.now().year
            search_params['mindate'] = f"{current_year - 20}/01/01"
            search_params['maxdate'] = f"{current_year}/12/31"
            search_params['datetype'] = 'pdat'
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search for IDs
                logger.debug(f"PubMed search URL: {self.base_url}/esearch.fcgi")
                logger.debug(f"PubMed search params: {search_params}")
                
                async with session.get(
                    f"{self.base_url}/esearch.fcgi",
                    params=search_params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pmids = data.get('esearchresult', {}).get('idlist', [])
                        logger.debug(f"PubMed search returned {len(pmids)} PMIDs")
                        
                        if pmids:
                            papers = await self._fetch_details_async(session, pmids)
                    else:
                        logger.error(f"PubMed search failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"PubMed search error: {type(e).__name__}: {e}")
            # Return empty list instead of raising to allow fallback
            return []
        
        return papers
    
    async def _fetch_details_async(self, session: aiohttp.ClientSession, pmids: List[str]) -> List[Paper]:
        """Fetch detailed information for PubMed IDs.
        
        Parameters
        ----------
        session : aiohttp.ClientSession
            Active session for making requests
        pmids : List[str]
            List of PubMed IDs to fetch
            
        Returns
        -------
        List[Paper]
            List of Paper objects with full details
        """
        await self._rate_limit_async()
        
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email
        }
        
        papers = []
        
        async with session.get(
            f"{self.base_url}/efetch.fcgi",
            params=fetch_params
        ) as response:
            if response.status == 200:
                xml_data = await response.text()
                papers = self._parse_xml(xml_data)
            else:
                logger.error(f"PubMed fetch failed: {response.status}")
        
        return papers
    
    def _parse_xml(self, xml_data: str) -> List[Paper]:
        """Parse PubMed XML response into Paper objects.
        
        Parameters
        ----------
        xml_data : str
            XML response from PubMed
            
        Returns
        -------
        List[Paper]
            Parsed Paper objects
        """
        papers = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for article_elem in root.findall('.//PubmedArticle'):
                try:
                    medline = article_elem.find('.//MedlineCitation')
                    if medline is None:
                        continue
                    
                    # Extract title
                    title_elem = medline.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ''
                    
                    # Extract authors
                    authors = []
                    for author_elem in medline.findall('.//Author'):
                        last_name = author_elem.findtext('LastName', '')
                        first_name = author_elem.findtext('ForeName', '')
                        if last_name:
                            name = f"{last_name}, {first_name}" if first_name else last_name
                            authors.append(name)
                    
                    # Extract abstract
                    abstract_parts = []
                    for abstract_elem in medline.findall('.//AbstractText'):
                        text = abstract_elem.text or ''
                        abstract_parts.append(text)
                    abstract = ' '.join(abstract_parts)
                    
                    # Extract year
                    year_elem = medline.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else None
                    
                    # Extract journal
                    journal_elem = medline.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else ''
                    
                    # Extract PMID
                    pmid_elem = medline.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ''
                    
                    # Extract DOI
                    doi = None
                    for id_elem in article_elem.findall('.//ArticleId'):
                        if id_elem.get('IdType') == 'doi':
                            doi = id_elem.text
                            break
                    
                    # Extract keywords (MeSH terms)
                    keywords = []
                    for kw_elem in medline.findall('.//MeshHeading/DescriptorName'):
                        if kw_elem.text:
                            keywords.append(kw_elem.text)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        source='pubmed',
                        year=year,
                        doi=doi,
                        pmid=pmid,
                        journal=journal,
                        keywords=keywords
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
        
        return papers

    async def fetch_by_id_async(self, identifier: str) -> Optional[Paper]:
        """Fetch single paper by PMID from PubMed."""
        try:
            # Rate limiting
            await self._rate_limit_async()
            
            # PubMed fetch URL for PMID
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': identifier,
                'retmode': 'xml',
                'email': self.email
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        papers = self._parse_pubmed_response(xml_data)
                        return papers[0] if papers else None
                    else:
                        logger.error(f"PubMed fetch_by_id_async failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching paper by ID {identifier}: {e}")
            return None

    async def get_citation_count_async(self, doi: str) -> Optional[int]:
        """Get citation count for DOI (PubMed doesn't provide citation counts directly)."""
        # PubMed doesn't provide citation counts directly
        # This would require integration with a service like Google Scholar or Web of Science
        logger.debug("PubMed doesn't provide citation counts directly")
        return None

    async def resolve_doi_async(self, title: str, year: Optional[int] = None) -> Optional[str]:
        """Resolve title to DOI using PubMed search."""
        try:
            # Search for the paper by title
            search_query = title
            if year:
                search_query += f" {year}[pdat]"
                
            papers = await self.search_async(search_query, limit=5)
            
            # Look for exact or close title matches
            title_lower = title.lower().strip()
            for paper in papers:
                if paper.doi and paper.title:
                    paper_title_lower = paper.title.lower().strip()
                    # Simple matching - could be improved with fuzzy matching
                    if title_lower in paper_title_lower or paper_title_lower in title_lower:
                        # If year is specified, prefer papers from that year
                        if year and paper.year and abs(int(paper.year) - year) <= 1:
                            return paper.doi
                        elif not year:
                            return paper.doi
            
            # If no exact match but we have results with DOI, return the first DOI
            for paper in papers:
                if paper.doi:
                    return paper.doi
                
            return None
            
        except Exception as e:
            logger.error(f"Error resolving DOI for title '{title}': {e}")
            return None


async def main():
    """Test function for PubMedSearchEngine."""
    from scitex.scholar.config import ScholarConfig
    
    config = ScholarConfig()
    engine = PubMedSearchEngine(config=config)
    
    print("Testing PubMed search engine...")
    print(f"Email: {engine.email}")
    
    try:
        papers = await engine.search_async("machine learning", limit=5)
        print(f"Found {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   DOI: {paper.doi}")
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


# EOF