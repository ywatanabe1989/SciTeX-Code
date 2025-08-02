#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/resource/test__log_processor_usages.py

"""Tests for processor usage logging functionality."""

import math
import os
import tempfile
import time
from multiprocessing import Process
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest

from scitex.resource import log_processor_usages
from scitex.resource._log_processor_usages import (
    _add,
    _ensure_log_file,
    _log_processor_usages,
)


class TestLogProcessorUsages:
    """Test suite for log_processor_usages function."""
    
    @patch('scitex.resource._log_processor_usages._log_processor_usages')
    def test_foreground_execution(self, mock_log):
        """Test foreground execution mode."""
        mock_log.return_value = None
        
        result = log_processor_usages(
            path="/tmp/test.csv",
            limit_min=1,
            interval_s=0.1,
            background=False
        )
        
        assert result is None
        mock_log.assert_called_once_with(
            path="/tmp/test.csv",
            limit_min=1,
            interval_s=0.1,
            init=True,
            verbose=False
        )
    
    @patch('scitex.resource._log_processor_usages.Process')
    def test_background_execution(self, mock_process_class):
        """Test background execution mode."""
        mock_process = Mock()
        mock_process_class.return_value = mock_process
        
        result = log_processor_usages(
            path="/tmp/test.csv",
            limit_min=5,
            background=True
        )
        
        assert result == mock_process
        mock_process_class.assert_called_once()
        mock_process.start.assert_called_once()
    
    @patch('scitex.resource._log_processor_usages._log_processor_usages')
    def test_default_parameters(self, mock_log):
        """Test with default parameters."""
        mock_log.return_value = None
        
        log_processor_usages()
        
        mock_log.assert_called_once_with(
            path="/tmp/scitex/processor_usages.csv",
            limit_min=30,
            interval_s=1,
            init=True,
            verbose=False
        )
    
    @patch('scitex.resource._log_processor_usages._log_processor_usages')
    def test_custom_parameters(self, mock_log):
        """Test with custom parameters."""
        mock_log.return_value = None
        
        log_processor_usages(
            path="/custom/path.csv",
            limit_min=10,
            interval_s=2.5,
            init=False,
            verbose=True,
            background=False
        )
        
        mock_log.assert_called_once_with(
            path="/custom/path.csv",
            limit_min=10,
            interval_s=2.5,
            init=False,
            verbose=True
        )


class TestLogProcessorUsagesInternal:
    """Test suite for _log_processor_usages function."""
    
    @patch('scitex.resource._log_processor_usages.time.sleep')
    @patch('scitex.resource._log_processor_usages._add')
    @patch('scitex.resource._log_processor_usages._ensure_log_file')
    def test_basic_logging(self, mock_ensure, mock_add, mock_sleep):
        """Test basic logging functionality."""
        _log_processor_usages(
            path="/tmp/test.csv",
            limit_min=0.05,  # 3 seconds
            interval_s=1.0,
            init=True,
            verbose=False
        )
        
        mock_ensure.assert_called_once_with("/tmp/test.csv", True)
        assert mock_add.call_count == 3  # ceil(3/1) = 3 calls
        assert mock_sleep.call_count == 3
        
        # Check sleep was called with correct interval
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 1.0
    
    @patch('scitex.resource._log_processor_usages.time.sleep')
    @patch('scitex.resource._log_processor_usages._add')
    @patch('scitex.resource._log_processor_usages._ensure_log_file')
    def test_timing_calculation(self, mock_ensure, mock_add, mock_sleep):
        """Test timing calculation with different intervals."""
        _log_processor_usages(
            path="/tmp/test.csv",
            limit_min=0.05,  # 3 seconds  
            interval_s=1.5,
            init=False,
            verbose=True
        )
        
        expected_calls = math.ceil(3 / 1.5)  # ceil(2.0) = 2
        assert mock_add.call_count == expected_calls
        assert mock_sleep.call_count == expected_calls
    
    def test_csv_path_validation(self):
        """Test CSV path validation."""
        with pytest.raises(AssertionError, match="Path must end with .csv"):
            _log_processor_usages(path="/tmp/test.txt")
    
    @patch('scitex.resource._log_processor_usages.time.sleep')
    @patch('scitex.resource._log_processor_usages._add')
    @patch('scitex.resource._log_processor_usages._ensure_log_file')
    def test_verbose_parameter(self, mock_ensure, mock_add, mock_sleep):
        """Test verbose parameter is passed to _add."""
        _log_processor_usages(
            path="/tmp/test.csv",
            limit_min=0.03,  # 2 seconds
            interval_s=1.0,
            verbose=True
        )
        
        # Check verbose=True was passed to each _add call
        for call in mock_add.call_args_list:
            assert call[1]['verbose'] is True


