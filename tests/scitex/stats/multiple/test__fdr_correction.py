#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/multiple/test__fdr_correction.py

import pytest
import numpy as np
import pandas as pd
import torch
import scitex


class TestImports:
    def test_import_main(self):
        import scitex

    def test_import_submodule(self):
        import scitex.stats

    def test_import_target(self):
        import scitex.stats.multiple._fdr_correction
    
    def test_import_from_stats(self):
        # Test that fdr_correction is available from stats module
        assert hasattr(scitex.stats, 'fdr_correction')


class TestFDRCorrectionDataFrame:
    """Test the pandas DataFrame-based FDR correction function."""
    
    def test_basic_functionality(self):
        """Test basic FDR correction on DataFrame."""
        df = pd.DataFrame({
            'p_value': [0.001, 0.008, 0.039, 0.041, 0.042],
            'other_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Check that new columns are added
        assert 'p_value_fdr' in result.columns
        assert 'p_value_fdr_stars' in result.columns
        
        # Check that original columns are preserved
        assert 'p_value' in result.columns
        assert 'other_col' in result.columns
        
        # Check that FDR values are >= original p-values
        assert np.all(result['p_value_fdr'] >= result['p_value'])
    
    def test_multiple_p_value_columns(self):
        """Test with multiple p-value columns."""
        df = pd.DataFrame({
            'p_value': [0.01, 0.02, 0.03],
            'p_value_2': [0.001, 0.05, 0.10],
            'pval': [0.02, 0.04, 0.06],
            'data': [1, 2, 3]
        })
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Should create FDR columns for each p-value column
        assert 'p_value_fdr' in result.columns
        assert 'p_value_fdr_stars' in result.columns
        assert 'p_value_2_fdr' in result.columns
        assert 'p_value_2_fdr_stars' in result.columns
        assert 'pval_fdr' in result.columns
        assert 'pval_fdr_stars' in result.columns
    
    def test_with_nan_values(self):
        """Test handling of NaN values in p-value column."""
        df = pd.DataFrame({
            'p_value': [0.01, np.nan, 0.03, 0.04, np.nan],
            'id': [1, 2, 3, 4, 5]
        })
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Check that NaN values are preserved
        assert pd.isna(result.loc[1, 'p_value_fdr'])
        assert pd.isna(result.loc[4, 'p_value_fdr'])
        
        # Check that non-NaN values are corrected
        assert not pd.isna(result.loc[0, 'p_value_fdr'])
        assert not pd.isna(result.loc[2, 'p_value_fdr'])
        assert not pd.isna(result.loc[3, 'p_value_fdr'])
    
    def test_no_p_value_column(self):
        """Test with DataFrame that has no p-value columns."""
        df = pd.DataFrame({
            'data1': [1, 2, 3],
            'data2': ['a', 'b', 'c']
        })
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Should return unchanged DataFrame
        assert result.equals(df)
        assert 'p_value_fdr' not in result.columns
    
    def test_star_conversion(self):
        """Test that stars are correctly assigned."""
        df = pd.DataFrame({
            'p_value': [0.001, 0.01, 0.05, 0.1, 0.5]
        })
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Check star assignments based on corrected p-values
        # Note: FDR correction makes p-values larger, so stars may differ
        stars = result['p_value_fdr_stars']
        assert isinstance(stars.iloc[0], str)  # Should have stars for low p-values
    
    def test_preserve_index(self):
        """Test that DataFrame index is preserved."""
        df = pd.DataFrame({
            'p_value': [0.01, 0.02, 0.03]
        }, index=['A', 'B', 'C'])
        
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Index should be preserved
        assert list(result.index) == ['A', 'B', 'C']
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame({'p_value': []})
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        assert len(result) == 0
        assert 'p_value_fdr' in result.columns
        assert 'p_value_fdr_stars' in result.columns


class TestFDRCorrectionWrapper:
    """Test the wrapper function from stats module."""
    
    def test_wrapper_functionality(self):
        """Test wrapper returns only corrected p-values."""
        p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042])
        p_corrected = scitex.stats.fdr_correction(p_values, alpha=0.05)
        
        # Wrapper should return only corrected p-values
        assert isinstance(p_corrected, np.ndarray)
        assert p_corrected.shape == p_values.shape
        
        # FDR corrected values should be >= original
        assert np.all(p_corrected >= p_values)
    
    def test_wrapper_with_method_parameter(self):
        """Test wrapper with different methods."""
        p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        
        # Test with independent method
        p_corrected_indep = scitex.stats.fdr_correction(p_values, method='indep')
        
        # Test with negative correlation method
        p_corrected_negcorr = scitex.stats.fdr_correction(p_values, method='negcorr')
        
        # negcorr should be more conservative (larger p-values)
        assert np.all(p_corrected_negcorr >= p_corrected_indep)


