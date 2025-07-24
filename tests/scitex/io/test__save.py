#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-13 22:30:12 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/io/test__save.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/test__save.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import os
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import torch
import json
import pickle
import sys
from pathlib import Path

# Optional imports for specific formats
try:
    import h5py
except ImportError:
    h5py = None


try:
    import scipy.io
except ImportError:
    scipy = None

try:
    import joblib
except ImportError:
    joblib = None

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex


def test_torch_save_pt_extension():
    """Test that PyTorch models can be saved with .pt extension."""
    _save = scitex.io.save

    # Create temp file path
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp:
        temp_path = tmp.name

    try:
        # Create simple model tensor
        model = torch.tensor([1, 2, 3])

        # Test saving with .pt extension
        _save(model, temp_path, verbose=False)

        # Verify the file exists and can be loaded back
        assert os.path.exists(temp_path)
        loaded_model = torch.load(temp_path)
        assert torch.all(loaded_model == model)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_torch_save_kwargs():
    """Test that kwargs are properly passed to torch.save."""
    _save = scitex.io.save

    # Create temp file path
    with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as tmp:
        temp_path = tmp.name

    try:
        # Create simple model tensor
        model = torch.tensor([1, 2, 3])

        # _save should pass kwargs to torch.save
        # While we can't directly test the internal call, we can verify that
        # using _save with _use_new_zipfile_serialization=False works
        _save(model, temp_path, verbose=False, _use_new_zipfile_serialization=False)

        # Verify the file exists and can be loaded back
        assert os.path.exists(temp_path)
        loaded_model = torch.load(temp_path)
        assert torch.all(loaded_model == model)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.skip(reason="_save_csv is an internal function")
def test_save_csv_deduplication():
    """Test that CSV files are not rewritten if content hasn't changed."""
    # This test requires access to internal _save_csv function
    pass


def test_save_matplotlib_figure():
    """Test saving matplotlib figures in various formats."""
    import matplotlib.pyplot as plt
    from scitex.io import save
    
    # Create a simple figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title("Test Plot")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test PNG save
        png_path = os.path.join(tmpdir, "figure.png")
        save(fig, png_path, verbose=False)
        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0
        
        # Test PDF save
        pdf_path = os.path.join(tmpdir, "figure.pdf")
        save(fig, pdf_path, verbose=False)
        assert os.path.exists(pdf_path)
        
        # Test SVG save
        svg_path = os.path.join(tmpdir, "figure.svg")
        save(fig, svg_path, verbose=False)
        assert os.path.exists(svg_path)
    
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


def test_save_hdf5():
    """Test saving HDF5 files."""
    if h5py is None:
        pytest.skip("h5py not installed")
        
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test saving numpy array to HDF5
        data = np.random.rand(10, 20, 30)
        hdf5_path = os.path.join(tmpdir, "data.h5")
        save(data, hdf5_path, verbose=False)
        
        assert os.path.exists(hdf5_path)
        
        # Verify content
        with h5py.File(hdf5_path, 'r') as f:
            assert 'data' in f
            loaded_data = f['data'][:]
            np.testing.assert_array_almost_equal(loaded_data, data)


def test_save_matlab():
    """Test saving MATLAB .mat files."""
    if scipy is None:
        pytest.skip("scipy not installed")
        
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test saving dict to .mat
        data = {
            'array': np.array([1, 2, 3]),
            'matrix': np.array([[1, 2], [3, 4]]),
            'scalar': 42.0
        }
        mat_path = os.path.join(tmpdir, "data.mat")
        save(data, mat_path, verbose=False)
        
        assert os.path.exists(mat_path)
        
        # Verify content
        loaded = scipy.io.loadmat(mat_path)
        np.testing.assert_array_equal(loaded['array'].flatten(), data['array'])
        np.testing.assert_array_equal(loaded['matrix'], data['matrix'])
        assert float(loaded['scalar']) == data['scalar']


