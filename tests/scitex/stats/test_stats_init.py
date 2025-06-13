import pytest
import numpy as np
import pandas as pd
import scitex


class TestStatsModuleImports:
    """Test stats module imports and structure."""

    def test_module_import(self):
        """Test that stats module can be imported."""
        assert hasattr(scitex, "stats")

    def test_submodules(self):
        """Test that submodules are available."""
        assert hasattr(scitex.stats, "desc")
        assert hasattr(scitex.stats, "multiple")
        assert hasattr(scitex.stats, "tests")

    def test_main_functions(self):
        """Test main statistical functions are imported."""
        # Descriptive statistics
        assert hasattr(scitex.stats, "describe")
        assert hasattr(scitex.stats, "nan")
        assert hasattr(scitex.stats, "real")
        
        # Correlation tests
        assert hasattr(scitex.stats, "corr_test")
        assert hasattr(scitex.stats, "corr_test_spearman")
        assert hasattr(scitex.stats, "corr_test_pearson")
        assert hasattr(scitex.stats, "corr_test_multi")
        assert hasattr(scitex.stats, "nocorrelation_test")
        
        # Statistical tests
        assert hasattr(scitex.stats, "brunner_munzel_test")
        assert hasattr(scitex.stats, "smirnov_grubbs")
        
        # P-value formatting
        assert hasattr(scitex.stats, "p2stars")
        
        # Multiple testing corrections
        assert hasattr(scitex.stats, "bonferroni_correction")
        assert hasattr(scitex.stats, "fdr_correction")
        assert hasattr(scitex.stats, "multicompair")

    def test_calc_partial_corr(self):
        """Test partial correlation function is available."""
        assert hasattr(scitex.stats, "calc_partial_corr")

    def test_private_functions_not_exposed(self):
        """Test that private functions are not exposed."""
        # Check that underscore-prefixed functions are not in main namespace
        # (except the ones explicitly imported in __init__.py)
        for attr in dir(scitex.stats):
            if attr.startswith("_") and not attr.startswith("__"):
                # These are explicitly imported in __init__.py
                allowed_private = ["_compute_surrogate"]
                if attr not in allowed_private:
                    # Should not have other private functions
                    assert not callable(getattr(scitex.stats, attr, None))


class TestBasicFunctionality:
    """Test basic functionality of main stats functions."""

    def test_describe_basic(self):
        """Test basic describe functionality."""
        data = np.random.randn(100)
        result = scitex.stats.describe(data)
        
        # Should return a dictionary or similar structure
        assert result is not None
        
        # For pandas Series/DataFrame input
        df = pd.DataFrame({"A": data, "B": data * 2})
        result_df = scitex.stats.describe(df)
        assert result_df is not None

    def test_corr_test_basic(self):
        """Test basic correlation test functionality."""
        x = np.random.randn(50)
        y = 2 * x + np.random.randn(50) * 0.5  # Correlated data
        
        result = scitex.stats.corr_test(x, y)
        assert result is not None
        
        # Test specific correlation types
        result_spear = scitex.stats.corr_test_spearman(x, y)
        assert result_spear is not None
        
        result_pear = scitex.stats.corr_test_pearson(x, y)
        assert result_pear is not None

    def test_p2stars_basic(self):
        """Test p-value to stars conversion."""
        # Test various p-values
        assert scitex.stats.p2stars(0.001) == "***"
        assert scitex.stats.p2stars(0.01) == "**"
        assert scitex.stats.p2stars(0.05) == "*"
        assert scitex.stats.p2stars(0.1) == "n.s."
        
        # Test with array input
        p_values = np.array([0.001, 0.01, 0.05, 0.1, 0.5])
        stars = scitex.stats.p2stars(p_values)
        assert len(stars) == len(p_values)

    def test_multiple_corrections_basic(self):
        """Test multiple testing corrections."""
        p_values = np.array([0.01, 0.04, 0.03, 0.05, 0.20])
        
        # Bonferroni correction
        corrected_bonf = scitex.stats.bonferroni_correction(p_values)
        assert corrected_bonf is not None
        assert len(corrected_bonf) == len(p_values)
        
        # FDR correction
        corrected_fdr = scitex.stats.fdr_correction(p_values)
        assert corrected_fdr is not None

    def test_statistical_tests_basic(self):
        """Test statistical tests with basic data."""
        # Brunner-Munzel test
        x = np.random.randn(30)
        y = np.random.randn(30) + 0.5
        
        result = scitex.stats.brunner_munzel_test(x, y)
        assert result is not None
        
        # Smirnov-Grubbs test for outliers
        data_with_outlier = np.concatenate([np.random.randn(50), [10.0]])
        result = scitex.stats.smirnov_grubbs(data_with_outlier)
        assert result is not None


