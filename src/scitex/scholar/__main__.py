#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py

"""Scholar CLI entry point.

Minimal entry point with clear separation of concerns:
- Argument parsing: cli/_CentralArgumentParser.py
- Argument definitions: cli/_argument_groups.py
- Business logic: cli/handlers/*.py
- Routing: this file (minimal)
"""

from __future__ import annotations

import asyncio
import os
import sys

__FILE__ = "./src/scitex/scholar/__main__.py"
__DIR__ = os.path.dirname(__FILE__)

from scitex import logging

from .cli._CentralArgumentParser import CentralArgumentParser
from .cli.handlers import (
    handle_bibtex_operations,
    handle_doi_operations,
    handle_project_operations,
)
from .core.Scholar import Scholar
from .utils._cleanup_scholar_processes import cleanup_scholar_processes

logger = logging.getLogger(__name__)


async def main_async():
    """Main async entry point."""
    # Parse arguments using centralized parser
    args = CentralArgumentParser.parse_args()

    # Handle stop command (no Scholar needed)
    if args.stop_download:
        cleanup_scholar_processes()
        return 0

    # Determine browser mode
    browser_mode = (
        args.browser if hasattr(args, "browser") else "stealth"
    )

    # Initialize Scholar
    if args.project:
        scholar = Scholar(
            project=args.project,
            project_description=(
                args.project_description
                if hasattr(args, "project_description")
                else None
            ),
            browser_mode=browser_mode,
        )
    else:
        scholar = Scholar(browser_mode=browser_mode)

    # Route to appropriate handler based on input source
    if args.bibtex:
        return await handle_bibtex_operations(args, scholar)
    elif args.doi or args.dois:
        return await handle_doi_operations(args, scholar)
    elif args.project:
        return await handle_project_operations(args, scholar)
    else:
        logger.error("No operation specified. Use --help for usage.")
        return 1


def main():
    """Synchronous entry point."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())


# EOF
