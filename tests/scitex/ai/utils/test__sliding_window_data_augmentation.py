#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 03:45:00 (ywatanabe)"
# File: ./tests/scitex/ai/utils/test__sliding_window_data_augmentation.py

"""Comprehensive tests for scitex.ai.utils._sliding_window_data_augmentation module.

This module provides sliding window data augmentation for time series data,
commonly used in machine learning for creating training samples from continuous
signals.
"""

import pytest
import numpy as np
import torch
from unittest.mock import patch, MagicMock
import random
import warnings
from typing import Union, Tuple, List
import tempfile
import pickle
import gc
import psutil
import os

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False

from scitex.ai.utils import sliding_window_data_augmentation


class TestSlidingWindowDataAugmentationBasic:
    """Basic functionality tests for sliding_window_data_augmentation."""

    def test_basic_1d_array(self):
        """Test with basic 1D array."""
        x = np.arange(100)
        window_size = 30
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check output shape
        assert result.shape == (window_size,)
        # Check that values are from original array
        assert np.all(np.isin(result, x))
        # Check consecutive values
        assert np.all(np.diff(result) == 1)

    def test_2d_array(self):
        """Test with 2D array (channels x time)."""
        x = np.random.rand(5, 1000)  # 5 channels, 1000 time points
        window_size = 200
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check output shape
        assert result.shape == (5, window_size)
        # Check that all channels are included
        assert result.shape[0] == x.shape[0]

    def test_3d_array(self):
        """Test with 3D array (batch x channels x time)."""
        x = np.random.rand(10, 5, 500)
        window_size = 100
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check output shape
        assert result.shape == (10, 5, window_size)
        # Check that batch and channel dimensions are preserved
        assert result.shape[:-1] == x.shape[:-1]

    def test_torch_tensor(self):
        """Test with PyTorch tensor."""
        x = torch.randn(3, 4, 1000)
        window_size = 256
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check output type and shape
        assert isinstance(result, torch.Tensor)
        assert result.shape == (3, 4, window_size)

    def test_window_size_equals_array_size(self):
        """Test when window size equals array size."""
        x = np.arange(50)
        window_size = 50
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Should return the entire array
        np.testing.assert_array_equal(result, x)

    def test_deterministic_with_fixed_seed(self):
        """Test deterministic behavior with fixed random seed."""
        x = np.arange(100)
        window_size = 30
        
        # Fix random seed
        with patch('random.randint', return_value=10):
            result1 = sliding_window_data_augmentation(x, window_size)
            result2 = sliding_window_data_augmentation(x, window_size)
        
        # Should produce same results
        np.testing.assert_array_equal(result1, result2)
        # Check specific window
        np.testing.assert_array_equal(result1, x[10:40])

    def test_random_window_positions(self):
        """Test that different windows are selected randomly."""
        x = np.arange(1000)
        window_size = 100
        
        # Get multiple windows
        windows = []
        for _ in range(10):
            window = sliding_window_data_augmentation(x, window_size)
            windows.append(window[0])  # Store first element
        
        # Should have different starting positions
        unique_starts = len(set(windows))
        assert unique_starts > 1  # Very unlikely to get same position 10 times

    def test_window_larger_than_array_error(self):
        """Test error when window size is larger than array."""
        x = np.arange(50)
        window_size = 100
        
        with pytest.raises(ValueError):
            sliding_window_data_augmentation(x, window_size)

    def test_negative_window_size_error(self):
        """Test error with negative window size."""
        x = np.arange(100)
        window_size = -10
        
        with pytest.raises(ValueError):
            sliding_window_data_augmentation(x, window_size)

    def test_zero_window_size(self):
        """Test with zero window size."""
        x = np.arange(100)
        window_size = 0
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Should return empty array with same number of dimensions
        assert result.shape == (0,)

    def test_float_array(self):
        """Test with float array."""
        x = np.random.randn(200).astype(np.float32)
        window_size = 50
        
        result = sliding_window_data_augmentation(x, window_size)
        
        assert result.dtype == np.float32
        assert result.shape == (window_size,)

    def test_complex_array(self):
        """Test with complex array."""
        x = np.random.randn(100) + 1j * np.random.randn(100)
        window_size = 30
        
        result = sliding_window_data_augmentation(x, window_size)
        
        assert result.dtype == np.complex128
        assert result.shape == (window_size,)

    def test_preserves_data_continuity(self):
        """Test that data continuity is preserved."""
        # Create array with specific pattern
        x = np.sin(np.linspace(0, 10*np.pi, 1000))
        window_size = 200
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check that the window contains continuous data
        # by verifying the sine wave pattern is preserved
        diffs = np.diff(result)
        # Adjacent differences should be smooth (no jumps)
        assert np.all(np.abs(diffs) < 0.1)  # Small threshold for continuity

    @pytest.mark.parametrize("shape,window_size", [
        ((100,), 50),
        ((10, 100), 30),
        ((5, 10, 200), 100),
        ((2, 3, 4, 500), 250),
    ])
    def test_various_shapes(self, shape, window_size):
        """Test with various array shapes."""
        x = np.random.rand(*shape)
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Check that all dimensions except last are preserved
        assert result.shape[:-1] == x.shape[:-1]
        assert result.shape[-1] == window_size

    def test_boundary_cases(self):
        """Test boundary cases for window selection."""
        x = np.arange(100)
        window_size = 20
        
        # Mock to test boundary positions
        # Test start position
        with patch('random.randint', return_value=0):
            result = sliding_window_data_augmentation(x, window_size)
            np.testing.assert_array_equal(result, x[:20])
        
        # Test end position
        with patch('random.randint', return_value=80):
            result = sliding_window_data_augmentation(x, window_size)
            np.testing.assert_array_equal(result, x[80:100])

    def test_data_augmentation_variety(self):
        """Test that augmentation provides variety for training."""
        x = np.random.rand(1000)
        window_size = 100
        
        # Collect multiple augmented samples
        samples = []
        for _ in range(50):
            sample = sliding_window_data_augmentation(x, window_size)
            samples.append(sample)
        
        # Convert to array for analysis
        samples = np.array(samples)
        
        # Check that we get variety in the data
        # Mean of first elements should vary
        first_elements = samples[:, 0]
        assert np.std(first_elements) > 0.1  # Should have variation


