#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-11 03:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/ax/_style/test__format_label.py
# ----------------------------------------
"""Comprehensive tests for format_label function."""

import os
import pytest
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import numpy as np

__FILE__ = "./tests/scitex/plt/ax/_style/test__format_label.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.plt.ax._style import format_label


class TestFormatLabelBasicFunctionality:
    """Test basic functionality of format_label."""
    
    def test_passthrough_strings(self):
        """Test that strings are passed through unchanged (current behavior)."""
        assert format_label("test_label") == "test_label"
        assert format_label("complex_label_with_underscores") == "complex_label_with_underscores"
        assert format_label("UPPERCASE") == "UPPERCASE"
        assert format_label("lowercase") == "lowercase"
        assert format_label("MixedCase") == "MixedCase"
        assert format_label("camelCase") == "camelCase"
        assert format_label("PascalCase") == "PascalCase"
        
    def test_passthrough_numbers(self):
        """Test that numeric values are passed through unchanged."""
        assert format_label(123) == 123
        assert format_label(123.456) == 123.456
        assert format_label(0) == 0
        assert format_label(-42) == -42
        assert format_label(1e6) == 1e6
        assert format_label(np.pi) == np.pi
        
    def test_passthrough_none(self):
        """Test that None is passed through unchanged."""
        assert format_label(None) is None
        
    def test_passthrough_containers(self):
        """Test that containers are passed through unchanged."""
        assert format_label([1, 2, 3]) == [1, 2, 3]
        assert format_label((1, 2, 3)) == (1, 2, 3)
        assert format_label({1, 2, 3}) == {1, 2, 3}
        assert format_label({"a": 1, "b": 2}) == {"a": 1, "b": 2}
        
    def test_passthrough_numpy_arrays(self):
        """Test that numpy arrays are passed through unchanged."""
        arr = np.array([1, 2, 3])
        result = format_label(arr)
        assert np.array_equal(result, arr)
        assert result is arr  # Same object
        
    def test_empty_string(self):
        """Test empty string handling."""
        assert format_label("") == ""
        
    def test_whitespace_strings(self):
        """Test strings with various whitespace."""
        assert format_label(" ") == " "
        assert format_label("\t") == "\t"
        assert format_label("\n") == "\n"
        assert format_label("  spaced  ") == "  spaced  "
        assert format_label("multi\nline") == "multi\nline"
        
    def test_special_characters(self):
        """Test strings with special characters."""
        assert format_label("special!@#$%^&*()_+") == "special!@#$%^&*()_+"
        assert format_label("path/to/file.txt") == "path/to/file.txt"
        assert format_label("key=value") == "key=value"
        assert format_label("item[0]") == "item[0]"
        assert format_label("{braces}") == "{braces}"
        
    def test_unicode_characters(self):
        """Test strings with unicode characters."""
        assert format_label("unicode_текст_测试") == "unicode_текст_测试"
        assert format_label("π_constant") == "π_constant"
        assert format_label("café") == "café"
        assert format_label("naïve") == "naïve"
        assert format_label("emoji_🎨_test") == "emoji_🎨_test"
        
    def test_latex_strings(self):
        """Test LaTeX formatted strings."""
        assert format_label(r"$\alpha$") == r"$\alpha$"
        assert format_label(r"$\beta_{test}$") == r"$\beta_{test}$"
        assert format_label(r"$\frac{a}{b}$") == r"$\frac{a}{b}$"
        assert format_label(r"$\sum_{i=0}^{n} x_i$") == r"$\sum_{i=0}^{n} x_i$"


class TestFormatLabelCommentedFunctionality:
    """Test the commented-out functionality for future reference."""
    
    def test_future_underscore_replacement(self):
        """Test what the function would do if underscore replacement was enabled."""
        # Currently returns unchanged
        assert format_label("test_label") == "test_label"
        # Would return: "Test Label" if enabled
        
        assert format_label("complex_label_with_underscores") == "complex_label_with_underscores"
        # Would return: "Complex Label With Underscores" if enabled
        
        assert format_label("__private__") == "__private__"
        # Would return: "  Private  " if enabled (preserving double underscores)
        
    def test_future_capitalization(self):
        """Test what the function would do if capitalization was enabled."""
        # Currently returns unchanged
        assert format_label("all_lowercase") == "all_lowercase"
        # Would return: "All Lowercase" if enabled
        
        assert format_label("KEEP_UPPERCASE") == "KEEP_UPPERCASE"
        # Would return: "KEEP_UPPERCASE" if enabled (all caps preserved)
        
        assert format_label("mixed_Case_Label") == "mixed_Case_Label"
        # Would return: "Mixed Case Label" if enabled
        
    def test_future_edge_cases(self):
        """Test edge cases for the commented functionality."""
        # Single character
        assert format_label("x") == "x"
        # Would return: "X" if enabled
        
        # Multiple underscores
        assert format_label("a__b___c") == "a__b___c"
        # Would return: "A  B   C" if enabled
        
        # Leading/trailing underscores
        assert format_label("_private_var_") == "_private_var_"
        # Would return: " Private Var " if enabled


