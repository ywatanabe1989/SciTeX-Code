#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 18:14:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/ax/_style/test__format_label_comprehensive.py

"""Comprehensive tests for format_label functionality."""

import os
import pytest
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import tempfile
from scitex.plt.ax._style import format_label


class TestFormatLabelBasic:
    """Test basic format_label functionality."""
    
    def test_string_passthrough(self):
        """Test that strings are passed through unchanged (current implementation)."""
        test_cases = [
            "simple",
            "with_underscores",
            "WITH_CAPS",
            "MixedCase",
            "with spaces",
            "with-hyphens",
            "with.dots",
            "with123numbers"
        ]
        
        for test_string in test_cases:
            assert format_label(test_string) == test_string
    
    def test_non_string_types(self):
        """Test handling of non-string types."""
        # Numeric types
        assert format_label(123) == 123
        assert format_label(3.14) == 3.14
        assert format_label(0) == 0
        assert format_label(-5) == -5
        
        # Boolean
        assert format_label(True) is True
        assert format_label(False) is False
        
        # None
        assert format_label(None) is None
        
        # Complex types
        assert format_label([1, 2, 3]) == [1, 2, 3]
        assert format_label({"key": "value"}) == {"key": "value"}
        assert format_label((1, 2)) == (1, 2)
        assert format_label({1, 2, 3}) == {1, 2, 3}
    
    def test_empty_and_whitespace(self):
        """Test empty strings and whitespace."""
        assert format_label("") == ""
        assert format_label(" ") == " "
        assert format_label("   ") == "   "
        assert format_label("\t") == "\t"
        assert format_label("\n") == "\n"
        assert format_label("  text  ") == "  text  "


class TestFormatLabelSpecialCharacters:
    """Test handling of special characters."""
    
    def test_punctuation(self):
        """Test strings with punctuation."""
        punctuation_tests = [
            "test!",
            "test?",
            "test.",
            "test,test",
            "test;test",
            "test:test",
            "test'test",
            'test"test',
            "test-test",
            "test_test",
            "test/test",
            "test\\test",
            "test|test",
            "test@test",
            "test#test",
            "test$test",
            "test%test",
            "test^test",
            "test&test",
            "test*test",
            "test(test)",
            "test[test]",
            "test{test}",
            "test<test>",
            "test=test",
            "test+test",
            "test~test",
            "test`test"
        ]
        
        for test_string in test_string:
            assert format_label(test_string) == test_string
    
    def test_unicode_characters(self):
        """Test Unicode characters from various languages."""
        unicode_tests = [
            "测试",  # Chinese
            "テスト",  # Japanese
            "테스트",  # Korean
            "тест",  # Russian
            "δοκιμή",  # Greek
            "परीक्षण",  # Hindi
            "اختبار",  # Arabic
            "בדיקה",  # Hebrew
            "ทดสอบ",  # Thai
            "🔬🧪",  # Emojis
            "α_β_γ",  # Greek letters with underscores
            "Ω_resistance",  # Mixed
            "température_°C",  # Degree symbol
            "π≈3.14",  # Mathematical symbols
        ]
        
        for test_string in unicode_tests:
            assert format_label(test_string) == test_string
    
    def test_control_characters(self):
        """Test control characters."""
        control_tests = [
            "test\x00test",  # Null
            "test\x01test",  # Start of heading
            "test\x1btest",  # Escape
            "test\x7ftest",  # Delete
        ]
        
        for test_string in control_tests:
            assert format_label(test_string) == test_string


class TestFormatLabelEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_strings(self):
        """Test very long strings."""
        long_string = "a" * 10000
        assert format_label(long_string) == long_string
        
        long_underscore = "_" * 1000
        assert format_label(long_underscore) == long_underscore
        
        repeated_pattern = "test_label_" * 500
        assert format_label(repeated_pattern) == repeated_pattern
    
    def test_numeric_strings(self):
        """Test strings that look like numbers."""
        numeric_strings = [
            "123",
            "3.14",
            "-5",
            "1e10",
            "0x1234",
            "0b1010",
            "0o777",
            "inf",
            "nan",
            "1_000_000",  # Python numeric literal
        ]
        
        for test_string in numeric_strings:
            assert format_label(test_string) == test_string
    
    def test_special_python_strings(self):
        """Test special Python string formats."""
        special_strings = [
            "__init__",
            "__main__",
            "__file__",
            "_private",
            "__double_underscore__",
            "CamelCase",
            "camelCase",
            "snake_case",
            "SCREAMING_SNAKE_CASE",
            "kebab-case",
            "dot.case",
            "PascalCase",
            "mixed_Case_Style",
        ]
        
        for test_string in special_strings:
            assert format_label(test_string) == test_string
    
    def test_path_like_strings(self):
        """Test strings that look like file paths."""
        path_strings = [
            "/path/to/file",
            "C:\\Windows\\System32",
            "../relative/path",
            "./current/path",
            "~/home/user",
            "file.txt",
            "script.py",
            "data_2023_01_01.csv",
        ]
        
        for test_string in path_strings:
            assert format_label(test_string) == test_string


