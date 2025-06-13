#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-10 17:52:00 (claude)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/io/test__save_comprehensive.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/test__save_comprehensive.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Comprehensive tests for scitex.io.save function covering all supported formats."""

import os
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import torch
import json
import pickle
import h5py
import scipy.io
import joblib
from pathlib import Path
from datetime import datetime
import warnings
import time


def test_save_matplotlib_figure_formats():
    """Test saving matplotlib figures in various formats."""
    import matplotlib.pyplot as plt
    from scitex.io import save
    
    # Create a simple figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title("Test Plot")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test various image formats
        formats = ['.png', '.pdf', '.svg', '.jpg', '.eps']
        for fmt in formats:
            save_path = os.path.join(tmpdir, f"figure{fmt}")
            save(fig, save_path, verbose=False)
            assert os.path.exists(save_path)
            assert os.path.getsize(save_path) > 0
    
    plt.close(fig)


def test_save_plotly_figure():
    """Test saving plotly figures."""
    try:
        import plotly.graph_objects as go
        from scitex.io import save
        
        # Create a simple plotly figure
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[1, 4, 9]))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test HTML save
            html_path = os.path.join(tmpdir, "plotly_fig.html")
            save(fig, html_path, verbose=False)
            assert os.path.exists(html_path)
            assert os.path.getsize(html_path) > 0
    except ImportError:
        pytest.skip("plotly not installed")


def test_save_hdf5_formats():
    """Test saving HDF5 files with different data types."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test numpy array
        arr_data = np.random.rand(10, 20, 30)
        save(arr_data, os.path.join(tmpdir, "array.h5"), verbose=False)
        
        # Test dict with multiple arrays
        dict_data = {
            'array1': np.random.rand(100),
            'array2': np.random.rand(50, 50),
            'metadata': {'version': 1.0}
        }
        save(dict_data, os.path.join(tmpdir, "dict.hdf5"), verbose=False)
        
        # Verify files exist
        assert os.path.exists(os.path.join(tmpdir, "array.h5"))
        assert os.path.exists(os.path.join(tmpdir, "dict.hdf5"))


def test_save_matlab_formats():
    """Test saving MATLAB .mat files with various data types."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test various MATLAB-compatible data
        data = {
            'scalar': 42.0,
            'vector': np.array([1, 2, 3, 4, 5]),
            'matrix': np.random.rand(10, 10),
            'string': 'test_string',
            'cell_like': [[1, 2], [3, 4, 5]]
        }
        
        mat_path = os.path.join(tmpdir, "data.mat")
        save(data, mat_path, verbose=False)
        
        assert os.path.exists(mat_path)
        
        # Verify it's readable by scipy
        loaded = scipy.io.loadmat(mat_path)
        assert 'scalar' in loaded
        assert 'vector' in loaded
        assert 'matrix' in loaded


def test_save_compressed_formats():
    """Test saving compressed file formats."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Large data for compression testing
        large_data = {
            'repeated': [42] * 10000,
            'random': np.random.rand(1000, 100).tolist()
        }
        
        # Test compressed pickle
        save(large_data, os.path.join(tmpdir, "data.pkl.gz"), verbose=False)
        
        # Test compressed numpy
        arr_data = np.random.rand(1000, 1000)
        save(arr_data, os.path.join(tmpdir, "array.npz"), verbose=False)
        
        # Verify compression worked
        gz_size = os.path.getsize(os.path.join(tmpdir, "data.pkl.gz"))
        save(large_data, os.path.join(tmpdir, "data.pkl"), verbose=False)
        pkl_size = os.path.getsize(os.path.join(tmpdir, "data.pkl"))
        
        assert gz_size < pkl_size  # Compressed should be smaller


def test_save_text_formats():
    """Test saving various text-based formats."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Plain text
        text_data = "Line 1\nLine 2\nLine 3"
        save(text_data, os.path.join(tmpdir, "text.txt"), verbose=False)
        
        # JSON
        json_data = {"key": "value", "list": [1, 2, 3]}
        save(json_data, os.path.join(tmpdir, "data.json"), verbose=False)
        
        # YAML
        yaml_data = {"config": {"param1": 1, "param2": "test"}}
        save(yaml_data, os.path.join(tmpdir, "config.yaml"), verbose=False)
        save(yaml_data, os.path.join(tmpdir, "config.yml"), verbose=False)
        
        # CSV from various inputs
        save([1, 2, 3], os.path.join(tmpdir, "list.csv"), verbose=False)
        save({"a": 1, "b": 2}, os.path.join(tmpdir, "dict.csv"), verbose=False)
        save(42, os.path.join(tmpdir, "scalar.csv"), verbose=False)
        
        # Verify all exist
        for fname in ["text.txt", "data.json", "config.yaml", "config.yml", 
                     "list.csv", "dict.csv", "scalar.csv"]:
            assert os.path.exists(os.path.join(tmpdir, fname))


def test_save_pandas_formats():
    """Test saving pandas DataFrames in various formats."""
    from scitex.io import save
    
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5],
        'D': pd.date_range('2023-01-01', periods=5)
    })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # CSV
        save(df, os.path.join(tmpdir, "data.csv"), verbose=False, index=False)
        
        # Excel (if available)
        try:
            save(df, os.path.join(tmpdir, "data.xlsx"), verbose=False)
        except:
            pass  # Excel writer might not be available
        
        # Pickle
        save(df, os.path.join(tmpdir, "data.pkl"), verbose=False)
        
        # Verify CSV at least
        loaded_df = pd.read_csv(os.path.join(tmpdir, "data.csv"))
        assert len(loaded_df) == len(df)


