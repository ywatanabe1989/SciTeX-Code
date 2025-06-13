#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 21:46:06 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/plt/ax/_plot/test__plot_raster.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/ax/_plot/test__plot_raster.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scitex.plt.ax._plot import plot_raster

matplotlib.use("Agg")  # Use non-GUI backend for testing


class TestMainFunctionality:
    def setup_method(self):
        # Setup test fixtures
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        # Sample positions data for testing
        self.positions = [
            [10, 50, 90],  # Channel 1 events
            [20, 60, 100],  # Channel 2 events
            [30, 70, 110],  # Channel 3 events
            [40, 80, 120],  # Channel 4 events
        ]
        # Create output directory if it doesn't exist
        self.out_dir = __file__.replace(".py", "_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def teardown_method(self):
        # Clean up after tests
        plt.close(self.fig)

    def save_test_figure(self, method_name):
        """Helper method to save figure using method name"""
        from scitex.io import save

        spath = f"./{os.path.basename(__file__).replace('.py', '')}_{method_name}.jpg"
        save(self.fig, spath)
        # Check saved file
        actual_spath = os.path.join(self.out_dir, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"

    def test_basic_functionality(self):
        # Test basic plot_raster plot creation
        ax, df = plot_raster(self.ax, self.positions)
        self.ax.set_title("Basic Raster Plot")

        # Save figure
        self.save_test_figure("test_basic_functionality")

        # Check that events were plotted (EventCollection objects added)
        assert len(self.ax.collections) == len(self.positions)
        # Check that df is a DataFrame with the right structure
        assert isinstance(df, pd.DataFrame)
        assert df.shape[1] == len(self.positions)  # Column for each channel
        assert not df.empty

    def test_with_time_parameter(self):
        # Test with custom time parameter
        custom_time = np.linspace(0, 150, 200)
        ax, df = plot_raster(self.ax, self.positions, time=custom_time)
        self.ax.set_title("Raster Plot with Custom Time")

        # Save figure
        self.save_test_figure("test_with_time_parameter")

        # Check that time was used correctly
        assert df.index.equals(pd.Index(custom_time))
        assert len(df) == len(custom_time)

    def test_with_labels(self):
        # Test with channel labels
        labels = ["Channel A", "Channel B", "Channel C", "Channel D"]
        ax, df = plot_raster(self.ax, self.positions, labels=labels)
        self.ax.set_title("Raster Plot with Labels")

        # Save figure
        self.save_test_figure("test_with_labels")

        # Check that a legend was created
        assert self.ax.get_legend() is not None
        # Check that the legend has the right number of entries
        handles, legend_labels = self.ax.get_legend_handles_labels()
        assert len(legend_labels) == len(labels)
        assert all(l1 == l2 for l1, l2 in zip(legend_labels, labels))

    def test_with_colors(self):
        # Test with custom colors
        colors = ["red", "green", "blue", "purple"]
        ax, df = plot_raster(self.ax, self.positions, colors=colors)
        self.ax.set_title("Raster Plot with Custom Colors")

        # Save figure
        self.save_test_figure("test_with_colors")

    def test_with_mixed_types(self):
        # Test with mixed input types (single values and lists)
        mixed_positions = [
            10,  # Single value
            [20, 60],  # List
            30,  # Single value
            [40, 80],  # List
        ]
        ax, df = plot_raster(self.ax, mixed_positions)
        self.ax.set_title("Raster Plot with Mixed Types")

        # Save figure
        self.save_test_figure("test_with_mixed_types")

        # Check that single values were properly handled
        assert len(self.ax.collections) == len(mixed_positions)

    def test_with_kwargs(self):
        # Test with additional kwargs
        ax, df = plot_raster(self.ax, self.positions, linewidths=2.0, linelengths=0.8)
        self.ax.set_title("Raster Plot with Custom Line Properties")

        # Save figure
        self.save_test_figure("test_with_kwargs")

        # # Check that kwargs were applied
        # for collection in self.ax.collections:
        #     assert collection.get_linewidths()[0] == 2.0
        #     assert collection.get_linelengths()[0] == 0.8

    def test_data_processing(self):
        # Check the DataFrame creation logic
        ax, df = plot_raster(self.ax, self.positions)
        self.ax.set_title("Raster Plot Data Processing Test")

        # Save figure
        self.save_test_figure("test_data_processing")

        # Verify that each channel has events marked at the right positions
        time_values = df.index.values
        # Find indices closest to our event positions
        for channel_idx, positions in enumerate(self.positions):
            for pos in positions:
                # Find rows in df where this channel has an event
                events = df[df.iloc[:, channel_idx] == channel_idx]
                # At least one event should be close to each position
                found = False
                for time in events.index:
                    if abs(time - pos) < 2.0:  # Allow some tolerance
                        found = True
                        break
                assert (
                    found
                ), f"No event found near position {pos} for channel {channel_idx}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_raster.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 15:23:01 (ywatanabe)"
# # File: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/ax/_plot/_plot_raster.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/ax/_plot/_plot_raster.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# import matplotlib
#
# from bisect import bisect_left
#
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
#
#
# def plot_raster(
#     ax,
#     event_times,
#     time=None,
#     labels=None,
#     colors=None,
#     orientation="horizontal",
#     **kwargs
# ):
#     """
#     Create a raster plot using eventplot with custom labels and colors.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes on which to draw the raster plot.
#     event_times : Array-like or list of lists
#         Time points of events by channels
#     time : array-like, optional
#         The time indices for the events (default: np.linspace(0, max(event_times))).
#     labels : list, optional
#         Labels for each channel.
#     colors : list, optional
#         Colors for each channel.
#     orientation: str, optional
#         Orientation of raster plot (default: horizontal).
#     **kwargs : dict
#         Additional keyword arguments for eventplot.
#
#     Returns
#     -------
#     ax : matplotlib.axes.Axes
#         The axes with the raster plot.
#     df : pandas.DataFrame
#         DataFrame with time indices and channel events.
#     """
#     assert isinstance(
#         ax, matplotlib.axes._axes.Axes
#     ), "First argument must be a matplotlib axis"
#
#     # Format event_times data
#     event_times_list = _ensure_list(event_times)
#
#     # Handle colors and labels
#     colors = _handle_colors(colors, event_times_list)
#
#     # Plotting as eventplot using event_times_list
#     for ii, (pos, color) in enumerate(zip(event_times_list, colors)):
#         label = _define_label(labels, ii)
#         ax.eventplot(
#             pos, orientation=orientation, colors=color, label=label, **kwargs
#         )
#
#     # Legend
#     if labels is not None:
#         ax.legend()
#
#     # Return event_times in a useful format
#     event_times_digital_df = _event_times_to_digital_df(event_times_list, time)
#
#     return ax, event_times_digital_df
#
#
# def _ensure_list(event_times):
#     return [
#         [pos] if isinstance(pos, (int, float)) else pos for pos in event_times
#     ]
#
#
# def _define_label(labels, ii):
#     if (labels is not None) and (ii < len(labels)):
#         return labels[ii]
#     else:
#         return None
#
#
# def _handle_colors(colors, event_times_list):
#     if colors is None:
#         colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
#     if len(colors) < len(event_times_list):
#         colors = colors * (len(event_times_list) // len(colors) + 1)
#     return colors
#
#
# def _event_times_to_digital_df(event_times_list, time):
#     if time is None:
#         time = np.linspace(
#             0, np.max([np.max(pos) for pos in event_times_list]), 1000
#         )
#
#     digi = np.full((len(event_times_list), len(time)), np.nan, dtype=float)
#
#     for i_ch, posis_ch in enumerate(event_times_list):
#         for posi_ch in posis_ch:
#             i_insert = bisect_left(time, posi_ch)
#             if i_insert == len(time):
#                 i_insert -= 1
#             digi[i_ch, i_insert] = i_ch
#
#     return pd.DataFrame(digi.T, index=time)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_plot/_plot_raster.py
# --------------------------------------------------------------------------------
