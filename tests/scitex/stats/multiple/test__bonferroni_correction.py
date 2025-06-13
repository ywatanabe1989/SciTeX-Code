#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./tests/scitex/stats/multiple/test__bonferroni_correction.py

import pytest
import numpy as np
import torch
import scitex


class TestImports:
    def test_import_main(self):
        import scitex

    def test_import_submodule(self):
        import scitex.stats

    def test_import_target(self):
        import scitex.stats.multiple._bonferroni_correction
    
    def test_import_from_stats(self):
        # Test that bonferroni_correction is available from stats module
        assert hasattr(scitex.stats, 'bonferroni_correction')


class TestBonferroniCorrection:
    """Test bonferroni_correction function."""
    
    def test_basic_functionality(self):
        """Test basic Bonferroni correction."""
        p_values = np.array([0.01, 0.04, 0.03])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values, alpha=0.05)
        
        # Check output types
        assert isinstance(reject, np.ndarray)
        assert isinstance(p_corrected, np.ndarray)
        assert reject.dtype == bool
        
        # Check shapes match
        assert reject.shape == p_values.shape
        assert p_corrected.shape == p_values.shape
        
        # Check correction factor
        n_tests = len(p_values)
        expected_corrected = p_values * n_tests
        assert np.allclose(p_corrected, expected_corrected)
    
    def test_rejection_logic(self):
        """Test rejection logic with different alpha levels."""
        p_values = np.array([0.01, 0.02, 0.04])
        
        # With alpha=0.05
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values, alpha=0.05)
        # After correction: [0.03, 0.06, 0.12]
        # Only first should be rejected
        assert reject[0] == True
        assert reject[1] == False
        assert reject[2] == False
        
        # With alpha=0.15
        reject2, _ = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values, alpha=0.15)
        # First two should be rejected
        assert reject2[0] == True
        assert reject2[1] == True
        assert reject2[2] == False
    
    def test_clipping_to_one(self):
        """Test that corrected p-values are clipped to maximum of 1.0."""
        p_values = np.array([0.5, 0.8, 0.9])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values)
        
        # All should be clipped to 1.0
        assert np.all(p_corrected <= 1.0)
        assert p_corrected[1] == 1.0  # 0.8 * 3 = 2.4 -> 1.0
        assert p_corrected[2] == 1.0  # 0.9 * 3 = 2.7 -> 1.0
    
    def test_single_p_value(self):
        """Test with single p-value."""
        p_value = np.array([0.04])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_value, alpha=0.05)
        
        # Single test, no correction needed
        assert p_corrected[0] == 0.04
        assert reject[0] == True
    
    def test_different_input_types(self):
        """Test with different input types."""
        # List input
        p_list = [0.01, 0.02, 0.03]
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_list)
        assert isinstance(p_corrected, np.ndarray)
        
        # Scalar input
        p_scalar = 0.01
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_scalar)
        assert p_corrected.shape == ()
    
    def test_empty_input(self):
        """Test with empty input."""
        p_values = np.array([])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values)
        
        assert len(reject) == 0
        assert len(p_corrected) == 0


class TestBonferroniCorrectionTorch:
    """Test bonferroni_correction_torch function."""
    
    def test_basic_functionality(self):
        """Test basic PyTorch version functionality."""
        p_values = torch.tensor([0.01, 0.04, 0.03])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction_torch(p_values, alpha=0.05)
        
        # Check output types
        assert isinstance(reject, torch.Tensor)
        assert isinstance(p_corrected, torch.Tensor)
        assert reject.dtype == torch.bool
        
        # Check correction
        n_tests = len(p_values)
        expected_corrected = p_values * n_tests
        assert torch.allclose(p_corrected, expected_corrected)
    
    def test_consistency_with_numpy(self):
        """Test that PyTorch and NumPy versions give same results."""
        p_values_np = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        p_values_torch = torch.tensor(p_values_np)
        
        reject_np, p_corrected_np = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values_np)
        reject_torch, p_corrected_torch = scitex.stats.multiple._bonferroni_correction.bonferroni_correction_torch(p_values_torch)
        
        # Convert torch results to numpy for comparison
        assert np.allclose(p_corrected_np, p_corrected_torch.numpy())
        assert np.array_equal(reject_np, reject_torch.numpy())
    
    def test_different_dtypes(self):
        """Test with different tensor dtypes."""
        p_values_float32 = torch.tensor([0.01, 0.02, 0.03], dtype=torch.float32)
        p_values_float64 = torch.tensor([0.01, 0.02, 0.03], dtype=torch.float64)
        
        reject32, p_corrected32 = scitex.stats.multiple._bonferroni_correction.bonferroni_correction_torch(p_values_float32)
        reject64, p_corrected64 = scitex.stats.multiple._bonferroni_correction.bonferroni_correction_torch(p_values_float64)
        
        assert torch.allclose(p_corrected32, p_corrected64.float())


