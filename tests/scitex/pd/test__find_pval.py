#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 10:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__find_pval.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys


class TestFindPvalDataFrame:
    """Test find_pval with DataFrame inputs."""

    def test_single_pval_column(self):
        """Test finding single p-value column."""
from scitex.pd import find_pval

        df = pd.DataFrame({"p_value": [0.05, 0.01], "other": [1, 2]})
        result = find_pval(df, multiple=False)

        assert result == "p_value"

    def test_multiple_pval_columns(self):
        """Test finding multiple p-value columns."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {
                "p_value": [0.05, 0.01],
                "pval": [0.1, 0.001],
                "p-val": [0.2, 0.02],
                "other": [1, 2],
            }
        )
        result = find_pval(df, multiple=True)

        assert isinstance(result, list)
        assert set(result) == {"p_value", "pval", "p-val"}

    def test_pvalue_variations(self):
        """Test various p-value column name variations."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {
                "pval": [0.1],
                "p_val": [0.2],
                "p-val": [0.3],
                "pvalue": [0.4],
                "p_value": [0.5],
                "p-value": [0.6],
                "Pval": [0.7],
                "PVALUE": [0.8],
                "P_Value": [0.9],
            }
        )
        result = find_pval(df, multiple=True)

        assert len(result) == 9
        assert all(col in result for col in df.columns)

    def test_no_pval_columns(self):
        """Test when no p-value columns exist."""
from scitex.pd import find_pval

        df = pd.DataFrame({"alpha": [0.05], "beta": [0.1], "gamma": [1]})
        result = find_pval(df, multiple=False)

        assert result is None

    def test_no_pval_columns_multiple(self):
        """Test when no p-value columns exist with multiple=True."""
from scitex.pd import find_pval

        df = pd.DataFrame({"alpha": [0.05], "beta": [0.1], "gamma": [1]})
        result = find_pval(df, multiple=True)

        assert result == []

    def test_pval_stars_exclusion(self):
        """Test that p-value stars columns are excluded."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {
                "p_value": [0.05],
                "pval_stars": ["*"],
                "p_value_stars": ["**"],
                "pvalstars": ["***"],
            }
        )
        result = find_pval(df, multiple=True)

        assert result == ["p_value"]

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
from scitex.pd import find_pval

        df = pd.DataFrame()
        result = find_pval(df, multiple=True)

        assert result == []


class TestFindPvalDict:
    """Test find_pval with dictionary inputs."""

    def test_dict_single_match(self):
        """Test finding p-value key in dictionary."""
from scitex.pd import find_pval

        data = {"p_value": 0.05, "coefficient": 1.2, "se": 0.1}
        result = find_pval(data, multiple=False)

        assert result == "p_value"

    def test_dict_multiple_matches(self):
        """Test finding multiple p-value keys in dictionary."""
from scitex.pd import find_pval

        data = {"p_value": 0.05, "pval": 0.01, "p-val": 0.02, "coefficient": 1.2}
        result = find_pval(data, multiple=True)

        assert set(result) == {"p_value", "pval", "p-val"}

    def test_dict_no_matches(self):
        """Test dictionary with no p-value keys."""
from scitex.pd import find_pval

        data = {"alpha": 0.05, "beta": 0.1, "gamma": 1}
        result = find_pval(data, multiple=False)

        assert result is None

    def test_nested_dict(self):
        """Test with nested dictionary structure."""
from scitex.pd import find_pval

        data = {"results": {"p_value": 0.05}, "p_val": 0.01}
        result = find_pval(data, multiple=True)

        # Should only find top-level keys
        assert result == ["p_val"]


class TestFindPvalList:
    """Test find_pval with list inputs."""

    def test_list_of_dicts(self):
        """Test list of dictionaries."""
from scitex.pd import find_pval

        data = [
            {"p_value": 0.05, "coef": 1.2},
            {"p_value": 0.01, "coef": 2.3},
            {"p_value": 0.001, "coef": 3.4},
        ]
        result = find_pval(data, multiple=False)

        assert result == "p_value"

    def test_list_of_dicts_multiple_pvals(self):
        """Test list of dictionaries with multiple p-value keys."""
from scitex.pd import find_pval

        data = [
            {"p_value": 0.05, "pval": 0.06, "coef": 1.2},
            {"p_value": 0.01, "pval": 0.02, "coef": 2.3},
        ]
        result = find_pval(data, multiple=True)

        assert set(result) == {"p_value", "pval"}

    def test_empty_list(self):
        """Test empty list."""
from scitex.pd import find_pval

        data = []
        result = find_pval(data, multiple=True)

        assert result == []

    def test_list_of_non_dicts(self):
        """Test list of non-dictionary items."""
from scitex.pd import find_pval

        data = [1, 2, 3, 4]
        result = find_pval(data, multiple=False)

        assert result is None


class TestFindPvalNumPy:
    """Test find_pval with numpy array inputs."""

    def test_numpy_array_of_dicts(self):
        """Test numpy array containing dictionaries."""
from scitex.pd import find_pval

        data = np.array(
            [{"p_value": 0.05, "stat": 2.1}, {"p_value": 0.01, "stat": 3.2}]
        )
        result = find_pval(data, multiple=False)

        assert result == "p_value"

    def test_numpy_structured_array(self):
        """Test with numpy structured array."""
from scitex.pd import find_pval

        # Regular numpy arrays don't have column names
        data = np.array([1, 2, 3])
        result = find_pval(data, multiple=False)

        assert result is None

    def test_numpy_empty_array(self):
        """Test with empty numpy array."""
from scitex.pd import find_pval

        data = np.array([])
        result = find_pval(data, multiple=True)

        assert result == []


class TestFindPvalEdgeCases:
    """Test edge cases and error handling."""

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {"P_VALUE": [0.05], "Pval": [0.01], "P-Val": [0.02], "PVALUE": [0.03]}
        )
        result = find_pval(df, multiple=True)

        assert len(result) == 4

    def test_numeric_column_names(self):
        """Test with numeric column names."""
from scitex.pd import find_pval

        df = pd.DataFrame({0: [1, 2], 1: [3, 4], "p_value": [0.05, 0.01]})
        result = find_pval(df, multiple=False)

        assert result == "p_value"

    def test_special_characters(self):
        """Test column names with special characters."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {"p.value": [0.05], "p$val": [0.01], "p_value!": [0.02], "normal": [1]}
        )
        result = find_pval(df, multiple=True)

        # The regex pattern requires 'p' followed by optional '-' or '_', then 'val'
        # So 'p.value' and 'p$val' won't match, but 'p_value!' will
        assert "p_value!" in result
        assert len(result) == 1

    def test_invalid_input_type(self):
        """Test with invalid input type."""
