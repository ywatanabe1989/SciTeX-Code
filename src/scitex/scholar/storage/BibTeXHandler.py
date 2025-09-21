#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:01:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_BibTeXHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/_BibTeXHandler.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


class BibTeXHandler:
    """Handles BibTeX parsing and conversion to Paper objects."""

    def __init__(self, project: str = None, config=None):
        self.project = project
        self.config = config

    def papers_from_bibtex(
        self, bibtex_input: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from BibTeX file or content."""
        is_path = False
        input_str = str(bibtex_input)

        if len(input_str) < 500:
            if (
                input_str.endswith(".bib")
                or input_str.endswith(".bibtex")
                or "/" in input_str
                or "\\" in input_str
                or input_str.startswith("~")
                or input_str.startswith(".")
                or os.path.exists(os.path.expanduser(input_str))
            ):
                is_path = True

        if "\n@" in input_str or input_str.strip().startswith("@"):
            is_path = False

        if is_path:
            return self._papers_from_bibtex_file(input_str)
        else:
            return self._papers_from_bibtex_text(input_str)

    def _papers_from_bibtex_file(
        self, file_path: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from a BibTeX file."""
        bibtex_path = Path(os.path.expanduser(str(file_path)))
        if not bibtex_path.exists():
            raise ValueError(f"BibTeX file not found: {bibtex_path}")

        from scitex.io import load

        entries = load(str(bibtex_path))

        papers = []
        for entry in entries:
            paper = self.paper_from_bibtex_entry(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created {len(papers)} papers from BibTeX file")
        return papers

    def _papers_from_bibtex_text(self, bibtex_content: str) -> List["Paper"]:
        """Create Papers from BibTeX content string."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bib", delete=False
        ) as f:
            f.write(bibtex_content)
            temp_path = f.name

        try:
            from scitex.io import load

            entries = load(temp_path)
        finally:
            os.unlink(temp_path)

        papers = []
        for entry in entries:
            paper = self.paper_from_bibtex_entry(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created {len(papers)} papers from BibTeX text")
        return papers

    def paper_from_bibtex_entry(
        self, entry: Dict[str, Any]
    ) -> Optional["Paper"]:
        """Convert BibTeX entry to Paper."""
        from ..core.Paper import Paper

        fields = entry.get("fields", {})
        title = fields.get("title", "")
        if not title:
            return None

        author_str = fields.get("author", "")
        authors = []
        if author_str:
            authors = [a.strip() for a in author_str.split(" and ")]

        basic_data = {
            "title": title,
            "authors": authors,
            "abstract": fields.get("abstract", ""),
            "year": fields.get("year"),
            "keywords": (
                fields.get("keywords", "").split(", ")
                if fields.get("keywords")
                else []
            ),
        }

        id_data = {
            "doi": fields.get("doi"),
            "pmid": fields.get("pmid"),
            "arxiv_id": fields.get("eprint"),
        }

        publication_data = {
            "journal": fields.get("journal"),
        }

        url_data = {
            "pdf": fields.get("url"),
        }

        paper = Paper(
            basic=basic_data,
            id=id_data,
            publication=publication_data,
            url=url_data,
            project=self.project,
            config=self.config,
        )

        paper._original_bibtex_fields = fields.copy()
        paper._bibtex_entry_type = entry.get("entry_type", "misc")
        paper._bibtex_key = entry.get("key", "")

        self._handle_enriched_metadata(paper, fields)

        return paper

    def _handle_enriched_metadata(
        self, paper: "Paper", fields: Dict[str, Any]
    ) -> None:
        """Handle enriched metadata from BibTeX fields."""
        if "citation_count" in fields:
            try:
                paper.citation_count.total = int(fields["citation_count"])
                paper.citation_count.source = fields.get(
                    "citation_count_source", "bibtex"
                )
            except (ValueError, AttributeError):
                pass

        for field_name in fields:
            if "impact_factor" in field_name and "JCR" in field_name:
                try:
                    paper.publication.impact_factor = float(fields[field_name])
                    paper.publication.impact_factor_source = fields.get(
                        "impact_factor_source", "bibtex"
                    )
                    break
                except (ValueError, AttributeError):
                    pass

        for field_name in fields:
            if "quartile" in field_name and "JCR" in field_name:
                try:
                    paper.publication.journal_quartile = fields[field_name]
                    break
                except AttributeError:
                    pass

        if "volume" in fields:
            try:
                paper.publication.volume = fields["volume"]
            except AttributeError:
                pass
        if "pages" in fields:
            try:
                paper.publication.pages = fields["pages"]
            except AttributeError:
                pass

# EOF
