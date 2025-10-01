#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-24 14:07:02 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_save.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/io/_save.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings

"""
1. Functionality:
   - Provides utilities for saving various data types to different file formats.
2. Input:
   - Objects to be saved (e.g., NumPy arrays, PyTorch tensors, Pandas DataFrames, etc.)
   - File path or name where the object should be saved
3. Output:
   - Saved files in various formats (e.g., CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML, JSON, HDF5, PTH, MAT, CBM)
4. Prerequisites:
   - Python 3.x
   - Required libraries: numpy, pandas, torch, matplotlib, plotly, h5py, joblib, PIL, ruamel.yaml
"""

"""Imports"""
import inspect
import os as _os
from pathlib import Path
from typing import Any, Union

from scitex import logging

from .._sh import sh
from ..path._clean import clean
from ..path._getsize import getsize
from ..str._clean_path import clean_path
from ..str._color_text import color_text
from ..str._readable_bytes import readable_bytes
# Import save functions from the new modular structure
from ._save_modules import (save_catboost, save_csv, save_excel, save_hdf5,
                            save_html, save_image, save_joblib, save_json,
                            save_matlab, save_mp4, save_npy, save_npz,
                            save_pickle, save_pickle_compressed, save_text,
                            save_torch, save_yaml, save_zarr)
from ._save_modules._bibtex import save_bibtex

logger = logging.getLogger()


def _get_figure_with_data(obj):
    """
    Extract figure or axes object that may contain plotting data for CSV export.

    Parameters
    ----------
    obj : various matplotlib objects
        Could be Figure, Axes, FigWrapper, AxisWrapper, or other matplotlib objects

    Returns
    -------
    object or None
        Figure or axes object that has export_as_csv methods, or None if not found
    """
    import matplotlib.axes
    import matplotlib.figure
    import matplotlib.pyplot as plt

    # Check if object already has export methods (SciTeX wrapped objects)
    if hasattr(obj, "export_as_csv"):
        return obj

    # Handle matplotlib Figure objects
    if isinstance(obj, matplotlib.figure.Figure):
        # Get the current axes that might be wrapped with SciTeX functionality
        current_ax = plt.gca()
        if hasattr(current_ax, "export_as_csv"):
            return current_ax

        # Check all axes in the figure
        for ax in obj.axes:
            if hasattr(ax, "export_as_csv"):
                return ax

        return None

    # Handle matplotlib Axes objects
    if isinstance(obj, matplotlib.axes.Axes):
        if hasattr(obj, "export_as_csv"):
            return obj
        return None

    # Handle FigWrapper or similar SciTeX objects
    if hasattr(obj, "figure") and hasattr(obj.figure, "axes"):
        # Check if the wrapper itself has export methods
        if hasattr(obj, "export_as_csv"):
            return obj

        # Check the underlying figure's axes
        for ax in obj.figure.axes:
            if hasattr(ax, "export_as_csv"):
                return ax

        return None

    # Handle AxisWrapper or similar SciTeX objects
    if hasattr(obj, "_axis_mpl") or hasattr(obj, "_ax"):
        if hasattr(obj, "export_as_csv"):
            return obj
        return None

    # Try to get the current figure and its axes as fallback
    try:
        current_fig = plt.gcf()
        current_ax = plt.gca()

        if hasattr(current_ax, "export_as_csv"):
            return current_ax
        elif hasattr(current_fig, "export_as_csv"):
            return current_fig

        # Check all axes in current figure
        for ax in current_fig.axes:
            if hasattr(ax, "export_as_csv"):
                return ax

    except:
        pass

    return None


