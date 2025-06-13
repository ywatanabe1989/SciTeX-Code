#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-30 10:50:00 (Claude)"
# File: /tests/scitex/gen/test__start_comprehensive.py

"""
Comprehensive tests for scitex.gen.start and related functions.
Tests actual functionality without excessive mocking.
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

import scitex
from scitex.gen import start, close
from scitex.dict import DotDict


class TestStartClose:
    """Comprehensive test cases for start/close workflow."""

    @pytest.fixture
    def temp_script(self):
        """Create a temporary script file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("#!/usr/bin/env python3\n# Test script")
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def clean_output_dirs(self):
        """Clean up any test output directories."""
        yield
        # Cleanup after test
        for pattern in ["*_out", "test_*_out", "RUNNING", "FINISHED*"]:
            for path in Path(".").glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)

    def test_start_returns_correct_tuple(self, clean_output_dirs):
        """Test that start() returns the expected tuple of objects."""
        # Act
        result = start(verbose=False)

        # Assert
        assert isinstance(result, tuple), "start() should return a tuple"
        assert len(result) == 5, "start() should return 5 elements"

        CONFIG, stdout, stderr, plt, CC = result

        # Check types
        assert isinstance(CONFIG, (dict, DotDict)), "CONFIG should be dict-like"
        # When sys is not provided, stdout/stderr will be None
        assert stdout is None or hasattr(
            stdout, "write"
        ), "stdout should be None or file-like"
        assert stderr is None or hasattr(
            stderr, "write"
        ), "stderr should be None or file-like"
        # plt and CC can be None if matplotlib not passed

    def test_start_creates_log_directory(self, temp_script, clean_output_dirs):
        """Test that start() creates the log directory structure."""
        # Act
        CONFIG, _, _, _, _ = start(file=temp_script, verbose=False)

        # Assert
        assert "SDIR" in CONFIG, "CONFIG should contain SDIR"
        assert os.path.exists(
            CONFIG["SDIR"]
        ), f"Directory {CONFIG['SDIR']} should exist"
        assert "RUNNING" in CONFIG["SDIR"], "Should create RUNNING directory"

    def test_start_with_sys_redirects_output(self, clean_output_dirs):
        """Test that start() with sys module redirects stdout/stderr."""
        import sys as sys_module

        # Save original streams
        orig_stdout = sys_module.stdout
        orig_stderr = sys_module.stderr

        try:
            # Act
            CONFIG, new_stdout, new_stderr, _, _ = start(sys=sys_module, verbose=False)

            # Assert
            assert sys_module.stdout != orig_stdout, "stdout should be redirected"
            assert sys_module.stderr != orig_stderr, "stderr should be redirected"
            assert hasattr(
                sys_module.stdout, "_log_file"
            ), "stdout should be Tee object"
            assert hasattr(
                sys_module.stderr, "_log_file"
            ), "stderr should be Tee object"

            # Test that output is captured
            print("Test output")
            sys_module.stderr.write("Test error\n")

        finally:
            # Restore original streams
            sys_module.stdout = orig_stdout
            sys_module.stderr = orig_stderr

    def test_start_close_workflow(self, clean_output_dirs):
        """Test complete start/close workflow."""
        import sys as sys_module

        # Act
        CONFIG, stdout, stderr, plt, CC = start(sys=sys_module, verbose=False)

        # Generate some output
        print("Test message")

        # Close
        close(CONFIG, verbose=False)

        # Assert - check that logs were saved
        log_dir = CONFIG["SDIR"].replace("RUNNING", "FINISHED")
        # The directory might have different suffixes (SUCCESS, ERROR, etc)
        finished_dirs = list(
            Path(CONFIG["SDIR"]).parent.parent.glob("FINISHED*/*/logs")
        )
        assert (
            len(finished_dirs) > 0
        ), "Should have created FINISHED directory with logs"

        # Check log files exist
        log_files = list(finished_dirs[0].glob("*.log"))
        assert len(log_files) >= 2, "Should have stdout.log and stderr.log"

    def test_start_with_custom_sdir(self, clean_output_dirs):
        """Test start() with custom save directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_sdir = os.path.join(tmpdir, "custom_output")

            # Act
            CONFIG, _, _, _, _ = start(sdir=custom_sdir, verbose=False)

            # Assert
            assert CONFIG["SDIR"] == custom_sdir, "Should use custom sdir"
            assert os.path.exists(custom_sdir), "Custom directory should be created"

    def test_start_generates_unique_id(self, clean_output_dirs):
        """Test that start() generates unique IDs for each run."""
        # Act
        CONFIG1, _, _, _, _ = start(verbose=False)
        CONFIG2, _, _, _, _ = start(verbose=False)

        # Assert
        assert "ID" in CONFIG1, "CONFIG should contain ID"
        assert "ID" in CONFIG2, "CONFIG should contain ID"
        assert CONFIG1["ID"] != CONFIG2["ID"], "Each run should have unique ID"
        # ID format is timestamp_randomstring, so it's longer than 4 chars
        assert len(CONFIG1["ID"]) > 4, "ID should include timestamp and random string"
        assert "_" in CONFIG1["ID"], "ID should have underscore separator"

    def test_start_sets_timestamps(self, clean_output_dirs):
        """Test that start() sets proper timestamps."""
        # Act
        CONFIG, _, _, _, _ = start(verbose=False)

        # Assert
        assert "START_TIME" in CONFIG, "CONFIG should contain START_TIME"
        assert CONFIG["START_TIME"] is not None, "START_TIME should be set"

    def test_start_matplotlib_configuration(self, clean_output_dirs):
        """Test matplotlib configuration when plt is provided."""
        import matplotlib.pyplot as plt

        # Act
        CONFIG, _, _, plt_result, CC = start(plt=plt, verbose=False, agg=True)

        # Assert
        assert plt_result is not None, "plt should be returned"
        assert CC is not None, "Color cycle should be returned"
        assert isinstance(CC, dict), "CC should be a dictionary"
        assert "blue" in CC, "CC should contain color definitions"

    def test_start_with_args(self, clean_output_dirs):
        """Test start() with command line arguments."""
        from argparse import Namespace

        args = Namespace(input_file="test.txt", output_dir="./output", verbose=True)

        # Act
        CONFIG, _, _, _, _ = start(args=args, verbose=False)

        # Assert
        assert "ARGS" in CONFIG, "CONFIG should contain ARGS"
        assert CONFIG["ARGS"]["input_file"] == "test.txt"
        assert CONFIG["ARGS"]["output_dir"] == "./output"

    def test_start_seed_setting(self, clean_output_dirs):
        """Test that start() sets random seeds properly."""
        import random
        import numpy as np

        # Act with specific seed
        start(random=random, np=np, seed=12345, verbose=False)

        # Generate random numbers
        rand1 = random.random()
        np_rand1 = np.random.random()

        # Reset with same seed
        start(random=random, np=np, seed=12345, verbose=False)

        # Generate again
        rand2 = random.random()
        np_rand2 = np.random.random()

        # Assert - same seed should produce same random numbers
        assert rand1 == rand2, "Random seed should be reproducible"
        assert np_rand1 == np_rand2, "NumPy seed should be reproducible"

    def test_close_saves_logs(self, clean_output_dirs):
        """Test that close() properly saves log files."""
        import sys as sys_module

        # Start
        CONFIG, _, _, _, _ = start(sys=sys_module, verbose=False)

        # Generate output
        print("Test stdout message")
        sys_module.stderr.write("Test stderr message\n")

        # Close
        close(CONFIG, verbose=False)

        # Find log files - use the ID from CONFIG to find the right directory
        finished_dir_pattern = f'**/FINISHED*/{CONFIG["ID"]}/logs'
        finished_dirs = list(Path(".").glob(finished_dir_pattern))
        assert (
            len(finished_dirs) == 1
        ), f"Should have created exactly one FINISHED directory for {CONFIG['ID']}"

        # Check stdout log
        stdout_logs = list(finished_dirs[0].glob("stdout.log"))
        assert len(stdout_logs) == 1, "Should have stdout.log"

        with open(stdout_logs[0], "r") as f:
            content = f.read()
            # The log contains header info too, just check our message is there
            assert (
                "test stdout message" in content.lower()
            ), f"stdout log should contain test message, but got: {content}"

    def test_close_with_exit_status(self, clean_output_dirs):
        """Test close() with different exit statuses."""
        import sys as sys_module

        # Test success
        CONFIG1, _, _, _, _ = start(sys=sys_module, verbose=False)
        close(CONFIG1, exit_status=0, verbose=False)
        assert any(
            Path(".").glob("**/FINISHED_SUCCESS/**")
        ), "Should create FINISHED_SUCCESS"

        # Test error
        CONFIG2, _, _, _, _ = start(sys=sys_module, verbose=False)
        close(CONFIG2, exit_status=1, verbose=False)
        assert any(
            Path(".").glob("**/FINISHED_ERROR/**")
        ), "Should create FINISHED_ERROR"

        # Test no status
        CONFIG3, _, _, _, _ = start(sys=sys_module, verbose=False)
        close(CONFIG3, exit_status=None, verbose=False)
        assert any(Path(".").glob("**/FINISHED/**")), "Should create FINISHED"


class TestUtilityFunctions:
    """Test utility functions in the gen module."""

    def test_title2path(self):
        """Test title2path conversion."""
        from scitex.gen import title2path

        # Test cases - based on actual implementation
        assert title2path("Hello World!") == "hello_world!"  # ! is not removed
        assert title2path("Test:File") == "testfile"  # : is removed
        assert title2path("Test[File]") == "testfile"  # [] are removed
        assert (
            title2path("Test  File") == "test_file"
        )  # Multiple spaces become single _
        assert title2path("CamelCase") == "camelcase"  # Lowercase conversion

    def test_gen_ID(self):
        """Test ID generation."""
        from scitex.reproduce import gen_ID

        # Test default format (timestamp + N random chars)
        id1 = gen_ID(N=4)
        assert "_" in id1, "ID should have underscore separator"
        parts = id1.split("_")
        assert len(parts) == 2, "ID should have timestamp and random parts"
        assert len(parts[1]) == 4, "Random part should be 4 characters"

        # Test custom length
        id2 = gen_ID(N=8)
        parts2 = id2.split("_")
        assert len(parts2[1]) == 8, "Custom length random part should match"

        # Test uniqueness
        ids = [gen_ID(N=4) for _ in range(10)]
        assert len(set(ids)) == len(ids), "IDs should be unique"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
