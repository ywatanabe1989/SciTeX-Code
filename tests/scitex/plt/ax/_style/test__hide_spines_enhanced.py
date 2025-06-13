#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:05:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_style/test__hide_spines_enhanced.py
# ----------------------------------------
"""
Enhanced test suite for hide_spines function with advanced testing patterns.

This test suite demonstrates:
- Property-based testing
- Comprehensive fixtures
- Mock usage
- Performance testing
- Edge case handling
- Integration testing
"""

import itertools
from unittest.mock import MagicMock, patch, call

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from hypothesis import given, strategies as st, assume, settings

from scitex.plt.ax._style import hide_spines


# ----------------------------------------
# Fixtures
# ----------------------------------------

@pytest.fixture
def axes_types():
    """Provide different types of axes for testing."""
    axes = {}
    
    # Standard 2D axes
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [1, 2, 3])
    axes['2d'] = (fig1, ax1)
    
    # Multiple subplots
    fig2, axs2 = plt.subplots(2, 2)
    for ax in axs2.flat:
        ax.plot(np.random.rand(10))
    axes['subplots'] = (fig2, axs2)
    
    # Different plot types
    fig3, ax3 = plt.subplots()
    ax3.scatter(np.random.rand(20), np.random.rand(20))
    axes['scatter'] = (fig3, ax3)
    
    fig4, ax4 = plt.subplots()
    ax4.bar(['A', 'B', 'C'], [1, 2, 3])
    axes['bar'] = (fig4, ax4)
    
    yield axes
    
    # Cleanup
    for fig, _ in axes.values():
        if isinstance(fig, plt.Figure):
            plt.close(fig)


@pytest.fixture
def spine_states():
    """Provide different spine visibility states for testing."""
    return [
        {'top': True, 'bottom': True, 'left': True, 'right': True},
        {'top': False, 'bottom': False, 'left': False, 'right': False},
        {'top': True, 'bottom': False, 'left': True, 'right': False},
        {'top': False, 'bottom': True, 'left': False, 'right': True},
    ]


# ----------------------------------------
# Basic Functionality Tests
# ----------------------------------------

class TestBasicFunctionality:
    """Test basic hide_spines functionality."""
    
    def test_hide_all_spines_default(self, fig_ax):
        """Test hiding all spines with default parameters."""
        fig, ax = fig_ax
        result = hide_spines(ax)
        
        # Check return value
        assert result is ax
        
        # Check all spines are hidden
        for spine in ['top', 'bottom', 'left', 'right']:
            assert not ax.spines[spine].get_visible()
            
        # Check ticks and labels are removed
        assert ax.xaxis.get_ticks_position() == 'none'
        assert ax.yaxis.get_ticks_position() == 'none'
        assert all(label.get_text() == '' for label in ax.get_xticklabels())
        assert all(label.get_text() == '' for label in ax.get_yticklabels())
        
    def test_hide_specific_spines(self, fig_ax):
        """Test hiding only specific spines."""
        fig, ax = fig_ax
        
        # Hide only top and right
        result = hide_spines(ax, top=True, bottom=False, left=False, right=True)
        
        assert not ax.spines['top'].get_visible()
        assert ax.spines['bottom'].get_visible()
        assert ax.spines['left'].get_visible()
        assert not ax.spines['right'].get_visible()
        
    def test_keep_ticks_and_labels(self, fig_ax):
        """Test keeping ticks and labels while hiding spines."""
        fig, ax = fig_ax
        
        # Set some labels to verify they're preserved
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['A', 'B', 'C'])
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['X', 'Y', 'Z'])
        
        hide_spines(ax, ticks=False, labels=False)
        
        # Spines should be hidden
        for spine in ['top', 'bottom', 'left', 'right']:
            assert not ax.spines[spine].get_visible()
            
        # But ticks and labels should remain
        fig.canvas.draw()
        assert ax.xaxis.get_ticks_position() != 'none'
        assert ax.yaxis.get_ticks_position() != 'none'
        assert [label.get_text() for label in ax.get_xticklabels()] == ['A', 'B', 'C']
        assert [label.get_text() for label in ax.get_yticklabels()] == ['X', 'Y', 'Z']


# ----------------------------------------
# Parametrized Tests
# ----------------------------------------