def save(
    obj: Any,
    specified_path: Union[str, Path],
    makedirs: bool = True,
    verbose: bool = True,
    symlink_from_cwd: bool = False,
    symlink_to: Union[str, Path] = None,
    dry_run: bool = False,
    no_csv: bool = False,
    **kwargs,
) -> None:
    """
    Save an object to a file with the specified format.

    Parameters
    ----------
    obj : Any
        The object to be saved. Can be a NumPy array, PyTorch tensor, Pandas DataFrame, or any serializable object.
    specified_path : Union[str, Path]
        The file name or path where the object should be saved. Can be a string or pathlib.Path object. The file extension determines the format.
    makedirs : bool, optional
        If True, create the directory path if it does not exist. Default is True.
    verbose : bool, optional
        If True, print a message upon successful saving. Default is True.
    symlink_from_cwd : bool, optional
        If True, create a _symlink from the current working directory. Default is False.
    symlink_to : Union[str, Path], optional
        If specified, create a symlink at this path pointing to the saved file. Default is None.
    dry_run : bool, optional
        If True, simulate the saving process without actually writing files. Default is False.
    **kwargs
        Additional keyword arguments to pass to the underlying save function of the specific format.

    Returns
    -------
    None

    Notes
    -----
    Supported formats include CSV, NPY, PKL, JOBLIB, PNG, HTML, TIFF, MP4, YAML, JSON, HDF5, PTH, MAT, and CBM.
    The function dynamically selects the appropriate saving mechanism based on the file extension.

    Examples
    --------
    >>> import scitex
    >>> import numpy as np
    >>> import pandas as pd
    >>> import torch
    >>> import matplotlib.pyplot as plt

    >>> # Save NumPy array
    >>> arr = np.array([1, 2, 3])
    >>> scitex.io.save(arr, "data.npy")

    >>> # Save Pandas DataFrame
    >>> df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    >>> scitex.io.save(df, "data.csv")

    >>> # Save PyTorch tensor
    >>> tensor = torch.tensor([1, 2, 3])
    >>> scitex.io.save(tensor, "model.pth")

    >>> # Save dictionary
    >>> data_dict = {"a": 1, "b": 2, "c": [3, 4, 5]}
    >>> scitex.io.save(data_dict, "data.pkl")

    >>> # Save matplotlib figure
    >>> plt.figure()
    >>> plt.plot(np.array([1, 2, 3]))
    >>> scitex.io.save(plt, "plot.png")

    >>> # Save as YAML
    >>> scitex.io.save(data_dict, "config.yaml")

    >>> # Save as JSON
    >>> scitex.io.save(data_dict, "data.json")
    """
    try:
        # Convert Path objects to strings for consistency
        if isinstance(specified_path, Path):
            specified_path = str(specified_path)

        ########################################
        # DO NOT MODIFY THIS SECTION
        ########################################
        #
        # Determine saving directory from the script.
        #
        # When called in /path/to/script.py,
        # data will be saved under `/path/to/script.py_out/`
        #
        # When called in a Jupyter notebook /path/to/notebook.ipynb,
        # data will be saved under `/path/to/notebook_out/`
        #
        # When called in ipython environment,
        # data will be saved under `/tmp/{_os.getenv("USER")/`
        #
        ########################################
        spath, sfname = None, None

        # f-expression handling - safely parse f-strings
        if specified_path.startswith('f"') or specified_path.startswith("f'"):
            # Remove the f prefix and quotes
            path_content = specified_path[2:-1]

            # Get the caller's frame to access their local variables
            frame = inspect.currentframe().f_back
            try:
                # Use string formatting with the caller's locals and globals
                # This is much safer than eval() as it only does string substitution
                import re

                # Find all {variable} patterns
                variables = re.findall(r"\{([^}]+)\}", path_content)
                format_dict = {}
                for var in variables:
                    # Only allow simple variable names, not arbitrary expressions
                    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
                        if var in frame.f_locals:
                            format_dict[var] = frame.f_locals[var]
                        elif var in frame.f_globals:
                            format_dict[var] = frame.f_globals[var]
                    else:
                        raise ValueError(
                            f"Invalid variable name in f-string: {var}"
                        )

                # Use str.format() which is safe
                specified_path = path_content.format(**format_dict)
            finally:
                del frame  # Avoid reference cycles

        # When full path
        if specified_path.startswith("/"):
            spath = specified_path

        # When relative path
        else:
            # Import here to avoid circular imports
            from ..gen._detect_environment import detect_environment
            from ..gen._get_notebook_path import get_notebook_info_simple

            # Detect the current environment
            env_type = detect_environment()

            if env_type == "jupyter":
                # Special handling for Jupyter notebooks
                notebook_name, notebook_dir = get_notebook_info_simple()

                if notebook_name:
                    # Remove .ipynb extension and add _out
                    notebook_base = _os.path.splitext(notebook_name)[0]
                    sdir = _os.path.join(
                        notebook_dir or _os.getcwd(), f"{notebook_base}_out"
                    )
                else:
                    # Fallback if we can't detect notebook name
                    sdir = _os.path.join(_os.getcwd(), "notebook_out")

                spath = _os.path.join(sdir, specified_path)

            elif env_type == "script":
                # Regular script handling
                script_path = inspect.stack()[1].filename
                sdir = clean_path(_os.path.splitext(script_path)[0] + "_out")
                spath = _os.path.join(sdir, specified_path)

            else:
                # IPython console or interactive mode
                script_path = inspect.stack()[1].filename

                if (
                    ("ipython" in script_path)
                    or ("<stdin>" in script_path)
                    or env_type in ["ipython", "interactive"]
                ):
                    script_path = f'/tmp/{_os.getenv("USER")}'
                    sdir = script_path
                else:
                    # Unknown environment, use current directory
                    sdir = _os.path.join(_os.getcwd(), "output")

                spath = _os.path.join(sdir, specified_path)

        # Sanitization
        spath_final = clean(spath)
        ########################################

        # Potential path to _symlink
        spath_cwd = _os.getcwd() + "/" + specified_path
        spath_cwd = clean(spath_cwd)

        # Removes spath and spath_cwd to prevent potential circular links
        # Skip deletion for CSV files to allow caching to work
        # Also skip deletion for HDF5 files when a key is specified
        should_skip_deletion = spath_final.endswith(".csv") or (
            (spath_final.endswith(".hdf5") or spath_final.endswith(".h5"))
            and "key" in kwargs
        )

        if not should_skip_deletion:
            for path in [spath_final, spath_cwd]:
                sh(f"rm -f {path}", verbose=False)

        if dry_run:
            # Get relative path from current working directory
            try:
                rel_path = _os.path.relpath(spath, _os.getcwd())
            except ValueError:
                rel_path = spath

            if verbose:
                print()
                logger.success(
                    color_text(f"(dry run) Saved to: ./{rel_path}", c="yellow")
                )
            return

        # Ensure directory exists
        if makedirs:
            _os.makedirs(_os.path.dirname(spath_final), exist_ok=True)

        # Main
        _save(
            obj,
            spath_final,
            verbose=verbose,
            symlink_from_cwd=symlink_from_cwd,
            dry_run=dry_run,
            no_csv=no_csv,
            **kwargs,
        )

        # Symbolic links
        _symlink(spath, spath_cwd, symlink_from_cwd, verbose)
        _symlink_to(spath_final, symlink_to, verbose)

    except Exception as e:
        logger.error(
            f"Error occurred while saving: {str(e)}\n"
            f"Debug: Initial script_path = {inspect.stack()[1].filename}\n"
            f"Debug: Final spath = {spath}\n"
            f"Debug: specified_path type = {type(specified_path)}\n"
            f"Debug: specified_path = {specified_path}"
        )


