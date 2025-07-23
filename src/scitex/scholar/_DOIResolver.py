#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 15:51:01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_DOIResolver.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_DOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Clean, optimized DOI resolver with pluggable sources."""

import logging
import re
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Dict, List, Optional, Type

from tqdm import tqdm

logger = logging.getLogger(__name__)


class DOISource(ABC):
    """Abstract base class for DOI sources."""

    @abstractmethod
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search for DOI by title."""
        pass

    @abstractmethod
    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract by DOI."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Source name for logging."""
        pass

    @property
    def rate_limit_delay(self) -> float:
        """Delay between requests in seconds."""
        return 0.5

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from URL if present."""
        if not url:
            return None

        # Direct DOI URLs
        if "doi.org/" in url:
            match = re.search(r"doi\.org/(.+?)(?:\?|$|#)", url)
            if match:
                return match.group(1).strip()

        # DOI pattern in URL
        doi_pattern = r"10\.\d{4,}/[-._;()/:\w]+"
        match = re.search(doi_pattern, url)
        if match:
            return match.group(0)

        return None


class CrossRefSource(DOISource):
    """CrossRef DOI source - no API key required, generous rate limits."""

    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
            )
        return self._session

    @property
    def name(self) -> str:
        return "CrossRef"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1  # CrossRef is very generous

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search CrossRef for DOI."""
        url = "https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 5,
            "select": "DOI,title,published-print",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                items = data.get("message", {}).get("items", [])

                for item in items:
                    item_title = " ".join(item.get("title", []))
                    if self._is_title_match(title, item_title):
                        return item.get("DOI")
        except Exception as e:
            logger.debug(f"CrossRef error: {e}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from CrossRef."""
        url = f"https://api.crossref.org/works/{doi}"
        params = {"mailto": self.email}

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("abstract")
        except Exception as e:
            logger.debug(f"CrossRef abstract error: {e}")

        return None

    @staticmethod
    def _is_title_match(
        title1: str, title2: str, threshold: float = 0.85
    ) -> bool:
        """Simple title matching."""
        import string

        # Normalize
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Remove punctuation
        for p in string.punctuation:
            t1 = t1.replace(p, " ")
            t2 = t2.replace(p, " ")

        # Word overlap
        words1 = set(t1.split())
        words2 = set(t2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return (intersection / union) >= threshold if union > 0 else False


class PubMedSource(DOISource):
    """PubMed DOI source - free, no API key required."""

    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            import requests

            self._session = requests.Session()
        return self._session

    @property
    def name(self) -> str:
        return "PubMed"

    @property
    def rate_limit_delay(self) -> float:
        return 0.35  # NCBI requests 3 per second max

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search PubMed for DOI."""
        # Build query
        query_parts = [f'"{title}"[Title]']
        if year:
            query_parts.append(f"{year}[pdat]")

        query = " AND ".join(query_parts)

        # Search
        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": 5,
            "email": self.email,
        }

        try:
            response = self.session.get(
                search_url, params=search_params, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                pmids = data.get("esearchresult", {}).get("idlist", [])

                # Check each PMID
                for pmid in pmids:
                    doi = self._fetch_doi_for_pmid(pmid, title)
                    if doi:
                        return doi
        except Exception as e:
            logger.debug(f"PubMed error: {e}")

        return None

    def _fetch_doi_for_pmid(
        self, pmid: str, expected_title: str
    ) -> Optional[str]:
        """Fetch DOI for a specific PMID."""
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "email": self.email,
        }

        try:
            response = self.session.get(
                fetch_url, params=fetch_params, timeout=30
            )
            if response.status_code == 200:
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.text)

                # Verify title match
                title_elem = root.find(".//ArticleTitle")
                if title_elem is not None and title_elem.text:
                    if CrossRefSource._is_title_match(
                        expected_title, title_elem.text
                    ):
                        # Extract DOI
                        for id_elem in root.findall(".//ArticleId"):
                            if id_elem.get("IdType") == "doi":
                                return id_elem.text
        except Exception as e:
            logger.debug(f"PubMed fetch error: {e}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from PubMed by DOI."""
        # First find PMID by DOI
        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": f"{doi}[doi]",
            "retmode": "json",
            "email": self.email,
        }

        try:
            response = self.session.get(
                search_url, params=search_params, timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                pmids = data.get("esearchresult", {}).get("idlist", [])

                if pmids:
                    # Fetch abstract
                    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                    fetch_params = {
                        "db": "pubmed",
                        "id": pmids[0],
                        "retmode": "xml",
                        "email": self.email,
                    }

                    response = self.session.get(
                        fetch_url, params=fetch_params, timeout=30
                    )
                    if response.status_code == 200:
                        import xml.etree.ElementTree as ET

                        root = ET.fromstring(response.text)
                        abstract_elem = root.find(".//AbstractText")
                        if abstract_elem is not None:
                            return abstract_elem.text
        except Exception as e:
            logger.debug(f"PubMed abstract error: {e}")

        return None


class OpenAlexSource(DOISource):
    """OpenAlex - free and open alternative to proprietary databases."""

    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
            )
        return self._session

    @property
    def name(self) -> str:
        return "OpenAlex"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1  # OpenAlex is generous

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search OpenAlex for DOI."""
        url = "https://api.openalex.org/works"

        # Build filter
        filters = [f'title.search:"{title}"']
        if year:
            filters.append(f"publication_year:{year}")

        params = {
            "filter": ",".join(filters),
            "per_page": 5,
            "mailto": self.email,
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for work in results:
                    work_title = work.get("title", "")
                    if work_title and CrossRefSource._is_title_match(
                        title, work_title
                    ):
                        doi_url = work.get("doi", "")
                        if doi_url:
                            # Extract DOI from URL
                            return doi_url.replace("https://doi.org/", "")
        except Exception as e:
            logger.debug(f"OpenAlex error: {e}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """OpenAlex doesn't provide abstracts."""
        return None


class DOIResolver:
    """Clean, optimized DOI resolver with configurable sources."""

    # Default source order (based on rate limits and reliability)
    DEFAULT_SOURCES = ["crossref", "pubmed", "openalex"]

    # Source registry
    SOURCE_CLASSES: Dict[str, Type[DOISource]] = {
        "crossref": CrossRefSource,
        "pubmed": PubMedSource,
        "openalex": OpenAlexSource,
    }

    def __init__(
        self,
        email: str = "research@example.com",
        sources: Optional[List[str]] = None,
    ):
        """
        Initialize resolver with specified sources.

        Args:
            email: Email for API access
            sources: List of source names to use (default: all available)
        """
        self.email = email
        self.sources = sources or self.DEFAULT_SOURCES
        self._source_instances: Dict[str, DOISource] = {}

    def _get_source(self, name: str) -> Optional[DOISource]:
        """Get or create source instance."""
        if name not in self._source_instances:
            source_class = self.SOURCE_CLASSES.get(name)
            if source_class:
                self._source_instances[name] = source_class(self.email)
        return self._source_instances.get(name)

    @lru_cache(maxsize=1000)
    def title_to_doi(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[tuple] = None,  # Tuple for hashability
        sources: Optional[tuple] = None,  # Tuple for hashability
    ) -> Optional[str]:
        """
        Resolve DOI from title with caching.

        Args:
            title: Paper title
            year: Publication year
            authors: Author names as tuple
            sources: Override default source list as tuple

        Returns:
            DOI if found
        """
        sources_list = list(sources) if sources else self.sources
        authors_list = list(authors) if authors else None

        logger.info(f"Resolving DOI for: {title[:60]}...")

        for source_name in sources_list:
            source = self._get_source(source_name)
            if not source:
                continue

            try:
                doi = source.search(title, year, authors_list)
                if doi:
                    logger.info(f"  ✓ Found DOI via {source.name}: {doi}")
                    return doi
            except Exception as e:
                logger.debug(f"Error with {source_name}: {e}")

            # Rate limiting
            time.sleep(source.rate_limit_delay)

        logger.info(f"  ✗ No DOI found")
        return None

    def get_abstract(
        self, doi: str, sources: Optional[List[str]] = None
    ) -> Optional[str]:
        """Get abstract for DOI from available sources."""
        sources = sources or [
            "crossref",
            "pubmed",
        ]  # OpenAlex doesn't have abstracts

        for source_name in sources:
            source = self._get_source(source_name)
            if not source:
                continue

            try:
                abstract = source.get_abstract(doi)
                if abstract:
                    return abstract
            except Exception as e:
                logger.debug(f"Abstract error with {source_name}: {e}")

        return None

    def add_source(self, name: str, source_class: Type[DOISource]):
        """Add a custom source."""
        self.SOURCE_CLASSES[name] = source_class
        if name not in self.sources:
            self.sources.append(name)

    def resolve_from_url(self, url: str) -> Optional[str]:
        """
        Resolve DOI from URL using multiple strategies.

        Args:
            url: URL that might contain or lead to a DOI

        Returns:
            DOI if found
        """
        if not url:
            return None

        # 1. Try direct DOI extraction
        doi = self._extract_doi_from_url(url)
        if doi:
            return doi

        # 2. Try Semantic Scholar
        if "semanticscholar.org" in url and "CorpusId:" in url:
            doi = self._resolve_semantic_scholar(url)
            if doi:
                return doi

        # 3. Try PubMed
        if "ncbi.nlm.nih.gov" in url and "pubmed" in url:
            doi = self._resolve_pubmed_url(url)
            if doi:
                return doi

        return None

    def _extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI directly from URL."""
        # Use the base class method
        source = self._get_source("crossref")
        if source:
            return source.extract_doi_from_url(url)
        return None

    def _resolve_semantic_scholar(self, url: str) -> Optional[str]:
        """Resolve DOI from Semantic Scholar URL."""
        match = re.search(r"CorpusId:(\d+)", url)
        if not match:
            return None

        corpus_id = match.group(1)

        try:
            import requests

            api_url = f"https://api.semanticscholar.org/graph/v1/paper/CorpusID:{corpus_id}"
            params = {"fields": "externalIds"}

            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                external_ids = data.get("externalIds", {})
                if external_ids and "DOI" in external_ids:
                    logger.info(
                        f"  ✓ Found DOI from Semantic Scholar: {external_ids['DOI']}"
                    )
                    return external_ids["DOI"]
            elif response.status_code == 429:
                logger.warning("Semantic Scholar rate limited")

            time.sleep(1.5)  # Rate limiting
        except Exception as e:
            logger.debug(f"Semantic Scholar error: {e}")

        return None

    def _resolve_pubmed_url(self, url: str) -> Optional[str]:
        """Resolve DOI from PubMed URL."""
        match = re.search(r"pubmed/(\d+)", url)
        if not match:
            return None

        pmid = match.group(1)

        try:
            import requests

            api_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            )
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "json",
                "email": self.email,
            }

            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {}).get(pmid, {})

                for article_id in result.get("articleids", []):
                    if article_id.get("idtype") == "doi":
                        doi = article_id.get("value")
                        logger.info(f"  ✓ Found DOI from PubMed: {doi}")
                        return doi

            time.sleep(0.3)  # NCBI rate limit
        except Exception as e:
            logger.debug(f"PubMed URL error: {e}")

        return None


class BatchDOIResolver:
    """Batch DOI resolver with parallel processing and progress tracking."""

    def __init__(
        self,
        email: str = "research@example.com",
        max_workers: int = 3,
        delay_between_papers: float = 0.5,
    ):
        """
        Initialize batch resolver.

        Args:
            email: Email for API access
            max_workers: Number of parallel workers (be respectful to APIs)
            delay_between_papers: Delay between processing papers
        """
        self.email = email
        self.max_workers = max_workers
        self.delay_between_papers = delay_between_papers
        self._resolver = DOIResolver(email=email)

    def resolve_batch(
        self, papers: List[Dict[str, any]], show_progress: bool = True
    ) -> List[Dict[str, any]]:
        """
        Resolve DOIs for a batch of papers.

        Args:
            papers: List of dicts with 'title', 'year', 'authors' keys
            show_progress: Show progress bar

        Returns:
            List of results with 'doi', 'abstract', 'title' keys
        """
        results = []

        # Use progress bar if requested
        iterator = (
            tqdm(papers, desc="Resolving DOIs") if show_progress else papers
        )

        # Process in small batches to respect rate limits
        batch_size = self.max_workers
        for i in range(0, len(papers), batch_size):
            batch = papers[i : i + batch_size]

            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all papers in batch
                future_to_paper = {
                    executor.submit(self._process_paper, paper): paper
                    for paper in batch
                }

                # Collect results as they complete
                for future in as_completed(future_to_paper):
                    paper = future_to_paper[future]
                    try:
                        result = future.result()
                        results.append(result)

                        if show_progress and result["doi"]:
                            tqdm.write(
                                f"✓ Found DOI for: {result['title'][:50]}..."
                            )

                    except Exception as e:
                        logger.error(f"Error processing paper: {e}")
                        results.append(
                            {
                                "title": paper.get("title", ""),
                                "doi": None,
                                "abstract": None,
                                "error": str(e),
                            }
                        )

            # Delay between batches
            if i + batch_size < len(papers):
                time.sleep(self.delay_between_papers)

        return results

    def _process_paper(self, paper: Dict[str, any]) -> Dict[str, any]:
        """Process a single paper."""
        title = paper.get("title", "")
        year = paper.get("year")
        authors = paper.get("authors", [])
        url = paper.get("url") or paper.get("pdf_url")

        doi = None

        # First try URL resolution if available
        if url and not doi:
            doi = self._resolver.resolve_from_url(url)
            if doi:
                logger.debug(f"Found DOI from URL for: {title[:50]}...")

        # If no DOI from URL, try title-based search
        if not doi:
            # Convert authors to tuple for caching
            authors_tuple = tuple(authors) if authors else None

            # Resolve DOI
            doi = self._resolver.title_to_doi(
                title=title, year=year, authors=authors_tuple
            )

        # Get abstract if DOI found
        abstract = None
        if doi:
            abstract = self._resolver.get_abstract(doi)

        return {
            "title": title,
            "doi": doi,
            "abstract": abstract,
            "year": year,
            "authors": authors,
            "url": url,
        }

    def enhance_papers_parallel(
        self, papers: List[any], show_progress: bool = True  # Paper objects
    ) -> Dict[str, Dict[str, any]]:
        """
        Enhance Paper objects with DOIs and abstracts in parallel.

        Args:
            papers: List of Paper objects
            show_progress: Show progress bar

        Returns:
            Dict mapping paper identifiers to enhancement results
        """
        # Prepare paper data for batch processing
        paper_data = []
        paper_map = {}

        for paper in papers:
            paper_id = paper.get_identifier()
            paper_data.append(
                {
                    "title": paper.title,
                    "year": paper.year,
                    "authors": paper.authors,
                    "pdf_url": paper.pdf_url,  # Include URL for resolution
                }
            )
            paper_map[paper.title] = paper_id

        # Process in batch
        results = self.resolve_batch(paper_data, show_progress)

        # Map results back to paper IDs
        enhanced_data = {}
        for result in results:
            paper_id = paper_map.get(result["title"])
            if paper_id:
                enhanced_data[paper_id] = result

        # Update paper objects
        success_count = 0
        for paper in papers:
            paper_id = paper.get_identifier()
            if paper_id in enhanced_data:
                data = enhanced_data[paper_id]

                if data.get("doi") and not paper.doi:
                    paper.doi = data["doi"]
                    success_count += 1

                if data.get("abstract") and not paper.abstract:
                    paper.abstract = data["abstract"]

        if show_progress:
            print(
                f"\n✓ Enhanced {success_count}/{len(papers)} papers with DOIs"
            )

        return enhanced_data


# Example usage
if __name__ == "__main__":
    # Test papers
    test_papers = [
        {
            "title": "The functional role of cross-frequency coupling",
            "year": 2010,
        },
        {
            "title": "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies",
            "year": 2010,
        },
        {
            "title": "Phase-amplitude coupling supports phase coding in human ECoG",
            "year": 2015,
        },
    ]

    # Create batch resolver
    resolver = BatchDOIResolver(
        email="research@example.com",
        max_workers=2,  # Process 2 papers in parallel
    )

    # Resolve in batch
    print("Batch DOI Resolution Demo")
    print("=" * 60)

    results = resolver.resolve_batch(test_papers)

    # Display results
    print(f"\nProcessed {len(results)} papers:")
    for result in results:
        print(f"\nTitle: {result['title'][:60]}...")
        if result["doi"]:
            print(f"  DOI: {result['doi']}")
            print(f"  Abstract: {'Yes' if result['abstract'] else 'No'}")
        else:
            print("  DOI: Not found")

# EOF
