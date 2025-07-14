#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 16:55:30 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/tests/conftest.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/conftest.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from pathlib import Path

__FILE__ = os.path.abspath(__file__)

import re

# match lines that begin with "def test_"
_pattern_test_def = re.compile(r"^def test_", re.MULTILINE)


def pytest_collect_file(file_path):
    # Only load files that have test functions
    if str(file_path).endswith(".py") and (
        file_path.name.startswith("test_")
        or file_path.name.endswith("_test.py")
    ):
        try:
            content = Path(file_path).read_text()
            if "def test_" not in content:
                return None
            print(file_path)
        except:
            pass
    return None


# # You can also use this hook to show when a test file is actually processed
# def pytest_pycollect_makemodule(path, parent):
#     print(f"Processing module: {path}")
#     return pytest.Module.from_parent(parent, path=path)

# EOF
