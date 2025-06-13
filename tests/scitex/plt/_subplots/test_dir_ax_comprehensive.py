#!/usr/bin/env python3
"""Comprehensive test for dir(ax) functionality"""

import pytest
import scitex.plt


def test_dir_ax_single_subplot():
    """Test that dir(ax) works correctly for single subplot"""
    fig, ax = scitex.plt.subplots()
    
    # Should not raise exception
    attrs = dir(ax)
    assert isinstance(attrs, list)
    assert len(attrs) > 50  # Should have many attributes
    
    # Check for matplotlib methods
    matplotlib_methods = [
        'plot', 'scatter', 'bar', 'barh', 'hist', 'boxplot',
        'set_xlabel', 'set_ylabel', 'set_title', 'legend',
        'set_xlim', 'set_ylim', 'grid', 'annotate', 'text'
    ]
    for method in matplotlib_methods:
        assert method in attrs, f"Missing matplotlib method: {method}"
    
    # Check for seaborn methods
    seaborn_methods = [
        'sns_barplot', 'sns_boxplot', 'sns_heatmap', 'sns_histplot',
        'sns_kdeplot', 'sns_scatterplot', 'sns_violinplot'
    ]
    for method in seaborn_methods:
        assert method in attrs, f"Missing seaborn method: {method}"
    
    # Check for custom scitex methods
    custom_methods = [
        'set_xyt', 'hide_spines', 'rotate_labels', 'set_n_ticks',
        'export_as_csv', 'plot_kde', 'plot_raster'
    ]
    for method in custom_methods:
        assert method in attrs, f"Missing custom method: {method}"


def test_dir_ax_multiple_subplots():
    """Test that dir(ax) works correctly for multiple subplots"""
    fig, axes = scitex.plt.subplots(2, 2)
    
    # Test on the axes array itself
    axes_attrs = dir(axes)
    assert isinstance(axes_attrs, list)
    assert 'shape' in axes_attrs
    assert 'flat' in axes_attrs
    
    # Test on individual axis
    ax = axes[0, 0]
    attrs = dir(ax)
    assert isinstance(attrs, list)
    assert len(attrs) > 50
    
    # Should have same methods as single subplot
    assert 'plot' in attrs
    assert 'sns_barplot' in attrs
    assert 'set_xyt' in attrs


def test_dir_does_not_include_private_attributes():
    """Test that dir(ax) filters out private attributes"""
    fig, ax = scitex.plt.subplots()
    attrs = dir(ax)
    
    # Should not include private attributes
    private_attrs = [attr for attr in attrs if attr.startswith('_')]
    assert len(private_attrs) == 0, f"Found private attributes: {private_attrs[:5]}"


def test_callable_methods_are_actually_callable():
    """Test that methods shown in dir(ax) are actually callable"""
    fig, ax = scitex.plt.subplots()
    attrs = dir(ax)
    
    # Check some key methods are callable
    test_methods = ['plot', 'scatter', 'sns_barplot', 'set_xyt']
    for method_name in test_methods:
        if method_name in attrs:
            method = getattr(ax, method_name)
            assert callable(method), f"{method_name} is not callable"


def test_dir_consistency():
    """Test that dir(ax) returns consistent results"""
    fig, ax = scitex.plt.subplots()
    
    # Multiple calls should return the same result
    attrs1 = dir(ax)
    attrs2 = dir(ax)
    
    assert attrs1 == attrs2, "dir(ax) returns different results on multiple calls"


def test_axes_wrapper_dir():
    """Test dir() on AxesWrapper for multiple subplots"""
    fig, axes = scitex.plt.subplots(2, 2)
    
    # dir(axes) should work
    attrs = dir(axes)
    assert isinstance(attrs, list)
    
    # Should include array-like methods
    assert 'shape' in attrs
    assert 'flat' in attrs
    assert 'flatten' in attrs
    
    # Should include methods from individual axes
    assert 'plot' in attrs
    assert 'sns_barplot' in attrs


def test_no_sns_plot_method():
    """Verify there's no generic sns_plot method"""
    fig, ax = scitex.plt.subplots()
    attrs = dir(ax)
    
    # There should be no sns_plot method
    assert 'sns_plot' not in attrs
    
    # But specific seaborn methods should exist
    assert any(attr.startswith('sns_') for attr in attrs)