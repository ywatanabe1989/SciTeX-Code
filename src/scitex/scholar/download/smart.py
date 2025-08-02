#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for smart PDF downloads."""

import asyncio
import sys

from _SmartPDFDownloader import main

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)