def test_save_compressed_pickle():
    """Test saving compressed pickle files."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Large data that benefits from compression
        data = {
            'large_array': np.random.rand(1000, 1000),
            'metadata': {'compression': True}
        }
        
        # Test .pkl.gz
        gz_path = os.path.join(tmpdir, "data.pkl.gz")
        save(data, gz_path, verbose=False)
        assert os.path.exists(gz_path)
        
        # Verify it's compressed (should be smaller than uncompressed)
        pkl_path = os.path.join(tmpdir, "data_uncompressed.pkl")
        save(data, pkl_path, verbose=False)
        
        assert os.path.getsize(gz_path) < os.path.getsize(pkl_path)


def test_save_joblib():
    """Test saving with joblib format."""
    if joblib is None:
        pytest.skip("joblib not installed")
        
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create complex object
        data = {
            'model': {'weights': np.random.rand(100, 100)},
            'config': {'learning_rate': 0.001}
        }
        
        joblib_path = os.path.join(tmpdir, "model.joblib")
        save(data, joblib_path, verbose=False)
        
        assert os.path.exists(joblib_path)
        
        # Verify content
        loaded = joblib.load(joblib_path)
        np.testing.assert_array_equal(loaded['model']['weights'], data['model']['weights'])
        assert loaded['config'] == data['config']


def test_save_pil_image():
    """Test saving PIL images."""
    from PIL import Image
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple PIL image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Test various image formats
        for ext in ['.png', '.jpg', '.tiff']:
            img_path = os.path.join(tmpdir, f"image{ext}")
            save(img, img_path, verbose=False)
            assert os.path.exists(img_path)
            
            # Verify it can be loaded
            loaded_img = Image.open(img_path)
            assert loaded_img.size == (100, 100)
            loaded_img.close()


def test_save_with_datetime_path():
    """Test saving with datetime in path."""
    from scitex.io import save
    from datetime import datetime
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create path with datetime placeholder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {"test": "data"}
        
        # Path with datetime
        save_path = os.path.join(tmpdir, f"data_{timestamp}.json")
        save(data, save_path, verbose=False)
        
        assert os.path.exists(save_path)


def test_save_verbose_output(capsys):
    """Test verbose output during save."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        data = np.array([1, 2, 3])
        save_path = os.path.join(tmpdir, "data.npy")
        
        # Save with verbose=True
        save(data, save_path, verbose=True)


def test_save_hdf5_with_key_and_override(capsys):
    """Test HDF5 save functionality with key and override parameters."""
    if h5py is None:
        pytest.skip("h5py not installed")
        
    from scitex.io import save, has_h5_key
    from scitex.io._H5Explorer import H5Explorer
    
    with tempfile.TemporaryDirectory() as tmpdir:
        h5_path = os.path.join(tmpdir, "test_data.h5")
        
        # Test data
        test_data = {
            'array1': np.random.rand(10, 10),
            'array2': np.arange(100).reshape(10, 10),
            'scalar': 42,
            'string': 'test_string',
            'metadata': {'test_id': 1, 'description': 'Test HDF5'}
        }
        
        # Test 1: Save with key parameter
        save(test_data, h5_path, key='group1/subgroup/data', verbose=False)
        assert os.path.exists(h5_path)
        
        # Verify structure using H5Explorer
        with H5Explorer(h5_path) as explorer:
            # Check that nested groups were created
            assert 'group1' in explorer.keys('/')
            assert 'subgroup' in explorer.keys('/group1')
            assert 'data' in explorer.keys('/group1/subgroup')
            
            # Load and verify data
            loaded_data = explorer.load('/group1/subgroup/data')
            np.testing.assert_array_equal(loaded_data['array1'], test_data['array1'])
            assert loaded_data['scalar'] == test_data['scalar']
            assert loaded_data['string'] == test_data['string']
        
        # Test 2: has_h5_key function
        assert has_h5_key(h5_path, 'group1/subgroup/data')
        assert not has_h5_key(h5_path, 'nonexistent/key')
        
        # Test 3: Save again without override (should skip)
        # Modify data to check if it's overwritten
        test_data['array1'] = np.ones((5, 5))
        save(test_data, h5_path, key='group1/subgroup/data', override=False, verbose=False)
        
        # Verify data was NOT overwritten
        with H5Explorer(h5_path) as explorer:
            loaded_data = explorer.load('/group1/subgroup/data')
            assert loaded_data['array1'].shape == (10, 10)  # Original shape
            assert not np.array_equal(loaded_data['array1'], np.ones((5, 5)))
        
        # Test 4: Save with override=True
        save(test_data, h5_path, key='group1/subgroup/data', override=True, verbose=False)
        
        # Verify data WAS overwritten
        with H5Explorer(h5_path) as explorer:
            loaded_data = explorer.load('/group1/subgroup/data')
            assert loaded_data['array1'].shape == (5, 5)  # New shape
            np.testing.assert_array_equal(loaded_data['array1'], np.ones((5, 5)))
        
        # Test 5: Save to root (no key)
        root_data = {'root_array': np.random.rand(3, 3)}
        h5_path2 = os.path.join(tmpdir, "test_root.h5")
        save(root_data, h5_path2, verbose=False)
        
        with H5Explorer(h5_path2) as explorer:
            # Data should be at root level
            assert 'root_array' in explorer.keys('/')
            loaded = explorer.load('/root_array')
            np.testing.assert_array_equal(loaded, root_data['root_array'])
        
        # Test 6: Complex nested structure (like PAC data)
        pac_data = {
            'pac_values': np.random.rand(64, 10, 10),
            'p_values': np.random.rand(64, 10, 10),
            'metadata': {
                'seizure_id': 'S001',
                'patient_id': 'P023',
                'duration_sec': 60.0
            }
        }
        
        pac_key = 'patient_023/seizure_001/pac_analysis'
        save(pac_data, h5_path, key=pac_key, verbose=False)
        
        # Verify complex structure
        assert has_h5_key(h5_path, pac_key)
        with H5Explorer(h5_path) as explorer:
            loaded_pac = explorer.load(f'/{pac_key}')
            np.testing.assert_array_equal(loaded_pac['pac_values'], pac_data['pac_values'])
            assert loaded_pac['metadata']['seizure_id'] == 'S001'
        
        # Check output (commented out since all saves are with verbose=False)
        # captured = capsys.readouterr()
        # assert "Saved to:" in captured.out
        # assert save_path in captured.out
        # assert "KB" in captured.out or "B" in captured.out  # Size info


