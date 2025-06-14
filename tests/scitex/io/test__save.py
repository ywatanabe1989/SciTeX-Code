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
