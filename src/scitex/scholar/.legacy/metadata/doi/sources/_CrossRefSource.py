#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:26:40 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_CrossRefSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from typing import Dict, List, Optional, Union

from scitex import logging

from ..utils import to_complete_metadata_structure
from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class CrossRefSource(BaseDOISource):
    """CrossRef DOI source - no API key required, generous rate limits."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.base_url = "https://api.crossref.org/works"

    @property
    def name(self) -> str:
        return "CrossRef"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=5,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi is provided, all the information other than doi is ignored"""
        if doi:
            return self._search_by_doi(doi, return_as)
        else:
            return self._search_by_metadata(
                title, year, authors, max_results, return_as
            )

    def _search_by_doi(self, doi: str, return_as: str) -> Optional[Dict]:
        """Search by DOI directly"""
        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )
        url = f"{self.base_url}/{doi}"

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            item = data.get("message", {})
            return self._extract_metadata_from_item(item, return_as)
        except Exception as exc:
            logger.warn(f"CrossRef DOI search error: {exc}")
            return None

    def _search_by_metadata(
        self,
        title: str,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: int = 5,
        return_as: str = "dict",
    ) -> Optional[Dict]:
        """Search by metadata other than doi"""
        if not title:
            return None

        params = {
            "query": title,
            "rows": max_results,
            "select": "DOI,title,published-print,published-online,container-title,short-container-title,publisher,volume,issue,ISSN,abstract,author",
            "mailto": self.email,
        }

        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("message", {}).get("items", [])
            for item in items:
                item_title = " ".join(item.get("title", []))
                if item_title.endswith("."):
                    item_title = item_title[:-1]
                if self._is_title_match(title, item_title):
                    return self._extract_metadata_from_item(item, return_as)
            return None
        except Exception as exc:
            logger.warn(f"CrossRef metadata error: {exc}")
            return None

    def _extract_metadata_from_item(
        self, item, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from CrossRef item"""
        item_title = " ".join(item.get("title", []))
        if item_title.endswith("."):
            item_title = item_title[:-1]

        pub_year = None
        published = item.get("published-print") or item.get("published-online")
        if published and published.get("date-parts"):
            pub_year = published["date-parts"][0][0]

        extracted_authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if family:
                if given:
                    extracted_authors.append(f"{given} {family}")
                else:
                    extracted_authors.append(family)

        container_titles = item.get("container-title", [])
        short_container_titles = item.get("short-container-title", [])
        journal = container_titles[0] if container_titles else None
        short_journal = (
            short_container_titles[0] if short_container_titles else None
        )
        issn_list = item.get("ISSN", [])
        issn = issn_list[0] if issn_list else None

        metadata = {
            "id": {
                "doi": item.get("DOI"),
                "doi_sources": [self.name] if item.get("DOI") else None,
            },
            "basic": {
                "title": item_title if item_title else None,
                "title_sources": [self.name] if item_title else None,
                "year": pub_year if pub_year else None,
                "year_sources": [self.name] if pub_year else None,
                "abstract": (
                    item.get("abstract") if item.get("abstract") else None
                ),
                "abstract_sources": (
                    [self.name] if item.get("abstract") else None
                ),
                "authors": extracted_authors if extracted_authors else None,
                "authors_sources": [self.name] if extracted_authors else None,
            },
            "publication": {
                "journal": journal if journal else None,
                "journal_sources": [self.name] if journal else None,
                "short_journal": short_journal if short_journal else None,
                "short_journal_sources": (
                    [self.name] if short_journal else None
                ),
                "publisher": (
                    item.get("publisher") if item.get("publisher") else None
                ),
                "publisher_sources": (
                    [self.name] if item.get("publisher") else None
                ),
                "volume": item.get("volume") if item.get("volume") else None,
                "volume_sources": [self.name] if item.get("volume") else None,
                "issue": item.get("issue") if item.get("issue") else None,
                "issue_sources": [self.name] if item.get("issue") else None,
                "issn": issn if issn else None,
                "issn_sources": [self.name] if issn else None,
            },
            "url": {
                "doi": (
                    "https://doi.org/" + item.get("DOI")
                    if item.get("DOI")
                    else None
                ),
                "doi_sources": [self.name] if item.get("DOI") else None,
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


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Attention is All You Need"
    # DOI = "https://doi.org/10.48550/arXiv.1706.03762"
    DOI = "10.1007/978-3-031-84300-6_13"

    # Example: CrossRef search
    source = CrossRefSource("test@example.com")

    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = source.search(title=TITLE)
    outputs["metadata_by_title_json"] = source.search(
        title=TITLE, return_as="json"
    )

    # Search by DOI
    outputs["metadata_by_doi_dict"] = source.search(doi=DOI)
    outputs["metadata_by_doi_json"] = source.search(doi=DOI, return_as="json")

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

# python -m scitex.scholar.metadata.doi.sources._CrossRefSource

# EOF