class TestSlidingWindowDataAugmentationAdvanced:
    """Advanced tests for sliding window data augmentation."""
    
    def test_time_series_data_structure(self):
        """Test with typical time series data structures."""
        # Multi-channel EEG data (channels x time)
        eeg_data = np.random.randn(64, 10000)  # 64 channels, 10k samples
        window_size = 1000
        
        result = sliding_window_data_augmentation(eeg_data, window_size)
        
        assert result.shape == (64, window_size)
        # Verify channel integrity
        for ch in range(64):
            # Each channel should be continuous
            assert np.all(np.diff(np.where(np.isin(eeg_data[ch], result[ch]))[0]) == 1)
    
    def test_batch_processing_consistency(self):
        """Test consistency when processing batches."""
        batch_data = np.random.randn(32, 10, 5000)  # 32 batch, 10 channels, 5k samples
        window_size = 500
        
        # Process each batch item
        results = []
        for i in range(32):
            with patch('random.randint', return_value=100):
                result = sliding_window_data_augmentation(batch_data[i], window_size)
                results.append(result)
        
        # All should have same window position due to fixed random
        results = np.array(results)
        assert results.shape == (32, 10, window_size)
        
        # Verify each batch processed independently
        for i in range(32):
            np.testing.assert_array_equal(results[i], batch_data[i, :, 100:600])
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large arrays."""
        # Create large array
        large_array = np.random.randn(100, 50000)  # ~40MB
        window_size = 1000
        
        # Get memory before
        gc.collect()
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        
        # Perform augmentation
        result = sliding_window_data_augmentation(large_array, window_size)
        
        # Get memory after
        gc.collect()
        mem_after = process.memory_info().rss
        
        # Memory increase should be minimal (just the window)
        mem_increase = mem_after - mem_before
        expected_size = result.nbytes
        
        # Allow some overhead but should be roughly the window size
        assert mem_increase < expected_size * 3  # Allow 3x for overhead
    
    @pytest.mark.skipif(not HAS_PANDAS, reason="pandas not available")
    def test_pandas_dataframe_compatibility(self):
        """Test with pandas DataFrame."""
        # Create DataFrame with time series
        df = pd.DataFrame({
            'sensor1': np.random.randn(1000),
            'sensor2': np.random.randn(1000),
            'sensor3': np.random.randn(1000)
        })
        
        # Convert to numpy for processing
        data = df.values.T  # Shape: (3, 1000)
        window_size = 200
        
        result = sliding_window_data_augmentation(data, window_size)
        
        assert result.shape == (3, window_size)
        
        # Convert back to DataFrame
        result_df = pd.DataFrame(result.T, columns=df.columns)
        assert len(result_df) == window_size
        assert list(result_df.columns) == list(df.columns)
    
    @pytest.mark.skipif(not HAS_XARRAY, reason="xarray not available")
    def test_xarray_compatibility(self):
        """Test with xarray DataArray."""
        # Create xarray with time dimension
        time = pd.date_range('2024-01-01', periods=1000, freq='1min')
        data = xr.DataArray(
            np.random.randn(5, 1000),
            dims=['channel', 'time'],
            coords={'channel': ['ch1', 'ch2', 'ch3', 'ch4', 'ch5'],
                   'time': time}
        )
        
        window_size = 100
        result = sliding_window_data_augmentation(data.values, window_size)
        
        assert result.shape == (5, window_size)
    
    def test_gradient_preservation(self):
        """Test that gradients are preserved for torch tensors."""
        x = torch.randn(10, 1000, requires_grad=True)
        window_size = 200
        
        result = sliding_window_data_augmentation(x, window_size)
        
        # Should preserve gradient requirement
        assert result.requires_grad == True
        
        # Gradient should flow back
        loss = result.sum()
        loss.backward()
        
        assert x.grad is not None
        # Only the selected window should have gradients
        grad_sum = x.grad.sum(dim=0)
        non_zero_grads = (grad_sum != 0).sum()
        assert non_zero_grads == window_size


class TestSlidingWindowDataAugmentationEdgeCases:
    """Edge case tests for sliding window augmentation."""
    
    def test_single_sample_window(self):
        """Test with window size of 1."""
        x = np.arange(100)
        window_size = 1
        
        result = sliding_window_data_augmentation(x, window_size)
        
        assert result.shape == (1,)
        assert result[0] in x
    
    def test_non_contiguous_array(self):
        """Test with non-contiguous array."""
        # Create non-contiguous array by slicing
        x = np.arange(1000).reshape(10, 100)
        x_slice = x[::2, ::2]  # Non-contiguous
        assert not x_slice.flags['C_CONTIGUOUS']
        
        window_size = 20
        result = sliding_window_data_augmentation(x_slice, window_size)
        
        assert result.shape == (5, window_size)
    
    def test_fortran_order_array(self):
        """Test with Fortran-ordered array."""
        x = np.asfortranarray(np.random.randn(50, 1000))
        window_size = 100
        
        result = sliding_window_data_augmentation(x, window_size)
        
        assert result.shape == (50, window_size)
        # Result should maintain order
        assert result.flags['F_CONTIGUOUS'] or result.flags['C_CONTIGUOUS']
    
    def test_view_vs_copy_behavior(self):
        """Test whether result is a view or copy."""
        x = np.arange(1000)
        window_size = 100
        
        with patch('random.randint', return_value=100):
            result = sliding_window_data_augmentation(x, window_size)
        
        # Modify result
        original_value = result[0]
        result[0] = -999
        
        # Check if original is modified (view) or not (copy)
        if x[100] == -999:
            # It's a view
            assert result.base is x
        else:
            # It's a copy
            assert result.base is not x
        
        # Restore for other tests
        if x[100] == -999:
            x[100] = original_value
    
    def test_masked_array(self):
        """Test with numpy masked array."""
        x = np.ma.array(np.arange(100), mask=np.zeros(100, dtype=bool))
        x.mask[40:60] = True  # Mask some values
        window_size = 30
        
        result = sliding_window_data_augmentation(x, window_size)
        
        assert isinstance(result, np.ma.MaskedArray)
        assert result.shape == (window_size,)
    
    def test_structured_array(self):
        """Test with structured numpy array."""
        # Create structured array
        dt = np.dtype([('time', 'f8'), ('value', 'f8'), ('flag', 'i4')])
        x = np.zeros(1000, dtype=dt)
        x['time'] = np.arange(1000)
        x['value'] = np.random.randn(1000)
        x['flag'] = np.random.randint(0, 2, 1000)
        
        window_size = 100
        result = sliding_window_data_augmentation(x, window_size)
        
        assert result.dtype == dt
        assert result.shape == (window_size,)
        assert np.all(np.diff(result['time']) == 1)  # Time continuity


class TestSlidingWindowDataAugmentationErrors:
    """Error handling tests."""
    
    def test_invalid_input_types(self):
        """Test with invalid input types."""
        # List input
        with pytest.raises(AttributeError):
            sliding_window_data_augmentation([1, 2, 3, 4], 2)
        
        # Scalar input
        with pytest.raises(AttributeError):
            sliding_window_data_augmentation(42, 10)
        
        # None input
        with pytest.raises(AttributeError):
            sliding_window_data_augmentation(None, 10)
    
    def test_invalid_window_sizes(self):
        """Test with invalid window sizes."""
        x = np.arange(100)
        
        # Negative window size
        with pytest.raises(ValueError):
            sliding_window_data_augmentation(x, -10)
        
        # Window larger than data
        with pytest.raises(ValueError):
            sliding_window_data_augmentation(x, 200)
        
        # Float window size (should work if can be converted to int)
        result = sliding_window_data_augmentation(x, 30.0)
        assert result.shape == (30,)
    
    def test_empty_array(self):
        """Test with empty array."""
        x = np.array([])
        
        # Any window size should fail
        with pytest.raises(ValueError):
            sliding_window_data_augmentation(x, 1)
    
    def test_nan_inf_values(self):
        """Test with NaN and Inf values."""
        x = np.random.randn(1000)
        x[100:110] = np.nan
        x[200:210] = np.inf
        x[300:310] = -np.inf
        
        window_size = 50
        
        # Should work normally
        result = sliding_window_data_augmentation(x, window_size)
        assert result.shape == (window_size,)
        
        # May contain special values depending on window position
        # This is expected behavior


class TestSlidingWindowDataAugmentationPerformance:
    """Performance and efficiency tests."""
    
    def test_large_array_performance(self):
        """Test performance with large arrays."""
        import time
        
        # Large array (100MB)
        x = np.random.randn(1000, 100000)
        window_size = 1000
        
        start_time = time.time()
        result = sliding_window_data_augmentation(x, window_size)
        end_time = time.time()
        
        # Should be fast (< 1 second for slicing)
        assert end_time - start_time < 1.0
        assert result.shape == (1000, window_size)
    
    def test_repeated_augmentation_performance(self):
        """Test performance of repeated augmentations."""
        import time
        
        x = np.random.randn(10, 10000)
        window_size = 1000
        
        start_time = time.time()
        for _ in range(1000):
            result = sliding_window_data_augmentation(x, window_size)
        end_time = time.time()
        
        # Should handle 1000 augmentations quickly
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001  # Less than 1ms per augmentation
    
    def test_memory_leak_prevention(self):
        """Test that repeated use doesn't cause memory leaks."""
        x = np.random.randn(100, 10000)
        window_size = 1000
        
        gc.collect()
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss
        
        # Perform many augmentations
        for _ in range(10000):
            result = sliding_window_data_augmentation(x, window_size)
            # Simulate some processing
            _ = result.mean()
        
        gc.collect()
        mem_end = process.memory_info().rss
        
        # Memory should not grow significantly
        mem_growth = mem_end - mem_start
        assert mem_growth < 50 * 1024 * 1024  # Less than 50MB growth


