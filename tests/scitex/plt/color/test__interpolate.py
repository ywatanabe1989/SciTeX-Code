#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 00:52:01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/color/test__interpolate.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/color/test__interpolate.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.colors as mcolors
import numpy as np
import pytest
import warnings


def test_interpolate():
from scitex.plt.color import interpolate

    # Test with basic colors and small number of points
    color_start = "red"
    color_end = "blue"
    num_points = 5

    colors = interpolate(color_start, color_end, num_points)

    # Check that we get the expected number of colors
    assert len(colors) == num_points

    # Check that each color is a list of 4 values (RGBA)
    for color in colors:
        assert len(color) == 4
        for value in color:
            assert 0 <= value <= 1

    # Check that the first and last colors match the inputs
    start_rgba = np.array(mcolors.to_rgba(color_start)).round(3)
    end_rgba = np.array(mcolors.to_rgba(color_end)).round(3)

    np.testing.assert_almost_equal(colors[0], start_rgba, decimal=3)
    np.testing.assert_almost_equal(colors[-1], end_rgba, decimal=3)


def test_gen_interpolate_basic():
    """Test gen_interpolate with basic functionality."""
from scitex.plt.color import gen_interpolate
    
    # Test with named colors
    colors = gen_interpolate("red", "blue", 5)
    assert len(colors) == 5
    assert all(len(c) == 4 for c in colors)
    
    # Check start and end colors
    assert colors[0] == list(np.array(mcolors.to_rgba("red")).round(3))
    assert colors[-1] == list(np.array(mcolors.to_rgba("blue")).round(3))


def test_gen_interpolate_hex_colors():
    """Test gen_interpolate with hex color codes."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("#FF0000", "#0000FF", 3)
    assert len(colors) == 3
    
    # Check intermediate color is purple-ish
    assert colors[1][0] > 0  # Red component
    assert colors[1][2] > 0  # Blue component


def test_gen_interpolate_rgb_tuples():
    """Test gen_interpolate with RGB tuples."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate((1, 0, 0), (0, 0, 1), 4)
    assert len(colors) == 4
    
    # Check gradual transition
    for i in range(1, 4):
        assert colors[i][0] < colors[i-1][0]  # Red decreasing
        assert colors[i][2] > colors[i-1][2]  # Blue increasing


def test_gen_interpolate_rgba_tuples():
    """Test gen_interpolate with RGBA tuples including alpha."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate((1, 0, 0, 0.5), (0, 0, 1, 1.0), 3)
    assert len(colors) == 3
    
    # Check alpha interpolation
    assert colors[0][3] == 0.5
    assert colors[1][3] == 0.75
    assert colors[2][3] == 1.0


def test_gen_interpolate_single_point():
    """Test gen_interpolate with single point."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("red", "blue", 1)
    assert len(colors) == 1
    # With single point, should return start color
    assert colors[0] == list(np.array(mcolors.to_rgba("red")).round(3))


def test_gen_interpolate_two_points():
    """Test gen_interpolate with two points."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("red", "blue", 2)
    assert len(colors) == 2
    assert colors[0] == list(np.array(mcolors.to_rgba("red")).round(3))
    assert colors[1] == list(np.array(mcolors.to_rgba("blue")).round(3))


def test_gen_interpolate_large_number():
    """Test gen_interpolate with large number of points."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("black", "white", 100)
    assert len(colors) == 100
    
    # Check monotonic increase in grayscale
    for i in range(1, 100):
        assert colors[i][0] >= colors[i-1][0]
        assert colors[i][1] >= colors[i-1][1]
        assert colors[i][2] >= colors[i-1][2]


def test_gen_interpolate_custom_rounding():
    """Test gen_interpolate with custom rounding."""
from scitex.plt.color import gen_interpolate
    
    # Test with different rounding values
    colors_round_1 = gen_interpolate("red", "blue", 3, round=1)
    colors_round_5 = gen_interpolate("red", "blue", 3, round=5)
    
    # Check that values are rounded appropriately
    for color in colors_round_1:
        for val in color:
            assert val == round(val, 1)
    
    for color in colors_round_5:
        for val in color:
            assert val == round(val, 5)


def test_gen_interpolate_same_colors():
    """Test gen_interpolate when start and end colors are the same."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("red", "red", 5)
    assert len(colors) == 5
    
    # All colors should be the same
    red_rgba = list(np.array(mcolors.to_rgba("red")).round(3))
    for color in colors:
        assert color == red_rgba


def test_interpolate_deprecation_warning():
    """Test that interpolate function raises deprecation warning."""
from scitex.plt.color import interpolate
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        colors = interpolate("red", "blue", 3)
        
        # Check that deprecation warning was raised
        assert len(w) >= 1
        assert any("deprecated" in str(warning.message).lower() for warning in w)
        assert any("Use gen_interpolate instead" in str(warning.message) for warning in w)
    
    # Check that it still works despite deprecation
    assert len(colors) == 3


def test_gen_interpolate_invalid_color():
    """Test gen_interpolate with invalid color names."""
from scitex.plt.color import gen_interpolate
    
    with pytest.raises(ValueError):
        gen_interpolate("not_a_color", "blue", 3)
    
    with pytest.raises(ValueError):
        gen_interpolate("red", "invalid_color", 3)


def test_gen_interpolate_zero_points():
    """Test gen_interpolate with zero points."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("red", "blue", 0)
    assert len(colors) == 0
    assert colors == []


def test_gen_interpolate_negative_points():
    """Test gen_interpolate with negative number of points."""
from scitex.plt.color import gen_interpolate
    
    # NumPy linspace should handle this gracefully
    colors = gen_interpolate("red", "blue", -5)
    assert len(colors) == 0
    assert colors == []


def test_gen_interpolate_grayscale():
    """Test gen_interpolate with grayscale colors."""
from scitex.plt.color import gen_interpolate
    
    colors = gen_interpolate("gray", "lightgray", 5)
    assert len(colors) == 5
    
    # Check that RGB components are equal (grayscale)
    for color in colors:
        assert abs(color[0] - color[1]) < 0.001
        assert abs(color[1] - color[2]) < 0.001


def test_gen_interpolate_css_colors():
    """Test gen_interpolate with CSS color names."""
from scitex.plt.color import gen_interpolate
    
    # Test with various CSS color names
    css_colors = [
        ("crimson", "deepskyblue"),
        ("forestgreen", "gold"),
        ("darkviolet", "orange")
    ]
    
    for start, end in css_colors:
        colors = gen_interpolate(start, end, 3)
        assert len(colors) == 3
        assert all(len(c) == 4 for c in colors)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_interpolate.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 00:51:06 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_interp_colors.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/color/_interp_colors.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib.colors as mcolors
# import numpy as np
# from scitex.decorators import deprecated
#
#
# def gen_interpolate(color_start, color_end, num_points, round=3):
#     color_start_rgba = np.array(mcolors.to_rgba(color_start))
#     color_end_rgba = np.array(mcolors.to_rgba(color_end))
#     rgba_values = np.linspace(
#         color_start_rgba, color_end_rgba, num_points
#     ).round(round)
#     return [list(color) for color in rgba_values]
#
#
# @deprecated("Use gen_interpolate instead")
# def interpolate(color_start, color_end, num_points, round=3):
#     return gen_interpolate(color_start, color_end, num_points, round=round)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_interpolate.py
# --------------------------------------------------------------------------------
