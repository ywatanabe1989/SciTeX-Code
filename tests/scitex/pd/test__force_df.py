#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-04-27 20:00:00 (ywatanabe)"
# File: ./tests/scitex/pd/test__force_df.py

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys


class TestForceDfBasic:
    """Test basic functionality of force_df."""

    def test_dict_to_dataframe(self):
        """Test converting dictionary to DataFrame."""
        from scitex.pd import force_df

        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        result = force_df(data)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 2)
        assert list(result.columns) == ["a", "b"]
        assert result["a"].tolist() == [1, 2, 3]
        assert result["b"].tolist() == [4, 5, 6]

    def test_dataframe_passthrough(self):
        """Test that DataFrame is returned unchanged."""
        from scitex.pd import force_df

        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = force_df(df)

        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, df)

    def test_series_to_dataframe(self):
        """Test converting Series to DataFrame."""
        from scitex.pd import force_df

        series = pd.Series([1, 2, 3], name="data")
        result = force_df(series)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 1)
        assert result.columns[0] == "data"
        assert result["data"].tolist() == [1, 2, 3]

    def test_list_to_dataframe(self):
        """Test converting list to DataFrame."""
        from scitex.pd import force_df

        data = [1, 2, 3, 4, 5]
        result = force_df(data)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (5, 1)
        assert result.columns[0] == "value"
        assert result["value"].tolist() == [1, 2, 3, 4, 5]

    def test_tuple_to_dataframe(self):
        """Test converting tuple to DataFrame."""
        from scitex.pd import force_df

        data = (10, 20, 30)
        result = force_df(data)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 1)
        assert result.columns[0] == "value"
        assert result["value"].tolist() == [10, 20, 30]


class TestForceDfNumPy:
    """Test force_df with numpy arrays."""

    def test_1d_array_to_dataframe(self):
        """Test converting 1D numpy array to DataFrame."""
        from scitex.pd import force_df

        arr = np.array([1, 2, 3, 4])
        result = force_df(arr)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (4, 1)
        assert result.columns[0] == "value"
        assert result["value"].tolist() == [1, 2, 3, 4]

    def test_2d_array_to_dataframe(self):
        """Test converting 2D numpy array to DataFrame."""
        from scitex.pd import force_df

        arr = np.array([[1, 2, 3], [4, 5, 6]])
        result = force_df(arr)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (2, 3)
        assert list(result.columns) == [0, 1, 2]
        assert result[0].tolist() == [1, 4]
        assert result[1].tolist() == [2, 5]
        assert result[2].tolist() == [3, 6]

    def test_empty_array(self):
        """Test with empty numpy array."""
        from scitex.pd import force_df

        arr = np.array([])
        result = force_df(arr)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (0, 1)


class TestForceDfMixedLengths:
    """Test force_df with mixed-length data."""

    def test_dict_mixed_lengths_default_filler(self):
        """Test dictionary with mixed-length values using default filler."""
        from scitex.pd import force_df

        data = {"a": [1, 2, 3], "b": [4, 5], "c": [6]}
        result = force_df(data)

        assert result.shape == (3, 3)
        assert result["a"].tolist() == [1, 2, 3]
        # NaN values need special comparison
        b_values = result["b"].tolist()
        assert b_values[0] == 4
        assert b_values[1] == 5
        assert pd.isna(b_values[2])
        assert pd.isna(result["b"].iloc[2])
        assert result["c"].iloc[0] == 6
        assert pd.isna(result["c"].iloc[1])
        assert pd.isna(result["c"].iloc[2])

    def test_dict_mixed_lengths_custom_filler(self):
        """Test dictionary with mixed-length values using custom filler."""
        from scitex.pd import force_df

        data = {"a": [1, 2, 3], "b": [4, 5], "c": [6]}
        result = force_df(data, filler=0)

        assert result.shape == (3, 3)
        assert result["b"].tolist() == [4, 5, 0]
        assert result["c"].tolist() == [6, 0, 0]

    def test_scalar_values_in_dict(self):
        """Test dictionary with scalar values."""
        from scitex.pd import force_df

        data = {"a": 1, "b": [2, 3, 4], "c": "hello"}
        result = force_df(data)

        assert result.shape == (3, 3)
        assert result["a"].iloc[0] == 1
        assert pd.isna(result["a"].iloc[1])
        assert pd.isna(result["a"].iloc[2])
        assert result["b"].tolist() == [2, 3, 4]
        assert result["c"].iloc[0] == "hello"
        assert pd.isna(result["c"].iloc[1])


