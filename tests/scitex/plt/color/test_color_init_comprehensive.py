#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for plt/color/__init__.py

Tests cover:
- Module imports and exports
- Color conversion functions
- Color manipulation functions
- Colormap utilities
- Parameter constants
- Integration between color functions
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock

import matplotlib.pyplot as plt
import numpy as np
import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


class TestModuleStructure:
    """Test basic module structure and imports."""
    
    def test_module_imports(self):
        """Test that the module can be imported."""
        import scitex.plt.color
        assert scitex.plt.color is not None
    
    def test_file_and_dir_attributes(self):
        """Test __FILE__ and __DIR__ attributes."""
        import scitex.plt.color
        
        assert hasattr(scitex.plt.color, '__FILE__')
        assert hasattr(scitex.plt.color, '__DIR__')
        assert scitex.plt.color.__FILE__ == "./src/scitex/plt/color/__init__.py"
    
    def test_all_imports_available(self):
        """Test that all expected functions are imported."""
        import scitex.plt.color
        
        # Colormap functions
        assert hasattr(scitex.plt.color, 'get_color_from_cmap')
        assert hasattr(scitex.plt.color, 'get_colors_from_cmap')
        assert hasattr(scitex.plt.color, 'get_categorical_colors_from_cmap')
        
        # Other utilities
        assert hasattr(scitex.plt.color, 'interpolate')
        assert hasattr(scitex.plt.color, 'PARAMS')
        assert hasattr(scitex.plt.color, 'vizualize_colors')
        
        # RGB functions
        assert hasattr(scitex.plt.color, 'str2rgb')
        assert hasattr(scitex.plt.color, 'str2rgba')
        assert hasattr(scitex.plt.color, 'rgb2rgba')
        assert hasattr(scitex.plt.color, 'rgba2rgb')
        assert hasattr(scitex.plt.color, 'rgba2hex')
        assert hasattr(scitex.plt.color, 'cycle_color_rgb')
        assert hasattr(scitex.plt.color, 'gradiate_color_rgb')
        assert hasattr(scitex.plt.color, 'gradiate_color_rgba')
        
        # BGR functions
        assert hasattr(scitex.plt.color, 'str2bgr')
        assert hasattr(scitex.plt.color, 'str2bgra')
        assert hasattr(scitex.plt.color, 'bgr2bgra')
        assert hasattr(scitex.plt.color, 'bgra2bgr')
        assert hasattr(scitex.plt.color, 'bgra2hex')
        assert hasattr(scitex.plt.color, 'cycle_color_bgr')
        assert hasattr(scitex.plt.color, 'gradiate_color_bgr')
        assert hasattr(scitex.plt.color, 'gradiate_color_bgra')
        
        # Common functions
        assert hasattr(scitex.plt.color, 'rgb2bgr')
        assert hasattr(scitex.plt.color, 'bgr2rgb')
        assert hasattr(scitex.plt.color, 'str2hex')
        assert hasattr(scitex.plt.color, 'update_alpha')
        assert hasattr(scitex.plt.color, 'cycle_color')
        assert hasattr(scitex.plt.color, 'gradiate_color')
        assert hasattr(scitex.plt.color, 'to_rgb')
        assert hasattr(scitex.plt.color, 'to_rgba')
        assert hasattr(scitex.plt.color, 'to_hex')


