#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:55:33 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__src.py

"""Test suite for scitex.gen._src module."""

import pytest
from unittest.mock import patch, MagicMock, call
import subprocess
import inspect
from scitex.gen import src


# Test fixtures
def test_function():
    """A test function for source code retrieval."""
    return 42


class TestClass:
    """A test class for source code retrieval."""

    def method(self):
        """A test method."""
        return "test"


class TestSrc:
    """Test cases for the src function."""

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_function(self, mock_getsource, mock_popen):
        """Test src with a regular function."""
        # Setup
        expected_source = "def test_function():\n    return 42\n"
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(test_function)

        # Verify
        mock_getsource.assert_called_once_with(test_function)
        mock_popen.assert_called_once_with(
            ["less"], stdin=subprocess.PIPE, encoding="utf8"
        )
        mock_process.communicate.assert_called_once_with(input=expected_source)

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_class(self, mock_getsource, mock_popen):
        """Test src with a class."""
        # Setup
        expected_source = (
            'class TestClass:\n    def method(self):\n        return "test"\n'
        )
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(TestClass)

        # Verify
        mock_getsource.assert_called_once_with(TestClass)
        mock_process.communicate.assert_called_once_with(input=expected_source)

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_instance(self, mock_getsource, mock_popen):
        """Test src with a class instance."""
        # Setup
        instance = TestClass()
        expected_source = (
            'class TestClass:\n    def method(self):\n        return "test"\n'
        )
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(instance)

        # Verify - should get source of the class, not instance
        mock_getsource.assert_called_once_with(TestClass)
        mock_process.communicate.assert_called_once_with(input=expected_source)

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_method(self, mock_getsource, mock_popen):
        """Test src with a method."""
        # Setup
        method = TestClass.method
        expected_source = '    def method(self):\n        return "test"\n'
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(method)

        # Verify
        mock_getsource.assert_called_once_with(method)
        mock_process.communicate.assert_called_once_with(input=expected_source)

    @patch("builtins.print")
    @patch("inspect.getsource")
    def test_src_with_builtin_function(self, mock_getsource, mock_print):
        """Test src with a built-in function."""
        # Setup - getsource raises OSError for built-in functions
        mock_getsource.side_effect = OSError("could not get source code")

        # Test with built-in function
        src(print)

        # Verify error message was printed
        mock_print.assert_called()
        error_msg = mock_print.call_args[0][0]
        assert "Cannot retrieve source code:" in error_msg

    @patch("builtins.print")
    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_process_error(self, mock_getsource, mock_popen, mock_print):
        """Test src when less process returns non-zero exit code."""
        # Setup
        mock_getsource.return_value = "def test():\n    pass\n"

        mock_process = MagicMock()
        mock_process.returncode = 1  # Non-zero exit code
        mock_popen.return_value = mock_process

        # Test
        src(test_function)

        # Verify error message was printed
        mock_print.assert_called_with("Process exited with return code 1")

    @patch("builtins.print")
    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_subprocess_error(self, mock_getsource, mock_popen, mock_print):
        """Test src when subprocess.Popen raises an error."""
        # Setup
        mock_getsource.return_value = "def test():\n    pass\n"
        mock_popen.side_effect = OSError("less command not found")

        # Test
        src(test_function)

        # Verify error was caught and printed
        mock_print.assert_called()
        error_msg = mock_print.call_args[0][0]
        assert "Cannot retrieve source code:" in error_msg


class TestSrcEdgeCases:
    """Test edge cases for the src function."""

    @patch("builtins.print")
    @patch("inspect.getsource")
    def test_src_with_type_error(self, mock_getsource, mock_print):
        """Test src when inspect.getsource raises TypeError."""
        # Setup
        mock_getsource.side_effect = TypeError(
            "Object is not a module, class, method, function, etc."
        )

        # Test with an object that causes TypeError
        src(test_function)

        # Verify error was caught and printed
        mock_print.assert_called()
        error_msg = mock_print.call_args[0][0]
        assert "TypeError:" in error_msg

    @patch("builtins.print")
    @patch("inspect.getsource")
    def test_src_with_unexpected_error(self, mock_getsource, mock_print):
        """Test src with unexpected error."""
        # Setup
        mock_getsource.side_effect = RuntimeError("Unexpected error")

        # Test
        src(test_function)

        # Verify generic error was caught and printed
        mock_print.assert_called()
        error_msg = mock_print.call_args[0][0]
        assert "Error:" in error_msg

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_lambda(self, mock_getsource, mock_popen):
        """Test src with a lambda function."""
        # Setup
        test_lambda = lambda x: x * 2
        expected_source = "test_lambda = lambda x: x * 2\n"
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(test_lambda)

        # Verify
        mock_getsource.assert_called_once()
        mock_process.communicate.assert_called_once_with(input=expected_source)

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_with_nested_class(self, mock_getsource, mock_popen):
        """Test src with a nested class."""

        class OuterClass:
            class InnerClass:
                def inner_method(self):
                    return "inner"

        # Setup
        expected_source = '    class InnerClass:\n        def inner_method(self):\n            return "inner"\n'
        mock_getsource.return_value = expected_source

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(OuterClass.InnerClass)

        # Verify
        mock_getsource.assert_called_once_with(OuterClass.InnerClass)