def _symlink(spath, spath_cwd, symlink_from_cwd, verbose):
    """Create a symbolic link from the current working directory."""
    if symlink_from_cwd and (spath != spath_cwd):
        _os.makedirs(_os.path.dirname(spath_cwd), exist_ok=True)
        sh(f"rm -f {spath_cwd}", verbose=False)
        sh(f"ln -sfr {spath} {spath_cwd}", verbose=False)
        if verbose:
            # Get file extension to provide more informative message
            ext = _os.path.splitext(spath_cwd)[1].lower()
            logger.success(color_text(f"(Symlinked to: {spath_cwd})"))


def _symlink_to(spath_final, symlink_to, verbose):
    """Create a symbolic link at the specified path pointing to the saved file."""
    if symlink_to:
        # Convert Path objects to strings for consistency
        if isinstance(symlink_to, Path):
            symlink_to = str(symlink_to)

        # Clean the symlink path
        symlink_to = clean(symlink_to)

        # Ensure the symlink directory exists
        _os.makedirs(_os.path.dirname(symlink_to), exist_ok=True)

        # Remove existing symlink or file
        sh(f"rm -f {symlink_to}", verbose=False)

        # Create the symlink using relative path for robustness
        sh(f"ln -sfr {spath_final} {symlink_to}", verbose=False)

        if verbose:
            print(color_text(f"\n(Symlinked to: {symlink_to})", "yellow"))


