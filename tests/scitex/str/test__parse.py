#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__parse.py

"""Tests for string parsing functionality."""

import os
import pytest
from unittest.mock import patch


from scitex.str._parse import parse

class TestParseBidirectional:
    """Test bidirectional parse function."""
    
    def test_parse_forward_direction(self):
        """Test parsing in forward direction."""
        
        string = "./data/Patient_23_002"
        pattern = "./data/Patient_{id}"
        result = parse(string, pattern)
        
        assert hasattr(result, '__getitem__')  # DotDict behaves like dict
        assert result["id"] == "23_002"
    
    def test_parse_reverse_direction(self):
        """Test parsing in reverse direction."""
        
        pattern = "./data/Patient_{id}"
        string = "./data/Patient_23_002"
        result = parse(pattern, string)
        
        assert hasattr(result, '__getitem__')  # DotDict behaves like dict
        assert result["id"] == "23_002"
    
    def test_parse_complex_pattern(self):
        """Test parsing complex file path pattern."""
        
        string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_12_02_00.mat"
        pattern = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
        
        result = parse(string, pattern)
        
        assert result["patient_id"] == "23_002"
        assert result["YYYY"] == "2010"
        assert result["MM"] == "07"
        assert result["DD"] == "31"
        assert result["HH"] == "12"
        assert result["mm"] == "02"
    
    def test_parse_both_directions_fail(self):
        """Test when parsing fails in both directions."""
        
        string = "completely/different/path"
        pattern = "./data/Patient_{id}"
        
        with pytest.raises(ValueError, match="Parsing failed in both directions"):
            parse(string, pattern)
    
    def test_parse_inconsistent_placeholder_values(self):
        """Test error when placeholder values are inconsistent."""
        
        string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_99_02_00.mat"
        pattern = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
        
        with pytest.raises(ValueError, match="Parsing failed in both directions"):
            parse(string, pattern)
    
    def test_parse_returns_dotdict(self):
        """Test that parse returns a DotDict instance."""
        from scitex.dict import DotDict
        
        string = "./data/Patient_23_002"
        pattern = "./data/Patient_{id}"
        result = parse(string, pattern)
        
        assert isinstance(result, DotDict)
        assert result.id == "23_002"  # Test dot notation access


class TestParseInternal:
    """Test internal _parse function."""
    
    def test_parse_internal_basic(self):
        """Test internal _parse function basic functionality."""
        from scitex.str import _parse
        
        string = "./data/Patient_23_002"
        expression = "./data/Patient_{id}"
        result = _parse(string, expression)
        
        assert result["id"] == "23_002"
    
    def test_parse_internal_path_normalization(self):
        """Test path normalization in _parse."""
        from scitex.str import _parse
        
        string = "./././data/Patient_23_002"
        expression = "./data/Patient_{id}"
        result = _parse(string, expression)
        
        assert result["id"] == "23_002"
    
    def test_parse_internal_expression_cleanup(self):
        """Test expression cleanup in _parse."""
        from scitex.str import _parse
        
        string = "./data/Patient_23_002"
        expression = 'f"./data/Patient_{id}"'  # With f-string formatting
        result = _parse(string, expression)
        
        assert result["id"] == "23_002"
    
    def test_parse_internal_no_match(self):
        """Test _parse when string doesn't match pattern."""
        from scitex.str import _parse
        
        string = "./different/path"
        expression = "./data/Patient_{id}"
        
        with pytest.raises(ValueError, match="String format does not match expression"):
            _parse(string, expression)
    
    def test_parse_internal_duplicate_placeholder_consistent(self):
        """Test _parse with duplicate placeholders having consistent values."""
        from scitex.str import _parse
        
        string = "./data/Patient_12_Hour_12_UTC_12_02_00.mat"
        expression = "./data/Patient_{HH}_Hour_{HH}_UTC_{HH}_{mm}_00.mat"
        result = _parse(string, expression)
        
        assert result["HH"] == "12"
        assert result["mm"] == "02"
    
    def test_parse_internal_duplicate_placeholder_inconsistent(self):
        """Test _parse with duplicate placeholders having inconsistent values."""
        from scitex.str import _parse
        
        string = "./data/Patient_12_Hour_99_UTC_88_02_00.mat"
        expression = "./data/Patient_{HH}_Hour_{HH}_UTC_{HH}_{mm}_00.mat"
        
        with pytest.raises(ValueError, match="Inconsistent values for placeholder 'HH'"):
            _parse(string, expression)


class TestParseEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_parse_empty_string_empty_pattern(self):
        """Test parsing empty string with empty pattern."""
        from scitex.str import _parse
        
        result = _parse("", "")
        assert result == {}
    
    def test_parse_no_placeholders(self):
        """Test parsing with no placeholders in pattern."""
        from scitex.str import _parse
        
        string = "./data/fixed_path"
        expression = "./data/fixed_path"
        result = _parse(string, expression)
        
        assert result == {}
    
    def test_parse_multiple_placeholders_same_segment(self):
        """Test parsing with multiple placeholders in same path segment."""
        from scitex.str import _parse
        
        # This will not work with current regex pattern but should handle gracefully
        string = "file_prefix_suffix.txt"
        expression = "file_{prefix}_{suffix}.txt"
        
        # Current implementation doesn't handle this case properly
        # but should not crash
        with pytest.raises(ValueError):
            _parse(string, expression)
    
    def test_parse_special_characters(self):
        """Test parsing with special regex characters."""
        from scitex.str import _parse
        
        string = "./data/file[1].txt"
        expression = "./data/file[1].txt"  # No placeholders, should match exactly
        result = _parse(string, expression)
        
        assert result == {}
    
    def test_parse_unicode_characters(self):
        """Test parsing with unicode characters."""
        from scitex.str import _parse
        
        string = "./data/Patient_測試_002"
        expression = "./data/Patient_{id}_002"
        result = _parse(string, expression)
        
        assert result["id"] == "測試"


