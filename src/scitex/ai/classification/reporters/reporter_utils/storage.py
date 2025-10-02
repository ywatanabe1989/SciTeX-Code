#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-02 06:48:06 (ywatanabe)"
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
- Lazy directory creation
- Numerical precision control
- Better error handling
- Optimized file organization
"""

from pathlib import Path
from typing import Any, Dict, Union

import numpy as np


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
        self, data: Any, relative_path: Union[str, Path], verbose=True
    ) -> Path:
        """
        Save data with lazy directory creation and precision control.

        Parameters
        ----------
        data : Any
            Data to save
        relative_path : Union[str, Path]
            Path relative to base_dir

        Returns
        -------
        Path
            Absolute path to saved file
        """
        # Round numerical values
        data = self._round_numeric(data)

        # Construct full path
        full_path = self.base_dir / relative_path

        # Create directory only when actually needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format from extension
        extension = full_path.suffix.lower()

        try:
            # Save based on extension
            if extension == ".json":
                self._save_json(data, full_path)
            elif extension == ".csv":
                self._save_csv(data, full_path)
            elif extension in [".png", ".jpg", ".jpeg", ".pdf", ".svg"]:
                self._save_figure(data, full_path)
            elif extension in [".txt", ".md"]:
                self._save_text(data, full_path)
            else:
                raise ValueError(f"Unsupported file extension: {extension}")

            return full_path.absolute()

        except Exception as e:
            print(f"Warning: Failed to save {relative_path}: {e}")
            return full_path.absolute()

    def _save_json(
        self, data: Any, full_path: Path, verbose: bool = True
        ) -> None:
        """Save data as JSON with proper formatting."""
        import json

        # Ensure JSON serializable
        if hasattr(data, "tolist"):  # numpy arrays
            data = data.tolist()

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if verbose or self.verbose:
            import scitex.logging as logging
            logger = logging.getLogger(__name__)
            logger.info(f"Saved to: {full_path}")

    def _save_csv(self, data: Any, full_path: Path) -> None:
        """Save data as CSV."""
        import pandas as pd

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, pd.DataFrame):
            data.to_csv(full_path, index=True)
        else:
            # Assume it's array-like
            pd.DataFrame(data).to_csv(full_path, index=False)

        if self.verbose:
            import scitex.logging as logging
            logger = logging.getLogger(__name__)
            logger.info(f"Saved to: {full_path}")

        # if isinstance(data, pd.DataFrame):
        #     # data.to_csv(path, index=True)
        #     stx_io_save(data, path)
        # elif isinstance(data, dict):
        #     # Convert dict to DataFrame
        #     df = pd.DataFrame([data])
        #     # df.to_csv(path, index=False)
        #     stx_io_save(df, path)
        # elif isinstance(data, np.ndarray):
        #     # Save numpy array as CSV
        #     if data.ndim == 2:
        #         # pd.DataFrame(data).to_csv(path, index=False)
        #         stx_io_save(pd.DataFrame(data), path)
        #     else:
        #         # pd.Series(data).to_csv(path, index=False)
        #         stx_io_save(pd.Series(data), path)
        # else:
        #     # Try to convert to string representation
        #     with open(path, "w") as f:
        #         f.write(str(data))

    def _save_figure(self, figure, full_path: Path) -> None:
        """Save matplotlib figure."""
        from scitex.io import save as stx_io_save

        # fullpath = Path(str(self.base_dir)) / path
        stx_io_save(figure, full_path)
        # if hasattr(figure, "savefig"):
        #     figure.savefig(path, dpi=300, bbox_inches="tight")
        # else:
        #     raise ValueError("Object is not a matplotlib figure")

    def _save_text(self, data: Any, full_path: Path) -> None:
        """Save data as text file."""
        from scitex.io import save as stx_io_save

        # fullpath = Path(str(self.base_dir)) / path
        stx_io_save(data, full_path)
        # with open(path, "w") as f:
        #     f.write(str(data))


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
    path = Path(path)
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

    from scitex.io import save as stx_io_save

    stx_io_save(data, path)
    # Save as JSON
    # with open(path, "w") as f:
    #     json.dump(data, f, indent=2, ensure_ascii=False)

    return path.absolute()


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
