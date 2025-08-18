#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 07:13:28 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/01_auth.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/01_auth.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from scitex.scholar.auth import ScholarAuthManager


async def main_async():
    # Setup authentication manager
    auth_manager = ScholarAuthManager()

    # Authenticate
    await auth_manager.ensure_authenticate_async()

    # Check status
    is_authenticate_async = await auth_manager.is_authenticate_async()


asyncio.run(main_async())

# EOF
