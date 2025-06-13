#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 21:54:49 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_plot/test__plot_image.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_image.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")
import pytest
from scitex.plt.ax._plot import plot_image


class TestPlotImage:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.data_2d = np.random.rand(10, 20)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test basic display with default parameters
        ax = plot_image(self.ax, self.data_2d)

        # Check that there's an image
        assert len(ax.images) == 1

        # Check that y-axis is inverted
        assert ax.get_ylim()[0] < ax.get_ylim()[1]

        # Check that colorbar is shown
        assert len(self.fig.axes) > 1

    def test_without_colorbar(self):
        # Test without colorbar
        ax = plot_image(self.ax, self.data_2d, cbar=False)

        # Check that no colorbar is added
        assert len(self.fig.axes) == 1

    def test_with_colorbar_label(self):
        # Test with colorbar label
        cbar_label = "Test Label"
        ax = plot_image(self.ax, self.data_2d, cbar_label=cbar_label)

        # Check that colorbar label is correctly set
        colorbar_axes = None
        for axes in self.fig.axes:
            if axes != self.ax:
                colorbar_axes = axes
                break

        assert colorbar_axes is not None
        # Note: Colorbar label is attached to the colorbar axes
        assert colorbar_axes.get_ylabel() == cbar_label

    def test_with_custom_cmap(self):
        # Test with custom colormap
        custom_cmap = "hot"
        ax = plot_image(self.ax, self.data_2d, cmap=custom_cmap)

        # Check that the colormap is correctly set
        assert ax.images[0].get_cmap().name == custom_cmap

    def test_with_custom_vmin_vmax(self):
        # Test with custom vmin and vmax
        vmin, vmax = 0.2, 0.8
        ax = plot_image(self.ax, self.data_2d, vmin=vmin, vmax=vmax)

        # Check that vmin and vmax are correctly set
        assert ax.images[0].norm.vmin == vmin
        assert ax.images[0].norm.vmax == vmax

    def test_error_handling(self):
        # Test with invalid input
        with pytest.raises(AssertionError):
            # Should fail with 1D array
            plot_image(self.ax, np.random.rand(10))

        with pytest.raises(AssertionError):
            # Should fail with 3D array
            plot_image(self.ax, np.random.rand(10, 20, 3))

    def test_plot_image_savefig(self):
        ax = plot_image(self.ax, self.data_2d, cbar_label="Values")

        # Saving
        from scitex.io import save

        spath = f"./{os.path.basename(__file__)}.jpg"
        save(self.fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_image.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 08:39:46 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_plot/_plot_image2d.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_image2d.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib
#
#
# def plot_image(
#     ax,
#     arr_2d,
#     cbar=True,
#     cbar_label=None,
#     cbar_shrink=1.0,
#     cbar_fraction=0.046,
#     cbar_pad=0.04,
#     cmap="viridis",
#     aspect="auto",
#     vmin=None,
#     vmax=None,
#     **kwargs,
# ):
#     """
#     Imshows an two-dimensional array with theese two conditions:
#     1) The first dimension represents the x dim, from left to right.
#     2) The second dimension represents the y dim, from bottom to top
#     """
#     assert isinstance(ax, matplotlib.axes._axes.Axes)
#     assert arr_2d.ndim == 2
#
#     if kwargs.get("xyz"):
#         kwargs.pop("xyz")
#
#     # Transposes arr_2d for correct orientation
#     arr_2d = arr_2d.T
#
#     # Cals the original ax.imshow() method on the transposed array
#     im = ax.imshow(
#         arr_2d, cmap=cmap, vmin=vmin, vmax=vmax, aspect=aspect, **kwargs
#     )
#
#     # Color bar
#     if cbar:
#         fig = ax.get_figure()
#         _cbar = fig.colorbar(
#             im, ax=ax, shrink=cbar_shrink, fraction=cbar_fraction, pad=cbar_pad
#         )
#         if cbar_label:
#             _cbar.set_label(cbar_label)
#
#     # Invert y-axis to match typical image orientation
#     ax.invert_yaxis()
#
#     return ax
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_image.py
# --------------------------------------------------------------------------------