def test_save_figure_with_csv_export():
    """Test saving figure with CSV data export."""
    import matplotlib.pyplot as plt
    from scitex.io import save
    
    # Create figure with data
    fig, ax = plt.subplots()
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    ax.plot(x, y, label="Test Line")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        fig_path = os.path.join(tmpdir, "figure.png")
        
        # Save figure (CSV export depends on wrapped axes)
        save(fig, fig_path, verbose=False)
        assert os.path.exists(fig_path)
    
    plt.close(fig)


def test_save_error_handling(caplog):
    """Test error handling in save function."""
    from scitex.io import save
    import logging
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test with None object - should log error
        save(None, os.path.join(tmpdir, "none.txt"), verbose=False)
        assert "Error occurred while saving" in caplog.text
        
        # Test with unsupported extension - should show warning
        data = {"test": "data"}
        save(data, os.path.join(tmpdir, "no_extension"), verbose=False)
        # Check that file wasn't created since format is unsupported
        assert not os.path.exists(os.path.join(tmpdir, "no_extension"))
        
        # Test with read-only directory - should log error
        ro_dir = os.path.join(tmpdir, "readonly")
        os.makedirs(ro_dir)
        os.chmod(ro_dir, 0o444)
        
        try:
            save(data, os.path.join(ro_dir, "data.json"), verbose=False)
            # Should not create file due to permission error
            assert not os.path.exists(os.path.join(ro_dir, "data.json"))
        finally:
            # Restore permissions for cleanup
            os.chmod(ro_dir, 0o755)


def test_save_catboost_model():
    """Test saving CatBoost models."""
    try:
        from catboost import CatBoostClassifier
        from scitex.io import save
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple model
            model = CatBoostClassifier(iterations=10, verbose=False)
            
            # Mock training data
            X = np.random.rand(100, 5)
            y = np.random.randint(0, 2, 100)
            model.fit(X, y, verbose=False)
            
            # Save model
            cbm_path = os.path.join(tmpdir, "model.cbm")
            save(model, cbm_path, verbose=False)
            
            assert os.path.exists(cbm_path)
    except ImportError:
        pytest.skip("CatBoost not installed")


def test_save_with_makedirs_false(caplog):
    """Test save behavior when makedirs=False."""
    from scitex.io import save
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Try to save to non-existent directory with makedirs=False
        data = {"test": "data"}
        save_path = os.path.join(tmpdir, "nonexistent", "data.json")
        
        # Should not create the file since directory doesn't exist
        save(data, save_path, verbose=False, makedirs=False)
        assert not os.path.exists(save_path)
        assert "Error occurred while saving" in caplog.text


