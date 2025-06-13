#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:30:00 (ywatanabe)"
# File: tests/scitex/dt/test___init__.py

"""Comprehensive tests for dt module initialization"""

import pytest
import datetime
import numpy as np
from unittest.mock import patch, MagicMock


class TestDtModuleInit:
    """Test suite for scitex.dt module initialization"""
    
    def test_linspace_import(self):
        """Test that linspace function can be imported from scitex.dt"""
        from scitex.dt import linspace
        
        assert callable(linspace)
        assert hasattr(linspace, '__call__')
    
    def test_module_attributes(self):
        """Test that scitex.dt module has expected attributes"""
        import scitex.dt
        
        assert hasattr(scitex.dt, 'linspace')
        assert callable(scitex.dt.linspace)
    
    def test_dynamic_import_mechanism(self):
        """Test that the dynamic import mechanism works correctly"""
        import scitex.dt
        
        # Check that linspace is available after dynamic import
        assert hasattr(scitex.dt, 'linspace')
        
        # Check that cleanup variables are not present
        assert not hasattr(scitex.dt, '__os')
        assert not hasattr(scitex.dt, '__importlib')
        assert not hasattr(scitex.dt, '__inspect')
        assert not hasattr(scitex.dt, 'current_dir')
    
    def test_linspace_basic_functionality(self):
        """Test basic linspace functionality"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 10)
        
        # Test with n_samples
        result = linspace(start, end, n_samples=11)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 11
        assert result[0] == start
        assert result[-1] == end
    
    def test_linspace_with_sampling_rate(self):
        """Test linspace with sampling rate"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 1)  # 1 second
        
        # Test with 10 Hz sampling rate
        result = linspace(start, end, sampling_rate=10)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 11  # 10 Hz for 1 second + 1 for endpoint
        assert result[0] == start
        assert result[-1] == end
    
    def test_linspace_uniform_spacing(self):
        """Test that linspace creates uniform spacing"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 10)
        
        result = linspace(start, end, n_samples=6)
        
        # Check uniform spacing (2 seconds between each)
        for i in range(len(result) - 1):
            delta = (result[i+1] - result[i]).total_seconds()
            assert pytest.approx(delta, rel=1e-6) == 2.0
    
    def test_linspace_parameter_validation(self):
        """Test linspace parameter validation"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Test mutual exclusivity
        with pytest.raises(ValueError, match="Provide either n_samples or sampling_rate, not both"):
            linspace(start, end, n_samples=10, sampling_rate=1.0)
        
        # Test missing parameters
        with pytest.raises(ValueError, match="Either n_samples or sampling_rate must be provided"):
            linspace(start, end)
    
    def test_linspace_type_checking(self):
        """Test linspace type checking"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Test invalid start_dt type
        with pytest.raises(TypeError, match="start_dt must be a datetime object"):
            linspace("2023-01-01", end, n_samples=10)
        
        # Test invalid end_dt type
        with pytest.raises(TypeError, match="end_dt must be a datetime object"):
            linspace(start, "2023-01-02", n_samples=10)
    
    def test_linspace_edge_cases(self):
        """Test linspace edge cases"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Test start >= end
        with pytest.raises(ValueError, match="start_dt must be earlier than end_dt"):
            linspace(end, start, n_samples=10)
        
        # Test negative n_samples
        with pytest.raises(ValueError, match="n_samples must be positive"):
            linspace(start, end, n_samples=-1)
        
        # Test negative sampling_rate
        with pytest.raises(ValueError, match="sampling_rate must be positive"):
            linspace(start, end, sampling_rate=-1.0)
    
    def test_function_signature(self):
        """Test function signature of linspace"""
        from scitex.dt import linspace
        import inspect
        
        sig = inspect.signature(linspace)
        params = list(sig.parameters.keys())
        
        assert 'start_dt' in params
        assert 'end_dt' in params
        assert 'n_samples' in params
        assert 'sampling_rate' in params
        assert len(params) == 4
    
    def test_function_docstring(self):
        """Test that linspace has proper docstring"""
        from scitex.dt import linspace
        
        assert hasattr(linspace, '__doc__')
        assert linspace.__doc__ is not None
        assert 'datetime' in linspace.__doc__
        assert 'linearly spaced' in linspace.__doc__.lower()
    
    def test_module_import_side_effects(self):
        """Test that importing dt module doesn't have unwanted side effects"""
        import sys
        
        # Store original modules
        original_modules = set(sys.modules.keys())
        
        # Import dt module
        import scitex.dt
        
        # Check that only expected modules were added
        new_modules = set(sys.modules.keys()) - original_modules
        
        # Should only add scitex.dt and its submodules
        for module in new_modules:
            assert 'scitex.dt' in module or module in ['datetime', 'numpy']
    
    def test_datetime_range_support(self):
        """Test support for various datetime ranges"""
        from scitex.dt import linspace
        
        # Test microsecond precision
        start = datetime.datetime(2023, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 0, 1000)  # 1 millisecond
        
        result = linspace(start, end, n_samples=2)
        assert len(result) == 2
        assert result[0] == start
        assert result[-1] == end
        
        # Test year-scale range
        start = datetime.datetime(2020, 1, 1)
        end = datetime.datetime(2023, 1, 1)
        
        result = linspace(start, end, n_samples=4)
        assert len(result) == 4
        assert result[0] == start
        assert result[-1] == end
    
    def test_high_frequency_sampling(self):
        """Test high frequency sampling scenarios"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 1)  # 1 second
        
        # Test 1000 Hz sampling
        result = linspace(start, end, sampling_rate=1000)
        
        assert len(result) == 1001  # 1000 Hz for 1 second + 1
        assert result[0] == start
        assert result[-1] == end
        
        # Check that consecutive samples are ~1ms apart
        delta = (result[1] - result[0]).total_seconds()
        assert pytest.approx(delta, rel=1e-6) == 0.001
    
    def test_timezone_awareness(self):
        """Test behavior with timezone-aware datetimes"""
        from scitex.dt import linspace
        from datetime import timezone
        
        # Create timezone-aware datetimes
        start = datetime.datetime(2023, 1, 1, tzinfo=timezone.utc)
        end = datetime.datetime(2023, 1, 2, tzinfo=timezone.utc)
        
        result = linspace(start, end, n_samples=3)
        
        assert len(result) == 3
        assert all(dt.tzinfo == timezone.utc for dt in result)
        assert result[0] == start
        assert result[-1] == end
    
    def test_practical_use_cases(self):
        """Test practical use cases for datetime linspace"""
        from scitex.dt import linspace
        
        # Use case 1: Create hourly timestamps for a day
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 23, 0, 0)
        
        hourly = linspace(start, end, n_samples=24)
        assert len(hourly) == 24
        
        # Verify hourly spacing
        for i in range(len(hourly) - 1):
            delta_hours = (hourly[i+1] - hourly[i]).total_seconds() / 3600
            assert pytest.approx(delta_hours, rel=1e-6) == 1.0
        
        # Use case 2: Create timestamps for EEG data at 256 Hz
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 10)  # 10 seconds
        
        eeg_timestamps = linspace(start, end, sampling_rate=256)
        expected_samples = int(10 * 256) + 1  # 10 seconds at 256 Hz + 1
        assert len(eeg_timestamps) == expected_samples


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