class TestParametrized:
    """Parametrized tests for comprehensive coverage."""
    
    @pytest.mark.parametrize("spine_config", [
        {'top': True, 'bottom': True, 'left': True, 'right': True},
        {'top': False, 'bottom': False, 'left': False, 'right': False},
        {'top': True, 'bottom': False, 'left': True, 'right': False},
        {'top': False, 'bottom': True, 'left': False, 'right': True},
    ])
    def test_spine_combinations(self, fig_ax, spine_config):
        """Test various spine visibility combinations."""
        fig, ax = fig_ax
        hide_spines(ax, **spine_config)
        
        for spine, should_hide in spine_config.items():
            if should_hide:
                assert not ax.spines[spine].get_visible()
            else:
                assert ax.spines[spine].get_visible()
                
    @pytest.mark.parametrize("ticks,labels", [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_ticks_labels_combinations(self, fig_ax, ticks, labels):
        """Test various combinations of tick and label visibility."""
        fig, ax = fig_ax
        
        # Set labels for testing
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['A', 'B', 'C'])
        
        hide_spines(ax, bottom=True, left=True, ticks=ticks, labels=labels)
        
        fig.canvas.draw()
        
        if ticks:
            assert ax.xaxis.get_ticks_position() == 'none'
            assert ax.yaxis.get_ticks_position() == 'none'
            
        if labels:
            assert all(label.get_text() == '' for label in ax.get_xticklabels())
            assert all(label.get_text() == '' for label in ax.get_yticklabels())


# ----------------------------------------
# Property-Based Tests
# ----------------------------------------

class TestPropertyBased:
    """Property-based tests using Hypothesis."""
    
    @given(
        top=st.booleans(),
        bottom=st.booleans(),
        left=st.booleans(),
        right=st.booleans(),
        ticks=st.booleans(),
        labels=st.booleans()
    )
    @settings(max_examples=50, deadline=1000)
    def test_arbitrary_configurations(self, top, bottom, left, right, ticks, labels):
        """Test with arbitrary valid configurations."""
        fig, ax = plt.subplots()
        
        try:
            result = hide_spines(
                ax, 
                top=top, bottom=bottom, 
                left=left, right=right,
                ticks=ticks, labels=labels
            )
            
            # Basic invariants
            assert result is ax
            assert isinstance(ax, matplotlib.axes.Axes)
            
            # Check spine states
            if top:
                assert not ax.spines['top'].get_visible()
            if bottom:
                assert not ax.spines['bottom'].get_visible()
            if left:
                assert not ax.spines['left'].get_visible()
            if right:
                assert not ax.spines['right'].get_visible()
                
        finally:
            plt.close(fig)
            
    @given(st.lists(st.sampled_from(['top', 'bottom', 'left', 'right']), min_size=0, max_size=4))
    def test_spine_list_property(self, spines_to_hide):
        """Test hiding arbitrary lists of spines."""
        fig, ax = plt.subplots()
        
        try:
            # Convert list to kwargs
            kwargs = {spine: (spine in spines_to_hide) for spine in ['top', 'bottom', 'left', 'right']}
            
            hide_spines(ax, **kwargs)
            
            # Verify
            for spine in ['top', 'bottom', 'left', 'right']:
                if spine in spines_to_hide:
                    assert not ax.spines[spine].get_visible()
                else:
                    assert ax.spines[spine].get_visible()
                    
        finally:
            plt.close(fig)


# ----------------------------------------
# Edge Cases and Error Handling
# ----------------------------------------

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_axes_type(self):
        """Test with invalid axes type."""
        with pytest.raises(AssertionError, match="must be a matplotlib axis"):
            hide_spines("not_an_axes")
            
        with pytest.raises(AssertionError):
            hide_spines(None)
            
        with pytest.raises(AssertionError):
            hide_spines(plt.figure())
            
    def test_already_hidden_spines(self, fig_ax):
        """Test hiding already hidden spines."""
        fig, ax = fig_ax
        
        # Hide spines first time
        hide_spines(ax)
        
        # Hide again - should not raise error
        result = hide_spines(ax)
        assert result is ax
        
        # All spines should still be hidden
        for spine in ax.spines.values():
            assert not spine.get_visible()
            
    def test_with_shared_axes(self):
        """Test with shared axes."""
        fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)
        
        try:
            # Hide spines on first axes
            hide_spines(ax1, bottom=True, left=True)
            
            # Should not affect second axes
            assert ax2.spines['bottom'].get_visible()
            assert ax2.spines['left'].get_visible()
            
        finally:
            plt.close(fig)
            
    def test_with_twin_axes(self, fig_ax):
        """Test with twin axes."""
        fig, ax1 = fig_ax
        ax2 = ax1.twinx()
        
        # Hide spines on original axes
        hide_spines(ax1, right=True)
        
        # Twin axes should not be affected
        assert ax2.spines['right'].get_visible()


# ----------------------------------------
# Mock Tests
# ----------------------------------------