def _save(
    obj,
    spath,
    verbose=True,
    symlink_from_cwd=False,
    dry_run=False,
    no_csv=False,
    **kwargs,
):
    # Don't use object's own save method - use consistent handlers
    # This ensures all saves go through the same pipeline and get
    # the yellow confirmation message

    # Get file extension
    ext = _os.path.splitext(spath)[1].lower()

    # Try dispatch dictionary first for O(1) lookup
    if ext in _FILE_HANDLERS:
        # Check if handler needs special parameters
        if ext in [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif", ".svc"]:
            _FILE_HANDLERS[ext](
                obj,
                spath,
                no_csv=no_csv,
                symlink_from_cwd=symlink_from_cwd,
                dry_run=dry_run,
                **kwargs,
            )
        elif ext in [".hdf5", ".h5", ".zarr"]:
            # HDF5 and Zarr files may need special 'key' parameter
            _FILE_HANDLERS[ext](obj, spath, **kwargs)
        else:
            _FILE_HANDLERS[ext](obj, spath, **kwargs)
    # csv - special case as it doesn't have a dot prefix in dispatch
    elif spath.endswith(".csv"):
        save_csv(obj, spath, **kwargs)
    # Check for special extension cases not in dispatch
    elif spath.endswith(".pkl.gz"):
        save_pickle_compressed(obj, spath, **kwargs)
    else:
        warnings.warn(f"Unsupported file format. {spath} was not saved.")

    if verbose:
        if _os.path.exists(spath):
            file_size = getsize(spath)
            file_size = readable_bytes(file_size)
            # Get relative path from current working directory
            try:
                rel_path = _os.path.relpath(spath, _os.getcwd())
            except ValueError:
                rel_path = spath

            print()
            logger.success(
                color_text(f"Saved to: ./{rel_path} ({file_size})", c="yellow")
            )


def _save_separate_legends(
    obj, spath, symlink_from_cwd=False, dry_run=False, **kwargs
):
    """Save separate legend files if ax.legend('separate') was used."""
    if dry_run:
        return

    import matplotlib.figure
    import matplotlib.pyplot as plt

    # Get the matplotlib figure object
    fig = None
    if isinstance(obj, matplotlib.figure.Figure):
        fig = obj
    elif hasattr(obj, "_fig_mpl"):
        fig = obj._fig_mpl
    elif hasattr(obj, "figure"):
        if isinstance(obj.figure, matplotlib.figure.Figure):
            fig = obj.figure
        elif hasattr(obj.figure, "_fig_mpl"):
            fig = obj.figure._fig_mpl

    if fig is None:
        return

    # Check if there are separate legend parameters stored
    if not hasattr(fig, "_separate_legend_params"):
        return

    # Save each legend as a separate file
    base_path = _os.path.splitext(spath)[0]
    ext = _os.path.splitext(spath)[1]

    for legend_params in fig._separate_legend_params:
        # Create a new figure for the legend
        legend_fig = plt.figure(figsize=legend_params["figsize"])
        legend_ax = legend_fig.add_subplot(111)

        # Create the legend
        legend = legend_ax.legend(
            legend_params["handles"],
            legend_params["labels"],
            loc="center",
            frameon=legend_params["frameon"],
            fancybox=legend_params["fancybox"],
            shadow=legend_params["shadow"],
            **legend_params["kwargs"],
        )

        # Remove axes
        legend_ax.axis("off")

        # Adjust layout to fit the legend
        legend_fig.tight_layout()

        # Save the legend figure
        legend_filename = f"{base_path}_{legend_params['axis_id']}_legend{ext}"
        save_image(legend_fig, legend_filename, **kwargs)

        # Close the legend figure to free memory
        plt.close(legend_fig)

        if not dry_run and _os.path.exists(legend_filename):
            file_size = getsize(legend_filename)
            file_size = readable_bytes(file_size)
            print(
                color_text(
                    f"\nSaved legend to: {legend_filename} ({file_size})",
                    c="yellow",
                )
            )


def _handle_image_with_csv(
    obj, spath, no_csv=False, symlink_from_cwd=False, dry_run=False, **kwargs
):
    """Handle image file saving with optional CSV export."""
    if dry_run:
        return

    save_image(obj, spath, **kwargs)

    # Handle separate legend saving
    _save_separate_legends(
        obj,
        spath,
        symlink_from_cwd=symlink_from_cwd,
        dry_run=dry_run,
        **kwargs,
    )

    if not no_csv:
        ext = _os.path.splitext(spath)[1].lower()
        ext_wo_dot = ext.replace(".", "")

        try:
            # Get the figure object that may contain plot data
            fig_obj = _get_figure_with_data(obj)

            if fig_obj is not None:
                # Save regular CSV if export method exists
                if hasattr(fig_obj, "export_as_csv"):
                    csv_data = fig_obj.export_as_csv()
                    if csv_data is not None and not csv_data.empty:
                        # Replace directory name AND extension to separate data from visualizations
                        # Example: ./path/to/jpg/fig.jpg -> ./path/to/csv/fig.csv
                        dir_path, filename = _os.path.split(spath)
                        dir_name = _os.path.basename(dir_path)
                        parent_dir = _os.path.dirname(dir_path)

                        # Replace image directory name with "csv"
                        csv_dir = _os.path.join(parent_dir, "csv")
                        # Replace extension
                        csv_filename = _os.path.splitext(filename)[0] + ".csv"
                        csv_path = _os.path.join(csv_dir, csv_filename)
                        # Save directly using _save to avoid path doubling
                        _save(
                            csv_data,
                            csv_path,
                            verbose=True,
                            symlink_from_cwd=False,  # Will handle symlink manually
                            dry_run=dry_run,
                            no_csv=True,
                            **kwargs,
                        )
                        # Create symlink for CSV manually if needed
                        if symlink_from_cwd:
                            # Get the relative path from the original specified path
                            # This preserves the directory structure for the symlink
                            import inspect

                            frame_info = inspect.stack()
                            # Find the original specified_path from the parent save() call
                            for frame in frame_info:
                                if "specified_path" in frame.frame.f_locals:
                                    original_path = frame.frame.f_locals[
                                        "specified_path"
                                    ]
                                    if isinstance(original_path, str):
                                        # Replace extension to get CSV path structure
                                        csv_relative = original_path.replace(
                                            _os.path.splitext(original_path)[
                                                1
                                            ],
                                            ".csv",
                                        )
                                        csv_cwd = _os.path.join(
                                            _os.getcwd(), csv_relative
                                        )
                                        _symlink(csv_path, csv_cwd, True, True)
                                        break
                            else:
                                # Fallback to basename if we can't find the original path
                                csv_cwd = (
                                    _os.getcwd()
                                    + "/"
                                    + _os.path.basename(csv_path)
                                )
                                _symlink(csv_path, csv_cwd, True, True)

                # Save SigmaPlot CSV if method exists
                if hasattr(fig_obj, "export_as_csv_for_sigmaplot"):
                    sigmaplot_data = fig_obj.export_as_csv_for_sigmaplot()
                    if sigmaplot_data is not None and not sigmaplot_data.empty:
                        # For CSV files, we want them in the same directory as the image
                        csv_sigmaplot_path = spath.replace(
                            ext_wo_dot, "csv"
                        ).replace(".csv", "_for_sigmaplot.csv")
                        # Save directly using _save to avoid path doubling
                        _save(
                            sigmaplot_data,
                            csv_sigmaplot_path,
                            verbose=True,
                            symlink_from_cwd=False,  # Will handle symlink manually
                            dry_run=dry_run,
                            no_csv=True,
                            **kwargs,
                        )
                        # Create symlink for SigmaPlot CSV manually if needed
                        if symlink_from_cwd:
                            csv_cwd = (
                                _os.getcwd()
                                + "/"
                                + _os.path.basename(csv_sigmaplot_path)
                            )
                            _symlink(csv_sigmaplot_path, csv_cwd, True, True)
        except Exception:
            pass


# Dispatch dictionary for O(1) file format lookup
_FILE_HANDLERS = {
    # Excel formats
    ".xlsx": save_excel,
    ".xls": save_excel,
    # NumPy formats
    ".npy": save_npy,
    ".npz": save_npz,
    # Pickle formats
    ".pkl": save_pickle,
    ".pickle": save_pickle,
    ".pkl.gz": save_pickle_compressed,
    # Other binary formats
    ".joblib": save_joblib,
    ".pth": save_torch,
    ".pt": save_torch,
    ".mat": save_matlab,
    ".cbm": save_catboost,
    # Text formats
    ".json": save_json,
    ".yaml": save_yaml,
    ".yml": save_yaml,
    ".txt": save_text,
    ".md": save_text,
    ".py": save_text,
    ".css": save_text,
    ".js": save_text,
    # Bibliography
    ".bib": save_bibtex,
    # Data formats
    ".html": save_html,
    ".hdf5": save_hdf5,
    ".h5": save_hdf5,
    ".zarr": save_zarr,
    # Media formats
    ".mp4": save_mp4,
    ".png": _handle_image_with_csv,
    ".jpg": _handle_image_with_csv,
    ".jpeg": _handle_image_with_csv,
    ".gif": _handle_image_with_csv,
    ".tiff": _handle_image_with_csv,
    ".tif": _handle_image_with_csv,
    ".svg": _handle_image_with_csv,
    ".pdf": _handle_image_with_csv,
}

# EOF
