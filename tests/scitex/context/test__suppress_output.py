#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 16:30:00 (claude)"
# File: ./tests/scitex/context/test__suppress_output.py
# ----------------------------------------

"""
Comprehensive test suite for scitex.context._suppress_output module.

This module tests the suppress_output context manager for stdout/stderr suppression.

Test Structure:
- Basic output suppression functionality
- Conditional suppression behavior
- Error handling and edge cases
- Integration with different output types
- Alias testing (quiet)
"""

import pytest
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from src.scitex.context._suppress_output import suppress_output, quiet


class TestSuppressOutput:
    """Test cases for the suppress_output context manager."""
    
    def test_function_exists(self):
        """Test that the suppress_output function exists and is callable."""
        assert callable(suppress_output), "suppress_output should be callable"
        
    def test_suppress_stdout(self):
        """Test that stdout is suppressed when using the context manager."""
        # Capture stdout to verify suppression
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            # This should not appear in captured output
            with suppress_output():
                print("This should be suppressed")
                
            # This should appear in captured output
            print("This should be visible")
        
        output = captured_output.getvalue()
        assert "This should be suppressed" not in output
        assert "This should be visible" in output
        
    def test_suppress_stderr(self):
        """Test that stderr is suppressed when using the context manager."""
        # Capture stderr to verify suppression
        captured_error = StringIO()
        
        with redirect_stderr(captured_error):
            # This should not appear in captured error
            with suppress_output():
                print("This should be suppressed to stderr", file=sys.stderr)
                
            # This should appear in captured error
            print("This should be visible to stderr", file=sys.stderr)
        
        error_output = captured_error.getvalue()
        assert "This should be suppressed to stderr" not in error_output
        assert "This should be visible to stderr" in error_output
        
    def test_suppress_both_stdout_stderr(self):
        """Test that both stdout and stderr are suppressed simultaneously."""
        captured_output = StringIO()
        captured_error = StringIO()
        
        with redirect_stdout(captured_output), redirect_stderr(captured_error):
            with suppress_output():
                print("Suppressed stdout")
                print("Suppressed stderr", file=sys.stderr)
                
            print("Visible stdout")
            print("Visible stderr", file=sys.stderr)
        
        output = captured_output.getvalue()
        error_output = captured_error.getvalue()
        
        assert "Suppressed stdout" not in output
        assert "Suppressed stderr" not in error_output
        assert "Visible stdout" in output
        assert "Visible stderr" in error_output
        
    def test_suppress_false(self):
        """Test that output is NOT suppressed when suppress=False."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with suppress_output(suppress=False):
                print("This should be visible")
        
        output = captured_output.getvalue()
        assert "This should be visible" in output
        
    def test_suppress_true_explicit(self):
        """Test explicit suppress=True parameter."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with suppress_output(suppress=True):
                print("This should be suppressed")
                
            print("This should be visible")
        
        output = captured_output.getvalue()
        assert "This should be suppressed" not in output
        assert "This should be visible" in output
        
    def test_nested_suppress_contexts(self):
        """Test nested suppress_output contexts."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            print("Before outer context")
            
            with suppress_output():
                print("Outer suppressed")
                
                with suppress_output():
                    print("Inner suppressed")
                    
                print("Outer suppressed again")
                
            print("After outer context")
        
        output = captured_output.getvalue()
        assert "Before outer context" in output
        assert "Outer suppressed" not in output
        assert "Inner suppressed" not in output
        assert "Outer suppressed again" not in output
        assert "After outer context" in output
        
    def test_mixed_nested_contexts(self):
        """Test nested contexts with mixed suppress settings."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with suppress_output(suppress=False):
                print("Outer not suppressed")
                
                with suppress_output(suppress=True):
                    print("Inner suppressed")
                    
                print("Outer not suppressed again")
        
        output = captured_output.getvalue()
        assert "Outer not suppressed" in output
        assert "Inner suppressed" not in output
        assert "Outer not suppressed again" in output
        
    def test_exception_handling(self):
        """Test that exceptions are properly handled within suppressed context."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with pytest.raises(ValueError):
                with suppress_output():
                    print("This should be suppressed")
                    raise ValueError("Test exception")
        
        output = captured_output.getvalue()
        assert "This should be suppressed" not in output
        
    def test_return_values_preserved(self):
        """Test that return values from functions work within suppressed context."""
        def test_function():
            print("This should be suppressed")
            return "test_value"
        
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with suppress_output():
                result = test_function()
        
        output = captured_output.getvalue()
        assert "This should be suppressed" not in output
        assert result == "test_value"
        
    def test_quiet_alias(self):
        """Test that 'quiet' is an alias for suppress_output."""
        assert quiet is suppress_output
        
        # Test that it works the same way
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with quiet():
                print("This should be suppressed by quiet")
                
            print("This should be visible")
        
        output = captured_output.getvalue()
        assert "This should be suppressed by quiet" not in output
        assert "This should be visible" in output
        
    def test_context_manager_protocol(self):
        """Test that suppress_output properly implements context manager protocol."""
        # Test __enter__ and __exit__ methods exist
        context_manager = suppress_output()
        assert hasattr(context_manager, '__enter__')
        assert hasattr(context_manager, '__exit__')
        
        # Test manual context manager usage
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            cm = suppress_output()
            cm.__enter__()
            try:
                print("Manually suppressed")
            finally:
                cm.__exit__(None, None, None)
                
            print("After manual context")
        
        output = captured_output.getvalue()
        assert "Manually suppressed" not in output
        assert "After manual context" in output
        
    def test_large_output_suppression(self):
        """Test suppression with large amounts of output."""
        captured_output = StringIO()
        
        with redirect_stdout(captured_output):
            with suppress_output():
                # Generate large output
                for i in range(1000):
                    print(f"Line {i} should be suppressed")
                    
            print("Final visible line")
        
        output = captured_output.getvalue()
        assert "Line 0 should be suppressed" not in output
        assert "Line 999 should be suppressed" not in output
        assert "Final visible line" in output
        
    def test_output_types(self):
        """Test suppression with different types of output."""
        captured_output = StringIO()
        captured_error = StringIO()
        
        with redirect_stdout(captured_output), redirect_stderr(captured_error):
            with suppress_output():
                # Different print operations
                print("Simple string")
                print(42)
                print([1, 2, 3])
                print({"key": "value"})
                
                # stderr output
                print("Error message", file=sys.stderr)
                
                # sys.stdout.write
                sys.stdout.write("Direct stdout write\n")
                sys.stderr.write("Direct stderr write\n")
        
        output = captured_output.getvalue()
        error_output = captured_error.getvalue()
        
        # All should be suppressed
        assert len(output) == 0
        assert len(error_output) == 0

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/context/_suppress_output.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 09:11:04 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/context/_suppress_output.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/context/_suppress_output.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# from contextlib import contextmanager, redirect_stderr, redirect_stdout
# 
# 
# @contextmanager
# def suppress_output(suppress=True):
#     """
#     A context manager that suppresses stdout and stderr.
# 
#     Example:
#         with suppress_output():
#             print("This will not be printed to the console.")
#     """
#     if suppress:
#         # Open a file descriptor that points to os.devnull (a black hole for data)
#         with open(os.devnull, "w") as fnull:
#             # Temporarily redirect stdout and stderr to the file descriptor fnull
#             with redirect_stdout(fnull), redirect_stderr(fnull):
#                 # Yield control back to the context block
#                 yield
#     else:
#         # If suppress is False, just yield without redirecting output
#         yield
# 
# 
# quiet = suppress_output
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/context/_suppress_output.py
# --------------------------------------------------------------------------------
