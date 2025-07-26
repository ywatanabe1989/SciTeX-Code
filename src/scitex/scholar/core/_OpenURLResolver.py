#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-25 11:00:00 (ywatanabe)"
# File: ./src/scitex/scholar/_OpenURLResolver.py
# ----------------------------------------

"""
OpenURL resolver for finding full-text access through institutional libraries.

Based on University of Melbourne library recommendation.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, quote
import aiohttp

from ...errors import ScholarError

logger = logging.getLogger(__name__)


class OpenURLResolver:
    """
    Resolves DOIs/metadata to full-text URLs via institutional OpenURL resolver.
    
    OpenURL is a standardized format for encoding bibliographic information
    that libraries use to link to full-text resources.
    """
    
    # Known institutional resolvers
    KNOWN_RESOLVERS = {
        "unimelb": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        "harvard": "https://sfx.hul.harvard.edu/sfx_local",
        "mit": "https://sfx.mit.edu/sfx_local",
        "stanford": "https://searchworks.stanford.edu/openurl",
    }
    
    def __init__(self, resolver_url: Optional[str] = None):
        """
        Initialize OpenURL resolver.
        
        Args:
            resolver_url: Base URL of institutional OpenURL resolver
                         Defaults to University of Melbourne
        """
        self.resolver_url = resolver_url or self.KNOWN_RESOLVERS["unimelb"]
        self.timeout = 30
        
    def build_openurl(self, paper: Dict[str, Any]) -> str:
        """
        Build OpenURL query string from paper metadata.
        
        OpenURL v1.0 format:
        - ctx_ver=Z39.88-2004 (version)
        - rft_val_fmt=info:ofi/fmt:kev:mtx:journal (format for journal articles)
        - rft.genre=article
        - rft.atitle=Article Title
        - rft.jtitle=Journal Title
        - rft.date=Year
        - rft.volume=Volume
        - rft.issue=Issue
        - rft.spage=Start Page
        - rft.epage=End Page
        - rft.doi=DOI
        - rft.pmid=PubMed ID
        """
        # Base parameters
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
        }
        
        # Add metadata
        if paper.get("title"):
            params["rft.atitle"] = paper["title"]
        if paper.get("journal"):
            params["rft.jtitle"] = paper["journal"]
        if paper.get("year"):
            params["rft.date"] = str(paper["year"])
        if paper.get("volume"):
            params["rft.volume"] = str(paper["volume"])
        if paper.get("issue"):
            params["rft.issue"] = str(paper["issue"])
        if paper.get("pages"):
            # Handle page ranges like "123-456"
            if "-" in str(paper["pages"]):
                spage, epage = paper["pages"].split("-", 1)
                params["rft.spage"] = spage.strip()
                params["rft.epage"] = epage.strip()
            else:
                params["rft.spage"] = str(paper["pages"])
        if paper.get("doi"):
            params["rft.doi"] = paper["doi"]
        if paper.get("pmid"):
            params["rft.pmid"] = str(paper["pmid"])
            
        # Add authors
        if paper.get("authors"):
            # First author in special fields
            if paper["authors"]:
                first_author = paper["authors"][0]
                if "," in first_author:
                    last, first = first_author.split(",", 1)
                    params["rft.aulast"] = last.strip()
                    params["rft.aufirst"] = first.strip()
                params["rft.au"] = first_author
                
        # Build URL
        query_string = urlencode(params, safe=':/')
        return f"{self.resolver_url}?{query_string}"
    
    async def resolve_async(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve paper to full-text URLs via OpenURL.
        
        Args:
            paper: Paper metadata dictionary
            
        Returns:
            Dictionary with resolved URLs and access information
        """
        openurl = self.build_openurl(paper)
        logger.info(f"Resolving via OpenURL: {openurl}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    openurl,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True,
                    headers={
                        "User-Agent": "SciTeX Scholar/2.0",
                        "Accept": "text/html,application/xhtml+xml",
                    }
                ) as response:
                    if response.status == 200:
                        # Parse response to find full-text links
                        html = await response.text()
                        
                        # Look for common patterns in SFX responses
                        result = {
                            "resolver_url": str(response.url),
                            "full_text_urls": [],
                            "access_type": None,
                        }
                        
                        # Common SFX patterns
                        if "getFullTxt" in html:
                            result["access_type"] = "subscription"
                            # Extract full-text links (simplified)
                            import re
                            pdf_links = re.findall(r'href="([^"]+)"[^>]*>.*?(?:PDF|Full\s*Text)', html, re.IGNORECASE)
                            result["full_text_urls"] = pdf_links[:3]  # Top 3 links
                            
                        elif "No full text available" in html:
                            result["access_type"] = "no_access"
                            
                        logger.info(f"OpenURL resolver found {len(result['full_text_urls'])} links")
                        return result
                        
                    else:
                        logger.warning(f"OpenURL resolver returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"OpenURL resolution failed: {e}")
            
        return None
    
    def resolve(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper for resolve_async."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.resolve_async(paper))
        finally:
            loop.close()


# Integration with PDFDownloader
async def try_openurl_resolver_async(
    paper_metadata: Dict[str, Any],
    resolver_url: Optional[str] = None
) -> Optional[str]:
    """
    Try to find PDF URL via OpenURL resolver.
    
    Args:
        paper_metadata: Paper metadata
        resolver_url: OpenURL resolver base URL
        
    Returns:
        PDF URL if found, None otherwise
    """
    resolver = OpenURLResolver(resolver_url)
    result = await resolver.resolve_async(paper_metadata)
    
    if result and result.get("full_text_urls"):
        # Return first PDF URL found
        for url in result["full_text_urls"]:
            if ".pdf" in url.lower() or "pdf" in url.lower():
                return url
        # Return first URL if no explicit PDF
        return result["full_text_urls"][0]
        
    return None


if __name__ == "__main__":
    # Example usage
    async def test_resolver():
        # Test paper
        paper = {
            "title": "Deep learning in neuroimaging",
            "authors": ["Smith, John", "Doe, Jane"],
            "journal": "Nature Neuroscience",
            "year": 2023,
            "volume": 26,
            "issue": 3,
            "pages": "123-145",
            "doi": "10.1038/s41593-023-01234-5",
        }
        
        resolver = OpenURLResolver()
        
        # Build OpenURL
        openurl = resolver.build_openurl(paper)
        print(f"OpenURL: {openurl}")
        
        # Resolve
        result = await resolver.resolve_async(paper)
        if result:
            print(f"\nResolved:")
            print(f"  Access type: {result['access_type']}")
            print(f"  Full-text URLs: {result['full_text_urls']}")
        else:
            print("\nNo resolution found")
    
    asyncio.run(test_resolver())