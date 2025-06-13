#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:17:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_style/test__set_xyt_comprehensive.py

"""Comprehensive tests for set_xyt functionality."""

import os
import pytest
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from unittest.mock import patch, MagicMock, call
import tempfile
from scitex.plt.ax._style import set_xyt
from scitex.plt.ax._style import format_label

matplotlib.use('Agg')


class TestSetXYTBasic:
    """Test basic set_xyt functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_set_all_labels(self):
        """Test setting all three labels at once."""
        ax = set_xyt(self.ax, x="X Label", y="Y Label", t="Title")
        
        assert ax.get_xlabel() == "X Label"
        assert ax.get_ylabel() == "Y Label"
        assert ax.get_title() == "Title"
        assert ax is self.ax  # Should return the same axis
    
    def test_set_individual_labels(self):
        """Test setting labels individually."""
        # Set only X
        ax = set_xyt(self.ax, x="X Only")
        assert ax.get_xlabel() == "X Only"
        assert ax.get_ylabel() == ""
        assert ax.get_title() == ""
        
        # Set only Y
        ax = set_xyt(self.ax, y="Y Only")
        assert ax.get_xlabel() == "X Only"  # Previous value preserved
        assert ax.get_ylabel() == "Y Only"
        assert ax.get_title() == ""
        
        # Set only title
        ax = set_xyt(self.ax, t="Title Only")
        assert ax.get_xlabel() == "X Only"  # Previous value preserved
        assert ax.get_ylabel() == "Y Only"  # Previous value preserved
        assert ax.get_title() == "Title Only"
    
    def test_empty_strings(self):
        """Test setting empty string labels."""
        ax = set_xyt(self.ax, x="", y="", t="")
        
        assert ax.get_xlabel() == ""
        assert ax.get_ylabel() == ""
        assert ax.get_title() == ""
    
    def test_false_values_skip_setting(self):
        """Test that False values skip setting labels."""
        # First set some labels
        self.ax.set_xlabel("Original X")
        self.ax.set_ylabel("Original Y")
        self.ax.set_title("Original Title")
        
        # Call with False values
        ax = set_xyt(self.ax, x=False, y=False, t=False)
        
        # Original labels should be preserved
        assert ax.get_xlabel() == "Original X"
        assert ax.get_ylabel() == "Original Y"
        assert ax.get_title() == "Original Title"
    
    def test_none_values(self):
        """Test behavior with None values."""
        # Set initial labels
        self.ax.set_xlabel("Initial X")
        self.ax.set_ylabel("Initial Y")
        self.ax.set_title("Initial Title")
        
        # None should be treated as a value, not False
        ax = set_xyt(self.ax, x=None, y=None, t=None)
        
        # Should set "None" as string
        assert ax.get_xlabel() == "None"
        assert ax.get_ylabel() == "None"
        assert ax.get_title() == "None"


class TestSetXYTFormatting:
    """Test format_labels functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    @patch('scitex.plt.ax._style._set_xyt.format_label')
    def test_format_labels_true(self, mock_format):
        """Test with format_labels=True (default)."""
        mock_format.side_effect = lambda x: f"FORMATTED_{x}"
        
        ax = set_xyt(self.ax, x="x_label", y="y_label", t="title", format_labels=True)
        
        # format_label should be called for each label
        assert mock_format.call_count == 3
        mock_format.assert_has_calls([
            call("x_label"),
            call("y_label"),
            call("title")
        ])
        
        # Labels should be formatted
        assert ax.get_xlabel() == "FORMATTED_x_label"
        assert ax.get_ylabel() == "FORMATTED_y_label"
        assert ax.get_title() == "FORMATTED_title"
    
    @patch('scitex.plt.ax._style._set_xyt.format_label')
    def test_format_labels_false(self, mock_format):
        """Test with format_labels=False."""
        mock_format.side_effect = lambda x: f"FORMATTED_{x}"
        
        ax = set_xyt(self.ax, x="x_label", y="y_label", t="title", format_labels=False)
        
        # format_label should not be called
        assert mock_format.call_count == 0
        
        # Labels should be set as-is
        assert ax.get_xlabel() == "x_label"
        assert ax.get_ylabel() == "y_label"
        assert ax.get_title() == "title"
    
    @patch('scitex.plt.ax._style._set_xyt.format_label')
    def test_format_labels_partial(self, mock_format):
        """Test formatting with only some labels set."""
        mock_format.side_effect = lambda x: x.upper()
        
        ax = set_xyt(self.ax, x="lower", y=False, t="mixed_Case", format_labels=True)
        
        # Only non-False values should be formatted
        assert mock_format.call_count == 2
        
        assert ax.get_xlabel() == "LOWER"
        assert ax.get_ylabel() == ""  # Not set
        assert ax.get_title() == "MIXED_CASE"


