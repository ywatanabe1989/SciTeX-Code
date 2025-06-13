#!/usr/bin/env python3
"""Test tight_layout compatibility and warning suppression"""

import numpy as np
import pytest
import warnings


def test_tight_layout_with_colorbars():
    """Test that tight_layout works without warnings when colorbars are present."""
    import scitex.plt as plt
    
    # Create figure with subplots (now uses constrained_layout by default)
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    data = np.random.randn(10, 10)
    
    # Add plots with colorbars
    for ax in axes.flat:
        im = ax.imshow(data, aspect='auto')
        plt.colorbar(im, ax=ax)
    
    # Test that no warning is raised
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plt.tight_layout()
        
        # Check no warning about incompatible axes
        incompatible_warnings = [warning for warning in w 
                               if "not compatible with tight_layout" in str(warning.message)]
        assert len(incompatible_warnings) == 0, "tight_layout warning was not suppressed"
    
    plt.close(fig)


def test_constrained_layout_default():
    """Test that scitex.plt.subplots uses constrained_layout by default."""
    import scitex.plt as plt
    
    # Create figure with default settings
    fig, ax = plt.subplots()
    
    # Check that constrained_layout is enabled
    assert fig.get_constrained_layout() is True, "constrained_layout should be enabled by default"
    
    plt.close(fig)
    
    
def test_constrained_layout_override():
    """Test that constrained_layout can be overridden."""
    import scitex.plt as plt
    
    # Create figure with constrained_layout explicitly disabled
    fig1, ax1 = plt.subplots(constrained_layout=False)
    assert fig1.get_constrained_layout() is False, "constrained_layout should be disabled"
    
    # Create figure with tight_layout instead
    fig2, ax2 = plt.subplots(layout='tight')
    assert fig2.get_constrained_layout() is False, "constrained_layout should be disabled when layout='tight'"
    
    plt.close(fig1)
    plt.close(fig2)


def test_fig_tight_layout_with_colorbars():
    """Test that fig.tight_layout() works without warnings."""
    import scitex.plt as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    data = np.random.randn(10, 10)
    
    # Add plots with colorbars
    for ax in axes.flat:
        im = ax.imshow(data, aspect='auto')
        plt.colorbar(im, ax=ax)
    
    # Test that no warning is raised
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fig.tight_layout()
        
        # Check no warning about incompatible axes
        incompatible_warnings = [warning for warning in w 
                               if "not compatible with tight_layout" in str(warning.message)]
        assert len(incompatible_warnings) == 0, "fig.tight_layout() warning was not suppressed"
    
    plt.close(fig)


def test_tight_layout_parameters():
    """Test tight_layout with various parameters."""
    import scitex.plt as plt
    
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    
    # Test with different parameters
    plt.tight_layout(pad=1.5)
    plt.tight_layout(h_pad=2.0, w_pad=2.0)
    
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    plt.close(fig)


def test_tight_layout_compatibility():
    """Test that scitex.plt.tight_layout behaves like matplotlib.pyplot.tight_layout."""
    import scitex.plt as mplt
    import matplotlib.pyplot as plt
    
    # Verify tight_layout is accessible
    assert hasattr(mplt, 'tight_layout')
    assert callable(mplt.tight_layout)
    
    # Create identical figures
    fig1, ax1 = mplt.subplots()
    ax1.plot([1, 2, 3], [1, 2, 3])
    
    fig2, ax2 = plt.subplots()
    ax2.plot([1, 2, 3], [1, 2, 3])
    
    # Both should work without errors
    mplt.tight_layout()
    plt.tight_layout()
    
    mplt.close(fig1)
    plt.close(fig2)


def test_matplotlib_pyplot_tight_layout_patched():
    """Test that matplotlib.pyplot.tight_layout is patched when scitex.plt is imported."""
    import scitex.plt  # This should patch matplotlib.pyplot.tight_layout
    import matplotlib.pyplot as plt
    import warnings
    
    # Create figure with scitex.plt but use matplotlib.pyplot for everything else
    fig, axes = scitex.plt.subplots(2, 2, figsize=(8, 6))
    data = np.random.randn(10, 10)
    
    # Add plots with colorbars using matplotlib.pyplot
    for ax in axes.flat:
        im = ax.imshow(data, aspect='auto')
        plt.colorbar(im, ax=ax)
    
    # Test that matplotlib.pyplot.tight_layout doesn't raise warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plt.tight_layout()  # Using matplotlib.pyplot.tight_layout
        
        # Check no warning about incompatible axes
        incompatible_warnings = [warning for warning in w 
                               if "not compatible with tight_layout" in str(warning.message)]
        assert len(incompatible_warnings) == 0, "matplotlib.pyplot.tight_layout warning was not suppressed"
    
    plt.close(fig)