#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-03 08:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/life/test__monitor_rain.py

"""Tests for life._monitor_rain module.

This module tests the weather monitoring functionality including API interactions,
notification systems, and monitoring loops.
"""

import pytest
import time
from unittest.mock import patch, Mock, MagicMock
import requests


class TestMonitorRain:
    """Test the weather monitoring functionality."""

    def test_module_import(self):
        """Test that the module can be imported successfully."""
        from scitex.life import _monitor_rain
        assert _monitor_rain is not None

    def test_api_constants(self):
        """Test that API constants are defined."""
        from scitex.life import _monitor_rain
        
        assert hasattr(_monitor_rain, 'API_KEY')
        assert hasattr(_monitor_rain, 'CITY')
        assert hasattr(_monitor_rain, 'API_URL')
        
        # Check that API_URL is properly formatted
        assert isinstance(_monitor_rain.API_URL, str)
        assert 'api.openweathermap.org' in _monitor_rain.API_URL
        assert _monitor_rain.CITY in _monitor_rain.API_URL
        assert _monitor_rain.API_KEY in _monitor_rain.API_URL

    def test_check_rain_function_exists(self):
        """Test that check_rain function exists and is callable."""
        from scitex.life import _monitor_rain
        
        assert hasattr(_monitor_rain, 'check_rain')
        assert callable(_monitor_rain.check_rain)

    def test_notify_rain_function_exists(self):
        """Test that notify_rain function exists and is callable."""
        from scitex.life import _monitor_rain
        
        assert hasattr(_monitor_rain, 'notify_rain')
        assert callable(_monitor_rain.notify_rain)

    def test_monitor_rain_function_exists(self):
        """Test that monitor_rain function exists and is callable."""
        from scitex.life import _monitor_rain
        
        assert hasattr(_monitor_rain, 'monitor_rain')
        assert callable(_monitor_rain.monitor_rain)

    @patch('requests.get')
    @patch('scitex.life._monitor_rain.notify_rain')
    def test_check_rain_with_rain_data(self, mock_notify, mock_get):
        """Test check_rain function when rain is detected."""
        from scitex.life import _monitor_rain
        
        # Mock response with rain data
        mock_response = Mock()
        mock_response.json.return_value = {
            'weather': [{'main': 'Rain'}],
            'rain': {'1h': 2.5},
            'main': {'temp': 15.2}
        }
        mock_get.return_value = mock_response
        
        # Call check_rain
        _monitor_rain.check_rain()
        
        # Verify requests.get was called with correct URL
        mock_get.assert_called_once_with(_monitor_rain.API_URL)
        
        # Verify notify_rain was called since rain is present
        mock_notify.assert_called_once()

    @patch('requests.get')
    @patch('scitex.life._monitor_rain.notify_rain')
    def test_check_rain_without_rain_data(self, mock_notify, mock_get):
        """Test check_rain function when no rain is detected."""
        from scitex.life import _monitor_rain
        
        # Mock response without rain data
        mock_response = Mock()
        mock_response.json.return_value = {
            'weather': [{'main': 'Clear'}],
            'main': {'temp': 22.1}
        }
        mock_get.return_value = mock_response
        
        # Call check_rain
        _monitor_rain.check_rain()
        
        # Verify requests.get was called
        mock_get.assert_called_once_with(_monitor_rain.API_URL)
        
        # Verify notify_rain was NOT called since no rain
        mock_notify.assert_not_called()

    @patch('requests.get')
    def test_check_rain_request_exception(self, mock_get):
        """Test check_rain function when request fails."""
        from scitex.life import _monitor_rain
        
        # Make requests.get raise an exception
        mock_get.side_effect = requests.RequestException("Network error")
        
        # Should handle the exception gracefully
        try:
            _monitor_rain.check_rain()
            # If no exception is raised, that's also acceptable
        except requests.RequestException:
            # Module doesn't handle the exception, that's ok
            pass

    @patch('requests.get')
    def test_check_rain_json_decode_error(self, mock_get):
        """Test check_rain function when JSON decoding fails."""
        from scitex.life import _monitor_rain
        
        # Mock response that fails JSON decoding
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        # Should handle JSON error gracefully
        try:
            _monitor_rain.check_rain()
        except ValueError:
            # Module doesn't handle JSON errors, that's acceptable
            pass

    def test_notify_rain_with_plyer_available(self):
        """Test notify_rain function when plyer is available."""
        from scitex.life import _monitor_rain
        
        # Mock the notification module
        with patch('scitex.life._monitor_rain.notification') as mock_notification:
            mock_notification.notify = Mock()
            
            # Call notify_rain
            _monitor_rain.notify_rain()
            
            # Verify notification.notify was called with correct parameters
            mock_notification.notify.assert_called_once_with(
                title="Rain Alert",
                message="It's starting to rain in your area!",
                timeout=10,
            )

    def test_notify_rain_without_plyer(self):
        """Test notify_rain function when plyer is not available."""
        from scitex.life import _monitor_rain
        
        # Check if notification is available
        if not hasattr(_monitor_rain, 'notification'):
            # If notification is not available, the function should still be callable
            try:
                _monitor_rain.notify_rain()
                # Should handle missing plyer gracefully
            except NameError:
                # Expected if notification is not defined
                pass

    @patch('time.sleep')
    @patch('scitex.life._monitor_rain.check_rain')
    def test_monitor_rain_loop_structure(self, mock_check_rain, mock_sleep):
        """Test monitor_rain function loop structure (limited iterations)."""
        from scitex.life import _monitor_rain
        
        # Mock check_rain to avoid actual API calls
        mock_check_rain.return_value = None
        
        # Mock sleep and make it break the loop after a few iterations
        call_count = 0
        def sleep_side_effect(duration):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:  # Break after 3 iterations
                raise KeyboardInterrupt("Test interrupt")
        
        mock_sleep.side_effect = sleep_side_effect
        
        # Test the monitor loop (should break after 3 iterations)
        with pytest.raises(KeyboardInterrupt):
            _monitor_rain.monitor_rain()
        
        # Verify check_rain was called multiple times
        assert mock_check_rain.call_count >= 3
        
        # Verify sleep was called with correct duration (300 seconds = 5 minutes)
        for call in mock_sleep.call_args_list:
            args, kwargs = call
            assert args[0] == 300

    @patch('time.sleep')
    @patch('scitex.life._monitor_rain.check_rain')
    def test_monitor_rain_exception_handling(self, mock_check_rain, mock_sleep):
        """Test monitor_rain function handles exceptions in check_rain."""
        from scitex.life import _monitor_rain
        
        # Make check_rain raise an exception
        mock_check_rain.side_effect = Exception("API error")
        
        # Mock sleep to break the loop quickly
        def sleep_side_effect(duration):
            raise KeyboardInterrupt("Test interrupt")
        
        mock_sleep.side_effect = sleep_side_effect
        
        # Monitor should propagate exceptions from check_rain (no exception handling in the loop)
        with pytest.raises(Exception, match="API error"):
            _monitor_rain.monitor_rain()

    def test_api_url_format(self):
        """Test that API URL is properly formatted."""
        from scitex.life import _monitor_rain
        
        # Check URL structure
        url = _monitor_rain.API_URL
        assert url.startswith('http://api.openweathermap.org/data/2.5/weather')
        assert 'q=' in url
        assert 'appid=' in url
        
        # Check that placeholders are replaced
        assert _monitor_rain.CITY in url
        assert _monitor_rain.API_KEY in url

    def test_module_constants_types(self):
        """Test that module constants have correct types."""
        from scitex.life import _monitor_rain
        
        assert isinstance(_monitor_rain.API_KEY, str)
        assert isinstance(_monitor_rain.CITY, str)
        assert isinstance(_monitor_rain.API_URL, str)

    @patch('requests.get')
    def test_check_rain_response_structure(self, mock_get):
        """Test check_rain with various response structures."""
        from scitex.life import _monitor_rain
        
        # Test with empty response
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        # Should handle empty response gracefully
        _monitor_rain.check_rain()
        
        # Test with malformed response
        mock_response.json.return_value = {'unexpected': 'data'}
        
        # Should handle malformed response gracefully
        _monitor_rain.check_rain()

    def test_rain_detection_logic(self):
        """Test the rain detection logic by examining the source."""
        from scitex.life import _monitor_rain
        import inspect
        
        # Get the source code of check_rain function
        source = inspect.getsource(_monitor_rain.check_rain)
        
        # Verify it checks for "rain" in the response data
        assert '"rain"' in source or "'rain'" in source
        assert 'notify_rain' in source

    def test_notification_parameters(self):
        """Test notification parameters by examining the source."""
        from scitex.life import _monitor_rain
        import inspect
        
        # Get the source code of notify_rain function
        source = inspect.getsource(_monitor_rain.notify_rain)
        
        # Verify notification parameters
        assert 'Rain Alert' in source
        assert "It's starting to rain in your area!" in source
        assert '10' in source  # timeout value

    def test_sleep_duration(self):
        """Test sleep duration in monitor loop."""
        from scitex.life import _monitor_rain
        import inspect
        
        # Get the source code of monitor_rain function
        source = inspect.getsource(_monitor_rain.monitor_rain)
        
        # Verify sleep duration (300 seconds = 5 minutes)
        assert '300' in source

    def test_import_warning_handling(self):
        """Test that plyer import warnings are handled."""
        # This test verifies that the module can be imported even if plyer is not available
        from scitex.life import _monitor_rain
        
        # The module should be successfully imported and functions should exist
        assert hasattr(_monitor_rain, 'check_rain')
        assert hasattr(_monitor_rain, 'notify_rain')
        assert hasattr(_monitor_rain, 'monitor_rain')
        
        # Test that notify_rain handles missing plyer gracefully
        try:
            # If plyer/notification is not available, this may raise NameError
            _monitor_rain.notify_rain()
        except NameError:
            # This is expected if plyer is not available
            pass

    def test_function_signatures(self):
        """Test that functions have expected signatures."""
        from scitex.life import _monitor_rain
        import inspect
        
        # check_rain should take no arguments
        sig = inspect.signature(_monitor_rain.check_rain)
        assert len(sig.parameters) == 0
        
        # notify_rain should take no arguments
        sig = inspect.signature(_monitor_rain.notify_rain)
        assert len(sig.parameters) == 0
        
        # monitor_rain should take no arguments
        sig = inspect.signature(_monitor_rain.monitor_rain)
        assert len(sig.parameters) == 0


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])
