#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 19:02:22 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/00_config.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/00_config.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar.config import ScholarConfig


def main():
    config = ScholarConfig()

    # Path
    print(config.get_auth_cache_dir())
    print(config.get_chrome_cache_dir("extension"))
    print(config.get_downloads_dir())
    print(config.get_library_dir("my_library"))
    print(config.get_screenshots_dir())
    print(config.get_screenshots_dir("aab"))
    print(config.resolve("scitex_dir", None))
    print(config.print())


main()

# EOF
