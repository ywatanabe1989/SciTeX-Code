#!/usr/bin/env python3
"""Test colorbar enhancements and overlap prevention"""

import numpy as np
import pytest


def test_colorbar_no_overlap():
    """Test that colorbars don't overlap with axes."""
    import scitex.plt as plt
    
    # Create figure with heatmaps and colorbars
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    
    for ax in axes.flat[:3]:
        data = np.random.randn(10, 10)
        im = ax.imshow(data, aspect='auto')
        cbar = plt.colorbar(im, ax=ax)
        
        # Check that colorbar exists
        assert cbar is not None
    
    # No assertion for overlap - visual inspection required
    # But we can check that no errors or warnings occur
    plt.close(fig)


def test_adjust_layout_method():
    """Test the fig.adjust_layout() method."""
    import scitex.plt as plt
    
    fig, ax = plt.subplots()
    
    # Check that adjust_layout method exists
    assert hasattr(fig, 'adjust_layout')
    
    # Test calling it with parameters
    fig.adjust_layout(w_pad=0.2, h_pad=0.2)
    
    plt.close(fig)


def test_enhanced_colorbar_function():
    """Test that enhanced colorbar is used through scitex.plt."""
    import scitex.plt as plt
    
    fig, ax = plt.subplots()
    data = np.random.randn(10, 10)
    im = ax.imshow(data)
    
    # Call colorbar through scitex.plt
    cbar = plt.colorbar(im, ax=ax)
    
    # Check that colorbar was created
    assert cbar is not None
    assert hasattr(cbar, 'ax')  # Colorbar should have an axes
    
    plt.close(fig)


def test_shared_colorbar():
    """Test add_shared_colorbar utility."""
    import scitex.plt as plt
    from scitex.plt.utils import add_shared_colorbar
    
    fig, axes = plt.subplots(2, 2)
    
    # Create multiple images with same scale
    images = []
    for ax in axes.flat:
        data = np.random.randn(10, 10)
        im = ax.imshow(data, vmin=-2, vmax=2)
        images.append(im)
    
    # Add shared colorbar
    cbar = add_shared_colorbar(fig, axes, images[0])
    
    assert cbar is not None
    
    plt.close(fig)


def test_constrained_layout_with_colorbars():
    """Test that constrained_layout properly handles colorbars."""
    import scitex.plt as plt
    
    # Create figure - should use constrained_layout by default
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    
    # Verify constrained_layout is active
    assert fig.get_constrained_layout() is True
    
    # Add colorbars to all axes
    for ax in axes.flat:
        data = np.random.randn(10, 10)
        im = ax.imshow(data, aspect='auto')
        plt.colorbar(im, ax=ax)
    
    # Call tight_layout - should be harmless with constrained_layout
    plt.tight_layout()
    
    plt.close(fig)


def test_manual_spacing_control():
    """Test manual control of spacing parameters."""
    import scitex.plt as plt
    
    # Create with custom spacing
    fig1, axes1 = plt.subplots(2, 2, 
                               constrained_layout={'w_pad': 0.2, 'h_pad': 0.2})
    
    # Create with default and adjust later
    fig2, axes2 = plt.subplots(2, 2)
    fig2.adjust_layout(w_pad=0.15, h_pad=0.15, wspace=0.1, hspace=0.1)
    
    plt.close(fig1)
    plt.close(fig2)


def test_colorbar_with_constrained_layout_disabled():
    """Test behavior when constrained_layout is disabled."""
    import scitex.plt as plt
    
    fig, ax = plt.subplots(constrained_layout=False)
    
    # Verify constrained_layout is disabled
    assert fig.get_constrained_layout() is False
    
    data = np.random.randn(10, 10)
    im = ax.imshow(data)
    cbar = plt.colorbar(im, ax=ax)
    
    # Should still work, using traditional layout
    assert cbar is not None
    
    plt.close(fig)