class TestEnsureLogFile:
    """Test suite for _ensure_log_file function."""
    
    @patch('scitex.resource._log_processor_usages.os.path.exists')
    @patch('scitex.resource._log_processor_usages.os.makedirs')
    @patch('scitex.resource._log_processor_usages.pd.DataFrame')
    @patch('scitex.resource._log_processor_usages.printc')
    def test_create_new_file(self, mock_printc, mock_df, mock_makedirs, mock_exists):
        """Test creating new log file."""
        mock_exists.return_value = False
        mock_df_instance = Mock()
        mock_df.return_value = mock_df_instance
        
        _ensure_log_file("/tmp/new/test.csv", init=True)
        
        mock_makedirs.assert_called_once_with("/tmp/new", exist_ok=True)
        mock_df.assert_called_once_with(columns=["Timestamp", "CPU [%]", "RAM [GiB]", "GPU [%]", "VRAM [GiB]"])
        mock_df_instance.to_csv.assert_called_once_with("/tmp/new/test.csv", index=False)
        mock_printc.assert_called_once_with("/tmp/new/test.csv created.")
    
    @patch('scitex.resource._log_processor_usages.os.path.exists')
    @patch('scitex.resource._log_processor_usages.sh')
    @patch('scitex.resource._log_processor_usages.os.makedirs')
    @patch('scitex.resource._log_processor_usages.pd.DataFrame')
    @patch('scitex.resource._log_processor_usages.printc')
    def test_reinitialize_existing_file(self, mock_printc, mock_df, mock_makedirs, mock_sh, mock_exists):
        """Test reinitializing existing log file."""
        mock_exists.return_value = True
        mock_df_instance = Mock()
        mock_df.return_value = mock_df_instance
        
        _ensure_log_file("/tmp/existing.csv", init=True)
        
        mock_sh.assert_called_once_with("rm -f /tmp/existing.csv")
        mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)
        mock_df.assert_called_once()
        mock_df_instance.to_csv.assert_called_once_with("/tmp/existing.csv", index=False)
    
    @patch('scitex.resource._log_processor_usages.os.path.exists')
    @patch('scitex.resource._log_processor_usages.sh')
    @patch('scitex.resource._log_processor_usages.os.makedirs')
    @patch('scitex.resource._log_processor_usages.pd.DataFrame')
    def test_keep_existing_file(self, mock_df, mock_makedirs, mock_sh, mock_exists):
        """Test keeping existing log file when init=False."""
        mock_exists.return_value = True
        
        _ensure_log_file("/tmp/existing.csv", init=False)
        
        mock_sh.assert_not_called()
        mock_makedirs.assert_not_called()
        mock_df.assert_not_called()
    
    @patch('scitex.resource._log_processor_usages.os.path.exists')
    @patch('scitex.resource._log_processor_usages.sh')
    def test_file_removal_error(self, mock_sh, mock_exists):
        """Test error handling during file removal."""
        mock_exists.return_value = True
        mock_sh.side_effect = Exception("Permission denied")
        
        with pytest.raises(RuntimeError, match="Failed to init log file"):
            _ensure_log_file("/tmp/test.csv", init=True)


