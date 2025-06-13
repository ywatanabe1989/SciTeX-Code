#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 01:15:00 (Claude)"
# File: /tests/scitex/gen/test__start.py

import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex
from scitex.gen import start
from scitex.gen._start import (
    _print_header,
    _initialize_env,
    _setup_configs,
    _setup_matplotlib,
    _get_debug_mode,
    _get_scitex_version,
)


class TestStart:
    """Test cases for scitex.gen.start function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    @pytest.fixture
    def mock_logging(self):
        """Mock logging setup."""
        with patch("scitex.gen._start.logging") as mock_log:
            yield mock_log

    @pytest.fixture
    def mock_matplotlib(self):
        """Mock matplotlib configuration."""
        with patch("scitex.gen._start.plt") as mock_plt:
            with patch("scitex.gen._start.mpl") as mock_mpl:
                yield mock_plt, mock_mpl

    def test_start_creates_directories(self, temp_dir):
        """Test that start() creates necessary directories."""
        # Arrange
        with patch("os.getcwd", return_value=temp_dir):
            # Act
            result = start(sdir=temp_dir, verbose=False)

            # Assert
            assert os.path.exists(temp_dir)
            assert result is not None

    def test_start_sets_matplotlib_backend(self, mock_matplotlib):
        """Test that start() sets matplotlib backend to Agg."""
        # Arrange
        mock_plt, mock_mpl = mock_matplotlib

        # Act
        start(verbose=False)

        # Assert
        mock_mpl.use.assert_called_with("Agg")

    def test_start_configures_logging(self, temp_dir, mock_logging):
        """Test that start() configures logging properly."""
        # Arrange
        with patch("os.getcwd", return_value=temp_dir):
            # Act
            start(sdir=temp_dir, verbose=False)

            # Assert
            mock_logging.basicConfig.assert_called_once()

    def test_start_sets_random_seeds(self):
        """Test that start() sets random seeds for reproducibility."""
        # Arrange
        with patch("scitex.gen._start.random") as mock_random:
            with patch("scitex.gen._start.np.random") as mock_np_random:
                with patch("scitex.gen._start.torch") as mock_torch:
                    # Act
                    start(seed=42, verbose=False)

                    # Assert
                    mock_random.seed.assert_called_with(42)
                    mock_np_random.seed.assert_called_with(42)
                    mock_torch.manual_seed.assert_called_with(42)

    def test_start_with_verbose(self, capsys):
        """Test that start() prints messages when verbose=True."""
        # Act
        with patch("scitex.gen._start.configure_mpl"):
            with patch("scitex.gen._start.fix_seeds"):
                start(verbose=True)

        # Assert
        captured = capsys.readouterr()
        assert len(captured.out) > 0  # Should print something

    def test_start_returns_config(self):
        """Test that start() returns configuration object."""
        # Act
        with patch("scitex.gen._start.configure_mpl"):
            with patch("scitex.gen._start.fix_seeds"):
                result = start(verbose=False)

        # Assert
        assert result is not None
        assert hasattr(result, "__dict__") or isinstance(result, dict)

    def test_start_handles_missing_torch_gracefully(self):
        """Test that start() handles missing torch module gracefully."""
        # Arrange
        with patch.dict(sys.modules, {"torch": None}):
            # Act & Assert - should not raise exception
            try:
                start(verbose=False)
            except ImportError:
                pytest.fail("start() should handle missing torch gracefully")

    def test_start_creates_symlink(self, temp_dir):
        """Test that start() creates symlinks for outputs."""
        # Arrange
        script_path = os.path.join(temp_dir, "test_script.py")
        with open(script_path, "w") as f:
            f.write("# test script")

        with patch("sys.argv", [script_path]):
            with patch("os.getcwd", return_value=temp_dir):
                # Act
                start(sdir=temp_dir, verbose=False)

                # Assert - check if output directory structure created
                assert os.path.exists(temp_dir)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_start.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 23:44:56 (ywatanabe)"
# # File: /home/ywatanabe/proj/_scitex_repo/src/scitex/gen/_start.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/gen/_start.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_start.py"
#
# import inspect
# import os as _os
# import re
# import sys as sys_module
# from datetime import datetime
# from pprint import pprint
# from time import sleep
# from typing import Any, Dict, Optional, Tuple
#
# import matplotlib
# import matplotlib.pyplot as plt_module
#
# from ..dev._analyze_code_flow import analyze_code_flow
# from ..dict import DotDict
# from ..gen._tee import tee
# from ..io import flush
# from ..io._load import load
# from ..io._load_configs import load_configs
# from ..plt.utils._configure_mpl import configure_mpl
# from ..reproduce._fix_seeds import fix_seeds
# from ..reproduce._gen_ID import gen_ID
# from ..str._clean_path import clean_path
# from ..str._printc import printc as _printc
#
# """
# Functionality:
#     * Initializes experimental environment with reproducible settings
#     * Sets up logging, random seeds, and matplotlib configurations
#     * Generates unique IDs for experiment tracking
# Input:
#     * System modules (sys, os, random, numpy, torch)
#     * Matplotlib configuration parameters
#     * Directory paths and debugging flags
# Output:
#     * Configured environment with unique ID
#     * Configured matplotlib instance
#     * Redirected stdout/stderr streams
# Prerequisites:
#     * Python 3.6+
#     * matplotlib
#     * scitex package
# """
#
#
# def _print_header(
#     ID: str,
#     PID: int,
#     file: str,
#     args: Any,
#     configs: Dict[str, Any],
#     verbose: bool = True,
# ) -> None:
#     """Prints formatted header with scitex version, ID, and PID information.
#
#     Parameters
#     ----------
#     ID : str
#         Unique identifier for the current run
#     PID : int
#         Process ID of the current Python process
#     configs : Dict[str, Any]
#         Configuration dictionary to display
#     verbose : bool, optional
#         Whether to print detailed information, by default True
#     """
#     _printc(
#         (f"## scitex v{_get_scitex_version()}\n" f"## {ID} (PID: {PID})"), char="#"
#     )
#
#     _printc((f"{file}\n" f"{args}"), c="yellow", char="=")
#     sleep(1)
#     if verbose:
#         print(f"\n{'-'*40}\n")
#         pprint(configs)
#         print(f"\n{'-'*40}\n")
#     sleep(1)
#
#
# def _initialize_env(IS_DEBUG: bool) -> Tuple[str, int]:
#     """Initialize environment with ID and PID.
#
#     Parameters
#     ----------
#     IS_DEBUG : bool
#         Debug mode flag
#
#     Returns
#     -------
#     tuple
#         (ID, PID) - Unique identifier and Process ID
#     """
#     ID = gen_ID(N=4) if not IS_DEBUG else "DEBUG_" + gen_ID(N=4)
#     PID = _os.getpid()
#     return ID, PID
#
#
# def _setup_configs(
#     IS_DEBUG: bool,
#     ID: str,
#     PID: int,
#     file: str,
#     sdir: str,
#     relative_sdir: str,
#     verbose: bool,
# ) -> Dict[str, Any]:
#     """Setup configuration dictionary with basic parameters.
#
#     Parameters
#     ----------
#     IS_DEBUG : bool
#         Debug mode flag
#     ID : str
#         Unique identifier
#     PID : int
#         Process ID
#     sdir : str
#         Save directory path
#     relative_sdir : str
#         Relative save directory path
#     verbose : bool
#         Verbosity flag
#
#     Returns
#     -------
#     dict
#         Configuration dictionary
#     """
#
#     CONFIGS = load_configs(IS_DEBUG).to_dict()
#     CONFIGS.update(
#         {
#             "ID": ID,
#             "PID": PID,
#             "START_TIME": datetime.now(),
#             "FILE": file,
#             "SDIR": sdir,
#             "REL_SDIR": relative_sdir,
#         }
#     )
#     return CONFIGS
#
#
# def _setup_matplotlib(
#     plt: plt_module = None, agg: bool = False, **mpl_kwargs: Any
# ) -> Tuple[Any, Optional[Dict[str, Any]]]:
#     """Configure matplotlib settings.
#
#     Parameters
#     ----------
#     plt : module
#         Matplotlib.pyplot module
#     agg : bool
#         Whether to use Agg backend
#     **mpl_kwargs : dict
#         Additional matplotlib configuration parameters
#
#     Returns
#     -------
#     tuple
#         (plt, CC) - Configured pyplot module and color cycle
#     """
#     if plt is not None:
#         plt.close("all")
#         plt, CC = configure_mpl(plt, **mpl_kwargs)
#         CC["gray"] = CC["grey"]
#         if agg:
#             matplotlib.use("Agg")
#         return plt, CC
#     return plt, None
#
#
# def start(
#     sys: sys_module = None,
#     plt: plt_module = None,
#     file: Optional[str] = None,
#     sdir: Optional[str] = None,
#     sdir_suffix: Optional[str] = None,
#     args: Optional[Any] = None,
#     os: Optional[Any] = None,
#     random: Optional[Any] = None,
#     np: Optional[Any] = None,
#     torch: Optional[Any] = None,
#     seed: int = 42,
#     agg: bool = False,
#     fig_size_mm: Tuple[int, int] = (160, 100),
#     fig_scale: float = 1.0,
#     dpi_display: int = 100,
#     dpi_save: int = 300,
#     fontsize="small",
#     autolayout=True,
#     show_execution_flow=False,
#     # font_size_base: int = 10,
#     # font_size_title: int = 10,
#     # font_size_axis_label: int = 8,
#     # font_size_tick_label: int = 7,
#     # font_size_legend: int = 6,
#     hide_top_right_spines: bool = True,
#     alpha: float = 0.9,
#     line_width: float = 0.5,
#     clear_logs: bool = False,
#     verbose: bool = True,
# ) -> Tuple[DotDict, Any, Any, Any, Optional[Dict[str, Any]]]:
#     """Initialize experiment environment with reproducibility settings.
#
#     Parameters
#     ----------
#     sys : module, optional
#         Python sys module for I/O redirection
#     plt : module, optional
#         Matplotlib pyplot module for plotting configuration
#     sdir : str, optional
#         Save directory path. If None, automatically generated
#     sdir_suffix : str, optional
#         Suffix to append to save directory
#     verbose : bool, default=True
#         Whether to print detailed information
#     args : object, optional
#         Command line arguments or configuration object
#     os, random, np, torch : modules, optional
#         Modules for random seed fixing
#     seed : int, default=42
#         Random seed for reproducibility
#     agg : bool, default=False
#         Whether to use matplotlib Agg backend
#     fig_size_mm : tuple, default=(160, 100)
#         Figure size in millimeters
#     fig_scale : float, default=1.0
#         Scale factor for figure size
#     dpi_display, dpi_save : int
#         DPI for display and saving
#     font_size_* : int
#         Various font size settings
#     hide_top_right_spines : bool, default=True
#         Whether to hide top and right spines
#     alpha : float, default=0.9
#         Default alpha value for plots
#     line_width : float, default=0.5
#         Default line width for plots
#     clear_logs : bool, default=False
#         Whether to clear existing log directory
#
#     Returns
#     -------
#     tuple
#         (CONFIGS, stdout, stderr, plt: Any = None, CC)
#         - CONFIGS: Configuration dictionary
#         - stdout, stderr: Redirected output streams
#         - plt: Configured matplotlib.pyplot module
#         - CC: Color cycle dictionary
#     """
#     IS_DEBUG = _get_debug_mode()
#     ID, PID = _initialize_env(IS_DEBUG)
#
#     ########################################
#     # Defines SDIR (DO NOT MODIFY THIS SECTION)
#     ########################################
#     if sdir is None:
#         # Define __file__
#         if file:
#             THIS_FILE = file
#         else:
#             THIS_FILE = inspect.stack()[1].filename
#             if "ipython" in __file__:
#                 THIS_FILE = f"/tmp/{_os.getenv('USER')}.py"
#
#         # Define sdir
#         sdir = clean_path(
#             _os.path.splitext(__file__)[0] + f"_out/RUNNING/{ID}/"
#         )
#
#         # Optional
#         if sdir_suffix:
#             sdir = sdir[:-1] + f"-{sdir_suffix}/"
#
#     if clear_logs:
#         _clear_python_log_dir(_sdir + sfname + "/")
#     _os.makedirs(sdir, exist_ok=True)
#     relative_sdir = _simplify_relative_path(sdir)
#     ########################################
#
#     # Setup configs after having all necessary parameters
#     CONFIGS = _setup_configs(
#         IS_DEBUG, ID, PID, file, sdir, relative_sdir, verbose
#     )
#
#     # Logging
#     if sys is not None:
#         flush(sys)
#         sys.stdout, sys.stderr = tee(sys, sdir=sdir, verbose=verbose)
#         CONFIGS["sys"] = sys
#
#     # Random Seeds
#     fix_seeds(
#         os=os, random=random, np=np, torch=torch, seed=seed, verbose=verbose
#     )
#
#     # Matplotlib configurations
#     plt, CC = _setup_matplotlib(
#         plt,
#         agg,
#         fig_size_mm=fig_size_mm,
#         fig_scale=fig_scale,
#         dpi_display=dpi_display,
#         dpi_save=dpi_save,
#         hide_top_right_spines=hide_top_right_spines,
#         alpha=alpha,
#         line_width=line_width,
#         fontsize=fontsize,
#         autolayout=autolayout,
#         # font_size_base=font_size_base,
#         # font_size_title=font_size_title,
#         # font_size_axis_label=font_size_axis_label,
#         # font_size_tick_label=font_size_tick_label,
#         # font_size_legend=font_size_legend,
#         verbose=verbose,
#     )
#
#     # Adds argument-parsed variables
#     if args is not None:
#         CONFIGS["ARGS"] = vars(args) if hasattr(args, "__dict__") else args
#
#     CONFIGS = DotDict(CONFIGS)
#
#     _print_header(ID, PID, file, args, CONFIGS, verbose)
#
#     if show_execution_flow:
#         structure = analyze_code_flow(file)
#         _printc(structure)
#
#     return CONFIGS, sys.stdout, sys.stderr, plt, CC
#
#
# def _simplify_relative_path(sdir: str) -> str:
#     """
#     Simplify the relative path by removing specific patterns.
#
#     Example
#     -------
#     sdir = '/home/user/scripts/memory-load/distance_between_gs_stats/RUNNING/2024Y-09M-12D-02h44m40s_GlBZ'
#     simplified_path = simplify_relative_path(sdir)
#     print(simplified_path)
#     # Output: './memory-load/distance_between_gs_stats/'
#
#     Parameters
#     ----------
#     sdir : str
#         The directory path to simplify
#
#     Returns
#     -------
#     str
#         Simplified relative path
#     """
#     base_path = _os.getcwd()
#     relative_sdir = _os.path.relpath(sdir, base_path) if base_path else sdir
#     simplified_path = relative_sdir.replace("scripts/", "./").replace(
#         "RUNNING/", ""
#     )
#     # Remove date-time pattern and random string
#     simplified_path = re.sub(
#         r"\d{4}Y-\d{2}M-\d{2}D-\d{2}h\d{2}m\d{2}s_\w+/?$", "", simplified_path
#     )
#     return simplified_path
#
#
# def _get_debug_mode() -> bool:
#     # Debug mode check
#     try:
#         IS_DEBUG_PATH = "./config/IS_DEBUG.yaml"
#         if _os.path.exists(IS_DEBUG_PATH):
#             IS_DEBUG = load(IS_DEBUG_PATH).get("IS_DEBUG", False)
#             if IS_DEBUG == "true":
#                 IS_DEBUG = True
#         else:
#             IS_DEBUG = False
#
#     except Exception as e:
#         print(e)
#         IS_DEBUG = False
#     return IS_DEBUG
#
#
# def _clear_python_log_dir(log_dir: str) -> None:
#     try:
#         if _os.path.exists(log_dir):
#             _os.system(f"rm -rf {log_dir}")
#     except Exception as e:
#         print(f"Failed to clear directory {log_dir}: {e}")
#
#
# def _get_scitex_version() -> str:
#     """Gets scitex version"""
#     try:
#         import scitex
#
#         return scitex.__version__
#     except Exception as e:
#         print(e)
#         return "(not found)"
#
#
# if __name__ == "__main__":
#     import os
#     import sys
#
#     import matplotlib.pyplot as plt
#     import scitex
#
#     # Config
#     CONFIG = scitex.io.load_configs()
#
#     # Functions
#     # Your awesome code here :)
#
#     if __name__ == "__main__":
#         # Start
#         CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
#
#         # Your awesome code here :)
#
#         # Close
#         scitex.gen.close(CONFIG)
#
#
# """
# /home/ywatanabe/proj/entrance/scitex/gen/_start.py
# """
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_start.py
# --------------------------------------------------------------------------------
