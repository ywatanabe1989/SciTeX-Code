#!/usr/bin/env python3
"""Scitex loss module."""

from ._L1L2Losses import elastic, l1, l2
from .multi_task_loss import MultiTaskLoss

__all__ = [
    "elastic",
    "l1",
    "l2",
    "MultiTaskLoss",
]
