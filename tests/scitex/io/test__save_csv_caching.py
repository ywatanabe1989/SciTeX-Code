#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 17:45:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/io/test__save_csv_caching.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/test__save_csv_caching.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import os
import sys
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import time
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex


class TestCSVCaching:
    """Test cases for CSV hash caching functionality in scitex.io.save."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_csv_deduplication_dataframe(self, temp_dir):
        """Test that identical DataFrames don't rewrite CSV files."""
        # Arrange
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        csv_path = os.path.join(temp_dir, "test_data.csv")
        
        # Act - First save
        scitex.io.save(df, csv_path, verbose=False, index=False)
        first_mtime = os.path.getmtime(csv_path)
        
        # Wait a bit to ensure different mtime if file is rewritten
        time.sleep(0.1)
        
        # Act - Second save with identical data
        scitex.io.save(df, csv_path, verbose=False, index=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert - File should not be rewritten
        assert first_mtime == second_mtime, "File was rewritten despite identical content"

    def test_csv_deduplication_numpy_array(self, temp_dir):
        """Test that identical NumPy arrays don't rewrite CSV files."""
        # Arrange
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        csv_path = os.path.join(temp_dir, "test_array.csv")
        
        # Act - First save
        scitex.io.save(arr, csv_path, verbose=False)
        first_mtime = os.path.getmtime(csv_path)
        
        # Wait a bit
        time.sleep(0.1)
        
        # Act - Second save with identical array
        scitex.io.save(arr, csv_path, verbose=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert
        assert first_mtime == second_mtime, "File was rewritten despite identical content"

    def test_csv_update_on_change(self, temp_dir):
        """Test that CSV files ARE updated when content changes."""
        # Arrange
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 7]})  # Changed last value
        csv_path = os.path.join(temp_dir, "test_change.csv")
        
        # Act - First save
        scitex.io.save(df1, csv_path, verbose=False, index=False)
        first_mtime = os.path.getmtime(csv_path)
        
        # Wait a bit
        time.sleep(0.1)
        
        # Act - Second save with different data
        scitex.io.save(df2, csv_path, verbose=False, index=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert - File should be updated
        assert second_mtime > first_mtime, "File was not updated despite content change"
        
        # Verify content actually changed
        loaded = pd.read_csv(csv_path)
        pd.testing.assert_frame_equal(loaded, df2)

    def test_csv_caching_with_lists(self, temp_dir):
        """Test CSV caching with list inputs."""
        # Arrange
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        csv_path = os.path.join(temp_dir, "test_list.csv")
        
        # Act - Save twice
        scitex.io.save(data, csv_path, verbose=False)
        first_mtime = os.path.getmtime(csv_path)
        
        time.sleep(0.1)
        
        scitex.io.save(data, csv_path, verbose=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert
        assert first_mtime == second_mtime, "List data was rewritten despite being identical"

    def test_csv_caching_with_dict(self, temp_dir):
        """Test CSV caching with dictionary inputs."""
        # Arrange
        data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}
        csv_path = os.path.join(temp_dir, "test_dict.csv")
        
        # Act
        scitex.io.save(data, csv_path, verbose=False)
        first_mtime = os.path.getmtime(csv_path)
        
        time.sleep(0.1)
        
        scitex.io.save(data, csv_path, verbose=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert
        assert first_mtime == second_mtime, "Dict data was rewritten despite being identical"

    def test_csv_caching_performance(self, temp_dir):
        """Test that caching improves performance for repeated saves."""
        # Arrange
        df = pd.DataFrame(np.random.rand(1000, 10))  # Large DataFrame
        csv_path = os.path.join(temp_dir, "test_performance.csv")
        
        # Act - First save (no cache)
        start1 = time.perf_counter()
        scitex.io.save(df, csv_path, verbose=False, index=False)
        time1 = time.perf_counter() - start1
        
        # Act - Second save (should use cache)
        start2 = time.perf_counter()
        scitex.io.save(df, csv_path, verbose=False, index=False)
        time2 = time.perf_counter() - start2
        
        # Assert - Cached save should be faster
        # Allow some variance but generally should be much faster
        assert time2 < time1 * 0.8, f"Caching didn't improve performance: {time1:.4f}s vs {time2:.4f}s"

    def test_csv_caching_with_single_value(self, temp_dir):
        """Test CSV caching with single value inputs."""
        # Arrange
        value = 42
        csv_path = os.path.join(temp_dir, "test_single.csv")
        
        # Act
        scitex.io.save(value, csv_path, verbose=False)
        first_mtime = os.path.getmtime(csv_path)
        
        time.sleep(0.1)
        
        scitex.io.save(value, csv_path, verbose=False)
        second_mtime = os.path.getmtime(csv_path)
        
        # Assert
        assert first_mtime == second_mtime, "Single value was rewritten despite being identical"

    def test_csv_caching_edge_cases(self, temp_dir):
        """Test CSV caching with edge cases."""
        csv_path = os.path.join(temp_dir, "test_edge.csv")
        
        # Test 1: Empty DataFrame
        empty_df = pd.DataFrame()
        scitex.io.save(empty_df, csv_path, verbose=False)
        mtime1 = os.path.getmtime(csv_path)
        
        time.sleep(0.1)
        scitex.io.save(empty_df, csv_path, verbose=False)
        mtime2 = os.path.getmtime(csv_path)
        assert mtime1 == mtime2, "Empty DataFrame was rewritten"
        
        # Test 2: DataFrame with NaN values
        nan_df = pd.DataFrame({'A': [1, np.nan, 3], 'B': [4, 5, np.nan]})
        csv_path_nan = os.path.join(temp_dir, "test_nan.csv")
        
        scitex.io.save(nan_df, csv_path_nan, verbose=False, index=False)
        mtime1 = os.path.getmtime(csv_path_nan)
        
        time.sleep(0.1)
        scitex.io.save(nan_df, csv_path_nan, verbose=False, index=False)
        mtime2 = os.path.getmtime(csv_path_nan)
        assert mtime1 == mtime2, "DataFrame with NaN was rewritten"

    def test_csv_caching_file_not_exists(self, temp_dir):
        """Test CSV caching when file doesn't exist initially."""
        # Arrange
        df = pd.DataFrame({'A': [1, 2, 3]})
        csv_path = os.path.join(temp_dir, "new_file.csv")
        
        # Assert file doesn't exist
        assert not os.path.exists(csv_path)
        
        # Act - Should create file without error
        scitex.io.save(df, csv_path, verbose=False, index=False)
        
        # Assert
        assert os.path.exists(csv_path)
        loaded = pd.read_csv(csv_path)
        pd.testing.assert_frame_equal(loaded, df)


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])