class TestFormatLabelIntegration:
    """Test integration with matplotlib."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_with_axis_labels(self):
        """Test format_label with matplotlib axis labels."""
        labels = [
            "x_axis_label",
            "y_axis_label",
            "Plot_Title",
            "Legend_Entry_1",
        ]
        
        for label in labels:
            formatted = format_label(label)
            
            # Test setting as xlabel
            self.ax.set_xlabel(formatted)
            assert self.ax.get_xlabel() == label
            
            # Test setting as ylabel
            self.ax.set_ylabel(formatted)
            assert self.ax.get_ylabel() == label
            
            # Test setting as title
            self.ax.set_title(formatted)
            assert self.ax.get_title() == label
    
    def test_with_legend_labels(self):
        """Test format_label with legend labels."""
        data_labels = ["data_set_1", "data_set_2", "control_group"]
        
        for i, label in enumerate(data_labels):
            self.ax.plot([0, 1], [i, i+1], label=format_label(label))
        
        legend = self.ax.legend()
        legend_texts = [t.get_text() for t in legend.get_texts()]
        
        assert legend_texts == data_labels
    
    def test_with_tick_labels(self):
        """Test format_label with tick labels."""
        tick_labels = ["category_a", "category_b", "category_c"]
        formatted_labels = [format_label(label) for label in tick_labels]
        
        self.ax.set_xticks(range(len(tick_labels)))
        self.ax.set_xticklabels(formatted_labels)
        
        actual_labels = [t.get_text() for t in self.ax.get_xticklabels()]
        assert actual_labels == tick_labels


class TestFormatLabelCommented:
    """Test the commented-out functionality for future reference."""
    
    def test_future_underscore_replacement(self):
        """Test what the behavior would be with underscore replacement."""
        # These tests document the expected behavior if the commented
        # functionality is enabled
        
        test_cases = [
            # (input, expected_output_if_enabled)
            ("test_label", "Test Label"),
            ("simple", "Simple"),
            ("UPPERCASE", "UPPERCASE"),  # All caps preserved
            ("multiple_word_label", "Multiple Word Label"),
            ("_leading_underscore", " Leading Underscore"),
            ("trailing_underscore_", "Trailing Underscore "),
            ("__double__underscore__", "  Double  Underscore  "),
            ("mixed_CASE_label", "Mixed Case Label"),
            ("", ""),
            ("_", " "),
            ("___", "   "),
        ]
        
        for input_str, expected_if_enabled in test_cases:
            # Current behavior: passthrough
            assert format_label(input_str) == input_str
            
            # Document what it would be if enabled
            # (This helps understand the intended functionality)
    
    def test_future_capitalization(self):
        """Test what the capitalization behavior would be."""
        test_cases = [
            ("lowercase", "Lowercase"),
            ("UPPERCASE", "UPPERCASE"),  # Preserved
            ("mixedCase", "Mixedcase"),  # Only first letter capitalized
            ("multiple words", "Multiple Words"),
            ("123numbers", "123numbers"),  # Numbers at start
            ("test123test", "Test123test"),
        ]
        
        for input_str, expected_if_enabled in test_cases:
            # Current behavior: passthrough
            assert format_label(input_str) == input_str


class TestFormatLabelPerformance:
    """Test performance aspects."""
    
    def test_many_calls(self):
        """Test performance with many calls."""
        # Should handle many calls efficiently
        for i in range(1000):
            result = format_label(f"test_label_{i}")
            assert result == f"test_label_{i}"
    
    def test_complex_strings(self):
        """Test with complex string patterns."""
        complex_patterns = [
            "a_very_long_label_with_many_underscores_and_words_that_keeps_going",
            "MixedCase_with_underscores_AND_CAPS_and_lowercase",
            "numbers_123_and_456_with_underscores",
            "special!@#$%^&*()_characters_mixed_with_underscores",
            "unicode_测试_テスト_테스트_mixed_with_english",
        ]
        
        for pattern in complex_patterns:
            assert format_label(pattern) == pattern


class TestFormatLabelTypeHints:
    """Test type handling and edge cases."""
    
    def test_custom_objects(self):
        """Test with custom objects."""
        class CustomLabel:
            def __init__(self, value):
                self.value = value
            
            def __str__(self):
                return f"CustomLabel({self.value})"
        
        custom = CustomLabel("test")
        assert format_label(custom) == custom
    
    def test_callable_objects(self):
        """Test with callable objects."""
        def label_function():
            return "function_label"
        
        assert format_label(label_function) == label_function
        
        lambda_func = lambda: "lambda_label"
        assert format_label(lambda_func) == lambda_func
    
    def test_numpy_types(self):
        """Test with numpy types if available."""
        try:
            import numpy as np
            
            # NumPy scalars
            assert format_label(np.int32(42)) == np.int32(42)
            assert format_label(np.float64(3.14)) == np.float64(3.14)
            
            # NumPy arrays
            arr = np.array([1, 2, 3])
            assert format_label(arr) is arr
            
            # NumPy strings
            np_str = np.str_("numpy_string")
            assert format_label(np_str) == np_str
        except ImportError:
            pytest.skip("NumPy not available")
    
    def test_pandas_types(self):
        """Test with pandas types if available."""
        try:
            import pandas as pd
            
            # Pandas strings
            pd_str = pd.Series(["test_label"])[0]
            assert format_label(pd_str) == pd_str
            
        except ImportError:
            pytest.skip("Pandas not available")


class TestFormatLabelSaveIntegration:
    """Test integration with figure saving."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.fig, self.ax = plt.subplots()
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_save_with_formatted_labels(self):
        """Test saving figures with formatted labels."""
        # Apply formatted labels
        self.ax.set_xlabel(format_label("x_axis_variable"))
        self.ax.set_ylabel(format_label("y_axis_variable"))
        self.ax.set_title(format_label("plot_title_with_underscores"))
        
        # Plot some data
        self.ax.plot([1, 2, 3], [1, 4, 9], label=format_label("data_series_1"))
        self.ax.legend()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            try:
                self.fig.savefig(f.name)
                assert os.path.exists(f.name)
                assert os.path.getsize(f.name) > 0
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)
    
    def test_batch_label_formatting(self):
        """Test formatting multiple labels in batch."""
        labels = [
            "series_1",
            "series_2", 
            "control_group",
            "experimental_group",
            "baseline_measurement"
        ]
        
        formatted_labels = [format_label(label) for label in labels]
        
        # All should be unchanged in current implementation
        assert formatted_labels == labels
        
        # Use in plot
        for i, label in enumerate(formatted_labels):
            self.ax.plot([0, 1], [i, i+1], label=label)
        
        self.ax.legend()
        legend = self.ax.get_legend()
        assert legend is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])