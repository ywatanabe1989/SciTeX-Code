#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 04:40:00"
# File: _load_cache.py

"""
File load caching infrastructure for scitex.io module.
Provides intelligent caching with file modification detection.
"""

import os
import hashlib
import weakref
from functools import lru_cache
from typing import Any, Tuple, Optional, Dict
from scitex import logging

# Cache for file metadata (path -> (mtime, size, hash))
_file_metadata_cache: Dict[str, Tuple[float, int, str]] = {}

# Weak reference cache for actual data
_file_data_cache = weakref.WeakValueDictionary()

# Cache statistics
_cache_stats = {
    'hits': 0,
    'misses': 0,
    'evictions': 0
}

# Configuration
_cache_config = {
    'enabled': True,
    'max_size': 32,  # Maximum number of files to track
    'verbose': False
}


def get_file_key(file_path: str) -> Tuple[str, float, int]:
    """
    Get cache key based on file path, modification time, and size.
    
    Parameters
    ----------
    file_path : str
        Path to the file
        
    Returns
    -------
    Tuple[str, float, int]
        Tuple of (absolute_path, mtime, size)
    """
    abs_path = os.path.abspath(file_path)
    stat = os.stat(abs_path)
    return (abs_path, stat.st_mtime, stat.st_size)


def get_file_hash(file_path: str) -> str:
    """
    Get a hash based on file metadata.
    
    Parameters
    ----------
    file_path : str
        Path to the file
        
    Returns
    -------
    str
        MD5 hash of file metadata
    """
    key = get_file_key(file_path)
    hash_input = f"{key[0]}:{key[1]}:{key[2]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def is_cache_valid(file_path: str) -> bool:
    """
    Check if cached data for a file is still valid.
    
    Parameters
    ----------
    file_path : str
        Path to the file
        
    Returns
    -------
    bool
        True if cache is valid, False otherwise
    """
    abs_path = os.path.abspath(file_path)
    
    if abs_path not in _file_metadata_cache:
        return False
    
    # Get current file metadata
    try:
        current_key = get_file_key(file_path)
        cached_mtime, cached_size, cached_hash = _file_metadata_cache[abs_path]
        
        # Check if file has been modified
        return (current_key[1] == cached_mtime and 
                current_key[2] == cached_size)
    except (OSError, KeyError):
        return False


def get_cached_data(file_path: str) -> Optional[Any]:
    """
    Retrieve cached data if available and valid.
    
    Parameters
    ----------
    file_path : str
        Path to the file
        
    Returns
    -------
    Optional[Any]
        Cached data if available, None otherwise
    """
    if not _cache_config['enabled']:
        return None
    
    abs_path = os.path.abspath(file_path)
    
    # Check if cache is valid
    if not is_cache_valid(file_path):
        _cache_stats['misses'] += 1
        return None
    
    # Try to get data from weak reference cache
    if abs_path in _file_data_cache:
        _cache_stats['hits'] += 1
        if _cache_config['verbose']:
            logging.info(f"[Cache HIT] {file_path}")
        return _file_data_cache[abs_path]
    
    _cache_stats['misses'] += 1
    return None


def cache_data(file_path: str, data: Any) -> None:
    """
    Cache data for a file.
    
    Parameters
    ----------
    file_path : str
        Path to the file
    data : Any
        Data to cache
    """
    if not _cache_config['enabled']:
        return
    
    abs_path = os.path.abspath(file_path)
    
    # Update metadata cache
    key = get_file_key(file_path)
    _file_metadata_cache[abs_path] = (key[1], key[2], get_file_hash(file_path))
    
    # Try to cache the data (may fail for non-weakref-able types)
    try:
        # For numpy arrays and other special types, we need to wrap them
        if hasattr(data, '__array__'):
            # Numpy arrays can't be weakly referenced directly
            # We'll skip caching for now (could implement a wrapper)
            pass
        else:
            _file_data_cache[abs_path] = data
    except TypeError:
        # Some objects can't be weakly referenced
        if _cache_config['verbose']:
            logging.debug(f"Cannot cache {type(data).__name__} objects")
    
    # Implement cache size limit
    if len(_file_metadata_cache) > _cache_config['max_size']:
        # Remove oldest entries (simple FIFO for metadata)
        oldest = list(_file_metadata_cache.keys())[0]
        del _file_metadata_cache[oldest]
        _cache_stats['evictions'] += 1


def clear_cache() -> None:
    """Clear all cached data."""
    _file_metadata_cache.clear()
    _file_data_cache.clear()
    _numpy_cache_keys.clear()
    _cached_load_npy.cache_clear()  # Clear LRU cache
    _cache_stats['hits'] = 0
    _cache_stats['misses'] = 0
    _cache_stats['evictions'] = 0


def get_cache_info() -> Dict[str, Any]:
    """
    Get cache statistics and configuration.
    
    Returns
    -------
    Dict[str, Any]
        Cache information including stats and config
    """
    return {
        'stats': _cache_stats.copy(),
        'config': _cache_config.copy(),
        'metadata_size': len(_file_metadata_cache),
        'data_size': len(_file_data_cache)
    }


def configure_cache(enabled: Optional[bool] = None,
                   max_size: Optional[int] = None,
                   verbose: Optional[bool] = None) -> None:
    """
    Configure cache settings.
    
    Parameters
    ----------
    enabled : Optional[bool]
        Enable or disable caching
    max_size : Optional[int]
        Maximum number of files to cache
    verbose : Optional[bool]
        Enable verbose logging
    """
    if enabled is not None:
        _cache_config['enabled'] = enabled
    if max_size is not None:
        _cache_config['max_size'] = max_size
    if verbose is not None:
        _cache_config['verbose'] = verbose


# Track numpy cache separately  
_numpy_cache_keys = set()

# Specialized cache for numpy arrays (using LRU cache)
@lru_cache(maxsize=16)
def _cached_load_npy(file_key: Tuple[str, float, int]) -> Any:
    """
    Cached numpy loader using LRU cache.
    
    Parameters
    ----------
    file_key : Tuple[str, float, int]
        Cache key (path, mtime, size)
        
    Returns
    -------
    Any
        Loaded numpy array
    """
    file_path = file_key[0]
    # Import here to avoid circular imports
    from ._load_modules._numpy import _load_npy
    result = _load_npy(file_path)
    
    # Track that we've cached this key
    _numpy_cache_keys.add(file_key)
    
    return result


def load_npy_cached(file_path: str, **kwargs) -> Any:
    """
    Load numpy file with caching.
    
    Parameters
    ----------
    file_path : str
        Path to numpy file
    **kwargs
        Additional arguments for numpy.load
        
    Returns
    -------
    Any
        Loaded numpy array
    """
    if not _cache_config['enabled']:
        from ._load_modules._numpy import _load_npy
        return _load_npy(file_path, **kwargs)
    
    # Check if we have a cache hit
    file_key = get_file_key(file_path)
    
    # Check if this key is already cached
    if file_key in _numpy_cache_keys:
        _cache_stats['hits'] += 1
        if _cache_config['verbose']:
            print(f"[Cache HIT] Loaded from cache: {file_path}")
    else:
        _cache_stats['misses'] += 1
        if _cache_config['verbose']:
            print(f"[Cache MISS] Loading from disk: {file_path}")
    
    # Use LRU cache for numpy files
    return _cached_load_npy(file_key)


# EOF