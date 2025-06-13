#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__set_supxyt.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__set_supxyt.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.plt.ax._style import format_label


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        pass

    def teardown_method(self):
        # Clean up after tests
        pass

    def test_basic_functionality(self):
        # Test with different input types
        # Current implementation just returns the label unchanged

        # String input
        assert format_label("test_label") == "test_label"

        # Numeric input
        assert format_label(123) == 123

        # Empty string
        assert format_label("") == ""

    def test_edge_cases(self):
        # Test with None
        assert format_label(None) == None

        # Test with special characters
        assert format_label("特殊字符@#$%") == "特殊字符@#$%"

    def test_commented_functionality(self):
        # This tests the currently commented out functionality
        # It's useful to keep these tests for if/when this functionality is uncommented

        # This function should return the input label unchanged with current implementation
        assert format_label("test_label") == "test_label"

        # If uncommented, it would capitalize and replace underscores:
        # assert format_label("test_label") == "Test Label"

        # If uncommented, it would handle uppercase:
        # assert format_label("TEST") == "TEST"

    def test_savefig(self):
        import matplotlib.pyplot as plt
        from scitex.io import save

        # Setup
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [1, 2, 3])

        # Main test functionality
from scitex.plt.ax._style import set_supxyt

        set_supxyt(
            ax,
            xlabel="Super X Label",
            ylabel="Super Y Label",
            title="Super Title",
        )

        # Saving
        spath = f"./{os.path.basename(__file__)}.jpg"
        save(fig, spath)

        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_supxyt.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-07-13 07:56:46 (ywatanabe)"
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
# def set_supxyt(
#     ax, xlabel=False, ylabel=False, title=False, format_labels=True
# ):
#     """Sets xlabel, ylabel and title"""
#     fig = ax.get_figure()
#
#     # if xlabel is not False:
#     #     fig.supxlabel(xlabel)
#
#     # if ylabel is not False:
#     #     fig.supylabel(ylabel)
#
#     # if title is not False:
#     #     fig.suptitle(title)
#     if xlabel is not False:
#         xlabel = format_label(xlabel) if format_labels else xlabel
#         fig.supxlabel(xlabel)
#
#     if ylabel is not False:
#         ylabel = format_label(ylabel) if format_labels else ylabel
#         fig.supylabel(ylabel)
#
#     if title is not False:
#         title = format_label(title) if format_labels else title
#         fig.suptitle(title)
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

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_set_supxyt.py
# --------------------------------------------------------------------------------
