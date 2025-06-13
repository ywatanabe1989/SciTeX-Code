#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:48:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__joblib.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__joblib.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for joblib saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from scitex.io._save_modules import save_joblib


@pytest.mark.skipif(not JOBLIB_AVAILABLE, reason="joblib not installed")
class TestSaveJoblib:
    """Test suite for save_joblib function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.joblib")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_object(self):
        """Test saving simple Python objects"""
        obj = {"a": 1, "b": [2, 3, 4], "c": "hello"}
        save_joblib(obj, self.test_file)
        
        assert os.path.exists(self.test_file)
        loaded = joblib.load(self.test_file)
        assert loaded == obj

    def test_save_numpy_array(self):
        """Test saving numpy array - joblib is efficient for this"""
        arr = np.random.randn(100, 200)
        save_joblib(arr, self.test_file)
        
        loaded = joblib.load(self.test_file)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_large_numpy_array(self):
        """Test saving large numpy array - joblib excels at this"""
        arr = np.random.randn(1000, 1000)
        save_joblib(arr, self.test_file)
        
        loaded = joblib.load(self.test_file)
        np.testing.assert_array_equal(arr, loaded)

    def test_save_pandas_dataframe(self):
        """Test saving pandas DataFrame"""
        df = pd.DataFrame({
            "a": np.random.randn(1000),
            "b": np.random.randn(1000),
            "c": ["category_" + str(i % 10) for i in range(1000)]
        })
        save_joblib(df, self.test_file)
        
        loaded = joblib.load(self.test_file)
        pd.testing.assert_frame_equal(df, loaded)

    def test_save_sklearn_model(self):
        """Test saving scikit-learn model (joblib's primary use case)"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.datasets import make_classification
            
            X, y = make_classification(n_samples=100, n_features=20)
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            model.fit(X, y)
            
            save_joblib(model, self.test_file)
            
            loaded_model = joblib.load(self.test_file)
            # Test that predictions are the same
            np.testing.assert_array_equal(
                model.predict(X), 
                loaded_model.predict(X)
            )
        except ImportError:
            pytest.skip("scikit-learn not installed")

    def test_save_with_compression(self):
        """Test saving with different compression levels"""
        large_arr = np.random.randn(500, 500)
        
        # Test different compression levels
        for compress in [0, 3, 9]:
            file_path = os.path.join(self.temp_dir, f"test_compress_{compress}.joblib")
            save_joblib(large_arr, file_path, compress=compress)
            
            loaded = joblib.load(file_path)
            np.testing.assert_array_equal(large_arr, loaded)

    def test_save_mixed_object_types(self):
        """Test saving object with mixed types"""
        obj = {
            "arrays": [np.array([1, 2, 3]), np.array([[4, 5], [6, 7]])],
            "dataframe": pd.DataFrame({"x": [1, 2, 3]}),
            "numbers": [1, 2.5, 3.14159],
            "strings": ["hello", "world"],
            "nested": {"a": {"b": {"c": 42}}}
        }
        save_joblib(obj, self.test_file)
        
        loaded = joblib.load(self.test_file)
        
        # Check arrays
        for i, arr in enumerate(obj["arrays"]):
            np.testing.assert_array_equal(arr, loaded["arrays"][i])
        
        # Check dataframe
        pd.testing.assert_frame_equal(obj["dataframe"], loaded["dataframe"])
        
        # Check other fields
        assert loaded["numbers"] == obj["numbers"]
        assert loaded["strings"] == obj["strings"]
        assert loaded["nested"] == obj["nested"]

    def test_save_sparse_matrix(self):
        """Test saving sparse matrix"""
        try:
            from scipy.sparse import csr_matrix
            
            # Create sparse matrix
            data = np.array([1, 2, 3, 4, 5, 6])
            indices = np.array([0, 2, 2, 0, 1, 2])
            indptr = np.array([0, 2, 3, 6])
            sparse = csr_matrix((data, indices, indptr), shape=(3, 3))
            
            save_joblib(sparse, self.test_file)
            
            loaded = joblib.load(self.test_file)
            np.testing.assert_array_equal(sparse.toarray(), loaded.toarray())
        except ImportError:
            pytest.skip("scipy not installed")

    def test_save_custom_class(self):
        """Test saving custom class instance"""
        class CustomModel:
            def __init__(self, param1, param2):
                self.param1 = param1
                self.param2 = param2
                self.data = np.random.randn(10, 10)
            
            def process(self, x):
                return x * self.param1 + self.param2
        
        model = CustomModel(2.0, 3.0)
        save_joblib(model, self.test_file)
        
        loaded = joblib.load(self.test_file)
        assert loaded.param1 == 2.0
        assert loaded.param2 == 3.0
        assert loaded.process(5) == 13.0

    def test_save_function_with_closure(self):
        """Test saving function with closure"""
        def make_multiplier(n):
            def multiplier(x):
                return x * n
            return multiplier
        
        func = make_multiplier(5)
        save_joblib(func, self.test_file)
        
        loaded = joblib.load(self.test_file)
        assert loaded(10) == 50

    def test_save_with_mmap_mode(self):
        """Test saving large array with memory mapping"""
        large_arr = np.random.randn(1000, 1000)
        save_joblib(large_arr, self.test_file)
        
        # Load with memory mapping
        loaded = joblib.load(self.test_file, mmap_mode='r')
        np.testing.assert_array_almost_equal(large_arr, loaded)

    def test_save_none_and_empty_containers(self):
        """Test saving None and empty containers"""
        obj = {
            "none": None,
            "empty_list": [],
            "empty_dict": {},
            "empty_array": np.array([])
        }
        save_joblib(obj, self.test_file)
        
        loaded = joblib.load(self.test_file)
        assert loaded["none"] is None
        assert loaded["empty_list"] == []
        assert loaded["empty_dict"] == {}
        assert loaded["empty_array"].size == 0

    def test_save_with_protocol(self):
        """Test saving with specific pickle protocol"""
        obj = {"test": "data"}
        import pickle
        save_joblib(obj, self.test_file, protocol=pickle.HIGHEST_PROTOCOL)
        
        loaded = joblib.load(self.test_file)
        assert loaded == obj

    def test_parallel_object_saving(self):
        """Test saving objects that could be used in parallel processing"""
        # joblib is often used for saving objects in parallel workflows
        objects = [
            {"id": i, "data": np.random.randn(100)} 
            for i in range(10)
        ]
        save_joblib(objects, self.test_file)
        
        loaded = joblib.load(self.test_file)
        assert len(loaded) == 10
        for i, obj in enumerate(loaded):
            assert obj["id"] == i


# EOF
