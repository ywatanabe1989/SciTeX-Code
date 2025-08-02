#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 01:07:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/utils/test__configure_mpl.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/utils/test__configure_mpl.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import matplotlib.pyplot as plt
import pytest
from scitex.plt.utils import configure_mpl
from scitex.plt.utils._configure_mpl import _convert_font_size


def test_convert_font_size_string():
    """Tests font size conversion from string values."""
    assert _convert_font_size("xx-small") == 9
    assert _convert_font_size("x-small") == 11
    assert _convert_font_size("small") == 13
    assert _convert_font_size("medium") == 15
    assert _convert_font_size("large") == 18
    assert _convert_font_size("x-large") == 22
    assert _convert_font_size("xx-large") == 26
    assert _convert_font_size("unknown") == 15  # Default for unknown strings


def test_convert_font_size_numeric():
    """Tests font size conversion from numeric values."""
    assert _convert_font_size(10) == 10.0
    assert _convert_font_size(14.5) == 14.5
    assert _convert_font_size(8) == 9.0  # Minimum size enforced
    assert isinstance(_convert_font_size(10), float)


def test_convert_font_size_invalid():
    """Tests error handling for invalid font size types."""
    with pytest.raises(ValueError):
        _convert_font_size(None)

    with pytest.raises(ValueError):
        _convert_font_size([10])


def test_configure_mpl_basic():
    """Tests basic configuration of matplotlib."""
    original_rcparams = plt.rcParams.copy()

    try:
        # Run with default parameters
        plt_result, colors = configure_mpl(plt)

        # Check that plt was returned correctly
        assert plt_result is plt

        # Check that colors dictionary is not empty
        assert isinstance(colors, dict)
        assert len(colors) > 0

        # Check that rcParams were updated
        assert plt.rcParams["figure.dpi"] == 100
        assert plt.rcParams["savefig.dpi"] == 300
        assert plt.rcParams["font.size"] == 15.0  # Default 'medium'
    finally:
        # Restore original settings
        plt.rcParams.update(original_rcparams)


def test_configure_mpl_custom_params():
    """Tests configuration with custom parameters."""
    original_rcparams = plt.rcParams.copy()

    try:
        # Run with custom parameters
        plt_result, colors = configure_mpl(
            plt,
            fig_size_mm=(200, 150),
            dpi_display=150,
            dpi_save=600,
            fontsize="large",
            hide_top_right_spines=False,
            line_width=1.0,
            alpha=0.7,
        )

        # Check that custom parameters were applied
        assert plt.rcParams["figure.dpi"] == 150
        assert plt.rcParams["savefig.dpi"] == 600
        assert plt.rcParams["font.size"] == 18.0  # 'large'
        assert plt.rcParams["lines.linewidth"] == 1.0
        assert plt.rcParams["axes.spines.top"] == True  # Not hidden
        assert plt.rcParams["axes.spines.right"] == True  # Not hidden

        # Check figure size conversion (mm to inches)
        assert plt.rcParams["figure.figsize"][0] == pytest.approx(200 / 25.4)
        assert plt.rcParams["figure.figsize"][1] == pytest.approx(150 / 25.4)
    finally:
        # Restore original settings
        plt.rcParams.update(original_rcparams)


def test_configure_mpl_font_scaling():
    """Tests correct scaling of font sizes relative to base size."""
    original_rcparams = plt.rcParams.copy()
    try:
        # Use a specific base size
        plt_result, colors = configure_mpl(plt, fontsize=12)

        # Check that derived font sizes are correctly scaled
        assert plt.rcParams["font.size"] == 12.0  # Base size
        assert plt.rcParams["axes.titlesize"] == 15.0  # 125% of base
        assert plt.rcParams["axes.labelsize"] == 12.0  # 100% of base
        assert plt.rcParams["xtick.labelsize"] == max(
            12.0 * 0.85, 8.0
        )  # 85% of base, min 8.0
        assert plt.rcParams["ytick.labelsize"] == max(
            12.0 * 0.85, 8.0
        )  # 85% of base, min 8.0
        assert plt.rcParams["legend.fontsize"] == max(
            12.0 * 0.85, 8.0
        )  # 85% of base, min 8.0
    finally:
        # Restore original settings
        plt.rcParams.update(original_rcparams)


