"""Core browser management components."""

from .BrowserMixin import BrowserMixin
from .ProfileManager import ChromeProfileManager

__all__ = [
    "BrowserMixin",
    "ChromeProfileManager",
]
