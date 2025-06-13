#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 12:35:50 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/_subplots/test__FigWrapper.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/_subplots/test__FigWrapper.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pytest

# class TestFigWrapper:
#     def setup_method(self):
#         self.fig = plt.figure()
#         self.wrapper = FigWrapper(self.fig)

#     def test_init(self):
#         assert self.wrapper.fig is self.fig
#         assert hasattr(self.wrapper, "axes")
#         assert self.wrapper.axes == []

#     def test_getattr_existing_attribute(self):
#         # Test accessing an existing attribute on the figure
#         assert hasattr(self.wrapper, "figsize")

#     def test_getattr_existing_method(self):
#         # Test accessing an existing method on the figure
#         assert callable(self.wrapper.add_subplot)

#     def test_getattr_warning(self):
#         # Test attempting to access a non-existent attribute
#         with pytest.warns(UserWarning, match="not implemented, ignored"):
#             result = self.wrapper.nonexistent_method()
#             assert result is None

#     def test_legend(self):
#         # Create mock axes
#         ax1 = MagicMock()
#         ax2 = MagicMock()
#         self.wrapper.axes = MagicMock()
#         self.wrapper.axes.__iter__ = lambda _: iter([ax1, ax2])

#         # Call legend
#         self.wrapper.legend(loc="upper right")

#         # Check that legend was called on each axis
#         ax1.legend.assert_called_once_with(loc="upper right")
#         ax2.legend.assert_called_once_with(loc="upper right")

#     def test_export_as_csv_with_empty_axes(self):
#         # Test with no axes
#         self.wrapper.axes = MagicMock()
#         self.wrapper.axes.flat = []

#         result = self.wrapper.export_as_csv()
#         assert isinstance(result, pd.DataFrame)
#         assert result.empty

#     def test_export_as_csv_with_data(self):
#         # Create mock axes with sigma data
#         ax1 = MagicMock()
#         ax1.export_as_csv.return_value = pd.DataFrame(
#             {"x": [1, 2, 3], "y": [4, 5, 6]}
#         )

#         self.wrapper.axes = MagicMock()
#         self.wrapper.axes.flat = [ax1]

#         result = self.wrapper.export_as_csv()
#         assert isinstance(result, pd.DataFrame)
#         assert not result.empty
#         assert "ax_00_x" in result.columns
#         assert "ax_00_y" in result.columns

#     def test_supxyt(self):
#         # Test supxyt method
#         self.wrapper.fig = MagicMock()

#         # Call with x and y labels
#         self.wrapper.supxyt(x="X Label", y="Y Label")

#         # Check that appropriate methods were called
#         self.wrapper.fig.supxlabel.assert_called_once_with("X Label")
#         self.wrapper.fig.supylabel.assert_called_once_with("Y Label")
#         self.wrapper.fig.suptitle.assert_not_called()

#         # Reset and test with title
#         self.wrapper.fig.reset_mock()
#         self.wrapper.supxyt(t="Title")

#         self.wrapper.fig.supxlabel.assert_not_called()
#         self.wrapper.fig.supylabel.assert_not_called()
#         self.wrapper.fig.suptitle.assert_called_once_with("Title")

#     def test_tight_layout(self):
#         # Test tight_layout method
#         self.wrapper.fig = MagicMock()

#         # Call with default rect
#         self.wrapper.tight_layout()

#         # Check that tight_layout was called with the correct rect
#         self.wrapper.fig.tight_layout.assert_called_once_with(
#             rect=[0, 0.03, 1, 0.95]
#         )

#         # Reset and test with custom rect
#         self.wrapper.fig.reset_mock()
#         custom_rect = [0.1, 0.1, 0.9, 0.9]
#         self.wrapper.tight_layout(rect=custom_rect)

#         self.wrapper.fig.tight_layout.assert_called_once_with(rect=custom_rect)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_FigWrapper.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 14:56:48 (ywatanabe)"
# # File: /home/ywatanabe/proj/_scitex_repo/src/scitex/plt/_subplots/_FigWrapper.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/_subplots/_FigWrapper.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# from functools import wraps
#
# import pandas as pd
#
#
# class FigWrapper:
#     def __init__(self, fig_mpl):
#         self._fig_mpl = fig_mpl
#         self._last_saved_info = None
#         self._not_saved_yet_flag = True
#         self._called_from_mng_io_save = False
#
#     @property
#     def figure(
#         self,
#     ):
#         return self._fig_mpl
#
#     def __getattr__(self, attr):
#         # print(f"Attribute of FigWrapper: {attr}")
#         attr_mpl = getattr(self._fig_mpl, attr)
#
#         if callable(attr_mpl):
#
#             @wraps(attr_mpl)
#             def wrapper(*args, track=None, id=None, **kwargs):
#                 results = attr_mpl(*args, **kwargs)
#                 # self._track(track, id, attr, args, kwargs)
#                 return results
#
#             return wrapper
#
#         else:
#             return attr_mpl
#
#     def __dir__(self):
#         # Combine attributes from both self and the wrapped matplotlib figure
#         attrs = set(dir(self.__class__))
#         attrs.update(object.__dir__(self))
#         attrs.update(dir(self._fig_mpl))
#         return sorted(attrs)
#
#     # def savefig(self, fname, *args, **kwargs):
#     #     if not self._called_from_mng_io_save:
#     #         warnings.warn(
#     #             f"Instead of `FigWrapper.savefig({fname})`, use `scitex.io.save(fig, {fname}, symlink_from_cwd=True)` to handle symlink and export as csv.",
#     #             UserWarning,
#     #         )
#     #         self._called_from_mng_io_save = False
#     #     self._fig_mpl.savefig(fname, *args, **kwargs)
#
#     def export_as_csv(self):
#         """Export plotted data from all axes."""
#         dfs = []
#         for ii, ax in enumerate(self.axes.flat):
#             if hasattr(ax, "export_as_csv"):
#                 df = ax.export_as_csv()
#                 if not df.empty:
#                     df.columns = [f"ax_{ii:02d}_{col}" for col in df.columns]
#                     dfs.append(df)
#
#         return pd.concat(dfs, axis=1) if dfs else pd.DataFrame()
#
#     def legend(self, *args, loc="upper left", **kwargs):
#         """Legend with upper left by default."""
#         for ax in self.axes:
#             try:
#                 ax.legend(*args, loc=loc, **kwargs)
#             except:
#                 pass
#
#     def supxyt(self, x=False, y=False, t=False):
#         """Wrapper for supxlabel, supylabel, and suptitle"""
#         if x is not False:
#             self._fig_mpl.supxlabel(x)
#         if y is not False:
#             self._fig_mpl.supylabel(y)
#         if t is not False:
#             self._fig_mpl.suptitle(t)
#         return self._fig_mpl
#
#     def tight_layout(self, *, rect=[0, 0.03, 1, 0.95], **kwargs):
#         """Wrapper for tight_layout with rect=[0, 0.03, 1, 0.95] by default"""
#         self._fig_mpl.tight_layout(rect=rect, **kwargs)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/_subplots/_FigWrapper.py
# --------------------------------------------------------------------------------