class TestParseDocstrings:
    """Test examples from docstrings work correctly."""
    
    def test_docstring_example_forward(self):
        """Test forward parsing example from docstring."""
        
        result = parse("./data/Patient_23_002", "./data/Patient_{id}")
        assert result["id"] == "23_002"
    
    def test_docstring_example_reverse(self):
        """Test reverse parsing example from docstring."""
        
        result = parse("./data/Patient_{id}", "./data/Patient_23_002")
        assert result["id"] == "23_002"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_parse.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-16 10:14:44 (ywatanabe)"
# # File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/str/_parse.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/str/_parse.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import re
# from typing import Dict, Union
# 
# from ..dict._DotDict import DotDict as _DotDict
# 
# 
# def parse(
#     string_or_fstring: str, fstring_or_string: str
# ) -> Union[Dict[str, Union[str, int]], str]:
#     """
#     Bidirectional parser that attempts parsing in both directions.
# 
#     Parameters
#     ----------
#     string_or_fstring : str
#         Either the input string to parse or the pattern
#     fstring_or_string : str
#         Either the pattern to match against or the input string
# 
#     Returns
#     -------
#     Union[Dict[str, Union[str, int]], str]
#         Parsed dictionary or formatted string
# 
#     Raises
#     ------
#     ValueError
#         If parsing fails in both directions
# 
#     Examples
#     --------
#     >>> # Forward parsing
#     >>> parse("./data/Patient_23_002", "./data/Patient_{id}")
#     {'id': '23_002'}
# 
#     >>> # Reverse parsing
#     >>> parse("./data/Patient_{id}", "./data/Patient_23_002")
#     {'id': '23_002'}
#     """
#     # try:
#     #     parsed = _parse(string_or_fstring, fstring_or_string)
#     #     if parsed:
#     #         return parsed
#     # except Exception as e:
#     #     print(e)
# 
#     # try:
#     #     parsed = _parse(fstring_or_string, string_or_fstring)
#     #     if parsed:
#     #         return parsed
#     # except Exception as e:
#     #     print(e)
#     errors = []
# 
#     # Try first direction
#     try:
#         result = _parse(string_or_fstring, fstring_or_string)
#         if result:
#             return result
#     except ValueError as e:
#         errors.append(str(e))
#         # logging.warning(f"First attempt failed: {e}")
# 
#     # Try reverse direction
#     try:
#         result = _parse(fstring_or_string, string_or_fstring)
#         if result:
#             return result
#     except ValueError as e:
#         errors.append(str(e))
#         # logging.warning(f"Second attempt failed: {e}")
# 
#     raise ValueError(
#         f"Parsing failed in both directions: {' | '.join(errors)}"
#     )
# 
# 
# def _parse(string: str, expression: str) -> Dict[str, Union[str, int]]:
#     """
#     Parse a string based on a given expression pattern.
# 
#     Parameters
#     ----------
#     string : str
#         The string to parse
#     expression : str
#         The expression pattern to match against the string
# 
#     Returns
#     -------
#     Dict[str, Union[str, int]]
#         A dictionary containing parsed information
# 
#     Raises
#     ------
#     ValueError
#         If the string format does not match the given expression
#         If duplicate placeholders have inconsistent values
#     """
#     # Clean up inputs
#     string = string.replace("/./", "/")
#     expression = expression.strip()
#     if expression.startswith('f"') and expression.endswith('"'):
#         expression = expression[2:-1]
#     elif expression.startswith('"') and expression.endswith('"'):
#         expression = expression[1:-1]
#     elif expression.startswith("'") and expression.endswith("'"):
#         expression = expression[1:-1]
# 
#     # Remove format specifiers from placeholders
#     expression_clean = re.sub(r"{(\w+):[^}]+}", r"{\1}", expression)
# 
#     # Extract placeholder names
#     placeholders = re.findall(r"{(\w+)}", expression_clean)
# 
#     # Create regex pattern
#     pattern = re.sub(r"{(\w+)}", r"([^/]+)", expression_clean)
# 
#     match = re.match(pattern, string)
# 
#     if not match:
#         raise ValueError(
#             f"String format does not match expression: {string} vs {expression}"
#         )
# 
#     groups = match.groups()
#     result = {}
# 
#     for placeholder, value in zip(placeholders, groups):
#         if placeholder in result and result[placeholder] != value:
#             raise ValueError(
#                 f"Inconsistent values for placeholder '{placeholder}'"
#             )
# 
#         # Try to convert to int if it looks like a number
#         if value.lstrip("-").isdigit():
#             result[placeholder] = int(value)
#         else:
#             result[placeholder] = value
# 
#     return _DotDict(result)
# 
# 
# if __name__ == "__main__":
#     string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_12_02_00.mat"
#     expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
#     results = parse(string, expression)
#     print(results)
# 
#     # Inconsistent version
#     string = "./data/mat_tmp/Patient_23_002/Data_2010_07_31/Hour_12/UTC_99_99_00.mat"
#     expression = "./data/mat_tmp/Patient_{patient_id}/Data_{YYYY}_{MM}_{DD}/Hour_{HH}/UTC_{HH}_{mm}_00.mat"
#     results = parse(string, expression)  # this should raise error
#     print(results)
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_parse.py
# --------------------------------------------------------------------------------
