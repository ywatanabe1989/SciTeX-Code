#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 02:03:32 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/config.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/config.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar.config import ScholarConfig


def main():
    config = ScholarConfig()

    # Path
    print(config.get_cache_dir("chrome"))
    print(config.get_auth_cache_dir())
    print(config.get_chrome_cache_dir("extension"))
    print(config.get_downloads_dir())
    print(config.get_library_dir("my_library"))
    print(config.get_screenshots_dir())
    print(config.get_screenshots_dir("aab"))
    print(config.load())
    print(config.print_resolutions())
    print(config.resolve("scitex_dir", None))


main()

# EOF
