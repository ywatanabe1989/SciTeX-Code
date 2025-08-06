#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 15:05:51 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/_CentralArgumentParser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/_CentralArgumentParser.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Single source of truth for command-line argument configurations."""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ArgumentConfig:
    """Configuration for a single argument."""

    name: str
    help_text: str
    type_: type = str
    default: Any = None
    action: Optional[str] = None
    nargs: Optional[str] = None
    choices: Optional[List[str]] = None
    required: bool = False
    mutually_exclusive_group: Optional[str] = None


class CentralArgumentParser:
    # @classmethod
    # def get_command_parsers(cls):
    #     """Import and get parsers from command modules."""
    #     parsers = {}

    #     try:
    #         from .enrich_bibtex import create_parser

    #         parsers["enrich-bibtex"] = create_parser()
    #     except ImportError:
    #         pass

    #     try:
    #         from .resolve_doi import create_parser

    #         parsers["resolve-doi"] = create_parser()
    #     except ImportError:
    #         pass

    #     try:
    #         from .resolve_and_enrich import create_parser

    #         parsers["resolve-and-enrich"] = create_parser()
    #     except ImportError:
    #         pass

    #     try:
    #         from .open_chrome import create_parser

    #         parsers["open-chrome"] = create_parser()
    #     except ImportError:
    #         pass

    #     return parsers

    @classmethod
    def get_command_parsers(cls):
        """Import and get parsers with descriptions from command modules."""
        parsers = {}
        descriptions = {}

        # try:
        #     from .enrich_bibtex import create_parser

        #     parser = create_parser()
        #     parsers["enrich-bibtex"] = parser
        #     descriptions["enrich-bibtex"] = parser.description
        # except ImportError:
        #     pass

        # try:
        #     from .resolve_doi import create_parser

        #     parser = create_parser()
        #     parsers["resolve-doi"] = parser
        #     descriptions["resolve-doi"] = parser.description
        # except ImportError:
        #     pass

        try:
            from .resolve_and_enrich import create_parser

            parser = create_parser()
            parsers["resolve-and-enrich"] = parser
            descriptions["resolve-and-enrich"] = parser.description
        except ImportError:
            pass

        try:
            from .open_chrome import create_parser

            parser = create_parser()
            parsers["open-chrome"] = parser
            descriptions["open-chrome"] = parser.description
        except ImportError:
            pass

        return parsers, descriptions

    @classmethod
    def create_parser(cls, command_name: str):
        """Get parser for specific command."""
        parsers = cls.get_command_parsers()
        return parsers.get(command_name)

# EOF
