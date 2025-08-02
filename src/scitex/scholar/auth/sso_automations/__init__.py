#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:30:00 (claude)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/sso_automations/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/sso_automations/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""SSO Automation module for academic institutions."""

# Import base class
from ._BaseSSOAutomator import BaseSSOAutomator

# Import factory
from ._SSOAutomatorFactory import SSOAutomatorFactory

# Import specific automators
from ._UniversityOfMelbourneSSOAutomator import UniversityOfMelbourneSSOAutomator

__all__ = [
    "BaseSSOAutomator",
    "SSOAutomatorFactory",
    "UniversityOfMelbourneSSOAutomator",
]

# EOF