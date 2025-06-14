#!/usr/bin/env python3
"""Tests for scitex.gen._close module."""

import os
import sys
import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call
import pytest

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# Import public function from scitex.gen
from scitex.gen import close

# Import private functions directly from the module file
from scitex.gen._close import (
    _format_diff_time,
    _process_timestamp,
    _save_configs,
    _args_to_str,
    running2finished,
)


class TestFormatDiffTime:
    """Test cases for _format_diff_time function."""

    def test_format_diff_time_seconds(self):
        """Test formatting time difference in seconds."""
        diff = timedelta(seconds=45)
        assert _format_diff_time(diff) == "00:00:45"

    def test_format_diff_time_minutes(self):
        """Test formatting time difference in minutes."""
        diff = timedelta(minutes=5, seconds=30)
        assert _format_diff_time(diff) == "00:05:30"

    def test_format_diff_time_hours(self):
        """Test formatting time difference in hours."""
        diff = timedelta(hours=2, minutes=15, seconds=10)
        assert _format_diff_time(diff) == "02:15:10"

    def test_format_diff_time_large(self):
        """Test formatting large time difference."""
        diff = timedelta(hours=25, minutes=30, seconds=45)
        assert _format_diff_time(diff) == "25:30:45"


class TestProcessTimestamp:
    """Test cases for _process_timestamp function."""

    def test_process_timestamp_basic(self):
        """Test basic timestamp processing."""
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 30, 45)

        CONFIG = {"START_TIME": start_time}

        with patch("scitex.gen._close.datetime") as mock_datetime:
            mock_datetime.now.return_value = end_time
            _process_timestamp(CONFIG, verbose=False)

        assert CONFIG["END_TIME"] == end_time
        assert CONFIG["RUN_TIME"] == "02:30:45"

    def test_process_timestamp_verbose(self, capsys):
        """Test timestamp processing with verbose output."""
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 10, 5, 30)

        CONFIG = {"START_TIME": start_time}

        with patch("scitex.gen._close.datetime") as mock_datetime:
            mock_datetime.now.return_value = end_time
            _process_timestamp(CONFIG, verbose=True)

        captured = capsys.readouterr()
        assert "START TIME:" in captured.out
        assert "END TIME:" in captured.out
        assert "RUN TIME: 00:05:30" in captured.out

    def test_process_timestamp_exception(self):
        """Test exception handling in timestamp processing."""
        CONFIG = {}  # Missing START_TIME

        # Should not raise exception, just print it
        _process_timestamp(CONFIG, verbose=False)


class TestArgsToStr:
    """Test cases for _args_to_str function."""

    def test_args_to_str_basic(self):
        """Test converting basic args dict to string."""
        args = {"param1": "value1", "param2": 123, "param3": True}

        result = _args_to_str(args)
        assert "param1" in result and "value1" in result
        assert "param2" in result and "123" in result
        assert "param3" in result and "True" in result

    def test_args_to_str_none(self):
        """Test with None args."""
        result = _args_to_str(None)
        assert result == ""

    def test_args_to_str_empty_dict(self):
        """Test with empty dictionary."""
        result = _args_to_str({})
        assert result == ""

    def test_args_to_str_formatting(self):
        """Test proper formatting with alignment."""
        args = {"short": "val", "longer_param": "value"}

        result = _args_to_str(args)
        lines = result.split("\n")
        # Check that longer keys are properly aligned
        assert len(lines) == 2
        assert " : " in lines[0]
        assert " : " in lines[1]