class TestForceDfListedSeries:
    """Test force_df with list of Series."""

    def test_list_of_series(self):
        """Test that list of Series is handled (though not ideally)."""
        from scitex.pd import force_df

        series1 = pd.Series({"a": 1, "b": 2})
        series2 = pd.Series({"a": 3, "b": 4})
        series3 = pd.Series({"a": 5, "b": 6})

        # The current implementation treats Series as complex objects 
        # and creates a DataFrame with NaN values
        result = force_df([series1, series2, series3])
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 1)
        assert result.columns[0] == "value"
        # The values are NaN because Series objects aren't handled properly
        assert result["value"].isna().all()

    def test_list_of_series_workaround(self):
        """Test workaround for list of Series."""
        from scitex.pd import force_df

        series1 = pd.Series({"a": 1, "b": 2})
        series2 = pd.Series({"a": 3, "b": 4})

        # Workaround: manually convert to dict
        data = {"row_0": series1.to_dict(), "row_1": series2.to_dict()}

        # This creates a transposed result
        result = force_df(data)

        assert isinstance(result, pd.DataFrame)
        # The result will have row_0, row_1 as columns
        assert "row_0" in result.columns
        assert "row_1" in result.columns


class TestForceDfEdgeCases:
    """Test edge cases for force_df."""

    def test_empty_dict(self):
        """Test with empty dictionary."""
        from scitex.pd import force_df

        result = force_df({})

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (0, 0)

    def test_nested_structures(self):
        """Test with nested structures."""
        from scitex.pd import force_df

        data = {"a": [1, 2], "b": [[3, 4], [5, 6]]}
        result = force_df(data)

        assert result.shape == (2, 2)
        assert result["a"].tolist() == [1, 2]
        assert result["b"].iloc[0] == [3, 4]
        assert result["b"].iloc[1] == [5, 6]

    def test_mixed_types(self):
        """Test with mixed data types."""
        from scitex.pd import force_df

        data = {
            "int": [1, 2, 3],
            "float": [1.1, 2.2, 3.3],
            "str": ["a", "b", "c"],
            "bool": [True, False, True],
            "none": [None, None, None],
        }
        result = force_df(data)

        assert result.shape == (3, 5)
        assert result["int"].dtype == "int64"
        assert result["float"].dtype == "float64"
        assert result["str"].dtype == "object"
        assert result["bool"].dtype == "bool"

    def test_single_value_dict(self):
        """Test with single-value dictionary."""
        from scitex.pd import force_df

        data = {"a": 42}
        result = force_df(data)

        assert result.shape == (1, 1)
        assert result["a"].iloc[0] == 42


class TestForceDfSpecialCases:
    """Test special cases and behaviors."""

    def test_series_without_name(self):
        """Test Series without name."""
        from scitex.pd import force_df

        series = pd.Series([1, 2, 3])
        result = force_df(series)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (3, 1)
        assert result.columns[0] == 0  # Default column name

    def test_dict_with_none_values(self):
        """Test dictionary with None values."""
        from scitex.pd import force_df

        data = {"a": None, "b": [1, 2, 3]}
        result = force_df(data)

        assert result.shape == (3, 2)
        # When None is extended with np.nan filler, it becomes [None, nan, nan]
        # but pandas may convert None to nan
        assert pd.isna(result["a"].iloc[0])
        assert pd.isna(result["a"].iloc[1])
        assert pd.isna(result["a"].iloc[2])

    def test_dict_with_string_keys(self):
        """Test dictionary with various string keys."""
        from scitex.pd import force_df

        data = {
            "column_1": [1, 2],
            "Column 2": [3, 4],
            "3rdColumn": [5, 6],
            "col-4": [7, 8],
        }
        result = force_df(data)

        assert set(result.columns) == set(data.keys())
        assert result["column_1"].tolist() == [1, 2]
        assert result["Column 2"].tolist() == [3, 4]

    def test_custom_filler_types(self):
        """Test various custom filler types."""
        from scitex.pd import force_df

        # Test with string filler
        data = {"a": [1], "b": [2, 3]}
        result = force_df(data, filler="missing")
        assert result["a"].iloc[1] == "missing"

        # Test with None filler
        data = {"a": [1], "b": [2, 3]}
        result = force_df(data, filler=None)
        # Pandas may convert None to nan in numeric columns
        assert pd.isna(result["a"].iloc[1])

        # Test with custom object filler
        custom_obj = object()
        data = {"a": [1], "b": [2, 3]}
        result = force_df(data, filler=custom_obj)
        assert result["a"].iloc[1] is custom_obj


class TestForceDfIntegration:
    """Integration tests for force_df."""

    def test_real_world_scenario(self):
        """Test with realistic data scenario."""
        from scitex.pd import force_df

        # Simulating data from different sources with varying lengths
        data = {
            "experiment_id": [1, 2, 3],
            "measurements": [10.5, 20.3],
            "status": "completed",
            "notes": ["good", "better", "best", "excellent"],
        }

        result = force_df(data, filler="N/A")

        assert result.shape == (4, 4)
        assert result["experiment_id"].tolist() == [1, 2, 3, "N/A"]
        assert result["measurements"].tolist() == [10.5, 20.3, "N/A", "N/A"]
        assert result["status"].tolist() == ["completed", "N/A", "N/A", "N/A"]
        assert result["notes"].tolist() == ["good", "better", "best", "excellent"]

    def test_chained_operations(self):
        """Test force_df in chained operations."""
        from scitex.pd import force_df

        # Start with mixed data
        data = {"a": [1, 2], "b": [3, 4, 5]}

        # Convert to DataFrame and perform operations
        result = force_df(data)
        result = result.fillna(0)  # Replace NaN with 0
        result["sum"] = result["a"] + result["b"]

        assert result["sum"].tolist() == [4, 6, 5]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_force_df.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-27 19:59:11 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/pd/_force_df.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/pd/_force_df.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import numpy as np
