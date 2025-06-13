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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_xyt.py
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
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_xyt.py
# --------------------------------------------------------------------------------
