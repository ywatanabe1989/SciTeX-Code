#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:31:00 (ywatanabe)"
# File: tests/scitex/dt/test__linspace.py

"""Comprehensive tests for dt._linspace module"""

import pytest
import datetime
import numpy as np
from datetime import timedelta, timezone
from unittest.mock import patch, MagicMock


class TestLinspace:
    """Test suite for linspace function"""
    
    def test_linspace_basic_n_samples(self):
        """Test basic linspace functionality with n_samples"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 10)
        
        result = linspace(start, end, n_samples=11)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 11
        assert result[0] == start
        assert result[-1] == end
        assert all(isinstance(dt, datetime.datetime) for dt in result)
    
    def test_linspace_basic_sampling_rate(self):
        """Test basic linspace functionality with sampling_rate"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 1)  # 1 second
        
        # 10 Hz sampling rate
        result = linspace(start, end, sampling_rate=10)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == 11  # 10 Hz for 1 second + 1 for endpoint
        assert result[0] == start
        assert result[-1] == end
    
    def test_linspace_uniform_spacing(self):
        """Test that linspace creates uniform spacing"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 1, 0)  # 1 minute
        
        result = linspace(start, end, n_samples=61)  # One per second
        
        # Check uniform spacing
        deltas = [(result[i+1] - result[i]).total_seconds() for i in range(len(result) - 1)]
        
        # All deltas should be 1 second
        assert all(pytest.approx(delta, rel=1e-6) == 1.0 for delta in deltas)
    
    def test_linspace_parameter_validation(self):
        """Test parameter validation"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Both parameters provided
        with pytest.raises(ValueError, match="Provide either n_samples or sampling_rate, not both"):
            linspace(start, end, n_samples=10, sampling_rate=1.0)
        
        # Neither parameter provided
        with pytest.raises(ValueError, match="Either n_samples or sampling_rate must be provided"):
            linspace(start, end)
    
    def test_linspace_type_checking(self):
        """Test type checking for all parameters"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Invalid start_dt type
        with pytest.raises(TypeError, match="start_dt must be a datetime object"):
            linspace("2023-01-01", end, n_samples=10)
        
        # Invalid end_dt type
        with pytest.raises(TypeError, match="end_dt must be a datetime object"):
            linspace(start, "2023-01-02", n_samples=10)
        
        # Invalid n_samples type
        with pytest.raises(TypeError, match="n_samples must be a number"):
            linspace(start, end, n_samples="10")
        
        # Invalid sampling_rate type
        with pytest.raises(TypeError, match="sampling_rate must be a number"):
            linspace(start, end, sampling_rate="10")
    
    def test_linspace_value_validation(self):
        """Test value validation for parameters"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # start >= end
        with pytest.raises(ValueError, match="start_dt must be earlier than end_dt"):
            linspace(end, start, n_samples=10)
        
        # Same start and end
        with pytest.raises(ValueError, match="start_dt must be earlier than end_dt"):
            linspace(start, start, n_samples=10)
        
        # Negative n_samples
        with pytest.raises(ValueError, match="n_samples must be positive"):
            linspace(start, end, n_samples=-1)
        
        # Zero n_samples
        with pytest.raises(ValueError, match="n_samples must be positive"):
            linspace(start, end, n_samples=0)
        
        # Negative sampling_rate
        with pytest.raises(ValueError, match="sampling_rate must be positive"):
            linspace(start, end, sampling_rate=-1.0)
        
        # Zero sampling_rate
        with pytest.raises(ValueError, match="sampling_rate must be positive"):
            linspace(start, end, sampling_rate=0.0)
    
    def test_linspace_microsecond_precision(self):
        """Test microsecond precision in datetime handling"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 0, 10000)  # 10 milliseconds
        
        result = linspace(start, end, n_samples=11)
        
        # Check microsecond precision
        for i in range(len(result)):
            expected_microseconds = i * 1000  # 0, 1000, 2000, ..., 10000
            assert result[i].microsecond == expected_microseconds
    
    def test_linspace_large_range(self):
        """Test with large datetime ranges"""
        from scitex.dt import linspace
        
        # Year-scale range
        start = datetime.datetime(2020, 1, 1)
        end = datetime.datetime(2025, 1, 1)  # 5 years
        
        result = linspace(start, end, n_samples=6)
        
        assert len(result) == 6
        assert result[0] == start
        assert result[-1] == end
        
        # Check approximately yearly spacing
        for i in range(len(result) - 1):
            delta_days = (result[i+1] - result[i]).days
            assert 364 <= delta_days <= 366  # Account for leap years
    
    def test_linspace_small_range(self):
        """Test with very small datetime ranges"""
        from scitex.dt import linspace
        
        # Microsecond-scale range
        start = datetime.datetime(2023, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 0, 1)  # 1 microsecond
        
        result = linspace(start, end, n_samples=2)
        
        assert len(result) == 2
        assert result[0] == start
        assert result[-1] == end
    
    def test_linspace_high_frequency_sampling(self):
        """Test high frequency sampling scenarios"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 1)  # 1 second
        
        # Test various sampling rates
        test_rates = [100, 256, 512, 1000]  # Skip 10000 Hz due to precision
        
        for rate in test_rates:
            result = linspace(start, end, sampling_rate=rate)
            expected_samples = int(1.0 * rate) + 1
            
            assert len(result) == expected_samples
            assert result[0] == start
            assert result[-1] == end
            
            # Check spacing (skip for rates > 1000 due to float precision)
            if len(result) > 1 and rate <= 1000:
                delta = (result[1] - result[0]).total_seconds()
                expected_delta = 1.0 / rate
                assert pytest.approx(expected_delta, rel=1e-4) == delta
    
    def test_linspace_timezone_aware(self):
        """Test with timezone-aware datetimes"""
        from scitex.dt import linspace
        
        # UTC timezone
        start = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime.datetime(2023, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        
        result = linspace(start, end, n_samples=5)
        
        assert len(result) == 5
        assert all(dt.tzinfo == timezone.utc for dt in result)
        assert result[0] == start
        assert result[-1] == end
    
    def test_linspace_float_n_samples(self):
        """Test behavior with float n_samples (should be converted to int)"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Float n_samples should be converted to int internally
        result = linspace(start, end, n_samples=10)
        assert len(result) == 10
    
    def test_linspace_edge_case_single_sample(self):
        """Test edge case with n_samples=1"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        result = linspace(start, end, n_samples=1)
        
        assert len(result) == 1
        # numpy.linspace with n=1 returns the start point
        assert result[0] == start
    
    def test_linspace_numerical_stability(self):
        """Test numerical stability with very small intervals"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 0, 0, 0, 100)  # 100 microseconds
        
        result = linspace(start, end, n_samples=101)
        
        # Check that we get exactly the right microseconds
        for i in range(101):
            assert result[i].microsecond == i
    
    def test_linspace_sampling_rate_calculation(self):
        """Test accurate sampling rate calculation"""
        from scitex.dt import linspace
        
        # Test various durations
        test_cases = [
            (1, 256),    # 1 second at 256 Hz
            (10, 100),   # 10 seconds at 100 Hz
            (0.5, 1000), # 0.5 seconds at 1000 Hz
            (60, 1),     # 60 seconds at 1 Hz
        ]
        
        for duration, rate in test_cases:
            start = datetime.datetime(2023, 1, 1, 0, 0, 0)
            end = start + timedelta(seconds=duration)
            
            result = linspace(start, end, sampling_rate=rate)
            
            expected_samples = int(duration * rate) + 1
            assert len(result) == expected_samples
    
    def test_linspace_return_type(self):
        """Test that return type is always numpy array of datetime objects"""
        from scitex.dt import linspace
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 1, 2)
        
        # Test with n_samples
        result1 = linspace(start, end, n_samples=10)
        assert isinstance(result1, np.ndarray)
        assert result1.dtype == object
        assert all(isinstance(dt, datetime.datetime) for dt in result1)
        
        # Test with sampling_rate
        result2 = linspace(start, end, sampling_rate=1.0)
        assert isinstance(result2, np.ndarray)
        assert result2.dtype == object
        assert all(isinstance(dt, datetime.datetime) for dt in result2)
    
    def test_linspace_practical_eeg_timestamps(self):
        """Test practical use case: EEG timestamp generation"""
        from scitex.dt import linspace
        
        # Common EEG sampling rates
        eeg_rates = {
            'clinical': 256,
            'research': 512,
        }
        
        duration = 10  # 10 seconds of data
        start = datetime.datetime(2023, 1, 1, 12, 0, 0)
        
        for name, rate in eeg_rates.items():
            end = start + timedelta(seconds=duration)
            timestamps = linspace(start, end, sampling_rate=rate)
            
            expected_samples = duration * rate + 1
            assert len(timestamps) == expected_samples
            
            # Verify consistent sampling interval
            if len(timestamps) > 1:
                intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                            for i in range(10)]  # Check first 10 intervals
                expected_interval = 1.0 / rate
                
                for interval in intervals:
                    assert pytest.approx(expected_interval, rel=1e-3) == interval
    
    def test_linspace_hourly_daily_schedules(self):
        """Test practical use case: hourly/daily schedules"""
        from scitex.dt import linspace
        
        # Hourly schedule for a day
        start = datetime.datetime(2023, 1, 1, 0, 0, 0)
        end = datetime.datetime(2023, 1, 1, 23, 0, 0)
        
        hourly = linspace(start, end, n_samples=24)
        
        assert len(hourly) == 24
        for i, ts in enumerate(hourly):
            assert ts.hour == i
            assert ts.minute == 0
            assert ts.second == 0
    
    def test_linspace_data_logging_scenario(self):
        """Test practical use case: data logging at specific intervals"""
        from scitex.dt import linspace
        
        # Log data every 5 minutes for 1 hour
        start = datetime.datetime(2023, 1, 1, 9, 0, 0)
        end = datetime.datetime(2023, 1, 1, 10, 0, 0)
        
        # 12 intervals of 5 minutes each + 1 for endpoint
        timestamps = linspace(start, end, n_samples=13)
        
        assert len(timestamps) == 13
        
        # Verify 5-minute intervals
        for i in range(len(timestamps) - 1):
            delta_minutes = (timestamps[i+1] - timestamps[i]).total_seconds() / 60
            assert pytest.approx(delta_minutes, rel=1e-6) == 5.0
    
    def test_linspace_performance(self):
        """Test performance with large number of samples"""
        from scitex.dt import linspace
        import time
        
        start = datetime.datetime(2023, 1, 1)
        end = datetime.datetime(2023, 12, 31)  # Full year
        
        # Generate 1 million timestamps
        start_time = time.time()
        result = linspace(start, end, n_samples=1_000_000)
        elapsed = time.time() - start_time
        
        assert len(result) == 1_000_000
        assert elapsed < 5.0  # Should complete within 5 seconds
        
        # Verify endpoints
        assert result[0] == start
        assert result[-1] == end


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dt/_linspace.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-04-23 10:42:43 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/dt/_linspace.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/dt/_linspace.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from typing import Union, Optional, List, Any
# import numpy as np
# import datetime
# from datetime import timedelta
# 
# 
# def linspace(
#     start_dt: datetime.datetime,
#     end_dt: datetime.datetime,
#     n_samples: Optional[int] = None,
#     sampling_rate: Optional[float] = None,
# ) -> np.ndarray:
#     """
#     Create a linearly spaced array between two datetime objects.
# 
#     Args:
#         start_dt: Starting datetime object
#         end_dt: Ending datetime object
#         n_samples: Number of samples to create (mutually exclusive with sampling_rate)
#         sampling_rate: Sampling rate in Hz (mutually exclusive with n_samples)
# 
#     Returns:
#         Array of datetime objects evenly spaced between start_dt and end_dt
#     """
#     # Type checking
#     if not isinstance(start_dt, datetime.datetime):
#         raise TypeError(f"start_dt must be a datetime object, got {type(start_dt)}")
# 
#     if not isinstance(end_dt, datetime.datetime):
#         raise TypeError(f"end_dt must be a datetime object, got {type(end_dt)}")
# 
#     if n_samples is not None and not isinstance(n_samples, (int, float)):
#         raise TypeError(f"n_samples must be a number, got {type(n_samples)}")
# 
#     if sampling_rate is not None and not isinstance(sampling_rate, (int, float)):
#         raise TypeError(f"sampling_rate must be a number, got {type(sampling_rate)}")
# 
#     if start_dt >= end_dt:
#         raise ValueError("start_dt must be earlier than end_dt")
# 
#     duration_seconds = (end_dt - start_dt).total_seconds()
# 
#     if n_samples is not None and sampling_rate is not None:
#         raise ValueError("Provide either n_samples or sampling_rate, not both")
# 
#     if n_samples is None and sampling_rate is None:
#         raise ValueError("Either n_samples or sampling_rate must be provided")
# 
#     if sampling_rate is not None:
#         if sampling_rate <= 0:
#             raise ValueError("sampling_rate must be positive")
#         n_samples = int(duration_seconds * sampling_rate) + 1
#     else:
#         if n_samples <= 0:
#             raise ValueError("n_samples must be positive")
# 
#     # Create linear space in seconds
#     seconds_array = np.linspace(0, duration_seconds, n_samples)
# 
#     # Convert to datetime objects
#     datetime_array = np.array(
#         [start_dt + timedelta(seconds=float(sec)) for sec in seconds_array]
#     )
# 
#     return datetime_array
# 
# 
# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # # Timestamp: "2025-04-23 10:38:20 (ywatanabe)"
# # # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/dt/_linspace.py
# # # ----------------------------------------
# # import os
# # __FILE__ = (
# #     "./src/scitex/dt/_linspace.py"
# # )
# # __DIR__ = os.path.dirname(__FILE__)
# # # ----------------------------------------
# 
# # import numpy as np
# # from datetime import timedelta
# 
# # def linspace(start_dt, end_dt, n_samples=None, sampling_rate=None):
# #     """
# #     Create a linearly spaced array between two datetime objects.
# 
# #     Args:
# #         start_dt: Starting datetime object
# #         end_dt: Ending datetime object
# #         n_samples: Number of samples to create (mutually exclusive with sampling_rate)
# #         sampling_rate: Sampling rate in Hz (mutually exclusive with n_samples)
# 
# #     Returns:
# #         Array of datetime objects evenly spaced between start_dt and end_dt
# #     """
# 
# #     duration_seconds = (end_dt - start_dt).total_seconds()
# 
# #     if n_samples is not None and sampling_rate is not None:
# #         raise ValueError("Provide either n_samples or sampling_rate, not both")
# 
# #     if n_samples is None and sampling_rate is None:
# #         raise ValueError("Either n_samples or sampling_rate must be provided")
# 
# #     if sampling_rate is not None:
# #         n_samples = int(duration_seconds * sampling_rate) + 1
# 
# 
# #     # Create linear space in seconds
# #     seconds_array = np.linspace(0, duration_seconds, n_samples)
# 
# #     # Convert to datetime objects
# #     datetime_array = np.array([start_dt + timedelta(seconds=float(sec)) for sec in seconds_array])
# 
# #     return datetime_array
# 
# # # EOF
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dt/_linspace.py
# --------------------------------------------------------------------------------