class TestColorConversions:
    """Test color conversion functions."""
    
    def test_str2rgb(self):
        """Test string to RGB conversion."""
        import scitex.plt.color
        
        # Test with color names
        red = scitex.plt.color.str2rgb('red')
        assert isinstance(red, (list, tuple, np.ndarray))
        assert len(red) == 3
        assert all(0 <= c <= 1 for c in red)
        
        # Red should have high R component
        assert red[0] > 0.9
        assert red[1] < 0.1
        assert red[2] < 0.1
    
    def test_str2rgba(self):
        """Test string to RGBA conversion."""
        import scitex.plt.color
        
        blue = scitex.plt.color.str2rgba('blue')
        assert isinstance(blue, (list, tuple, np.ndarray))
        assert len(blue) == 4
        assert all(0 <= c <= 1 for c in blue)
        
        # Blue should have high B component
        assert blue[2] > 0.9
        assert blue[3] == 1.0  # Default alpha
    
    def test_rgb2rgba(self):
        """Test RGB to RGBA conversion."""
        import scitex.plt.color
        
        rgb = [1.0, 0.5, 0.0]
        rgba = scitex.plt.color.rgb2rgba(rgb)
        
        assert len(rgba) == 4
        assert rgba[:3] == rgb or np.allclose(rgba[:3], rgb)
        assert rgba[3] == 1.0  # Default alpha
    
    def test_rgba2rgb(self):
        """Test RGBA to RGB conversion."""
        import scitex.plt.color
        
        rgba = [1.0, 0.5, 0.0, 0.8]
        rgb = scitex.plt.color.rgba2rgb(rgba)
        
        assert len(rgb) == 3
        assert rgb == rgba[:3] or np.allclose(rgb, rgba[:3])
    
    def test_rgba2hex(self):
        """Test RGBA to hex conversion."""
        import scitex.plt.color
        
        rgba = [1.0, 0.0, 0.0, 1.0]  # Red
        hex_color = scitex.plt.color.rgba2hex(rgba)
        
        assert isinstance(hex_color, str)
        assert hex_color.startswith('#')
        assert len(hex_color) in [7, 9]  # #RRGGBB or #RRGGBBAA
    
    def test_str2hex(self):
        """Test string to hex conversion."""
        import scitex.plt.color
        
        hex_green = scitex.plt.color.str2hex('green')
        assert isinstance(hex_green, str)
        assert hex_green.startswith('#')
    
    def test_rgb2bgr(self):
        """Test RGB to BGR conversion."""
        import scitex.plt.color
        
        rgb = [1.0, 0.5, 0.0]
        bgr = scitex.plt.color.rgb2bgr(rgb)
        
        assert bgr[0] == rgb[2]
        assert bgr[1] == rgb[1]
        assert bgr[2] == rgb[0]
    
    def test_bgr2rgb(self):
        """Test BGR to RGB conversion."""
        import scitex.plt.color
        
        bgr = [0.0, 0.5, 1.0]
        rgb = scitex.plt.color.bgr2rgb(bgr)
        
        assert rgb[0] == bgr[2]
        assert rgb[1] == bgr[1]
        assert rgb[2] == bgr[0]
    
    def test_to_rgb(self):
        """Test generic to_rgb conversion."""
        import scitex.plt.color
        
        # From string
        rgb1 = scitex.plt.color.to_rgb('red')
        assert len(rgb1) == 3
        
        # From hex
        rgb2 = scitex.plt.color.to_rgb('#FF0000')
        assert len(rgb2) == 3
        
        # From rgba
        rgb3 = scitex.plt.color.to_rgb([1, 0, 0, 1])
        assert len(rgb3) == 3
    
    def test_to_rgba(self):
        """Test generic to_rgba conversion."""
        import scitex.plt.color
        
        # From string
        rgba1 = scitex.plt.color.to_rgba('blue')
        assert len(rgba1) == 4
        
        # From rgb
        rgba2 = scitex.plt.color.to_rgba([0, 0, 1])
        assert len(rgba2) == 4
    
    def test_to_hex(self):
        """Test generic to_hex conversion."""
        import scitex.plt.color
        
        # From string
        hex1 = scitex.plt.color.to_hex('green')
        assert hex1.startswith('#')
        
        # From rgb
        hex2 = scitex.plt.color.to_hex([0, 1, 0])
        assert hex2.startswith('#')