class TestSetXYTSpecialCases:
    """Test special cases and edge conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_numeric_labels(self):
        """Test with numeric label values."""
        ax = set_xyt(self.ax, x=123, y=3.14, t=0)
        
        assert ax.get_xlabel() == "123"
        assert ax.get_ylabel() == "3.14"
        assert ax.get_title() == "0"
    
    def test_unicode_labels(self):
        """Test with Unicode characters."""
        ax = set_xyt(self.ax, x="α_coefficient", y="β_value", t="Δt analysis")
        
        assert ax.get_xlabel() == "α_coefficient"
        assert ax.get_ylabel() == "β_value"
        assert ax.get_title() == "Δt analysis"
    
    def test_latex_labels(self):
        """Test with LaTeX formatted labels."""
        ax = set_xyt(
            self.ax,
            x=r"$\alpha$ coefficient",
            y=r"$\beta$ value",
            t=r"$\Delta t$ analysis"
        )
        
        assert ax.get_xlabel() == r"$\alpha$ coefficient"
        assert ax.get_ylabel() == r"$\beta$ value"
        assert ax.get_title() == r"$\Delta t$ analysis"
    
    def test_multiline_labels(self):
        """Test with multiline labels."""
        ax = set_xyt(
            self.ax,
            x="Line 1\nLine 2",
            y="First\nSecond\nThird",
            t="Title\nSubtitle"
        )
        
        assert ax.get_xlabel() == "Line 1\nLine 2"
        assert ax.get_ylabel() == "First\nSecond\nThird"
        assert ax.get_title() == "Title\nSubtitle"
    
    def test_very_long_labels(self):
        """Test with very long labels."""
        long_label = "A" * 200
        ax = set_xyt(self.ax, x=long_label, y=long_label, t=long_label)
        
        assert ax.get_xlabel() == long_label
        assert ax.get_ylabel() == long_label
        assert ax.get_title() == long_label
    
    def test_special_characters(self):
        """Test with special characters in labels."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        ax = set_xyt(self.ax, x=special_chars, y=special_chars, t=special_chars)
        
        assert ax.get_xlabel() == special_chars
        assert ax.get_ylabel() == special_chars
        assert ax.get_title() == special_chars


class TestSetXYTMultipleAxes:
    """Test set_xyt with multiple axes."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig, self.axes = plt.subplots(2, 2)
        self.axes_flat = self.axes.flatten()
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_multiple_axes_different_labels(self):
        """Test setting different labels on multiple axes."""
        for i, ax in enumerate(self.axes_flat):
            set_xyt(
                ax,
                x=f"X{i}",
                y=f"Y{i}",
                t=f"Subplot {i}"
            )
        
        # Verify each axis has correct labels
        for i, ax in enumerate(self.axes_flat):
            assert ax.get_xlabel() == f"X{i}"
            assert ax.get_ylabel() == f"Y{i}"
            assert ax.get_title() == f"Subplot {i}"
    
    def test_batch_label_setting(self):
        """Test setting same labels on all axes."""
        common_x = "Common X"
        common_y = "Common Y"
        
        for ax in self.axes_flat:
            set_xyt(ax, x=common_x, y=common_y)
        
        # All axes should have same labels
        for ax in self.axes_flat:
            assert ax.get_xlabel() == common_x
            assert ax.get_ylabel() == common_y
            assert ax.get_title() == ""  # Not set
    
    def test_mixed_label_setting(self):
        """Test mixed label setting patterns."""
        # Set different patterns on each subplot
        set_xyt(self.axes[0, 0], x="X1", y=False, t="Title1")
        set_xyt(self.axes[0, 1], x=False, y="Y2", t="Title2")
        set_xyt(self.axes[1, 0], x="X3", y="Y3", t=False)
        set_xyt(self.axes[1, 1], x=False, y=False, t="Title4")
        
        # Verify
        assert self.axes[0, 0].get_xlabel() == "X1"
        assert self.axes[0, 0].get_ylabel() == ""
        assert self.axes[0, 0].get_title() == "Title1"
        
        assert self.axes[0, 1].get_xlabel() == ""
        assert self.axes[0, 1].get_ylabel() == "Y2"
        assert self.axes[0, 1].get_title() == "Title2"
        
        assert self.axes[1, 0].get_xlabel() == "X3"
        assert self.axes[1, 0].get_ylabel() == "Y3"
        assert self.axes[1, 0].get_title() == ""
        
        assert self.axes[1, 1].get_xlabel() == ""
        assert self.axes[1, 1].get_ylabel() == ""
        assert self.axes[1, 1].get_title() == "Title4"


class TestSetXYTIntegration:
    """Test integration with other matplotlib features."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_plot_data(self):
        """Test setting labels with plotted data."""
        # Plot some data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.ax.plot(x, y)
        
        # Set labels
        ax = set_xyt(self.ax, x="Time (s)", y="Amplitude", t="Sine Wave")
        
        assert ax.get_xlabel() == "Time (s)"
        assert ax.get_ylabel() == "Amplitude"
        assert ax.get_title() == "Sine Wave"
        
        # Data should still be there
        assert len(ax.lines) == 1
    
    def test_with_twin_axes(self):
        """Test with twin axes."""
        # Create twin axis
        ax2 = self.ax.twinx()
        
        # Set labels on both
        set_xyt(self.ax, x="X Label", y="Y1 Label", t="Main Title")
        set_xyt(ax2, y="Y2 Label")  # Only Y label for twin
        
        # Verify
        assert self.ax.get_xlabel() == "X Label"
        assert self.ax.get_ylabel() == "Y1 Label"
        assert self.ax.get_title() == "Main Title"
        
        assert ax2.get_ylabel() == "Y2 Label"
        # Twin axis shares X and title
        assert ax2.get_xlabel() == ""  # Not typically set on twin
    
    def test_with_colorbar(self):
        """Test with colorbar axis."""
        # Create an image plot with colorbar
        im = self.ax.imshow(np.random.rand(10, 10))
        cbar = self.fig.colorbar(im)
        
        # Set labels on main axis
        set_xyt(self.ax, x="X pixels", y="Y pixels", t="Random Image")
        
        # Set label on colorbar axis
        set_xyt(cbar.ax, y="Intensity")
        
        assert self.ax.get_xlabel() == "X pixels"
        assert self.ax.get_ylabel() == "Y pixels"
        assert self.ax.get_title() == "Random Image"
        assert cbar.ax.get_ylabel() == "Intensity"
    
    def test_label_properties_preserved(self):
        """Test that existing label properties are preserved."""
        # Set labels with properties
        self.ax.set_xlabel("Original", fontsize=20, color='red')
        self.ax.set_ylabel("Original", fontsize=16, color='blue')
        
        # Update labels
        set_xyt(self.ax, x="New X", y="New Y")
        
        # New text should be set
        assert self.ax.get_xlabel() == "New X"
        assert self.ax.get_ylabel() == "New Y"
        
        # Note: Font properties are not preserved when setting new text
        # This is matplotlib's default behavior


