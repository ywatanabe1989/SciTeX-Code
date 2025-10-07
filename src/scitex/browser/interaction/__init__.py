#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Browser Interaction Utilities
# ----------------------------------------

from .click_center import click_center, click_center_async
from .click_and_wait import click_and_wait
from .click_with_fallbacks import click_with_fallbacks
from .fill_with_fallbacks import fill_with_fallbacks

__all__ = [
    "click_center",
    "click_center_async",  # Backward compatibility
    "click_and_wait",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]

# EOF