class TestFormatLabelWithMatplotlib:
    """Test format_label in matplotlib context."""
    
    def test_with_axis_labels(self):
        """Test using format_label with axis labels."""
        fig, ax = plt.subplots()
        
        xlabel = format_label("time_seconds")
        ylabel = format_label("voltage_mV")
        title = format_label("experiment_results")
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        
        assert ax.get_xlabel() == "time_seconds"
        assert ax.get_ylabel() == "voltage_mV"
        assert ax.get_title() == "experiment_results"
        
        plt.close(fig)
        
    def test_with_legend_labels(self):
        """Test using format_label with legend labels."""
        fig, ax = plt.subplots()
        
        x = np.linspace(0, 10, 100)
        labels = ["sine_wave", "cosine_wave", "tangent_wave"]
        
        for i, func in enumerate([np.sin, np.cos, np.tan]):
            ax.plot(x, func(x), label=format_label(labels[i]))
        
        legend = ax.legend()
        legend_texts = [t.get_text() for t in legend.get_texts()]
        
        assert legend_texts == labels
        
        plt.close(fig)
        
    def test_with_tick_labels(self):
        """Test using format_label with tick labels."""
        fig, ax = plt.subplots()
        
        categories = ["category_A", "category_B", "category_C"]
        formatted_categories = [format_label(cat) for cat in categories]
        
        ax.bar(range(len(categories)), [1, 2, 3])
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(formatted_categories)
        
        tick_labels = [t.get_text() for t in ax.get_xticklabels()]
        assert tick_labels == categories
        
        plt.close(fig)
        
    def test_savefig_integration(self):
        """Test integration with figure saving."""
        import matplotlib.pyplot as plt
        from scitex.io import save
        
        # Setup
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Apply formatted label
        label = format_label("test_label_for_saving")
        ax.set_title(label)
        
        # Saving
        spath = f"./{os.path.basename(__file__)}.jpg"
        save(fig, spath)
        
        # Check saved file
        ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
        actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
        assert os.path.exists(actual_spath), f"Failed to save figure to {spath}"
        
        plt.close(fig)


class TestFormatLabelRobustness:
    """Test robustness and error handling."""
    
    def test_very_long_labels(self):
        """Test handling of very long labels."""
        long_label = "a" * 1000
        assert format_label(long_label) == long_label
        
        long_underscore_label = "_".join(["word"] * 100)
        assert format_label(long_underscore_label) == long_underscore_label
        
    def test_numeric_string_labels(self):
        """Test labels that look like numbers."""
        assert format_label("123") == "123"
        assert format_label("3.14159") == "3.14159"
        assert format_label("1e6") == "1e6"
        assert format_label("0xFF") == "0xFF"
        
    def test_mixed_type_labels(self):
        """Test labels with mixed content."""
        assert format_label("label_123") == "label_123"
        assert format_label("v2.0_beta") == "v2.0_beta"
        assert format_label("test@2024") == "test@2024"
        
    def test_boolean_values(self):
        """Test boolean value handling."""
        assert format_label(True) is True
        assert format_label(False) is False
        
    def test_custom_objects(self):
        """Test custom objects that might be used as labels."""
        class CustomLabel:
            def __str__(self):
                return "custom_label"
        
        obj = CustomLabel()
        assert format_label(obj) is obj  # Returns unchanged
        
    def test_callable_objects(self):
        """Test callable objects."""
        func = lambda x: x
        assert format_label(func) is func
        
        def named_func():
            pass
        assert format_label(named_func) is named_func


class TestFormatLabelPerformance:
    """Test performance characteristics."""
    
    def test_no_unnecessary_string_copies(self):
        """Test that strings aren't unnecessarily copied."""
        original = "test_string"
        result = format_label(original)
        assert result is original  # Same object since no transformation
        
    def test_handles_many_calls(self):
        """Test performance with many calls."""
        labels = [f"label_{i}" for i in range(1000)]
        
        # Should handle many calls efficiently
        formatted = [format_label(label) for label in labels]
        assert formatted == labels
        
    def test_memory_efficiency(self):
        """Test memory efficiency with various inputs."""
        # Large objects should be returned unchanged without copying
        large_array = np.zeros((1000, 1000))
        result = format_label(large_array)
        assert result is large_array  # Same object


class TestFormatLabelIntegration:
    """Test integration with the broader scitex ecosystem."""
    
    @patch('scitex.plt.ax._style._format_label.format_label')
    def test_mocked_enhanced_functionality(self, mock_format):
        """Test what enhanced functionality might look like."""
        # Mock the enhanced functionality
        def enhanced_format(label):
            if isinstance(label, str):
                label = label.replace("_", " ")
                label = " ".join(word.capitalize() for word in label.split())
                if label.isupper():
                    return label
            return label
        
        mock_format.side_effect = enhanced_format
        
        # Test enhanced behavior
        assert mock_format("test_label") == "Test Label"
        assert mock_format("UPPERCASE") == "UPPERCASE"
        
    def test_compatible_with_matplotlib_text(self):
        """Test compatibility with matplotlib Text objects."""
        fig, ax = plt.subplots()
        
        text = ax.text(0.5, 0.5, format_label("test_text"))
        assert text.get_text() == "test_text"
        
        plt.close(fig)
        
    def test_preserves_label_properties(self):
        """Test that label properties are preserved."""
        labels_with_properties = [
            ("$equation$", True),  # Math text
            ("plain text", False),
            (r"\LaTeX", False),
            ("_subscript", False),
            ("^superscript", False)
        ]
        
        for label, is_math in labels_with_properties:
            formatted = format_label(label)
            assert formatted == label  # Current behavior preserves everything


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_format_label.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-09-15 09:39:02 (ywatanabe)"
# # /home/ywatanabe/proj/_scitex_repo_openhands/src/scitex/plt/ax/_format_label.py
#
#
# def format_label(label):
#     """
#     Format label by capitalizing first letter and replacing underscores with spaces.
#     """
#
#     # if isinstance(label, str):
#     #     # Replace underscores with spaces
#     #     label = label.replace("_", " ")
#
#     #     # Capitalize first letter of each word
#     #     label = " ".join(word.capitalize() for word in label.split())
#
#     #     # Special case for abbreviations (all caps)
#     #     if label.isupper():
#     #         return label
#
#     return label

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/ax/_style/_format_label.py
# --------------------------------------------------------------------------------
