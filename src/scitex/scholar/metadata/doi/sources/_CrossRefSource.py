#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 10:54:56 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_CrossRefSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_CrossRefSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
from typing import List, Optional

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
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        max_results=5,
        return_as: Optional[str] = "dict",
    ) -> Optional[str]:
        """Get comprehensive metadata from CrossRef."""
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
                    pub_year = None
                    published = item.get("published-print") or item.get(
                        "published-online"
                    )
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
                    short_container_titles = item.get(
                        "short-container-title", []
                    )
                    journal = container_titles[0] if container_titles else None
                    short_journal = (
                        short_container_titles[0]
                        if short_container_titles
                        else None
                    )

                    issn_list = item.get("ISSN", [])
                    issn = issn_list[0] if issn_list else None

                    metadata = {
                        "id": {
                            "doi": item.get("DOI"),
                            "doi_source": (
                                self.name if item.get("DOI") else None
                            ),
                        },
                        "basic": {
                            "title": item_title if item_title else None,
                            "title_source": self.name if item_title else None,
                            "year": pub_year if pub_year else None,
                            "year_source": self.name if pub_year else None,
                            "abstract": (
                                item.get("abstract")
                                if item.get("abstract")
                                else None
                            ),
                            "abstract_source": (
                                self.name if item.get("abstract") else None
                            ),
                            "authors": (
                                extracted_authors
                                if extracted_authors
                                else None
                            ),
                            "authors_source": (
                                self.name if extracted_authors else None
                            ),
                        },
                        "publication": {
                            "journal": journal if journal else None,
                            "journal_source": self.name if journal else None,
                            "short_journal": (
                                short_journal if short_journal else None
                            ),
                            "short_journal_source": (
                                self.name if short_journal else None
                            ),
                            "publisher": (
                                item.get("publisher")
                                if item.get("publisher")
                                else None
                            ),
                            "publisher_source": (
                                self.name if item.get("publisher") else None
                            ),
                            "volume": (
                                item.get("volume")
                                if item.get("volume")
                                else None
                            ),
                            "volume_source": (
                                self.name if item.get("volume") else None
                            ),
                            "issue": (
                                item.get("issue")
                                if item.get("issue")
                                else None
                            ),
                            "issue_source": (
                                self.name if item.get("issue") else None
                            ),
                            "issn": issn if issn else None,
                            "issn_source": self.name if issn else None,
                        },
                        "url": {
                            "doi": (
                                "https://doi.org/" + item.get("DOI")
                                if item.get("DOI")
                                else None
                            ),
                            "doi_source": (
                                self.name if item.get("DOI") else None
                            ),
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

                    return metadata

        except Exception as exc:
            logger.warn(f"CrossRef metadata error: {exc}")
            return None


if __name__ == "__main__":
    from pprint import pprint

    # Example: CrossRef search
    source = CrossRefSource("test@example.com")

    # Search metadata
    metadata_dict = source.search(
        "Neural Network and Deep Learning", year=2015
    )
    pprint(metadata_dict)

    metadata_json = source.search(
        "Neural Network and Deep Learning", year=2015, return_as="json"
    )
    print(metadata_json)

# python -m scitex.scholar.metadata.doi.sources._CrossRefSource

# EOF
