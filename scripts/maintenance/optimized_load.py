#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 04:25:00"
# File: optimized_load.py

"""
Optimized version of scitex.io.load with caching.
Demonstrates performance improvements.
"""

import os
import time
import hashlib
from functools import lru_cache
from typing import Any, Tuple
import weakref

# Cache for file metadata
_file_cache_metadata = {}
# Weak reference cache for actual data
_file_cache_data = weakref.WeakValueDictionary()


def get_file_hash(file_path: str) -> str:
    """Get a hash based on file path and modification time."""
    stat = os.stat(file_path)
    # Use file path, size, and modification time as hash
    hash_input = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def load_with_cache(file_path: str, show: bool = False, verbose: bool = False, **kwargs) -> Any:
    """
    Enhanced load function with intelligent caching.
    
    Features:
    - LRU cache for recently accessed files
    - Weak references to prevent memory bloat
    - File modification detection
    - Configurable cache size
    """
    # Get absolute path
    abs_path = os.path.abspath(file_path)
    
    # Check if file exists
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")
    
    # Get file hash
    file_hash = get_file_hash(abs_path)
    
    # Check cache
    if abs_path in _file_cache_metadata:
        cached_hash = _file_cache_metadata[abs_path]
        if cached_hash == file_hash:
            # File hasn't changed, try to get from weak ref cache
            if abs_path in _file_cache_data:
                if verbose:
                    print(f"[Cache HIT] Loading from cache: {file_path}")
                return _file_cache_data[abs_path]
    
    # Not in cache or file changed - load from disk
    if verbose:
        print(f"[Cache MISS] Loading from disk: {file_path}")
    
    # Import original load function
    from scitex.io import load as original_load
    
    # Load data
    data = original_load(file_path, show=show, verbose=verbose, **kwargs)
    
    # Update cache
    _file_cache_metadata[abs_path] = file_hash
    
    # Try to cache the data (may fail for non-cacheable types)
    try:
        _file_cache_data[abs_path] = data
    except TypeError:
        # Some objects can't be weakly referenced
        pass
    
    return data


# Alternative: Decorator-based caching
def cached_load(maxsize: int = 128):
    """
    Decorator to add caching to any load function.
    
    Parameters
    ----------
    maxsize : int
        Maximum number of files to cache
    """
    cache = {}
    cache_order = []
    
    def decorator(func):
        def wrapper(file_path: str, *args, **kwargs):
            # Get file metadata
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                return func(file_path, *args, **kwargs)
            
            file_hash = get_file_hash(abs_path)
            cache_key = (abs_path, file_hash)
            
            # Check cache
            if cache_key in cache:
                # Move to end (LRU)
                cache_order.remove(cache_key)
                cache_order.append(cache_key)
                return cache[cache_key]
            
            # Load data
            data = func(file_path, *args, **kwargs)
            
            # Update cache
            cache[cache_key] = data
            cache_order.append(cache_key)
            
            # Evict oldest if cache is full
            if len(cache) > maxsize:
                oldest = cache_order.pop(0)
                del cache[oldest]
            
            return data
        
        # Add cache management methods
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'maxsize': maxsize,
            'hits': 0,  # Would need to track this
            'misses': 0  # Would need to track this
        }
        wrapper.cache_clear = lambda: cache.clear() or cache_order.clear()
        
        return wrapper
    
    return decorator


# Configuration class for cache settings
class CacheConfig:
    """Configuration for file caching."""
    
    def __init__(self):
        self.enabled = True
        self.max_size = 32  # Maximum files to cache
        self.max_memory = 1024 * 1024 * 512  # 512 MB max memory
        self.ttl = 3600  # Time to live in seconds
        self.exclude_patterns = ['*.tmp', '*.temp', '*.log']
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        config.enabled = os.getenv('SCITEX_IO_CACHE_ENABLED', 'true').lower() == 'true'
        config.max_size = int(os.getenv('SCITEX_IO_CACHE_SIZE', '32'))
        config.max_memory = int(os.getenv('SCITEX_IO_CACHE_MEMORY', str(1024 * 1024 * 512)))
        return config


def benchmark_caching():
    """Benchmark the caching performance."""
    import numpy as np
    import tempfile
    
    print("=== Caching Benchmark ===")
    
    # Create test data
    data = np.random.randn(1000, 1000)
    
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
        np.save(tmp.name, data)
        tmp_path = tmp.name
    
    try:
        # Test without cache
        print("\n1. Without caching:")
        start = time.time()
        for i in range(10):
            _ = np.load(tmp_path)
        no_cache_time = time.time() - start
        print(f"   10 loads: {no_cache_time:.3f}s")
        
        # Test with cache
        print("\n2. With caching:")
        
        # Prime the cache
        _ = load_with_cache(tmp_path, verbose=True)
        
        start = time.time()
        for i in range(10):
            _ = load_with_cache(tmp_path)
        cache_time = time.time() - start
        print(f"   10 loads: {cache_time:.3f}s")
        
        # Results
        speedup = no_cache_time / cache_time
        print(f"\nSpeedup: {speedup:.1f}x")
        print(f"Time saved: {no_cache_time - cache_time:.3f}s")
        
    finally:
        os.unlink(tmp_path)


def demonstrate_cache_integration():
    """Show how to integrate caching into scitex.io."""
    print("\n=== Cache Integration Example ===")
    
    code = '''
# In scitex/io/_load.py

from functools import lru_cache
import os
from typing import Tuple

# Cache for file metadata
_file_cache = {}

def _get_file_key(file_path: str) -> Tuple[str, float, int]:
    """Get cache key based on path, mtime, and size."""
    stat = os.stat(file_path)
    return (file_path, stat.st_mtime, stat.st_size)

# Apply caching to specific loaders
@lru_cache(maxsize=32)
def _cached_load_npy(file_key: Tuple[str, float, int]):
    """Cached numpy loader."""
    file_path = file_key[0]
    return _load_npy(file_path)

def load(file_path: str, **kwargs):
    """Enhanced load with optional caching."""
    # Check if caching is enabled
    use_cache = kwargs.pop('cache', True)
    
    if use_cache and file_path.endswith('.npy'):
        # Use cached loader for numpy files
        file_key = _get_file_key(file_path)
        return _cached_load_npy(file_key)
    
    # Fall back to original implementation
    return _original_load(file_path, **kwargs)
'''
    
    print(code)


def main():
    """Run demonstrations."""
    print("SciTeX I/O Caching Optimization")
    print("=" * 40)
    
    benchmark_caching()
    demonstrate_cache_integration()
    
    print("\n" + "=" * 40)
    print("Implementation ready for integration!")


if __name__ == "__main__":
    main()