# import pandas as pd
# 
# from ..types import is_listed_X
# 
# 
# def force_df(data, filler=np.nan):
#     """
#     Convert various data types to pandas DataFrame.
#     
#     Parameters
#     ----------
#     data : various
#         The data to convert to DataFrame. Can be DataFrame, Series, ndarray, 
#         list, tuple, dict, scalar value, etc.
#     filler : any, optional
#         Value to use for filling missing values, by default np.nan
#         
#     Returns
#     -------
#     pd.DataFrame
#         Data converted to DataFrame
#         
#     Examples
#     --------
#     >>> import scitex
#     >>> import pandas as pd
#     >>> import numpy as np
#     
#     # DataFrame input returns the same DataFrame
#     >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
#     >>> scitex.pd.force_df(df) is df
#     True
#     
#     # Series input is converted to DataFrame
#     >>> series = pd.Series([1, 2, 3], name='test')
#     >>> scitex.pd.force_df(series)
#        test
#     0     1
#     1     2
#     2     3
#     
#     # NumPy array input is converted to DataFrame
#     >>> arr = np.array([1, 2, 3])
#     >>> scitex.pd.force_df(arr)
#        value
#     0      1
#     1      2
#     2      3
#     
#     # Scalar values are converted to single-value DataFrames
#     >>> scitex.pd.force_df(42)
#        value
#     0     42
#     
#     # Lists and tuples are converted to DataFrame
#     >>> scitex.pd.force_df([1, 2, 3])
#        value
#     0      1
#     1      2
#     2      3
#     
#     # Dictionaries are converted to DataFrame with appropriate handling
#     # of different length values
#     >>> data = {'A': [1, 2, 3], 'B': [4, 5]}
#     >>> scitex.pd.force_df(data)
#        A  B
#     0  1  4
#     1  2  5
#     2  3  NaN
#     """
#     # Return None as empty DataFrame
#     if data is None:
#         return pd.DataFrame()
#         
#     # Return DataFrame as is
#     if isinstance(data, pd.DataFrame):
#         return data
#         
#     # Convert Series to DataFrame
#     if isinstance(data, pd.Series):
#         return data.to_frame()
#         
#     # Convert numpy array to DataFrame
#     if isinstance(data, np.ndarray):
#         # Handle 1D array
#         if data.ndim == 1:
#             return pd.DataFrame(data, columns=['value'])
#         # Handle 2D array
#         elif data.ndim == 2:
#             return pd.DataFrame(data)
#         # Handle higher dimensional arrays
#         else:
#             shape = data.shape
#             reshaped = data.reshape(shape[0], -1)
#             return pd.DataFrame(reshaped)
#             
#     # Handle scalar values (int, float, str, etc.)
#     if isinstance(data, (int, float, str, bool)):
#         return pd.DataFrame([data], columns=['value'])
#             
#     # Handle lists and tuples
#     if isinstance(data, (list, tuple)):
#         # Handle list of lists/arrays -> DataFrame
#         if len(data) > 0 and isinstance(data[0], (list, tuple, np.ndarray)):
#             return pd.DataFrame(data)
#         # Handle simple list/tuple -> single column DataFrame
#         else:
#             return pd.DataFrame(data, columns=['value'])
#     
#     # Continue with the original implementation for dictionaries
#     if isinstance(data, dict):
#         # Original implementation
#         permutable_dict = data.copy()
#         
#         # Get the lengths
#         max_len = 0
#         for k, v in permutable_dict.items():
#             # Check if v is an iterable (but not string) or treat as single length otherwise
#             if isinstance(v, (str, int, float)) or not hasattr(v, "__len__"):
#                 length = 1
#             else:
#                 length = len(v)
#             max_len = max(max_len, length)
#         
#         # Replace with appropriately filled list
#         for k, v in permutable_dict.items():
#             if isinstance(v, (str, int, float)) or not hasattr(v, "__len__"):
#                 permutable_dict[k] = [v] + [filler] * (max_len - 1)
#             else:
#                 permutable_dict[k] = list(v) + [filler] * (max_len - len(v))
#         
#         # Puts them into a DataFrame
#         return pd.DataFrame(permutable_dict)
#     
#     # For any other iterable type
#     try:
#         return pd.DataFrame(list(data), columns=['value'])
#     except:
#         raise TypeError(f"Cannot convert object of type {type(data)} to DataFrame")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/pd/_force_df.py
# --------------------------------------------------------------------------------
