#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-14 15:28:49 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Minimal scitex initialization.
Modules are imported on-demand to avoid circular dependencies.
"""

import warnings
# Always show our own deprecation warnings first
warnings.filterwarnings(
    "always", category=DeprecationWarning, module="scitex.*"
)
# Then ignore others
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Version
from .__version__ import __version__

# Lazy loading for all modules
class _LazyModule:
    def __init__(self, name):
        self._name = name
        self._module = None

    def __getattr__(self, attr):
        if self._module is None:
            import importlib

            self._module = importlib.import_module(
                f".{self._name}", package="scitex"
            )
        return getattr(self._module, attr)


# Create lazy modules
io = _LazyModule("io")
gen = _LazyModule("gen")
plt = _LazyModule("plt")
ai = _LazyModule("ai")
ml = _LazyModule("ai")  # Alias for machine learning - same as ai
pd = _LazyModule("pd")
str = _LazyModule("str")
stats = _LazyModule("stats")
path = _LazyModule("path")
dict = _LazyModule("dict")
decorators = _LazyModule("decorators")
dsp = _LazyModule("dsp")
nn = _LazyModule("nn")
torch = _LazyModule("torch")
web = _LazyModule("web")
db = _LazyModule("db")
repro = _LazyModule("repro")
reproduce = _LazyModule("reproduce")
rng = _LazyModule("rng")
scholar = _LazyModule("scholar")
resource = _LazyModule("resource")
tex = _LazyModule("tex")
linalg = _LazyModule("linalg")
parallel = _LazyModule("parallel")
dt = _LazyModule("dt")
types = _LazyModule("types")
utils = _LazyModule("utils")
etc = _LazyModule("etc")
context = _LazyModule("context")
dev = _LazyModule("dev")
gists = _LazyModule("gists")
errors = _LazyModule("errors")
units = _LazyModule("units")
logging = _LazyModule("logging")
# log = _LazyModule("log")
session = _LazyModule("session")

# Import sh function directly as it's commonly used
try:
    from ._sh import sh
except ImportError:
    sh = None

__all__ = [
    "io",
    "gen",
    "plt",
    "ai",
    "ml",
    "pd",
    "str",
    "stats",
    "path",
    "dict",
    "decorators",
    "__version__",
    "sh",
    "errors",
    "units",
    "logging",
    "session",
    "rng",
]

# EOF
