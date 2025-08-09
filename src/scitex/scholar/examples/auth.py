#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 01:26:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/scholar/examples/auth.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./scholar/examples/auth.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio

from scitex.scholar.auth import AuthenticationManager


async def main_async():
    # Setup authentication manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )

    # Authenticate
    await auth_manager.ensure_authenticate_async()

    # Check status
    is_authenticate_async = await auth_manager.is_authenticate_async()


asyncio.run(main_async())

# EOF