class TestSaveConfigs:
    """Test cases for _save_configs function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_save_configs_basic(self, temp_dir):
        """Test basic config saving."""
        CONFIG = {"SDIR": temp_dir, "param1": "value1", "param2": 123}

        _save_configs(CONFIG)

        # Check if CONFIG.pkl was saved
        config_file = os.path.join(temp_dir, "CONFIG.pkl")
        assert os.path.exists(config_file)

    @patch("scitex.gen._close.scitex_io_save")
    def test_save_configs_exception(self, mock_save):
        """Test exception handling in save_configs."""
        mock_save.side_effect = Exception("Save failed")
        CONFIG = {"SDIR": "/invalid/path"}

        # Should not raise exception
        _save_configs(CONFIG)


class TestRunning2Finished:
    """Test cases for running2finished function."""

    @pytest.fixture
    def setup_dirs(self):
        """Set up test directories."""
        with tempfile.TemporaryDirectory() as base_dir:
            running_dir = os.path.join(base_dir, "RUNNING", "test_exp")
            os.makedirs(running_dir)

            # Create some test files
            with open(os.path.join(running_dir, "test.txt"), "w") as f:
                f.write("test content")

            os.makedirs(os.path.join(running_dir, "subdir"))
            with open(os.path.join(running_dir, "subdir", "sub.txt"), "w") as f:
                f.write("sub content")

            yield base_dir, running_dir

    def test_running2finished_success(self, setup_dirs):
        """Test moving from RUNNING to FINISHED_SUCCESS."""
        base_dir, running_dir = setup_dirs

        CONFIG = {"SDIR": running_dir}
        result_config = running2finished(CONFIG, exit_status=0, remove_src_dir=True)

        # Check destination directory
        expected_dest = running_dir.replace("RUNNING/", "FINISHED_SUCCESS/")
        assert os.path.exists(expected_dest)
        assert os.path.exists(os.path.join(expected_dest, "test.txt"))
        assert os.path.exists(os.path.join(expected_dest, "subdir", "sub.txt"))

        # Check source directory removed
        assert not os.path.exists(running_dir)

        # Check CONFIG updated
        assert result_config["SDIR"] == expected_dest

    def test_running2finished_error(self, setup_dirs):
        """Test moving from RUNNING to FINISHED_ERROR."""
        base_dir, running_dir = setup_dirs

        CONFIG = {"SDIR": running_dir}
        result_config = running2finished(CONFIG, exit_status=1, remove_src_dir=False)

        # Check destination directory
        expected_dest = running_dir.replace("RUNNING/", "FINISHED_ERROR/")
        assert os.path.exists(expected_dest)

        # Check source directory still exists
        assert os.path.exists(running_dir)

    def test_running2finished_none_status(self, setup_dirs):
        """Test moving from RUNNING to FINISHED with None status."""
        base_dir, running_dir = setup_dirs

        CONFIG = {"SDIR": running_dir}
        result_config = running2finished(CONFIG, exit_status=None)

        # Check destination directory
        expected_dest = running_dir.replace("RUNNING/", "FINISHED/")
        assert os.path.exists(expected_dest)


class TestClose:
    """Test cases for the main close function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock CONFIG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            return {
                "SDIR": tmpdir,
                "START_TIME": datetime(2023, 1, 1, 10, 0, 0),
                "ID": "test_id",
                "FILE": "test_file.py",
            }

    @patch("scitex.gen._close._process_timestamp")
    @patch("scitex.gen._close._save_configs")
    @patch("scitex.gen._close.running2finished")
    def test_close_basic(self, mock_r2f, mock_save, mock_timestamp, mock_config):
        """Test basic close functionality."""
        mock_r2f.return_value = mock_config

        close(mock_config, verbose=False, notify=False)

        # Check functions were called
        mock_timestamp.assert_called_once()
        mock_save.assert_called_once()
        mock_r2f.assert_called_once()

    @patch("scitex.gen._close.scitex_utils_notify")
    def test_close_with_notify(self, mock_notify, mock_config):
        """Test close with notification."""
        close(mock_config, verbose=False, notify=True, message="Test complete")

        # Check notification was called
        mock_notify.assert_called_once()
        call_args = mock_notify.call_args[1]
        assert "Test complete" in call_args["message"]
        assert call_args["ID"] == "test_id"


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_close.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-14 21:12:25 (ywatanabe)"
# # File: ./src/scitex/gen/_close.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_close.py"
#
# import os
# import re
# import shutil
# import time
# from datetime import datetime
# from glob import glob as _glob
#
# from ..io import flush as scitex_io_flush
# from ..io import save as scitex_io_save
# from ..str._printc import printc
# from ..utils._notify import notify as scitex_utils_notify
#
#
# def _format_diff_time(diff_time):
#     # Get total seconds from the timedelta object
#     total_seconds = int(diff_time.total_seconds())
#
#     # Calculate hours, minutes and seconds
#     hours = total_seconds // 3600
#     minutes = (total_seconds % 3600) // 60
#     seconds = total_seconds % 60
#
#     # Format the time difference as a string
#     diff_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
#     return diff_time_str
#
#
# def _process_timestamp(CONFIG, verbose=True):
#     try:
#         CONFIG["END_TIME"] = datetime.now()
#         CONFIG["RUN_TIME"] = _format_diff_time(
#             CONFIG["END_TIME"] - CONFIG["START_TIME"]
#         )
#         if verbose:
#             print()
#             print(f"START TIME: {CONFIG['START_TIME']}")
#             print(f"END TIME: {CONFIG['END_TIME']}")
#             print(f"RUN TIME: {CONFIG['RUN_TIME']}")
#             print()
#
#     except Exception as e:
#         print(e)
#
#     return CONFIG
#
#
# def _save_configs(CONFIG):
#     scitex_io_save(CONFIG, CONFIG["SDIR"] + "CONFIGS/CONFIG.pkl", verbose=False)
#     scitex_io_save(CONFIG, CONFIG["SDIR"] + "CONFIGS/CONFIG.yaml", verbose=False)
#
#
# def _escape_ANSI_from_log_files(log_files):
#     ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
#
#     # ANSI code escape
#     for f in log_files:
#         with open(f, "r", encoding="utf-8") as file:
#             content = file.read()
#         cleaned_content = ansi_escape.sub("", content)
#         with open(f, "w", encoding="utf-8") as file:
#             file.write(cleaned_content)
#
#
# def _args_to_str(args_dict):
#     """Convert args dictionary to formatted string."""
#     if args_dict:
#         max_key_length = max(len(str(k)) for k in args_dict.keys())
#         return "\n".join(
#             f"{str(k):<{max_key_length}} : {str(v)}"
#             for k, v in sorted(args_dict.items())
#         )
#     else:
#         return ""
#
# def close(CONFIG, message=":)", notify=False, verbose=True, exit_status=None):
#     try:
#         CONFIG.EXIT_STATUS = exit_status
#         CONFIG = CONFIG.to_dict()
#         CONFIG = _process_timestamp(CONFIG, verbose=verbose)
#         sys = CONFIG.pop("sys")
#         _save_configs(CONFIG)
#         # scitex_io_flush(sys=sys)
#
#         # RUNNING to RUNNING2FINISHEDED
#         CONFIG = running2finished(CONFIG, exit_status=exit_status)
#         # scitex_io_flush(sys=sys)
#
#         # ANSI code escape
#         log_files = _glob(CONFIG["SDIR"] + "logs/*.log")
#         _escape_ANSI_from_log_files(log_files)
#         # scitex_io_flush(sys=sys)
#
#         if CONFIG.get("ARGS"):
#             message += f"\n{_args_to_str(CONFIG.get('ARGS'))}"
#
#         if notify:
#             try:
#                 message = (
#                     f"[DEBUG]\n" + str(message)
#                     if CONFIG.get("DEBUG", False)
#                     else str(message)
#                 )
#                 scitex_utils_notify(
#                     message=message,
#                     ID=CONFIG["ID"],
#                     file=CONFIG.get("FILE"),
#                     attachment_paths=log_files,
#                     verbose=verbose,
#                 )
#                 # scitex_io_flush(sys=sys)
#             except Exception as e:
#                 print(e)
#
#     finally:
#         # Only close if they're custom file objects
#         if hasattr(sys, 'stdout') and hasattr(sys.stdout, 'close') and not sys.stdout.closed:
#             if sys.stdout != sys.__stdout__:
#                 sys.stdout.close()
#         if hasattr(sys, 'stderr') and hasattr(sys.stderr, 'close') and not sys.stderr.closed:
#             if sys.stderr != sys.__stderr__:
#                 sys.stderr.close()
#     # finally:
#     #     # Ensure file handles are closed
#     #     if hasattr(sys, 'stdout') and hasattr(sys.stdout, 'close'):
#     #         sys.stdout.close()
#     #     if hasattr(sys, 'stderr') and hasattr(sys.stderr, 'close'):
#     #         sys.stderr.close()
#     # # try:
#     # #     sys.stdout.close()
#     # #     sys.stderr.close()
#     # # except Exception as e:
#     # #     print(e)
#
#
# def running2finished(CONFIG, exit_status=None, remove_src_dir=True, max_wait=60):
#     if exit_status == 0:
#         dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED_SUCCESS/")
#     elif exit_status == 1:
#         dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED_ERROR/")
#     else:  # exit_status is None:
#         dest_dir = CONFIG["SDIR"].replace("RUNNING/", "FINISHED/")
#
#     src_dir = CONFIG["SDIR"]
#     # if dest_dir is None:
#     #     dest_dir = src_dir.replace("RUNNING/", "FINISHED/")
#
#     os.makedirs(dest_dir, exist_ok=True)
#     try:
#
#         # Copy files individually
#         for item in os.listdir(src_dir):
#             s = os.path.join(src_dir, item)
#             d = os.path.join(dest_dir, item)
#             if os.path.isdir(s):
#                 shutil.copytree(s, d)
#             else:
#                 shutil.copy2(s, d)
#
#         start_time = time.time()
#         while not os.path.exists(dest_dir) and time.time() - start_time < max_wait:
#             time.sleep(0.1)
#         if os.path.exists(dest_dir):
#             printc(
#                 f"Congratulations! The script completed.\n\n{dest_dir}",
#                 c="yellow",
#             )
#             if remove_src_dir:
#                 shutil.rmtree(src_dir)
#         else:
#             print(f"Copy operation timed out after {max_wait} seconds")
#
#         CONFIG["SDIR"] = dest_dir
#     except Exception as e:
#         print(e)
#
#     finally:
#         return CONFIG
#
#
# if __name__ == "__main__":
#     import sys
#
#     import matplotlib.pyplot as plt
#     from icecream import ic
#
#     from .._start import start
#
#     CONFIG, sys.stdout, sys.stderr, plt, CC = start(sys, plt, verbose=False)
#
#     ic("aaa")
#     ic("bbb")
#     ic("ccc")
#
#     close(CONFIG)
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_close.py
# --------------------------------------------------------------------------------
