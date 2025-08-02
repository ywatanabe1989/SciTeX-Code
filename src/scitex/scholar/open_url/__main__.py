#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for OpenURL resolution."""

import asyncio
import sys

from ._DOIToURLResolver import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)