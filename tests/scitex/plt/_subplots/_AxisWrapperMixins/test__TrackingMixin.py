#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 12:35:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test__TrackingMixin.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/_subplots/_AxisWrapperMixins/test__TrackingMixin.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tracking_mixin_instance():
    """Fixture that creates a simple TrackingMixin instance for testing."""
    from scitex.plt._subplots._AxisWrapperMixins import TrackingMixin

    class TestTrackingMixin(TrackingMixin):
        def __init__(self):
            self.axis = MagicMock()
            self.track = True
            self.id = 0
            self._ax_history = {}

    return TestTrackingMixin()


def test_track_method_with_tracking_enabled(tracking_mixin_instance):
    """Tests that _track method correctly stores history when tracking is enabled."""
    # Setup
    instance = tracking_mixin_instance
    instance.track = True
    method_name = "test_method"
    args = ([1, 2, 3], [4, 5, 6])
    kwargs = {"color": "red", "marker": "o"}
    plot_id = "test_plot"

    # Execute
    instance._track(True, plot_id, method_name, args, kwargs)

    # Verify
    assert plot_id in instance._ax_history
    assert instance._ax_history[plot_id] == (
        plot_id,
        method_name,
        args,
        kwargs,
    )


def test_track_method_with_tracking_disabled(tracking_mixin_instance):
    """Tests that _track method does not store history when tracking is disabled."""
    # Setup
    instance = tracking_mixin_instance
    instance.track = False
    method_name = "test_method"
    args = ([1, 2, 3], [4, 5, 6])
    kwargs = {"color": "red"}
    plot_id = "test_plot"

    # Execute
    instance._track(False, plot_id, method_name, args, kwargs)

    # Verify
    assert plot_id not in instance._ax_history


def test_track_method_with_id_from_kwargs(tracking_mixin_instance):
    """Tests that _track method extracts id from kwargs if present."""
    # Setup
    instance = tracking_mixin_instance
    method_name = "test_method"
    args = ([1, 2, 3],)
    kwargs = {"color": "blue", "id": "kwargs_id"}

    # Execute
    instance._track(True, None, method_name, args, kwargs)

    # Verify
    assert "kwargs_id" in instance._ax_history
    assert "id" not in kwargs  # id should have been removed from kwargs


def test_no_tracking_context_manager(tracking_mixin_instance):
    """Tests that _no_tracking context manager temporarily disables tracking."""
    # Setup
    instance = tracking_mixin_instance
    instance.track = True

    # Execute
    with instance._no_tracking():
        tracking_during = instance.track
    tracking_after = instance.track

    # Verify
    assert tracking_during is False
    assert tracking_after is True


def test_history_property(tracking_mixin_instance):
    """Tests that history property returns the correct dictionary."""
    # Setup
    instance = tracking_mixin_instance
    instance._ax_history = {
        "plot1": ("plot1", "method1", ([1, 2], [3, 4]), {}),
        "plot2": ("plot2", "method2", ([5, 6], [7, 8]), {"color": "red"}),
    }

    # Execute
    history = instance.history

    # Verify
    assert history == instance._ax_history
    assert "plot1" in history
    assert "plot2" in history


def test_reset_history(tracking_mixin_instance):
    """Tests that reset_history clears the history."""
    # Setup
    instance = tracking_mixin_instance
    instance._ax_history = {
        "plot1": ("plot1", "method1", ([1, 2], [3, 4]), {}),
    }

    # Execute
    instance.reset_history()

    # Verify
    assert instance._ax_history == {}


# def test_export_as_csv_method(tracking_mixin_instance):
#     """Tests that export_as_csv method correctly converts history to DataFrame."""
#     # Setup
#     instance = tracking_mixin_instance
#     history_data = {
#         "plot1": ("plot1", "plot", ([1, 2, 3], [4, 5, 6]), {}),
#     }
#     instance._ax_history = history_data

#     # Mock the _export_as_csv function
#     expected_df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})

#     with patch(
#         "scitex.plt._subplots._AxisWrapperMixins._TrackingMixin.TrackingMixin.export_as_csv",
#         return_value=expected_df,
#     ) as mock_export_as_csv:
#         # Execute
#         result = instance.export_as_csv()

#         # Verify
#         mock_export_as_csv.assert_called_once_with(history_data)
#         pd.testing.assert_frame_equal(result, expected_df)


# def test_flat_property_with_single_axis(tracking_mixin_instance):
#     """Tests that flat property returns a list with a single axis."""
#     # Setup
#     instance = tracking_mixin_instance
#     instance.axis = MagicMock()

#     # Execute
#     flat_result = instance.flat

