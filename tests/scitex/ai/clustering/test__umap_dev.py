#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 17:05:00 (ywatanabe)"
# File: ./tests/scitex/ai/clustering/test__umap_dev.py

import numpy as np
import pytest
from unittest.mock import Mock, patch, MagicMock
import matplotlib.pyplot as plt


def test_umap_basic_functionality():
    """Test basic UMAP functionality with minimal parameters."""
from scitex.ai.clustering import umap
    
    # Generate sample data
    np.random.seed(42)
    data = [np.random.randn(100, 10)]
    labels = [np.random.randint(0, 3, 100)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(100, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(data, labels)
            
            assert isinstance(result, tuple)
            assert len(result) == 3  # fig, legend_figs, umap_model
            mock_umap_class.assert_called_once_with(random_state=42)


def test_umap_supervised_mode():
    """Test supervised UMAP clustering."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(50, 5)]
    labels = [np.random.randint(0, 2, 50)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(50, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(data, labels, supervised=True)
            
            # Verify supervised fit was called with labels
            mock_umap.fit.assert_called_once()
            call_args = mock_umap.fit.call_args
            assert call_args[1]['y'] is not None  # y parameter should be provided


def test_umap_unsupervised_mode():
    """Test unsupervised UMAP clustering."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(50, 5)]
    labels = [np.random.randint(0, 2, 50)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(50, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(data, labels, supervised=False)
            
            # Verify unsupervised fit was called without labels
            mock_umap.fit.assert_called_once()
            call_args = mock_umap.fit.call_args
            assert call_args[1]['y'] is None  # y parameter should be None


def test_umap_with_hues():
    """Test UMAP with custom hue coloring."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(30, 8)]
    labels = [np.random.randint(0, 3, 30)]
    hues = [np.random.choice(['A', 'B', 'C'], 30)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(30, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(data, labels, hues=hues)
            
            assert isinstance(result, tuple)
            assert len(result) == 3


def test_umap_with_colors():
    """Test UMAP with custom color mapping."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(30, 8)]
    labels = [np.random.randint(0, 3, 30)]
    colors = [np.random.rand(30, 3).tolist()]  # RGB colors as list
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(30, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(data, labels, hues_colors=colors)
            
            assert isinstance(result, tuple)


def test_umap_with_existing_axes():
    """Test UMAP plotting on existing axes."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(50, 10)]
    labels = [np.random.randint(0, 2, 50)]
    
    # For existing axes test, use a single axis wrapped to handle both axis and array behavior
    mock_ax = Mock()
    mock_fig = Mock()
    mock_ax.get_figure.return_value = mock_fig
    mock_ax.flat = [mock_ax]
    # Add methods that make it work like both single axis and array
    mock_ax.__len__ = lambda self: 1
    mock_ax.__iter__ = lambda self: iter([mock_ax])
    mock_ax.__getitem__ = lambda self, key: mock_ax  # For indexing
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(50, 2)
        mock_umap_class.return_value = mock_umap
        
        result = umap(data, labels, axes=mock_ax)
        
        assert isinstance(result, tuple)
        # Should use existing axes instead of creating new ones


def test_umap_with_pretrained_model():
    """Test UMAP with pre-fitted model."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(40, 6)]
    labels = [np.random.randint(0, 4, 40)]
    
    # Mock pre-trained model
    mock_pretrained = Mock()
    mock_pretrained.transform.return_value = np.random.randn(40, 2)
    
    with patch('scitex.plt.subplots') as mock_subplots:
        mock_fig = Mock()
        mock_ax = Mock()
        mock_axes = Mock()
        mock_axes.flat = [mock_ax]
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        result = umap(data, labels, umap_model=mock_pretrained)
        
        # Should use pre-trained model instead of creating new one
        mock_pretrained.transform.assert_called()
        assert result[2] == mock_pretrained


def test_umap_multiple_datasets():
    """Test UMAP with multiple datasets."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(30, 5), np.random.randn(40, 5)]
    labels = [np.random.randint(0, 2, 30), np.random.randint(0, 2, 40)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.side_effect = [
            np.random.randn(30, 2), 
            np.random.randn(40, 2)
        ]
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax1, mock_ax2 = Mock(), Mock()
            # Configure axis mock methods for sharing functionality
            mock_ax1.get_xlim.return_value = (0, 1)
            mock_ax1.get_ylim.return_value = (0, 1)
            mock_ax2.get_xlim.return_value = (0, 1)
            mock_ax2.get_ylim.return_value = (0, 1)
            mock_axes = np.array([mock_ax1, mock_ax2])  # Use numpy array for multiple axes
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            result = umap(data, labels)
            
            # Should call transform for each dataset
            assert mock_umap.transform.call_count == 2


def test_umap_superimposed_plot():
    """Test UMAP with superimposed plotting."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(30, 5), np.random.randn(40, 5)]
    labels = [np.random.randint(0, 2, 30), np.random.randint(0, 2, 40)]
    colors = [np.random.rand(30, 3).tolist(), np.random.rand(40, 3).tolist()]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.side_effect = [
            np.random.randn(30, 2), 
            np.random.randn(40, 2)
        ]
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax1, mock_ax2, mock_ax3 = Mock(), Mock(), Mock()
            # Configure axis mock methods for sharing functionality
            for ax in [mock_ax1, mock_ax2, mock_ax3]:
                ax.get_xlim.return_value = (0, 1)
                ax.get_ylim.return_value = (0, 1)
            mock_axes = np.array([mock_ax1, mock_ax2, mock_ax3])  # Use numpy array for multiple axes
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            result = umap(data, labels, hues_colors=colors, add_super_imposed=True)
            
            assert isinstance(result, tuple)


def test_umap_independent_legend():
    """Test UMAP with independent legend creation."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(25, 4)]
    labels = [np.random.randint(0, 3, 25)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(25, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.figure') as mock_figure:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat for legend processing
            mock_ax.__iter__ = lambda self: iter([mock_ax])  # Make single axis iterable for legend processing
            mock_legend = Mock()
            mock_legend.get_lines.return_value = []
            mock_legend.texts = []
            mock_ax.get_legend.return_value = mock_legend
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_figure.return_value = Mock()
            
            result = umap(data, labels, use_independent_legend=True)
            
            assert isinstance(result, tuple)
            assert len(result) == 3


def test_umap_visualization_parameters():
    """Test UMAP with custom visualization parameters."""
from scitex.ai.clustering import umap
    
    np.random.seed(42)
    data = [np.random.randn(20, 3)]
    labels = [np.random.randint(0, 2, 20)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap.transform.return_value = np.random.randn(20, 2)
        mock_umap_class.return_value = mock_umap
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.flat = [mock_ax]  # Add flat attribute to single axis for legend processing
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            result = umap(
                data, 
                labels, 
                title="Custom Title",
                alpha=0.5,
                s=10,
                axes_titles=["Custom Axis Title"]
            )
            
            assert isinstance(result, tuple)


def test_check_input_vars():
    """Test input validation function."""
from scitex.ai.clustering import _check_input_vars
    
    data_all = [np.random.randn(10, 5)]
    labels_all = [np.random.randint(0, 2, 10)]
    
    # Test with None values
    result = _check_input_vars(data_all, labels_all, None, None)
    assert len(result) == 4
    assert result[2] == [None]  # hues_all
    assert result[3] == [None]  # hues_colors_all
    
    # Test with provided values
    hues_all = [np.random.choice(['A', 'B'], 10)]
    hues_colors_all = [np.random.rand(10, 3)]
    
    result = _check_input_vars(data_all, labels_all, hues_all, hues_colors_all)
    assert len(result) == 4
    assert result[2] == hues_all
    assert result[3] == hues_colors_all


def test_check_input_vars_validation():
    """Test input validation with mismatched lengths."""
from scitex.ai.clustering import _check_input_vars
    
    data_all = [np.random.randn(10, 5)]
    labels_all = [np.random.randint(0, 2, 10)]
    hues_all = [None, None]  # Wrong length
    hues_colors_all = [None]
    
    with pytest.raises(AssertionError):
        _check_input_vars(data_all, labels_all, hues_all, hues_colors_all)


def test_check_input_vars_type_validation():
    """Test input validation with wrong types."""
from scitex.ai.clustering import _check_input_vars
    
    data_all = np.random.randn(10, 5)  # Not a list
    labels_all = [np.random.randint(0, 2, 10)]
    
    with pytest.raises(AssertionError):
        _check_input_vars(data_all, labels_all, None, None)


def test_run_umap_new_model():
    """Test _run_umap with new model creation."""
from scitex.ai.clustering import _run_umap
    
    data_all = [np.random.randn(30, 5)]
    labels_all = [np.random.randint(0, 3, 30)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap_class.return_value = mock_umap
        
        result = _run_umap(None, data_all, labels_all, False, "Test")
        
        assert result == mock_umap
        mock_umap_class.assert_called_once_with(random_state=42)
        mock_umap.fit.assert_called_once_with(data_all[0], y=None)


def test_run_umap_supervised():
    """Test _run_umap with supervised learning."""
from scitex.ai.clustering import _run_umap
    
    data_all = [np.random.randn(30, 5)]
    labels_all = [np.random.randint(0, 3, 30)]
    
    with patch('scitex.ai.clustering._umap.umap_orig.UMAP') as mock_umap_class:
        mock_umap = Mock()
        mock_umap.fit.return_value = mock_umap
        mock_umap_class.return_value = mock_umap
        
        result = _run_umap(None, data_all, labels_all, True, "Test")
        
        mock_umap.fit.assert_called_once_with(data_all[0], y=labels_all[0])


def test_run_umap_existing_model():
    """Test _run_umap with existing model."""
from scitex.ai.clustering import _run_umap
    
    data_all = [np.random.randn(30, 5)]
    labels_all = [np.random.randint(0, 3, 30)]
    existing_model = Mock()
    
    result = _run_umap(existing_model, data_all, labels_all, False, "Test")
    
    assert result == existing_model


def test_test_function_iris():
    """Test the _test function with iris dataset."""
from scitex.ai.clustering import _test
    
    with patch('scitex.ai.clustering._umap.umap') as mock_umap, \
         patch('sklearn.datasets.load_iris') as mock_load_iris, \
         patch('scitex.io.save') as mock_save:
        
        # Mock iris dataset
        mock_dataset = Mock()
        mock_dataset.data = np.random.randn(150, 4)
        mock_dataset.target = np.random.randint(0, 3, 150)
        mock_load_iris.return_value = mock_dataset
        
        # Mock umap return values
        mock_fig = Mock()
        mock_legend_figs = [Mock()]
        mock_model = Mock()
        mock_umap.return_value = (mock_fig, mock_legend_figs, mock_model)
        
        _test("iris")
        
        mock_umap.assert_called_once()
        mock_save.assert_called()  # Should save the figure


def test_test_function_mnist():
    """Test the _test function with MNIST dataset."""
from scitex.ai.clustering import _test
    
    with patch('scitex.ai.clustering._umap.umap') as mock_umap, \
         patch('sklearn.datasets.load_digits') as mock_load_digits, \
         patch('scitex.io.save') as mock_save:
        
        # Mock MNIST dataset
        mock_dataset = Mock()
        mock_dataset.data = np.random.randn(1797, 64)
        mock_dataset.target = np.random.randint(0, 10, 1797)
        mock_load_digits.return_value = mock_dataset
        
        # Mock umap return values
        mock_fig = Mock()
        mock_legend_figs = [Mock(), Mock()]
        mock_model = Mock()
        mock_umap.return_value = (mock_fig, mock_legend_figs, mock_model)
        
        _test("mnist")
        
        mock_umap.assert_called_once()
        # Should save main figure and legend figures
        assert mock_save.call_count >= 2


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
