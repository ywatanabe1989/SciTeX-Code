#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 23:16:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/color/test__vizualize_colors.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/color/test__vizualize_colors.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

matplotlib.use("Agg")  # Use non-interactive backend for testing


def test_vizualize_colors():
    from scitex.plt.color import vizualize_colors

    test_colors = {"blue": [0, 0.5, 0.75, 0.9], "red": [1, 0.27, 0.2, 0.9]}

    fig, ax = vizualize_colors(test_colors)

    from scitex.io import save

    spath = (
        f"./{os.path.basename(__file__).replace('.py', '')}_test_vizualize_colors.jpg"
    )
    save(fig, spath)
    # Check saved file
    out_dir = __file__.replace(".py", "_out")
    actual_spath = os.path.join(out_dir, spath)
    assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


def test_vizualize_colors_return_types():
    """Test that vizualize_colors returns correct types."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {"green": [0, 1, 0, 1], "yellow": [1, 1, 0, 1]}
    fig, ax = vizualize_colors(test_colors)
    
    # Check return types
    assert isinstance(fig, plt.Figure)
    assert hasattr(ax, 'plot')  # Check it's an axes-like object
    
    plt.close(fig)


def test_vizualize_colors_empty_dict():
    """Test vizualize_colors with empty dictionary."""
    from scitex.plt.color import vizualize_colors
    
    fig, ax = vizualize_colors({})
    
    # Should still return valid figure and axes
    assert isinstance(fig, plt.Figure)
    assert hasattr(ax, 'plot')
    
    # Should have no legend entries
    legend = ax.get_legend()
    if legend is not None:
        assert len(legend.get_texts()) == 0
    
    plt.close(fig)


def test_vizualize_colors_single_color():
    """Test vizualize_colors with single color."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {"purple": [0.5, 0, 0.5, 1]}
    fig, ax = vizualize_colors(test_colors)
    
    # Check that legend has one entry
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 1
    assert legend.get_texts()[0].get_text() == "purple"
    
    plt.close(fig)


def test_vizualize_colors_many_colors():
    """Test vizualize_colors with many colors."""
    from scitex.plt.color import vizualize_colors
    
    # Create 10 colors
    test_colors = {}
    for i in range(10):
        color_name = f"color_{i}"
        # Create gradual color transition
        r = i / 9
        g = 1 - i / 9
        b = 0.5
        test_colors[color_name] = [r, g, b, 1]
    
    fig, ax = vizualize_colors(test_colors)
    
    # Check that all colors are in legend
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 10
    
    plt.close(fig)


def test_vizualize_colors_rgb_values():
    """Test vizualize_colors with RGB values (no alpha)."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {
        "rgb_red": [1, 0, 0],  # 3 values
        "rgb_green": [0, 1, 0],  # 3 values
    }
    
    # Should handle RGB values without error
    fig, ax = vizualize_colors(test_colors)
    assert isinstance(fig, plt.Figure)
    
    plt.close(fig)


def test_vizualize_colors_different_alpha():
    """Test vizualize_colors with different alpha values."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {
        "opaque": [1, 0, 0, 1.0],
        "semi_transparent": [0, 1, 0, 0.5],
        "very_transparent": [0, 0, 1, 0.1],
    }
    
    fig, ax = vizualize_colors(test_colors)
    
    # Check that all colors appear in legend
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 3
    
    plt.close(fig)


def test_vizualize_colors_grayscale():
    """Test vizualize_colors with grayscale colors."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {
        "black": [0, 0, 0, 1],
        "dark_gray": [0.25, 0.25, 0.25, 1],
        "gray": [0.5, 0.5, 0.5, 1],
        "light_gray": [0.75, 0.75, 0.75, 1],
        "white": [1, 1, 1, 1],
    }
    
    fig, ax = vizualize_colors(test_colors)
    
    # Verify all grayscale colors are shown
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 5
    
    plt.close(fig)


def test_vizualize_colors_special_names():
    """Test vizualize_colors with special characters in color names."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {
        "color-with-dashes": [1, 0, 0, 1],
        "color_with_underscores": [0, 1, 0, 1],
        "color.with.dots": [0, 0, 1, 1],
        "color with spaces": [1, 1, 0, 1],
        "#FF00FF": [1, 0, 1, 1],  # Hex-like name
    }
    
    fig, ax = vizualize_colors(test_colors)
    
    # Check all names appear correctly
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 5
    
    # Check that special characters are preserved
    legend_texts = [t.get_text() for t in legend.get_texts()]
    assert "color-with-dashes" in legend_texts
    assert "color_with_underscores" in legend_texts
    assert "color.with.dots" in legend_texts
    assert "color with spaces" in legend_texts
    assert "#FF00FF" in legend_texts
    
    plt.close(fig)


