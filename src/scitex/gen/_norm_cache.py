#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:15:00"
# File: _norm_cache.py

"""
Cached normalization functions for improved performance on repeated operations.
"""

import torch
import numpy as np
import weakref
from functools import lru_cache
from typing import Union, Tuple, Optional
import hashlib

from ..decorators import torch_fn


# Cache for normalized data
_norm_cache = weakref.WeakValueDictionary()
_cache_metadata = {}
_cache_config = {
    'enabled': True,
    'max_size': 64,
    'verbose': False
}


def _get_array_key(x: Union[np.ndarray, torch.Tensor], axis: Optional[int] = None) -> str:
    """
    Generate a unique key for an array based on its content and parameters.
    
    Parameters
    ----------
    x : array-like
        Input array
    axis : int, optional
        Axis parameter
        
    Returns
    -------
    str
        Unique hash key
    """
    # Create a hash based on array properties
    if isinstance(x, torch.Tensor):
        # For tensors, use shape, dtype, device, and a sample of values
        props = f"torch_{x.shape}_{x.dtype}_{x.device}_{axis}"
        # Sample a few values for hash (avoid full array for performance)
        if x.numel() > 100:
            sample = x.flatten()[::max(1, x.numel() // 100)][:100]
        else:
            sample = x.flatten()
        props += f"_{sample.sum().item():.6f}_{sample.std().item():.6f}"
    else:
        # For numpy arrays
        props = f"numpy_{x.shape}_{x.dtype}_{axis}"
        if x.size > 100:
            sample = x.flatten()[::max(1, x.size // 100)][:100]
        else:
            sample = x.flatten()
        props += f"_{np.sum(sample):.6f}_{np.std(sample):.6f}"
    
    return hashlib.md5(props.encode()).hexdigest()


def _check_cache(key: str, x: Union[np.ndarray, torch.Tensor]) -> Optional[Union[np.ndarray, torch.Tensor]]:
    """Check if cached result exists and is valid."""
    if not _cache_config['enabled']:
        return None
        
    if key in _cache_metadata:
        # Verify array hasn't changed by checking a few properties
        cached_info = _cache_metadata[key]
        
        if isinstance(x, torch.Tensor):
            current_sum = x.sum().item()
            current_mean = x.mean().item()
        else:
            current_sum = np.sum(x)
            current_mean = np.mean(x)
            
        # Check if values match (within floating point tolerance)
        if (abs(cached_info['sum'] - current_sum) < 1e-10 and 
            abs(cached_info['mean'] - current_mean) < 1e-10):
            
            # Try to get from weak reference cache
            if key in _norm_cache:
                if _cache_config['verbose']:
                    print(f"[Norm Cache HIT] {cached_info['op']}")
                return _norm_cache[key]
                
    return None


def _store_cache(key: str, x: Union[np.ndarray, torch.Tensor], 
                result: Union[np.ndarray, torch.Tensor], op: str) -> None:
    """Store result in cache."""
    if not _cache_config['enabled']:
        return
        
    # Store metadata
    if isinstance(x, torch.Tensor):
        _cache_metadata[key] = {
            'sum': x.sum().item(),
            'mean': x.mean().item(),
            'shape': x.shape,
            'op': op
        }
    else:
        _cache_metadata[key] = {
            'sum': np.sum(x),
            'mean': np.mean(x),
            'shape': x.shape,
            'op': op
        }
    
    # Try to store in weak reference cache
    try:
        _norm_cache[key] = result
    except TypeError:
        # Some types can't be weakly referenced
        pass
        
    # Implement size limit
    if len(_cache_metadata) > _cache_config['max_size']:
        # Remove oldest entries
        oldest = list(_cache_metadata.keys())[0]
        del _cache_metadata[oldest]
        if oldest in _norm_cache:
            del _norm_cache[oldest]


# Cached version of to_z
@torch_fn
def to_z_cached(x, axis=-1, dim=None, device="cuda"):
    """
    Cached version of z-score normalization.
    
    Caches results for repeated normalizations of the same data.
    """
    # Generate cache key
    dimension = dim if dim is not None else axis
    cache_key = _get_array_key(x, dimension) + "_z"
    
    # Check cache
    cached = _check_cache(cache_key, x)
    if cached is not None:
        return cached
    
    # Compute normalization
    if isinstance(x, torch.Tensor):
        result = (x - x.mean(dim=dimension, keepdim=True)) / x.std(dim=dimension, keepdim=True)
    else:
        result = (x - np.mean(x, axis=dimension, keepdims=True)) / np.std(x, axis=dimension, keepdims=True)
    
    # Store in cache
    _store_cache(cache_key, x, result, "z-score")
    
    return result


# Cached version of to_01
@torch_fn  
def to_01_cached(x, axis=-1, dim=None, device="cuda"):
    """
    Cached version of min-max normalization.
    
    Caches results for repeated normalizations of the same data.
    """
    # Generate cache key
    dimension = dim if dim is not None else axis
    cache_key = _get_array_key(x, dimension) + "_01"
    
    # Check cache
    cached = _check_cache(cache_key, x)
    if cached is not None:
        return cached
    
    # Compute normalization
    if isinstance(x, torch.Tensor):
        if dimension is None:
            x_min = x.min()
            x_max = x.max()
        else:
            x_min = x.min(dim=dimension, keepdim=True)[0]
            x_max = x.max(dim=dimension, keepdim=True)[0]
        result = (x - x_min) / (x_max - x_min + 1e-8)
    else:
        if dimension is None:
            x_min = np.min(x)
            x_max = np.max(x)
        else:
            x_min = np.min(x, axis=dimension, keepdims=True)
            x_max = np.max(x, axis=dimension, keepdims=True)
        result = (x - x_min) / (x_max - x_min + 1e-8)
    
    # Store in cache
    _store_cache(cache_key, x, result, "min-max")
    
    return result


def configure_norm_cache(enabled: Optional[bool] = None,
                        max_size: Optional[int] = None,
                        verbose: Optional[bool] = None) -> None:
    """
    Configure normalization cache settings.
    
    Parameters
    ----------
    enabled : bool, optional
        Enable or disable caching
    max_size : int, optional
        Maximum number of arrays to cache
    verbose : bool, optional
        Enable verbose output
    """
    if enabled is not None:
        _cache_config['enabled'] = enabled
    if max_size is not None:
        _cache_config['max_size'] = max_size
    if verbose is not None:
        _cache_config['verbose'] = verbose


def clear_norm_cache() -> None:
    """Clear all cached normalization results."""
    _norm_cache.clear()
    _cache_metadata.clear()


def get_norm_cache_info() -> dict:
    """Get information about the normalization cache."""
    return {
        'enabled': _cache_config['enabled'],
        'max_size': _cache_config['max_size'],
        'current_size': len(_cache_metadata),
        'operations': [v['op'] for v in _cache_metadata.values()]
    }


# Monkey patch the original functions if enabled
def patch_normalization_functions():
    """Replace original normalization functions with cached versions."""
    import scitex.gen._norm as norm_module
    
    # Store originals
    norm_module.to_z_original = norm_module.to_z
    norm_module.to_01_original = norm_module.to_01
    
    # Replace with cached versions
    norm_module.to_z = to_z_cached
    norm_module.to_01 = to_01_cached
    
    # Also patch in the gen module namespace
    try:
        import scitex.gen as gen_module
        gen_module.to_z = to_z_cached
        gen_module.to_01 = to_01_cached
    except:
        pass


# Auto-patch if enabled
import os
if os.getenv('SCITEX_CACHE_NORM', 'true').lower() == 'true':
    patch_normalization_functions()