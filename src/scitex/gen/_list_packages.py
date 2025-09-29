#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:11:54 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_list_packages.py
"""
Functionality:
    * Lists and analyzes installed Python packages and their modules
Input:
    * None (uses importlib.metadata to get installed packages)
Output:
    * DataFrame containing package module information
Prerequisites:
    * importlib.metadata (Python 3.8+) or importlib_metadata, pandas
"""

import sys
from typing import Optional

import pandas as pd

try:
    # Python 3.8+ standard library
    from importlib.metadata import distributions
except ImportError:
    # Fallback for older Python versions
    from importlib_metadata import distributions

from ._inspect_module import inspect_module


def list_packages(
    max_depth: int = 1,
    root_only: bool = True,
    skip_errors: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """Lists all installed packages and their modules."""
    sys.setrecursionlimit(10_000)

    # Skip known problematic packages
    skip_patterns = [
        "nvidia",
        "cuda",
        "pillow",
        "fonttools",
        "ipython",
        "jsonschema",
        "readme",
        "importlib-metadata",
    ]

    # Get installed packages, excluding problematic ones
    installed_packages = [
        dist.name.replace("-", "_")
        for dist in distributions()
        if not any(pat in dist.name.lower() for pat in skip_patterns)
    ]

    # Focus on commonly used packages first
    safelist = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "sklearn",
        "torch",
        "tensorflow",
        "keras",
        "xarray",
        "dask",
        "pytest",
        "requests",
        "flask",
        "django",
        "seaborn",
    ]

    # Prioritize safelist packages
    installed_packages = [pkg for pkg in installed_packages if pkg in safelist] + [
        pkg for pkg in installed_packages if pkg not in safelist
    ]

    all_dfs = []
    for package_name in installed_packages:
        try:
            df = inspect_module(
                package_name,
                docstring=False,  # Speed up by skipping docstrings
                print_output=False,
                columns=["Name"],
                root_only=root_only,
                max_depth=max_depth,
                skip_depwarnings=True,
            )
            if not df.empty:
                all_dfs.append(df)
        except Exception as err:
            if verbose:
                print(f"Error processing {package_name}: {err}")
            if not skip_errors:
                raise

    if not all_dfs:
        return pd.DataFrame(columns=["Name"])

    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df.drop_duplicates().sort_values("Name")


def main() -> Optional[int]:
    """Main function for testing package listing functionality."""
    df = list_packages(verbose=True)
    __import__("ipdb").set_trace()
    return 0


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
        sys,
        plt,
        verbose=False,
        agg=True,
    )

    exit_status = main()

    scitex.session.close(
        CONFIG,
        verbose=False,
        sys=sys,
        notify=False,
        message="",
        exit_status=exit_status,
    )

# EOF
