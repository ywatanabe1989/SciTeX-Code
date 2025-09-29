#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:41:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__csv.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__csv.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for CSV saving functionality
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from scitex.io._save_modules import save_csv


class TestSaveCSV:
    """Test suite for save_csv function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.csv")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_dataframe(self):
        """Test saving a pandas DataFrame"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        save_csv(df, self.test_file)
        
        # Verify file exists and content is correct
        assert os.path.exists(self.test_file)
        loaded_df = pd.read_csv(self.test_file, index_col=0)
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_save_dataframe_no_index(self):
        """Test saving DataFrame without index"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        save_csv(df, self.test_file, index=False)
        
        loaded_df = pd.read_csv(self.test_file)
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_save_series(self):
        """Test saving a pandas Series"""
        series = pd.Series([1, 2, 3], name="test_series")
        save_csv(series, self.test_file)
        
        assert os.path.exists(self.test_file)
        loaded_df = pd.read_csv(self.test_file, index_col=0)
        pd.testing.assert_series_equal(series, loaded_df["test_series"])

    def test_save_numpy_array(self):
        """Test saving numpy array"""
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        save_csv(arr, self.test_file)
        
        loaded_df = pd.read_csv(self.test_file)
        np.testing.assert_array_equal(arr, loaded_df.values)

    def test_save_list(self):
        """Test saving list of numbers"""
        data = [1, 2, 3, 4, 5]
        save_csv(data, self.test_file)
        
        loaded_df = pd.read_csv(self.test_file)
        assert list(loaded_df.iloc[:, 0]) == data

    def test_save_list_of_dataframes(self):
        """Test saving list of DataFrames"""
        df1 = pd.DataFrame({"a": [1, 2]})
        df2 = pd.DataFrame({"a": [3, 4]})
        save_csv([df1, df2], self.test_file)
        
        loaded_df = pd.read_csv(self.test_file, index_col=0)
        expected = pd.concat([df1, df2])
        pd.testing.assert_frame_equal(expected, loaded_df)

    def test_save_dict(self):
        """Test saving dictionary"""
        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        save_csv(data, self.test_file)
        
        loaded_df = pd.read_csv(self.test_file)
        pd.testing.assert_frame_equal(pd.DataFrame(data), loaded_df)

    def test_save_scalar(self):
        """Test saving single scalar value"""
        save_csv(42, self.test_file)
        
        loaded_df = pd.read_csv(self.test_file)
        assert loaded_df.iloc[0, 0] == 42

    def test_caching_same_content(self):
        """Test that saving identical content doesn't rewrite file"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        
        # Save once
        save_csv(df, self.test_file, index=False)
        mtime1 = os.path.getmtime(self.test_file)
        
        # Save again with same content
        import time
        time.sleep(0.01)  # Ensure time difference
        save_csv(df, self.test_file, index=False)
        mtime2 = os.path.getmtime(self.test_file)
        
        # File should not have been rewritten
        assert mtime1 == mtime2

    def test_caching_different_content(self):
        """Test that saving different content does rewrite file"""
        df1 = pd.DataFrame({"a": [1, 2, 3]})
        df2 = pd.DataFrame({"a": [4, 5, 6]})
        
        # Save first dataframe
        save_csv(df1, self.test_file, index=False)
        mtime1 = os.path.getmtime(self.test_file)
        
        # Save different dataframe
        import time
        time.sleep(0.01)  # Ensure time difference
        save_csv(df2, self.test_file, index=False)
        mtime2 = os.path.getmtime(self.test_file)
        
        # File should have been rewritten
        assert mtime2 > mtime1

    def test_save_with_custom_kwargs(self):
        """Test saving with custom pandas kwargs"""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        save_csv(df, self.test_file, index=False, sep=";")
        
        # Verify with custom separator
        loaded_df = pd.read_csv(self.test_file, sep=";")
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_save_mixed_types(self):
        """Test saving mixed data types"""
        data = {"int": [1, 2, 3], 
                "float": [1.1, 2.2, 3.3],
                "str": ["a", "b", "c"]}
        save_csv(data, self.test_file)
        
        loaded_df = pd.read_csv(self.test_file)
        assert loaded_df["int"].dtype == np.int64
        assert loaded_df["float"].dtype == np.float64
        assert loaded_df["str"].dtype == object

    def test_error_unsupported_type(self):
        """Test error handling for unsupported types"""
        # Complex object that can't be converted to DataFrame
        class CustomObject:
            pass
        
        obj = CustomObject()
        with pytest.raises(ValueError, match="Unable to save type"):
            save_csv(obj, self.test_file)


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_csv.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:12:18 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_csv.py
# 
# import os
# import pandas as pd
# import numpy as np
# 
# 
# def _save_csv(obj, spath: str, **kwargs) -> None:
#     """
#     Save data to a CSV file, handling various input types appropriately.
#     
#     Parameters
#     ----------
#     obj : Any
#         The object to save. Can be DataFrame, Series, ndarray, list, tuple, dict, or scalar.
#     spath : str
#         Path where the CSV file will be saved.
#     **kwargs : dict
#         Additional keyword arguments to pass to the pandas to_csv method.
#         
#     Returns
#     -------
#     None
#     
#     Raises
#     ------
#     ValueError
#         If the object type cannot be converted to CSV format.
#     """
#     # Check if path already exists
#     if os.path.exists(spath):
#         # Calculate hash of new data
#         data_hash = None
# 
#         # Process based on type
#         if isinstance(obj, (pd.Series, pd.DataFrame)):
#             data_hash = hash(obj.to_string())
#         elif isinstance(obj, np.ndarray):
#             data_hash = hash(pd.DataFrame(obj).to_string())
#         else:
#             # For other types, create a string representation and hash it
#             try:
#                 data_str = str(obj)
#                 data_hash = hash(data_str)
#             except:
#                 # If we can't hash it, proceed with saving
#                 pass
# 
#         # Compare with existing file if hash calculation was successful
#         if data_hash is not None:
#             try:
#                 existing_df = pd.read_csv(spath)
#                 existing_hash = hash(existing_df.to_string())
# 
#                 # Skip if hashes match
#                 if existing_hash == data_hash:
#                     return
#             except:
#                 # If reading fails, proceed with saving
#                 pass
# 
#     # Set default index=False if not explicitly specified in kwargs
#     if 'index' not in kwargs:
#         kwargs['index'] = False
#         
#     # Save the file based on type
#     if isinstance(obj, (pd.Series, pd.DataFrame)):
#         obj.to_csv(spath, **kwargs)
#     elif isinstance(obj, np.ndarray):
#         pd.DataFrame(obj).to_csv(spath, **kwargs)
#     elif isinstance(obj, (int, float)):
#         pd.DataFrame([obj]).to_csv(spath, **kwargs)
#     elif isinstance(obj, (list, tuple)):
#         if all(isinstance(x, (int, float)) for x in obj):
#             pd.DataFrame(obj).to_csv(spath, **kwargs)
#         elif all(isinstance(x, pd.DataFrame) for x in obj):
#             pd.concat(obj).to_csv(spath, **kwargs)
#         else:
#             pd.DataFrame({"data": obj}).to_csv(spath, **kwargs)
#     elif isinstance(obj, dict):
#         pd.DataFrame.from_dict(obj).to_csv(spath, **kwargs)
#     else:
#         # Check if it's a PaperCollection or similar object with to_dataframe method
#         if hasattr(obj, 'to_dataframe') and callable(getattr(obj, 'to_dataframe')):
#             obj.to_dataframe().to_csv(spath, **kwargs)
#         else:
#             try:
#                 pd.DataFrame({"data": [obj]}).to_csv(spath, **kwargs)
#             except:
#                 raise ValueError(f"Unable to save type {type(obj)} as CSV")

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_csv.py
# --------------------------------------------------------------------------------
