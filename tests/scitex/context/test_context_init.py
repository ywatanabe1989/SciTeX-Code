#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/context/test___init__.py

"""Tests for context module initialization and suppress_output functionality."""

import pytest
import sys
import io
from unittest.mock import patch, mock_open
from contextlib import redirect_stdout, redirect_stderr


class TestContextInit:
    """Test cases for scitex.context.__init__.py module."""

    def test_context_module_imports(self):
        """Test that context module imports successfully."""
        import scitex.context
        assert hasattr(scitex.context, 'suppress_output')

    def test_suppress_output_import(self):
        """Test that suppress_output can be imported from context module."""
        from scitex.context import suppress_output
        assert callable(suppress_output)

    def test_suppress_output_basic_functionality(self):
        """Test basic suppress_output functionality."""
        from scitex.context import suppress_output
        
        # Capture stdout to verify suppression
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # This should print normally
            print("Before suppression")
            
            # This should be suppressed
            with suppress_output():
                print("This should be suppressed")
            
            # This should print normally again
            print("After suppression")
        
        output = captured_output.getvalue()
        assert "Before suppression" in output
        assert "After suppression" in output
        assert "This should be suppressed" not in output

    def test_suppress_output_stderr_suppression(self):
        """Test that suppress_output suppresses stderr as well."""
        from scitex.context import suppress_output
        
        # Capture stderr to verify suppression
        captured_error = io.StringIO()
        with redirect_stderr(captured_error):
            # This should print normally to stderr
            print("Before error suppression", file=sys.stderr)
            
            # This should be suppressed
            with suppress_output():
                print("This error should be suppressed", file=sys.stderr)
            
            # This should print normally again
            print("After error suppression", file=sys.stderr)
        
        error_output = captured_error.getvalue()
        assert "Before error suppression" in error_output
        assert "After error suppression" in error_output
        assert "This error should be suppressed" not in error_output

    def test_suppress_output_with_suppress_false(self):
        """Test suppress_output when suppress=False."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # This should not be suppressed when suppress=False
            with suppress_output(suppress=False):
                print("This should NOT be suppressed")
        
        output = captured_output.getvalue()
        assert "This should NOT be suppressed" in output

    def test_suppress_output_with_suppress_true(self):
        """Test suppress_output when suppress=True explicitly."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # This should be suppressed when suppress=True
            with suppress_output(suppress=True):
                print("This should be suppressed")
        
        output = captured_output.getvalue()
        assert "This should be suppressed" not in output

    def test_suppress_output_nested_context(self):
        """Test nested suppress_output contexts."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            print("Outside")
            
            with suppress_output():
                print("Outer suppressed")
                
                with suppress_output(suppress=False):
                    print("Inner not suppressed")
                
                print("Outer suppressed again")
            
            print("Outside again")
        
        output = captured_output.getvalue()
        assert "Outside" in output
        assert "Outside again" in output
        assert "Inner not suppressed" in output
        assert "Outer suppressed" not in output
        assert "Outer suppressed again" not in output

    def test_suppress_output_with_exception(self):
        """Test suppress_output behavior when exception is raised inside context."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            print("Before exception")
            
            try:
                with suppress_output():
                    print("This should be suppressed")
                    raise ValueError("Test exception")
            except ValueError as e:
                assert str(e) == "Test exception"
            
            print("After exception")
        
        output = captured_output.getvalue()
        assert "Before exception" in output
        assert "After exception" in output
        assert "This should be suppressed" not in output

    def test_suppress_output_return_value(self):
        """Test that suppress_output context manager handles return values correctly."""
        from scitex.context import suppress_output
        
        def function_with_output():
            print("Function output")
            return "function result"
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # Function should still return value even when output is suppressed
            with suppress_output():
                result = function_with_output()
        
        assert result == "function result"
        output = captured_output.getvalue()
        assert "Function output" not in output

    def test_suppress_output_multiple_prints(self):
        """Test suppress_output with multiple print statements."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with suppress_output():
                print("Line 1")
                print("Line 2")
                print("Line 3")
                print("Line 4", end="")  # No newline
                print(" continues")
        
        output = captured_output.getvalue()
        assert output == ""  # All should be suppressed

    def test_suppress_output_with_flush(self):
        """Test suppress_output with explicit flush calls."""
        from scitex.context import suppress_output
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with suppress_output():
                print("This should be suppressed")
                sys.stdout.flush()  # Should not cause issues
                print("This too should be suppressed")
        
        output = captured_output.getvalue()
        assert output == ""

    def test_suppress_output_context_manager_protocol(self):
        """Test that suppress_output follows context manager protocol correctly."""
        from scitex.context import suppress_output
        
        # Test that it has __enter__ and __exit__ methods
        context_manager = suppress_output()
        assert hasattr(context_manager, '__enter__')
        assert hasattr(context_manager, '__exit__')
        assert callable(context_manager.__enter__)
        assert callable(context_manager.__exit__)

    def test_quiet_alias(self):
        """Test that quiet is an alias for suppress_output."""
        from scitex.context import quiet, suppress_output
        
        # Should be the same function
        assert quiet is suppress_output

    def test_suppress_output_import_via_quiet(self):
        """Test that quiet can be used as an alias."""
        from scitex.context import quiet
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with quiet():
                print("This should be suppressed via quiet")
        
        output = captured_output.getvalue()
        assert "This should be suppressed via quiet" not in output

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_suppress_output_file_error_handling(self, mock_open):
        """Test suppress_output when os.devnull cannot be opened."""
        from scitex.context import suppress_output
        
        # Should raise OSError when unable to open devnull
        with pytest.raises(OSError):
            with suppress_output():
                print("This won't be reached")

    def test_suppress_output_with_subprocess_like_output(self):
        """Test suppress_output with output that simulates subprocess behavior."""
        from scitex.context import suppress_output
        import subprocess
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            with suppress_output():
                # Simulate subprocess-like output
                for i in range(3):
                    print(f"Processing item {i}")
                    sys.stdout.flush()
        
        output = captured_output.getvalue()
        assert output == ""

    def test_suppress_output_original_streams_restored(self):
        """Test that original stdout/stderr are restored after context."""
        from scitex.context import suppress_output
        
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        with suppress_output():
            # Streams should be redirected inside context
            assert sys.stdout is not original_stdout
            assert sys.stderr is not original_stderr
        
        # Streams should be restored after context
        assert sys.stdout is original_stdout
        assert sys.stderr is original_stderr

    def test_suppress_output_both_stdout_and_stderr(self):
        """Test that both stdout and stderr are suppressed simultaneously."""
        from scitex.context import suppress_output
        
        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()
        
        with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
            with suppress_output():
                print("stdout message")
                print("stderr message", file=sys.stderr)
        
        stdout_output = captured_stdout.getvalue()
        stderr_output = captured_stderr.getvalue()
        
        assert "stdout message" not in stdout_output
        assert "stderr message" not in stderr_output

    def test_module_structure_integrity(self):
        """Test that context module has expected structure."""
        import scitex.context
        
        # Check module name
        assert scitex.context.__name__ == 'scitex.context'
        
        # Check that suppress_output is available
        assert hasattr(scitex.context, 'suppress_output')
        
        # Verify it's the same function as imported directly
        from scitex.context import suppress_output as direct_import
        assert scitex.context.suppress_output is direct_import

    def test_suppress_output_docstring_and_attributes(self):
        """Test that suppress_output has proper documentation."""
        from scitex.context import suppress_output
        
        # Should have docstring
        assert suppress_output.__doc__ is not None
        assert "context manager" in suppress_output.__doc__.lower()
        assert "suppress" in suppress_output.__doc__.lower()

    def test_context_module_constants(self):
        """Test that context module defines expected constants."""
        import scitex.context
        
        # Should have file path constants (if they exist)
        # These might not be exposed at module level, so we test what's available
        assert hasattr(scitex.context, 'suppress_output')


if __name__ == "__main__":
    pytest.main([__file__])