def test_vizualize_colors_plot_properties():
    """Test that plot properties are set correctly."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {
        "test_red": [1, 0, 0, 1],
        "test_blue": [0, 0, 1, 1],
    }
    
    fig, ax = vizualize_colors(test_colors)
    
    # Check that axes has plot elements
    assert len(ax.lines) > 0 or len(ax.collections) > 0
    
    # Check that x and y limits are set
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    assert xlim[0] < xlim[1]
    assert ylim[0] < ylim[1]
    
    plt.close(fig)


def test_vizualize_colors_invalid_rgba_values():
    """Test vizualize_colors with invalid RGBA values."""
    from scitex.plt.color import vizualize_colors
    
    # Test with values outside [0, 1] range
    test_colors = {
        "too_high": [1.5, 0, 0, 1],  # R > 1
        "negative": [0, -0.5, 0, 1],  # G < 0
    }
    
    # Should handle invalid values (matplotlib will clamp them)
    fig, ax = vizualize_colors(test_colors)
    assert isinstance(fig, plt.Figure)
    
    plt.close(fig)


def test_vizualize_colors_reproducibility():
    """Test that vizualize_colors produces consistent results with same seed."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {"color1": [1, 0, 0, 1], "color2": [0, 1, 0, 1]}
    
    # Set random seed for reproducibility
    np.random.seed(42)
    fig1, ax1 = vizualize_colors(test_colors)
    
    # Reset seed and create again
    np.random.seed(42)
    fig2, ax2 = vizualize_colors(test_colors)
    
    # Both figures should have same number of plot elements
    assert len(ax1.lines) == len(ax2.lines)
    assert len(ax1.collections) == len(ax2.collections)
    
    plt.close(fig1)
    plt.close(fig2)


def test_vizualize_colors_figure_size():
    """Test that figure has reasonable size."""
    from scitex.plt.color import vizualize_colors
    
    test_colors = {"test": [0.5, 0.5, 0.5, 1]}
    fig, ax = vizualize_colors(test_colors)
    
    # Check figure size is reasonable
    size = fig.get_size_inches()
    assert size[0] > 0 and size[1] > 0
    assert size[0] < 20 and size[1] < 20  # Not too large
    
    plt.close(fig)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_vizualize_colors.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 00:53:43 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/color/_vizualize_colors.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/color/_vizualize_colors.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import numpy as np
#
#
# def vizualize_colors(colors):
#
#     def gen_rand_sample(size=100):
#         x = np.linspace(-1, 1, size)
#         y = np.random.normal(size=size)
#         s = np.random.randn(size)
#         return x, y, s
#
#     from .. import subplots as scitex_plt_subplots
#
#     fig, ax = scitex_plt_subplots()
#
#     for ii, (color_str, rgba) in enumerate(colors.items()):
#         xx, yy, ss = gen_rand_sample()
#
#         # # Box color plot
#         # ax.plot_rectangle(
#         #     xx=ii, yy=0, width=1, height=1, color=rgba, label=color_str
#         # )
#
#         # Line plot
#         ax.plot_shaded_line(
#             xx, yy - ss, yy, yy + ss, color=rgba, label=color_str
#         )
#
#         # # Scatter plot
#         # axes[2].scatter(xx, yy, color=rgba, label=color_str)
#
#         # # KDE plot
#         # axes[3].plot_kde(yy, color=rgba, label=color_str)
#
#     # for ax in axes.flat:
#     #     # ax.axis("off")
#     #     ax.legend()
#
#     ax.legend()
#     # plt.tight_layout()
#     # plt.show()
#     return fig, ax
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/color/_vizualize_colors.py
# --------------------------------------------------------------------------------