class TestAddFunction:
    """Test suite for _add function."""
    
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    @patch('builtins.open', new_callable=mock_open)
    def test_basic_append(self, mock_file, mock_get_usage):
        """Test basic data appending."""
        # Mock processor usage data
        mock_df = Mock()
        mock_get_usage.return_value = mock_df
        
        # Mock file position (empty file)
        mock_file.return_value.tell.return_value = 0
        
        _add("/tmp/test.csv", verbose=True)
        
        mock_get_usage.assert_called_once()
        mock_file.assert_called_once_with("/tmp/test.csv", "a")
        mock_df.to_csv.assert_called_once_with(mock_file.return_value, header=True, index=False)
    
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    @patch('builtins.open', new_callable=mock_open)
    def test_append_to_existing(self, mock_file, mock_get_usage):
        """Test appending to existing file (no header)."""
        mock_df = Mock()
        mock_get_usage.return_value = mock_df
        
        # Mock file position (non-empty file)
        mock_file.return_value.tell.return_value = 100
        
        _add("/tmp/test.csv", verbose=False)
        
        mock_df.to_csv.assert_called_once_with(mock_file.return_value, header=False, index=False)
    
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    @patch('builtins.open', new_callable=mock_open)
    def test_header_logic(self, mock_file, mock_get_usage):
        """Test header inclusion logic based on file position."""
        mock_df = Mock()
        mock_get_usage.return_value = mock_df
        
        # Test empty file (header should be included)
        mock_file.return_value.tell.return_value = 0
        _add("/tmp/test.csv")
        assert mock_df.to_csv.call_args[1]['header'] is True
        
        # Reset mock
        mock_df.reset_mock()
        
        # Test non-empty file (header should not be included)
        mock_file.return_value.tell.return_value = 50
        _add("/tmp/test.csv")
        assert mock_df.to_csv.call_args[1]['header'] is False
    
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    def test_file_error_handling(self, mock_get_usage):
        """Test error handling when file cannot be opened."""
        mock_get_usage.return_value = Mock()
        
        with patch('builtins.open', side_effect=IOError("Cannot open file")):
            with pytest.raises(IOError):
                _add("/tmp/test.csv")


