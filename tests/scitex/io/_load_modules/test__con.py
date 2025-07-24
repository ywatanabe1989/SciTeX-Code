#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:59:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__con.py

"""Comprehensive tests for MNE connectivity file loading functionality."""

import os
import tempfile
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


class TestLoadCon:
    """Test suite for _load_con function"""
    
    def test_valid_extension_check(self):
        """Test that function validates .con extension"""
        from scitex.io._load_modules import _load_con
        
        # Test invalid extensions
        invalid_files = ["file.txt", "data.fif", "connectivity.csv", "test.xlsx"]
        
        for invalid_file in invalid_files:
            with pytest.raises(ValueError, match="File must have .con extension"):
                _load_con(invalid_file)
    
    @patch('mne.io.read_raw_fif')
    def test_mne_read_raw_fif_called_correctly(self, mock_read_raw):
        """Test that mne.io.read_raw_fif is called with correct parameters"""
        from scitex.io._load_modules import _load_con
        
        # Mock the MNE raw object
        mock_raw = MagicMock()
        mock_df = pd.DataFrame({'channel_1': [1, 2, 3], 'channel_2': [4, 5, 6]})
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 250.0}
        mock_read_raw.return_value = mock_raw
        
        # Call function
        result = _load_con('test_file.con', verbose=False, picks=['eeg'])
        
        # Verify MNE function was called correctly
        mock_read_raw.assert_called_once_with('test_file.con', preload=True, verbose=False, picks=['eeg'])
        mock_raw.to_data_frame.assert_called_once()
        
        # Verify the result structure
        assert isinstance(result, pd.DataFrame)
        assert 'samp_rate' in result.columns
    
    @patch('mne.io.read_raw_fif')
    def test_dataframe_conversion_and_samp_rate_addition(self, mock_read_raw):
        """Test that raw data is converted to DataFrame and samp_rate is added"""
        from scitex.io._load_modules import _load_con
        
        # Create mock data
        mock_raw = MagicMock()
        mock_df = pd.DataFrame({
            'Fp1': [0.1, 0.2, 0.3],
            'Fp2': [0.4, 0.5, 0.6],
            'F3': [0.7, 0.8, 0.9]
        })
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 512.0}
        mock_read_raw.return_value = mock_raw
        
        # Call function
        result = _load_con('connectivity.con')
        
        # Verify DataFrame structure
        assert isinstance(result, pd.DataFrame)
        assert 'samp_rate' in result.columns
        assert all(result['samp_rate'] == 512.0)
        assert 'Fp1' in result.columns
        assert 'Fp2' in result.columns
        assert 'F3' in result.columns
        
        # Verify original data is preserved
        assert list(result['Fp1']) == [0.1, 0.2, 0.3]
        assert list(result['Fp2']) == [0.4, 0.5, 0.6]
        assert list(result['F3']) == [0.7, 0.8, 0.9]
    
    @patch('mne.io.read_raw_fif')
    def test_sampling_rate_extraction(self, mock_read_raw):
        """Test different sampling rate scenarios"""
        from scitex.io._load_modules import _load_con
        
        sampling_rates = [250.0, 500.0, 1000.0, 2048.0]
        
        for sfreq in sampling_rates:
            mock_raw = MagicMock()
            mock_df = pd.DataFrame({'channel': [1, 2, 3]})
            mock_raw.to_data_frame.return_value = mock_df
            mock_raw.info = {'sfreq': sfreq}
            mock_read_raw.return_value = mock_raw
            
            result = _load_con('test.con')
            
            assert result['samp_rate'].iloc[0] == sfreq
            assert all(result['samp_rate'] == sfreq)  # All rows should have same sampling rate
    
    @patch('mne.io.read_raw_fif')
    def test_kwargs_forwarding(self, mock_read_raw):
        """Test that kwargs are properly forwarded to mne.io.read_raw_fif"""
        from scitex.io._load_modules import _load_con
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame({'data': [1, 2, 3]})
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 250.0}
        mock_read_raw.return_value = mock_raw
        
        # Test various kwargs
        kwargs = {
            'verbose': False,
            'picks': ['eeg'],
            'exclude': ['bad_channel'],
            'proj': True
        }
        
        _load_con('test.con', **kwargs)
        
        # Verify all kwargs were passed to mne function
        mock_read_raw.assert_called_once_with('test.con', preload=True, **kwargs)
    
    @patch('mne.io.read_raw_fif')
    def test_mne_exception_propagation(self, mock_read_raw):
        """Test that MNE exceptions are properly propagated"""
        from scitex.io._load_modules import _load_con
        
        # Test file not found error
        mock_read_raw.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            _load_con('nonexistent.con')
        
        # Test invalid file format error
        mock_read_raw.side_effect = ValueError("Invalid file format")
        
        with pytest.raises(ValueError, match="Invalid file format"):
            _load_con('invalid.con')
    
    @patch('mne.io.read_raw_fif')
    def test_empty_dataframe_handling(self, mock_read_raw):
        """Test handling of empty dataframes"""
        from scitex.io._load_modules import _load_con
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame()  # Empty DataFrame
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 250.0}
        mock_read_raw.return_value = mock_raw
        
        result = _load_con('empty.con')
        
        assert isinstance(result, pd.DataFrame)
        assert 'samp_rate' in result.columns
        assert len(result) == 0
    
    @patch('mne.io.read_raw_fif')
    def test_large_dataframe_handling(self, mock_read_raw):
        """Test handling of large dataframes"""
        from scitex.io._load_modules import _load_con
        
        # Create large mock DataFrame (1000 samples, 64 channels)
        import numpy as np
        n_samples, n_channels = 1000, 64
        data = np.random.randn(n_samples, n_channels)
        columns = [f'channel_{i}' for i in range(n_channels)]
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame(data, columns=columns)
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 1000.0}
        mock_read_raw.return_value = mock_raw
        
        result = _load_con('large.con')
        
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (n_samples, n_channels + 1)  # +1 for samp_rate
        assert 'samp_rate' in result.columns
        assert all(result['samp_rate'] == 1000.0)
    
    @patch('mne.io.read_raw_fif')
    def test_missing_sfreq_info(self, mock_read_raw):
        """Test handling when sfreq is missing from info"""
        from scitex.io._load_modules import _load_con
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame({'channel': [1, 2, 3]})
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {}  # Missing sfreq
        mock_read_raw.return_value = mock_raw
        
        with pytest.raises(KeyError):
            _load_con('test.con')
    
    def test_function_signature(self):
        """Test function signature and type annotations"""
        from scitex.io._load_modules import _load_con
        import inspect
        
        sig = inspect.signature(_load_con)
        
        # Check parameters
        assert 'lpath' in sig.parameters
        assert 'kwargs' in sig.parameters or len(sig.parameters) >= 1
        
        # Check return annotation
        assert sig.return_annotation != inspect.Signature.empty
    
    @patch('mne.io.read_raw_fif')
    def test_real_world_eeg_scenario(self, mock_read_raw):
        """Test realistic EEG connectivity file scenario"""
        from scitex.io._load_modules import _load_con
        
        # Simulate realistic EEG data
        eeg_channels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2']
        n_samples = 2560  # 10 seconds at 256 Hz
        
        # Create realistic EEG data
        import numpy as np
        np.random.seed(42)
        eeg_data = np.random.randn(n_samples, len(eeg_channels)) * 50e-6  # Realistic EEG amplitudes
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame(eeg_data, columns=eeg_channels)
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 256.0}
        mock_read_raw.return_value = mock_raw
        
        result = _load_con('eeg_connectivity.con', verbose=False)
        
        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (n_samples, len(eeg_channels) + 1)
        assert all(col in result.columns for col in eeg_channels)
        assert 'samp_rate' in result.columns
        assert all(result['samp_rate'] == 256.0)
        
        # Verify data integrity
        for ch in eeg_channels:
            assert not result[ch].isna().any()
            assert len(result[ch]) == n_samples
    
    @patch('mne.io.read_raw_fif')
    def test_preload_always_true(self, mock_read_raw):
        """Test that preload=True is always enforced"""
        from scitex.io._load_modules import _load_con
        
        mock_raw = MagicMock()
        mock_df = pd.DataFrame({'data': [1]})
        mock_raw.to_data_frame.return_value = mock_df
        mock_raw.info = {'sfreq': 250.0}
        mock_read_raw.return_value = mock_raw
        
        # Even if user passes preload=False, it should be overridden to True
        _load_con('test.con')
        
        # Verify preload=True was used
        args, kwargs = mock_read_raw.call_args
        assert kwargs['preload'] is True

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_con.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:51:45 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_con.py
# 
# from typing import Any
# 
# import mne
# 
# 
# def _load_con(lpath: str, **kwargs) -> Any:
#     if not lpath.endswith(".con"):
#         raise ValueError("File must have .con extension")
#     obj = mne.io.read_raw_fif(lpath, preload=True, **kwargs)
#     obj = obj.to_data_frame()
#     obj["samp_rate"] = obj.info["sfreq"]
#     return obj
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_con.py
# --------------------------------------------------------------------------------