class TestColorManipulation:
    """Test color manipulation functions."""
    
    def test_update_alpha(self):
        """Test alpha channel update."""
        import scitex.plt.color
        
        rgba = [1.0, 0.5, 0.0, 1.0]
        new_rgba = scitex.plt.color.update_alpha(rgba, 0.5)
        
        assert new_rgba[:3] == rgba[:3] or np.allclose(new_rgba[:3], rgba[:3])
        assert new_rgba[3] == 0.5
    
    def test_cycle_color(self):
        """Test color cycling."""
        import scitex.plt.color
        
        # Get cycled colors
        colors = [scitex.plt.color.cycle_color(i) for i in range(10)]
        
        # Should return different colors
        assert len(set(map(tuple, colors))) > 1
        
        # Colors should cycle back
        cycle_length = 10  # Typical matplotlib cycle length
        color1 = scitex.plt.color.cycle_color(0)
        color2 = scitex.plt.color.cycle_color(cycle_length)
        # Might be same color if cycle repeats
    
    def test_gradiate_color(self):
        """Test color gradiation."""
        import scitex.plt.color
        
        # Create gradient from red to blue
        n_colors = 5
        colors = []
        for i in range(n_colors):
            t = i / (n_colors - 1)
            color = scitex.plt.color.gradiate_color('red', 'blue', t)
            colors.append(color)
        
        # First should be red-ish, last should be blue-ish
        assert colors[0][0] > colors[0][2]  # More red than blue
        assert colors[-1][2] > colors[-1][0]  # More blue than red
    
    def test_cycle_color_rgb(self):
        """Test RGB color cycling."""
        import scitex.plt.color
        
        colors = [scitex.plt.color.cycle_color_rgb(i) for i in range(5)]
        assert all(len(c) == 3 for c in colors)
        assert all(all(0 <= val <= 1 for val in c) for c in colors)
    
    def test_gradiate_color_rgb(self):
        """Test RGB color gradiation."""
        import scitex.plt.color
        
        color1 = [1, 0, 0]  # Red
        color2 = [0, 0, 1]  # Blue
        
        # Midpoint
        mid_color = scitex.plt.color.gradiate_color_rgb(color1, color2, 0.5)
        assert len(mid_color) == 3
        
        # Should be purplish (mix of red and blue)
        assert 0.3 < mid_color[0] < 0.7
        assert 0.3 < mid_color[2] < 0.7


class TestColormapFunctions:
    """Test colormap-related functions."""
    
    def test_get_color_from_cmap(self):
        """Test getting single color from colormap."""
        import scitex.plt.color
        
        # Get color from viridis colormap
        color = scitex.plt.color.get_color_from_cmap(0.5, 'viridis')
        
        assert isinstance(color, (list, tuple, np.ndarray))
        assert len(color) in [3, 4]  # RGB or RGBA
        assert all(0 <= c <= 1 for c in color)
    
    def test_get_colors_from_cmap(self):
        """Test getting multiple colors from colormap."""
        import scitex.plt.color
        
        n_colors = 10
        colors = scitex.plt.color.get_colors_from_cmap(n_colors, 'plasma')
        
        assert len(colors) == n_colors
        assert all(len(c) in [3, 4] for c in colors)
        assert all(all(0 <= val <= 1 for val in c) for c in colors)
    
    def test_get_categorical_colors_from_cmap(self):
        """Test getting categorical colors from colormap."""
        import scitex.plt.color
        
        n_categories = 5
        colors = scitex.plt.color.get_categorical_colors_from_cmap(n_categories, 'tab10')
        
        assert len(colors) == n_categories
        # Colors should be distinct for categorical use
        color_tuples = [tuple(c) for c in colors]
        assert len(set(color_tuples)) == n_categories


