#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 09:45:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/utils/test__mk_patches_enhanced.py

"""Comprehensive tests for matplotlib patches creation functionality."""

import pytest
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np


class TestMkPatchesEnhanced:
    """Enhanced test suite for mk_patches function."""

    def test_basic_patches_creation(self):
        """Test basic patch creation with colors and labels."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue", "green"]
        labels = ["Label A", "Label B", "Label C"]
        patches = mk_patches(colors, labels)
        
        assert isinstance(patches, list)
        assert len(patches) == 3
        
        # Check each patch
        for i, patch in enumerate(patches):
            assert isinstance(patch, mpatches.Patch)
            assert patch.get_label() == labels[i]
            assert patch.get_facecolor() == mcolors.to_rgba(colors[i])

    def test_hex_color_codes(self):
        """Test with hexadecimal color codes."""
        from scitex.plt.utils import mk_patches
        
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        labels = ["Red", "Green", "Blue"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 3
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]
            # Hex colors should be properly handled
            assert isinstance(patch.get_facecolor(), tuple)

    def test_rgb_tuple_colors(self):
        """Test with RGB tuple colors."""
        from scitex.plt.utils import mk_patches
        
        colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        labels = ["Red", "Green", "Blue"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 3
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]
            # RGB tuples should be handled correctly
            expected_color = mcolors.to_rgba(colors[i])
            assert np.allclose(patch.get_facecolor(), expected_color)

    def test_rgba_tuple_colors(self):
        """Test with RGBA tuple colors including alpha."""
        from scitex.plt.utils import mk_patches
        
        colors = [(1.0, 0.0, 0.0, 0.5), (0.0, 1.0, 0.0, 0.7), (0.0, 0.0, 1.0, 0.9)]
        labels = ["Semi Red", "Green 70%", "Blue 90%"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 3
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]
            # RGBA tuples should preserve alpha
            assert np.allclose(patch.get_facecolor(), colors[i])

    def test_matplotlib_color_names(self):
        """Test with matplotlib named colors."""
        from scitex.plt.utils import mk_patches
        
        colors = ["crimson", "forestgreen", "royalblue", "orange"]
        labels = ["Crimson", "Forest Green", "Royal Blue", "Orange"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 4
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]

    def test_single_color_label_pair(self):
        """Test with single color and label."""
        from scitex.plt.utils import mk_patches
        
        colors = ["purple"]
        labels = ["Single Label"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 1
        assert patches[0].get_label() == "Single Label"
        assert patches[0].get_facecolor() == mcolors.to_rgba("purple")

    def test_empty_lists(self):
        """Test with empty color and label lists."""
        from scitex.plt.utils import mk_patches
        
        colors = []
        labels = []
        patches = mk_patches(colors, labels)
        
        assert isinstance(patches, list)
        assert len(patches) == 0

    def test_mixed_color_formats(self):
        """Test with mixed color format types."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "#00FF00", (0.0, 0.0, 1.0), (1.0, 1.0, 0.0, 0.8)]
        labels = ["Named", "Hex", "RGB", "RGBA"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 4
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]
            assert isinstance(patch.get_facecolor(), tuple)

    def test_special_characters_in_labels(self):
        """Test with special characters in labels."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue", "green"]
        labels = ["Label with spaces", "Label-with-dashes", "Label_with_underscores"]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 3
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]

    def test_unicode_labels(self):
        """Test with unicode characters in labels."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue"]
        labels = ["レッド", "ブルー"]  # Japanese
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 2
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]

    def test_numeric_labels(self):
        """Test with numeric labels (should be converted to strings)."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue", "green"]
        labels = [1, 2.5, 3]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 3
        for i, patch in enumerate(patches):
            # Labels should be converted to strings
            assert patch.get_label() == str(labels[i])

    def test_long_labels(self):
        """Test with very long labels."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue"]
        labels = [
            "This is a very long label that might be used in scientific plots",
            "Another extremely long label with lots of descriptive text"
        ]
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 2
        for i, patch in enumerate(patches):
            assert patch.get_label() == labels[i]

    def test_patch_properties(self):
        """Test that patches have correct matplotlib properties."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue"]
        labels = ["Red Patch", "Blue Patch"]
        patches = mk_patches(colors, labels)
        
        for patch in patches:
            # Should be Patch instances with standard properties
            assert hasattr(patch, 'get_facecolor')
            assert hasattr(patch, 'get_edgecolor')
            assert hasattr(patch, 'get_linewidth')
            assert hasattr(patch, 'get_linestyle')
            assert hasattr(patch, 'get_alpha')

    def test_mismatched_lengths_fewer_colors(self):
        """Test when colors list is shorter than labels list."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue"]
        labels = ["Label 1", "Label 2", "Label 3"]
        
        # zip() will stop at shortest list
        patches = mk_patches(colors, labels)
        assert len(patches) == 2  # Limited by colors

    def test_mismatched_lengths_fewer_labels(self):
        """Test when labels list is shorter than colors list."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue", "green"]
        labels = ["Label 1", "Label 2"]
        
        # zip() will stop at shortest list
        patches = mk_patches(colors, labels)
        assert len(patches) == 2  # Limited by labels

    def test_legend_integration_compatibility(self):
        """Test that patches work correctly with matplotlib legend."""
        from scitex.plt.utils import mk_patches
        import matplotlib.pyplot as plt
        
        colors = ["red", "blue", "green"]
        labels = ["Series A", "Series B", "Series C"]
        patches = mk_patches(colors, labels)
        
        # Create a figure and test legend creation
        fig, ax = plt.subplots(figsize=(3, 2))
        
        # Should not raise any errors
        legend = ax.legend(handles=patches)
        
        # Check legend has correct number of entries
        assert len(legend.get_texts()) == 3
        
        plt.close(fig)

    def test_list_comprehension_equivalence(self):
        """Test that result matches manual list comprehension."""
        from scitex.plt.utils import mk_patches
        
        colors = ["red", "blue", "green"]
        labels = ["A", "B", "C"]
        
        # Function result
        patches_func = mk_patches(colors, labels)
        
        # Manual list comprehension
        patches_manual = [mpatches.Patch(color=c, label=l) 
                         for c, l in zip(colors, labels)]
        
        assert len(patches_func) == len(patches_manual)
        for func_patch, manual_patch in zip(patches_func, patches_manual):
            assert func_patch.get_label() == manual_patch.get_label()
            assert func_patch.get_facecolor() == manual_patch.get_facecolor()

    def test_color_validation_with_invalid_colors(self):
        """Test behavior with invalid color specifications."""
        from scitex.plt.utils import mk_patches
        
        # These might raise errors or be handled gracefully
        colors = ["not_a_color", "also_invalid"]
        labels = ["Invalid 1", "Invalid 2"]
        
        try:
            patches = mk_patches(colors, labels)
            # If it doesn't raise, check that patches were created
            assert len(patches) == 2
        except (ValueError, TypeError):
            # It's acceptable for invalid colors to raise errors
            pass

    def test_memory_efficiency(self):
        """Test memory efficiency with large numbers of patches."""
        from scitex.plt.utils import mk_patches
        
        # Create many patches
        n = 1000
        colors = ["red"] * n
        labels = [f"Label {i}" for i in range(n)]
        
        patches = mk_patches(colors, labels)
        
        assert len(patches) == n
        assert all(isinstance(p, mpatches.Patch) for p in patches)

    def test_color_cycle_compatibility(self):
        """Test compatibility with matplotlib color cycle."""
        from scitex.plt.utils import mk_patches
        import matplotlib.pyplot as plt
        
        # Use matplotlib's default color cycle
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = [item['color'] for item in prop_cycle][:5]
        labels = [f"Series {i+1}" for i in range(5)]
        
        patches = mk_patches(colors, labels)
        
        assert len(patches) == 5
        for patch in patches:
            assert isinstance(patch, mpatches.Patch)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])