#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 04:46:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/_parse_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

import bibtexparser

from scitex import logging

logger = logging.getLogger(__name__)


def parse_bibtex(bibtex_path):
    """Safely parse BibTeX file, handling comment lines."""

    with open(bibtex_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove comment lines starting with %
    lines = content.split("\n")
    cleaned_lines = [line for line in lines if not re.match(r"^\s*%", line)]
    cleaned_content = "\n".join(cleaned_lines)

    try:
        # Try standard parser first
        logger.info(f"Parsing {bibtex_path} using bibtexparser...")
        bib_db = bibtexparser.loads(cleaned_content)
        if len(bib_db.entries) > 0:
            logger.info(f"Parsed to {len(bib_db.entries)} entries.")
            return bib_db.entries
    except Exception as e:
        logger.fail(f"Parsing with bibtexparser failed {str(e)}")

    try:
        # Manual parsing fallback
        logger.info(f"Parsing {bibtex_path} using Regular Expressions...")
        entries = []
        pattern = r"@(article|inproceedings|book)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)"
        matches = re.findall(
            pattern, cleaned_content, re.DOTALL | re.IGNORECASE
        )

        for entry_type, entry_id, entry_content in matches:
            entry = {"ENTRYTYPE": entry_type.lower(), "ID": entry_id.strip()}

            # Parse fields
            field_pattern = r"(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"
            field_matches = re.findall(field_pattern, entry_content)

            for field_name, field_value in field_matches:
                if not field_name.endswith("_source"):
                    entry[field_name.lower()] = field_value.strip()

            if entry.get("title") or entry.get("doi"):
                entries.append(entry)

        logger.info(f"Parsed {bibtex_path} to {len(entries)} entries.")

        return entries
    except Exception as e:
        logger.fail(f"Parsing with REgular Expressions failed {str(e)}")

# EOF
