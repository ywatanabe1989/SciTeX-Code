#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 00:10:39 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/00_config.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates comprehensive ScholarConfig functionality
- Shows directory structure and path resolution methods
- Tests configuration cascade behavior (direct -> config -> env -> default)
- Displays storage statistics and maintenance capabilities
- Validates directory structure integrity

Dependencies:
- scripts:
  - None
- packages:
  - scitex

Input:
- Configuration files from scitex.scholar.config
- Environment variables with SCITEX_SCHOLAR_ prefix
- System Chrome profile (if exists)

Output:
- Console output showing configuration paths and values
- Directory structure visualization
- Storage statistics and maintenance results
"""

"""Imports"""
import argparse
from pathlib import Path

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
def demonstrate_basic_paths(config) -> None:
    """Show basic directory paths and creation.

    Parameters
    ----------
    config : ScholarConfig
        Configuration instance
    """
    print("=== Basic Directory Paths ===")
    print(f"Scholar base directory: {config.paths.scholar_dir}")
    print(f"Cache directory: {config.get_cache_file('example', 'search')}")
    print(f"Auth cache: {config.get_auth_cache_dir()}")
    print(f"Chrome cache (system): {config.get_chrome_cache_dir('system')}")
    print(f"Downloads: {config.get_downloads_dir()}")
    print(f"Screenshots: {config.get_screenshots_dir()}")
    print(
        f"Screenshots (category): {config.get_screenshots_dir('test_category')}"
    )
    print()


def demonstrate_library_system(config) -> None:
    """Show library system with paper storage and project organization.

    Parameters
    ----------
    config : ScholarConfig
        Configuration instance
    """
    print("=== Library System ===")
    print(f"Library base: {config.get_library_dir()}")
    print(f"Project library: {config.get_library_dir('my_project')}")
    print(f"Master storage: {config.get_library_master_dir()}")

    storage_path, readable_name, paper_id = (
        config.paths.get_paper_storage_paths(
            doi="10.1038/nature12373",
            title="Attention Is All You Need",
            authors=["Vaswani, Ashish", "Shazeer, Noam"],
            journal="Nature",
            year=2017,
            project="transformer_papers",
        )
    )

    print(f"Paper storage example:")
    print(f"  Storage path: {storage_path}")
    print(f"  Readable name: {readable_name}")
    print(f"  Paper ID: {paper_id}")
    print()


def demonstrate_config_resolution(config) -> None:
    """Show configuration cascade resolution behavior.

    Parameters
    ----------
    config : ScholarConfig
        Configuration instance
    """
    print("=== Configuration Resolution ===")

    debug_mode = config.resolve("debug_mode", default=False, type=bool)
    project = config.resolve("project", default="default")
    api_key = config.resolve("semantic_scholar_api_key", default="not_set")

    print(f"Debug mode: {debug_mode}")
    print(f"Project: {project}")
    print(
        f"API key status: {'configured' if api_key != 'not_set' else 'not configured'}"
    )

    print("\nResolution log:")
    config.print()
    print()


def demonstrate_storage_stats(config) -> None:
    """Show storage statistics and maintenance.

    Parameters
    ----------
    config : ScholarConfig
        Configuration instance
    """
    print("=== Storage Statistics ===")
    stats = config.paths.get_storage_stats()

    for directory, info in stats.items():
        print(f"{directory.capitalize()}:")
        print(f"  Size: {info['size_mb']:.2f} MB")
        print(f"  Files: {info['file_count']:,}")
        print(f"  Path: {info['path']}")

    print("\nPerforming maintenance...")
    maintenance_results = config.paths.perform_maintenance()

    for operation, count in maintenance_results.items():
        if count > 0:
            print(f"  {operation}: {count:,}")
    print()


def demonstrate_advanced_features(config) -> None:
    """Show advanced PathManager features.

    Parameters
    ----------
    config : ScholarConfig
        Configuration instance
    """
    print("=== Advanced Features ===")

    progress_file = config.paths.get_doi_resolution_progress_path()
    print(f"Auto-generated progress file: {progress_file}")

    bibtex_dir = config.get_project_bibtex_dir("example_project")
    print(f"Project BibTeX directory: {bibtex_dir}")

    unresolved_dir = config.get_unresolved_entries_dir("example_project")
    print(f"Unresolved entries: {unresolved_dir}")

    logs_dir = config.get_project_logs_dir("example_project")
    print(f"Project logs: {logs_dir}")
    print()


def main(args) -> int:
    from scitex.scholar.config import ScholarConfig

    config_path = Path(args.config) if args.config else None
    config = ScholarConfig(config_path)

    if args.structure:
        print("=== Expected Directory Structure ===")
        config.paths.print_expected_structure()
        return 0

    demonstrate_basic_paths(config)
    demonstrate_library_system(config)
    demonstrate_config_resolution(config)

    if args.stats:
        demonstrate_storage_stats(config)

    if args.advanced:
        demonstrate_advanced_features(config)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate ScholarConfig functionality"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to custom config YAML file (default: %(default)s)",
    )
    parser.add_argument(
        "--structure",
        "-s",
        action="store_true",
        default=False,
        help="Show expected directory structure (default: %(default)s)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Show storage statistics and perform maintenance (default: %(default)s)",
    )
    parser.add_argument(
        "--advanced",
        "-a",
        action="store_true",
        default=False,
        help="Show advanced PathManager features (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
