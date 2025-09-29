#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-14 11:00:03 (ywatanabe)"
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

    def __init__(self, seed: int = 42, verbose=False):
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

    def _auto_fix_seeds(self, verbose=None):
        """Automatically detect and fix ALL available random modules."""
        # Use instance verbose if not specified
        if verbose is None:
            verbose = self.verbose

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
            fixed_modules.append("numpy")
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
                fixed_modules.append("torch+cuda")
            else:
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

        if verbose and fixed_modules:
            print(f"Fixed random seeds for: {', '.join(fixed_modules)}")

    def get_np_generator(self, name: str):
        """
        Get or create a named NumPy random generator.

        Parameters
        ----------
        name : str
            Generator name (e.g., "data", "model", "augment")

        Returns
        -------
        numpy.random.Generator
            Independent NumPy random generator

        Examples
        --------
        >>> rng = RandomStateManager(42)
        >>> gen = rng.get_np_generator("data")
        >>> values = gen.random(100)
        >>> perm = gen.permutation(100)
        """
        if self._np is None:
            raise ImportError("NumPy required for random generators")

        if name not in self._generators:
            # Create deterministic seed from name
            name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
            seed = (self.seed + name_hash) % (2**32)
            self._generators[name] = self._np.random.default_rng(seed)

        return self._generators[name]
    
    def __call__(self, name: str, verbose: bool = None):
        """
        Get or create a named NumPy random generator.
        
        This is a backward compatibility wrapper for get_np_generator().
        Consider using get_np_generator() directly for clarity.
        
        Parameters
        ----------
        name : str
            Generator name
        verbose : bool, optional
            Whether to show deprecation warning
        
        Returns
        -------
        numpy.random.Generator
            NumPy random generator with deterministic seed
        """
        if verbose:
            print(f"Note: rng('{name}') is deprecated. Use rng.get_np_generator('{name}') instead.")
        return self.get_np_generator(name)

    def verify(self, obj: Any, name: str = None, verbose: bool = True) -> bool:
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

        # Use instance verbose if not specified
        if verbose is None:
            verbose = self.verbose

        # Check cache
        if cache_file.exists():
            with open(cache_file, "r") as f:
                cached = json.load(f)

            matches = cached["hash"] == obj_hash
            if not matches and verbose:
                print(f"⚠️  Reproducibility broken for '{name}'!")
                print(f"   Expected: {cached['hash'][:16]}...")
                print(f"   Got:      {obj_hash[:16]}...")
                raise ValueError(
                    f"Reproducibility verification failed for '{name}'"
                )
            elif matches and verbose:
                print(f"✓ Reproducibility verified for '{name}'")

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

    def get_sklearn_random_state(self, name: str):
        """
        Get a random state for scikit-learn.

        Scikit-learn uses integers for random_state parameter.

        Parameters
        ----------
        name : str
            Generator name

        Returns
        -------
        int
            Random state integer for sklearn

        Examples
        --------
        >>> rng = RandomStateManager(42)
        >>> from sklearn.model_selection import train_test_split
        >>> X_train, X_test = train_test_split(
        ...     X, test_size=0.2,
        ...     random_state=rng.get_sklearn_random_state("split")
        ... )
        """
        # Create deterministic seed from name
        name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        seed = (self.seed + name_hash) % (2**32)
        return seed

    def get_torch_generator(self, name: str):
        """
        Get or create a named PyTorch generator.

        Parameters
        ----------
        name : str
            Generator name

        Returns
        -------
        torch.Generator
            PyTorch generator with deterministic seed

        Examples
        --------
        >>> rng = RandomStateManager(42)
        >>> gen = rng.get_torch_generator("model")
        >>> torch.randn(5, 5, generator=gen)
        """
        try:
            import torch
        except ImportError:
            raise ImportError("PyTorch not installed")

        if not hasattr(self, "_torch_generators"):
            self._torch_generators = {}

        if name not in self._torch_generators:
            # Create deterministic seed from name
            name_hash = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
            seed = (self.seed + name_hash) % (2**32)

            gen = torch.Generator()
            gen.manual_seed(seed)
            self._torch_generators[name] = gen

        return self._torch_generators[name]

    def get_generator(self, name: str):
        """Alias for get_np_generator for compatibility."""
        return self.get_np_generator(name)
    
    def clear_cache(self, patterns: str | list[str] = None) -> int:
        """
        Clear verification cache files.
        
        Parameters
        ----------
        patterns : str or list of str, optional
            Specific cache patterns to clear. If None, clears all.
            Can be:
            - Single name: "my_data"
            - List of names: ["data1", "data2"]
            - Glob pattern: "experiment_*"
            - None: clear all cache files
        
        Returns
        -------
        int
            Number of cache files removed
        
        Examples
        --------
        >>> rng = RandomStateManager(42)
        >>> rng.clear_cache()  # Clear all
        >>> rng.clear_cache("old_data")  # Clear specific
        >>> rng.clear_cache(["test1", "test2"])  # Clear multiple
        >>> rng.clear_cache("experiment_*")  # Clear pattern
        """
        import glob
        
        if not self._cache_dir.exists():
            return 0
        
        removed_count = 0
        
        if patterns is None:
            # Clear all .json files
            cache_files = list(self._cache_dir.glob("*.json"))
            for cache_file in cache_files:
                cache_file.unlink()
                removed_count += 1
        else:
            # Ensure patterns is a list
            if isinstance(patterns, str):
                patterns = [patterns]
            
            for pattern in patterns:
                # Handle glob patterns
                if "*" in pattern or "?" in pattern:
                    cache_files = list(self._cache_dir.glob(f"{pattern}.json"))
                else:
                    # Exact match
                    cache_file = self._cache_dir / f"{pattern}.json"
                    cache_files = [cache_file] if cache_file.exists() else []
                
                for cache_file in cache_files:
                    cache_file.unlink()
                    removed_count += 1
        
        return removed_count


def get(verbose: bool = False) -> RandomStateManager:
    """
    Get or create the global RandomStateManager instance.

    Parameters
    ----------
    verbose : bool, optional
        Whether to print status messages (default: False)

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
        _GLOBAL_INSTANCE = RandomStateManager(42, verbose=verbose)

    return _GLOBAL_INSTANCE


def reset(seed: int = 42, verbose: bool = False) -> RandomStateManager:
    """
    Reset global RandomStateManager with new seed.

    Parameters
    ----------
    seed : int
        New seed value
    verbose : bool, optional
        Whether to print status messages (default: False)

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
    _GLOBAL_INSTANCE = RandomStateManager(seed, verbose=verbose)
    return _GLOBAL_INSTANCE

# EOF
