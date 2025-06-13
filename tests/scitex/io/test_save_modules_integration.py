#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 15:06:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/test_save_modules_integration.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/test_save_modules_integration.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Integration tests for scitex.io save modules.

This test file verifies that:
1. All save modules can be imported correctly
2. The _mv_to_tmp import issue is resolved
3. All save functions work as expected
"""

import tempfile
import shutil
import numpy as np
import pandas as pd
import pytest
import torch
import matplotlib.pyplot as plt

import scitex


class TestSaveModulesIntegration:
    """Test suite for save modules integration"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_import_save_modules(self):
        """Test that all save modules can be imported"""
        # Test importing from main save module
        from scitex.io import save
        
        # Test importing from save_modules package
        from scitex.io import (
            save_csv,
            save_excel,
            save_npy,
            save_npz,
            save_pickle,
            save_pickle_compressed,
            save_joblib,
            save_torch,
            save_json,
            save_yaml,
            save_hdf5,
            save_matlab,
            save_catboost,
            save_text,
            save_html,
            save_image,
            save_mp4,
            save_listed_dfs_as_csv,
            save_listed_scalars_as_csv,
            save_optuna_study_as_csv_and_pngs,
        )
        
        # Verify all imports are callable
        assert callable(save)
        assert callable(save_csv)
        assert callable(save_listed_dfs_as_csv)
        
    def test_save_listed_dfs_functionality(self, temp_dir):
        """Test save_listed_dfs_as_csv functionality"""
        # Create test dataframes
        df1 = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        df2 = pd.DataFrame({'x': [7, 8, 9], 'y': [10, 11, 12]})
        listed_dfs = [df1, df2]
        
        # Test path
        csv_path = os.path.join(temp_dir, "test_listed_dfs.csv")
        
        # Save using scitex.io.save
        scitex.io.save(listed_dfs, csv_path)
        
        # Verify file exists
        assert os.path.exists(csv_path)
        
        # Read and verify content
        with open(csv_path, 'r') as f:
            content = f.read()
            assert '0' in content  # First dataframe index
            assert '1' in content  # Second dataframe index
            assert 'a,b' in content  # First df columns
            assert 'x,y' in content  # Second df columns
    
    def test_save_listed_scalars_functionality(self, temp_dir):
        """Test save_listed_scalars_as_csv functionality"""
        # Create test scalars
        scalars = [1.5, 2.7, 3.9, 4.2]
        
        # Test path
        csv_path = os.path.join(temp_dir, "test_listed_scalars.csv")
        
        # Save using scitex.io.save
        scitex.io.save(scalars, csv_path)
        
        # Verify file exists
        assert os.path.exists(csv_path)
        
        # Read and verify content
        loaded_df = pd.read_csv(csv_path)
        assert len(loaded_df) == len(scalars)
    
    def test_save_numpy_arrays(self, temp_dir):
        """Test saving numpy arrays in various formats"""
        # Create test array
        arr = np.random.rand(10, 5)
        
        # Test .npy format
        npy_path = os.path.join(temp_dir, "test_array.npy")
        scitex.io.save(arr, npy_path)
        assert os.path.exists(npy_path)
        loaded_npy = np.load(npy_path)
        np.testing.assert_array_almost_equal(arr, loaded_npy)
        
        # Test .npz format
        npz_path = os.path.join(temp_dir, "test_array.npz")
        scitex.io.save({'array': arr}, npz_path)
        assert os.path.exists(npz_path)
        loaded_npz = np.load(npz_path)
        np.testing.assert_array_almost_equal(arr, loaded_npz['array'])
    
    def test_save_dataframe_csv(self, temp_dir):
        """Test saving pandas DataFrame as CSV"""
        # Create test dataframe
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4],
            'col2': ['a', 'b', 'c', 'd'],
            'col3': [1.1, 2.2, 3.3, 4.4]
        })
        
        # Test path
        csv_path = os.path.join(temp_dir, "test_df.csv")
        
        # Save
        scitex.io.save(df, csv_path)
        assert os.path.exists(csv_path)
        
        # Load and verify
        loaded_df = pd.read_csv(csv_path, index_col=0)
        pd.testing.assert_frame_equal(df, loaded_df)
    
    def test_save_torch_tensor(self, temp_dir):
        """Test saving PyTorch tensor"""
        # Create test tensor
        tensor = torch.randn(5, 3)
        
        # Test path
        pth_path = os.path.join(temp_dir, "test_tensor.pth")
        
        # Save
        scitex.io.save(tensor, pth_path)
        assert os.path.exists(pth_path)
        
        # Load and verify
        loaded_tensor = torch.load(pth_path)
        torch.testing.assert_close(tensor, loaded_tensor)
    
    def test_save_dict_json(self, temp_dir):
        """Test saving dictionary as JSON"""
        # Create test dictionary
        test_dict = {
            'name': 'test',
            'value': 42,
            'nested': {'a': 1, 'b': 2}
        }
        
        # Test path
        json_path = os.path.join(temp_dir, "test_dict.json")
        
        # Save
        scitex.io.save(test_dict, json_path)
        assert os.path.exists(json_path)
        
        # Load and verify
        import json
        with open(json_path, 'r') as f:
            loaded_dict = json.load(f)
        assert loaded_dict == test_dict
    
    def test_save_figure_image(self, temp_dir):
        """Test saving matplotlib figure as image"""
        # Create test figure
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        ax.set_title('Test Plot')
        
        # Test path
        png_path = os.path.join(temp_dir, "test_figure.png")
        
        # Save
        scitex.io.save(fig, png_path)
        assert os.path.exists(png_path)
        
        # Verify file size (should be non-empty)
        assert os.path.getsize(png_path) > 0
        
        plt.close(fig)
    
    def test_save_text_content(self, temp_dir):
        """Test saving text content"""
        # Create test text
        text_content = "This is a test\nWith multiple lines\nAnd special chars: ñáéíóú"
        
        # Test path
        txt_path = os.path.join(temp_dir, "test_text.txt")
        
        # Save
        scitex.io.save(text_content, txt_path)
        assert os.path.exists(txt_path)
        
        # Load and verify
        with open(txt_path, 'r', encoding='utf-8') as f:
            loaded_text = f.read()
        assert loaded_text == text_content
    
    def test_mv_to_tmp_import(self):
        """Test that _mv_to_tmp can be imported correctly from save modules"""
        # This specifically tests the import that was causing issues
        from scitex.io._save_modules import _save_listed_dfs_as_csv