class TestIntegration:
    """Test integration between stats functions."""

    def test_describe_with_nan_handling(self):
        """Test describe with NaN values."""
        data = np.array([1, 2, 3, np.nan, 5, 6, np.nan])
        
        # Test nan handling
        nan_result = scitex.stats.nan(data)
        assert nan_result is not None
        
        # Test real values only
        real_result = scitex.stats.real(data)
        assert real_result is not None
        assert len(real_result) == 5  # Should have 5 non-nan values

    def test_correlation_workflow(self):
        """Test typical correlation analysis workflow."""
        # Generate correlated data
        n_samples = 100
        x = np.random.randn(n_samples)
        y = 0.7 * x + np.random.randn(n_samples) * 0.5
        z = 0.3 * x + 0.4 * y + np.random.randn(n_samples) * 0.3
        
        # Single correlation test
        corr_xy = scitex.stats.corr_test(x, y)
        assert corr_xy is not None
        
        # Multiple correlation tests
        data = pd.DataFrame({"x": x, "y": y, "z": z})
        corr_multi = scitex.stats.corr_test_multi(data)
        assert corr_multi is not None
        
        # Partial correlation
        partial_corr = scitex.stats.calc_partial_corr(data)
        assert partial_corr is not None

    def test_p_value_workflow(self):
        """Test p-value processing workflow."""
        # Generate multiple p-values
        p_values = np.array([0.001, 0.01, 0.03, 0.04, 0.05, 0.1, 0.5])
        
        # Convert to stars
        stars = scitex.stats.p2stars(p_values)
        assert len(stars) == len(p_values)
        
        # Apply corrections
        p_bonf = scitex.stats.bonferroni_correction(p_values)
        p_fdr = scitex.stats.fdr_correction(p_values)
        
        # Convert corrected p-values to stars
        stars_bonf = scitex.stats.p2stars(p_bonf)
        stars_fdr = scitex.stats.p2stars(p_fdr)
        
        assert len(stars_bonf) == len(p_values)
        assert len(stars_fdr) == len(p_values)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/__init__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-17 12:29:22 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/stats/__init__.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/stats/__init__.py"
#
# import os
# import importlib
# import inspect
#
# # Get the current directory
# current_dir = os.path.dirname(__file__)
#
# # Iterate through all Python files in the current directory
# for filename in os.listdir(current_dir):
#     if filename.endswith(".py") and not filename.startswith("__"):
#         module_name = filename[:-3]  # Remove .py extension
#         module = importlib.import_module(f".{module_name}", package=__name__)
#
#         # Import only functions and classes from the module
#         for name, obj in inspect.getmembers(module):
#             if inspect.isfunction(obj) or inspect.isclass(obj):
#                 if not name.startswith("_"):
#                     globals()[name] = obj
#
# # Clean up temporary variables
# del os, importlib, inspect, current_dir, filename, module_name, module, name, obj
#
# from . import desc
# from . import multiple
# from . import tests
# from ._describe_wrapper import describe
# from ._nan_stats import nan, real
# from ._corr_test_wrapper import corr_test, corr_test_spearman, corr_test_pearson
# from .tests._corr_test import _compute_surrogate
# from ._corr_test_multi import corr_test_multi, nocorrelation_test
# from ._statistical_tests import brunner_munzel_test, smirnov_grubbs
# from ._p2stars_wrapper import p2stars
# from ._multiple_corrections import bonferroni_correction, fdr_correction, multicompair
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/stats/__init__.py
# --------------------------------------------------------------------------------
