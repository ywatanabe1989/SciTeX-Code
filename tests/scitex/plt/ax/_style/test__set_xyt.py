#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__set_xyt.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__set_xyt.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
from scitex.plt.ax._style import set_xyt

matplotlib.use("Agg")


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_basic_functionality(self):
        # Test setting all three labels
        ax = set_xyt(self.ax, x="Test X", y="Test Y", t="Test Title")

        assert ax.get_xlabel() == "Test X"
        assert ax.get_ylabel() == "Test Y"
        assert ax.get_title() == "Test Title"

    def test_partial_labels(self):
        # Test setting only some labels
        ax1 = set_xyt(self.ax, x="Only X")
        assert ax1.get_xlabel() == "Only X"
        assert ax1.get_ylabel() == ""
        assert ax1.get_title() == ""

        ax2 = set_xyt(self.ax, y="Only Y")
        assert ax2.get_xlabel() == "Only X"  # Still has previous value
        assert ax2.get_ylabel() == "Only Y"
        assert ax2.get_title() == ""

        ax3 = set_xyt(self.ax, t="Only Title")
        assert ax3.get_xlabel() == "Only X"  # Still has previous value
        assert ax3.get_ylabel() == "Only Y"  # Still has previous value
        assert ax3.get_title() == "Only Title"

    # def test_format_labels_option(self):
    #     # Test with format_labels=False
    #     with patch(
    #         "scitex.plt.ax._format_label.format_label",
    #         side_effect=lambda x: x.upper(),
    #     ):
    #         # When format_labels=True, it should call format_label
    #         ax1 = set_xyt(
    #             self.ax, x="test", y="test", t="test", format_labels=True
    #         )
    #         assert ax1.get_xlabel() == "TEST"
    #         assert ax1.get_ylabel() == "TEST"
    #         assert ax1.get_title() == "TEST"

    #         # When format_labels=False, it should not call format_label
    #         ax2 = set_xyt(
    #             self.ax, x="test", y="test", t="test", format_labels=False
    #         )
    #         assert ax2.get_xlabel() == "test"
    #         assert ax2.get_ylabel() == "test"
    #         assert ax2.get_title() == "test"

    def test_edge_cases(self):
        # Test with False values (which should skip setting those labels)
        ax = set_xyt(self.ax, x=False, y=False, t=False)
        assert ax.get_xlabel() == ""
        assert ax.get_ylabel() == ""
        assert ax.get_title() == ""

        # Test with empty strings
        ax = set_xyt(self.ax, x="", y="", t="")
        assert ax.get_xlabel() == ""
        assert ax.get_ylabel() == ""
        assert ax.get_title() == ""

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        self.ax.plot([1, 2, 3], [1, 2, 3])
        set_xyt(self.ax, x="X Label", y="Y Label", t="Test Title")

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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_xyt.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-07-13 08:14:19 (ywatanabe)"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
# 
# """
# This script does XYZ.
# """
# 
# # Imports
# import matplotlib.pyplot as plt
# 
# from ._format_label import format_label
# 
# 
# # Functions
# def set_xyt(ax, x=False, y=False, t=False, format_labels=True):
#     """Sets xlabel, ylabel and title"""
# 
#     if x is not False:
#         x = format_label(x) if format_labels else x
#         ax.set_xlabel(x)
# 
#     if y is not False:
#         y = format_label(y) if format_labels else y
#         ax.set_ylabel(y)
# 
#     if t is not False:
#         t = format_label(t) if format_labels else t
#         ax.set_title(t)
# 
#     return ax
# 
# 
# def set_xytc(ax, x=False, y=False, t=False, c=False, methods=False, stats=False, format_labels=True):
#     """Sets xlabel, ylabel, title, and caption with SciTeX-Paper integration
#     
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         The axes to modify
#     x : str or False, optional
#         X-axis label, by default False
#     y : str or False, optional 
#         Y-axis label, by default False
#     t : str or False, optional
#         Title, by default False
#     c : str or False, optional
#         Caption to store for later use with scitex.io.save(), by default False
#     methods : str or False, optional
#         Methods description for SciTeX-Paper integration, by default False
#     stats : str or False, optional
#         Statistical analysis details for SciTeX-Paper integration, by default False
#     format_labels : bool, optional
#         Whether to apply automatic formatting, by default True
#         
#     Returns
#     -------
#     ax : matplotlib.axes.Axes or scitex AxisWrapper
#         The modified axes
#         
#     Examples
#     --------
#     >>> fig, ax = scitex.plt.subplots()
#     >>> ax.plot(x, y)
#     >>> ax.set_xytc(x='Time (s)', y='Voltage (mV)', 
#     ...             t='Neural Signal', 
#     ...             c='Example neural recording showing action potentials.',
#     ...             methods='Intracellular recordings performed using patch-clamp technique.',
#     ...             stats='Data analyzed using t-test with p<0.05 significance.')
#     >>> scitex.io.save(fig, 'neural_signal.png')  # Caption automatically saved
#     """
#     # Set labels and title using existing function
#     set_xyt(ax, x=x, y=y, t=t, format_labels=format_labels)
#     
#     # Store caption and extended metadata for later use by scitex.io.save()
#     if c is not False or methods is not False or stats is not False:
#         # Store comprehensive metadata as axis attribute for retrieval by save function
#         metadata = {
#             'caption': c if c is not False else None,
#             'methods': methods if methods is not False else None,
#             'stats': stats if stats is not False else None
#         }
#         
#         if hasattr(ax, '_scitex_metadata'):
#             ax._scitex_metadata.update(metadata)
#         else:
#             # For matplotlib axes, store in figure metadata
#             fig = ax.get_figure()
#             if not hasattr(fig, '_scitex_metadata'):
#                 fig._scitex_metadata = {}
#             # Use axis position as identifier
#             fig._scitex_metadata[ax] = metadata
#             
#         # Backward compatibility - also store simple caption
#         if c is not False:
#             if hasattr(ax, '_scitex_caption'):
#                 ax._scitex_caption = c
#             else:
#                 fig = ax.get_figure()
#                 if not hasattr(fig, '_scitex_captions'):
#                     fig._scitex_captions = {}
#                 fig._scitex_captions[ax] = c
#     
#     return ax
# 
# 
# if __name__ == "__main__":
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # (YOUR AWESOME CODE)
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/plt/ax/_set_lt.py
# """

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_set_xyt.py
# --------------------------------------------------------------------------------
