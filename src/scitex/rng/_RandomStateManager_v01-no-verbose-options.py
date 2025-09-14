#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-14 09:51:10 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/rng/_RandomStateManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/rng/_RandomStateManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Clean, simple RandomStateManager for scientific reproducibility.

Main API:
    rng = RandomStateManager(seed=42)   # Create instance
    gen = rng("name")                   # Get named generator
    rng.verify(obj, "name")             # Verify reproducibility
"""

import hashlib
import json
import pickle
from contextlib import contextmanager
from pathlib import Path
from typing import Any

# Global singleton instance
_GLOBAL_INSTANCE = None


class RandomStateManager:
    """
    Simple, robust random state manager for scientific computing.

    Examples
    --------
    >>> import scitex as stx
    >>>
    >>> # Method 1: Direct usage
    >>> rng = stx.rng.RandomStateManager(seed=42)
    >>> data = rng("data").random(100)
    >>>
    >>> # Method 2: From session.start
    >>> CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(seed=42)
    >>> model = rng("model").normal(size=(10, 10))
    >>>
    >>> # Verify reproducibility
    >>> rng.verify(data, "my_data")
    """

    def __init__(self, seed: int = 42, verbose=True):
        """Initialize with automatic module detection."""
        self.seed = seed
        self.verbose = verbose
        self._generators = {}
        self._cache_dir = Path.home() / ".scitex" / "rng"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"RandomStateManager initialized with seed {seed}")

        # Auto-fix all available seeds
        self._auto_fix_seeds(verbose=verbose)

    def _auto_fix_seeds(self, verbose=True):
        """Automatically detect and fix ALL available random modules."""
        # OS environment
        os.environ["PYTHONHASHSEED"] = str(self.seed)
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

        fixed_modules = []

        # Python random
        try:
            import random

            random.seed(self.seed)
            fixed_modules.append("random")
        except ImportError:
            pass

        # NumPy
        try:
            import numpy as np

            np.random.seed(self.seed)
            # Also set default_rng for new API
            self._np = np
            self._np_default_rng = np.random.default_rng(self.seed)
            fixed_modules.append("np")
        except ImportError:
            self._np = None

        # PyTorch
        try:
            import torch

            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
            fixed_modules.append("torch")
        except ImportError:
            pass

        # TensorFlow
        try:
            import tensorflow as tf

            tf.random.set_seed(self.seed)
            fixed_modules.append("tensorflow")
        except ImportError:
            pass

        # JAX
        try:
            import jax

            self._jax_key = jax.random.PRNGKey(self.seed)
            fixed_modules.append("jax")
        except ImportError:
            pass

        if verbose or self.verbose:
            print(f"Fixed random seeds for {fixed_modules}")

    def __call__(self, name: str, verbose=False):
        """
        Get or create a named random generator.

        Parameters
        ----------
        name : str
            Generator name (e.g., "data", "model", "augment")

        Returns
        -------
        numpy.random.Generator
            Independent random generator

        Examples
        --------
        >>> rng = RandomStateManager(42)
        >>> data_gen = rng("data")
        >>> values = data_gen.random(100)
        """
        if self._np is None:
            raise ImportError("NumPy required for random generators")

        if name not in self._generators:
            # Create deterministic seed from name
            name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
            seed = (self.seed + name_hash) % (2**32)
            self._generators[name] = self._np.random.default_rng(seed)

        return self._generators[name]

    def verify(self, obj: Any, name: str = None) -> bool:
        """
        Verify object matches cached hash (detects broken reproducibility).

        First call: caches the object's hash
        Later calls: verifies object matches cached hash

        Parameters
        ----------
        obj : Any
            Object to verify (array, tensor, data, model weights, etc.)
            Supports: numpy arrays, torch tensors, tf tensors, jax arrays,
            lists, dicts, pandas dataframes, and basic types
        name : str, optional
            Cache name. Auto-generated if not provided.

        Returns
        -------
        bool
            True if matches cache (or first call), False if different

        Examples
        --------
        >>> data = generate_data()
        >>> rng.verify(data, "train_data")  # First run: caches
        >>> # Next run:
        >>> rng.verify(data, "train_data")  # Verifies match
        """
        import numpy as np

        # Auto-generate name if needed
        if name is None:
            import inspect

            frame = inspect.currentframe().f_back
            filename = Path(frame.f_code.co_filename).stem
            lineno = frame.f_lineno
            name = f"{filename}_L{lineno}"

        # Sanitize name
        safe_name = "".join(
            c if c.isalnum() or c in "-_" else "_" for c in name
        )
        cache_file = self._cache_dir / f"{safe_name}.json"

        # Compute hash based on object type
        obj_hash = self._compute_hash(obj)

        # Check cache
        if cache_file.exists():
            with open(cache_file, "r") as f:
                cached = json.load(f)

            matches = cached["hash"] == obj_hash
            if not matches:
                print(f"⚠️  Reproducibility broken for '{name}'!")
                print(f"   Expected: {cached['hash'][:16]}...")
                print(f"   Got:      {obj_hash[:16]}...")
            return matches
        else:
            # First call - cache it
            with open(cache_file, "w") as f:
                json.dump(
                    {"name": name, "hash": obj_hash, "seed": self.seed}, f
                )
            return True

    def _compute_hash(self, obj: Any) -> str:
        """
        Compute hash for various object types.

        Supports:
        - NumPy arrays
        - PyTorch tensors
        - TensorFlow tensors
        - JAX arrays
        - Pandas DataFrames/Series
        - Lists, tuples, dicts
        - Basic types (int, float, str, bool)
        """
        import numpy as np

        # NumPy array
        if isinstance(obj, np.ndarray):
            return hashlib.sha256(obj.tobytes()).hexdigest()[:32]

        # PyTorch tensor
        try:
            import torch

            if isinstance(obj, torch.Tensor):
                # Move to CPU and convert to numpy for consistent hashing
                obj_np = obj.detach().cpu().numpy()
                return hashlib.sha256(obj_np.tobytes()).hexdigest()[:32]
        except ImportError:
            pass

        # TensorFlow tensor
        try:
            import tensorflow as tf

            if isinstance(obj, (tf.Tensor, tf.Variable)):
                obj_np = obj.numpy()
                return hashlib.sha256(obj_np.tobytes()).hexdigest()[:32]
        except ImportError:
            pass

        # JAX array
        try:
            import jax.numpy as jnp

            if isinstance(obj, jnp.ndarray):
                obj_np = np.array(obj)
                return hashlib.sha256(obj_np.tobytes()).hexdigest()[:32]
        except ImportError:
            pass

        # Pandas DataFrame/Series
        try:
            import pandas as pd

            if isinstance(obj, (pd.DataFrame, pd.Series)):
                # Use pandas string representation for hashing
                obj_str = obj.to_json(orient="split", date_format="iso")
                return hashlib.sha256(obj_str.encode()).hexdigest()[:32]
        except ImportError:
            pass

        # Lists and tuples - convert to numpy array if numeric
        if isinstance(obj, (list, tuple)):
            try:
                obj_np = np.array(obj)
                if obj_np.dtype != object:  # Numeric array
                    return hashlib.sha256(obj_np.tobytes()).hexdigest()[:32]
            except:
                pass
            # Fall through to string representation

        # Dictionaries - serialize to JSON
        if isinstance(obj, dict):
            try:
                obj_str = json.dumps(obj, sort_keys=True, default=str)
                return hashlib.sha256(obj_str.encode()).hexdigest()[:32]
            except:
                pass

        # Default: convert to string
        obj_str = str(obj)
        return hashlib.sha256(obj_str.encode()).hexdigest()[:32]

    def checkpoint(self, name: str = "checkpoint"):
        """Save current state of all generators."""
        checkpoint_file = self._cache_dir / f"{name}.pkl"
        state = {
            "seed": self.seed,
            "generators": {
                k: v.bit_generator.state for k, v in self._generators.items()
            },
        }
        with open(checkpoint_file, "wb") as f:
            pickle.dump(state, f)
        return checkpoint_file

    def restore(self, checkpoint):
        """Restore from checkpoint."""
        if isinstance(checkpoint, str):
            checkpoint = Path(checkpoint)

        with open(checkpoint, "rb") as f:
            state = pickle.load(f)

        self.seed = state["seed"]
        self._auto_fix_seeds()

        # Restore generator states
        for name, gen_state in state["generators"].items():
            gen = self(name)
            gen.bit_generator.state = gen_state

    @contextmanager
    def temporary_seed(self, seed: int):
        """Context manager for temporary seed change."""
        import random

        import numpy as np

        # Save current states
        old_random_state = random.getstate()
        old_np_state = np.random.get_state() if self._np else None

        # Set temporary seed
        random.seed(seed)
        if self._np:
            np.random.seed(seed)

        try:
            yield
        finally:
            # Restore states
            random.setstate(old_random_state)
            if self._np and old_np_state:
                np.random.set_state(old_np_state)

    def get_generator(self, name: str):
        """Alias for __call__ for compatibility."""
        return self(name)


def get() -> RandomStateManager:
    """
    Get or create the global RandomStateManager instance.

    Returns
    -------
    RandomStateManager
        Global instance

    Examples
    --------
    >>> import scitex as stx
    >>> rng = stx.rng.get()
    >>> data = rng("data").random(100)
    """
    global _GLOBAL_INSTANCE

    if _GLOBAL_INSTANCE is None:
        _GLOBAL_INSTANCE = RandomStateManager(42)

    return _GLOBAL_INSTANCE


def reset(seed: int = 42) -> RandomStateManager:
    """
    Reset global RandomStateManager with new seed.

    Parameters
    ----------
    seed : int
        New seed value

    Returns
    -------
    RandomStateManager
        New global instance

    Examples
    --------
    >>> import scitex as stx
    >>> rng = stx.rng.reset(seed=123)
    """
    global _GLOBAL_INSTANCE
    _GLOBAL_INSTANCE = RandomStateManager(seed)
    return _GLOBAL_INSTANCE

# EOF
