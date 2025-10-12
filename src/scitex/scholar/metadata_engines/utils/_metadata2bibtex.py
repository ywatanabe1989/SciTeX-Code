#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 22:12:13 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/utils/_metadata2bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def metadata2bibtex(metadata, key=None):
    """Convert complete metadata structure to BibTeX entry."""
    if not key:
        key = _generate_bibtex_key(metadata)

    entry_type = _determine_entry_type(metadata)
    lines = [f"@{entry_type}{{{key},"]

    # Core fields
    _add_bibtex_field(lines, "title", metadata["basic"]["title"])
    _add_bibtex_authors(lines, metadata["basic"]["authors"])
    _add_bibtex_field(lines, "year", metadata["basic"]["year"])

    # Publication details
    _add_bibtex_field(lines, "journal", metadata["publication"]["journal"])
    _add_bibtex_field(lines, "volume", metadata["publication"]["volume"])
    _add_bibtex_field(lines, "pages", _format_pages(metadata["publication"]))

    # Identifiers
    _add_bibtex_field(lines, "doi", metadata["id"]["doi"])
    _add_bibtex_arxiv(lines, metadata["id"]["arxiv_id"])

    # Optional fields
    _add_bibtex_field(lines, "abstract", metadata["basic"]["abstract"])

    lines.append("}")
    return "\n".join(lines)


def _generate_bibtex_key(metadata):
    """Generate BibTeX key from metadata."""
    authors = metadata["basic"]["authors"]
    year = metadata["basic"]["year"] or "0000"

    if authors:
        first_author = authors[0].split()[-1].lower()
    else:
        first_author = "unknown"

    return f"{first_author}-{year}"


def _determine_entry_type(metadata):
    """Determine BibTeX entry type from metadata."""
    if metadata["id"]["arxiv_id"]:
        return "misc"
    elif metadata["publication"]["journal"]:
        return "article"
    return "misc"


def _add_bibtex_field(lines, field_name, value):
    """Add BibTeX field if value exists."""
    if value:
        escaped_value = (
            str(value)
            .replace("\\", r"\\")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("_", r"\_")
            .replace("&", r"\&")
            .replace("%", r"\%")
        )
        lines.append(f"  {field_name} = {{{escaped_value}}},")


def _add_bibtex_authors(lines, authors):
    """Add authors field to BibTeX."""
    if authors:
        authors_str = " and ".join(authors)
        lines.append(f"  author = {{{authors_str}}},")


def _add_bibtex_arxiv(lines, arxiv_id):
    """Add arXiv-specific fields."""
    if arxiv_id:
        lines.append(f"  eprint = {{{arxiv_id}}},")
        lines.append("  archivePrefix = {arXiv},")


def _format_pages(publication_data):
    """Format page range for BibTeX."""
    first_page = publication_data.get("first_page")
    last_page = publication_data.get("last_page")

    if first_page and last_page:
        return f"{first_page}--{last_page}"
    elif first_page:
        return first_page
    return None

# EOF
