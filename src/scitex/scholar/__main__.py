#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 15:43:47 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio
import sys


def main():
    from .cli._CentralArgumentParser import CentralArgumentParser

    parsers, descriptions = CentralArgumentParser.get_command_parsers()

    parser = argparse.ArgumentParser(
        prog="python -m scitex.scholar",
        description="SciTeX Scholar - Academic paper management tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")
    for cmd_name, cmd_parser in parsers.items():
        description = descriptions.get(cmd_name, "")
        subparsers.add_parser(
            cmd_name, parents=[cmd_parser], add_help=False, help=description
        )

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args, remaining = parser.parse_known_args()

    if args.command == "resolve-and-enrich":
        from .cli.resolve_and_enrich import main as enhanced_main

        original_argv = sys.argv
        sys.argv = ["resolve-and-enrich"] + remaining
        try:
            enhanced_main()
        finally:
            sys.argv = original_argv

    # elif args.command == "enrich-bibtex":
    #     from .cli.enrich_bibtex import main as enrich_main

    #     original_argv = sys.argv
    #     sys.argv = ["enrich-bibtex"] + remaining
    #     try:
    #         enrich_main()
    #     finally:
    #         sys.argv = original_argv

    # elif args.command == "resolve-doi":
    #     from .cli.resolve_doi import main as resolve_main

    #     original_argv = sys.argv
    #     sys.argv = ["resolve-doi"] + remaining
    #     try:
    #         asyncio.run(resolve_main())
    #     finally:
    #         sys.argv = original_argv

    elif args.command == "chrome":
        from .cli.chrome import main_async as chrome_main_async

        original_argv = sys.argv
        sys.argv = ["chrome"] + remaining
        try:
            asyncio.run(chrome_main_async())
        finally:
            sys.argv = original_argv

    # elif args.command == "download":
    #     from .download.__main__ import main as download_main

    #     original_argv = sys.argv
    #     sys.argv = ["download"] + remaining
    #     try:
    #         download_main()
    #     finally:
    #         sys.argv = original_argv
    elif args.command == "download":
        from .cli.download_pdf import main as download_main

        original_argv = sys.argv
        sys.argv = ["download"] + remaining
        try:
            download_main()
        finally:
            sys.argv = original_argv

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# EOF
