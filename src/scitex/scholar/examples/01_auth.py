#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:01:51 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/01_auth.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/01_auth.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarAuthManager authentication workflow
- Shows authentication setup and status checking
- Validates authentication state for scholar access

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Authentication credentials from environment or interactive prompts
- Cached authentication tokens if available

Output:
- Console output showing authentication status
- Updated authentication cache
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def setup_authentication() -> bool:
    """Set up and validate ScholarAuthManager authentication.

    Example
    -------
    >>> auth_success = await setup_authentication()
    >>> print(f"Authentication successful: {auth_success}")
    True

    Returns
    -------
    bool
        True if authentication successful, False otherwise
    """
    from scitex.scholar.auth import ScholarAuthManager

    auth_manager = ScholarAuthManager()

    print("Setting up authentication...")
    await auth_manager.ensure_authenticate_async()

    print("Checking authentication status...")
    is_authenticated = await auth_manager.is_authenticate_async()

    print(
        f"Authentication status: {'✓ Authenticated' if is_authenticated else '✗ Not authenticated'}"
    )

    return is_authenticated


async def main_async(args) -> bool:
    """Main async function to handle authentication workflow.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    bool
        Authentication success status
    """
    print("🔐 Scholar Authentication Example")
    print("=" * 40)

    auth_success = await setup_authentication()

    if auth_success:
        print("✅ Authentication workflow completed successfully")
    else:
        print("❌ Authentication workflow failed")
        print("Please check your credentials and try again")

    return auth_success


def main(args) -> int:
    """Main function wrapper for asyncio execution.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit status code (0 for success, 1 for failure)
    """
    auth_success = asyncio.run(main_async(args))
    return 0 if auth_success else 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar authentication workflow"
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

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
