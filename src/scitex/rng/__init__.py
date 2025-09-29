#!/usr/bin/env python3
"""
SciTeX RNG Module - Simple Random State Management.

Main API:
    rng = stx.rng.RandomStateManager(seed=42)  # Create instance
    rng = stx.rng.get()                        # Get global instance  
    rng = stx.rng.reset(seed=123)              # Reset global
    
    gen = rng("name")                          # Get named generator
    rng.verify(obj, "name")                    # Verify reproducibility
    
Examples
--------
>>> import scitex as stx

>>> # Direct usage
>>> rng = stx.rng.RandomStateManager(seed=42)
>>> data = rng("data").random(100)

>>> # Global instance
>>> rng = stx.rng.get()
>>> model = rng("model").normal(size=(10, 10))

>>> # From session.start
>>> CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(seed=42)
>>> augment = rng("augment").random(50)

>>> # Verify reproducibility
>>> rng.verify(data, "my_data")
"""

from ._RandomStateManager import RandomStateManager, get, reset

__all__ = [
    "RandomStateManager",
    "get",
    "reset",
]