class TestColorInterpolation:
    """Test color interpolation."""
    
    def test_interpolate_basic(self):
        """Test basic color interpolation."""
        import scitex.plt.color
        
        color1 = [1, 0, 0]  # Red
        color2 = [0, 1, 0]  # Green
        
        # Interpolate at different points
        interp_0 = scitex.plt.color.interpolate(color1, color2, 0)
        interp_1 = scitex.plt.color.interpolate(color1, color2, 1)
        interp_half = scitex.plt.color.interpolate(color1, color2, 0.5)
        
        # At t=0, should be color1
        assert np.allclose(interp_0, color1)
        
        # At t=1, should be color2
        assert np.allclose(interp_1, color2)
        
        # At t=0.5, should be halfway
        assert 0.4 < interp_half[0] < 0.6
        assert 0.4 < interp_half[1] < 0.6
    
    def test_interpolate_with_alpha(self):
        """Test interpolation with alpha channel."""
        import scitex.plt.color
        
        color1 = [1, 0, 0, 1]  # Red, opaque
        color2 = [0, 0, 1, 0.5]  # Blue, semi-transparent
        
        interp = scitex.plt.color.interpolate(color1, color2, 0.5)
        assert len(interp) == 4
        assert 0.7 < interp[3] < 0.8  # Alpha should be interpolated too


class TestPARAMS:
    """Test PARAMS constant."""
    
    def test_params_exists(self):
        """Test that PARAMS is available."""
        import scitex.plt.color
        
        assert hasattr(scitex.plt.color, 'PARAMS')
        assert scitex.plt.color.PARAMS is not None
    
    def test_params_structure(self):
        """Test PARAMS structure if it's a dict."""
        import scitex.plt.color
        
        params = scitex.plt.color.PARAMS
        
        # Could be a dict with color definitions
        if isinstance(params, dict):
            # Might contain color palettes, default colors, etc.
            assert len(params) > 0


class TestVisualization:
    """Test color visualization."""
    
    def test_vizualize_colors_function_exists(self):
        """Test that vizualize_colors function exists."""
        import scitex.plt.color
        
        assert hasattr(scitex.plt.color, 'vizualize_colors')
        assert callable(scitex.plt.color.vizualize_colors)
    
    @patch('matplotlib.pyplot.show')
    def test_vizualize_colors_basic(self, mock_show):
        """Test basic color visualization."""
        import scitex.plt.color
        
        colors = ['red', 'green', 'blue']
        
        # Should create visualization without error
        result = scitex.plt.color.vizualize_colors(colors)
        
        # Might return figure or None
        if result is not None:
            plt.close(result)


class TestBGRFunctions:
    """Test BGR color space functions."""
    
    def test_str2bgr(self):
        """Test string to BGR conversion."""
        import scitex.plt.color
        
        bgr = scitex.plt.color.str2bgr('red')
        assert len(bgr) == 3
        
        # For red: BGR should have high B (which is R in RGB)
        assert bgr[2] > 0.9
        assert bgr[1] < 0.1
        assert bgr[0] < 0.1
    
    def test_bgr2bgra(self):
        """Test BGR to BGRA conversion."""
        import scitex.plt.color
        
        bgr = [0, 0.5, 1]
        bgra = scitex.plt.color.bgr2bgra(bgr)
        
        assert len(bgra) == 4
        assert bgra[:3] == bgr or np.allclose(bgra[:3], bgr)
        assert bgra[3] == 1.0
    
    def test_bgra2bgr(self):
        """Test BGRA to BGR conversion."""
        import scitex.plt.color
        
        bgra = [0, 0.5, 1, 0.8]
        bgr = scitex.plt.color.bgra2bgr(bgra)
        
        assert len(bgr) == 3
        assert bgr == bgra[:3] or np.allclose(bgr, bgra[:3])
    
    def test_cycle_color_bgr(self):
        """Test BGR color cycling."""
        import scitex.plt.color
        
        colors = [scitex.plt.color.cycle_color_bgr(i) for i in range(5)]
        assert all(len(c) == 3 for c in colors)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_color_string(self):
        """Test handling of invalid color strings."""
        import scitex.plt.color
        
        # Should either return a default or raise an error
        try:
            color = scitex.plt.color.str2rgb('not_a_color')
            # If it returns something, should be valid color
            assert len(color) == 3
            assert all(0 <= c <= 1 for c in color)
        except (ValueError, KeyError):
            # Error is acceptable for invalid input
            pass
    
    def test_out_of_range_values(self):
        """Test handling of out-of-range values."""
        import scitex.plt.color
        
        # Test with values > 1
        rgba = [1.5, 0.5, -0.5, 2.0]
        
        # Functions should either clip or raise error
        try:
            hex_color = scitex.plt.color.rgba2hex(rgba)
            # If successful, should be valid hex
            assert hex_color.startswith('#')
        except ValueError:
            # Error is acceptable for invalid input
            pass
    
    def test_empty_color_list(self):
        """Test handling of empty color lists."""
        import scitex.plt.color
        
        # Getting 0 colors from colormap
        colors = scitex.plt.color.get_colors_from_cmap(0, 'viridis')
        assert len(colors) == 0
    
    def test_single_color_gradient(self):
        """Test gradient with same start and end color."""
        import scitex.plt.color
        
        color = [0.5, 0.5, 0.5]
        result = scitex.plt.color.gradiate_color_rgb(color, color, 0.5)
        
        # Should return the same color
        assert np.allclose(result, color)


