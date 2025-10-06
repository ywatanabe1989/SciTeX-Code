#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 21:15:33 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/reporters/reporter_utils/storage.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Storage utilities for classification reporters.

Enhanced version of storage utilities with:
- Consistent use of stx.io.save for all file operations
- Lazy directory creation
- Numerical precision control
- Better error handling
- Optimized file organization
"""

from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
from scitex.io import save as stx_io_save


class MetricStorage:
    """
    Enhanced storage handler with lazy creation and precision control.

    Features:
    - Creates directories only when actually needed
    - Rounds numerical values to specified precision
    - Graceful error handling with informative messages
    - Supports all standard data formats
    """

    def __init__(
        self,
        base_dir: Union[str, Path],
        precision: int = 3,
        verbose: bool = True,
    ):
        """
        Initialize storage with base directory and precision.

        Parameters
        ----------
        base_dir : Union[str, Path]
            Base directory for saving files
        precision : int, default 3
            Number of decimal places for numerical outputs
        """
        self.base_dir = Path(base_dir)
        self.precision = precision
        self.verbose = verbose

    def _round_numeric(self, data: Any) -> Any:
        """Round numeric values to specified precision."""
        if isinstance(data, (int, float, np.integer, np.floating)):
            return round(float(data), self.precision)
        elif isinstance(data, dict):
            return {k: self._round_numeric(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return type(data)(self._round_numeric(v) for v in data)
        elif isinstance(data, np.ndarray):
            if data.dtype.kind in "fc":  # float or complex
                return np.round(data, self.precision)
            return data
        else:
            return data

    def save(
        self, data: Any, relative_path: Union[str, Path], verbose=True, **kwargs
    ) -> Path:
        """
        Save data with lazy directory creation and precision control.

        Uses stx.io.save for all file operations to ensure consistency.

        Parameters
        ----------
        data : Any
            Data to save
        relative_path : Union[str, Path]
            Path relative to base_dir
        verbose : bool, optional
            Print save confirmation
        **kwargs : dict
            Additional keyword arguments passed to stx.io.save (e.g., index=True for CSV)

        Returns
        -------
        Path
            Absolute path to saved file
        """
        # Round numerical values for precision control
        data = self._round_numeric(data)

        # Construct full path and resolve to absolute
        full_path = (self.base_dir / relative_path).resolve()

        # Create directory only when actually needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Use stx.io.save for all file types (handles json, csv, figures, text, etc.)
            # IMPORTANT: use_caller_path=False to avoid nested directory issues
            # IMPORTANT: full_path must be absolute to prevent _out directory creation
            stx_io_save(data, str(full_path), use_caller_path=False, **kwargs)

            if verbose or self.verbose:
                import scitex.logging as logging
                logger = logging.getLogger(__name__)
                logger.info(f"Saved to: {full_path}")

            return full_path.absolute()

        except Exception as e:
            import scitex.logging as logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to save {relative_path}: {e}")
            return full_path.absolute()



def save_metric(
    metric_value: Any,
    path: Union[str, Path],
    fold: int = None,
    precision: int = 4,
) -> Path:
    """
    Improved function to save individual metrics with precision control.

    Parameters
    ----------
    metric_value : Any
        Metric value to save
    path : Union[str, Path]
        Output path
    fold : int, optional
        Fold index to include in metadata
    precision : int, default 4
        Number of decimal places

    Returns
    -------
    Path
        Path to saved file
    """
    # Resolve to absolute path to prevent _out directory creation
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Round numerical values recursively
    def round_value(val, prec):
        if isinstance(val, (int, float, np.integer, np.floating)):
            return round(float(val), prec)
        elif isinstance(val, dict):
            return {k: round_value(v, prec) for k, v in val.items()}
        elif isinstance(val, (list, tuple)):
            return type(val)(round_value(v, prec) for v in val)
        else:
            return val

    metric_value = round_value(metric_value, precision)

    # Prepare data structure
    if isinstance(metric_value, dict):
        data = metric_value
    else:
        metric_name = path.stem  # Use filename as metric name
        data = {"metric": metric_name, "value": metric_value}

    # Add fold information if provided
    if fold is not None:
        data["fold"] = fold

    # IMPORTANT: use_caller_path=False and absolute path to avoid nested directory issues
    stx_io_save(data, str(path), use_caller_path=False)

    return path


def create_directory_structure_lazy(
    base_dir: Union[str, Path],
) -> Dict[str, Path]:
    """
    Create directory structure mapping without actually creating directories.

    This returns paths that can be created later when actually needed.

    Parameters
    ----------
    base_dir : Union[str, Path]
        Base directory

    Returns
    -------
    Dict[str, Path]
        Mapping of directory types to paths
    """
    base_path = Path(base_dir)

    structure = {
        "base": base_path,
        "metrics": base_path / "metrics",
        "plots": base_path / "plots",
        "tables": base_path / "tables",
        "reports": base_path / "reports",
        "models": base_path / "models",
        "paper_export": base_path / "paper_export",
    }

    return structure

# EOF