from scitex.io._save_modules import _save_listed_scalars_as_csv
        
        # Verify the functions have access to _mv_to_tmp
        import inspect
        
        # Check that the functions exist and are callable
        assert callable(_save_listed_dfs_as_csv)
        assert callable(_save_listed_scalars_as_csv)
        
        # Get the source to verify imports
        source = inspect.getsource(_save_listed_dfs_as_csv)
        assert 'from .._mv_to_tmp import _mv_to_tmp' in source
    
    def test_overwrite_with_mv_to_tmp(self, temp_dir):
        """Test that overwrite functionality works with _mv_to_tmp"""
        # Create initial file
        csv_path = os.path.join(temp_dir, "test_overwrite.csv")
        df1 = pd.DataFrame({'a': [1, 2, 3]})
        scitex.io.save(df1, csv_path)
        
        # Save again with overwrite
        df2 = pd.DataFrame({'b': [4, 5, 6]})
        listed_dfs = [df2]
        scitex.io.save(listed_dfs, csv_path)
        
        # Verify new content
        with open(csv_path, 'r') as f:
            content = f.read()
            assert 'b' in content
            assert 'a' not in content  # Old content should be gone


class TestSaveModulesEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_save_with_no_extension(self, temp_dir):
        """Test saving when no file extension is provided"""
        data = {'test': 'data'}
        path = os.path.join(temp_dir, "test_no_ext")
        
        # Should default to pickle
        scitex.io.save(data, path)
        assert os.path.exists(path) or os.path.exists(path + '.pkl')
    
    def test_save_unsupported_format(self, temp_dir):
        """Test saving with unsupported file extension"""
        data = {'test': 'data'}
        path = os.path.join(temp_dir, "test.xyz")
        
        # Should either raise error or default to a format
        try:
            scitex.io.save(data, path)
            # If it doesn't raise, verify file exists
            assert os.path.exists(path)
        except (ValueError, NotImplementedError):
            # Expected behavior for unsupported format
            pass
    
    def test_save_nested_directory_creation(self, temp_dir):
        """Test that nested directories are created when saving"""
        data = np.array([1, 2, 3])
        nested_path = os.path.join(temp_dir, "level1", "level2", "level3", "test.npy")
        
        # Save with makedirs=True (default)
        scitex.io.save(data, nested_path)
        
        # Verify file and directories exist
        assert os.path.exists(nested_path)
        assert os.path.exists(os.path.dirname(nested_path))


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

# EOF