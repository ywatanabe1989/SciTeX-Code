#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 17:24:25 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Authentication module for Scholar."""

from ._AuthenticatedBrowserMixin import AuthenticatedBrowserMixin
from ._AuthenticationManager import AuthenticationManager
from ._BaseAuthenticator import BaseAuthenticator
from ._OpenAthensAuthenticator import OpenAthensAuthenticator
from ._EZProxyAuthenticator import EZProxyAuthenticator
from ._ShibbolethAuthenticator import ShibbolethAuthenticator

__all__ = [
    "AuthenticatedBrowserMixin",
    "AuthenticationManager",
    "BaseAuthenticator",
    "OpenAthensAuthenticator",
    "EZProxyAuthenticator",
    "ShibbolethAuthenticator",
]

# EOF
