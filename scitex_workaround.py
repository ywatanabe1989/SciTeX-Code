#!/usr/bin/env python3
"""Temporary workaround to make scitex work with mngs backend."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import mngs and alias it as scitex
import mngs

# Create a wrapper module
class ScitexWrapper:
    def __init__(self):
        # Copy all mngs attributes
        for attr in dir(mngs):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(mngs, attr))
    
    def __getattr__(self, name):
        # Fallback to mngs
        return getattr(mngs, name)

# Create the scitex module
scitex = ScitexWrapper()
stx = scitex

# Make it available globally
sys.modules['scitex'] = scitex
sys.modules['stx'] = scitex

print("Scitex workaround loaded. You can now use:")
print("  import scitex as stx")
print("  CONFIG = stx.io.load_configs()")