#     # Verify
#     assert isinstance(flat_result, list)
#     assert len(flat_result) == 1
#     assert flat_result[0] == instance.axis


# def test_flat_property_with_multiple_axes(tracking_mixin_instance):
#     """Tests that flat property returns the axis list when axis is already a list."""
#     # Setup
#     instance = tracking_mixin_instance
#     axis_list = [MagicMock(), MagicMock()]
#     instance.axis = axis_list

#     # Execute
#     flat_result = instance.flat

#     # Verify
#     assert flat_result is axis_list


# def test_export_as_csv_with_none_result(tracking_mixin_instance):
#     """Tests that export_as_csv returns empty DataFrame when _export_as_csv returns None."""
#     # Setup
#     instance = tracking_mixin_instance

#     with patch(
#         "scitex.plt._subplots._AxisWrapperMixins._export_as_csv.export_as_csv",
#         return_value=None,
#     ) as mock_export_as_csv:
#         # Execute
#         result = instance.export_as_csv()

#         # Verify
#         assert isinstance(result, pd.DataFrame)
#         assert result.empty

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-30 18:40:59 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# """
# Functionality:
#     * Handles tracking and history management for matplotlib plot operations
# Input:
#     * Plot method calls, their arguments, and tracking configuration
# Output:
#     * Tracked plotting history and DataFrame export for analysis
# Prerequisites:
#     * pandas, matplotlib
# """
#
# from contextlib import contextmanager
#
# import pandas as pd
#
# from .._export_as_csv import export_as_csv as _export_as_csv
#
#
# class TrackingMixin:
#     """Mixin class for tracking matplotlib plotting operations.
#
#     Example
#     -------
#     >>> fig, ax = plt.subplots()
#     >>> ax.track = True
#     >>> ax.id = 0
#     >>> ax._ax_history = OrderedDict()
#     >>> ax.plot([1, 2, 3], [4, 5, 6], id="plot1")
#     >>> print(ax.history)
#     {'plot1': ('plot1', 'plot', ([1, 2, 3], [4, 5, 6]), {})}
#     """
#
#     def _track(self, track, id, method_name, args, kwargs):
#         # Extract id from kwargs and remove it before passing to matplotlib
#         if hasattr(kwargs, "get") and "id" in kwargs:
#             id = kwargs.pop("id")
#
#         if track is None:
#             track = self.track
#
#         if track:
#             id = id if id is not None else self.id
#             self.id += 1
#             self._ax_history[id] = (id, method_name, args, kwargs)
#
#     @contextmanager
#     def _no_tracking(self):
#         """Context manager to temporarily disable tracking."""
#         original_track = self.track
#         self.track = False
#         try:
#             yield
#         finally:
#             self.track = original_track
#
#     @property
#     def history(self):
#         return {k: self._ax_history[k] for k in self._ax_history}
#
#     @property
#     def flat(self):
#         if isinstance(self._axis_mpl, list):
#             return self._axis_mpl
#         else:
#             return [self._axis_mpl]
#
#     def reset_history(self):
#         self._ax_history = {}
#
#     def export_as_csv(self):
#         """
#         Export tracked plotting data to a DataFrame in SigmaPlot format.
#         """
#         df = _export_as_csv(self.history)
#
#         return df if df is not None else pd.DataFrame()
#
#     # def _track(
#     #     self,
#     #     track: Optional[bool],
#     #     plot_id: Optional[str],
#     #     method_name: str,
#     #     args: Any,
#     #     kwargs: Dict[str, Any]
#     # ) -> None:
#     #     """Tracks plotting operation if tracking is enabled."""
#     #     if track is None:
#     #         track = self.track
#     #     if track:
#     #         plot_id = plot_id if plot_id is not None else self.id
#     #         self.id += 1
#     #         self._ax_history[plot_id] = (plot_id, method_name, args, kwargs)
#
#     # @contextmanager
#     # def _no_tracking(self) -> None:
#     #     """Temporarily disables tracking within a context."""
#     #     original_track = self.track
#     #     self.track = False
#     #     try:
#     #         yield
#     #     finally:
#     #         self.track = original_track
#
#     # @property
#     # def history(self) -> Dict[str, Tuple]:
#     #     """Returns the plotting history."""
#     #     return dict(self._ax_history)
#
#     # def reset_history(self) -> None:
#     #     """Clears the plotting history."""
#     #     self._ax_history = OrderedDict()
#
#     # def export_as_csv(self) -> pd.DataFrame:
#     #     """Converts plotting history to a SigmaPlot-compatible DataFrame."""
#     #     df = _export_as_csv(self.history)
#     #     return df if df is not None else pd.DataFrame()
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_AxisWrapperMixins/_TrackingMixin.py
# --------------------------------------------------------------------------------