class TestFDRProperties:
    """Test statistical properties of FDR correction."""
    
    def test_benjamini_hochberg_procedure(self):
        """Test the Benjamini-Hochberg step-up procedure."""
        # Example from literature
        p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042])
        alpha = 0.05
        
        from statsmodels.stats.multitest import fdrcorrection
        reject, p_corrected = fdrcorrection(p_values, alpha=alpha)
        
        # Manual calculation for verification
        n = len(p_values)
        sorted_p = np.sort(p_values)
        
        # Find the largest i such that P(i) <= (i/n) * alpha
        for i in range(n, 0, -1):
            if sorted_p[i-1] <= (i/n) * alpha:
                # All p-values up to position i should be rejected
                break
        
        # Check that the correct hypotheses are rejected
        assert np.sum(reject) <= i
    
    def test_fdr_control(self):
        """Test that FDR is controlled at the specified level."""
        np.random.seed(42)
        n_simulations = 1000
        n_tests = 100
        n_true_null = 90  # 90% null hypotheses
        alpha = 0.05
        
        fdr_empirical_list = []
        
        for _ in range(n_simulations):
            # Generate p-values: most from null, some from alternative
            p_null = np.random.uniform(0, 1, n_true_null)
            p_alt = np.random.beta(0.5, 10, n_tests - n_true_null)  # Tend to be small
            p_values = np.concatenate([p_null, p_alt])
            
            # Apply FDR correction
            from statsmodels.stats.multitest import fdrcorrection
            reject, _ = fdrcorrection(p_values, alpha=alpha)
            
            # Calculate false discoveries
            false_discoveries = np.sum(reject[:n_true_null])
            total_discoveries = np.sum(reject)
            
            if total_discoveries > 0:
                fdr_empirical = false_discoveries / total_discoveries
                fdr_empirical_list.append(fdr_empirical)
        
        # Average FDR should be controlled at alpha level
        if fdr_empirical_list:
            mean_fdr = np.mean(fdr_empirical_list)
            assert mean_fdr <= alpha + 0.02  # Allow small margin
    
    def test_comparison_with_bonferroni(self):
        """Test that FDR is less conservative than Bonferroni."""
        p_values = np.array([0.001, 0.01, 0.02, 0.03, 0.04])
        
        # FDR correction
        from statsmodels.stats.multitest import fdrcorrection
        _, p_fdr = fdrcorrection(p_values)
        
        # Bonferroni correction
        p_bonf = scitex.stats.bonferroni_correction(p_values)
        
        # FDR should be less conservative (smaller corrected p-values)
        assert np.all(p_fdr <= p_bonf)
    
    def test_sorted_p_values(self):
        """Test that FDR correction preserves order relationships."""
        p_values = np.array([0.05, 0.01, 0.03, 0.02, 0.04])
        
        from statsmodels.stats.multitest import fdrcorrection
        _, p_corrected = fdrcorrection(p_values)
        
        # If p1 < p2, then corrected_p1 <= corrected_p2
        for i in range(len(p_values)):
            for j in range(len(p_values)):
                if p_values[i] < p_values[j]:
                    assert p_corrected[i] <= p_corrected[j] + 1e-10  # Small tolerance


