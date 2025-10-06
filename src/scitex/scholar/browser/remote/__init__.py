#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 22:34:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/remote/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Remote browser managers for ZenRows services

from ._ZenRowsRemoteScholarBrowserManager import ZenRowsRemoteScholarBrowserManager

__all__ = ["ZenRowsRemoteScholarBrowserManager"]

# EOF