class TestSrcIntegration:
    """Integration tests for src function."""

    @patch("subprocess.Popen")
    def test_src_with_actual_source_retrieval(self, mock_popen):
        """Test src with actual source code retrieval."""
        # Setup mock process
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Define a function with known source
        def sample_function(x, y):
            """Sample function for testing."""
            return x + y

        # Test
        src(sample_function)

        # Verify the actual source was passed to less
        mock_popen.assert_called_once()
        mock_process.communicate.assert_called_once()

        # The source should contain the function definition
        passed_source = mock_process.communicate.call_args[1]["input"]
        assert "def sample_function" in passed_source
        assert "return x + y" in passed_source

    @patch("subprocess.Popen")
    @patch("inspect.getsource")
    def test_src_preserves_formatting(self, mock_getsource, mock_popen):
        """Test that src preserves source code formatting."""
        # Setup with specific formatting
        source_with_formatting = '''def formatted_function():
    """Docstring."""
    # Comment
    if True:
        return 42
    else:
        return 0
'''
        mock_getsource.return_value = source_with_formatting

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Test
        src(test_function)

        # Verify formatting is preserved
        passed_source = mock_process.communicate.call_args[1]["input"]
        assert passed_source == source_with_formatting


def test_main():
    """Main function for running tests."""
    pytest.main([__file__, "-xvs"])

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_src.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-06-13 22:44:28 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_src.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/gen/_src.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# #!./env/bin/python3
# 
# import inspect
# import subprocess
# 
# 
# def src(obj):
#     """
#     Returns the source code of a given object using `less`.
#     Handles functions, classes, class instances, methods, and built-in functions.
#     """
#     # If obj is an instance of a class, get the class of the instance.
#     if (
#         not inspect.isclass(obj)
#         and not inspect.isfunction(obj)
#         and not inspect.ismethod(obj)
#     ):
#         obj = obj.__class__
# 
#     try:
#         # Attempt to retrieve the source code
#         source_code = inspect.getsource(obj)
# 
#         # Assuming scitex.gen.less is a placeholder for displaying text with `less`
#         # This part of the code is commented out as it seems to be a placeholder
#         # scitex.gen.less(source_code)
# 
#         # Open a subprocess to use `less` for displaying the source code
#         process = subprocess.Popen(
#             ["less"], stdin=subprocess.PIPE, encoding="utf8"
#         )
#         process.communicate(input=source_code)
#         if process.returncode != 0:
#             print(f"Process exited with return code {process.returncode}")
#     except OSError as e:
#         # Handle cases where the source code cannot be retrieved (e.g., built-in functions)
#         print(f"Cannot retrieve source code: {e}")
#     except TypeError as e:
#         # Handle cases where the object type is not supported
#         print(f"TypeError: {e}")
#     except Exception as e:
#         # Handle any other unexpected errors
#         print(f"Error: {e}")
# 
# 
# # def src(obj):
# #     """
# #     Returns the source code of a given object using `less`.
# #     Handles functions, classes, class instances, and methods.
# #     """
# #     # If obj is an instance of a class, get the class of the instance.
# #     if (
# #         not inspect.isclass(obj)
# #         and not inspect.isfunction(obj)
# #         and not inspect.ismethod(obj)
# #     ):
# #         obj = obj.__class__
# 
# #     try:
# #         # Attempt to retrieve the source code
# #         source_code = inspect.getsource(obj)
# #         scitex.gen.less(source_code)
# 
# #         # # Open a subprocess to use `less` for displaying the source code
# #         # process = subprocess.Popen(
# #         #     ["less"], stdin=subprocess.PIPE, encoding="utf8"
# #         # )
# #         # process.communicate(input=source_code)
# #         if process.returncode != 0:
# #             print(f"Process exited with return code {process.returncode}")
# #     except TypeError as e:
# #         # Handle cases where the object type is not supported
# #         print(f"TypeError: {e}")
# #     except Exception as e:
# #         # Handle any other unexpected errors
# #         print(f"Error: {e}")
# 
# # (YOUR AWESOME CODE)
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys, plt, verbose=False
#     )
#     import sys
# 
#     # (YOUR AWESOME CODE)
#     # Close
#     scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# """
# /ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/gen/_def.py
# """
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_src.py
# --------------------------------------------------------------------------------