class TestIntegration:
    """Integration tests for FDR correction."""
    
    def test_real_world_example(self):
        """Test with a realistic multiple testing scenario."""
        # Simulate gene expression data with multiple comparisons
        np.random.seed(42)
        n_genes = 1000
        
        # 5% of genes are differentially expressed
        n_de_genes = 50
        
        # Generate t-statistics
        t_stats = np.random.standard_t(df=10, size=n_genes)
        # Make some genes differentially expressed
        t_stats[:n_de_genes] += np.random.uniform(2, 4, n_de_genes)
        
        # Convert to p-values (two-sided test)
        from scipy import stats
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=10))
        
        # Create DataFrame
        df = pd.DataFrame({
            'gene_id': [f'GENE_{i:04d}' for i in range(n_genes)],
            't_statistic': t_stats,
            'p_value': p_values
        })
        
        # Apply FDR correction
        result = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Check results
        assert 'p_value_fdr' in result.columns
        assert 'p_value_fdr_stars' in result.columns
        
        # Some genes should be significant after correction
        significant = result['p_value_fdr'] < 0.05
        assert np.sum(significant) > 0
        assert np.sum(significant) < n_genes  # Not all should be significant
    
    def test_pipeline_workflow(self):
        """Test FDR correction in a typical analysis pipeline."""
        # Simulate results from multiple statistical tests
        test_results = []
        
        for i in range(5):
            for j in range(4):
                # Simulate correlation test results
                if i == j:
                    p_val = np.random.uniform(0.5, 0.9)  # No correlation
                else:
                    p_val = np.random.uniform(0.001, 0.05)  # Some correlation
                
                test_results.append({
                    'var1': f'VAR_{i}',
                    'var2': f'VAR_{j}',
                    'correlation': np.random.uniform(-0.5, 0.5),
                    'p_value': p_val
                })
        
        df = pd.DataFrame(test_results)
        
        # Apply FDR correction
        corrected_df = scitex.stats.multiple._fdr_correction.fdr_correction(df)
        
        # Filter significant results
        significant_results = corrected_df[corrected_df['p_value_fdr'] < 0.05]
        
        # Should have some significant results
        assert len(significant_results) > 0
        assert len(significant_results) < len(df)
    
    def test_edge_cases(self):
        """Test edge cases for FDR correction."""
        # All p-values are 1
        df1 = pd.DataFrame({'p_value': [1.0, 1.0, 1.0]})
        result1 = scitex.stats.multiple._fdr_correction.fdr_correction(df1)
        assert np.all(result1['p_value_fdr'] == 1.0)
        
        # All p-values are very small
        df2 = pd.DataFrame({'p_value': [0.0001, 0.0002, 0.0003]})
        result2 = scitex.stats.multiple._fdr_correction.fdr_correction(df2)
        assert np.all(result2['p_value_fdr'] < 0.05)
        
        # Single p-value
        df3 = pd.DataFrame({'p_value': [0.03]})
        result3 = scitex.stats.multiple._fdr_correction.fdr_correction(df3)
        assert result3['p_value_fdr'].iloc[0] == 0.03  # No correction needed


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/multiple/_fdr_correction.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-10-06 10:47:42 (ywatanabe)"
# # _fdr_correction.py
#
# """
# Functionality:
#     - Implements False Discovery Rate (FDR) correction for multiple comparisons
#     - Provides both NumPy and PyTorch implementations
#
# Input:
#     - Array-like object of p-values
#     - Alpha level for significance
#     - Method for correction ('indep' or 'negcorr')
#
# Output:
#     - Boolean array indicating rejected hypotheses
#     - Array of corrected p-values
#
# Prerequisites:
#     - NumPy, PyTorch, pandas, statsmodels, and scitex packages
# """
#
# """Imports"""
# from typing import Union, Tuple
# import numpy as np
# import torch
# import pandas as pd
# from statsmodels.stats.multitest import fdrcorrection
# import scitex
# from ...decorators import pandas_fn
#
# ArrayLike = Union[np.ndarray, torch.Tensor, pd.Series]
#
#
# @pandas_fn
# def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
#     """
#     Apply FDR correction to p-value columns in a DataFrame.
#
#     Example:
#     --------
#     >>> df = pd.DataFrame({'p_value': [0.01, 0.05, 0.1], 'other': [1, 2, 3]})
#     >>> fdr_correction(df)
#        p_value  other  p_value_fdr p_value_fdr_stars
#     0     0.01      1    0.030000               **
#     1     0.05      2    0.075000                *
#     2     0.10      3    0.100000
#
#     Parameters:
#     -----------
#     results : pd.DataFrame
#         DataFrame containing p-value columns
#
#     Returns:
#     --------
#     pd.DataFrame
#         DataFrame with added FDR-corrected p-values and stars
#     """
#     pval_cols = scitex.stats.find_pval(results, multiple=True)
#     if not pval_cols:
#         return results
#
#     for pval_col in pval_cols:
#         non_nan = results.dropna(subset=[pval_col])
#         nan_rows = results[results[pval_col].isna()]
#
#         pvals = non_nan[pval_col]
#         if isinstance(pvals, pd.DataFrame):
#             pvals = pvals.values.flatten()
#
#         _, fdr_corrected_pvals = fdrcorrection(pvals)
#         non_nan[f"{pval_col}_fdr"] = fdr_corrected_pvals
#         nan_rows[f"{pval_col}_fdr"] = np.nan
#
#         results = pd.concat([non_nan, nan_rows]).sort_index()
#         results[f"{pval_col}_fdr_stars"] = results[f"{pval_col}_fdr"].apply(
#             scitex.stats.p2stars
#         )
#
#     return results
#
#
# # def _ecdf(xx: ArrayLike) -> ArrayLike:
# #     """Compute empirical cumulative distribution function."""
# #     nobs = len(xx)
# #     return np.arange(1, nobs + 1) / float(nobs)
#
# # def _ecdf_torch(xx: torch.Tensor) -> torch.Tensor:
# #     """Compute empirical cumulative distribution function using PyTorch."""
# #     nobs = len(xx)
# #     return torch.arange(1, nobs + 1, device=xx.device) / float(nobs)
#
# # def fdr_correction_torch(pvals: torch.Tensor, alpha: float = 0.05, method: str = "indep") -> Tuple[torch.Tensor, torch.Tensor]:
# #     """
# #     P-value correction with False Discovery Rate (FDR) using PyTorch.
#
# #     Example:
# #     >>> pvals = torch.tensor([0.01, 0.02, 0.03, 0.04, 0.05])
# #     >>> reject, pvals_corrected = fdr_correction_torch(pvals)
# #     >>> print(reject, pvals_corrected)
#
# #     Parameters:
# #     -----------
# #     pvals : torch.Tensor
# #         Set of p-values of the individual tests
# #     alpha : float, optional
# #         Error rate (default is 0.05)
# #     method : str, optional
# #         'indep' for Benjamini/Hochberg, 'negcorr' for Benjamini/Yekutieli (default is 'indep')
#
# #     Returns:
# #     --------
# #     reject : torch.Tensor
# #         Boolean tensor indicating rejected hypotheses
# #     pvals_corrected : torch.Tensor
# #         Tensor of corrected p-values
# #     """
# #     shape_init = pvals.shape
# #     pvals = pvals.ravel()
#
# #     pvals_sortind = torch.argsort(pvals)
# #     pvals_sorted = pvals[pvals_sortind]
# #     sortrevind = pvals_sortind.argsort()
#
# #     if method in ["i", "indep", "p", "poscorr"]:
# #         ecdffactor = _ecdf_torch(pvals_sorted)
# #     elif method in ["n", "negcorr"]:
# #         cm = torch.sum(1.0 / torch.arange(1, len(pvals_sorted) + 1, device=pvals.device))
# #         ecdffactor = _ecdf_torch(pvals_sorted) / cm
# #     else:
# #         raise ValueError("Method should be 'indep' or 'negcorr'")
#
# #     ecdffactor = ecdffactor.to(pvals_sorted.dtype)
#
# #     reject = pvals_sorted < (ecdffactor * alpha)
#
# #     if reject.any():
# #         rejectmax = torch.nonzero(reject, as_tuple=True)[0].max()
# #     else:
# #         rejectmax = torch.tensor(0, device=pvals.device)
# #     reject[:rejectmax+1] = True
#
# #     pvals_corrected_raw = pvals_sorted / ecdffactor
# #     pvals_corrected = torch.minimum(torch.ones_like(pvals_corrected_raw), torch.cummin(pvals_corrected_raw.flip(0), 0)[0].flip(0))
#
# #     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
# #     reject = reject[sortrevind].reshape(shape_init)
# #     return reject, pvals_corrected
#
# if __name__ == "__main__":
#     pvals = [0.02, 0.03, 0.05]
#     pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))
#
#     reject, pvals_corrected = fdr_correction(pd.DataFrame({"p_value": pvals}))
#
#     reject_torch, pvals_corrected_torch = fdr_correction_torch(
#         pvals_torch, alpha=0.05, method="indep"
#     )
#
#     arr = pvals_corrected["fdr_p_value"].to_numpy().astype(float)
#     tor = pvals_corrected_torch.numpy().astype(float)
#     print(scitex.gen.isclose(arr, tor))
#
# # #!/usr/bin/env python3
# # # Time-stamp: "2024-10-06 09:26:33 (ywatanabe)"
#
# # """
# # Functionality:
# #     - Implements False Discovery Rate (FDR) correction for multiple comparisons
# #     - Provides both NumPy and PyTorch implementations
#
# # Input:
# #     - Array-like object of p-values
# #     - Alpha level for significance
# #     - Method for correction ('indep' or 'negcorr')
#
# # Output:
# #     - Boolean array indicating rejected hypotheses
# #     - Array of corrected p-values
#
# # Prerequisites:
# #     - NumPy, PyTorch, pandas, statsmodels, and scitex packages
# # """
#
# # """Imports"""
# # from typing import Union, Tuple
# # import numpy as np
# # import torch
# # import pandas as pd
# # from statsmodels.stats.multitest import fdrcorrection
# # import scitex
#
# # ArrayLike = Union[np.ndarray, torch.Tensor, pd.Series]
#
# # def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
# #     """
# #     Apply FDR correction to p-values in a DataFrame.
#
# #     Example:
# #     >>> df = pd.DataFrame({'p_value': [0.01, 0.02, 0.03, 0.04, 0.05]})
# #     >>> corrected_df = fdr_correction(df)
# #     >>> print(corrected_df)
#
# #     Parameters:
# #     -----------
# #     results : pd.DataFrame
# #         DataFrame containing a 'p_value' column
#
# #     Returns:
# #     --------
# #     pd.DataFrame
# #         DataFrame with added 'fdr_p_value' and 'fdr_stars' columns
# #     """
# #     if "p_value" not in results.columns:
# #         return results
# #     _, fdr_corrected_pvals = fdrcorrection(results["p_value"])
# #     results["fdr_p_value"] = fdr_corrected_pvals
# #     results["fdr_stars"] = results["fdr_p_value"].apply(scitex.stats.p2stars)
# #     return results
#
# # def fdr_correction(pvals, alpha=0.05, method="indep"):
# #     # https://github.com/mne-tools/mne-python/blob/main/mne/stats/multi_comp.py
# #     """P-value correction with False Discovery Rate (FDR).
#
# #     Correction for multiple comparison using FDR :footcite:`GenoveseEtAl2002`.
#
# #     This covers Benjamini/Hochberg for independent or positively correlated and
# #     Benjamini/Yekutieli for gen or negatively correlated tests.
#
# #     Parameters
# #     ----------
# #     pvals : array_like
# #         Set of p-values of the individual tests.
# #     alpha : float
# #         Error rate.
# #     method : 'indep' | 'negcorr'
# #         If 'indep' it implements Benjamini/Hochberg for independent or if
# #         'negcorr' it corresponds to Benjamini/Yekutieli.
#
# #     Returns
# #     -------
# #     reject : array, bool
# #         True if a hypothesis is rejected, False if not.
# #     pval_corrected : array
# #     alpha : float
# #         Error rate.
# #     method : 'indep' | 'negcorr'
# #         If 'indep' it implements Benjamini/Hochberg for independent or if
# #         'negcorr' it corresponds to Benjamini/Yekutieli.
#
# #     Returns
# #     -------
# #     reject : array, bool
# #         True if a hypothesis is rejected, False if not.
# #     pval_corrected : array
# #     alpha : float
# #         Error rate.
# #     method : 'indep' | 'negcorr'
# #         If 'indep' it implements Benjamini/Hochberg for independent or if
# #         'negcorr' it corresponds to Benjamini/Yekutieli.
#
# #     Returns
# #     -------
# #     reject : array, bool
# #         True if a hypothesis is rejected, False if not.
# #     pval_corrected : array
# #         P-values adjusted for multiple hypothesis testing to limit FDR.
#
# #     Returns
# #     -------
# #     reject : array, bool
# #         True if a hypothesis is rejected, False if not.
# #     pval_corrected : array
# #         P-values adjusted for multiple hypothesis testing to limit FDR.
#
# #     References
# #     ----------
# #     .. footbibliography::
# #     """
# #     pvals = np.asarray(pvals)
# #     shape_init = pvals.shape
# #     pvals = pvals.ravel()
#
# #     pvals_sortind = np.argsort(pvals)
# #     pvals_sorted = pvals[pvals_sortind]
# #     sortrevind = pvals_sortind.argsort()
#
# #     if method in ["i", "indep", "p", "poscorr"]:
# #         ecdffactor = _ecdf(pvals_sorted)
# #     elif method in ["n", "negcorr"]:
# #         cm = np.sum(1.0 / np.arange(1, len(pvals_sorted) + 1))
# #         ecdffactor = _ecdf(pvals_sorted) / cm
# #     else:
# #         raise ValueError("Method should be 'indep' and 'negcorr'")
#
# #     reject = pvals_sorted < (ecdffactor * alpha)
# #     if reject.any():
# #         rejectmax = max(np.nonzero(reject)[0])
# #     else:
# #         rejectmax = 0
# #     reject[:rejectmax] = True
#
# #     pvals_corrected_raw = pvals_sorted / ecdffactor
# #     pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]
# #     pvals_corrected[pvals_corrected > 1.0] = 1.0
# #     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
# #     reject = reject[sortrevind].reshape(shape_init)
# #     return reject, pvals_corrected
#
#
# # def fdr_correction(results: pd.DataFrame) -> pd.DataFrame:
# #     if "p_value" not in results.columns:
# #         return results
# #     _, fdr_corrected_pvals = fdrcorrection(results["p_value"])
# #     results["fdr_p_value"] = fdr_corrected_pvals
# #     results["fdr_stars"] = results["fdr_p_value"].apply(scitex.stats.p2stars)
# #     return results
#
# # def _ecdf(xx: ArrayLike) -> ArrayLike:
# #     """Compute empirical cumulative distribution function."""
# #     nobs = len(xx)
# #     return np.arange(1, nobs + 1) / float(nobs)
#
# # def _ecdf_torch(xx: torch.Tensor) -> torch.Tensor:
# #     """Compute empirical cumulative distribution function using PyTorch."""
# #     nobs = len(xx)
# #     return torch.arange(1, nobs + 1, device=xx.device) / float(nobs)
#
# # def fdr_correction_torch(pvals: torch.Tensor, alpha: float = 0.05, method: str = "indep") -> Tuple[torch.Tensor, torch.Tensor]:
# #     """
# #     P-value correction with False Discovery Rate (FDR) using PyTorch.
#
# #     Example:
# #     >>> pvals = torch.tensor([0.01, 0.02, 0.03, 0.04, 0.05])
# #     >>> reject, pvals_corrected = fdr_correction_torch(pvals)
# #     >>> print(reject, pvals_corrected)
#
# #     Parameters:
# #     -----------
# #     pvals : torch.Tensor
# #         Set of p-values of the individual tests
# #     alpha : float, optional
# #         Error rate (default is 0.05)
# #     method : str, optional
# #         'indep' for Benjamini/Hochberg, 'negcorr' for Benjamini/Yekutieli (default is 'indep')
#
# #     Returns:
# #     --------
# #     reject : torch.Tensor
# #         Boolean tensor indicating rejected hypotheses
# #     pvals_corrected : torch.Tensor
# #         Tensor of corrected p-values
# #     """
# #     shape_init = pvals.shape
# #     pvals = pvals.ravel()
#
# #     pvals_sortind = torch.argsort(pvals)
# #     pvals_sorted = pvals[pvals_sortind]
# #     sortrevind = pvals_sortind.argsort()
#
# #     if method in ["i", "indep", "p", "poscorr"]:
# #         ecdffactor = _ecdf_torch(pvals_sorted)
# #     elif method in ["n", "negcorr"]:
# #         cm = torch.sum(1.0 / torch.arange(1, len(pvals_sorted) + 1, device=pvals.device))
# #         ecdffactor = _ecdf_torch(pvals_sorted) / cm
# #     else:
# #         raise ValueError("Method should be 'indep' or 'negcorr'")
#
# #     ecdffactor = ecdffactor.to(pvals_sorted.dtype)
#
# #     reject = pvals_sorted < (ecdffactor * alpha)
#
# #     if reject.any():
# #         rejectmax = torch.nonzero(reject, as_tuple=True)[0].max()
# #     else:
# #         rejectmax = torch.tensor(0, device=pvals.device)
# #     reject[:rejectmax+1] = True
#
# #     pvals_corrected_raw = pvals_sorted / ecdffactor
# #     pvals_corrected = torch.minimum(torch.ones_like(pvals_corrected_raw), torch.cummin(pvals_corrected_raw.flip(0), 0)[0].flip(0))
#
# #     pvals_corrected = pvals_corrected[sortrevind].reshape(shape_init)
# #     reject = reject[sortrevind].reshape(shape_init)
# #     return reject, pvals_corrected
#
#
# # if __name__ == "__main__":
# #     pvals = [0.02, 0.03, 0.05]
# #     pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))
#
# #     reject, pvals_corrected = fdr_correction(pvals, alpha=0.05, method="indep")
#
# #     reject_torch, pvals_corrected_torch = fdr_correction_torch(
# #         pvals, alpha=0.05, method="indep"
# #     )
#
# #     arr = pvals_corrected.astype(float)
# #     tor = pvals_corrected_torch.numpy().astype(float)
# #     print(scitex.gen.isclose(arr, tor))
#
# # EOF
