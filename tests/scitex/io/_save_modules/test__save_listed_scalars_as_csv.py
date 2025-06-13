#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 14:00:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__save_listed_scalars_as_csv.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__save_listed_scalars_as_csv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for saving listed scalars as CSV functionality
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from scitex.io._save_modules import save_listed_scalars_as_csv


class TestSaveListedScalarsAsCSV:
    """Test suite for save_listed_scalars_as_csv function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_scalars.csv")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_scalars(self):
        """Test saving list of simple scalar values"""
        scalars = [1, 2, 3, 4, 5]
        save_listed_scalars_as_csv(scalars, self.test_file)
        
        assert os.path.exists(self.test_file)
        
        # Load and verify
        loaded = pd.read_csv(self.test_file)
        assert list(loaded.iloc[:, 0]) == scalars

    def test_save_with_labels(self):
        """Test saving scalars with labels"""
        scalars = [10, 20, 30]
        labels = ["A", "B", "C"]
        
        save_listed_scalars_as_csv(scalars, self.test_file, labels=labels)
        
        loaded = pd.read_csv(self.test_file)
        
        # Should have label and value columns
        assert "label" in loaded.columns
        assert "value" in loaded.columns
        assert list(loaded["label"]) == labels
        assert list(loaded["value"]) == scalars

    def test_save_mixed_numeric_types(self):
        """Test saving mixed numeric types"""
        scalars = [
            1,           # int
            2.5,         # float
            np.int32(3), # numpy int
            np.float64(4.5), # numpy float
            5 + 0j,      # complex (real part)
        ]
        save_listed_scalars_as_csv(scalars, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        # Complex numbers might be saved as their real part or string
        assert len(loaded) == len(scalars)

    def test_save_boolean_values(self):
        """Test saving boolean values"""
        scalars = [True, False, True, False, True]
        save_listed_scalars_as_csv(scalars, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        # Booleans might be loaded as True/False strings or 1/0
        assert len(loaded) == 5

    def test_save_with_column_name(self):
        """Test saving with custom column name"""
        scalars = [1.1, 2.2, 3.3, 4.4]
        save_listed_scalars_as_csv(scalars, self.test_file, column_name="measurements")
        
        loaded = pd.read_csv(self.test_file)
        assert "measurements" in loaded.columns
        assert list(loaded["measurements"]) == pytest.approx(scalars)

    def test_save_large_list(self):
        """Test saving large list of scalars"""
        scalars = list(range(10000))
        save_listed_scalars_as_csv(scalars, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 10000
        assert loaded.iloc[0, 0] == 0
        assert loaded.iloc[-1, 0] == 9999

    def test_save_statistical_results(self):
        """Test saving statistical computation results"""
        # Simulate results from multiple experiments
        results = []
        for i in range(10):
            np.random.seed(i)
            mean_value = np.mean(np.random.randn(100))
            results.append(mean_value)
        
        save_listed_scalars_as_csv(results, self.test_file, column_name="mean_values")
        
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 10
        assert "mean_values" in loaded.columns

    def test_save_with_index(self):
        """Test saving with index"""
        scalars = [10, 20, 30, 40, 50]
        save_listed_scalars_as_csv(scalars, self.test_file, index=True)
        
        loaded = pd.read_csv(self.test_file, index_col=0)
        assert list(loaded.index) == [0, 1, 2, 3, 4]

    def test_save_with_custom_index(self):
        """Test saving with custom index names"""
        scalars = [100, 200, 300]
        index_names = ["sample_1", "sample_2", "sample_3"]
        
        save_listed_scalars_as_csv(
            scalars, 
            self.test_file, 
            index=index_names
        )
        
        loaded = pd.read_csv(self.test_file, index_col=0)
        assert list(loaded.index) == index_names

    def test_save_empty_list(self):
        """Test handling empty list"""
        with pytest.raises(ValueError):
            save_listed_scalars_as_csv([], self.test_file)

    def test_save_single_scalar(self):
        """Test saving single scalar in list"""
        save_listed_scalars_as_csv([42], self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        assert len(loaded) == 1
        assert loaded.iloc[0, 0] == 42

    def test_save_with_header(self):
        """Test saving with/without header"""
        scalars = [1, 2, 3]
        
        # With header (default)
        save_listed_scalars_as_csv(scalars, self.test_file)
        with open(self.test_file, 'r') as f:
            first_line = f.readline()
        assert "," in first_line or first_line.strip().isalpha()  # Has header
        
        # Without header
        no_header_file = os.path.join(self.temp_dir, "no_header.csv")
        save_listed_scalars_as_csv(scalars, no_header_file, header=False)
        with open(no_header_file, 'r') as f:
            first_line = f.readline()
        assert first_line.strip().replace('.', '').isdigit()  # First line is data

    def test_save_scientific_notation(self):
        """Test saving very large/small numbers"""
        scalars = [1e-10, 1e-5, 1.0, 1e5, 1e10]
        save_listed_scalars_as_csv(scalars, self.test_file)
        
        loaded = pd.read_csv(self.test_file)
        np.testing.assert_array_almost_equal(
            loaded.iloc[:, 0].values, 
            scalars,
            decimal=15
        )

    def test_save_with_metadata(self):
        """Test saving with additional metadata columns"""
        scalars = [0.1, 0.2, 0.3, 0.4]
        conditions = ["control", "control", "treatment", "treatment"]
        iterations = [1, 2, 1, 2]
        
        # Create DataFrame with metadata
        df = pd.DataFrame({
            "value": scalars,
            "condition": conditions,
            "iteration": iterations
        })
        
        # Save using the function (might need to adapt based on actual API)
        save_listed_scalars_as_csv(
            scalars, 
            self.test_file,
            metadata={"condition": conditions, "iteration": iterations}
        )
        
        loaded = pd.read_csv(self.test_file)
        assert "value" in loaded.columns or loaded.shape[1] >= 1

    def test_save_percentages(self):
        """Test saving percentage values"""
        percentages = [0.95, 0.87, 0.92, 0.89, 0.91]
        save_listed_scalars_as_csv(
            percentages, 
            self.test_file,
            column_name="accuracy"
        )
        
        loaded = pd.read_csv(self.test_file)
        assert "accuracy" in loaded.columns
        assert all(0 <= v <= 1 for v in loaded["accuracy"])

    def test_error_non_scalar_values(self):
        """Test error handling for non-scalar values"""
        with pytest.raises(TypeError):
            # Lists are not scalars
            save_listed_scalars_as_csv([[1, 2], [3, 4]], self.test_file)
        
        with pytest.raises(TypeError):
            # Dicts are not scalars
            save_listed_scalars_as_csv([{"a": 1}, {"b": 2}], self.test_file)


# EOF