#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/cli/_argument_groups.py

"""Centralized argument group definitions for Scholar CLI.

Single source of truth for all command-line arguments.
Separation of concerns: definitions here, parsing in _CentralArgumentParser.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ArgumentDef:
    """Definition for a single command-line argument."""

    # Positional/flag names
    names: List[str]  # e.g., ["--bibtex"] or ["-p", "--project"]

    # Help text
    help: str

    # Type and validation
    type: Optional[type] = None
    choices: Optional[List[str]] = None
    nargs: Optional[str] = None

    # Default behavior
    default: Any = None
    action: Optional[str] = None
    const: Any = None

    # Metadata
    metavar: Optional[str] = None
    required: bool = False
    dest: Optional[str] = None


class ArgumentGroups:
    """Centralized definitions of all argument groups."""

    # ========================================
    # Input Sources
    # ========================================
    INPUT_SOURCES = [
        ArgumentDef(
            names=["--bibtex"],
            help="Path to BibTeX file containing paper references",
            type=str,
            metavar="FILE",
        ),
        ArgumentDef(
            names=["--doi"],
            help='Single DOI to process (e.g., "10.1038/nature12373")',
            type=str,
            metavar="DOI",
        ),
        ArgumentDef(
            names=["--dois"],
            help="Multiple DOIs to process (space-separated)",
            type=str,
            nargs="+",
            metavar="DOI",
        ),
        ArgumentDef(
            names=["--title"],
            help="Paper title for DOI resolution or library search",
            type=str,
        ),
    ]

    # ========================================
    # Project Management
    # ========================================
    PROJECT_MANAGEMENT = [
        ArgumentDef(
            names=["-p", "--project"],
            help="Project name for organizing papers (stored in ~/.scitex/scholar/library/PROJECT)",
            type=str,
            metavar="NAME",
        ),
        ArgumentDef(
            names=["--project-description"],
            help="Optional project description (project created automatically when needed)",
            type=str,
        ),
    ]

    # ========================================
    # Operations
    # ========================================
    OPERATIONS = [
        ArgumentDef(
            names=["--enrich", "-e"],
            help="Enrich papers with metadata (DOIs, abstracts, citations, impact factors) [Default: True when loading BibTeX]",
            action="store_true",
            default=True,
        ),
        ArgumentDef(
            names=["--no-enrich"],
            help="Skip metadata enrichment",
            action="store_true",
        ),
        ArgumentDef(
            names=["--download", "-d"],
            help="Download PDFs for papers",
            action="store_true",
        ),
        ArgumentDef(
            names=["--download-force"],
            help="Force re-download of existing PDFs (refresh)",
            action="store_true",
        ),
        ArgumentDef(
            names=["--list", "-l"],
            help="List papers in project library",
            action="store_true",
        ),
        ArgumentDef(
            names=["--search", "-s"],
            help="Search papers in project library (uses vector search)",
            type=str,
            metavar="QUERY",
        ),
        ArgumentDef(
            names=["--export"],
            help="Export search results or project to BibTeX file",
            type=str,
            metavar="FILE",
        ),
    ]

    # ========================================
    # Filtering
    # ========================================
    FILTERING = [
        ArgumentDef(
            names=["--year-min"],
            help="Minimum publication year (e.g., 2020)",
            type=int,
        ),
        ArgumentDef(
            names=["--year-max"],
            help="Maximum publication year (e.g., 2024)",
            type=int,
        ),
        ArgumentDef(
            names=["--min-citations"],
            help="Minimum citation count required",
            type=int,
        ),
        ArgumentDef(
            names=["--min-impact-factor"],
            help="Minimum journal impact factor (JCR 2024)",
            type=float,
        ),
        ArgumentDef(
            names=["--has-pdf"],
            help="Only include papers with downloaded PDFs",
            action="store_true",
        ),
    ]

    # ========================================
    # Output
    # ========================================
    OUTPUT = [
        ArgumentDef(
            names=["--output", "-o"],
            help="Output file path for enriched BibTeX or export",
            type=str,
            metavar="FILE",
        ),
    ]

    # ========================================
    # System
    # ========================================
    SYSTEM = [
        ArgumentDef(
            names=["--workers"],
            help="Number of parallel workers for downloads (default: 3)",
            type=int,
            default=3,
            metavar="N",
        ),
        ArgumentDef(
            names=["--no-cache"],
            help="Disable URL caching (forces fresh lookups)",
            action="store_true",
        ),
        ArgumentDef(
            names=["--browser"],
            help="Browser mode: 'stealth'=hidden downloads, 'interactive'=visible downloads, 'manual'=open browser for manual downloading",
            nargs="?",
            const="manual",
            choices=["stealth", "interactive", "manual"],
            default="stealth",
        ),
        ArgumentDef(
            names=["--stop-download"],
            help="Stop all running Scholar downloads and browser instances",
            action="store_true",
        ),
    ]

    @classmethod
    def get_all_groups(cls):
        """Get all argument groups as a dictionary."""
        return {
            "Input Sources": cls.INPUT_SOURCES,
            "Project Management": cls.PROJECT_MANAGEMENT,
            "Operations": cls.OPERATIONS,
            "Filtering": cls.FILTERING,
            "Output": cls.OUTPUT,
            "System": cls.SYSTEM,
        }


# EOF
