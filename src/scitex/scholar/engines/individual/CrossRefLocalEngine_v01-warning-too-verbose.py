#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 07:29:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/CrossRefLocalEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/engines/individual/CrossRefLocalEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
import urllib.parse
from typing import Dict, List, Optional, Union

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class CrossRefLocalEngine(BaseDOIEngine):
    """CrossRef Local Engine using local Django API"""

    def __init__(
        self,
        email: str = "research@example.com",
        api_url: str = "http://127.0.0.1:3333",
    ):
        super().__init__(email)
        self.api_url = api_url.rstrip("/")

    @property
    def name(self) -> str:
        return "CrossRefLocal"

    @property
    def rate_limit_delay(self) -> float:
        return 0.01

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """Search using local CrossRef API with all parameters"""
        params = {}

        if doi:
            doi = doi.replace("https://doi.org/", "").replace(
                "http://doi.org/", ""
            )
            params["doi"] = doi

        if title:
            params["title"] = title

        if year:
            params["year"] = str(year)

        if authors:
            if isinstance(authors, list):
                params["authors"] = " ".join(authors)
            else:
                params["authors"] = str(authors)

        if not params:
            return self._create_minimal_metadata(return_as=return_as)

        return self._make_search_request(params, return_as)

    def _make_search_request(
        self, params: dict, return_as: str
    ) -> Optional[Dict]:
        """Make search request to local API"""
        url = f"{self.api_url}/api/search/"

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either 'dict' or 'json'"

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if (
                "doi" in params
                and isinstance(data, dict)
                and not data.get("error")
            ):
                return self._extract_metadata_from_crossref_data(
                    data, return_as
                )

            elif "results" in data and data["results"]:
                first_result = data["results"][0]
                if first_result.get("doi"):
                    return self._search_by_doi_only(
                        first_result["doi"], return_as
                    )

            elif isinstance(data, dict) and not data.get("error"):
                return self._extract_metadata_from_crossref_data(
                    data, return_as
                )

            return self._create_minimal_metadata(return_as=return_as)

        except Exception as e:
            logger.warning(f"CrossRef Local search error: {e}")
            return self._create_minimal_metadata(return_as=return_as)

    def _search_by_doi_only(self, doi: str, return_as: str) -> Optional[Dict]:
        """Get full metadata for DOI"""
        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )
        url = f"{self.api_url}/api/search/"
        params = {"doi": doi}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._extract_metadata_from_crossref_data(data, return_as)
        except Exception as exc:
            logger.warning(f"CrossRef Local DOI lookup error: {exc}")
            return self._create_minimal_metadata(doi=doi, return_as=return_as)

    def _extract_metadata_from_crossref_data(
        self, data, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from CrossRef JSON data"""
        if not data or data.get("error"):
            return self._create_minimal_metadata(return_as=return_as)

        title_list = data.get("title", [])
        title = title_list[0] if title_list else None
        if title and title.endswith("."):
            title = title[:-1]

        pub_year = None
        published = data.get("published-print") or data.get("published-online")
        if published and published.get("date-parts"):
            pub_year = published["date-parts"][0][0]

        extracted_authors = []
        for author in data.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if family:
                if given:
                    extracted_authors.append(f"{given} {family}")
                else:
                    extracted_authors.append(family)

        container_titles = data.get("container-title", [])
        short_container_titles = data.get("short-container-title", [])
        journal = container_titles[0] if container_titles else None
        short_journal = (
            short_container_titles[0] if short_container_titles else None
        )

        issn_list = data.get("ISSN", [])
        issn = issn_list[0] if issn_list else None

        metadata = {
            "id": {
                "doi": data.get("DOI"),
                "doi_engines": [self.name] if data.get("DOI") else None,
            },
            "basic": {
                "title": title if title else None,
                "title_engines": [self.name] if title else None,
                "year": pub_year if pub_year else None,
                "year_engines": [self.name] if pub_year else None,
                "authors": extracted_authors if extracted_authors else None,
                "authors_engines": [self.name] if extracted_authors else None,
            },
            "publication": {
                "journal": journal if journal else None,
                "journal_engines": [self.name] if journal else None,
                "short_journal": short_journal if short_journal else None,
                "short_journal_engines": (
                    [self.name] if short_journal else None
                ),
                "publisher": (
                    data.get("publisher") if data.get("publisher") else None
                ),
                "publisher_engines": (
                    [self.name] if data.get("publisher") else None
                ),
                "volume": data.get("volume") if data.get("volume") else None,
                "volume_engines": [self.name] if data.get("volume") else None,
                "issue": data.get("issue") if data.get("issue") else None,
                "issue_engines": [self.name] if data.get("issue") else None,
                "issn": issn if issn else None,
                "issn_engines": [self.name] if issn else None,
            },
            "url": {
                "doi": (
                    f"https://doi.org/{data.get('DOI')}"
                    if data.get("DOI")
                    else None
                ),
                "doi_engines": [self.name] if data.get("DOI") else None,
            },
            "system": {
                f"searched_by_{self.name}": True,
            },
        }

        metadata = standardize_metadata(metadata)

        if return_as == "dict":
            return metadata
        if return_as == "json":
            return json.dumps(metadata, indent=2)


if __name__ == "__main__":
    from pprint import pprint

    from scitex.scholar.engines.individual import CrossRefLocalEngine

    TITLE = "deep learning"
    DOI = "10.1001/.387"

    engine = CrossRefLocalEngine("test@example.com")
    outputs = {}

    outputs["metadata_by_title_dict"] = engine.search(title=TITLE)
    outputs["metadata_by_doi_dict"] = engine.search(doi=DOI)

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)


# python -m scitex.scholar.engines.individual.CrossRefLocalEngine

# EOF
