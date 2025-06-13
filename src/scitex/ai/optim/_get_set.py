#!/usr/bin/env python3
"""Optimizer utilities - legacy interface maintained for compatibility."""

import warnings
from ._optimizers import get_optimizer, set_optimizer


def set(models, optim_str, lr):
    """Sets an optimizer to models.

    DEPRECATED: Use set_optimizer instead.
    """
    warnings.warn(
        "scitex.ai.optim.set is deprecated. Use scitex.ai.optim.set_optimizer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return set_optimizer(models, optim_str, lr)


def get(optim_str):
    """Get optimizer class by name.

    DEPRECATED: Use get_optimizer instead.
    """
    warnings.warn(
        "scitex.ai.optim.get is deprecated. Use scitex.ai.optim.get_optimizer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_optimizer(optim_str)
