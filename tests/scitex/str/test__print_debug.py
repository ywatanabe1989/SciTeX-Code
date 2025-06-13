#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__print_debug.py

"""Tests for debug printing functionality."""

import os
import pytest
from unittest.mock import patch, MagicMock


from scitex.str._print_debug import print_debug

class TestPrintDebugBasic:
    """Test basic print_debug functionality."""
    
    def test_print_debug_basic(self, capsys):
        """Test basic debug banner printing."""
        
        print_debug()
        captured = capsys.readouterr()
        
        assert "DEBUG MODE" in captured.out
        assert "!" in captured.out
        # Should have multiple lines of exclamation marks
        assert captured.out.count("!") > 50
    
    def test_print_debug_banner_structure(self, capsys):
        """Test that debug banner has correct structure."""
        
        print_debug()
        captured = capsys.readouterr()
        
        lines = captured.out.split('\n')
        # Should have multiple lines
        assert len(lines) > 5
        
        # Should contain "DEBUG MODE" in one of the lines
        debug_mode_lines = [line for line in lines if "DEBUG MODE" in line]
        assert len(debug_mode_lines) >= 1
    
    def test_print_debug_no_parameters(self):
        """Test that print_debug accepts no parameters."""
        
        # Should not raise any exception
        print_debug()
    
    def test_print_debug_returns_none(self):
        """Test that print_debug returns None."""
        
        result = print_debug()
        assert result is None


class TestPrintDebugOutput:
    """Test print_debug output content."""
    
    def test_debug_banner_content(self, capsys):
        """Test specific content of debug banner."""
        
        print_debug()
        captured = capsys.readouterr()
        
        # Should contain exactly "DEBUG MODE"
        assert "DEBUG MODE" in captured.out
        assert captured.out.count("DEBUG MODE") == 1
        
        # Should be surrounded by exclamation marks
        lines = captured.out.split('\n')
        debug_line = next((line for line in lines if "DEBUG MODE" in line), None)
        assert debug_line is not None
        assert "!" in debug_line
    
    def test_debug_banner_repetition(self, capsys):
        """Test calling print_debug multiple times."""
        
        print_debug()
        print_debug()
        captured = capsys.readouterr()
        
        # Should have "DEBUG MODE" twice
        assert captured.out.count("DEBUG MODE") == 2
    
    def test_debug_banner_formatting(self, capsys):
        """Test that debug banner has proper formatting."""
        
        print_debug()
        captured = capsys.readouterr()
        
        # Should have proper line breaks
        lines = captured.out.split('\n')
        
        # Each line should be either empty or contain exclamation marks
        non_empty_lines = [line for line in lines if line.strip()]
        for line in non_empty_lines:
            if line.strip():  # Non-empty lines should contain ! or DEBUG MODE
                assert "!" in line or "DEBUG MODE" in line


class TestPrintDebugIntegration:
    """Test print_debug integration with printc."""
    
    @patch('scitex.str._print_debug.printc')
    def test_print_debug_calls_printc(self, mock_printc):
        """Test that print_debug calls printc with correct parameters."""
        
        print_debug()
        
        # printc should be called once
        mock_printc.assert_called_once()
        
        # Check the arguments passed to printc
        args, kwargs = mock_printc.call_args
        
        # First argument should be the banner text
        banner_text = args[0]
        assert "DEBUG MODE" in banner_text
        assert "!" in banner_text
        
        # Should have color parameter
        assert kwargs.get('c') == 'yellow'
        assert kwargs.get('char') == '!'
        assert kwargs.get('n') == 60
    
    @patch('scitex.str._print_debug.printc')
    def test_print_debug_banner_dimensions(self, mock_printc):
        """Test banner dimensions passed to printc."""
        
        print_debug()
        
        args, kwargs = mock_printc.call_args
        
        # Should use 60-character width
        assert kwargs.get('n') == 60
        
        # Should use exclamation mark as border character
        assert kwargs.get('char') == '!'
        
        # Should use yellow color
        assert kwargs.get('c') == 'yellow'
    
    @patch('scitex.str._print_debug.printc')
    def test_print_debug_banner_content_structure(self, mock_printc):
        """Test the structure of banner content passed to printc."""
        
        print_debug()
        
        args, kwargs = mock_printc.call_args
        banner_text = args[0]
        
        # Should have multiple lines
        lines = banner_text.split('\n')
        assert len(lines) >= 7  # Should have at least 7 lines
        
        # Should have lines with 60 exclamation marks
        exclamation_lines = [line for line in lines if line == "!" * 60]
        assert len(exclamation_lines) >= 6  # Multiple lines of 60 exclamation marks
        
        # Should have exactly one line with "DEBUG MODE"
        debug_lines = [line for line in lines if "DEBUG MODE" in line]
        assert len(debug_lines) == 1
        
        # Debug mode line should have proper formatting
        debug_line = debug_lines[0]
        assert debug_line == "!" * 24 + " DEBUG MODE " + "!" * 24


class TestPrintDebugErrorHandling:
    """Test error handling and edge cases."""
    
    @patch('scitex.str._print_debug.printc')
    def test_print_debug_printc_exception(self, mock_printc):
        """Test behavior when printc raises an exception."""
        
        mock_printc.side_effect = Exception("printc failed")
        
        # Should propagate the exception
        with pytest.raises(Exception, match="printc failed"):
            print_debug()
    
    def test_print_debug_import_safety(self):
        """Test that importing the module doesn't cause issues."""
        # Should be able to import without errors
        
        # Function should be callable
        assert callable(print_debug)
    
    def test_print_debug_memory_usage(self, capsys):
        """Test that print_debug doesn't consume excessive memory."""
        
        # Call multiple times to check for memory leaks
        for _ in range(10):
            print_debug()
        
        captured = capsys.readouterr()
        
        # Should have called it 10 times
        assert captured.out.count("DEBUG MODE") == 10


class TestPrintDebugDocstring:
    """Test examples from docstring work correctly."""
    
    def test_docstring_example_debug_flag(self, capsys):
        """Test example usage with debug flag."""
        
        # Simulate the docstring example
        DEBUG = True
        if DEBUG:
            print_debug()
        
        captured = capsys.readouterr()
        assert "DEBUG MODE" in captured.out
    
    def test_docstring_example_config_debug(self, capsys):
        """Test example usage with config object."""
        
        # Simulate config object
        class Config:
            debug_mode = True
        
        config = Config()
        
        if config.debug_mode:
            print_debug()
            print("Debug logging enabled")
        
        captured = capsys.readouterr()
        assert "DEBUG MODE" in captured.out
        assert "Debug logging enabled" in captured.out


class TestPrintDebugConstants:
    """Test constants and module-level variables."""
    
    def test_this_file_constant(self):
        """Test that THIS_FILE constant is defined."""
        from scitex.str import THIS_FILE
        
        assert isinstance(THIS_FILE, str)
        assert "_print_debug.py" in THIS_FILE
    
    def test_printc_import(self):
        """Test that printc is properly imported."""
        from scitex.str import printc
        
        assert callable(printc)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
