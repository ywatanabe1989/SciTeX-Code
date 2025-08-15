#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 15:36:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_GoogleScholarSearchEngine.py
# ----------------------------------------
from __future__ import annotations

"""
Google Scholar search engine using scholarly package.

This module provides search functionality using Google Scholar through
the scholarly Python package.
"""

import asyncio
from scitex import logging
from typing import List, Optional

from .._BaseSearchEngine import BaseSearchEngine
from scitex.scholar.core import Paper
from scitex.errors import SearchError

logger = logging.getLogger(__name__)


class GoogleScholarSearchEngine(BaseSearchEngine):
    """Search engine for Google Scholar using scholarly package."""
    
    def __init__(self, timeout: int = 10):
        super().__init__(name="google_scholar", rate_limit=2.0)
        self._scholarly = None
        self.timeout = timeout
        
    def _init_scholarly(self):
        """Lazy load scholarly package."""
        if self._scholarly is None:
            try:
                from scholarly import scholarly
                self._scholarly = scholarly
            except ImportError:
                raise ImportError(
                    "scholarly package not installed. "
                    "Install with: pip install scholarly"
                )
        return self._scholarly
    
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search Google Scholar for papers."""
        papers = []
        
        try:
            # Initialize scholarly
            scholarly = self._init_scholarly()
            
            # Quick test to see if Google Scholar is accessible
            try:
                test_search = scholarly.search_pubs("test")
                next(test_search)
            except Exception as e:
                if "Cannot Fetch" in str(e) or "403" in str(e):
                    logger.warning("Google Scholar is blocking requests")
                    raise SearchError(
                        query=query,
                        source="google_scholar",
                        reason="Google Scholar is blocking automated access. Use PubMed or Semantic Scholar instead."
                    )
            
            # Apply year filters if provided
            year_min = kwargs.get('year_min')
            year_max = kwargs.get('year_max')
            
            # Build query with year filters
            search_query = query
            if year_min and year_max:
                search_query += f" after:{year_min-1} before:{year_max+1}"
            elif year_min:
                search_query += f" after:{year_min-1}"
            elif year_max:
                search_query += f" before:{year_max+1}"
            
            logger.info(f"Searching Google Scholar: {search_query}")
            
            # Run search in executor with timeout to avoid blocking
            loop = asyncio.get_event_loop()
            
            def search_with_limit():
                """Search and limit results to avoid hanging."""
                results = []
                try:
                    search_query_obj = scholarly.search_pubs(search_query)
                    for i, result in enumerate(search_query_obj):
                        if i >= limit:
                            break
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Google Scholar search interrupted: {e}")
                    if "Cannot Fetch" in str(e) or "403" in str(e):
                        logger.info("Google Scholar is blocking automated requests.")
                return results
            
            # Apply timeout to prevent hanging
            try:
                search_results = await asyncio.wait_for(
                    loop.run_in_executor(None, search_with_limit),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Google Scholar search timed out after {self.timeout} seconds")
                raise SearchError(
                    query=search_query,
                    source="google_scholar",
                    reason=f"Search timed out after {self.timeout} seconds. Google Scholar may be blocking requests."
                )
            
            # Process results
            for result in search_results:
                try:
                    # Extract basic info from search result
                    bib = result.get('bib', {})
                    
                    title = bib.get('title', '')
                    if not title:
                        continue
                    
                    # Authors
                    authors = bib.get('author', '').split(' and ')
                    if not authors or authors == ['']:
                        authors = []
                    
                    # Abstract (often not available in search results)
                    abstract = bib.get('abstract', '')
                    
                    # Year
                    year = None
                    pub_year = bib.get('pub_year')
                    if pub_year:
                        try:
                            year = int(pub_year)
                        except:
                            pass
                    
                    # Journal/Venue
                    journal = bib.get('venue', '')
                    
                    # Citation count
                    citation_count = result.get('num_citations', 0)
                    
                    # URL
                    url = result.get('pub_url', '')
                    
                    # Try to extract DOI from URL or other fields
                    doi = None
                    if 'doi.org/' in url:
                        doi = url.split('doi.org/')[-1]
                    
                    # Create Paper object
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract or "Abstract not available from Google Scholar search",
                        source='google_scholar',
                        year=year,
                        journal=journal,
                        doi=doi,
                        citation_count=citation_count,
                        metadata={
                            'google_scholar_url': url,
                            'google_scholar_id': result.get('author_id', ''),
                            'eprint_url': result.get('eprint_url', '')
                        }
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Google Scholar result: {e}")
                    continue
                    
        except ImportError as e:
            logger.error(f"Google Scholar search unavailable: {e}")
            raise SearchError(
                query=query,
                source="google_scholar",
                reason=f"Google Scholar search unavailable: {e}"
            )
        except Exception as e:
            logger.error(f"Google Scholar search failed: {e}")
            if "robot" in str(e).lower() or "captcha" in str(e).lower() or "Cannot Fetch" in str(e):
                raise SearchError(
                    query=query,
                    source="google_scholar",
                    reason="Google Scholar is blocking automated access. Consider using PubMed or Semantic Scholar instead."
                )
            raise SearchError(
                query=query,
                source="google_scholar",
                reason=f"Search failed: {e}"
            )
        
        logger.info(f"Found {len(papers)} papers from Google Scholar")
        return papers

# EOF