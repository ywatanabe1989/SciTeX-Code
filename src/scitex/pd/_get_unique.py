#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-18 18:42:11 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/pd/_get_unique.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/pd/_get_unique.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Extract unique values from DataFrame columns.
"""

from typing import Any, Optional

import pandas as pd


def get_unique(
    df: pd.DataFrame,
    column: str,
    default: Optional[Any] = None,
    raise_on_multiple: bool = False,
) -> Any:
    """Get value from column if it contains a unique value.

    Args:
        df: DataFrame to extract from
        column: Column name to check
        default: Default value if column doesn't exist or has multiple unique values
        raise_on_multiple: If True, raise ValueError when multiple unique values exist

    Returns:
        The unique value if exactly one exists, otherwise default value

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'patient_id': ['P01', 'P01', 'P01']})
        >>> get_unique(df, 'patient_id')
        'P01'

        >>> df = pd.DataFrame({'patient_id': ['P01', 'P02']})
        >>> get_unique(df, 'patient_id', default='Unknown')
        'Unknown'

        >>> # Raise error on multiple values
        >>> get_unique(df, 'patient_id', raise_on_multiple=True)
        ValueError: Column 'patient_id' has 2 unique values: ['P01', 'P02']
    """
    if column not in df.columns:
        if raise_on_multiple:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        return default

    unique_values = df[column].unique()

    if len(unique_values) == 1:
        return unique_values[0]

    if len(unique_values) > 1 and raise_on_multiple:
        raise ValueError(
            f"Column '{column}' has {len(unique_values)} unique values: "
            f"{list(unique_values[:5])}"
        )

    return default


if __name__ == "__main__":
    # Test the function
    import pandas as pd

    # Test case 1: Unique value
    df1 = pd.DataFrame({"patient_id": ["P01", "P01", "P01"]})
    assert get_unique(df1, "patient_id") == "P01"
    print("✓ Test 1 passed: Unique value extracted")

    # Test case 2: Multiple values with default
    df2 = pd.DataFrame({"patient_id": ["P01", "P02"]})
    assert get_unique(df2, "patient_id", default="Unknown") == "Unknown"
    print("✓ Test 2 passed: Default returned for multiple values")

    # Test case 3: Missing column
    assert get_unique(df1, "missing_col", default="N/A") == "N/A"
    print("✓ Test 3 passed: Default returned for missing column")

    # Test case 4: Raise on multiple
    try:
        get_unique(df2, "patient_id", raise_on_multiple=True)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "has 2 unique values" in str(e)
        print("✓ Test 4 passed: ValueError raised for multiple values")

    print("\nAll tests passed!")

# EOF
