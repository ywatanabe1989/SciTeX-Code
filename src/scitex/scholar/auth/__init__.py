#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 12:17:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/auth/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Authentication module for Scholar."""

from ._AuthenticationManager import AuthenticationManager
from ._BaseAuthenticator import BaseAuthenticator
from ._OpenAthensAuthenticator import OpenAthensAuthenticator
from ._EZProxyAuthenticator import EZProxyAuthenticator
from ._ShibbolethAuthenticator import ShibbolethAuthenticator

__all__ = [
    "AuthenticationManager",
    "BaseAuthenticator",
    "OpenAthensAuthenticator",
    "EZProxyAuthenticator",
    "ShibbolethAuthenticator",
]

# EOF
