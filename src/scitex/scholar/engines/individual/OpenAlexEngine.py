#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:00:41 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/OpenAlexEngine.py
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

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class OpenAlexEngine(BaseDOIEngine):
    """OpenAlex - free and open alternative to proprietary databases."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__(email)
        self.name = self.__class__.__name__
        self.base_url = "https://api.openalex.org/works"

    @property
    def name(self) -> str:
        return "OpenAlex"

    @property
    def rate_limit_delay(self) -> float:
        return 0.1

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

        params = {
            "filter": f"doi:{doi}",
            "per_page": 1,
        }

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
            results = data.get("results", [])
            if results:
                return self._extract_metadata_from_work(results[0], return_as)
            return self._create_minimal_metadata(
                doi=doi,
                return_as=return_as,
            )

        except Exception as exc:
            logger.warn(f"OpenAlex DOI search error: {exc}")
            return self._create_minimal_metadata(
                doi=doi,
                return_as=return_as,
            )

    def _search_by_metadata(
        self,
        title: str,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: int = 1,
        return_as: str = "dict",
    ) -> Optional[Dict]:
        """Search by metadata other than doi"""
        if not title:
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

        params = {
            "search": title,
            "per_page": 5,
        }

        if year:
            params["filter"] = f"publication_year:{year}"

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
            results = data.get("results", [])

            for work in results:
                work_title = work.get("title", "")
                if work_title and work_title.endswith("."):
                    work_title = work_title[:-1]
                if work_title and self._is_title_match(title, work_title):
                    return self._extract_metadata_from_work(work, return_as)
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

        except Exception as exc:
            logger.warn(f"OpenAlex metadata error: {exc}")
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

    def _extract_metadata_from_work(
        self, work, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from OpenAlex work"""
        work_title = work.get("title", "")
        if work_title and work_title.endswith("."):
            work_title = work_title[:-1]

        doi_url = work.get("doi", "")
        doi = doi_url.replace("https://doi.org/", "") if doi_url else None

        indexed_in = work.get("indexed_in", [])
        if indexed_in:
            indexed_in = ", ".join(indexed_in)
        # engine = f"{self.name} ({indexed_in})"

        ids = work.get("ids", {})
        pmid_url = ids.get("pmid", "")
        pmid = (
            pmid_url.replace("https://pubmed.ncbi.nlm.nih.gov/", "")
            if pmid_url
            else None
        )

        extracted_authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            if author.get("display_name"):
                extracted_authors.append(author["display_name"])

        journal = None
        issn = None
        publisher = None
        volume = None
        issue = None
        first_page = None
        last_page = None
        pdf_url = None

        primary_location = work.get("primary_location", {})
        if primary_location and primary_location.get("engine"):
            pdf_url = primary_location.get("pdf_url", None)
            _engine = primary_location["engine"]
            journal = _engine.get("display_name")
            issn = _engine.get("issn_l")
            if _engine.get("host_organization_name"):
                publisher = _engine["host_organization_name"]

        if not journal:
            host_venue = work.get("host_venue", {})
            if host_venue:
                journal = host_venue.get("display_name")
                issn = host_venue.get("issn_l")
                publisher = host_venue.get("publisher")

        biblio = work.get("biblio", {})
        if biblio:
            volume = biblio.get("volume")
            issue = biblio.get("issue")
            first_page = biblio.get("first_page")
            last_page = biblio.get("last_page")

        if doi and doi.startswith("10.48550/arxiv"):
            if not journal:
                journal = "arXiv (Cornell University)"
            if not publisher:
                publisher = "Cornell University"

        citation_count = work.get("cited_by_count")
        citation_count_by_year = work.get("counts_by_year")
        if citation_count_by_year:
            citation_count_by_year = {
                str(dd["year"]): dd["cited_by_count"]
                for dd in citation_count_by_year
            }
            citation_counts = {
                "total": citation_count,
                **citation_count_by_year,
            }
            citation_counts_engines = {
                f"{k}_engines": [self.name] for k, v in citation_counts.items()
            }
            citation_counts.update(citation_counts_engines)

        url_publisher = None
        if primary_location:
            url_publisher = primary_location.get("landing_page_url")
        if doi and doi.startswith("10.48550/arxiv") and not url_publisher:
            arxiv_id = doi.replace("10.48550/arxiv.", "")
            url_publisher = f"http://arxiv.org/abs/{arxiv_id}"

        keywords = []
        for keyword in work.get("keywords", []):
            if keyword.get("display_name"):
                keywords.append(keyword["display_name"])

        metadata = {
            "id": {
                "doi": doi if doi else None,
                "doi_engines": [self.name] if doi else None,
                "pmid": pmid if pmid else None,
                "pmid_engines": [self.name] if pmid else None,
            },
            "basic": {
                "title": work_title if work_title else None,
                "title_engines": [self.name] if work_title else None,
                "year": (
                    work.get("publication_year")
                    if work.get("publication_year")
                    else None
                ),
                "year_engines": (
                    [self.name] if work.get("publication_year") else None
                ),
                "authors": extracted_authors if extracted_authors else None,
                "authors_engines": [self.name] if extracted_authors else None,
                "keywords": keywords if keywords else None,
                "keywords_engines": [self.name] if keywords else None,
                "type": work.get("type") if work.get("type", None) else None,
                "type_engines": [self.name] if work.get("type") else None,
            },
            "citation_count": {
                **citation_counts,
            },
            "publication": {
                "journal": journal if journal else None,
                "journal_engines": [self.name] if journal else None,
                "issn": issn if issn else None,
                "issn_engines": [self.name] if issn else None,
                "publisher": publisher if publisher else None,
                "publisher_engines": [self.name] if publisher else None,
                "volume": volume if volume else None,
                "volume_engines": [self.name] if volume else None,
                "issue": issue if issue else None,
                "issue_engines": [self.name] if issue else None,
                "first_page": first_page if first_page else None,
                "first_page_engines": [self.name] if first_page else None,
                "last_page": last_page if last_page else None,
                "last_page_engines": [self.name] if last_page else None,
            },
            "url": {
                "doi": f"https://doi.org/{doi}" if doi else None,
                "doi_engines": [self.name] if doi else None,
                "pdf": pdf_url if pdf_url else None,
                "pdf_engines": [self.name] if pdf_url else None,
                "publisher": url_publisher if url_publisher else None,
                "publisher_engines": [self.name] if url_publisher else None,
            },
            "citation_count": citation_counts if citation_count_by_year else {
                "count": citation_count if citation_count else None,
                "count_engines": [self.name] if citation_count else None,
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

    TITLE = "Attention is All You Need"
    DOI = "10.1038/nature14539"

    engine = OpenAlexEngine("test@example.com")
    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = engine.search(title=TITLE)
    outputs["metadata_by_title_json"] = engine.search(
        title=TITLE, return_as="json"
    )

    # Search by DOI
    outputs["metadata_by_doi_dict"] = engine.search(doi=DOI)
    outputs["metadata_by_doi_json"] = engine.search(doi=DOI, return_as="json")

    # Empty Result
    outputs["empty_dict"] = engine._create_minimal_metadata(return_as="dict")
    outputs["empty_json"] = engine._create_minimal_metadata(return_as="json")

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

# python -m scitex.scholar.engines.individual.OpenAlexEngine

# EOF
