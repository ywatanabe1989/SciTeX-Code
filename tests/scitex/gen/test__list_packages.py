#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 21:30:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__list_packages.py

"""Tests for list_packages function."""

import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scitex.gen import list_packages, main


class MockDistribution:
    """Mock for importlib.metadata Distribution."""

    def __init__(self, name):
        self.name = name


class TestListPackages:
    """Test cases for list_packages function."""

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_basic_functionality(self, mock_inspect, mock_distributions):
        """Test basic package listing functionality."""
        # Setup mocks
        mock_distributions.return_value = [
            MockDistribution("numpy"),
            MockDistribution("pandas"),
            MockDistribution("scipy"),
        ]

        mock_inspect.return_value = pd.DataFrame(
            {"Name": ["numpy.array", "numpy.ndarray"]}
        )

        # Call function
        result = list_packages()

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert "Name" in result.columns
        assert len(result) > 0
        assert mock_inspect.call_count == 3  # Called for each package

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_skip_patterns_filtering(self, mock_inspect, mock_distributions):
        """Test that problematic packages are skipped."""
        # Setup mocks with problematic packages
        mock_distributions.return_value = [
            MockDistribution("numpy"),
            MockDistribution("nvidia-cuda-runtime"),
            MockDistribution("pillow"),
            MockDistribution("pandas"),
        ]

        mock_inspect.return_value = pd.DataFrame({"Name": ["test.module"]})

        # Call function
        result = list_packages()

        # Verify only numpy and pandas were processed
        assert mock_inspect.call_count == 2
        called_packages = [call[0][0] for call in mock_inspect.call_args_list]
        assert "numpy" in called_packages
        assert "pandas" in called_packages
        assert "nvidia_cuda_runtime" not in called_packages
        assert "pillow" not in called_packages

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_safelist_prioritization(self, mock_inspect, mock_distributions):
        """Test that safelist packages are prioritized."""
        # Setup mocks
        mock_distributions.return_value = [
            MockDistribution("unknown-package"),
            MockDistribution("numpy"),
            MockDistribution("another-unknown"),
            MockDistribution("pandas"),
        ]

        mock_inspect.return_value = pd.DataFrame({"Name": ["test.module"]})

        # Call function
        list_packages()

        # Verify order - safelist packages should be processed first
        called_packages = [call[0][0] for call in mock_inspect.call_args_list]
        numpy_idx = called_packages.index("numpy")
        pandas_idx = called_packages.index("pandas")
        unknown_idx = called_packages.index("unknown_package")

        assert numpy_idx < unknown_idx
        assert pandas_idx < unknown_idx

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_error_handling_skip_errors_true(self, mock_inspect, mock_distributions):
        """Test error handling with skip_errors=True."""
        # Setup mocks
        mock_distributions.return_value = [
            MockDistribution("numpy"),
            MockDistribution("pandas"),
        ]

        # First call raises error, second succeeds
        mock_inspect.side_effect = [
            Exception("Import error"),
            pd.DataFrame({"Name": ["pandas.DataFrame"]}),
        ]

        # Call function with skip_errors=True
        result = list_packages(skip_errors=True)

        # Should continue and return pandas results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["Name"] == "pandas.DataFrame"

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_error_handling_skip_errors_false(self, mock_inspect, mock_distributions):
        """Test error handling with skip_errors=False."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]

        mock_inspect.side_effect = Exception("Import error")

        # Call function with skip_errors=False
        with pytest.raises(Exception, match="Import error"):
            list_packages(skip_errors=False)

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_empty_results(self, mock_inspect, mock_distributions):
        """Test handling of empty results."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]
        mock_inspect.return_value = pd.DataFrame()  # Empty dataframe

        # Call function
        result = list_packages()

        # Should return empty dataframe with correct columns
        assert isinstance(result, pd.DataFrame)
        assert "Name" in result.columns
        assert len(result) == 0

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_no_packages_found(self, mock_inspect, mock_distributions):
        """Test when no packages are found."""
        # Setup mocks
        mock_distributions.return_value = []

        # Call function
        result = list_packages()

        # Should return empty dataframe
        assert isinstance(result, pd.DataFrame)
        assert "Name" in result.columns
        assert len(result) == 0
        assert mock_inspect.call_count == 0

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_duplicate_removal(self, mock_inspect, mock_distributions):
        """Test that duplicates are removed from results."""
        # Setup mocks
        mock_distributions.return_value = [
            MockDistribution("numpy"),
            MockDistribution("pandas"),
        ]

        # Return dataframes with duplicates
        mock_inspect.side_effect = [
            pd.DataFrame({"Name": ["shared.module", "numpy.array"]}),
            pd.DataFrame({"Name": ["shared.module", "pandas.DataFrame"]}),
        ]

        # Call function
        result = list_packages()

        # Verify duplicates removed
        assert len(result) == 3  # Not 4
        assert result["Name"].tolist() == sorted(
            ["numpy.array", "pandas.DataFrame", "shared.module"]
        )

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_sorting(self, mock_inspect, mock_distributions):
        """Test that results are sorted by Name."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]

        mock_inspect.return_value = pd.DataFrame(
            {"Name": ["zzz.module", "aaa.module", "mmm.module"]}
        )

        # Call function
        result = list_packages()

        # Verify sorted
        assert result["Name"].tolist() == ["aaa.module", "mmm.module", "zzz.module"]

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_max_depth_parameter(self, mock_inspect, mock_distributions):
        """Test max_depth parameter is passed correctly."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]
        mock_inspect.return_value = pd.DataFrame({"Name": ["numpy.array"]})

        # Call function with max_depth
        list_packages(max_depth=3)

        # Verify max_depth was passed
        mock_inspect.assert_called_with(
            "numpy",
            docstring=False,
            print_output=False,
            columns=["Name"],
            root_only=True,
            max_depth=3,
            skip_depwarnings=True,
        )

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_root_only_parameter(self, mock_inspect, mock_distributions):
        """Test root_only parameter is passed correctly."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]
        mock_inspect.return_value = pd.DataFrame({"Name": ["numpy.array"]})

        # Call function with root_only=False
        list_packages(root_only=False)

        # Verify root_only was passed
        mock_inspect.assert_called_with(
            "numpy",
            docstring=False,
            print_output=False,
            columns=["Name"],
            root_only=False,
            max_depth=1,
            skip_depwarnings=True,
        )

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    @patch("builtins.print")
    def test_verbose_output(self, mock_print, mock_inspect, mock_distributions):
        """Test verbose output for errors."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("numpy")]
        mock_inspect.side_effect = Exception("Test error")

        # Call function with verbose=True
        result = list_packages(verbose=True, skip_errors=True)

        # Verify error was printed
        mock_print.assert_called_with("Error processing numpy: Test error")

    def test_recursion_limit_set(self):
        """Test that recursion limit is increased."""
        original_limit = sys.getrecursionlimit()

        with patch("scitex.gen._list_packages.distributions") as mock_dist:
            mock_dist.return_value = []
            list_packages()

        # Verify recursion limit was set
        assert sys.getrecursionlimit() == 10_000

        # Restore original
        sys.setrecursionlimit(original_limit)

    @patch("scitex.gen._list_packages.distributions")
    @patch("scitex.gen._list_packages.inspect_module")
    def test_hyphen_to_underscore_conversion(self, mock_inspect, mock_distributions):
        """Test that package names with hyphens are converted to underscores."""
        # Setup mocks
        mock_distributions.return_value = [MockDistribution("scikit-learn")]

        mock_inspect.return_value = pd.DataFrame({"Name": ["sklearn.test"]})

        # Call function
        list_packages()

        # Verify hyphen converted to underscore
        mock_inspect.assert_called_with(
            "scikit_learn",  # Converted from scikit-learn
            docstring=False,
            print_output=False,
            columns=["Name"],
            root_only=True,
            max_depth=1,
            skip_depwarnings=True,
        )

    def test_main_function(self):
        """Test the main function."""
        # Create DataFrame outside patch context
        test_df = pd.DataFrame({"Name": ["test.module"]})

        with patch("scitex.gen._list_packages.list_packages") as mock_list_packages:
            with patch("builtins.__import__") as mock_import:
                # Setup mocks
                mock_ipdb = MagicMock()
                mock_import.return_value = mock_ipdb
                mock_list_packages.return_value = test_df

                # Call main
                result = main()

                # Verify
                assert result == 0
                mock_list_packages.assert_called_once_with(verbose=True)
                mock_ipdb.set_trace.assert_called_once()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_list_packages.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-03 02:11:54 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_list_packages.py
