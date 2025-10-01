#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:00:00"
# File: __corr_test_optimized.py

"""
Optimized correlation test implementation using vectorized operations and parallel processing.
"""

from bisect import bisect_right
import numpy as np
from scipy import stats
from typing import Any, Literal, Dict, Callable
from multiprocessing import Pool, cpu_count
from functools import partial
import warnings


def _compute_correlation_batch(permuted_indices: np.ndarray, data1: np.ndarray, data2: np.ndarray, method: str) -> np.ndarray:
    """
    Compute correlations for a batch of permutations.
    
    Parameters
    ----------
    permuted_indices : np.ndarray
        Array of shape (n_perms, n_samples) containing permutation indices
    data1 : np.ndarray
        First dataset
    data2 : np.ndarray  
        Second dataset
    method : str
        'pearson' or 'spearman'
        
    Returns
    -------
    np.ndarray
        Array of correlation values
    """
    n_perms = permuted_indices.shape[0]
    correlations = np.zeros(n_perms)
    
    if method == 'pearson':
        # Vectorized Pearson correlation
        for i in range(n_perms):
            data2_perm = data2[permuted_indices[i]]
            # Use numpy's corrcoef which is faster than scipy.stats.pearsonr
            correlations[i] = np.corrcoef(data1, data2_perm)[0, 1]
    else:  # spearman
        # Convert to ranks once for data1
        data1_ranks = stats.rankdata(data1)
        for i in range(n_perms):
            data2_perm = data2[permuted_indices[i]]
            data2_ranks = stats.rankdata(data2_perm)
            correlations[i] = np.corrcoef(data1_ranks, data2_ranks)[0, 1]
    
    return correlations


def _corr_test_base_optimized(
    data1: np.ndarray,
    data2: np.ndarray,
    only_significant: bool,
    n_perm: int,
    seed: int,
    corr_func: Callable,
    test_name: str,
    n_jobs: int = -1,
) -> Dict[str, Any]:
    """
    Optimized correlation test using vectorized operations and parallel processing.
    
    Parameters
    ----------
    data1 : np.ndarray
        First dataset
    data2 : np.ndarray
        Second dataset  
    only_significant : bool
        If True, only return significant results
    n_perm : int
        Number of permutations
    seed : int
        Random seed
    corr_func : Callable
        Correlation function (scipy.stats.pearsonr or spearmanr)
    test_name : str
        Name of the test ('Pearson' or 'Spearman')
    n_jobs : int
        Number of parallel jobs (-1 for all CPUs)
        
    Returns
    -------
    Dict[str, Any]
        Test results
    """
    np.random.seed(seed)
    
    # Remove NaN values
    non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
    data1_clean = data1[non_nan_indices]
    data2_clean = data2[non_nan_indices]
    n_samples = len(data1_clean)
    
    # Compute observed correlation
    if test_name == "Pearson":
        # Use numpy's corrcoef for speed
        corr_obs = np.corrcoef(data1_clean, data2_clean)[0, 1]
        _, p_analytical = stats.pearsonr(data1_clean, data2_clean)
    else:
        corr_obs, p_analytical = corr_func(data1_clean, data2_clean)
    
    # For small sample sizes or few permutations, use original method
    if n_samples < 100 or n_perm < 1000:
        # Original method for small datasets
        surrogate = np.array([
            corr_func(data1_clean, np.random.permutation(data2_clean))[0]
            for _ in range(n_perm)
        ])
    else:
        # Optimized parallel method for larger datasets
        
        # Determine number of workers
        if n_jobs == -1:
            n_workers = min(cpu_count(), 8)  # Cap at 8 workers
        else:
            n_workers = min(n_jobs, cpu_count())
        
        # Generate all permutation indices at once
        perm_indices = np.array([
            np.random.permutation(n_samples) for _ in range(n_perm)
        ])
        
        # Split permutations into chunks for parallel processing
        chunk_size = max(n_perm // n_workers, 100)
        chunks = [perm_indices[i:i+chunk_size] for i in range(0, n_perm, chunk_size)]
        
        # Parallel computation
        method = test_name.lower()
        compute_func = partial(_compute_correlation_batch, 
                              data1=data1_clean, 
                              data2=data2_clean,
                              method=method)
        
        if n_workers > 1 and len(chunks) > 1:
            with Pool(n_workers) as pool:
                results = pool.map(compute_func, chunks)
            surrogate = np.concatenate(results)
        else:
            # Single-threaded for small jobs
            surrogate = compute_func(perm_indices)
    
    # Calculate p-value using permutation test
    rank = bisect_right(sorted(surrogate), corr_obs)
    p_perm = min(rank, n_perm - rank) / n_perm * 2
    
    # Use the more conservative p-value
    p_value = max(p_perm, p_analytical) if p_analytical is not None else p_perm
    
    # Import p2stars locally to avoid circular imports
    try:
        from .. import p2stars
        stars = p2stars(p_value)
    except:
        # Fallback star calculation
        if p_value < 0.001:
            stars = "***"
        elif p_value < 0.01:
            stars = "**"
        elif p_value < 0.05:
            stars = "*"
        else:
            stars = ""
    
    effect_size = np.abs(corr_obs)
    
    result_string = (
        f"{test_name} Corr. = {corr_obs:.3f}; p-value = {p_value:.3f} "
        f"(n={n_samples:,}, eff={effect_size:.3f}) {stars}"
    )
    
    if not only_significant or (only_significant and p_value < 0.05):
        print(result_string)
    
    return {
        "corr": round(corr_obs, 3),
        "p_value": round(p_value, 3),
        "p_perm": round(p_perm, 3),
        "p_analytical": round(p_analytical, 3) if p_analytical is not None else None,
        "stars": stars,
        "effsize": round(effect_size, 3),
        "surrogate": surrogate,
        "n": n_samples,
        "test_name": f"Permutation-based {test_name} correlation",
        "statistic": round(corr_obs, 3),
        "H0": f"There is no {test_name.lower()} correlation between the two variables",
    }


# Monkey patch to replace the original implementation
def patch_correlation_functions():
    """Replace original correlation functions with optimized versions."""
    import scitex.stats.tests.__corr_test as corr_test_module
    
    # Store original for fallback
    corr_test_module._corr_test_base_original = corr_test_module._corr_test_base
    
    # Replace with optimized version
    corr_test_module._corr_test_base = _corr_test_base_optimized
    
    # Also update the wrapper if it exists
    try:
        import scitex.stats._corr_test_wrapper as wrapper_module
        wrapper_module._corr_test_base = _corr_test_base_optimized
    except:
        pass


# Auto-patch on import if enabled via environment variable
import os
if os.getenv('SCITEX_OPTIMIZE_STATS', 'true').lower() == 'true':
    patch_correlation_functions()