class TestBonferroniWrapper:
    """Test the wrapper function from stats module."""
    
    def test_wrapper_functionality(self):
        """Test wrapper returns only corrected p-values."""
        p_values = np.array([0.01, 0.02, 0.03])
        p_corrected = scitex.stats.bonferroni_correction(p_values, alpha=0.05)
        
        # Wrapper should return only corrected p-values (not reject array)
        assert isinstance(p_corrected, np.ndarray)
        assert p_corrected.shape == p_values.shape
        
        # Check values are correct
        expected = p_values * len(p_values)
        assert np.allclose(p_corrected, expected)
    
    def test_wrapper_with_different_alpha(self):
        """Test wrapper with different alpha values."""
        p_values = np.array([0.01, 0.02, 0.03])
        
        # Alpha doesn't affect the corrected p-values, only rejection
        p_corrected1 = scitex.stats.bonferroni_correction(p_values, alpha=0.01)
        p_corrected2 = scitex.stats.bonferroni_correction(p_values, alpha=0.10)
        
        assert np.allclose(p_corrected1, p_corrected2)


class TestIntegration:
    """Integration tests for Bonferroni correction."""
    
    def test_multiple_hypothesis_scenario(self):
        """Test realistic multiple hypothesis testing scenario."""
        # Simulate p-values from multiple t-tests
        np.random.seed(42)
        n_tests = 20
        
        # Mix of significant and non-significant p-values
        p_values = np.concatenate([
            np.random.uniform(0.001, 0.01, 3),  # True positives
            np.random.uniform(0.1, 0.9, 17)     # True negatives
        ])
        np.random.shuffle(p_values)
        
        # Apply Bonferroni correction
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values, alpha=0.05)
        
        # Check that correction is conservative
        assert np.sum(reject) <= np.sum(p_values < 0.05)
        
        # All corrected p-values should be >= original
        assert np.all(p_corrected >= p_values)
    
    def test_fwer_control(self):
        """Test family-wise error rate control."""
        # Under null hypothesis, all p-values uniformly distributed
        np.random.seed(42)
        n_simulations = 1000
        n_tests = 10
        alpha = 0.05
        
        fwer_count = 0
        for _ in range(n_simulations):
            # Generate p-values under null
            p_values = np.random.uniform(0, 1, n_tests)
            
            # Apply Bonferroni
            reject, _ = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_values, alpha=alpha)
            
            # Count if any false rejection
            if np.any(reject):
                fwer_count += 1
        
        # FWER should be controlled at alpha level
        empirical_fwer = fwer_count / n_simulations
        assert empirical_fwer <= alpha + 0.02  # Allow small margin for randomness
    
    def test_edge_cases(self):
        """Test edge cases."""
        # All p-values significant
        p_all_sig = np.array([0.001, 0.002, 0.003])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_all_sig, alpha=0.05)
        assert np.all(reject)
        
        # No p-values significant
        p_none_sig = np.array([0.5, 0.6, 0.7])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_none_sig, alpha=0.05)
        assert not np.any(reject)
        
        # Exactly at threshold
        p_threshold = np.array([0.05/3, 0.05/3, 0.05/3])
        reject, p_corrected = scitex.stats.multiple._bonferroni_correction.bonferroni_correction(p_threshold, alpha=0.05)
        # Should not reject (need to be strictly less than alpha)
        assert not np.any(reject)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/multiple/_bonferroni_correction.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # Time-stamp: "2021-09-25 15:39:51 (ylab)"
#
# import numpy as np
# import torch
# import scitex
#
#
# def bonferroni_correction(pval, alpha=0.05):
#     # https://github.com/mne-tools/mne-python/blob/main/mne/stats/multi_comp.py
#     """P-value correction with Bonferroni method.
#
#     Parameters
#     ----------
#     pval : array_like
#         Set of p-values of the individual tests.
#     alpha : float
#         Error rate.
#
#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pval_corrected : array
#         P-values adjusted for multiple hypothesis testing to limit FDR.
#     """
#     pval = np.asarray(pval)
#     pval_corrected = pval * float(pval.size)
#     # p-values must not be larger than 1.
#     pval_corrected = pval_corrected.clip(max=1.0)
#     reject = pval_corrected < alpha
#     return reject, pval_corrected
#
#
# def bonferroni_correction_torch(pvals, alpha=0.05):
#     """P-value correction with Bonferroni method.
#
#     Parameters
#     ----------
#     pvals : array_like
#         Set of p-values of the individual tests.
#     alpha : float
#         Error rate.
#
#     Returns
#     -------
#     reject : array, bool
#         True if a hypothesis is rejected, False if not.
#     pvals_corrected : array
#         P-values adjusted for multiple hypothesis testing to limit FDR.
#     """
#     pvals = torch.tensor(pvals)
#     pvals_corrected = pvals * torch.tensor(pvals.size()).float()
#     # p-values must not be larger than 1.
#     pvals_corrected = pvals_corrected.clip(max=1.0)
#     reject = pvals_corrected < alpha
#     return reject, pvals_corrected
#
#
# if __name__ == "__main__":
#     pvals_npy = np.array([0.02, 0.03, 0.05])
#     pvals_torch = torch.tensor(np.array([0.02, 0.03, 0.05]))
#
#     reject, pvals_corrected = bonferroni_correction(pvals_npy, alpha=0.05)
#
#     reject_torch, pvals_corrected_torch = bonferroni_correction_torch(
#         pvals_torch, alpha=0.05
#     )
#
#     arr = pvals_corrected.astype(float)
#     tor = pvals_corrected_torch.numpy().astype(float)
#     print(scitex.gen.isclose(arr, tor))
#
# # EOF
