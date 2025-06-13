#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 12:28:49 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/test__listen.py

import pytest
import unittest.mock as mock
from scitex.dsp import list_and_select_device


class TestListen:
    """Test cases for audio listening functionality."""

    def test_import(self):
        """Test that list_and_select_device can be imported."""
        assert callable(list_and_select_device)

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_valid(self, mock_input, mock_query):
        """Test device selection with valid input."""
        # Mock devices
        mock_devices = [
            {"name": "Device 0", "channels": 2},
            {"name": "Device 1", "channels": 2},
            {"name": "Device 2", "channels": 8},
        ]
        mock_query.return_value = mock_devices
        mock_input.return_value = "1"

        device_id = list_and_select_device()
        assert device_id == 1
        mock_query.assert_called_once()
        mock_input.assert_called_once()

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_invalid_id(self, mock_input, mock_query):
        """Test device selection with invalid device ID."""
        mock_devices = [
            {"name": "Device 0", "channels": 2},
            {"name": "Device 1", "channels": 2},
        ]
        mock_query.return_value = mock_devices
        mock_input.return_value = "5"  # Out of range

        device_id = list_and_select_device()
        assert device_id == 0  # Should return default

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_non_numeric(self, mock_input, mock_query):
        """Test device selection with non-numeric input."""
        mock_devices = [{"name": "Device 0", "channels": 2}]
        mock_query.return_value = mock_devices
        mock_input.return_value = "abc"  # Non-numeric

        device_id = list_and_select_device()
        assert device_id == 0  # Should return default

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_negative_id(self, mock_input, mock_query):
        """Test device selection with negative device ID."""
        mock_devices = [
            {"name": "Device 0", "channels": 2},
            {"name": "Device 1", "channels": 2},
        ]
        mock_query.return_value = mock_devices
        mock_input.return_value = "-1"  # Negative

        device_id = list_and_select_device()
        assert device_id == 0  # Should return default

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    @mock.patch("builtins.print")
    def test_list_and_select_device_prints_devices(
        self, mock_print, mock_input, mock_query
    ):
        """Test that device list is printed."""
        mock_devices = [
            {"name": "Device 0", "channels": 2},
            {"name": "Device 1", "channels": 2},
        ]
        mock_query.return_value = mock_devices
        mock_input.return_value = "0"

        device_id = list_and_select_device()

        # Check that devices were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Available audio devices:" in str(call) for call in print_calls)
        assert any(str(mock_devices) in str(call) for call in print_calls)

    @mock.patch("sounddevice.query_devices")
    def test_list_and_select_device_query_error(self, mock_query):
        """Test handling of sounddevice errors."""
        import sounddevice as sd

        mock_query.side_effect = sd.PortAudioError("No devices found")

        device_id = list_and_select_device()
        assert device_id == 0  # Should return default on error

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_empty_input(self, mock_input, mock_query):
        """Test device selection with empty input."""
        mock_devices = [{"name": "Device 0", "channels": 2}]
        mock_query.return_value = mock_devices
        mock_input.return_value = ""  # Empty string

        device_id = list_and_select_device()
        assert device_id == 0  # Should return default

    @mock.patch("sounddevice.query_devices")
    @mock.patch("builtins.input")
    def test_list_and_select_device_boundary_valid(self, mock_input, mock_query):
        """Test device selection at boundary (max valid ID)."""
        mock_devices = [
            {"name": "Device 0", "channels": 2},
            {"name": "Device 1", "channels": 2},
            {"name": "Device 2", "channels": 2},
        ]
        mock_query.return_value = mock_devices
        mock_input.return_value = "2"  # Max valid index

        device_id = list_and_select_device()
        assert device_id == 2

    def test_pulse_server_env_set(self):
        """Test that PULSE_SERVER environment variable is set."""
        import os

        assert "PULSE_SERVER" in os.environ
        assert os.environ["PULSE_SERVER"] == "unix:/mnt/wslg/PulseServer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
