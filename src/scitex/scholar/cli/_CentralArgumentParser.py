#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/cli/_CentralArgumentParser.py

"""Single source of truth for command-line argument configurations.

This module centralizes ALL argument definitions and parser creation.
No arguments should be defined anywhere else.
"""

import argparse
from typing import Dict, Optional

from scitex import logging

from ._argument_groups import ArgumentDef, ArgumentGroups

logger = logging.getLogger(__name__)


class CentralArgumentParser:
    """Centralized argument parser for Scholar CLI."""

    @staticmethod
    def _add_argument_to_parser(parser_or_group, arg_def: ArgumentDef):
        """Add a single argument to parser or argument group."""
        kwargs = {}

        # Build kwargs from ArgumentDef
        if arg_def.help:
            kwargs["help"] = arg_def.help
        if arg_def.type is not None:
            kwargs["type"] = arg_def.type
        if arg_def.choices is not None:
            kwargs["choices"] = arg_def.choices
        if arg_def.nargs is not None:
            kwargs["nargs"] = arg_def.nargs
        if arg_def.default is not None:
            kwargs["default"] = arg_def.default
        if arg_def.action is not None:
            kwargs["action"] = arg_def.action
        if arg_def.const is not None:
            kwargs["const"] = arg_def.const
        if arg_def.metavar is not None:
            kwargs["metavar"] = arg_def.metavar
        if arg_def.required:
            kwargs["required"] = arg_def.required
        if arg_def.dest is not None:
            kwargs["dest"] = arg_def.dest

        # Add argument
        parser_or_group.add_argument(*arg_def.names, **kwargs)

    @classmethod
    def create_main_parser(cls) -> argparse.ArgumentParser:
        """Create the main Scholar argument parser with all groups."""

        epilog_text = """
EXAMPLES:
  # RECOMMENDED: Two-step workflow for reliability
  # Step 1: Enrich metadata (DOIs, abstracts, citations, impact factors)
  python -m scitex.scholar --bibtex papers.bib \\
      --output papers_enriched.bib --project myresearch --enrich

  # Step 2: Download PDFs from enriched metadata
  python -m scitex.scholar --bibtex papers_enriched.bib \\
      --project myresearch --download

  # Single-step (works but less reliable for large batches)
  python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download

  # Manual browser download with auto-linking (for failed PDFs)
  python -m scitex.scholar --browser --project neurovista

  # Download single paper by DOI
  python -m scitex.scholar --doi "10.1038/nature12373" --project myresearch --download

  # Filter high-impact papers before download
  python -m scitex.scholar --bibtex papers.bib --project important \\
      --min-citations 100 --min-impact-factor 10.0 --download

  # Force re-download all PDFs (refresh)
  python -m scitex.scholar --bibtex papers.bib --project myresearch --download-force

  # List papers in a project
  python -m scitex.scholar --project myresearch --list

  # Search and export
  python -m scitex.scholar --project myresearch --search "neural" --export neural_papers.bib

STORAGE: ~/.scitex/scholar/library/
  MASTER/8DIGITID/  - Centralized storage (no duplicates)
  project_name/     - Project symlinks to MASTER

DOCUMENTATION: https://github.com/ywatanabe1989/SciTeX-Code/tree/main/src/scitex/scholar
"""

        parser = argparse.ArgumentParser(
            prog="python -m scitex.scholar",
            description="""
SciTeX Scholar - Unified Scientific Literature Management System
═════════════════════════════════════════════════════════════════

A comprehensive tool for managing academic papers with automatic enrichment,
PDF downloads, and persistent storage organization. Combines multiple operations
in flexible, chainable commands.

KEY FEATURES:
  • Automatic metadata enrichment (DOIs, abstracts, citations, impact factors)
  • Authenticated PDF downloads via institutional access
  • MASTER storage architecture prevents duplicates
  • Project-based organization with human-readable symlinks
  • Smart filtering by year, citations, and impact factor
  • Resume capability for interrupted operations
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog_text,
        )

        # Add all argument groups
        all_groups = ArgumentGroups.get_all_groups()

        for group_name, arg_defs in all_groups.items():
            group = parser.add_argument_group(group_name)
            for arg_def in arg_defs:
                cls._add_argument_to_parser(group, arg_def)

        return parser

    @classmethod
    def parse_args(cls, args=None):
        """Parse command-line arguments."""
        parser = cls.create_main_parser()
        return parser.parse_args(args)


# EOF
