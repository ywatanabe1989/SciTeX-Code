#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-02 09:02:28 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_adjust/test__map_ticks.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_adjust/test__map_ticks.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")  # Use non-GUI backend for testing

import pytest
from scitex.plt.ax._style import map_ticks


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def test_numeric_mapping_x_axis(self):
        # Create a plot with numeric x-axis
        xx = np.linspace(0, 2 * np.pi, 100)
        yy = np.sin(xx)
        self.ax.plot(xx, yy)

        # Define mapping points and labels
        src = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
        tgt = ["0", "π/2", "π", "3π/2", "2π"]

        # Apply mapping
        ax = map_ticks(self.ax, src, tgt, axis="x")

        # Force draw to update tick labels
        self.fig.canvas.draw()

        # Get tick positions and labels
        tick_positions = ax.get_xticks()
        tick_labels = [label.get_text() for label in ax.get_xticklabels()]

        # Check that ticks were set correctly
        assert len(tick_positions) == len(src)
        assert np.allclose(tick_positions, src)
        assert tick_labels == tgt

    def test_numeric_mapping_y_axis(self):
        # Create a plot with numeric y-axis
        xx = np.linspace(0, 2 * np.pi, 100)
        yy = np.sin(xx)
        self.ax.plot(xx, yy)

        # Define mapping points and labels
        src = [-1, -0.5, 0, 0.5, 1]
        tgt = ["-1.0", "-0.5", "0.0", "0.5", "1.0"]

        # Apply mapping
        ax = map_ticks(self.ax, src, tgt, axis="y")

        # Force draw to update tick labels
        self.fig.canvas.draw()

        # Get tick positions and labels
        tick_positions = ax.get_yticks()
        tick_labels = [label.get_text() for label in ax.get_yticklabels()]

        # Check that ticks were set correctly
        assert len(tick_positions) == len(src)
        assert np.allclose(tick_positions, src)
        assert tick_labels == tgt

    def test_string_mapping_x_axis(self):
        # Create a categorical plot
        categories = ["A", "B", "C", "D", "E"]
        values = [1, 3, 2, 5, 4]
        self.ax.bar(categories, values)

        # Force draw to ensure tick labels are created
        self.fig.canvas.draw()

        # Define mapping
        src = categories
        tgt = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]

        # Apply mapping
        ax = map_ticks(self.ax, src, tgt, axis="x")

        # Force draw again to update tick labels
        self.fig.canvas.draw()

        # Get tick labels
        tick_labels = [label.get_text() for label in ax.get_xticklabels()]

        # Check that labels were mapped correctly
        assert tick_labels == tgt

    def test_mismatched_lengths(self):
        """Test when source and target have different lengths."""
        import re

        # Create mismatched input
        src = [1, 2, 3]
        tgt = [4, 5]

        # Should raise ValueError
        with pytest.raises(
            ValueError,
        ):
            map_ticks(self.ax, src, tgt)

    def test_invalid_axis(self):
        # Test error with invalid axis parameter
        src = [0, 1, 2]
        tgt = ["A", "B", "C"]

        # Should raise ValueError
        with pytest.raises(ValueError, match="Invalid axis"):
            map_ticks(self.ax, src, tgt, axis="z")

    def test_partial_string_mapping(self):
        # Create a categorical plot
        categories = ["A", "B", "C", "D", "E"]
        values = [1, 3, 2, 5, 4]
        self.ax.bar(categories, values)

        # Force draw to ensure tick labels are created
        self.fig.canvas.draw()

        # Define partial mapping (only some categories)
        src = ["A", "C", "E"]
        tgt = ["Alpha", "Gamma", "Epsilon"]

        # Apply mapping
        ax = map_ticks(self.ax, src, tgt, axis="x")

        # Force draw again to update tick labels
        self.fig.canvas.draw()

        # Get tick labels and positions
        tick_labels = [label.get_text() for label in ax.get_xticklabels()]
        tick_positions = ax.get_xticks()

        # Check results
        assert len(tick_positions) == len(src)
        assert tick_labels == tgt

    def test_savefig(self):
        import numpy as np
        from scitex.io import save

        # Setup plot with data
        xx = np.linspace(0, 2 * np.pi, 100)
        yy = np.sin(xx)
        self.ax.plot(xx, yy)

        # Main test functionality
        src = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
        tgt = ["0", "π/2", "π", "3π/2", "2π"]
        map_ticks(self.ax, src, tgt, axis="x")

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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_map_ticks.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-02 09:00:56 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/ax/_style/_map_ticks.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/ax/_style/_map_ticks.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import matplotlib
# import matplotlib.pyplot as plt
# import numpy as np
# 
# from ....plt.utils import assert_valid_axis
# 
# 
# def map_ticks(ax, src, tgt, axis="x"):
#     """
#     Maps source tick positions or labels to new target labels on a matplotlib Axes object.
#     Supports both numeric positions and string labels for source ticks ('src'), enabling the mapping
#     to new target labels ('tgt'). This ensures only the specified target ticks are displayed on the
#     final axis, enhancing the clarity and readability of plots.
# 
#     Parameters:
#     - ax (matplotlib.axes.Axes or scitex.plt._subplots._AxisWrapper.AxisWrapper): The Axes object to modify.
#     - src (list of str or numeric): Source positions (if numeric) or labels (if str) to map from.
#       When using string labels, ensure they match the current tick labels on the axis.
#     - tgt (list of str): New target labels to apply to the axis. Must have the same length as 'src'.
#     - axis (str): Specifies which axis to apply the tick modifications ('x' or 'y').
# 
#     Returns:
#     - ax (matplotlib.axes.Axes or scitex.plt._subplots._AxisWrapper.AxisWrapper): The modified Axes object with adjusted tick labels.
# 
#     Examples:
#     --------
#     Numeric Example:
#         fig, ax = plt.subplots()
#         x = np.linspace(0, 2 * np.pi, 100)
#         y = np.sin(x)
#         ax.plot(x, y)  # Plot a sine wave
#         src = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]  # Numeric src positions
#         tgt = ['0', 'π/2', 'π', '3π/2', '2π']  # Corresponding target labels
#         map_ticks(ax, src, tgt, axis="x")  # Map src to tgt on the x-axis
#         plt.show()
# 
#     String Example:
#         fig, ax = plt.subplots()
#         categories = ['A', 'B', 'C', 'D', 'E']  # Initial categories
#         values = [1, 3, 2, 5, 4]
#         ax.bar(categories, values)  # Bar plot with string labels
#         src = ['A', 'B', 'C', 'D', 'E']  # Source labels to map from
#         tgt = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']  # New target labels
#         map_ticks(ax, src, tgt, axis="x")  # Apply the mapping
#         plt.show()
#     """
#     assert_valid_axis(ax, "First argument must be a matplotlib axis or scitex axis wrapper")
# 
#     if len(src) != len(tgt):
#         raise ValueError(
#             "Source ('src') and target ('tgt') must have the same number of elements."
#         )
# 
#     # Determine tick positions if src is string data
#     if all(isinstance(item, str) for item in src):
#         if axis == "x":
#             all_labels = [label.get_text() for label in ax.get_xticklabels()]
#         else:
#             all_labels = [label.get_text() for label in ax.get_yticklabels()]
# 
#         # Find positions of src labels
#         src_positions = [all_labels.index(s) for s in src if s in all_labels]
#     else:
#         # Use src as positions directly if numeric
#         src_positions = src
# 
#     # Set the ticks and labels based on the specified axis
#     if axis == "x":
#         ax.set_xticks(src_positions)
#         ax.set_xticklabels(tgt)
#     elif axis == "y":
#         ax.set_yticks(src_positions)
#         ax.set_yticklabels(tgt)
#     else:
#         raise ValueError("Invalid axis argument. Use 'x' or 'y'.")
# 
#     return ax
# 
# 
# def numeric_example():
#     """Example demonstrating numeric tick mapping.
# 
#     Shows how to replace numeric tick positions with custom labels,
#     such as replacing radian values with pi notation in trigonometric plots.
# 
#     Returns
#     -------
#     matplotlib.figure.Figure
#         Figure with two subplots showing before and after tick mapping.
# 
#     Examples
#     --------
#     >>> fig = numeric_example()
#     >>> plt.show()
# 
#     Notes
#     -----
#     The top subplot shows original numeric labels, while the bottom
#     subplot shows the same data with custom pi notation labels.
#     """
#     fig, axs = plt.subplots(2, 1, figsize=(10, 6))  # Two rows, one column
# 
#     # Original plot
#     x = np.linspace(0, 2 * np.pi, 100)
#     y = np.sin(x)
#     axs[0].plot(x, y)  # Plot a sine wave on the first row
#     axs[0].set_title("Original Numeric Labels")
# 
#     # Numeric src positions for ticks (e.g., multiples of pi) and target labels
#     src = [0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]
#     tgt = ["0", "π/2", "π", "3π/2", "2π"]
# 
#     # Plot with mapped ticks
#     axs[1].plot(x, y)  # Plot again on the second row for mapped labels
#     map_ticks(axs[1], src, tgt, axis="x")
#     axs[1].set_title("Mapped Numeric Labels")
# 
#     return fig
# 
# 
# def string_example():
#     """Example demonstrating string tick mapping.
# 
#     Shows how to replace categorical string labels with more descriptive
#     alternatives, useful for improving plot readability.
# 
#     Returns
#     -------
#     matplotlib.figure.Figure
#         Figure with two subplots showing before and after tick mapping.
# 
#     Examples
#     --------
#     >>> fig = string_example()
#     >>> plt.show()
# 
#     Notes
#     -----
#     The top subplot shows original short category labels (A, B, C...),
#     while the bottom subplot shows the same data with descriptive Greek
#     letter names.
#     """
#     fig, axs = plt.subplots(2, 1, figsize=(10, 6))  # Two rows, one column
# 
#     # Original plot with categorical string labels
#     categories = ["A", "B", "C", "D", "E"]
#     values = [1, 3, 2, 5, 4]
#     axs[0].bar(categories, values)
#     axs[0].set_title("Original String Labels")
# 
#     # src as the existing labels to change and target labels
#     src = categories
#     tgt = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
# 
#     # Plot with mapped string labels
#     axs[1].bar(categories, values)  # Bar plot again on the second row for mapped labels
#     map_ticks(axs[1], src, tgt, axis="x")
#     axs[1].set_title("Mapped String Labels")
# 
#     return fig
# 
# 
# # Execute examples
# if __name__ == "__main__":
#     fig_numeric = numeric_example()
#     fig_string = string_example()
# 
#     plt.tight_layout()
#     plt.show()
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/ax/_style/_map_ticks.py
# --------------------------------------------------------------------------------
