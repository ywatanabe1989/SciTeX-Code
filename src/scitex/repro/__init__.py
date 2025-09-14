#!/usr/bin/env python3
"""
SciTeX Repro Module - ID and timestamp generation utilities.

Note: Random state management has moved to stx.rng module.
"""

# Keep ID and timestamp utilities
from ._gen_ID import gen_ID, gen_id
from ._gen_timestamp import gen_timestamp, timestamp

# Deprecated imports with warnings
def _deprecated_function(new_location):
    """Create a deprecated function that redirects to new location."""
    def wrapper(*args, **kwargs):
        import warnings
        warnings.warn(
            f"This function has moved to {new_location}. "
            f"Please update your code to use the new location.",
            DeprecationWarning,
            stacklevel=2
        )
        # Import and call the new function
        import scitex as stx
        module_path = new_location.split('.')
        obj = stx
        for part in module_path[1:]:  # Skip 'stx'
            obj = getattr(obj, part)
        return obj(*args, **kwargs)
    return wrapper

# Import RandomStateManager directly from rng module for backward compatibility
from ..rng import RandomStateManager

# Special handling for fix_seeds with old signature
def fix_seeds(seed=42, os=True, random=True, np=True, torch=True, 
              tf=False, jax=False, verbose=False, **kwargs):
    """
    Deprecated: Use stx.rng.RandomStateManager instead.
    
    This function maintains backward compatibility with the old fix_seeds API.
    """
    import warnings
    if verbose:
        warnings.warn(
            "fix_seeds is deprecated. Use stx.rng.RandomStateManager instead.",
            DeprecationWarning,
            stacklevel=2
        )
    from ..rng import RandomStateManager
    # Just create RandomStateManager with seed and verbose
    # It automatically handles all available modules
    return RandomStateManager(seed=seed, verbose=verbose)

# Other deprecated functions
check_seeds = _deprecated_function("stx.rng.RandomStateManager")
verify_seeds = _deprecated_function("stx.rng.RandomStateManager.verify")
get_random_state_manager = _deprecated_function("stx.rng.get")
scientific_random_setup = _deprecated_function("stx.rng.RandomStateManager")

__all__ = [
    # Current utilities
    "gen_ID",
    "gen_id",
    "gen_timestamp",
    "timestamp",
    
    # Deprecated (kept for backward compatibility)
    "fix_seeds",
    "check_seeds", 
    "verify_seeds",
    "RandomStateManager",
    "get_random_state_manager",
    "scientific_random_setup",
]