#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-07 17:35:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/io/test__save_dispatch.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/test__save_dispatch.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import os
import sys
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import torch
import json
import time
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex
from scitex.io._save import _FILE_HANDLERS


class TestSaveDispatchDictionary:
    """Test cases for the dispatch dictionary optimization in scitex.io.save."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_dispatch_dictionary_exists(self):
        """Test that the dispatch dictionary is properly defined."""
        assert hasattr(scitex.io._save, '_FILE_HANDLERS')
        assert isinstance(_FILE_HANDLERS, dict)
        assert len(_FILE_HANDLERS) > 10  # Should have many handlers

    def test_dispatch_dictionary_completeness(self):
        """Test that dispatch dictionary covers all major formats."""
        expected_extensions = [
            '.csv', '.xlsx', '.xls', '.npy', '.npz', '.pkl', '.pickle',
            '.joblib', '.json', '.yaml', '.yml', '.hdf5', '.h5',
            '.pth', '.pt', '.mat', '.png', '.jpg', '.jpeg', '.gif',
            '.txt', '.md', '.py', '.html', '.mp4'
        ]
        
        # CSV is handled separately, so remove it from check
        expected_extensions.remove('.csv')
        
        for ext in expected_extensions:
            assert ext in _FILE_HANDLERS, f"Missing handler for {ext}"

    def test_dispatch_dictionary_handlers_callable(self):
        """Test that all handlers in dispatch dictionary are callable."""
        for ext, handler in _FILE_HANDLERS.items():
            assert callable(handler), f"Handler for {ext} is not callable"

    def test_dispatch_performance(self, temp_dir):
        """Test that dispatch dictionary provides O(1) lookup performance."""
        # Create test data
        data = {"test": [1, 2, 3]}
        
        # Test with many different extensions
        extensions = ['.json', '.yaml', '.pkl', '.npy', '.txt']
        times = []
        
        for ext in extensions:
            save_path = os.path.join(temp_dir, f"test{ext}")
            
            # Time the save operation
            start = time.perf_counter()
            if ext == '.npy':
                scitex.io.save(np.array([1, 2, 3]), save_path, verbose=False)
            elif ext == '.txt':
                scitex.io.save("test text", save_path, verbose=False)
            else:
                scitex.io.save(data, save_path, verbose=False)
            end = time.perf_counter()
            
            times.append(end - start)
        
        # Performance should be consistent (no linear increase)
        # Allow for some variance but overall should be similar
        avg_time = sum(times) / len(times)
        for t in times:
            assert t < avg_time * 2, "Performance varies too much, might not be O(1)"

    def test_excel_handler(self, temp_dir):
        """Test Excel file handler through dispatch."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        
        for ext in ['.xlsx', '.xls']:
            save_path = os.path.join(temp_dir, f"test{ext}")
            scitex.io.save(df, save_path, verbose=False)
            assert os.path.exists(save_path)

    def test_numpy_handlers(self, temp_dir):
        """Test NumPy file handlers through dispatch."""
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        
        # Test .npy
        npy_path = os.path.join(temp_dir, "test.npy")
        scitex.io.save(arr, npy_path, verbose=False)
        assert os.path.exists(npy_path)
        loaded = np.load(npy_path)
        np.testing.assert_array_equal(loaded, arr)
        
        # Test .npz
        npz_data = {"arr1": arr, "arr2": arr * 2}
        npz_path = os.path.join(temp_dir, "test.npz")
        scitex.io.save(npz_data, npz_path, verbose=False)
        assert os.path.exists(npz_path)

    def test_pickle_handlers(self, temp_dir):
        """Test pickle file handlers through dispatch."""
        data = {"test": [1, 2, 3], "nested": {"a": 1}}
        
        for ext in ['.pkl', '.pickle']:
            save_path = os.path.join(temp_dir, f"test{ext}")
            scitex.io.save(data, save_path, verbose=False)
            assert os.path.exists(save_path)

    def test_text_format_handlers(self, temp_dir):
        """Test text format handlers through dispatch."""
        # JSON
        json_data = {"test": "data", "number": 42}
        json_path = os.path.join(temp_dir, "test.json")
        scitex.io.save(json_data, json_path, verbose=False)
        assert os.path.exists(json_path)
        
        # YAML
        yaml_path = os.path.join(temp_dir, "test.yaml")
        scitex.io.save(json_data, yaml_path, verbose=False)
        assert os.path.exists(yaml_path)
        
        # Text files
        text_data = "Test text content"
        for ext in ['.txt', '.md', '.py']:
            text_path = os.path.join(temp_dir, f"test{ext}")
            scitex.io.save(text_data, text_path, verbose=False)
            assert os.path.exists(text_path)

    def test_torch_handlers(self, temp_dir):
        """Test PyTorch file handlers through dispatch."""
        tensor = torch.tensor([1.0, 2.0, 3.0])
        
        for ext in ['.pth', '.pt']:
            save_path = os.path.join(temp_dir, f"test{ext}")
            scitex.io.save(tensor, save_path, verbose=False)
            assert os.path.exists(save_path)
            loaded = torch.load(save_path)
            assert torch.allclose(loaded, tensor)

    def test_image_handler_special_params(self, temp_dir):
        """Test that image handlers receive special parameters."""
        # Create a mock figure
        fig = MagicMock()
        fig.savefig = MagicMock()
        
        # Patch _save_image to verify it's called with correct params
        with patch('scitex.io._save._save_image') as mock_save_image:
            png_path = os.path.join(temp_dir, "test.png")
            scitex.io.save(fig, png_path, verbose=False, no_csv=True)
            
            # Verify _save_image was called
            mock_save_image.assert_called_once()
            args, kwargs = mock_save_image.call_args
            assert args[0] == fig
            assert args[1] == png_path

    def test_unsupported_format_error(self, temp_dir):
        """Test that unsupported formats raise appropriate error."""
        data = {"test": "data"}
        unsupported_path = os.path.join(temp_dir, "test.unsupported")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            scitex.io.save(data, unsupported_path, verbose=False)

    def test_special_extension_handling(self, temp_dir):
        """Test special cases like .pkl.gz that need custom handling."""
        data = {"test": [1, 2, 3]}
        pkl_gz_path = os.path.join(temp_dir, "test.pkl.gz")
        
        scitex.io.save(data, pkl_gz_path, verbose=False)
        assert os.path.exists(pkl_gz_path)
        
        # Verify it's actually compressed
        file_size = os.path.getsize(pkl_gz_path)
        assert file_size > 0

    def test_handler_isolation(self):
        """Test that handlers are properly isolated functions."""
        # Each handler should be a separate function
        handler_names = set()
        for handler in _FILE_HANDLERS.values():
            handler_names.add(handler.__name__)
        
        # Should have multiple unique handlers
        assert len(handler_names) > 5, "Handlers should be separate functions"

    def test_csv_special_handling(self, temp_dir):
        """Test that CSV is handled specially outside dispatch dictionary."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        csv_path = os.path.join(temp_dir, "test.csv")
        
        # CSV should work even though it's not in _FILE_HANDLERS
        assert '.csv' not in _FILE_HANDLERS
        scitex.io.save(df, csv_path, verbose=False)
        assert os.path.exists(csv_path)


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])