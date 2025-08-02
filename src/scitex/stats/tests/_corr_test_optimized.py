#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 05:10:00"
# File: _corr_test_optimized.py

"""
Optimized correlation test implementation using vectorized operations.
"""

from bisect import bisect_right
import numpy as np
from scipy import stats
from typing import Any, Dict, Callable


def _corr_test_base_vectorized(
    data1: np.ndarray,
    data2: np.ndarray,
    only_significant: bool,
    num_permutations: int,
    seed: int,
    corr_func: Callable,
    test_name: str,
) -> Dict[str, Any]:
    """
    Optimized correlation test using vectorized operations.
    
    This version focuses on vectorization rather than parallelization
    for more consistent performance across different data sizes.
    """
    np.random.seed(seed)
    
    # Remove NaN values
    non_nan_indices = ~(np.isnan(data1) | np.isnan(data2))
    data1_clean = data1[non_nan_indices]
    data2_clean = data2[non_nan_indices]
    n_samples = len(data1_clean)
    
    # Compute observed correlation
    if test_name == "Pearson":
        # Use numpy's corrcoef for Pearson (faster than scipy)
        corr_matrix = np.corrcoef(data1_clean, data2_clean)
        corr_obs = corr_matrix[0, 1]
        
        # Still need scipy for p-value
        _, p_analytical = stats.pearsonr(data1_clean, data2_clean)
    else:  # Spearman
        corr_obs, p_analytical = corr_func(data1_clean, data2_clean)
    
    # Vectorized permutation test
    if test_name == "Pearson" and num_permutations >= 100:
        # Optimized vectorized approach for Pearson correlation
        
        # Pre-compute means and stds
        mean1 = np.mean(data1_clean)
        mean2 = np.mean(data2_clean)
        std1 = np.std(data1_clean, ddof=1)
        std2 = np.std(data2_clean, ddof=1)
        
        # Standardize data
        data1_std = (data1_clean - mean1) / std1
        data2_std = (data2_clean - mean2) / std2
        
        # Generate all permutations at once
        surrogate = np.zeros(num_permutations)
        
        # Batch process permutations
        batch_size = min(100, num_permutations)
        for i in range(0, num_permutations, batch_size):
            end_idx = min(i + batch_size, num_permutations)
            batch_perms = end_idx - i
            
            # Generate random permutations for this batch
            perm_indices = np.array([
                np.random.permutation(n_samples) 
                for _ in range(batch_perms)
            ])
            
            # Compute correlations for batch
            for j in range(batch_perms):
                data2_perm = data2_std[perm_indices[j]]
                # Correlation of standardized data
                surrogate[i + j] = np.mean(data1_std * data2_perm)
                
    else:
        # Fall back to original method for Spearman or small permutations
        surrogate = np.array([
            corr_func(data1_clean, np.random.permutation(data2_clean))[0]
            for _ in range(num_permutations)
        ])
    
    # Calculate p-value using permutation test
    rank = bisect_right(sorted(surrogate), corr_obs)
    p_perm = min(rank, num_permutations - rank) / num_permutations * 2
    
    # Use the more conservative p-value
    p_value = max(p_perm, p_analytical) if p_analytical is not None else p_perm
    
    # Get stars for significance
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
        "p_value": round(p_value, 3),
        "stars": stars,
        "effsize": round(effect_size, 3),
        "corr": round(corr_obs, 3),
        "surrogate": surrogate,
        "n": n_samples,
        "test_name": f"Permutation-based {test_name} correlation",
        "statistic": round(corr_obs, 3),
        "H0": f"There is no {test_name.lower()} correlation between the two variables",
    }


def corr_test_optimized(
    data1: np.ndarray,
    data2: np.ndarray,
    test: str = "pearson",
    only_significant: bool = False,
    num_permutations: int = 1_000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Optimized correlation test.
    
    Parameters
    ----------
    data1 : np.ndarray
        First dataset
    data2 : np.ndarray
        Second dataset
    test : str
        'pearson' or 'spearman'
    only_significant : bool
        Only return significant results
    num_permutations : int
        Number of permutations
    seed : int
        Random seed
        
    Returns
    -------
    Dict[str, Any]
        Test results
    """
    if test.lower() == "pearson":
        corr_func = stats.pearsonr
        test_name = "Pearson"
    elif test.lower() == "spearman":
        corr_func = stats.spearmanr
        test_name = "Spearman"
    else:
        raise ValueError("test must be 'pearson' or 'spearman'")
    
    return _corr_test_base_vectorized(
        data1, data2,
        only_significant,
        num_permutations,
        seed,
        corr_func,
        test_name
    )