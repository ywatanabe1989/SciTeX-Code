#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 01:45:48 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_BaseMixins/_BaseBlobMixin.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_BaseMixins/_BaseBlobMixin.py"

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


class _BaseBlobMixin(ABC):
    """Base class for BLOB data handling functionality"""

    @abstractmethod
    def save_array(
        self,
        table_name: str,
        data: np.ndarray,
        column: str = "data",
        ids: Optional[Union[int, List[int]]] = None,
        where: str = None,
        additional_columns: Dict[str, Any] = None,
        batch_size: int = 1000,
    ) -> None:
        """Save numpy array(s) to database"""
        pass

    @abstractmethod
    def load_array(
        self,
        table_name: str,
        column: str,
        ids: Union[int, List[int], str] = "all",
        where: str = None,
        order_by: str = None,
        batch_size: int = 128,
        dtype: np.dtype = None,
        shape: Optional[Tuple] = None,
    ) -> Optional[np.ndarray]:
        """Load numpy array(s) from database"""
        pass

    @abstractmethod
    def binary_to_array(
        self,
        binary_data,
        dtype_str=None,
        shape_str=None,
        dtype=None,
        shape=None,
    ) -> Optional[np.ndarray]:
        """Convert binary data to numpy array"""
        pass

    @abstractmethod
    def get_array_dict(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        dtype: Optional[np.dtype] = None,
        shape: Optional[Tuple] = None,
    ) -> Dict[str, np.ndarray]:
        """Convert DataFrame columns to dictionary of arrays"""
        pass

    @abstractmethod
    def decode_array_columns(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        dtype: Optional[np.dtype] = None,
        shape: Optional[Tuple] = None,
    ) -> pd.DataFrame:
        """Decode binary columns in DataFrame to numpy arrays"""
        pass


# EOF
