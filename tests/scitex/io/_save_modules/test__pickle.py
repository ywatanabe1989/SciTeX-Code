#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:47:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__pickle.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__pickle.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for pickle saving functionality
"""

import os
import tempfile
import pytest
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

from scitex.io._save_modules import save_pickle


class TestSavePickle:
    """Test suite for save_pickle function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.pkl")
        self.test_file_compressed = os.path.join(self.temp_dir, "test.pkl.gz")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_object(self):
        """Test saving simple Python objects"""
        obj = {"a": 1, "b": [2, 3, 4], "c": "hello"}
        save_pickle(obj, self.test_file)
        
        assert os.path.exists(self.test_file)
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == obj

    def test_save_numpy_array(self):
        """Test saving numpy array"""
        arr = np.random.randn(10, 20)
        save_pickle(arr, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_pandas_dataframe(self):
        """Test saving pandas DataFrame"""
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4.5, 5.6, 6.7],
            "c": ["x", "y", "z"]
        })
        save_pickle(df, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        pd.testing.assert_frame_equal(df, loaded)

    def test_save_custom_class(self):
        """Test saving custom class instance"""
        class CustomClass:
            def __init__(self, x, y):
                self.x = x
                self.y = y
            
            def __eq__(self, other):
                return self.x == other.x and self.y == other.y
        
        obj = CustomClass(10, "test")
        save_pickle(obj, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded.x == 10
        assert loaded.y == "test"

    def test_save_nested_structure(self):
        """Test saving complex nested structure"""
        obj = {
            "arrays": [np.array([1, 2, 3]), np.array([[4, 5], [6, 7]])],
            "dataframes": [pd.DataFrame({"a": [1, 2]}), pd.DataFrame({"b": [3, 4]})],
            "mixed": {
                "int": 42,
                "float": 3.14,
                "str": "hello",
                "list": [1, 2, 3],
                "dict": {"nested": True}
            }
        }
        save_pickle(obj, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        
        # Check arrays
        for i, arr in enumerate(obj["arrays"]):
            np.testing.assert_array_equal(arr, loaded["arrays"][i])
        
        # Check dataframes
        for i, df in enumerate(obj["dataframes"]):
            pd.testing.assert_frame_equal(df, loaded["dataframes"][i])
        
        # Check mixed data
        assert loaded["mixed"]["int"] == 42
        assert loaded["mixed"]["float"] == pytest.approx(3.14)

    def test_save_compressed(self):
        """Test saving with gzip compression"""
        large_obj = {"data": np.random.randn(1000, 1000).tolist()}
        save_pickle(large_obj, self.test_file_compressed)
        
        assert os.path.exists(self.test_file_compressed)
        # Compressed file should be smaller
        import gzip
        with gzip.open(self.test_file_compressed, "rb") as f:
            loaded = pickle.load(f)
        assert loaded["data"] == large_obj["data"]

    def test_save_function(self):
        """Test saving function object"""
        def test_func(x):
            return x * 2
        
        save_pickle(test_func, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded(5) == 10

    def test_save_lambda(self):
        """Test saving lambda function"""
        # Note: lambdas can be tricky with pickle
        func = lambda x: x + 1
        save_pickle(func, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded(5) == 6

    def test_save_none(self):
        """Test saving None"""
        save_pickle(None, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded is None

    def test_save_bytes(self):
        """Test saving bytes object"""
        data = b"Hello, World!"
        save_pickle(data, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == data

    def test_save_set_and_frozenset(self):
        """Test saving set and frozenset"""
        s = {1, 2, 3, 4}
        fs = frozenset([5, 6, 7, 8])
        obj = {"set": s, "frozenset": fs}
        save_pickle(obj, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded["set"] == s
        assert loaded["frozenset"] == fs

    def test_save_with_protocol(self):
        """Test saving with specific pickle protocol"""
        obj = {"test": "data"}
        save_pickle(obj, self.test_file, protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == obj

    def test_save_large_object(self):
        """Test saving large object"""
        # Create a large list
        large_list = list(range(1000000))
        save_pickle(large_list, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded == large_list

    def test_save_recursive_structure(self):
        """Test saving recursive data structure"""
        # Create a self-referential structure
        lst = [1, 2, 3]
        lst.append(lst)  # Circular reference
        
        save_pickle(lst, self.test_file)
        
        with open(self.test_file, "rb") as f:
            loaded = pickle.load(f)
        assert loaded[0] == 1
        assert loaded[1] == 2
        assert loaded[2] == 3
        assert loaded[3] is loaded  # Check circular reference


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_pickle.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:21:07 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_pickle.py
# 
# import pickle
# import gzip
# 
# 
# def _save_pickle(obj, spath):
#     """
#     Save an object using Python's pickle serialization.
#     
#     Parameters
#     ----------
#     obj : Any
#         Object to serialize.
#     spath : str
#         Path where the pickle file will be saved.
#         
#     Returns
#     -------
#     None
#     """
#     with open(spath, "wb") as s:
#         pickle.dump(obj, s)
# 
# 
# def _save_pickle_gz(obj, spath):
#     """
#     Save an object using Python's pickle serialization with gzip compression.
#     
#     Parameters
#     ----------
#     obj : Any
#         Object to serialize.
#     spath : str
#         Path where the compressed pickle file will be saved.
#         
#     Returns
#     -------
#     None
#     """
#     with gzip.open(spath, "wb") as f:
#         pickle.dump(obj, f)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_pickle.py
# --------------------------------------------------------------------------------