class TestIntegration:
    """Integration tests for the logging system."""
    
    def test_real_file_operations(self):
        """Test with real file operations (using temporary files)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test_log.csv")
            
            # Test file creation
            _ensure_log_file(log_path, init=True)
            assert os.path.exists(log_path)
            
            # Read the file and check headers
            with open(log_path, 'r') as f:
                content = f.read()
                assert "Timestamp,CPU [%],RAM [GiB],GPU [%],VRAM [GiB]" in content
    
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    def test_csv_format_validation(self, mock_get_usage):
        """Test that generated CSV has correct format."""
        # Mock realistic processor usage data
        mock_data = pd.DataFrame({
            'Timestamp': ['2024-01-01 10:00:00'],
            'CPU [%]': [25.3],
            'RAM [GiB]': [8.2],
            'GPU [%]': [65.0],
            'VRAM [GiB]': [4.5]
        })
        mock_get_usage.return_value = mock_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test_log.csv")
            
            # Initialize and add data
            _ensure_log_file(log_path, init=True)
            _add(log_path, verbose=False)
            
            # Read and validate CSV content
            df = pd.read_csv(log_path)
            assert len(df) == 1
            assert list(df.columns) == ['Timestamp', 'CPU [%]', 'RAM [GiB]', 'GPU [%]', 'VRAM [GiB]']
            assert df.iloc[0]['CPU [%]'] == 25.3
    
    @patch('scitex.resource._log_processor_usages.time.sleep')
    @patch('scitex.resource._log_processor_usages.get_processor_usages')
    def test_minimal_logging_session(self, mock_get_usage, mock_sleep):
        """Test minimal logging session with mocked time.sleep."""
        mock_data = pd.DataFrame({
            'Timestamp': ['2024-01-01 10:00:00'],
            'CPU [%]': [25.0],
            'RAM [GiB]': [8.0],
            'GPU [%]': [65.0],
            'VRAM [GiB]': [4.0]
        })
        mock_get_usage.return_value = mock_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "minimal_test.csv")
            
            # Run very short logging session
            _log_processor_usages(
                path=log_path,
                limit_min=0.03,  # ~2 seconds
                interval_s=1.0,
                init=True,
                verbose=False
            )
            
            # Verify file exists and has expected entries
            assert os.path.exists(log_path)
            df = pd.read_csv(log_path)
            assert len(df) >= 1  # Should have at least one entry

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/resource/_log_processor_usages.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 16:28:53 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/resource/_log_processor_usages.py
# 
# """
# Functionality:
#     * Monitors and logs system resource utilization over time
# Input:
#     * Path for saving logs
#     * Monitoring duration and interval
# Output:
#     * CSV file containing time-series resource usage data
# Prerequisites:
#     * scitex package with processor usage monitoring capabilities
# """
# 
# """Imports"""
# import math
# import os
# import sys
# import time
# from multiprocessing import Process
# from typing import Union
# 
# import matplotlib.pyplot as plt
# import scitex
# import pandas as pd
# 
# from .._sh import sh
# from ..io._load import load
# from ..io._save import save
# from ..str import printc
# from ._get_processor_usages import get_processor_usages
# 
# """Functions & Classes"""
# 
# 
# def log_processor_usages(
#     path: str = "/tmp/scitex/processor_usages.csv",
#     limit_min: float = 30,
#     interval_s: float = 1,
#     init: bool = True,
#     verbose: bool = False,
#     background: bool = False,
# ) -> Union[None, Process]:
#     """Logs system resource usage over time.
# 
#     Parameters
#     ----------
#     path : str
#         Path to save the log file
#     limit_min : float
#         Monitoring duration in minutes
#     interval_s : float
#         Sampling interval in seconds
#     init : bool
#         Whether to clear existing log file
#     verbose : bool
#         Whether to print the log
#     background : bool
#         Whether to run in background
# 
#     Returns
#     -------
#     Union[None, Process]
#         Process object if background=True, None otherwise
#     """
#     if background:
#         process = Process(
#             target=_log_processor_usages,
#             args=(path, limit_min, interval_s, init, verbose),
#         )
#         process.start()
#         return process
# 
#     return _log_processor_usages(
#         path=path,
#         limit_min=limit_min,
#         interval_s=interval_s,
#         init=init,
#         verbose=verbose,
#     )
# 
# 
# def _log_processor_usages(
#     path: str = "/tmp/scitex/processor_usages.csv",
#     limit_min: float = 30,
#     interval_s: float = 1,
#     init: bool = True,
#     verbose: bool = False,
# ) -> None:
#     """Logs system resource usage over time.
# 
#     Parameters
#     ----------
#     path : str
#         Path to save the log file
#     limit_min : float
#         Monitoring duration in minutes
#     interval_s : float
#         Sampling interval in seconds
#     init : bool
#         Whether to clear existing log file
#     verbose : bool
#         Whether to print the log
# 
#     Example
#     -------
#     >>> log_processor_usages(path="usage_log.csv", limit_min=5)
#     """
#     assert path.endswith(".csv"), "Path must end with .csv"
# 
#     # Log file initialization
#     _ensure_log_file(path, init)
#     printc(f"Log file can be monitored with with `tail -f {path}`")
# 
#     limit_s = limit_min * 60
#     n_max = math.ceil(limit_s // interval_s)
# 
#     for _ in range(n_max):
#         _add(path, verbose=verbose)
#         time.sleep(interval_s)
# 
# 
# # def _ensure_log_file(path: str, init: bool) -> None:
# #     def _create_path(path):
# #         os.makedirs(os.path.dirname(path), exist_ok=True)
# #         empty_df = pd.DataFrame()
# #         save(empty_df, path, verbose=False)
# #         printc(f"{path} created.")
# 
# #     if not os.path.exists(path):
# #         _create_path(path)
# 
# #     else:
# #         if init and os.path.exists(path):
# #             try:
# #                 sh(f"rm -f {path}")
# #                 _create_path(path)
# #             except Exception as err:
# #                 raise RuntimeError(f"Failed to init log file: {err}")
# 
# # def _add(path: str, verbose: bool = True) -> None:
# #     past = load(path)
# #     now = get_processor_usages()
# 
# #     combined = pd.concat([past, now]).round(3)
# #     save(combined, path, verbose=verbose)
# 
# 
# def _add(path: str, verbose: bool = True) -> None:
#     """Appends current resource usage to CSV file."""
#     now = get_processor_usages()
# 
#     # Append mode without loading entire file
#     with open(path, "a") as f:
#         now.to_csv(f, header=f.tell() == 0, index=False)
# 
# 
# def _ensure_log_file(path: str, init: bool) -> None:
#     """Creates or reinitializes log file with headers."""
# 
#     def _create_path(path):
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         # Write only headers
#         headers = ["Timestamp", "CPU [%]", "RAM [GiB]", "GPU [%]", "VRAM [GiB]"]
#         pd.DataFrame(columns=headers).to_csv(path, index=False)
#         printc(f"{path} created.")
# 
#     if not os.path.exists(path):
#         _create_path(path)
#     elif init:
#         try:
#             sh(f"rm -f {path}")
#             _create_path(path)
#         except Exception as err:
#             raise RuntimeError(f"Failed to init log file: {err}")
# 
# 
# main = log_processor_usages
# 
# if __name__ == "__main__":
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt, verbose=False)
#     main()
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # python -c "import scitex; scitex.resource.log_processor_usages(\"/tmp/processor_usages.csv\", init=True)"
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/resource/_log_processor_usages.py
# --------------------------------------------------------------------------------