from scitex.pd import find_pval

        with pytest.raises(ValueError, match="Input must be a pandas DataFrame"):
            find_pval("invalid_input")

    def test_partial_matches(self):
        """Test that partial matches work correctly."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {
                "pval_test": [0.05],
                "test_pvalue": [0.01],
                "my_p_value_column": [0.02],
                "not_related": [1],
            }
        )
        result = find_pval(df, multiple=True)

        assert len(result) == 3
        assert "not_related" not in result


class TestFindPvalDocumentation:
    """Test examples from documentation."""

    def test_docstring_example_multiple(self):
        """Test the multiple=True example from docstring."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {"p_value": [0.05, 0.01], "pval": [0.1, 0.001], "other": [1, 2]}
        )
        result = find_pval(df)  # default multiple=True

        assert set(result) == {"p_value", "pval"}

    def test_docstring_example_single(self):
        """Test the multiple=False example from docstring."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {"p_value": [0.05, 0.01], "pval": [0.1, 0.001], "other": [1, 2]}
        )
        result = find_pval(df, multiple=False)

        assert result == "p_value"

    def test_function_alias(self):
        """Test that _find_pval_col works directly."""
from scitex.pd import _find_pval_col

        df = pd.DataFrame({"p_value": [0.05], "data": [10]})
        result = _find_pval_col(df, multiple=False)

        assert result == "p_value"


class TestFindPvalIntegration:
    """Integration tests with real-world scenarios."""

    def test_statistical_results_dataframe(self):
        """Test with typical statistical results DataFrame."""
from scitex.pd import find_pval

        df = pd.DataFrame(
            {
                "variable": ["age", "gender", "treatment"],
                "coefficient": [0.5, -0.3, 1.2],
                "std_error": [0.1, 0.2, 0.3],
                "t_statistic": [5.0, -1.5, 4.0],
                "p_value": [0.001, 0.134, 0.002],
                "confidence_lower": [0.3, -0.7, 0.6],
                "confidence_upper": [0.7, 0.1, 1.8],
            }
        )
        result = find_pval(df, multiple=False)

        assert result == "p_value"

    def test_multiple_test_results(self):
        """Test with multiple test results format."""
from scitex.pd import find_pval

        results = [
            {"test": "t-test", "statistic": 2.5, "pval": 0.012},
            {"test": "chi-square", "statistic": 5.3, "pval": 0.021},
            {"test": "anova", "statistic": 3.8, "pval": 0.052},
        ]
        result = find_pval(results)

        assert result == ["pval"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
