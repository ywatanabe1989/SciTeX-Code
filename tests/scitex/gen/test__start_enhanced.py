#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-23 (ywatanabe)"

import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex
from scitex.gen import start
from scitex.gen._start import (
    _print_header,
    _initialize_env,
    _setup_configs,
    _setup_matplotlib,
    _get_debug_mode,
    _get_scitex_version,
    _simplify_relative_path,
    _clear_python_log_dir,
)


class TestStartEnhanced:
    """Enhanced comprehensive tests for scitex.gen.start function."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    @pytest.fixture
    def mock_modules(self):
        """Mock all external module dependencies."""
        mocks = {}
        mock_patches = [
            "scitex.gen._start.gen_ID",
            "scitex.gen._start.load_configs", 
            "scitex.gen._start.configure_mpl",
            "scitex.gen._start.fix_seeds",
            "scitex.gen._start.tee",
            "scitex.gen._start.flush",
            "scitex.gen._start.clean_path",
            "scitex.gen._start._printc",
            "scitex.gen._start.analyze_code_flow",
            "scitex.gen._start.matplotlib",
            "scitex.gen._start.datetime",
            "scitex.gen._start.sleep",
            "scitex.gen._start.pprint",
        ]
        
        for mock_name in mock_patches:
            mocks[mock_name] = patch(mock_name)
        
        # Start all patches
        started_mocks = {}
        for name, mock_patch in mocks.items():
            started_mocks[name] = mock_patch.start()
        
        yield started_mocks
        
        # Stop all patches
        for mock_patch in mocks.values():
            mock_patch.stop()

    @pytest.fixture
    def mock_filesystem(self, temp_dir):
        """Mock filesystem operations."""
        with patch("scitex.gen._start._os") as mock_os:
            mock_os.makedirs = MagicMock()
            mock_os.path.exists = MagicMock(return_value=True)
            mock_os.path.isabs = MagicMock(return_value=True)
            mock_os.path.abspath = MagicMock(return_value=temp_dir)
            mock_os.path.splitext = MagicMock(return_value=(temp_dir + "/test", ".py"))
            mock_os.path.relpath = MagicMock(return_value="./test/relative/path")
            mock_os.getcwd = MagicMock(return_value=temp_dir)
            mock_os.getpid = MagicMock(return_value=12345)
            mock_os.getenv = MagicMock(return_value="testuser")
            
            # Mock the _simplify_relative_path function to avoid regex issues
            with patch("scitex.gen._start._simplify_relative_path", return_value="./test/path"):
                yield mock_os


class TestStartFunctionality(TestStartEnhanced):
    """Test core start function functionality."""

    def test_start_minimal_call(self, mock_modules, mock_filesystem):
        """Test start function with minimal parameters."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        # Execute
        result = start(verbose=False)
        
        # Verify
        assert result is not None
        assert len(result) == 5  # (CONFIGS, stdout, stderr, plt, CC)
        mock_modules["scitex.gen._start.gen_ID"].assert_called_with(N=4)

    def test_start_with_debug_mode(self, mock_modules, mock_filesystem):
        """Test start function in debug mode."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        with patch("scitex.gen._start._get_debug_mode", return_value=True):
            # Execute
            result = start(verbose=False)
            
            # Verify
            assert result is not None
            # Should call gen_ID for debug mode
            mock_modules["scitex.gen._start.gen_ID"].assert_called_with(N=4)

    def test_start_with_system_modules(self, mock_modules, mock_filesystem):
        """Test start function with system modules for I/O redirection."""
        # Setup
        mock_sys = MagicMock()
        mock_sys.stdout = MagicMock()
        mock_sys.stderr = MagicMock()
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        mock_modules["scitex.gen._start.tee"].return_value = (MagicMock(), MagicMock())
        
        # Execute
        result = start(sys=mock_sys, verbose=False)
        
        # Verify
        assert result is not None
        mock_modules["scitex.gen._start.flush"].assert_called_with(mock_sys)
        mock_modules["scitex.gen._start.tee"].assert_called_once()

    def test_start_with_matplotlib_configuration(self, mock_modules, mock_filesystem):
        """Test start function with matplotlib configuration."""
        # Setup
        mock_plt = MagicMock()
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        mock_modules["scitex.gen._start.configure_mpl"].return_value = (mock_plt, {"red": "#FF0000"})
        
        # Execute
        result = start(plt=mock_plt, agg=True, verbose=False)
        
        # Verify
        assert result is not None
        mock_plt.close.assert_called_with("all")
        mock_modules["scitex.gen._start.configure_mpl"].assert_called_once()
        mock_modules["scitex.gen._start.matplotlib"].use.assert_called_with("Agg")

    def test_start_with_random_seeds(self, mock_modules, mock_filesystem):
        """Test start function with random seed configuration."""
        # Setup
        mock_random = MagicMock()
        mock_np = MagicMock()
        mock_torch = MagicMock()
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        # Execute
        start(random=mock_random, np=mock_np, torch=mock_torch, seed=123, verbose=False)
        
        # Verify
        mock_modules["scitex.gen._start.fix_seeds"].assert_called_with(
            os=None, random=mock_random, np=mock_np, torch=mock_torch, seed=123, verbose=False
        )

    def test_start_with_custom_sdir(self, mock_modules, mock_filesystem, temp_dir):
        """Test start function with custom save directory."""
        # Setup
        custom_sdir = os.path.join(temp_dir, "custom_output")
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        # Execute
        result = start(sdir=custom_sdir, verbose=False)
        
        # Verify
        assert result is not None
        mock_filesystem.makedirs.assert_called_with(custom_sdir, exist_ok=True)

    def test_start_with_args_configuration(self, mock_modules, mock_filesystem):
        """Test start function with command line arguments."""
        # Setup
        mock_args = MagicMock()
        mock_args.__dict__ = {"param1": "value1", "param2": "value2"}
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        # Execute
        result = start(args=mock_args, verbose=False)
        
        # Verify
        assert result is not None
        # Config should include args
        configs = result[0]
        assert configs is not None

    def test_start_with_execution_flow_analysis(self, mock_modules, mock_filesystem):
        """Test start function with execution flow analysis enabled."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        mock_modules["scitex.gen._start.analyze_code_flow"].return_value = "Flow structure"
        
        # Execute
        result = start(show_execution_flow=True, verbose=False)
        
        # Verify
        assert result is not None
        mock_modules["scitex.gen._start.analyze_code_flow"].assert_called_once()
        mock_modules["scitex.gen._start._printc"].assert_called()


