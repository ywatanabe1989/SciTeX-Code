#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__add_panel.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__add_panel.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scitex.plt.ax._style import add_panel

matplotlib.use("Agg")


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        pass

    def teardown_method(self):
        # Clean up after tests
        plt.close("all")

    def test_basic_functionality(self):
        # Test with default height parameter (uses H_TO_W_RATIO)
        fig, ax = add_panel(tgt_width_mm=40)

        # Calculate expected dimensions
        H_TO_W_RATIO = 0.7
        MM_TO_INCH_FACTOR = 1 / 25.4
        expected_width_in = 40 * MM_TO_INCH_FACTOR
        expected_height_in = expected_width_in * H_TO_W_RATIO

        # Get actual dimensions
        bbox = ax.get_position()
        fig_width_in, fig_height_in = fig.get_size_inches()
        actual_width_in = bbox.width * fig_width_in
        actual_height_in = bbox.height * fig_height_in

        # Check dimensions are correct (with small tolerance)
        assert np.isclose(actual_width_in, expected_width_in, rtol=1e-4)
        assert np.isclose(actual_height_in, expected_height_in, rtol=1e-4)

        # Check that the axes is properly centered
        center_x = bbox.x0 + bbox.width / 2
        center_y = bbox.y0 + bbox.height / 2
        assert np.isclose(center_x, 0.5, rtol=1e-4)
        assert np.isclose(center_y, 0.5, rtol=1e-4)

        # Clean up
        plt.close(fig)

    def test_custom_dimensions(self):
        # Test with custom width and height
        tgt_width_mm = 50
        tgt_height_mm = 30
        fig, ax = add_panel(tgt_width_mm=tgt_width_mm, tgt_height_mm=tgt_height_mm)

        # Calculate expected dimensions
        MM_TO_INCH_FACTOR = 1 / 25.4
        expected_width_in = tgt_width_mm * MM_TO_INCH_FACTOR
        expected_height_in = tgt_height_mm * MM_TO_INCH_FACTOR

        # Get actual dimensions
        bbox = ax.get_position()
        fig_width_in, fig_height_in = fig.get_size_inches()
        actual_width_in = bbox.width * fig_width_in
        actual_height_in = bbox.height * fig_height_in

        # Check dimensions are correct (with small tolerance)
        assert np.isclose(actual_width_in, expected_width_in, rtol=1e-4)
        assert np.isclose(actual_height_in, expected_height_in, rtol=1e-4)

        # Clean up
        plt.close(fig)

    # def test_aspect_ratio(self):
    #     # Test different aspect ratios
    #     for width_mm, height_mm, expected_ratio in [
    #         (40, 20, 0.5),
    #         (30, 30, 1.0),
    #         (20, 40, 2.0),
    #     ]:
    #         fig, ax = add_panel(tgt_width_mm=width_mm, tgt_height_mm=height_mm)

    #         # Calculate actual aspect ratio
    #         bbox = ax.get_position()
    #         actual_ratio = (bbox.height / bbox.width) * (
    #             fig.get_figwidth() / fig.get_figheight()
    #         )

    #         # Check aspect ratio is correct
    #         assert np.isclose(actual_ratio, expected_ratio, rtol=1e-2)

    #         # Clean up
    #         plt.close(fig)

    def test_plotting_compatibility(self):
        # Test that the returned axis can be used for plotting
        fig, ax = add_panel(tgt_width_mm=40)

        # Try different plotting methods
        ax.plot([1, 2, 3], [4, 5, 6])
        ax.scatter([1, 2, 3], [4, 5, 6])
        ax.bar([1, 2, 3], [4, 5, 6])

        # Check that plots were added to the axis
        assert len(ax.lines) > 0
        assert len(ax.collections) > 0
        assert len(ax.patches) > 0

        # Clean up
        plt.close(fig)

    def test_savefig(self):
        from scitex.io import save

        # Main test functionality
        fig, ax = add_panel(tgt_width_mm=40)
        ax.plot([1, 2, 3], [1, 2, 3])
        ax.set_title("Panel Test")

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
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_add_panel.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 21:24:49 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_panel.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_panel.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# # Time-stamp: "2024-02-03 15:34:08 (ywatanabe)"
#
# import matplotlib.pyplot as plt
# from scitex.decorators import deprecated
#
#
# def add_panel(tgt_width_mm=40, tgt_height_mm=None):
#     """Creates a fixed-size ax figure for panels."""
#
#     H_TO_W_RATIO = 0.7
#     MM_TO_INCH_FACTOR = 1 / 25.4
#
#     if tgt_height_mm is None:
#         tgt_height_mm = H_TO_W_RATIO * tgt_width_mm
#
#     # Convert target dimensions from millimeters to inches
#     tgt_width_in = tgt_width_mm * MM_TO_INCH_FACTOR
#     tgt_height_in = tgt_height_mm * MM_TO_INCH_FACTOR
#
#     # Create a figure with the specified dimensions
#     fig = plt.figure(figsize=(tgt_width_in * 2, tgt_height_in * 2))
#
#     # Calculate the position and size of the axes in figure units (0 to 1)
#     left = (fig.get_figwidth() - tgt_width_in) / 2 / fig.get_figwidth()
#     bottom = (fig.get_figheight() - tgt_height_in) / 2 / fig.get_figheight()
#     ax = fig.add_axes(
#         [
#             left,
#             bottom,
#             tgt_width_in / fig.get_figwidth(),
#             tgt_height_in / fig.get_figheight(),
#         ]
#     )
#
#     return fig, ax
#
#
# @deprecated("Use add_panel instead")
# def panel(tgt_width_mm=40, tgt_height_mm=None):
#     return add_panel(tgt_width_mm=40, tgt_height_mm=None)
#
#
# if __name__ == "__main__":
#     # Example usage:
#     fig, ax = panel(tgt_width_mm=40, tgt_height_mm=40 * 0.7)
#     ax.plot([1, 2, 3], [4, 5, 6])
#     ax.scatter([1, 2, 3], [4, 5, 6])
#     # ... compatible with other ax plotting methods as well
#     plt.show()
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_add_panel.py
# --------------------------------------------------------------------------------