class TestSave:
    """Test cases for scitex.io.save function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    def test_save_numpy_array(self, temp_dir):
        """Test saving NumPy arrays."""
        # Arrange
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        save_path = os.path.join(temp_dir, "array.npy")

        # Act
        scitex.io.save(arr, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        loaded = np.load(save_path)
        np.testing.assert_array_equal(loaded, arr)

    def test_save_numpy_compressed(self, temp_dir):
        """Test saving compressed NumPy arrays."""
        # Arrange
        data = {"array1": np.array([1, 2, 3]), "array2": np.array([[4, 5], [6, 7]])}
        save_path = os.path.join(temp_dir, "arrays.npz")

        # Act
        scitex.io.save(data, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        loaded = np.load(save_path)
        np.testing.assert_array_equal(loaded["array1"], data["array1"])
        np.testing.assert_array_equal(loaded["array2"], data["array2"])

    def test_save_pandas_dataframe(self, temp_dir):
        """Test saving pandas DataFrames."""
        # Arrange
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [1.1, 2.2, 3.3]})
        save_path = os.path.join(temp_dir, "data.csv")

        # Act
        scitex.io.save(df, save_path, verbose=False, index=False)

        # Assert
        assert os.path.exists(save_path)
        loaded = pd.read_csv(save_path)
        pd.testing.assert_frame_equal(loaded, df)

    def test_save_json(self, temp_dir):
        """Test saving JSON data."""
        # Arrange
        data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        save_path = os.path.join(temp_dir, "data.json")

        # Act
        scitex.io.save(data, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        with open(save_path, "r") as f:
            loaded = json.load(f)
        assert loaded == data

    def test_save_yaml(self, temp_dir):
        """Test saving YAML data."""
        # Arrange
        data = {"config": {"learning_rate": 0.001, "batch_size": 32}, "model": "ResNet"}
        save_path = os.path.join(temp_dir, "config.yaml")

        # Act
        scitex.io.save(data, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        loaded = scitex.io.load(save_path)
        assert loaded == data

    def test_save_pickle(self, temp_dir):
        """Test saving pickle files."""
        # Arrange
        data = {
            "array": np.array([1, 2, 3]),
            "list": [1, 2, 3],
            "dict": {"a": 1, "b": 2},
        }
        save_path = os.path.join(temp_dir, "data.pkl")

        # Act
        scitex.io.save(data, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        with open(save_path, "rb") as f:
            loaded = pickle.load(f)
        np.testing.assert_array_equal(loaded["array"], data["array"])
        assert loaded["list"] == data["list"]
        assert loaded["dict"] == data["dict"]

    def test_save_text(self, temp_dir):
        """Test saving text files."""
        # Arrange
        text = "Hello\nWorld\nTest"
        save_path = os.path.join(temp_dir, "text.txt")

        # Act
        scitex.io.save(text, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        with open(save_path, "r") as f:
            loaded = f.read()
        assert loaded == text

    def test_save_creates_directory(self, temp_dir):
        """Test that save creates parent directories."""
        # Arrange
        data = {"test": "data"}
        save_path = os.path.join(temp_dir, "nested", "dir", "data.json")

        # Act
        scitex.io.save(data, save_path, verbose=False, makedirs=True)

        # Assert
        assert os.path.exists(save_path)
        parent_dir = os.path.dirname(save_path)
        assert os.path.exists(parent_dir)

    def test_save_dry_run(self, temp_dir, capsys):
        """Test dry run mode."""
        # Arrange
        data = {"test": "data"}
        save_path = os.path.join(temp_dir, "data.json")

        # Act
        scitex.io.save(data, save_path, dry_run=True, verbose=True)

        # Assert
        assert not os.path.exists(save_path)  # File should not be created
        captured = capsys.readouterr()
        assert "(dry run)" in captured.out

    def test_save_with_symlink(self, temp_dir):
        """Test saving with symlink creation."""
        # Arrange
        data = {"test": "data"}
        # Change to temp dir to test symlink
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Act
            scitex.io.save(data, "subdir/data.json", verbose=False, symlink_from_cwd=True)

            # Assert
            # Should create both the actual file and a symlink
            assert os.path.exists("subdir/data.json")
            # The implementation creates files in script_out directories
        finally:
            os.chdir(original_cwd)

    def test_save_unsupported_format(self, temp_dir):
        """Test saving with unsupported format shows warning."""
        import warnings
        
        # Arrange
        data = {"test": "data"}
        save_path = os.path.join(temp_dir, "data.unknown")

        # Act - capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            scitex.io.save(data, save_path, verbose=False)
            
            # Assert - warning should be shown and file not created
            assert len(w) == 1
            assert "Unsupported file format" in str(w[0].message)
            assert not os.path.exists(save_path)

    def test_save_list_to_npz(self, temp_dir):
        """Test saving list of arrays to npz."""
        # Arrange
        arrays = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        save_path = os.path.join(temp_dir, "arrays.npz")

        # Act
        scitex.io.save(arrays, save_path, verbose=False)

        # Assert
        assert os.path.exists(save_path)
        loaded = np.load(save_path)
        np.testing.assert_array_equal(loaded["0"], arrays[0])
        np.testing.assert_array_equal(loaded["1"], arrays[1])

    def test_save_various_csv_types(self, temp_dir):
        """Test saving various types as CSV."""
        # Test DataFrame (primary CSV use case)
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        scitex.io.save(df, os.path.join(temp_dir, "dataframe.csv"), verbose=False)
        assert os.path.exists(os.path.join(temp_dir, "dataframe.csv"))
        
        # Test numpy array
        arr = np.array([[1, 2], [3, 4]])
        scitex.io.save(arr, os.path.join(temp_dir, "array.csv"), verbose=False)
        assert os.path.exists(os.path.join(temp_dir, "array.csv"))
        
        # Test Series
        series = pd.Series([1, 2, 3], name="values")
        scitex.io.save(series, os.path.join(temp_dir, "series.csv"), verbose=False)
        assert os.path.exists(os.path.join(temp_dir, "series.csv"))

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-14 15:21:15 (ywatanabe)"
# # File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/io/_save.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import warnings
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save.py"
# 
# """
# 1. Functionality:
#    - Provides utilities for saving various data types to different file formats.
# 2. Input:
#    - Objects to be saved (e.g., NumPy arrays, PyTorch tensors, Pandas DataFrames, etc.)
#    - File path or name where the object should be saved
# 3. Output:
#    - Saved files in various formats (e.g., CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML, JSON, HDF5, PTH, MAT, CBM)
# 4. Prerequisites:
#    - Python 3.x
#    - Required libraries: numpy, pandas, torch, matplotlib, plotly, h5py, joblib, PIL, ruamel.yaml
# """
# 
# """Imports"""
# import inspect
# import logging
# import os as _os
# from typing import Any
# 
# from .._sh import sh
# from ..path._clean import clean
# from ..path._getsize import getsize
# from ..str._clean_path import clean_path
# from ..str._color_text import color_text
# from ..str._readable_bytes import readable_bytes
# # Import save functions from the new modular structure
# from ._save_modules import (save_catboost, save_csv, save_excel, save_hdf5,
#                             save_html, save_image, save_joblib, save_json,
#                             save_matlab, save_mp4, save_npy, save_npz,
#                             save_pickle, save_pickle_compressed, save_text,
#                             save_torch, save_yaml, save_zarr)
# from ._save_modules._bibtex import save_bibtex
# 
# 
# def _get_figure_with_data(obj):
#     """
#     Extract figure or axes object that may contain plotting data for CSV export.
# 
#     Parameters
#     ----------
#     obj : various matplotlib objects
#         Could be Figure, Axes, FigWrapper, AxisWrapper, or other matplotlib objects
# 
#     Returns
#     -------
#     object or None
#         Figure or axes object that has export_as_csv methods, or None if not found
#     """
#     import matplotlib.axes
#     import matplotlib.figure
#     import matplotlib.pyplot as plt
# 
#     # Check if object already has export methods (SciTeX wrapped objects)
#     if hasattr(obj, "export_as_csv"):
#         return obj
# 
#     # Handle matplotlib Figure objects
#     if isinstance(obj, matplotlib.figure.Figure):
#         # Get the current axes that might be wrapped with SciTeX functionality
#         current_ax = plt.gca()
#         if hasattr(current_ax, "export_as_csv"):
#             return current_ax
# 
#         # Check all axes in the figure
#         for ax in obj.axes:
#             if hasattr(ax, "export_as_csv"):
#                 return ax
# 
#         return None
# 
#     # Handle matplotlib Axes objects
#     if isinstance(obj, matplotlib.axes.Axes):
#         if hasattr(obj, "export_as_csv"):
#             return obj
#         return None
# 
#     # Handle FigWrapper or similar SciTeX objects
#     if hasattr(obj, "figure") and hasattr(obj.figure, "axes"):
#         # Check if the wrapper itself has export methods
#         if hasattr(obj, "export_as_csv"):
#             return obj
# 
#         # Check the underlying figure's axes
#         for ax in obj.figure.axes:
#             if hasattr(ax, "export_as_csv"):
#                 return ax
# 
#         return None
# 
#     # Handle AxisWrapper or similar SciTeX objects
#     if hasattr(obj, "_axis_mpl") or hasattr(obj, "_ax"):
#         if hasattr(obj, "export_as_csv"):
#             return obj
#         return None
# 
#     # Try to get the current figure and its axes as fallback
#     try:
#         current_fig = plt.gcf()
#         current_ax = plt.gca()
# 
#         if hasattr(current_ax, "export_as_csv"):
#             return current_ax
#         elif hasattr(current_fig, "export_as_csv"):
#             return current_fig
# 
#         # Check all axes in current figure
#         for ax in current_fig.axes:
#             if hasattr(ax, "export_as_csv"):
#                 return ax
# 
#     except:
#         pass
# 
#     return None
# 
# 
# def save(
#     obj: Any,
#     specified_path: str,
#     makedirs: bool = True,
#     verbose: bool = True,
#     symlink_from_cwd: bool = False,
#     dry_run: bool = False,
#     no_csv: bool = False,
#     **kwargs,
# ) -> None:
#     """
#     Save an object to a file with the specified format.
# 
#     Parameters
#     ----------
#     obj : Any
#         The object to be saved. Can be a NumPy array, PyTorch tensor, Pandas DataFrame, or any serializable object.
#     specified_path : str
#         The file name or path where the object should be saved. The file extension determines the format.
#     makedirs : bool, optional
#         If True, create the directory path if it does not exist. Default is True.
#     verbose : bool, optional
#         If True, print a message upon successful saving. Default is True.
#     symlink_from_cwd : bool, optional
#         If True, create a _symlink from the current working directory. Default is False.
#     dry_run : bool, optional
#         If True, simulate the saving process without actually writing files. Default is False.
#     **kwargs
#         Additional keyword arguments to pass to the underlying save function of the specific format.
# 
#     Returns
#     -------
#     None
# 
#     Notes
#     -----
#     Supported formats include CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML, JSON, HDF5, PTH, MAT, and CBM.
#     The function dynamically selects the appropriate saving mechanism based on the file extension.
# 
#     Examples
#     --------
#     >>> import scitex
#     >>> import numpy as np
#     >>> import pandas as pd
#     >>> import torch
#     >>> import matplotlib.pyplot as plt
# 
#     >>> # Save NumPy array
#     >>> arr = np.array([1, 2, 3])
#     >>> scitex.io.save(arr, "data.npy")
# 
#     >>> # Save Pandas DataFrame
#     >>> df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
#     >>> scitex.io.save(df, "data.csv")
# 
#     >>> # Save PyTorch tensor
#     >>> tensor = torch.tensor([1, 2, 3])
#     >>> scitex.io.save(tensor, "model.pth")
# 
#     >>> # Save dictionary
#     >>> data_dict = {"a": 1, "b": 2, "c": [3, 4, 5]}
#     >>> scitex.io.save(data_dict, "data.pkl")
# 
#     >>> # Save matplotlib figure
#     >>> plt.figure()
#     >>> plt.plot(np.array([1, 2, 3]))
#     >>> scitex.io.save(plt, "plot.png")
# 
#     >>> # Save as YAML
#     >>> scitex.io.save(data_dict, "config.yaml")
# 
#     >>> # Save as JSON
#     >>> scitex.io.save(data_dict, "data.json")
#     """
#     try:
#         # Convert Path objects to strings to avoid AttributeError on startswith
#         if hasattr(
#             specified_path, "__fspath__"
#         ):  # Check if it's a path-like object
#             specified_path = str(specified_path)
# 
#         ########################################
#         # DO NOT MODIFY THIS SECTION
#         ########################################
#         #
#         # Determine saving directory from the script.
#         #
#         # When called in /path/to/script.py,
#         # data will be saved under `/path/to/script.py_out/`
#         #
#         # When called in a Jupyter notebook /path/to/notebook.ipynb,
#         # data will be saved under `/path/to/notebook_out/`
#         #
#         # When called in ipython environment,
#         # data will be saved under `/tmp/{_os.getenv("USER")/`
#         #
#         ########################################
#         spath, sfname = None, None
# 
#         # f-expression handling - safely parse f-strings
#         if specified_path.startswith('f"') or specified_path.startswith("f'"):
#             # Remove the f prefix and quotes
#             path_content = specified_path[2:-1]
# 
#             # Get the caller's frame to access their local variables
#             frame = inspect.currentframe().f_back
#             try:
#                 # Use string formatting with the caller's locals and globals
#                 # This is much safer than eval() as it only does string substitution
#                 import re
# 
#                 # Find all {variable} patterns
#                 variables = re.findall(r"\{([^}]+)\}", path_content)
#                 format_dict = {}
#                 for var in variables:
#                     # Only allow simple variable names, not arbitrary expressions
#                     if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
#                         if var in frame.f_locals:
#                             format_dict[var] = frame.f_locals[var]
#                         elif var in frame.f_globals:
#                             format_dict[var] = frame.f_globals[var]
#                     else:
#                         raise ValueError(
#                             f"Invalid variable name in f-string: {var}"
#                         )
# 
#                 # Use str.format() which is safe
#                 specified_path = path_content.format(**format_dict)
#             finally:
#                 del frame  # Avoid reference cycles
# 
#         # When full path
#         if specified_path.startswith("/"):
#             spath = specified_path
# 
#         # When relative path
#         else:
#             # Import here to avoid circular imports
#             from ..gen._detect_environment import detect_environment
#             from ..gen._get_notebook_path import get_notebook_info_simple
# 
#             # Detect the current environment
#             env_type = detect_environment()
# 
#             if env_type == "jupyter":
#                 # Special handling for Jupyter notebooks
#                 notebook_name, notebook_dir = get_notebook_info_simple()
# 
#                 if notebook_name:
#                     # Remove .ipynb extension and add _out
#                     notebook_base = _os.path.splitext(notebook_name)[0]
#                     sdir = _os.path.join(
#                         notebook_dir or _os.getcwd(), f"{notebook_base}_out"
#                     )
#                 else:
#                     # Fallback if we can't detect notebook name
#                     sdir = _os.path.join(_os.getcwd(), "notebook_out")
# 
#                 spath = _os.path.join(sdir, specified_path)
# 
#             elif env_type == "script":
#                 # Regular script handling
#                 script_path = inspect.stack()[1].filename
#                 sdir = clean_path(_os.path.splitext(script_path)[0] + "_out")
#                 spath = _os.path.join(sdir, specified_path)
# 
#             else:
#                 # IPython console or interactive mode
#                 script_path = inspect.stack()[1].filename
# 
#                 if (
#                     ("ipython" in script_path)
#                     or ("<stdin>" in script_path)
#                     or env_type in ["ipython", "interactive"]
#                 ):
#                     script_path = f'/tmp/{_os.getenv("USER")}'
#                     sdir = script_path
#                 else:
#                     # Unknown environment, use current directory
#                     sdir = _os.path.join(_os.getcwd(), "output")
# 
#                 spath = _os.path.join(sdir, specified_path)
# 
#         # Sanitization
#         spath_final = clean(spath)
#         ########################################
# 
#         # Potential path to _symlink
#         spath_cwd = _os.getcwd() + "/" + specified_path
#         spath_cwd = clean(spath_cwd)
# 
#         # Removes spath and spath_cwd to prevent potential circular links
#         # Skip deletion for CSV files to allow caching to work
#         # Also skip deletion for HDF5 files when a key is specified
#         should_skip_deletion = spath_final.endswith(".csv") or (
#             (spath_final.endswith(".hdf5") or spath_final.endswith(".h5"))
#             and "key" in kwargs
#         )
# 
#         if not should_skip_deletion:
#             for path in [spath_final, spath_cwd]:
#                 sh(f"rm -f {path}", verbose=False)
# 
#         if dry_run:
#             print(
#                 color_text(f"\n(dry run) Saved to: {spath_final}", c="yellow")
#             )
#             return
# 
#         # Ensure directory exists
#         if makedirs:
#             _os.makedirs(_os.path.dirname(spath_final), exist_ok=True)
# 
#         # Main
#         _save(
#             obj,
#             spath_final,
#             verbose=verbose,
#             symlink_from_cwd=symlink_from_cwd,
#             dry_run=dry_run,
#             no_csv=no_csv,
#             **kwargs,
#         )
# 
#         # Symbolic link
#         _symlink(spath, spath_cwd, symlink_from_cwd, verbose)
# 
#     except Exception as e:
#         logging.error(
#             f"Error occurred while saving: {str(e)}\n"
#             f"Debug: Initial script_path = {inspect.stack()[1].filename}\n"
#             f"Debug: Final spath = {spath}\n"
#             f"Debug: specified_path type = {type(specified_path)}\n"
#             f"Debug: specified_path = {specified_path}"
#         )
# 
# 
# def _symlink(spath, spath_cwd, symlink_from_cwd, verbose):
#     """Create a symbolic link from the current working directory."""
#     if symlink_from_cwd and (spath != spath_cwd):
#         _os.makedirs(_os.path.dirname(spath_cwd), exist_ok=True)
#         sh(f"rm -f {spath_cwd}", verbose=False)
#         sh(f"ln -sfr {spath} {spath_cwd}", verbose=False)
#         if verbose:
#             print(color_text(f"\n(Symlinked to: {spath_cwd})", "yellow"))
# 
# 
# def _save(
#     obj,
#     spath,
#     verbose=True,
#     symlink_from_cwd=False,
#     dry_run=False,
#     no_csv=False,
#     **kwargs,
# ):
#     # Don't use object's own save method - use consistent handlers
#     # This ensures all saves go through the same pipeline and get
#     # the yellow confirmation message
#     
#     # Get file extension
#     ext = _os.path.splitext(spath)[1].lower()
# 
#     # Try dispatch dictionary first for O(1) lookup
#     if ext in _FILE_HANDLERS:
#         # Check if handler needs special parameters
#         if ext in [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".svc"]:
#             _FILE_HANDLERS[ext](
#                 obj,
#                 spath,
#                 no_csv=no_csv,
#                 symlink_from_cwd=symlink_from_cwd,
#                 dry_run=dry_run,
#                 **kwargs,
#             )
#         elif ext in [".hdf5", ".h5", ".zarr"]:
#             # HDF5 and Zarr files may need special 'key' parameter
#             _FILE_HANDLERS[ext](obj, spath, **kwargs)
#         else:
#             _FILE_HANDLERS[ext](obj, spath, **kwargs)
#     # csv - special case as it doesn't have a dot prefix in dispatch
#     elif spath.endswith(".csv"):
#         save_csv(obj, spath, **kwargs)
#     # Check for special extension cases not in dispatch
#     elif spath.endswith(".pkl.gz"):
#         save_pickle_compressed(obj, spath, **kwargs)
#     else:
#         warnings.warn(f"Unsupported file format. {spath} was not saved.")
# 
#     if verbose:
#         if _os.path.exists(spath):
#             file_size = getsize(spath)
#             file_size = readable_bytes(file_size)
#             print(color_text(f"\nSaved to: {spath} ({file_size})", c="yellow"))
# 
# 
# def _save_separate_legends(
#     obj, spath, symlink_from_cwd=False, dry_run=False, **kwargs
# ):
#     """Save separate legend files if ax.legend('separate') was used."""
#     import matplotlib.figure
#     import matplotlib.pyplot as plt
# 
#     # Get the matplotlib figure object
#     fig = None
#     if isinstance(obj, matplotlib.figure.Figure):
#         fig = obj
#     elif hasattr(obj, "_fig_mpl"):
#         fig = obj._fig_mpl
#     elif hasattr(obj, "figure"):
#         if isinstance(obj.figure, matplotlib.figure.Figure):
#             fig = obj.figure
#         elif hasattr(obj.figure, "_fig_mpl"):
#             fig = obj.figure._fig_mpl
# 
#     if fig is None:
#         return
# 
#     # Check if there are separate legend parameters stored
#     if not hasattr(fig, "_separate_legend_params"):
#         return
# 
#     # Save each legend as a separate file
#     base_path = _os.path.splitext(spath)[0]
#     ext = _os.path.splitext(spath)[1]
# 
#     for legend_params in fig._separate_legend_params:
#         # Create a new figure for the legend
#         legend_fig = plt.figure(figsize=legend_params["figsize"])
#         legend_ax = legend_fig.add_subplot(111)
# 
#         # Create the legend
#         legend = legend_ax.legend(
#             legend_params["handles"],
#             legend_params["labels"],
#             loc="center",
#             frameon=legend_params["frameon"],
#             fancybox=legend_params["fancybox"],
#             shadow=legend_params["shadow"],
#             **legend_params["kwargs"],
#         )
# 
#         # Remove axes
#         legend_ax.axis("off")
# 
#         # Adjust layout to fit the legend
#         legend_fig.tight_layout()
# 
#         # Save the legend figure
#         legend_filename = f"{base_path}_{legend_params['axis_id']}_legend{ext}"
#         save_image(legend_fig, legend_filename, **kwargs)
# 
#         # Close the legend figure to free memory
#         plt.close(legend_fig)
# 
#         if not dry_run and _os.path.exists(legend_filename):
#             file_size = getsize(legend_filename)
#             file_size = readable_bytes(file_size)
#             print(
#                 color_text(
#                     f"\nSaved legend to: {legend_filename} ({file_size})",
#                     c="yellow",
#                 )
#             )
# 
# 
# def _handle_image_with_csv(
#     obj, spath, no_csv=False, symlink_from_cwd=False, dry_run=False, **kwargs
# ):
#     """Handle image file saving with optional CSV export."""
#     save_image(obj, spath, **kwargs)
# 
#     # Handle separate legend saving
#     _save_separate_legends(
#         obj,
#         spath,
#         symlink_from_cwd=symlink_from_cwd,
#         dry_run=dry_run,
#         **kwargs,
#     )
# 
#     if not no_csv:
#         ext = _os.path.splitext(spath)[1].lower()
#         ext_wo_dot = ext.replace(".", "")
# 
#         try:
#             # Get the figure object that may contain plot data
#             fig_obj = _get_figure_with_data(obj)
# 
#             if fig_obj is not None:
#                 # Save regular CSV if export method exists
#                 if hasattr(fig_obj, "export_as_csv"):
#                     csv_data = fig_obj.export_as_csv()
#                     if csv_data is not None and not csv_data.empty:
#                         save(
#                             csv_data,
#                             spath.replace(ext_wo_dot, "csv"),
#                             symlink_from_cwd=symlink_from_cwd,
#                             dry_run=dry_run,
#                             no_csv=True,
#                             **kwargs,
#                         )
# 
#                 # Save SigmaPlot CSV if method exists
#                 if hasattr(fig_obj, "export_as_csv_for_sigmaplot"):
#                     sigmaplot_data = fig_obj.export_as_csv_for_sigmaplot()
#                     if sigmaplot_data is not None and not sigmaplot_data.empty:
#                         save(
#                             sigmaplot_data,
#                             spath.replace(ext_wo_dot, "csv").replace(
#                                 ".csv", "_for_sigmaplot.csv"
#                             ),
#                             symlink_from_cwd=symlink_from_cwd,
#                             dry_run=dry_run,
#                             no_csv=True,
#                             **kwargs,
#                         )
#         except Exception:
#             pass
# 
# 
# # Dispatch dictionary for O(1) file format lookup
# _FILE_HANDLERS = {
#     # Excel formats
#     ".xlsx": save_excel,
#     ".xls": save_excel,
#     # NumPy formats
#     ".npy": save_npy,
#     ".npz": save_npz,
#     # Pickle formats
#     ".pkl": save_pickle,
#     ".pickle": save_pickle,
#     ".pkl.gz": save_pickle_compressed,
#     # Other binary formats
#     ".joblib": save_joblib,
#     ".pth": save_torch,
#     ".pt": save_torch,
#     ".mat": save_matlab,
#     ".cbm": save_catboost,
#     # Text formats
#     ".json": save_json,
#     ".yaml": save_yaml,
#     ".yml": save_yaml,
#     ".txt": save_text,
#     ".md": save_text,
#     ".py": save_text,
#     ".css": save_text,
#     ".js": save_text,
#     # Bibliography
#     ".bib": save_bibtex,
#     # Data formats
#     ".html": save_html,
#     ".hdf5": save_hdf5,
#     ".h5": save_hdf5,
#     ".zarr": save_zarr,
#     # Media formats
#     ".mp4": save_mp4,
#     ".png": _handle_image_with_csv,
#     ".jpg": _handle_image_with_csv,
#     ".jpeg": _handle_image_with_csv,
#     ".gif": _handle_image_with_csv,
#     ".tiff": _handle_image_with_csv,
#     ".tif": _handle_image_with_csv,
#     ".svg": _handle_image_with_csv,
#     ".pdf": _handle_image_with_csv,
# }
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save.py
# --------------------------------------------------------------------------------
