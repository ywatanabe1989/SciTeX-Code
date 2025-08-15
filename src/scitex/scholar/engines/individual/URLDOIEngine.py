#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:15:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/engines/_URLDOIEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/engines/_URLDOIEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import random
import re
import time
from typing import Dict, List, Optional, Union

import requests

from scitex import logging

from ..utils import to_complete_metadata_structure
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class URLDOIEngine(BaseDOIEngine):
    """Extract DOIs from URL fields - immediate recovery for papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        self.ieee_patterns = [
            r"ieeexplore\.ieee\.org/document/(\d+)",
            r"ieeexplore\.ieee\.org/abstract/document/(\d+)",
            r"ieeexplore\.ieee\.org/stamp/stamp\.jsp\?arnumber=(\d+)",
        ]

        self.pubmed_patterns = [
            r"pubmed/(\d+)",
            r"ncbi\.nlm\.nih\.gov/pubmed/(\d+)",
            r"PMID:(\d+)",
        ]

        self.semantic_patterns = [
            r"semanticscholar\.org/paper/([^/?]+)",
            r"CorpusId:(\d+)",
        ]

    @property
    def name(self) -> str:
        return "URL"

    @property
    def rate_limit_delay(self) -> float:
        return 0.0

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        url: Optional[str] = None,
        **kwargs,
    ) -> Optional[Dict]:
        """When doi is provided, all the information other than doi is ignored"""
        if doi:
            return self._search_by_doi(doi, return_as)
        else:
            return self._search_by_url(
                title, year, authors, max_results, return_as, url
            )

    def _search_by_doi(self, doi: str, return_as: str) -> Optional[Dict]:
        """Search by DOI directly"""
        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"

            metadata = {
                "id": {
                    "doi": doi,
                    "doi_engines": [self.name] if doi else None,
                },
                "url": {
                    "doi": f"https://doi.org/{doi}",
                    "doi_engines": [self.name] if doi else None,
                },
                "system": {
                    f"searched_by_{self.name}": True,
                },
            }

            metadata = to_complete_metadata_structure(metadata)
            if return_as == "dict":
                return metadata
            if return_as == "json":
                return json.dumps(metadata, indent=2)
        except Exception as exc:
            logger.warn(f"URL DOI search error: {exc}")
            return None

    def _search_by_url(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: int = 1,
        return_as: str = "dict",
        url: Optional[str] = None,
    ) -> Optional[Dict]:
        """Extract DOI from URL field if available"""
        if not url:
            return None

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"

            doi = self.url_doi_extractor.extract_doi_from_url(url)
            if doi:
                metadata = {
                    "id": {
                        "doi": doi,
                        "doi_engines": [self.name],
                    },
                    "basic": {
                        "title": title if title else None,
                        "title_engines": ["input"] if title else None,
                    },
                    "url": {
                        "doi": "https://doi.org/" + doi,
                        "doi_engines": [self.name],
                        "publisher": url,
                        "publisher_engines": [self.name],
                    },
                }
                metadata = to_complete_metadata_structure(metadata)
                if return_as == "dict":
                    return metadata
                if return_as == "json":
                    return json.dumps(metadata, indent=2)

            pmid = self._extract_pubmed_id(url)
            if pmid:
                doi = self.pubmed_converter.pmid2doi(pmid)
                if doi:
                    metadata = {
                        "id": {
                            "doi": doi,
                            "doi_engines": [self.name],
                            "pmid": pmid,
                            "pmid_engines": [self.name],
                        },
                        "basic": {
                            "title": title if title else None,
                            "title_engines": ["input"] if title else None,
                        },
                        "url": {
                            "publisher": url,
                            "publisher_engines": [self.name],
                        },
                        "system": {
                            f"searched_by_{self.name}": True,
                        },
                    }
                    metadata = to_complete_metadata_structure(metadata)
                    if return_as == "dict":
                        return metadata
                    if return_as == "json":
                        return json.dumps(metadata, indent=2)

            # Continue with other extractions (IEEE, Semantic Scholar)
            ieee_id = self._extract_ieee_id(url)
            if ieee_id:
                doi = self._lookup_ieee_doi(ieee_id)
                if doi:
                    metadata = {
                        "id": {
                            "doi": doi,
                            "doi_engines": [self.name],
                        },
                        "basic": {
                            "title": title if title else None,
                            "title_engines": ["input"] if title else None,
                        },
                        "url": {
                            "doi": "https://doi.org/" + doi,
                            "doi_engines": [self.name],
                            "publisher": url,
                            "publisher_engines": [self.name],
                        },
                        "system": {
                            f"searched_by_{self.name}": True,
                        },
                    }
                    metadata = to_complete_metadata_structure(metadata)
                    if return_as == "dict":
                        return metadata
                    if return_as == "json":
                        return json.dumps(metadata, indent=2)

            semantic_id = self._extract_semantic_corpus_id(url)
            if semantic_id:
                doi = self._lookup_semantic_scholar_doi(semantic_id)
                if doi:
                    metadata = {
                        "id": {
                            "doi": doi,
                            "doi_engines": [self.name],
                            "corpus_id": semantic_id,
                            "corpus_id_engines": [self.name],
                        },
                        "basic": {
                            "title": title if title else None,
                            "title_engines": ["input"] if title else None,
                        },
                        "url": {
                            "doi": "https://doi.org/" + doi,
                            "doi_engines": [self.name],
                            "publisher": url,
                            "publisher_engines": [self.name],
                        },
                        "system": {
                            f"searched_by_{self.name}": True,
                        },
                    }
                    metadata = to_complete_metadata_structure(metadata)
                    if return_as == "dict":
                        return metadata
                    if return_as == "json":
                        return json.dumps(metadata, indent=2)

            return None
        except Exception as exc:
            logger.warn(f"URL DOI extraction error: {exc}")
            return None

    def _extract_pubmed_id(self, url: str) -> Optional[str]:
        for pattern in self.pubmed_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_ieee_id(self, url: str) -> Optional[str]:
        for pattern in self.ieee_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_semantic_corpus_id(self, url: str) -> Optional[str]:
        for pattern in self.semantic_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _lookup_ieee_doi(self, ieee_id: str) -> Optional[str]:
        try:
            url = f"https://ieeexplore.ieee.org/document/{ieee_id}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                content = response.text
                doi_patterns = [
                    r'"doi":"([^"]+)"',
                    r'doi\.org/([^"\'>\s]+)',
                    r"DOI:\s*([^\s<]+)",
                    r'"DOI":"([^"]+)"',
                ]
                for pattern in doi_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        doi = match.group(1)
                        if doi and not doi.startswith("http"):
                            return self._clean_doi(doi)
        except Exception as exc:
            logger.debug(f"IEEE lookup failed for {ieee_id}: {exc}")
        return None

    def _lookup_semantic_scholar_doi(self, semantic_id: str) -> Optional[str]:
        max_retries = 3
        base_delay = 0.5 if self.api_key else 2.0

        for attempt in range(max_retries):
            try:
                if semantic_id.isdigit():
                    url = f"https://api.semanticscholar.org/graph/v1/paper/CorpusId:{semantic_id}"
                else:
                    url = f"https://api.semanticscholar.org/graph/v1/paper/{semantic_id}"

                params = {"fields": "externalIds,title,authors"}
                headers = {"User-Agent": f"SciTeX/1.0 (mailto:{self.email})"}
                if self.api_key:
                    headers["x-api-key"] = self.api_key

                response = requests.get(
                    url, params=params, headers=headers, timeout=15
                )

                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = (base_delay * (2**attempt)) + random.uniform(
                            0.5, 1.5
                        )
                        time.sleep(delay)
                        continue
                    return None

                if response.status_code == 404:
                    return None

                if response.status_code == 200:
                    data = response.json()
                    external_ids = data.get("externalIds", {})
                    doi = external_ids.get("DOI")
                    if doi:
                        return self._clean_doi(doi)
                    return None

                response.raise_for_status()

            except requests.HTTPError as exc:
                if exc.response and exc.response.status_code == 429:
                    continue
                logger.debug(
                    f"Semantic Scholar HTTP error for {semantic_id}: {exc}"
                )
                return None
            except Exception as exc:
                logger.debug(
                    f"Semantic Scholar lookup failed for {semantic_id}: {exc}"
                )
                return None
        return None

    def _clean_doi(self, doi: str) -> str:
        return doi.strip() if doi else doi


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Test Paper"
    DOI = "10.1038/nature14539"
    URL = "https://doi.org/10.1002/hbm.26190"

    engine = URLDOIEngine("test@example.com")
    outputs = {}

    # Search by DOI
    outputs["metadata_by_doi_dict"] = engine.search(doi=DOI)
    outputs["metadata_by_doi_json"] = engine.search(doi=DOI, return_as="json")

    # Search by URL
    outputs["metadata_by_url_dict"] = engine.search(title=TITLE, url=URL)
    outputs["metadata_by_url_json"] = engine.search(
        title=TITLE, url=URL, return_as="json"
    )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)
# if __name__ == "__main__":
#     from pprint import pprint

#     engine = URLDOIEngine("test@example.com")

#     test_urls = [
#         "https://doi.org/10.1002/hbm.26190",
#         "http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=\&arnumber=10040734",
#         "https://www.ncbi.nlm.nih.gov/pubmed/33841115",
#         "https://api.semanticscholar.org/CorpusId:3626970",
#     ]

#     for url in test_urls:
#         metadata = engine.search("Test Paper", url=url)
#         print(f"URL: {url}")
#         pprint(metadata)
#         print()

# python -m scitex.scholar.engines.individual._URLDOIEngine

# EOF
