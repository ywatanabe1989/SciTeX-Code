#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-10 07:44:49 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Database utilities")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Inspect command
    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect database structure"
    )
    inspect_parser.add_argument("db_path", help="Database file path")
    inspect_parser.add_argument(
        "--tables", nargs="*", help="Specific tables to inspect"
    )
    inspect_parser.add_argument(
        "--quiet", action="store_true", help="Minimal output"
    )

    # Health check command
    health_parser = subparsers.add_parser(
        "health", help="Check database health"
    )
    health_parser.add_argument(
        "db_paths", nargs="+", help="Database file paths"
    )
    health_parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix issues"
    )
    health_parser.add_argument(
        "--quiet", action="store_true", help="Minimal output"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        from ._inspect import inspect

        inspect(args.db_path, table_names=args.tables, verbose=not args.quiet)

    elif args.command == "health":
        from ._check_health import batch_health_check, check_health

        if len(args.db_paths) == 1:
            check_health(
                args.db_paths[0], verbose=not args.quiet, fix_issues=args.fix
            )
        else:
            batch_health_check(
                args.db_paths, verbose=not args.quiet, fix_issues=args.fix
            )

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF
