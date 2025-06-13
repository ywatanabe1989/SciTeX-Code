#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__TimeStamper.py

"""Tests for TimeStamper class."""

import time
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scitex.gen import TimeStamper


class TestTimeStamper:
    """Test cases for TimeStamper class."""

    def test_initialization(self):
        """Test TimeStamper initialization."""
        ts = TimeStamper()

        assert ts.id == -1
        assert ts._is_simple is True
        assert isinstance(ts.start_time, float)
        assert isinstance(ts._df_record, pd.DataFrame)
        assert list(ts._df_record.columns) == [
            "timestamp",
            "elapsed_since_start",
            "elapsed_since_prev",
            "comment",
            "formatted_text",
        ]

    def test_initialization_detailed(self):
        """Test TimeStamper initialization with is_simple=False."""
        ts = TimeStamper(is_simple=False)

        assert ts._is_simple is False

    def test_call_basic(self):
        """Test basic timestamp creation."""
        ts = TimeStamper()

        result = ts("Test comment")

        assert ts.id == 0
        assert isinstance(result, str)
        assert "ID:0" in result
        assert "Test comment" in result
        assert len(ts._df_record) == 1

    def test_call_multiple_timestamps(self):
        """Test multiple timestamp creation."""
        ts = TimeStamper()

        ts("First")
        ts("Second")
        ts("Third")

        assert ts.id == 2
        assert len(ts._df_record) == 3
        assert ts._df_record.loc[0, "comment"] == "First"
        assert ts._df_record.loc[1, "comment"] == "Second"
        assert ts._df_record.loc[2, "comment"] == "Third"

    @patch("time.time")
    def test_elapsed_time_tracking(self, mock_time):
        """Test elapsed time tracking."""
        # Mock time progression
        mock_time.side_effect = [0.0, 0.0, 1.0, 3.0]  # start, start, +1s, +3s

        ts = TimeStamper()
        ts("Start")
        ts("One second")

        # Check elapsed times
        assert ts._df_record.loc[0, "elapsed_since_start"] == 1.0
        assert ts._df_record.loc[0, "elapsed_since_prev"] == 1.0
        assert ts._df_record.loc[1, "elapsed_since_start"] == 3.0
        assert ts._df_record.loc[1, "elapsed_since_prev"] == 2.0

    def test_formatted_output_simple(self):
        """Test simple formatted output."""
        ts = TimeStamper(is_simple=True)

        result = ts("Test")

        # Simple format: "ID:0 | HH:MM:SS Test | "
        assert result.startswith("ID:0 | ")
        assert "Test" in result
        assert result.endswith(" | ")

    def test_formatted_output_detailed(self):
        """Test detailed formatted output."""
        ts = TimeStamper(is_simple=False)

        result = ts("Test")

        # Detailed format includes "total" and "prev"
        assert "Time (id:0):" in result
        assert "total" in result
        assert "prev" in result
        assert "[hh:mm:ss]:" in result
        assert "Test" in result
        assert result.endswith("\n")

    @patch("builtins.print")
    def test_verbose_output(self, mock_print):
        """Test verbose output."""
        ts = TimeStamper()

        # Test with verbose=False (default)
        ts("Silent")
        assert not mock_print.called

        # Test with verbose=True
        result = ts("Verbose", verbose=True)
        mock_print.assert_called_once_with(result)

    def test_record_property(self):
        """Test record property returns correct columns."""
        ts = TimeStamper()
        ts("Test1")
        ts("Test2")

        record = ts.record

        assert isinstance(record, pd.DataFrame)
        assert list(record.columns) == [
            "timestamp",
            "elapsed_since_start",
            "elapsed_since_prev",
            "comment",
        ]
        assert "formatted_text" not in record.columns
        assert len(record) == 2

    def test_delta_basic(self):
        """Test delta calculation between timestamps."""
        with patch("time.time") as mock_time:
            mock_time.side_effect = [0.0, 0.0, 1.0, 3.0, 6.0]

            ts = TimeStamper()
            ts("T0")  # time=1.0
            ts("T1")  # time=3.0
            ts("T2")  # time=6.0

            # Delta between T1 and T0
            delta = ts.delta(1, 0)
            assert delta == 2.0  # 3.0 - 1.0

            # Delta between T2 and T1
            delta = ts.delta(2, 1)
            assert delta == 3.0  # 6.0 - 3.0

    def test_delta_negative_indices(self):
        """Test delta with negative indices."""
        ts = TimeStamper()
        ts("T0")
        ts("T1")
        ts("T2")

        # -1 should refer to last timestamp (id=2)
        # -2 should refer to second-to-last (id=1)
        delta = ts.delta(-1, -2)

        # Should be same as delta(2, 1)
        assert delta == ts.delta(2, 1)

    def test_delta_invalid_ids(self):
        """Test delta with invalid IDs."""
        ts = TimeStamper()
        ts("T0")

        # Test with non-existent ID
        with pytest.raises(ValueError, match="Invalid timestamp ID"):
            ts.delta(0, 5)

        # Test with another non-existent ID
        with pytest.raises(ValueError, match="Invalid timestamp ID"):
            ts.delta(10, 0)

    @patch("time.gmtime")
    def test_time_formatting(self, mock_gmtime):
        """Test time formatting."""
        # Mock gmtime to return predictable result
        mock_struct = MagicMock()
        mock_struct.tm_hour = 1
        mock_struct.tm_min = 23
        mock_struct.tm_sec = 45
        mock_gmtime.return_value = mock_struct

        ts = TimeStamper()
        result = ts("Test")

        # Should format as HH:MM:SS
        assert "01:23:45" in result

    def test_continuous_operation(self):
        """Test continuous operation with sleep."""
        ts = TimeStamper()

        ts("Start")
        time.sleep(0.1)  # Small sleep
        ts("After sleep")

        # Check that elapsed times are positive and increasing
        assert ts._df_record.loc[0, "elapsed_since_start"] > 0
        assert ts._df_record.loc[0, "elapsed_since_prev"] > 0
        assert ts._df_record.loc[0, "elapsed_since_start"] >= 0.1

    def test_empty_comment(self):
        """Test timestamp with empty comment."""
        ts = TimeStamper()

        result = ts()  # No comment provided

        assert ts.id == 0
        assert isinstance(result, str)
        assert ts._df_record.loc[0, "comment"] == ""

    def test_dataframe_structure(self):
        """Test DataFrame structure after multiple operations."""
        ts = TimeStamper()

        ts("First", verbose=False)
        ts("Second", verbose=True)
        ts("Third")

        df = ts._df_record

        # Check structure
        assert len(df) == 3
        assert df.index.tolist() == [0, 1, 2]

        # Check data types
        assert df["timestamp"].dtype == float
        assert df["elapsed_since_start"].dtype == float
        assert df["elapsed_since_prev"].dtype == float
        assert df["comment"].dtype == object
        assert df["formatted_text"].dtype == object

    def test_prev_time_update(self):
        """Test that _prev time is updated correctly."""
        ts = TimeStamper()

        initial_prev = ts._prev
        assert initial_prev == ts.start_time

        ts("First")
        assert ts._prev != initial_prev

        prev_after_first = ts._prev
        ts("Second")
        assert ts._prev != prev_after_first

    def test_thread_safety_consideration(self):
        """Test basic thread safety considerations."""
        # Note: The class is not thread-safe, but test basic operation
        ts = TimeStamper()

        # Simulate rapid calls
        for i in range(10):
            ts(f"Call {i}")

        # Check all were recorded
        assert len(ts._df_record) == 10
        assert ts.id == 9


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