class TestIntegration:
    """Test integration between different color functions."""
    
    def test_full_color_pipeline(self):
        """Test converting through multiple formats."""
        import scitex.plt.color
        
        # Start with string
        color_str = 'red'
        
        # Convert to RGB
        rgb = scitex.plt.color.str2rgb(color_str)
        
        # Convert to RGBA
        rgba = scitex.plt.color.rgb2rgba(rgb)
        
        # Convert to hex
        hex_color = scitex.plt.color.rgba2hex(rgba)
        
        # Convert to BGR
        bgr = scitex.plt.color.rgb2bgr(rgb)
        
        # All should represent red
        assert rgb[0] > 0.9  # High red component
        assert rgba[0] > 0.9
        assert bgr[2] > 0.9  # Red is last in BGR
        assert 'ff' in hex_color.lower() or 'f0' in hex_color.lower()
    
    def test_colormap_to_hex(self):
        """Test getting colors from colormap and converting to hex."""
        import scitex.plt.color
        
        # Get colors from colormap
        colors = scitex.plt.color.get_colors_from_cmap(5, 'viridis')
        
        # Convert all to hex
        hex_colors = [scitex.plt.color.to_hex(c) for c in colors]
        
        assert len(hex_colors) == 5
        assert all(h.startswith('#') for h in hex_colors)
        assert len(set(hex_colors)) == 5  # All different
    
    def test_color_manipulation_pipeline(self):
        """Test color manipulation workflow."""
        import scitex.plt.color
        
        # Start with a base color
        base_color = scitex.plt.color.str2rgba('blue')
        
        # Update alpha
        transparent = scitex.plt.color.update_alpha(base_color, 0.5)
        assert transparent[3] == 0.5
        
        # Create gradient to another color
        target_color = scitex.plt.color.str2rgba('green')
        mid_color = scitex.plt.color.gradiate_color_rgba(
            base_color, target_color, 0.5
        )
        
        # Should be between blue and green
        assert mid_color[1] > base_color[1]  # More green
        assert mid_color[2] < base_color[2]  # Less blue


class TestImportOrder:
    """Test that imports work regardless of order."""
    
    def test_import_after_usage(self):
        """Test importing specific functions after module import."""
        import scitex.plt.color
        from scitex.plt.color import str2rgb, rgb2rgba
        
        # Should work
        rgb = str2rgb('red')
        rgba = rgb2rgba(rgb)
        
        assert len(rgb) == 3
        assert len(rgba) == 4
    
    def test_submodule_imports(self):
        """Test that submodules are properly organized."""
        import scitex.plt.color
        
        # Check module organization
        assert scitex.plt.color.__name__ == 'scitex.plt.color'
        
        # Functions should be at module level
        assert 'str2rgb' in dir(scitex.plt.color)
        assert 'get_colors_from_cmap' in dir(scitex.plt.color)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])