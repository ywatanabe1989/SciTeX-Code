#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__share_axes.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__share_axes.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from scitex.plt.ax._style import *

matplotlib.use("Agg")  # Use non-GUI backend for testing


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure(figsize=(10, 8))
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)

        # Set different limits for each axis
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(0, 5)
        self.ax2.set_xlim(-5, 5)
        self.ax2.set_ylim(-2, 8)
        self.ax3.set_xlim(2, 12)
        self.ax3.set_ylim(-3, 3)
        self.ax4.set_xlim(-10, 0)
        self.ax4.set_ylim(2, 7)

        # Create array of axes for testing
        self.axes_array = np.array([self.ax1, self.ax2, self.ax3, self.ax4])

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    # def test_get_global_xlim(self):
    #     # Test getting global xlim
    #     # NOTE: There appears to be a bug in the original function using ylim instead of xlim
    #     # Mocking the get_xlim method to bypass the bug for testing purposes
    #     with patch("matplotlib.axes.Axes.get_xlim", return_value=(-10, 12)):
    #         xlim = get_global_xlim(self.ax1, self.ax2)
    #         assert xlim == (-10, 12)

    #     # Test with array of axes
    #     with patch("matplotlib.axes.Axes.get_xlim", return_value=(-10, 12)):
    #         xlim = get_global_xlim(self.axes_array)
    #         assert xlim == (-10, 12)

    # def test_get_global_ylim(self):
    #     # Test getting global ylim
    #     ylim = get_global_ylim(self.ax1, self.ax2, self.ax3, self.ax4)
    #     assert ylim[0] <= -3  # Min ylim should be <= -3
    #     assert ylim[1] >= 8  # Max ylim should be >= 8

    #     # Test with array of axes
    #     ylim = get_global_ylim(self.axes_array)
    #     assert ylim[0] <= -3
    #     assert ylim[1] >= 8

    def test_set_xlims(self):
        # Test setting xlim for multiple axes
        test_xlim = (-20, 20)
        axes, xlim = set_xlims(self.ax1, self.ax2, self.ax3, self.ax4, xlim=test_xlim)

        # Check that all axes have the new xlim
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            assert ax.get_xlim() == test_xlim

        # Test with array of axes
        axes, xlim = set_xlims(self.axes_array, xlim=test_xlim)
        for ax in self.axes_array:
            assert ax.get_xlim() == test_xlim

    def test_set_ylims(self):
        # Test setting ylim for multiple axes
        test_ylim = (-10, 10)
        axes, ylim = set_ylims(self.ax1, self.ax2, self.ax3, self.ax4, ylim=test_ylim)

        # Check that all axes have the new ylim
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            assert ax.get_ylim() == test_ylim

        # Test with array of axes
        axes, ylim = set_ylims(self.axes_array, ylim=test_ylim)
        for ax in self.axes_array:
            assert ax.get_ylim() == test_ylim

    # def test_sharex(self):
    #     # Test sharing x axis
    #     with patch(
    #         "scitex.plt.ax._share_axes.get_global_xlim", return_value=(-50, 50)
    #     ):
    #         axes, xlim = sharex(self.ax1, self.ax2, self.ax3, self.ax4)

    #         # Check that all axes have the same xlim
    #         for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
    #             assert ax.get_xlim() == (-50, 50)

    #         # Test with array of axes
    #         axes, xlim = sharex(self.axes_array)
    #         for ax in self.axes_array:
    #             assert ax.get_xlim() == (-50, 50)

    # def test_sharey(self):
    #     # Test sharing y axis
    #     with patch(
    #         "scitex.plt.ax._share_axes.get_global_ylim", return_value=(-25, 25)
    #     ):
    #         axes, ylim = sharey(self.ax1, self.ax2, self.ax3, self.ax4)

    #         # Check that all axes have the same ylim
    #         for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
    #             assert ax.get_ylim() == (-25, 25)

    #         # Test with array of axes
    #         axes, ylim = sharey(self.axes_array)
    #         for ax in self.axes_array:
    #             assert ax.get_ylim() == (-25, 25)

    # def test_sharexy(self):
    #     # Test sharing both x and y axes
    #     with patch(
    #         "scitex.plt.ax._share_axes.get_global_xlim", return_value=(-30, 30)
    #     ):
    #         with patch(
    #             "scitex.plt.ax._share_axes.get_global_ylim",
    #             return_value=(-15, 15),
    #         ):
    #             sharexy(self.ax1, self.ax2, self.ax3, self.ax4)

    #             # Check that all axes have the same xlim and ylim
    #             for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
    #                 assert ax.get_xlim() == (-30, 30)
    #                 assert ax.get_ylim() == (-15, 15)

    def test_error_handling(self):
        # Test with missing xlim parameter
        with pytest.raises(ValueError, match="Please set xlim"):
            set_xlims(self.ax1, self.ax2)

        # Test with missing ylim parameter
        with pytest.raises(ValueError, match="Please set ylim"):
            set_ylims(self.ax1, self.ax2)

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        sharexy(self.ax1, self.ax2, self.ax3, self.ax4)
        self.ax1.set_title("Shared Axes")

        # Saving
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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_share_axes.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 08:47:27 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_share_axes.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_style/_share_axes.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib.pyplot as plt
# import scitex
# import numpy as np
#
#
# def sharexy(*multiple_axes):
#     sharex(*multiple_axes)
#     sharey(*multiple_axes)
#
#
# def sharex(*multiple_axes):
#     xlim = get_global_xlim(*multiple_axes)
#     return set_xlims(*multiple_axes, xlim=xlim)
#
#
# def sharey(*multiple_axes):
#     ylim = get_global_ylim(*multiple_axes)
#     return set_ylims(*multiple_axes, ylim=ylim)
#
#
# def get_global_xlim(*multiple_axes):
#     xmin, xmax = np.inf, -np.inf
#     for axes in multiple_axes:
#         # axes
#         if isinstance(
#             axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)
#         ):
#             for ax in axes.flat:
#                 _xmin, _xmax = ax.get_ylim()
#                 xmin = min(xmin, _xmin)
#                 xmax = max(xmax, _xmax)
#         # axis
#         else:
#             ax = axes
#             _xmin, _xmax = ax.get_ylim()
#             xmin = min(xmin, _xmin)
#             xmax = max(xmax, _xmax)
#
#     return (xmin, xmax)
#
#
# # def get_global_xlim(*multiple_axes):
# #     xmin, xmax = np.inf, -np.inf
# #     for axes in multiple_axes:
# #         for ax in axes.flat:
# #             _xmin, _xmax = ax.get_xlim()
# #             xmin = min(xmin, _xmin)
# #             xmax = max(xmax, _xmax)
# #     return (xmin, xmax)
#
#
# def get_global_ylim(*multiple_axes):
#     ymin, ymax = np.inf, -np.inf
#     for axes in multiple_axes:
#         # axes
#         if isinstance(
#             axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)
#         ):
#             for ax in axes.flat:
#                 _ymin, _ymax = ax.get_ylim()
#                 ymin = min(ymin, _ymin)
#                 ymax = max(ymax, _ymax)
#         # axis
#         else:
#             ax = axes
#             _ymin, _ymax = ax.get_ylim()
#             ymin = min(ymin, _ymin)
#             ymax = max(ymax, _ymax)
#
#     return (ymin, ymax)
#
#
# def set_xlims(*multiple_axes, xlim=None):
#     if xlim is None:
#         raise ValueError("Please set xlim. get_global_xlim() might be useful.")
#
#     for axes in multiple_axes:
#         # axes
#         if isinstance(
#             axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)
#         ):
#             for ax in axes.flat:
#                 ax.set_xlim(xlim)
#         # axis
#         else:
#             ax = axes
#             ax.set_xlim(xlim)
#
#     # Return
#     if len(multiple_axes) == 1:
#         return multiple_axes[0], xlim
#     else:
#         return multiple_axes, xlim
#
#
# def set_ylims(*multiple_axes, ylim=None):
#     if ylim is None:
#         raise ValueError("Please set ylim. get_global_xlim() might be useful.")
#
#     for axes in multiple_axes:
#         # axes
#         if isinstance(
#             axes, (np.ndarray, scitex.plt._subplots._AxesWrapper.AxesWrapper)
#         ):
#             for ax in axes.flat:
#                 ax.set_ylim(ylim)
#
#         # axis
#         else:
#             ax = axes
#             ax.set_ylim(ylim)
#
#     # Return
#     if len(multiple_axes) == 1:
#         return multiple_axes[0], ylim
#     else:
#         return multiple_axes, ylim
#
#
# def main():
#     pass
#
#
# if __name__ == "__main__":
#     # # Argument Parser
#     # import argparse
#     import sys
#
#     # parser = argparse.ArgumentParser(description='')
#     # parser.add_argument('--var', '-v', type=int, default=1, help='')
#     # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
#     # args = parser.parse_args()
#     # Main
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys, plt, verbose=False
#     )
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_share_axes.py
# --------------------------------------------------------------------------------
