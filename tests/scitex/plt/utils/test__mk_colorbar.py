#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 01:09:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/utils/test__mk_colorbar.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/utils/test__mk_colorbar.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import pytest
import numpy as np
import gc


def test_mk_colorbar():
    from scitex.plt.utils import mk_colorbar

    # Test with default colors
    fig = mk_colorbar()

    # Check that it returns a figure
    assert isinstance(fig, plt.Figure)

    # Check with custom colors
    fig = mk_colorbar(start="red", end="green")
    assert isinstance(fig, plt.Figure)

    plt.close("all")


def test_mk_colorbar_default_colors():
    """Test mk_colorbar with default white to blue gradient."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar()
    
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    
    # Check that image is displayed
    assert len(ax.images) == 1
    
    # Check gradient shape
    image_data = ax.images[0].get_array()
    assert image_data.shape == (1, 256)
    
    # Check gradient values
    assert image_data.min() == 0.0
    assert image_data.max() == 1.0
    
    plt.close(fig)


def test_mk_colorbar_custom_colors():
    """Test mk_colorbar with various custom color combinations."""
    from scitex.plt.utils import mk_colorbar
    
    color_pairs = [
        ("black", "white"),
        ("red", "blue"),
        ("green", "yellow"),
        ("purple", "orange"),
        ("navy", "pink"),
        ("brown", "light_blue")
    ]
    
    for start, end in color_pairs:
        fig = mk_colorbar(start=start, end=end)
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)


def test_mk_colorbar_same_color():
    """Test mk_colorbar when start and end colors are the same."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar(start="blue", end="blue")
    
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    
    # With same color, gradient should be uniform
    image_data = ax.images[0].get_array()
    assert image_data.std() < 1e-10  # Should be nearly constant
    
    plt.close(fig)


def test_mk_colorbar_figure_properties():
    """Test figure properties of mk_colorbar output."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar()
    
    # Check figure size
    assert fig.get_figwidth() == 6
    assert fig.get_figheight() == 1
    
    # Check axis properties
    ax = fig.axes[0]
    assert len(ax.get_xticks()) == 0
    assert len(ax.get_yticks()) == 0
    
    plt.close(fig)


def test_mk_colorbar_gray_grey_equivalence():
    """Test that gray and grey produce the same colorbar."""
    from scitex.plt.utils import mk_colorbar
    
    fig1 = mk_colorbar(start="gray", end="white")
    fig2 = mk_colorbar(start="grey", end="white")
    
    # Get image data from both
    data1 = fig1.axes[0].images[0].get_array()
    data2 = fig2.axes[0].images[0].get_array()
    
    # Should be identical
    assert np.allclose(data1, data2)
    
    plt.close(fig1)
    plt.close(fig2)


def test_mk_colorbar_invalid_color():
    """Test mk_colorbar with invalid color names."""
    from scitex.plt.utils import mk_colorbar
    
    with pytest.raises(KeyError):
        mk_colorbar(start="invalid_color", end="blue")
    
    with pytest.raises(KeyError):
        mk_colorbar(start="white", end="invalid_color")


def test_mk_colorbar_gradient_direction():
    """Test gradient direction from start to end color."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar(start="black", end="white")
    ax = fig.axes[0]
    
    # Get the colormap from the image
    image = ax.images[0]
    cmap = image.get_cmap()
    
    # Check that gradient goes from black to white
    # At 0, should be close to black
    start_color = cmap(0.0)
    assert np.allclose(start_color[:3], [0, 0, 0], atol=0.1)
    
    # At 1, should be close to white
    end_color = cmap(1.0)
    assert np.allclose(end_color[:3], [1, 1, 1], atol=0.1)
    
    plt.close(fig)


def test_mk_colorbar_colormap_properties():
    """Test properties of the generated colormap."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar(start="red", end="blue")
    ax = fig.axes[0]
    
    # Get the colormap
    image = ax.images[0]
    cmap = image.get_cmap()
    
    # Check colormap properties
    assert cmap.N == 256  # Number of levels
    assert cmap.name == "custom_cmap"
    
    plt.close(fig)


def test_mk_colorbar_aspect_ratio():
    """Test that the colorbar has appropriate aspect ratio."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar()
    ax = fig.axes[0]
    
    # Check that aspect is set to auto
    assert ax.get_aspect() == "auto"
    
    # Check that the image fills the axes
    image = ax.images[0]
    extent = image.get_extent()
    assert extent is not None
    
    plt.close(fig)


