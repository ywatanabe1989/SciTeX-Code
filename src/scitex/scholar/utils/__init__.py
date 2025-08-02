#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 03:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/utils/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Scholar utility modules for email, notifications, and other helper functions."""

from ._email import send_email_async, send_email

__all__ = [
    "send_email_async",
    "send_email",
]

# EOF