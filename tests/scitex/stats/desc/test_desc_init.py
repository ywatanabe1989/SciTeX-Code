import pytest
import numpy as np
import pandas as pd
import scitex


class TestDescModuleImports:
    """Test desc submodule imports and structure."""

    def test_module_import(self):
        """Test that desc module can be imported."""
        assert hasattr(scitex.stats, "desc")

    def test_functions_available(self):
        """Test that main functions are available."""
        # These should be imported from individual modules
        assert hasattr(scitex.stats.desc, "describe")
        assert hasattr(scitex.stats.desc, "nan")
        assert hasattr(scitex.stats.desc, "real")

    def test_module_namespace(self):
        """Test that the module namespace is properly set up."""
        # Check that the module has expected attributes
        desc_attrs = dir(scitex.stats.desc)
        
        # Should have some functions (not just dunder methods)
        public_attrs = [attr for attr in desc_attrs if not attr.startswith("_")]
        assert len(public_attrs) > 0


class TestDescBasicFunctionality:
    """Test basic functionality of desc module functions."""

    def test_describe_via_desc(self):
        """Test describe function accessed through desc module."""
        data = np.random.randn(100)
        result = scitex.stats.desc.describe(data)
        assert result is not None

    def test_nan_via_desc(self):
        """Test nan function accessed through desc module."""
        data = np.array([1, 2, np.nan, 4, np.nan])
        result = scitex.stats.desc.nan(data)
        assert result is not None

    def test_real_via_desc(self):
        """Test real function accessed through desc module."""
        data = np.array([1, 2, np.nan, 4, np.nan])
        result = scitex.stats.desc.real(data)
        assert result is not None
        assert len(result) == 3  # Only non-nan values


class TestDescIntegration:
    """Test integration of desc module functions."""

    def test_describe_with_different_inputs(self):
        """Test describe with various input types."""
        # NumPy array
        arr = np.random.randn(50)
        result_arr = scitex.stats.desc.describe(arr)
        assert result_arr is not None
        
        # Pandas Series
        series = pd.Series(arr)
        result_series = scitex.stats.desc.describe(series)
        assert result_series is not None
        
        # Pandas DataFrame
        df = pd.DataFrame({"A": arr, "B": arr * 2})
        result_df = scitex.stats.desc.describe(df)
        assert result_df is not None

    def test_nan_and_real_consistency(self):
        """Test that nan and real functions work together correctly."""
        data = np.array([1, 2, 3, np.nan, 5, np.nan, 7])
        
        # Get nan info
        nan_info = scitex.stats.desc.nan(data)
        
        # Get real values
        real_values = scitex.stats.desc.real(data)
        
        # Should have complementary information
        assert len(real_values) == 5  # 5 non-nan values
        
        # Total length should match
        total_length = len(data)
        assert total_length == 7


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/stats/desc/__init__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 03:22:30 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/stats/desc/__init__.py
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
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/stats/desc/__init__.py
# --------------------------------------------------------------------------------