def test_save_torch_formats():
    """Test saving PyTorch tensors and models."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simple tensor
        tensor = torch.randn(10, 20, 30)
        save(tensor, os.path.join(tmpdir, "tensor.pt"), verbose=False)
        save(tensor, os.path.join(tmpdir, "tensor.pth"), verbose=False)
        
        # Model state dict
        model = torch.nn.Sequential(
            torch.nn.Linear(10, 20),
            torch.nn.ReLU(),
            torch.nn.Linear(20, 1)
        )
        save(model.state_dict(), os.path.join(tmpdir, "model.pth"), verbose=False)
        
        # Verify all saved
        assert os.path.exists(os.path.join(tmpdir, "tensor.pt"))
        assert os.path.exists(os.path.join(tmpdir, "tensor.pth"))
        assert os.path.exists(os.path.join(tmpdir, "model.pth"))


def test_save_image_formats():
    """Test saving image data in various formats."""
    from PIL import Image
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images
        rgb_img = Image.new('RGB', (100, 100), color='red')
        grayscale_img = Image.new('L', (100, 100), color=128)
        
        # Test different formats
        formats = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']
        for fmt in formats:
            save(rgb_img, os.path.join(tmpdir, f"rgb{fmt}"), verbose=False)
            save(grayscale_img, os.path.join(tmpdir, f"gray{fmt}"), verbose=False)
            
            assert os.path.exists(os.path.join(tmpdir, f"rgb{fmt}"))
            assert os.path.exists(os.path.join(tmpdir, f"gray{fmt}"))


def test_save_special_cases():
    """Test special cases and edge conditions."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty data structures
        save([], os.path.join(tmpdir, "empty_list.json"), verbose=False)
        save({}, os.path.join(tmpdir, "empty_dict.json"), verbose=False)
        save("", os.path.join(tmpdir, "empty_string.txt"), verbose=False)
        
        # Unicode and special characters
        unicode_data = {"text": "Hello 世界 🌍", "symbols": "α β γ δ"}
        save(unicode_data, os.path.join(tmpdir, "unicode.json"), verbose=False)
        
        # Very long filename
        long_name = "a" * 200 + ".txt"
        save("test", os.path.join(tmpdir, long_name), verbose=False)
        
        # Nested lists/dicts
        nested = {"a": {"b": {"c": {"d": [1, 2, 3]}}}}
        save(nested, os.path.join(tmpdir, "nested.json"), verbose=False)
        
        # All should succeed
        assert os.path.exists(os.path.join(tmpdir, "empty_list.json"))
        assert os.path.exists(os.path.join(tmpdir, "unicode.json"))


def test_save_with_options():
    """Test save function with various options."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        data = {"test": "data"}
        
        # Test dry run
        dry_path = os.path.join(tmpdir, "dry_run.json")
        save(data, dry_path, dry_run=True, verbose=False)
        assert not os.path.exists(dry_path)  # Should not create file
        
        # Test with custom timestamp
        ts_path = os.path.join(tmpdir, "with_timestamp.json")
        save(data, ts_path, verbose=False)
        assert os.path.exists(ts_path)
        
        # Test makedirs=False with existing dir
        existing_path = os.path.join(tmpdir, "existing.json")
        save(data, existing_path, makedirs=False, verbose=False)
        assert os.path.exists(existing_path)


def test_save_error_conditions():
    """Test error handling in save function."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Unsupported extension
        with pytest.raises(ValueError, match="Unsupported file format"):
            save({"data": 1}, os.path.join(tmpdir, "file.xyz"), verbose=False)
        
        # No extension
        with pytest.raises(ValueError, match="Unsupported file format"):
            save({"data": 1}, os.path.join(tmpdir, "noext"), verbose=False)
        
        # Invalid data for format (e.g., non-serializable to JSON)
        class CustomObject:
            pass
        
        with pytest.raises(TypeError):
            save(CustomObject(), os.path.join(tmpdir, "custom.json"), verbose=False)


def test_save_performance():
    """Test save performance with large files."""
    from scitex.io import save
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create large array (100MB+)
        large_array = np.random.rand(5000, 5000)  # ~200MB
        
        # Time the save operation
        start_time = time.time()
        save(large_array, os.path.join(tmpdir, "large.npy"), verbose=False)
        save_time = time.time() - start_time
        
        # Should complete in reasonable time (< 10 seconds)
        assert save_time < 10.0
        
        # File should exist and be large
        file_size = os.path.getsize(os.path.join(tmpdir, "large.npy"))
        assert file_size > 100 * 1024 * 1024  # > 100MB


def test_save_concurrent_access():
    """Test save behavior with concurrent access."""
    from scitex.io import save
    import threading
    
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "concurrent.json")
        
        def save_data(thread_id):
            data = {"thread": thread_id, "timestamp": time.time()}
            save(data, save_path, verbose=False)
        
        # Create multiple threads trying to save to same file
        threads = []
        for i in range(5):
            t = threading.Thread(target=save_data, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # File should exist (last write wins)
        assert os.path.exists(save_path)


def test_save_path_handling():
    """Test various path handling scenarios."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Relative path
        os.chdir(tmpdir)
        save({"test": 1}, "relative.json", verbose=False)
        assert os.path.exists("relative.json")
        
        # Path with ~
        home_path = os.path.expanduser("~/test_save_temp.json")
        try:
            save({"test": 1}, "~/test_save_temp.json", verbose=False)
            assert os.path.exists(home_path)
        finally:
            if os.path.exists(home_path):
                os.remove(home_path)
        
        # Path object
        path_obj = Path(tmpdir) / "pathlib.json"
        save({"test": 1}, path_obj, verbose=False)
        assert path_obj.exists()


if __name__ == "__main__":
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])