class TestMocking:
    """Tests using mocks to verify internal behavior."""
    
    def test_spine_set_visible_calls(self, fig_ax):
        """Test that set_visible is called correctly on spines."""
        fig, ax = fig_ax
        
        # Mock all spines
        for spine_name in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine_name].set_visible = MagicMock()
            
        hide_spines(ax, top=True, bottom=False, left=True, right=False)
        
        # Verify calls
        ax.spines['top'].set_visible.assert_called_once_with(False)
        ax.spines['bottom'].set_visible.assert_not_called()
        ax.spines['left'].set_visible.assert_called_once_with(False)
        ax.spines['right'].set_visible.assert_not_called()
        
    @patch('matplotlib.axes.Axes.set_xticklabels')
    @patch('matplotlib.axes.Axes.set_yticklabels')
    def test_label_removal_calls(self, mock_set_y, mock_set_x, fig_ax):
        """Test that label removal methods are called correctly."""
        fig, ax = fig_ax
        
        hide_spines(ax, bottom=True, left=True, labels=True)
        
        mock_set_x.assert_called_once_with([])
        mock_set_y.assert_called_once_with([])
        
    def test_tick_position_calls(self, fig_ax):
        """Test tick position setting."""
        fig, ax = fig_ax
        
        ax.xaxis.set_ticks_position = MagicMock()
        ax.yaxis.set_ticks_position = MagicMock()
        
        hide_spines(ax, bottom=True, left=True, ticks=True)
        
        ax.xaxis.set_ticks_position.assert_called_once_with('none')
        ax.yaxis.set_ticks_position.assert_called_once_with('none')


# ----------------------------------------
# Performance Tests
# ----------------------------------------

class TestPerformance:
    """Test performance characteristics."""
    
    def test_multiple_axes_performance(self, performance_monitor):
        """Test performance with multiple axes."""
        n_axes = 100
        fig, axes = plt.subplots(10, 10, figsize=(20, 20))
        
        try:
            with performance_monitor.measure('hide_all'):
                for ax in axes.flat:
                    hide_spines(ax)
                    
            performance_monitor.assert_performance(
                'hide_all',
                max_duration=1.0,  # Should complete in under 1 second
                max_memory=10 * 1024 * 1024  # Less than 10MB
            )
        finally:
            plt.close(fig)
            
    def test_repeated_calls_performance(self, fig_ax, performance_monitor):
        """Test performance of repeated calls on same axes."""
        fig, ax = fig_ax
        
        with performance_monitor.measure('repeated_calls'):
            for _ in range(100):
                hide_spines(ax, top=True, bottom=False, left=True, right=False)
                
        performance_monitor.assert_performance(
            'repeated_calls',
            max_duration=0.1  # Very fast for repeated calls
        )


# ----------------------------------------
# Integration Tests
# ----------------------------------------

class TestIntegration:
    """Test integration with other plotting functions."""
    
    def test_with_different_plot_types(self, axes_types):
        """Test with various plot types."""
        for plot_type, (fig, ax) in axes_types.items():
            if isinstance(ax, np.ndarray):
                # Test on first subplot
                ax = ax.flat[0]
                
            hide_spines(ax)
            
            # Should work regardless of plot type
            for spine in ax.spines.values():
                assert not spine.get_visible()
                
    def test_with_scitex_plotting_wrapper(self):
        """Test integration with scitex plotting wrapper."""
        try:
            from scitex.plt import subplots
            
            fig, ax = subplots(1, 1)
            ax.plot([1, 2, 3], [1, 2, 3])
            
            # Should work with wrapped axes
            result = hide_spines(ax)
            
            # Verify it worked
            for spine in ['top', 'bottom', 'left', 'right']:
                assert not ax.spines[spine].get_visible()
                
            plt.close(fig)
            
        except ImportError:
            pytest.skip("scitex.plt not available")
            
    def test_save_after_hiding_spines(self, fig_ax, tmp_path):
        """Test saving figure after hiding spines."""
        fig, ax = fig_ax
        ax.plot([1, 2, 3], [1, 2, 3])
        
        hide_spines(ax, top=True, right=True)
        
        # Save figure
        output_path = tmp_path / "test_hidden_spines.png"
        fig.savefig(output_path)
        
        assert output_path.exists()
        assert output_path.stat().st_size > 0


# ----------------------------------------
# Visual Behavior Tests
# ----------------------------------------

class TestVisualBehavior:
    """Test visual aspects and behavior."""
    
    def test_spine_line_properties_preserved(self, fig_ax):
        """Test that other spine properties are preserved."""
        fig, ax = fig_ax
        
        # Set custom spine properties
        ax.spines['bottom'].set_linewidth(3)
        ax.spines['bottom'].set_linestyle('--')
        ax.spines['bottom'].set_color('red')
        
        # Hide top spine only
        hide_spines(ax, top=True, bottom=False, left=False, right=False)
        
        # Bottom spine properties should be preserved
        assert ax.spines['bottom'].get_linewidth() == 3
        assert ax.spines['bottom'].get_linestyle() == '--'
        assert ax.spines['bottom'].get_color() == 'red'
        
    def test_with_custom_tick_positions(self, fig_ax):
        """Test interaction with custom tick positions."""
        fig, ax = fig_ax
        
        # Set custom tick positions
        ax.xaxis.set_ticks_position('top')
        ax.yaxis.set_ticks_position('right')
        
        # Hide bottom and left spines
        hide_spines(ax, bottom=True, left=True, ticks=False)
        
        # Custom positions should be preserved
        assert ax.xaxis.get_ticks_position() == 'top'
        assert ax.yaxis.get_ticks_position() == 'right'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])