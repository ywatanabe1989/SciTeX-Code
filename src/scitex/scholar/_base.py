#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class for all scholar module classes with automatic logging name."""


class ScholarBase:
    """Base class that automatically sets self.name for logging."""

    def __init__(self):
        self.name = self.__class__.__name__


# EOF