class TestStartHelperFunctions(TestStartEnhanced):
    """Test helper functions used by start."""

    def test_initialize_env_normal_mode(self, mock_modules):
        """Test environment initialization in normal mode."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "ABCD1234"
        
        with patch("scitex.gen._start._os.getpid", return_value=9999):
            # Execute
            ID, PID = _initialize_env(IS_DEBUG=False)
            
            # Verify
            assert ID == "ABCD1234"
            assert PID == 9999
            mock_modules["scitex.gen._start.gen_ID"].assert_called_with(N=4)

    def test_initialize_env_debug_mode(self, mock_modules):
        """Test environment initialization in debug mode."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "ABCD1234"
        
        with patch("scitex.gen._start._os.getpid", return_value=9999):
            # Execute
            ID, PID = _initialize_env(IS_DEBUG=True)
            
            # Verify
            assert ID == "DEBUG_ABCD1234"
            assert PID == 9999

    def test_setup_configs(self, mock_modules):
        """Test configuration setup."""
        # Setup
        mock_config_obj = MagicMock()
        mock_config_obj.to_dict.return_value = {"base": "config"}
        mock_modules["scitex.gen._start.load_configs"].return_value = mock_config_obj
        
        with patch("scitex.gen._start.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            # Execute
            result = _setup_configs(
                IS_DEBUG=False,
                ID="TEST1234",
                PID=12345,
                file="test.py",
                sdir="/test/dir",
                relative_sdir="./test/dir",
                verbose=True
            )
            
            # Verify
            assert "ID" in result
            assert result["ID"] == "TEST1234"
            assert result["PID"] == 12345
            assert result["START_TIME"] == mock_now
            assert result["FILE"] == "test.py"
            assert result["SDIR"] == "/test/dir"
            assert result["REL_SDIR"] == "./test/dir"

    def test_setup_matplotlib_with_plt(self, mock_modules):
        """Test matplotlib setup when plt is provided."""
        # Setup
        mock_plt = MagicMock()
        mock_CC = {"red": "#FF0000", "blue": "#0000FF", "grey": "#808080"}
        mock_modules["scitex.gen._start.configure_mpl"].return_value = (mock_plt, mock_CC)
        
        # Execute
        result_plt, result_CC = _setup_matplotlib(plt=mock_plt, agg=True)
        
        # Verify
        assert result_plt == mock_plt
        assert result_CC["gray"] == mock_CC["grey"]  # Should add gray alias
        mock_plt.close.assert_called_with("all")
        mock_modules["scitex.gen._start.matplotlib"].use.assert_called_with("Agg")

    def test_setup_matplotlib_without_plt(self):
        """Test matplotlib setup when plt is None."""
        # Execute
        result_plt, result_CC = _setup_matplotlib(plt=None)
        
        # Verify
        assert result_plt is None
        assert result_CC is None

    def test_print_header_verbose(self, capsys):
        """Test header printing in verbose mode."""
        # Setup
        with patch("scitex.gen._start._get_scitex_version", return_value="1.0.0"):
            with patch("scitex.gen._start.sleep"):
                with patch("scitex.gen._start._printc") as mock_printc:
                    with patch("scitex.gen._start.pprint") as mock_pprint:
                        
                        configs = {"test": "config", "debug": True}
                        
                        # Execute
                        _print_header("TEST1234", 12345, "test.py", None, configs, verbose=True)
                        
                        # Verify
                        mock_printc.assert_called()
                        mock_pprint.assert_called_with(configs)

    def test_print_header_non_verbose(self):
        """Test header printing in non-verbose mode."""
        # Setup
        with patch("scitex.gen._start._get_scitex_version", return_value="1.0.0"):
            with patch("scitex.gen._start.sleep"):
                with patch("scitex.gen._start._printc") as mock_printc:
                    with patch("scitex.gen._start.pprint") as mock_pprint:
                        
                        configs = {"test": "config"}
                        
                        # Execute
                        _print_header("TEST1234", 12345, "test.py", None, configs, verbose=False)
                        
                        # Verify
                        mock_printc.assert_called()
                        # pprint should not be called in non-verbose mode
                        mock_pprint.assert_not_called()


class TestStartPathHandling(TestStartEnhanced):
    """Test path handling functionality."""

    def test_simplify_relative_path_basic(self):
        """Test basic relative path simplification."""
        # Setup
        test_path = "/home/user/scripts/memory-load/distance_between_gs_stats/RUNNING/2024Y-09M-12D-02h44m40s_GlBZ"
        
        with patch("scitex.gen._start._os.getcwd", return_value="/home/user"):
            with patch("scitex.gen._start._os.path.relpath", return_value="scripts/memory-load/distance_between_gs_stats/RUNNING/2024Y-09M-12D-02h44m40s_GlBZ"):
                # Execute
                result = _simplify_relative_path(test_path)
                
                # Verify
                expected = "./memory-load/distance_between_gs_stats/"
                assert result == expected

    def test_simplify_relative_path_with_no_base(self):
        """Test relative path simplification when base path is None."""
        # Setup
        test_path = "/absolute/path/RUNNING/timestamp_id/"
        
        with patch("scitex.gen._start._os.getcwd", return_value=None):
            with patch("scitex.gen._start._os.path.relpath", return_value=test_path):
                # Execute
                result = _simplify_relative_path(test_path)
                
                # Verify - should strip RUNNING and timestamp pattern
                assert "/absolute/path/" in result or test_path == result

    def test_clear_python_log_dir_exists(self):
        """Test clearing existing log directory."""
        # Setup
        test_dir = "/test/log/dir"
        
        with patch("scitex.gen._start._os.path.exists", return_value=True):
            with patch("scitex.gen._start._os.system") as mock_system:
                # Execute
                _clear_python_log_dir(test_dir)
                
                # Verify
                mock_system.assert_called_with(f"rm -rf {test_dir}")

    def test_clear_python_log_dir_not_exists(self):
        """Test clearing non-existent log directory."""
        # Setup
        test_dir = "/test/log/dir"
        
        with patch("scitex.gen._start._os.path.exists", return_value=False):
            with patch("scitex.gen._start._os.system") as mock_system:
                # Execute
                _clear_python_log_dir(test_dir)
                
                # Verify
                mock_system.assert_not_called()

    def test_clear_python_log_dir_with_exception(self, capsys):
        """Test clearing log directory with exception handling."""
        # Setup
        test_dir = "/test/log/dir"
        
        with patch("scitex.gen._start._os.path.exists", return_value=True):
            with patch("scitex.gen._start._os.system", side_effect=Exception("Permission denied")):
                # Execute
                _clear_python_log_dir(test_dir)
                
                # Verify - should handle exception gracefully
                captured = capsys.readouterr()
                assert "Failed to clear directory" in captured.out


class TestStartDebugAndVersion(TestStartEnhanced):
    """Test debug mode and version functionality."""

    def test_get_debug_mode_file_exists_true(self):
        """Test debug mode detection when file exists and is true."""
        # Setup
        mock_load_result = {"IS_DEBUG": "true"}
        
        with patch("scitex.gen._start._os.path.exists", return_value=True):
            with patch("scitex.gen._start.load", return_value=mock_load_result):
                # Execute
                result = _get_debug_mode()
                
                # Verify
                assert result is True

    def test_get_debug_mode_file_exists_false(self):
        """Test debug mode detection when file exists and is false."""
        # Setup
        mock_load_result = {"IS_DEBUG": False}
        
        with patch("scitex.gen._start._os.path.exists", return_value=True):
            with patch("scitex.gen._start.load", return_value=mock_load_result):
                # Execute
                result = _get_debug_mode()
                
                # Verify
                assert result is False

    def test_get_debug_mode_file_not_exists(self):
        """Test debug mode detection when file doesn't exist."""
        # Setup
        with patch("scitex.gen._start._os.path.exists", return_value=False):
            # Execute
            result = _get_debug_mode()
            
            # Verify
            assert result is False

    def test_get_debug_mode_with_exception(self):
        """Test debug mode detection with exception handling."""
        # Setup
        with patch("scitex.gen._start._os.path.exists", side_effect=Exception("IO Error")):
            # Execute
            result = _get_debug_mode()
            
            # Verify
            assert result is False

    def test_get_scitex_version_success(self):
        """Test successful scitex version retrieval."""
        # Setup
        import sys
        mock_scitex = MagicMock()
        mock_scitex.__version__ = "1.2.3"
        
        with patch.dict('sys.modules', {'scitex': mock_scitex}):
            # Execute
            result = _get_scitex_version()
            
            # Verify
            assert result == "1.2.3"

    def test_get_scitex_version_exception(self):
        """Test scitex version retrieval with exception."""
        # Setup - force import error by patching import mechanism
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'scitex':
                raise ImportError("Module not found")
            return original_import(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            # Execute
            result = _get_scitex_version()
            
            # Verify
            assert result == "(not found)"


class TestStartEdgeCases(TestStartEnhanced):
    """Test edge cases and error conditions."""

    def test_start_with_ipython_file_detection(self, mock_modules, mock_filesystem):
        """Test start function with ipython file detection."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        with patch("scitex.gen._start.inspect.stack") as mock_stack:
            mock_frame = MagicMock()
            mock_frame.filename = "/path/to/ipython_console.py"
            mock_stack.return_value = [None, mock_frame]  # [1] gets the calling frame
            
            # Execute
            result = start(verbose=False)
            
            # Verify
            assert result is not None
            # Should handle ipython detection

    def test_start_with_relative_file_path(self, mock_modules, mock_filesystem):
        """Test start function with relative file path."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        mock_modules["scitex.gen._start.clean_path"].return_value = "/absolute/path/test_out/RUNNING/TEST1234/"
        
        mock_filesystem.path.isabs.return_value = False
        
        # Execute
        result = start(file="./relative/test.py", verbose=False)
        
        # Verify
        assert result is not None
        mock_filesystem.path.abspath.assert_called()

    def test_start_with_sdir_suffix(self, mock_modules, mock_filesystem):
        """Test start function with sdir suffix."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        base_path = "/test/path/test_out/RUNNING/TEST1234/"
        mock_modules["scitex.gen._start.clean_path"].return_value = base_path
        
        # Execute
        result = start(sdir_suffix="experiment1", verbose=False)
        
        # Verify
        assert result is not None
        # Should modify sdir with suffix

    def test_start_with_clear_logs(self, mock_modules, mock_filesystem):
        """Test start function with log clearing enabled."""
        # Setup
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        
        with patch("scitex.gen._start._clear_python_log_dir") as mock_clear:
            # Execute
            result = start(clear_logs=True, verbose=False)
            
            # Verify
            assert result is not None
            mock_clear.assert_called_once()

    def test_start_comprehensive_matplotlib_params(self, mock_modules, mock_filesystem):
        """Test start function with comprehensive matplotlib parameters."""
        # Setup
        mock_plt = MagicMock()
        mock_modules["scitex.gen._start.gen_ID"].return_value = "TEST1234"
        mock_modules["scitex.gen._start.load_configs"].return_value = MagicMock()
        mock_modules["scitex.gen._start.load_configs"].return_value.to_dict.return_value = {"test": "config"}
        mock_modules["scitex.gen._start.configure_mpl"].return_value = (mock_plt, {"red": "#FF0000"})
        
        # Execute
        result = start(
            plt=mock_plt,
            fig_size_mm=(200, 150),
            fig_scale=1.5,
            dpi_display=120,
            dpi_save=400,
            fontsize="large",
            autolayout=False,
            hide_top_right_spines=False,
            alpha=0.8,
            line_width=1.0,
            verbose=False
        )
        
        # Verify
        assert result is not None
        mock_modules["scitex.gen._start.configure_mpl"].assert_called_with(
            mock_plt,
            fig_size_mm=(200, 150),
            fig_scale=1.5,
            dpi_display=120,
            dpi_save=400,
            hide_top_right_spines=False,
            alpha=0.8,
            line_width=1.0,
            fontsize="large",
            autolayout=False,
            verbose=False
        )


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])