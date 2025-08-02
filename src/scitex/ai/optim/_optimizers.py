#!/usr/bin/env python3
"""Optimizer utilities using external packages."""

import torch.optim as optim

# Use pytorch-optimizer package for Ranger when available
try:
    from pytorch_optimizer import Ranger21 as Ranger

    RANGER_AVAILABLE = True
except ImportError:
    # Fallback to vendored version temporarily
    try:
        from .Ranger_Deep_Learning_Optimizer.ranger.ranger2020 import Ranger

        RANGER_AVAILABLE = True
    except ImportError:
        RANGER_AVAILABLE = False
        Ranger = None


def get_optimizer(name: str):
    """Get optimizer class by name.

    Args:
        name: Optimizer name (adam, ranger, rmsprop, sgd)

    Returns:
        Optimizer class

    Raises:
        ValueError: If optimizer name is not supported
    """
    optimizers = {"adam": optim.Adam, "rmsprop": optim.RMSprop, "sgd": optim.SGD}

    if name == "ranger":
        if not RANGER_AVAILABLE:
            raise ImportError(
                "Ranger optimizer not available. "
                "Please install pytorch-optimizer: pip install pytorch-optimizer"
            )
        optimizers["ranger"] = Ranger

    if name not in optimizers:
        raise ValueError(
            f"Unknown optimizer: {name}. " f"Available: {list(optimizers.keys())}"
        )

    return optimizers[name]


def set_optimizer(models, optimizer_name: str, lr: float):
    """Set optimizer for models.

    Args:
        models: Model or list of models
        optimizer_name: Name of optimizer
        lr: Learning rate

    Returns:
        Configured optimizer instance
    """
    if not isinstance(models, list):
        models = [models]

    learnable_params = []
    for model in models:
        learnable_params.extend(list(model.parameters()))

    optimizer_class = get_optimizer(optimizer_name)
    return optimizer_class(learnable_params, lr=lr)