def test_configure_mpl_verbose_output(capsys):
    """Tests that verbose mode prints configuration details."""
    original_rcparams = plt.rcParams.copy()

    try:
        # Run with verbose output
        plt_result, colors = configure_mpl(plt, verbose=True)

        # Capture printed output
        captured = capsys.readouterr()

        # Verify key information is in the output
        assert "Matplotlib has been configured as follows" in captured.out
        assert "Figure DPI (Display): 100 DPI" in captured.out
        assert "Figure DPI (Save): 300 DPI" in captured.out
        assert "Base Size: 15.0pt" in captured.out
        assert "Hide Top and Right Axes: True" in captured.out
        assert "Custom Colors (RGBA)" in captured.out
    finally:
        # Restore original settings
        plt.rcParams.update(original_rcparams)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_configure_mpl.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-19 08:49:35 (ywatanabe)"
# # File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/scitex_repo/src/scitex/plt/utils/_configure_mpl.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/plt/utils/_configure_mpl.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from typing import Any, Dict, Tuple, Union
# 
# import matplotlib.pyplot as plt
# import scitex
# import numpy as np
# 
# 
# def configure_mpl(
#     plt,
#     fig_size_mm=(160, 100),
#     fig_scale=1.0,
#     dpi_display=100,
#     dpi_save=300,
#     fontsize="medium",
#     autolayout=True,
#     n_ticks=4,
#     hide_top_right_spines=True,
#     line_width=1.0,  # Increased from 0.5 for better visibility
#     alpha=0.85,  # Adjusted for better contrast
#     enable_latex=True,  # Enable LaTeX rendering by default
#     latex_preamble=None,  # Custom LaTeX preamble
#     verbose=False,
#     **kwargs,
# ) -> Tuple[Any, Dict]:
#     """Configures Matplotlib settings for publication-quality plots.
# 
#     Parameters
#     ----------
#     plt : matplotlib.pyplot
#         Matplotlib pyplot module
#     fig_size_mm : tuple of int, optional
#         Figure width and height in millimeters, by default (160, 100)
#     fig_scale : float, optional
#         Scaling factor for figure size, by default 1.0
#     dpi_display : int, optional
#         Display resolution in DPI, by default 100
#     dpi_save : int, optional
#         Saving resolution in DPI, by default 300
#     fontsize : Union[str, int, float], optional
#         Base font size ('xx-small' to 'xx-large' or points), by default 'medium'
#         Other sizes are derived from this:
#         - Title: 125% of base
#         - Labels: 100% of base
#         - Ticks/Legend: 85% of base
#     autolayout : bool, optional
#         Whether to enable automatic tight layout, by default True
#     hide_top_right_spines : bool, optional
#         Whether to hide top and right spines, by default True
#     line_width : float, optional
#         Default line width, by default 1.0
#     alpha : float, optional
#         Color transparency, by default 0.85
#     n_ticks : int, optional
#         Number of ticks on each axis, by default 4
#     verbose : bool, optional
#         Whether to print configuration details, by default False
# 
#     Returns
#     -------
#     tuple
#         (plt, dict of RGBA colors)
#     """
#     # Convert base font size
#     base_size = _convert_font_size(fontsize)
# 
#     # Ensure minimum sizes for different elements with better proportions
#     title_size = max(base_size * 1.25, 10.0)  # Increased for better hierarchy
#     label_size = max(base_size * 1.0, 9.0)  # Minimum 9pt for good readability
#     small_size = max(base_size * 0.85, 8.0)  # Increased ratio for better legibility
# 
#     # Colors
#     RGBA = {
#         k: scitex.plt.color.update_alpha(v, alpha)
#         for k, v in scitex.plt.color.PARAMS["RGBA"].items()
#     }
# 
#     RGBA_NORM = {
#         k: tuple(scitex.plt.color.update_alpha(v, alpha))
#         for k, v in scitex.plt.color.PARAMS["RGBA_NORM"].items()
#     }
# 
#     RGBA_NORM_FOR_CYCLE = {
#         k: tuple(scitex.plt.color.update_alpha(v, alpha))
#         for k, v in scitex.plt.color.PARAMS["RGBA_NORM_FOR_CYCLE"].items()
#     }
# 
#     # Normalize figure size from mm to inches
#     figsize_inch = (
#         fig_size_mm[0] / 25.4 * fig_scale,
#         fig_size_mm[1] / 25.4 * fig_scale,
#     )
# 
#     # Prepare matplotlib configuration
#     mpl_config = {
#         # Resolution
#         "figure.dpi": dpi_display,
#         "savefig.dpi": dpi_save,
#         # Figure Size
#         "figure.figsize": figsize_inch,
#         # Font Sizes
#         "font.size": base_size,
#         "axes.titlesize": title_size,
#         "axes.labelsize": label_size,
#         "xtick.labelsize": small_size,
#         "ytick.labelsize": small_size,
#         "legend.fontsize": small_size,
#         # Auto Layout
#         "figure.autolayout": autolayout,
#         # Top and Right Axes
#         "axes.spines.top": not hide_top_right_spines,
#         "axes.spines.right": not hide_top_right_spines,
#         # Spine width
#         "axes.linewidth": 0.8,  # Slightly thicker axes lines
#         # Custom color cycle
#         "axes.prop_cycle": plt.cycler(color=list(RGBA_NORM_FOR_CYCLE.values())),
#         # Line
#         "lines.linewidth": line_width,
#         "lines.markersize": 6.0,  # Better default marker size
#         # Grid (if used)
#         "grid.linewidth": 0.6,
#         "grid.alpha": 0.3,
#     }
#     
#     # Configure LaTeX rendering if enabled with enhanced fallback
#     if enable_latex:
#         latex_success = False
#         try:
#             # Try to enable LaTeX rendering
#             test_config = {
#                 "text.usetex": True,
#                 "text.latex.preamble": latex_preamble or r"\usepackage{amsmath}\usepackage{amssymb}",
#                 "font.family": "serif",
#                 "font.serif": ["Computer Modern Roman"],
#                 "mathtext.fontset": "cm",
#             }
#             
#             # Test LaTeX capability before applying
#             with plt.rc_context(test_config):
#                 try:
#                     # Create a test figure to verify LaTeX works
#                     fig, ax = plt.subplots(figsize=(1, 1))
#                     ax.text(0.5, 0.5, r'$x^2 + y^2 = r^2$', usetex=True)
#                     fig.canvas.draw()  # Force rendering
#                     plt.close(fig)
#                     latex_success = True
#                 except Exception as latex_error:
#                     plt.close(fig)
#                     if verbose:
#                         print(f"⚠️  LaTeX test render failed: {latex_error}")
#                     raise latex_error
#             
#             if latex_success:
#                 mpl_config.update(test_config)
#                 if verbose:
#                     print("✅ LaTeX rendering enabled and tested")
#                     
#         except Exception as e:
#             if verbose:
#                 print(f"⚠️  LaTeX rendering failed, falling back to mathtext: {e}")
#                 print("    This may be due to missing LaTeX fonts or Node.js conflicts")
#             
#             # Enhanced fallback to mathtext with better configuration
#             mpl_config.update({
#                 "text.usetex": False,
#                 "mathtext.default": "regular",
#                 "font.family": "serif",
#                 "mathtext.fontset": "cm",
#                 "mathtext.fallback": "cm",  # Fallback font for missing symbols
#             })
#             
#             # Enable LaTeX fallback mode in the str module
#             try:
#                 from scitex.str._latex_fallback import set_fallback_mode
#                 set_fallback_mode("force_mathtext")
#                 if verbose:
#                     print("📝 Enabled automatic LaTeX fallback mode")
#             except ImportError:
#                 if verbose:
#                     print("⚠️  LaTeX fallback module not available")
#                     
#     else:
#         # Use mathtext only with enhanced configuration
#         mpl_config.update({
#             "text.usetex": False,
#             "mathtext.default": "regular",
#             "mathtext.fontset": "cm",
#             "mathtext.fallback": "cm",
#         })
#         
#         # Set fallback mode to mathtext
#         try:
#             from scitex.str._latex_fallback import set_fallback_mode
#             set_fallback_mode("force_mathtext")
#         except ImportError:
#             pass
# 
#     # Update Matplotlib configuration
#     plt.rcParams.update(mpl_config)
# 
#     if verbose:
#         print("\n" + "-" * 40)
#         print("Matplotlib has been configured as follows:\n")
#         print(f"Figure DPI (Display): {dpi_display} DPI")
#         print(f"Figure DPI (Save): {dpi_save} DPI")
#         print(
#             f"Figure Size (Not the Axis Size): "
#             f"{fig_size_mm[0] * fig_scale:.1f} x "
#             f"{fig_size_mm[1] * fig_scale:.1f} mm (width x height)"
#         )
#         print("\nFont Sizes:")
#         print(f"  Base Size: {base_size:.1f}pt")
#         print(f"  Title: {title_size:.1f}pt (125% of base, min 10pt)")
#         print(f"  Axis Labels: {label_size:.1f}pt (100% of base, min 9pt)")
#         print(f"  Tick Labels: {small_size:.1f}pt (85% of base, min 8pt)")
#         print(f"  Legend: {small_size:.1f}pt (85% of base, min 8pt)")
#         print(f"\nHide Top and Right Axes: {hide_top_right_spines}")
#         print(f"Line Width: {line_width}")
#         # print(f"Number of Ticks: {n_ticks}")
#         print(f"\nCustom Colors (RGBA):")
#         for color_str, rgba in RGBA.items():
#             print(f"  {color_str}: {rgba}")
#         print("-" * 40)
# 
#     # Store n_ticks for later use
#     plt._n_ticks = n_ticks
# 
#     # Add a utility function to plt
#     def set_n_ticks(ax, n=None):
#         if n is None:
#             n = plt._n_ticks
#         ax.xaxis.set_major_locator(plt.MaxNLocator(n))
#         ax.yaxis.set_major_locator(plt.MaxNLocator(n))
# 
#     plt.set_n_ticks = set_n_ticks
# 
#     return plt, RGBA_NORM
# 
# 
# def _convert_font_size(size: Union[str, int, float]) -> float:
#     """Converts various font size specifications to numerical values.
# 
#     Parameters
#     ----------
#     size : Union[str, int, float]
#         Font size specification. Can be:
#         - String: 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'
#         - Numeric: direct point size value
# 
#     Returns
#     -------
#     float
#         Font size in points
#     """
#     if isinstance(size, str):
#         size_map = {
#             "xx-small": 9,
#             "x-small": 11,
#             "small": 13,
#             "medium": 15,
#             "large": 18,
#             "x-large": 22,
#             "xx-large": 26,
#         }
#         return size_map.get(size.lower(), 15)
#     elif isinstance(size, (int, float)):
#         return max(float(size), 9.0)  # Ensure minimum size of 9
#     else:
#         raise ValueError(f"Unsupported font size type: {type(size)}")
# 
# 
# if __name__ == "__main__":
#     plt, CC = configure_mpl(plt)
#     fig, axes = plt.subplots(nrows=2, sharex=True, sharey=True)
#     x = np.linspace(0, 10, 100)
#     for idx_cc, cc_str in enumerate(CC):
#         phase_shift = idx_cc * np.pi / len(CC)
#         y = np.sin(x + phase_shift)
#         axes[0].plot(x, y, label="Default color cycle")
#         axes[1].plot(x, y, color=CC[cc_str], label=f"{cc_str}")
#     axes[0].legend()
#     axes[1].legend()
#     plt.show()
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/plt/utils/_configure_mpl.py
# --------------------------------------------------------------------------------