def test_mk_colorbar_no_ticks():
    """Test that colorbar has no ticks as intended."""
    from scitex.plt.utils import mk_colorbar
    
    fig = mk_colorbar()
    ax = fig.axes[0]
    
    # Should have no x or y ticks
    assert len(ax.get_xticks()) == 0
    assert len(ax.get_yticks()) == 0
    
    # Check tick labels are also empty
    assert len(ax.get_xticklabels()) == 0
    assert len(ax.get_yticklabels()) == 0
    
    plt.close(fig)


def test_mk_colorbar_rgb_normalization():
    """Test that RGB values are properly normalized in the colormap."""
    from scitex.plt.utils import mk_colorbar
from scitex.plt.color import RGB
    
    # Test with colors that have known RGB values
    fig = mk_colorbar(start="red", end="blue")
    ax = fig.axes[0]
    
    # Get the colormap
    cmap = ax.images[0].get_cmap()
    
    # Check start color (red)
    start_rgba = cmap(0.0)
    expected_red = np.array(RGB["red"]) / 255.0
    assert np.allclose(start_rgba[:3], expected_red, atol=0.01)
    
    # Check end color (blue)
    end_rgba = cmap(1.0)
    expected_blue = np.array(RGB["blue"]) / 255.0
    assert np.allclose(end_rgba[:3], expected_blue, atol=0.01)
    
    plt.close(fig)


def test_mk_colorbar_memory_cleanup():
    """Test that figures are properly cleaned up."""
    from scitex.plt.utils import mk_colorbar
    
    initial_figs = plt.get_fignums()
    
    # Create and close multiple colorbars
    for _ in range(5):
        fig = mk_colorbar()
        plt.close(fig)
    
    # Force garbage collection
    gc.collect()
    
    # Check no figures are left open
    final_figs = plt.get_fignums()
    assert len(final_figs) == len(initial_figs)


if __name__ == "__main__":
    import pytest
    
    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_mk_colorbar.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 01:09:23 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/utils/_mk_colorbar.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/utils/_mk_colorbar.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# # def mk_colorbar(start="white", end="blue"):
# #     xx = np.linspace(0, 1, 256)
#
# #     start = np.array(scitex.plt.colors.RGB[start])
# #     end = np.array(scitex.plt.colors.RGB[end])
# #     colors = (end - start)[:, np.newaxis] * xx
#
# #     colors -= colors.min()
# #     colors /= colors.max()
#
# #     fig, ax = plt.subplots()
# #     [ax.axvline(_xx, color=colors[:, i_xx]) for i_xx, _xx in enumerate(xx)]
# #     ax.xaxis.set_ticks_position("none")
# #     ax.yaxis.set_ticks_position("none")
# #     ax.set_aspect(0.2)
# #     return fig
#
#
# def mk_colorbar(start="white", end="blue"):
#     """Create a colorbar gradient between two colors.
#
#     Args:
#         start (str): Starting color name
#         end (str): Ending color name
#
#     Returns:
#         matplotlib.figure.Figure: Figure with colorbar
#     """
#     import matplotlib.colors as mcolors
#     import matplotlib.pyplot as plt
#     import numpy as np
#     # import scitex
#     from scitex.plt.color._PARAMS import RGB
#
#     # Get RGB values for start and end colors
#     start_rgb = RGB[start]
#     end_rgb = RGB[end]
#
#     # Create a colormap
#     colors = [start_rgb, end_rgb]
#     cmap = mcolors.LinearSegmentedColormap.from_list(
#         "custom_cmap", colors, N=256
#     )
#
#     # Create the figure and plot the colorbar
#     fig, ax = plt.subplots(figsize=(6, 1))
#     gradient = np.linspace(0, 1, 256).reshape(1, -1)
#     ax.imshow(gradient, aspect="auto", cmap=cmap)
#     ax.set_xticks([])
#     ax.set_yticks([])
#
#     return fig
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/utils/_mk_colorbar.py
# --------------------------------------------------------------------------------
