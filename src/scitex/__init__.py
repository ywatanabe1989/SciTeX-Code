#!/usr/bin/env python3
"""
Minimal scitex initialization.
Modules are imported on-demand to avoid circular dependencies.
"""

import os
import warnings

# Configure warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Version
try:
    from .__version__ import __version__
except ImportError:
    __version__ = "unknown"

# Lazy loading for all modules
class _LazyModule:
    def __init__(self, name):
        self._name = name
        self._module = None
    
    def __getattr__(self, attr):
        if self._module is None:
            import importlib
            self._module = importlib.import_module(f".{self._name}", package="scitex")
        return getattr(self._module, attr)

# Create lazy modules
io = _LazyModule("io")
gen = _LazyModule("gen")
plt = _LazyModule("plt")
ai = _LazyModule("ai")
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
units = _LazyModule("units")

# Import sh function directly as it's commonly used
try:
    from ._sh import sh
except ImportError:
    sh = None

# Common function that's often needed
def start(*args, **kwargs):
    """Convenience function to access gen.start"""
    return gen.start(*args, **kwargs)

__all__ = ["io", "gen", "plt", "ai", "pd", "str", "stats", "path", 
           "dict", "decorators", "start", "__version__", "sh", "units"]