# """
# Functionality:
#     * Lists and analyzes installed Python packages and their modules
# Input:
#     * None (uses importlib.metadata to get installed packages)
# Output:
#     * DataFrame containing package module information
# Prerequisites:
#     * importlib.metadata (Python 3.8+) or importlib_metadata, pandas
# """
# 
# import sys
# from typing import Optional
# 
# import pandas as pd
# 
# try:
#     # Python 3.8+ standard library
#     from importlib.metadata import distributions
# except ImportError:
#     # Fallback for older Python versions
#     from importlib_metadata import distributions
# 
# from ._inspect_module import inspect_module
# 
# 
# def list_packages(
#     max_depth: int = 1,
#     root_only: bool = True,
#     skip_errors: bool = True,
#     verbose: bool = False,
# ) -> pd.DataFrame:
#     """Lists all installed packages and their modules."""
#     sys.setrecursionlimit(10_000)
# 
#     # Skip known problematic packages
#     skip_patterns = [
#         "nvidia",
#         "cuda",
#         "pillow",
#         "fonttools",
#         "ipython",
#         "jsonschema",
#         "readme",
#         "importlib-metadata",
#     ]
# 
#     # Get installed packages, excluding problematic ones
#     installed_packages = [
#         dist.name.replace("-", "_")
#         for dist in distributions()
#         if not any(pat in dist.name.lower() for pat in skip_patterns)
#     ]
# 
#     # Focus on commonly used packages first
#     safelist = [
#         "numpy",
#         "pandas",
#         "scipy",
#         "matplotlib",
#         "sklearn",
#         "torch",
#         "tensorflow",
#         "keras",
#         "xarray",
#         "dask",
#         "pytest",
#         "requests",
#         "flask",
#         "django",
#         "seaborn",
#     ]
# 
#     # Prioritize safelist packages
#     installed_packages = [pkg for pkg in installed_packages if pkg in safelist] + [
#         pkg for pkg in installed_packages if pkg not in safelist
#     ]
# 
#     all_dfs = []
#     for package_name in installed_packages:
#         try:
#             df = inspect_module(
#                 package_name,
#                 docstring=False,  # Speed up by skipping docstrings
#                 print_output=False,
#                 columns=["Name"],
#                 root_only=root_only,
#                 max_depth=max_depth,
#                 skip_depwarnings=True,
#             )
#             if not df.empty:
#                 all_dfs.append(df)
#         except Exception as err:
#             if verbose:
#                 print(f"Error processing {package_name}: {err}")
#             if not skip_errors:
#                 raise
# 
#     if not all_dfs:
#         return pd.DataFrame(columns=["Name"])
# 
#     combined_df = pd.concat(all_dfs, ignore_index=True)
#     return combined_df.drop_duplicates().sort_values("Name")
# 
# 
# def main() -> Optional[int]:
#     """Main function for testing package listing functionality."""
#     df = list_packages(verbose=True)
#     __import__("ipdb").set_trace()
#     return 0
# 
# 
# if __name__ == "__main__":
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys,
#         plt,
#         verbose=False,
#         agg=True,
#     )
# 
#     exit_status = main()
# 
#     scitex.gen.close(
#         CONFIG,
#         verbose=False,
#         sys=sys,
#         notify=False,
#         message="",
#         exit_status=exit_status,
#     )
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_list_packages.py
# --------------------------------------------------------------------------------