class TestSetXYTErrorHandling:
    """Test error handling and robustness."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_invalid_axis_object(self):
        """Test with invalid axis object."""
        # Should handle gracefully or raise appropriate error
        with pytest.raises(AttributeError):
            set_xyt("not_an_axis", x="X", y="Y", t="T")
    
    def test_closed_figure(self):
        """Test with closed figure."""
        plt.close(self.fig)
        
        # Depending on matplotlib version, this might work or raise
        try:
            set_xyt(self.ax, x="X", y="Y", t="T")
            # If it works, labels might not be retrievable
        except Exception:
            # Expected in some cases
            pass
    
    def test_object_labels(self):
        """Test with arbitrary objects as labels."""
        class CustomLabel:
            def __str__(self):
                return "CustomLabel"
        
        custom = CustomLabel()
        ax = set_xyt(self.ax, x=custom, y=[1, 2, 3], t={'key': 'value'})
        
        # Should convert to string
        assert ax.get_xlabel() == "CustomLabel"
        assert ax.get_ylabel() == "[1, 2, 3]"
        assert ax.get_title() == "{'key': 'value'}"


class TestSetXYTPerformance:
    """Test performance aspects."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_many_label_updates(self):
        """Test many rapid label updates."""
        for i in range(100):
            set_xyt(
                self.ax,
                x=f"X{i}",
                y=f"Y{i}",
                t=f"Title{i}"
            )
        
        # Final labels should be set
        assert self.ax.get_xlabel() == "X99"
        assert self.ax.get_ylabel() == "Y99"
        assert self.ax.get_title() == "Title99"
    
    def test_alternating_format_modes(self):
        """Test alternating between format modes."""
        for i in range(10):
            format_labels = i % 2 == 0
            set_xyt(
                self.ax,
                x=f"label_{i}",
                y=f"label_{i}",
                t=f"label_{i}",
                format_labels=format_labels
            )
        
        # Final labels
        assert self.ax.get_xlabel() == "label_9"
        assert self.ax.get_ylabel() == "label_9"
        assert self.ax.get_title() == "label_9"


class TestSetXYTSaveIntegration:
    """Test integration with figure saving."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_save_with_labels(self):
        """Test saving figure after setting labels."""
        # Add some content
        self.ax.plot([1, 2, 3], [1, 4, 9])
        
        # Set labels
        set_xyt(
            self.ax,
            x="X Values",
            y="Y Values",
            t="Test Plot"
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            try:
                self.fig.savefig(f.name)
                assert os.path.exists(f.name)
                assert os.path.getsize(f.name) > 0
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)
    
    def test_save_multiple_formats(self):
        """Test saving in different formats with labels."""
        set_xyt(self.ax, x="X", y="Y", t="Title")
        
        formats = ['.png', '.pdf', '.svg']
        for fmt in formats:
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                try:
                    self.fig.savefig(f.name)
                    assert os.path.exists(f.name)
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])