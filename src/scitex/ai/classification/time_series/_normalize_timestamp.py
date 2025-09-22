#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:21:06 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/time_series/_normalize_timestamp.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/ml/classification/time_series/_normalize_timestamp.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Timestamp Standardization Utilities

Functionality:
- Standardizes timestamps to consistent format defined in CONFIG.FORMATS.TIMESTAMP
- Handles various input formats (datetime objects, strings, timestamps)
- Provides UTC normalization
- Ensures consistent timestamp formatting across the codebase

Input formats supported:
- datetime objects (with or without timezone)
- Unix timestamps (int/float)
- Various string formats

Output:
- Standardized timestamp strings in format: "%Y-%m-%d %H:%M:%S.%f"
- UTC normalized timestamps
- Validation utilities

Prerequisites:
- CONFIG.FORMATS.TIMESTAMP for standard format
"""

"""Imports"""
import argparse
from datetime import datetime, timezone
from typing import Union

import scitex as stx

"""Parameters"""
# Default standard format if CONFIG not available
try:
    CONFIG = stx.io.load_configs()
    STANDARD_FORMAT = CONFIG.FORMATS.TIMESTAMP
except (AttributeError, ImportError):
    # Fallback to a sensible default
    STANDARD_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


# Common alternative formats to try when parsing
ALTERNATIVE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",  # ISO 8601 with T (no microseconnds)
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S.%f",
    "%Y/%m/%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S.%f",
    "%d-%m-%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S.%f",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y, %H:%M:%S",  # Format used in REC_START
    "%Y%m%d %H:%M:%S.%f",
    "%Y%m%d %H:%M:%S",
    "%Y-%m-%d_%H:%M:%S.%f",
    "%Y-%m-%d_%H:%M:%S",
]

"""Functions & Classes"""
def normalize_timestamp(
    timestamp: Union[datetime, str, int, float],
    return_as: str = "str",
    normalize_utc: bool = True,
) -> Union[str, datetime, float]:
    """
    Standardize any timestamp format to requested output type.

    Parameters
    ----------
    timestamp : datetime, str, int, or float
        Timestamp in any supported format
    return_as : str
        Output format: "str" (default), "datetime", or "unix"
    normalize_utc : bool
        If True, normalize to UTC timezone

    Returns
    -------
    str, datetime, or float
        Standardized timestamp in requested format:
        - "str": String in standard format
        - "datetime": datetime object
        - "unix": Unix timestamp (float)

    Examples
    --------
    >>> from datetime import datetime
    >>> dt = datetime(2010, 6, 18, 10, 15, 0)

    >>> normalize_timestamp(dt, return_as="str")
    "2010-06-18 10:15:00.000000"

    >>> normalize_timestamp(dt, return_as="datetime")
    datetime(2010, 6, 18, 10, 15, 0, tzinfo=timezone.utc)

    >>> normalize_timestamp(dt, return_as="unix")
    1276856100.0

    >>> normalize_timestamp("2010/06/18 10:15:00", return_as="str")
    "2010-06-18 10:15:00.000000"
    """
    # Convert to datetime object
    dt = to_datetime(timestamp)

    # Normalize to UTC if requested
    if normalize_utc:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

    # Return in requested format
    if return_as == "str":
        return dt.strftime(STANDARD_FORMAT)
    elif return_as == "datetime":
        return dt
    elif return_as == "unix":
        return dt.timestamp()
    elif return_as == "timestamp":  # Keep for backward compatibility
        return dt.timestamp()
    else:
        raise ValueError(
            f"return_as must be 'str', 'datetime', or 'unix', got: {return_as}"
        )


def to_datetime(timestamp: Union[datetime, str, int, float]) -> datetime:
    """
    Convert various timestamp formats to datetime object.

    Parameters
    ----------
    timestamp : datetime, str, int, or float
        Timestamp in any supported format

    Returns
    -------
    datetime
        Datetime object
    """
    # Already datetime
    if isinstance(timestamp, datetime):
        return timestamp

    # Unix timestamp (int/float)
    elif isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    # String format
    elif isinstance(timestamp, str):
        # Handle nanosecond precision by truncating to microseconds
        if "." in timestamp and len(timestamp.split(".")[-1]) > 6:
            parts = timestamp.split(".")
            # Keep only first 6 digits of fractional seconds
            truncated_microseconds = parts[-1][:6]
            # Handle cases where there might be additional text after microseconds
            if not truncated_microseconds.isdigit():
                # Extract just the digit portion
                import re

                digits = re.match(r"(\d+)", parts[-1])
                if digits:
                    truncated_microseconds = digits.group(1)[:6]
            timestamp = ".".join(parts[:-1] + [truncated_microseconds])

        # Try parsing with various formats
        for fmt in ALTERNATIVE_FORMATS:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue

        # If no format matched, raise error
        raise ValueError(
            f"Could not parse timestamp string: {timestamp}. "
            f"Tried formats: {ALTERNATIVE_FORMATS}"
        )

    else:
        raise TypeError(
            f"timestamp must be datetime, str, int, or float, got: {type(timestamp)}"
        )


def validate_timestamp_format(timestamp_str: str) -> bool:
    """
    Validate that a timestamp string matches the standard format.

    Parameters
    ----------
    timestamp_str : str
        Timestamp string to validate

    Returns
    -------
    bool
        True if string matches standard format
    """
    try:
        datetime.strptime(timestamp_str, STANDARD_FORMAT)
        return True
    except (ValueError, TypeError):
        return False


def format_for_filename(timestamp: Union[datetime, str]) -> str:
    """
    Format timestamp for use in filenames (no spaces or colons).

    Parameters
    ----------
    timestamp : datetime or str
        Timestamp to format

    Returns
    -------
    str
        Filename-safe timestamp string (YYYYMMDD_HHMMSS)

    Examples
    --------
    >>> dt = datetime(2010, 6, 18, 10, 15, 0)
    >>> format_for_filename(dt)
    "20100618_101500"
    """
    dt = to_datetime(timestamp)
    return dt.strftime("%Y%m%d_%H%M%S")


def format_for_display(timestamp: Union[datetime, str]) -> str:
    """
    Format timestamp for human-readable display.

    Parameters
    ----------
    timestamp : datetime or str
        Timestamp to format

    Returns
    -------
    str
        Human-readable timestamp string

    Examples
    --------
    >>> dt = datetime(2010, 6, 18, 10, 15, 0)
    >>> format_for_display(dt)
    "2010-06-18 10:15:00"
    """
    dt = to_datetime(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_patient_recording_start_format(
    patient_recording_start_str: str,
) -> datetime:
    """
    Parse recording start time from CONFIG.PATIENTS.REC_START format.

    Parameters
    ----------
    patient_recording_start_str : str
        Recording start time string in format "DD/MM/YYYY, HH:MM:SS"

    Returns
    -------
    datetime
        Parsed datetime object

    Examples
    --------
    >>> parse_patient_recording_start_format("10/06/2010, 07:40:34")
    datetime(2010, 6, 10, 7, 40, 34)
    """
    REC_START_FORMAT = "%d/%m/%Y, %H:%M:%S"
    return datetime.strptime(patient_recording_start_str, REC_START_FORMAT)


def get_time_delta_seconds(
    start: Union[datetime, str], end: Union[datetime, str]
) -> float:
    """
    Calculate time difference in seconds between two timestamps.

    Parameters
    ----------
    start : datetime or str
        Start timestamp
    end : datetime or str
        End timestamp

    Returns
    -------
    float
        Time difference in seconds
    """
    start_dt = to_datetime(start)
    end_dt = to_datetime(end)
    delta = end_dt - start_dt
    return delta.total_seconds()


def main(args):
    """Test timestamp standardization with various inputs."""

    print("Testing timestamp standardization:")
    print("=" * 60)
    print(f"Standard format: {STANDARD_FORMAT}")
    print()

    # Test data
    dt = datetime(2010, 6, 18, 10, 15, 3, 123456)
    unix_ts = dt.timestamp()

    test_cases = [
        (dt, "datetime object"),
        (unix_ts, "Unix timestamp"),
        ("2010-06-18 10:15:03.123456", "Standard format string"),
        ("2010-06-18 10:15:03", "Without microseconds"),
        ("2010/06/18 10:15:03", "Alternative format 1"),
        ("18/06/2010 10:15:03", "Alternative format 2"),
        ("10/06/2010, 07:40:34", "REC_START format"),
        ("2010-06-18 10:15:03.123456789", "Nanosecond precision"),
    ]

    for input_val, description in test_cases:
        try:
            standardized = normalize_timestamp(
                input_val, return_as="str", normalize_utc=False
            )
            print(f"✓ {description:30} -> {standardized}")
        except Exception as e:
            print(f"✗ {description:30} -> ERROR: {e}")

    print("\nDifferent return formats test:")
    print("-" * 40)
    test_dt = datetime(2010, 6, 18, 10, 15, 3, 123456)
    print(f"Input: {test_dt}")
    print(
        f"  as str:      {normalize_timestamp(test_dt, return_as='str', normalize_utc=False)}"
    )
    print(
        f"  as datetime: {normalize_timestamp(test_dt, return_as='datetime', normalize_utc=False)}"
    )
    print(
        f"  as timestamp: {normalize_timestamp(test_dt, return_as='timestamp', normalize_utc=False)}"
    )

    print("\nFormat validation tests:")
    print("-" * 40)

    valid_tests = [
        ("2010-06-18 10:15:03.123456", True),
        ("2010-06-18 10:15:03", False),
        ("2010/06/18 10:15:03.123456", False),
        ("invalid", False),
    ]

    for test_str, expected in valid_tests:
        is_valid = validate_timestamp_format(test_str)
        status = "✓" if is_valid == expected else "✗"
        print(
            f"{status} '{test_str[:30]:30}' -> Valid: {is_valid} (expected: {expected})"
        )

    print("\nFilename formatting test:")
    print("-" * 40)
    filename_ts = format_for_filename(dt)
    print(f"Filename format: {filename_ts}")

    print("\nDisplay formatting test:")
    print("-" * 40)
    display_ts = format_for_display(dt)
    print(f"Display format: {display_ts}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(
        description="Patient ID standardization utilities for NeuroVista project"
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
