#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 01:48:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/resolve_dois.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/resolve_dois.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .doi._resolve_dois import main

if __name__ == "__main__":
    main()

# EOF