class TestSlidingWindowDataAugmentationIntegration:
    """Integration tests with ML workflows."""
    
    def test_training_data_generation(self):
        """Test generating training data for ML model."""
        # Simulate multi-channel time series
        n_samples = 10000
        n_channels = 32
        data = np.random.randn(n_channels, n_samples)
        
        window_size = 256
        n_augmentations = 100
        
        # Generate augmented training set
        training_samples = []
        for _ in range(n_augmentations):
            sample = sliding_window_data_augmentation(data, window_size)
            training_samples.append(sample)
        
        training_data = np.array(training_samples)
        assert training_data.shape == (n_augmentations, n_channels, window_size)
        
        # Verify diversity
        # Check that we're using different parts of the signal
        first_samples = training_data[:, 0, 0]  # First value of first channel
        unique_starts = len(np.unique(first_samples))
        assert unique_starts > n_augmentations * 0.8  # Most should be unique
    
    def test_online_augmentation_generator(self):
        """Test using augmentation in a generator pattern."""
        def data_generator(x, window_size, batch_size=32):
            """Generate batches of augmented data."""
            while True:
                batch = []
                for _ in range(batch_size):
                    sample = sliding_window_data_augmentation(x, window_size)
                    batch.append(sample)
                yield np.array(batch)
        
        # Test data
        data = np.random.randn(10, 5000)
        window_size = 500
        
        # Create generator
        gen = data_generator(data, window_size)
        
        # Get a few batches
        batch1 = next(gen)
        batch2 = next(gen)
        batch3 = next(gen)
        
        assert batch1.shape == (32, 10, 500)
        assert batch2.shape == (32, 10, 500)
        assert batch3.shape == (32, 10, 500)
        
        # Batches should be different
        assert not np.array_equal(batch1, batch2)
        assert not np.array_equal(batch2, batch3)
    
    def test_multi_scale_augmentation(self):
        """Test augmentation with multiple window sizes."""
        x = np.random.randn(8, 10000)
        window_sizes = [100, 200, 500, 1000]
        
        multi_scale_samples = {}
        for size in window_sizes:
            samples = []
            for _ in range(10):
                sample = sliding_window_data_augmentation(x, size)
                samples.append(sample)
            multi_scale_samples[size] = np.array(samples)
        
        # Verify different scales
        for size in window_sizes:
            assert multi_scale_samples[size].shape == (10, 8, size)
        
        # Each scale should have different characteristics
        for i, size1 in enumerate(window_sizes[:-1]):
            size2 = window_sizes[i + 1]
            # Larger windows should have more stable statistics
            std1 = multi_scale_samples[size1].std(axis=-1).mean()
            std2 = multi_scale_samples[size2].std(axis=-1).mean()
            # This is approximate due to randomness
            assert abs(std1 - std2) < 0.5
    
    def test_augmentation_with_labels(self):
        """Test augmentation preserving label correspondence."""
        # Simulate labeled segments
        n_samples = 10000
        n_channels = 16
        data = np.random.randn(n_channels, n_samples)
        
        # Create labels (e.g., 0-3 for different states)
        labels = np.repeat([0, 1, 2, 3], n_samples // 4)
        
        window_size = 200
        
        # Augment with label preservation
        augmented_data = []
        augmented_labels = []
        
        for _ in range(50):
            # Get random start position
            start = random.randint(0, n_samples - window_size)
            
            # Extract window and corresponding labels
            window_data = data[:, start:start + window_size]
            window_labels = labels[start:start + window_size]
            
            # If window spans multiple labels, take majority
            unique, counts = np.unique(window_labels, return_counts=True)
            majority_label = unique[np.argmax(counts)]
            
            augmented_data.append(window_data)
            augmented_labels.append(majority_label)
        
        augmented_data = np.array(augmented_data)
        augmented_labels = np.array(augmented_labels)
        
        assert augmented_data.shape == (50, n_channels, window_size)
        assert augmented_labels.shape == (50,)
        assert np.all(np.isin(augmented_labels, [0, 1, 2, 3]))


class TestSlidingWindowDataAugmentationDocumentation:
    """Test documentation and usage examples."""
    
    def test_function_signature(self):
        """Test function signature and docstring."""
        import inspect
        
        # Check signature
        sig = inspect.signature(sliding_window_data_augmentation)
        params = list(sig.parameters.keys())
        assert params == ['x', 'window_size_pts']
        
        # Check if function has docstring (when implemented)
        # assert sliding_window_data_augmentation.__doc__ is not None
    
    def test_example_eeg_processing(self):
        """Example: EEG signal processing."""
        # Simulate 32-channel EEG at 256 Hz for 10 seconds
        fs = 256  # Hz
        duration = 10  # seconds
        n_channels = 32
        n_samples = fs * duration
        
        # Generate synthetic EEG
        eeg = np.random.randn(n_channels, n_samples)
        
        # Add some structure (alpha rhythm at 10 Hz)
        t = np.linspace(0, duration, n_samples)
        for ch in range(n_channels):
            eeg[ch] += 0.5 * np.sin(2 * np.pi * 10 * t)
        
        # Augment with 1-second windows
        window_samples = int(1.0 * fs)  # 1 second
        
        augmented = sliding_window_data_augmentation(eeg, window_samples)
        assert augmented.shape == (n_channels, window_samples)
    
    def test_example_audio_processing(self):
        """Example: Audio signal processing."""
        # Simulate stereo audio at 44.1 kHz
        fs = 44100  # Hz
        duration = 5  # seconds
        n_channels = 2  # Stereo
        n_samples = fs * duration
        
        # Generate synthetic audio
        audio = np.random.randn(n_channels, n_samples) * 0.1
        
        # Add some tones
        t = np.linspace(0, duration, n_samples)
        audio[0] += 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
        audio[1] += 0.3 * np.sin(2 * np.pi * 554.37 * t)  # C#5 note
        
        # Augment with 0.5-second windows
        window_samples = int(0.5 * fs)
        
        augmented = sliding_window_data_augmentation(audio, window_samples)
        assert augmented.shape == (n_channels, window_samples)
    
    def test_example_sensor_data(self):
        """Example: Multi-sensor time series."""
        # Simulate IoT sensor data
        n_sensors = 5
        n_samples = 100000  # 100k samples
        
        # Different sensors with different characteristics
        sensor_data = np.zeros((n_sensors, n_samples))
        
        # Temperature sensor (slow variation)
        sensor_data[0] = 20 + 5 * np.sin(np.linspace(0, 10, n_samples))
        
        # Vibration sensor (high frequency)
        sensor_data[1] = np.random.randn(n_samples) * 0.1
        
        # Pressure sensor (step changes)
        sensor_data[2] = np.repeat([1, 1.5, 1.2, 0.8], n_samples // 4)
        
        # Humidity sensor (drift)
        sensor_data[3] = 50 + np.linspace(0, 10, n_samples)
        
        # Binary sensor (on/off)
        sensor_data[4] = np.random.randint(0, 2, n_samples)
        
        # Augment with various window sizes
        for window_size in [100, 500, 1000]:
            augmented = sliding_window_data_augmentation(sensor_data, window_size)
            assert augmented.shape == (n_sensors, window_size)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# --------------------------------------------------------------------------------
# Source Code Reference:
# --------------------------------------------------------------------------------
# Function: sliding_window_data_augmentation(x, window_size_pts)
# 
# Parameters:
#   - x: Input array with shape (..., time_dimension)
#   - window_size_pts: Size of the window to extract
# 
# Returns:
#   - Sliced array with shape (..., window_size_pts)
# 
# The function randomly selects a starting position and extracts a window
# of the specified size from the last dimension of the input array.
# --------------------------------------------------------------------------------
