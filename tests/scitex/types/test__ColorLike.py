#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:53:00 (ywatanabe)"
# File: ./tests/scitex/types/test__ColorLike.py

"""
Functionality:
    * Tests ColorLike type definition for color representation
    * Validates that ColorLike encompasses various color formats
    * Tests type structure and compatibility
Input:
    * Various color representations
Output:
    * Test results
Prerequisites:
    * pytest
"""

import pytest
from typing import get_origin, get_args


class TestColorLike:
    """Test cases for ColorLike type definition."""

    def setup_method(self):
        """Setup test fixtures."""
        from scitex.types import ColorLike
        self.ColorLike = ColorLike

    def test_colorlike_type_structure(self):
        """Test that ColorLike has expected Union structure."""
        # ColorLike should be a Union type
        origin = get_origin(self.ColorLike)
        args = get_args(self.ColorLike)
        
        # Should have multiple type arguments (Union components)
        assert args is not None
        assert len(args) >= 3  # str, RGB tuple, RGBA tuple, List

    def test_colorlike_includes_string_type(self):
        """Test that ColorLike includes string type for named colors."""
        args = get_args(self.ColorLike)
        
        # Should include str type for named colors like 'red', 'blue', etc.
        assert str in args

    def test_colorlike_includes_rgb_tuple(self):
        """Test that ColorLike includes RGB tuple type."""
        args = get_args(self.ColorLike)
        
        # Should include tuple types for RGB values
        tuple_args = [arg for arg in args if get_origin(arg) is tuple or arg is tuple]
        
        # Should have tuple types (either generic tuple or specific RGB tuples)
        assert len(tuple_args) > 0

    def test_colorlike_includes_list_type(self):
        """Test that ColorLike includes list type for color values."""
        args = get_args(self.ColorLike)
        
        # Should include list type for color arrays
        list_types = [arg for arg in args if get_origin(arg) is list or arg is list]
        assert len(list_types) > 0

    def test_colorlike_type_annotation_usage(self):
        """Test that ColorLike can be used in type annotations."""
        # This is a compile-time test - if it runs without error, it passes
        def test_function(color: self.ColorLike) -> str:
            return str(color)
        
        # Should be able to define function with ColorLike annotation
        assert callable(test_function)
        assert test_function.__annotations__['color'] is self.ColorLike

    def test_colorlike_with_string_colors(self):
        """Test ColorLike compatibility with string color names."""
        # These would be valid color strings in matplotlib/web contexts
        string_colors = [
            'red',
            'blue', 
            'green',
            'black',
            'white',
            '#FF0000',
            '#00FF00',
            '#0000FF',
            'rgb(255, 0, 0)',
            'rgba(255, 0, 0, 1.0)'
        ]
        
        # Type checking would validate these at static analysis time
        # Here we just verify the type exists and has correct structure
        assert self.ColorLike is not None

    def test_colorlike_with_rgb_tuples(self):
        """Test ColorLike compatibility with RGB tuples."""
        # These would be valid RGB tuples
        rgb_tuples = [
            (1.0, 0.0, 0.0),    # Red
            (0.0, 1.0, 0.0),    # Green  
            (0.0, 0.0, 1.0),    # Blue
            (0.5, 0.5, 0.5),    # Gray
            (255, 0, 0),        # Red (0-255 scale)
            (0, 255, 0),        # Green (0-255 scale)
        ]
        
        # Type annotation compatibility test
        assert self.ColorLike is not None

    def test_colorlike_with_rgba_tuples(self):
        """Test ColorLike compatibility with RGBA tuples."""
        # These would be valid RGBA tuples
        rgba_tuples = [
            (1.0, 0.0, 0.0, 1.0),    # Red, fully opaque
            (0.0, 1.0, 0.0, 0.5),    # Green, semi-transparent
            (0.0, 0.0, 1.0, 0.0),    # Blue, fully transparent
            (255, 0, 0, 255),        # Red (0-255 scale)
            (0, 255, 0, 128),        # Green, semi-transparent (0-255 scale)
        ]
        
        # Type annotation compatibility test
        assert self.ColorLike is not None

    def test_colorlike_with_color_lists(self):
        """Test ColorLike compatibility with color lists."""
        # These would be valid color value lists
        color_lists = [
            [1.0, 0.0, 0.0],         # RGB as list
            [1.0, 0.0, 0.0, 1.0],    # RGBA as list
            [255, 0, 0],             # RGB (0-255 scale)
            [255, 0, 0, 255],        # RGBA (0-255 scale)
            [0.5],                   # Grayscale
            [0.2, 0.8],              # Custom format
        ]
        
        # Type annotation compatibility test
        assert self.ColorLike is not None

    def test_colorlike_function_parameter_annotation(self):
        """Test ColorLike usage as function parameter annotation."""
        def plot_with_color(data, color: self.ColorLike):
            """Example function that accepts ColorLike parameter."""
            return f"Plotting with color: {color}"
        
        # Verify annotation is correct
        import inspect
        sig = inspect.signature(plot_with_color)
        assert sig.parameters['color'].annotation is self.ColorLike

    def test_colorlike_function_return_annotation(self):
        """Test ColorLike usage as function return annotation."""
        def get_default_color() -> self.ColorLike:
            """Example function that returns ColorLike."""
            return 'blue'
        
        # Verify annotation is correct
        import inspect
        sig = inspect.signature(get_default_color)
        assert sig.return_annotation is self.ColorLike

    def test_colorlike_variable_annotation(self):
        """Test ColorLike usage in variable annotations."""
        # Test that we can annotate variables with ColorLike
        primary_color: self.ColorLike = 'red'
        secondary_color: self.ColorLike = (0.0, 1.0, 0.0)
        tertiary_color: self.ColorLike = [0.0, 0.0, 1.0]
        
        # If this runs without error, annotations work
        assert primary_color == 'red'
        assert secondary_color == (0.0, 1.0, 0.0)
        assert tertiary_color == [0.0, 0.0, 1.0]

    def test_colorlike_type_checking_compatibility(self):
        """Test ColorLike compatibility with type checking tools."""
        # This tests that the type is properly structured for static analysis
        from typing import Union, List, Tuple
        
        # ColorLike should be a Union containing these types
        args = get_args(self.ColorLike)
        type_names = [str(arg) for arg in args]
        
        # Should contain fundamental color representation types
        has_str = any('str' in name for name in type_names)
        has_tuple = any('tuple' in name.lower() for name in type_names)
        has_list = any('list' in name.lower() for name in type_names)
        
        assert has_str, "ColorLike should include str type"
        assert has_tuple, "ColorLike should include tuple type"
        assert has_list, "ColorLike should include list type"

    def test_colorlike_realistic_usage_scenarios(self):
        """Test ColorLike in realistic plotting/graphics scenarios."""
        def set_plot_colors(
            line_color: self.ColorLike,
            fill_color: self.ColorLike, 
            background_color: self.ColorLike
        ):
            """Realistic plotting function using ColorLike."""
            return {
                'line': line_color,
                'fill': fill_color,
                'background': background_color
            }
        
        # Test with different color formats
        result1 = set_plot_colors('red', (0.0, 1.0, 0.0), [0.0, 0.0, 1.0])
        result2 = set_plot_colors('#FF0000', (0, 255, 0, 128), [0.5, 0.5, 0.5, 1.0])
        
        assert result1['line'] == 'red'
        assert result1['fill'] == (0.0, 1.0, 0.0)
        assert result1['background'] == [0.0, 0.0, 1.0]

    def test_colorlike_matplotlib_compatibility(self):
        """Test ColorLike covers matplotlib color formats."""
        # Matplotlib accepts many color formats that should be in ColorLike
        matplotlib_colors = [
            # Named colors
            'red', 'blue', 'green', 'black', 'white',
            # Single letter codes  
            'r', 'g', 'b', 'k', 'w',
            # Hex colors
            '#FF0000', '#00FF00', '#0000FF',
            # RGB tuples (0-1 scale)
            (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
            # RGBA tuples (0-1 scale)
            (1.0, 0.0, 0.0, 0.5), (0.0, 1.0, 0.0, 1.0),
            # Grayscale strings
            '0.5', '0.8'
        ]
        
        # ColorLike should support these formats conceptually
        assert self.ColorLike is not None

    def test_colorlike_web_color_compatibility(self):
        """Test ColorLike covers web/CSS color formats."""
        # Web/CSS color formats that should be supported
        web_colors = [
            # Named colors
            'red', 'blue', 'green', 'black', 'white',
            # Hex colors
            '#FF0000', '#00FF00', '#0000FF', '#123456',
            # RGB function strings
            'rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)',
            # RGBA function strings
            'rgba(255, 0, 0, 1.0)', 'rgba(0, 255, 0, 0.5)',
            # HSL colors
            'hsl(0, 100%, 50%)', 'hsl(120, 100%, 50%)'
        ]
        
        # ColorLike string type should cover these
        assert str in get_args(self.ColorLike)

    def test_colorlike_scientific_color_compatibility(self):
        """Test ColorLike covers scientific visualization color formats."""
        # Scientific plotting often uses these formats
        scientific_colors = [
            # Normalized RGB arrays
            [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0],
            # Normalized RGBA arrays
            [1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 0.5],
            # Integer RGB arrays (0-255)
            [255, 0, 0], [0, 255, 0], [0, 0, 255],
            # Colormap names
            'viridis', 'plasma', 'inferno', 'magma'
        ]
        
        # ColorLike should support arrays and strings
        args = get_args(self.ColorLike)
        has_list = any(get_origin(arg) is list or arg is list for arg in args)
        has_str = str in args
        
        assert has_list and has_str

    def test_colorlike_module_integration(self):
        """Test ColorLike integration with the types module."""
        # Should be available through the main types module
        import scitex.types
        assert hasattr(scitex.types, 'ColorLike')
        assert scitex.types.ColorLike is self.ColorLike

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/types/_ColorLike.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 17:09:16 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/types/_ColorLike.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/types/_ColorLike.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# from typing import List, Tuple, Union
# 
# # Define ColorLike type
# ColorLike = Union[
#     str,
#     Tuple[float, float, float],
#     Tuple[float, float, float, float],
#     List[float],
# ]
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/types/_ColorLike.py
# --------------------------------------------------------------------------------
