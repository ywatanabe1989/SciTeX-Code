#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 22:26:23 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/_CentralArgumentParser.py
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

from scitex import logging

logger = logging.getLogger(__name__)


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

    @classmethod
    def get_command_parsers(cls):
        """Import and get parsers with descriptions from command modules."""
        parsers = {}
        descriptions = {}

        try:
            from .chrome import create_parser

            parser = create_parser()
            parsers["chrome"] = parser
            descriptions["chrome"] = parser.description
        except ImportError as ie:
            logger.warn(str(ie))

        try:
            from .download_pdf import create_parser

            parser = create_parser()
            parsers["download"] = parser
            descriptions["download"] = parser.description
        except ImportError as ie:
            logger.warn(str(ie))
        return parsers, descriptions

    @classmethod
    def create_parser(cls, command_name: str):
        """Get parser for specific command."""
        parsers = cls.get_command_parsers()
        return parsers.get(command_name)

# EOF
