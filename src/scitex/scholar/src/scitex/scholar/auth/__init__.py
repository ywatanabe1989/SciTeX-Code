#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:03:00 (ywatanabe)"
# File: ./src/scitex/scholar/auth/__init__.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/auth/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Authentication module for Scholar."""

# Import authentication providers
from ._BaseAuthenticationProvider import BaseAuthenticationProvider
from ._AuthenticationManager import AuthenticationManager
from ._OpenAthensAuthentication import OpenAthensAuthentication
from ._LeanLibraryAuthentication import LeanLibraryAuthentication

__all__ = [
    "BaseAuthenticationProvider",
    "AuthenticationManager",
    "OpenAthensAuthentication",
    "LeanLibraryAuthentication"
]

# EOF