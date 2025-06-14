#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10"

"""Comprehensive tests for _SigMacro_toBlue.py

Tests cover:
- Basic functionality of printing VBA macro
- Backward compatibility with deprecated function
- Output validation
- Warning handling
"""

import io
import os
import sys
import warnings
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestSigmacroToBlue:
    """Test sigmacro_to_blue function."""
    
    def test_sigmacro_to_blue_prints_output(self, capsys):
        """Test that function prints VBA macro."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "Option Explicit" in captured.out
    
    def test_sigmacro_to_blue_contains_vba_code(self, capsys):
        """Test that output contains expected VBA code sections."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for key VBA functions
        assert "Function FlagOn" in output
        assert "Function FlagOff" in output
        assert "Function getColor" in output
        assert "Function findObjectType" in output
        assert "Sub Main()" in output
        assert "Sub updatePlot" in output
        assert "Sub updateScatter" in output
        assert "Sub updateSolid" in output
    
    def test_sigmacro_to_blue_color_definitions(self, capsys):
        """Test that all color definitions are present."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for color definitions
        colors = [
            "Black", "Gray", "White", "Blue", "Green", "Red",
            "Yellow", "Purple", "Pink", "LightBlue", "DarkBlue",
            "Dan", "Brown"
        ]
        
        for color in colors:
            assert f'Case "{color}"' in output
            assert "RGB(" in output  # Should have RGB definitions
    
    def test_sigmacro_to_blue_object_types(self, capsys):
        """Test that all object types are handled."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for object type cases
        object_types = [
            "SLA_TYPE_SCATTER",
            "SLA_TYPE_BAR",
            "SLA_TYPE_STACKED",
            "SLA_TYPE_TUKEY",
            "SLA_TYPE_3DSCATTER"
        ]
        
        for obj_type in object_types:
            assert obj_type in output
    
    def test_sigmacro_to_blue_error_handling(self, capsys):
        """Test that error handling is included."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for error handling
        assert "On Error GoTo ErrorHandler" in output
        assert "ErrorHandler:" in output
        assert "Err.Description" in output
        assert "MsgBox" in output
    
    def test_sigmacro_to_blue_complete_structure(self, capsys):
        """Test that VBA macro has complete structure."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check structure
        assert output.strip().startswith("Option Explicit")
        assert "End Sub" in output
        assert "End Function" in output
        
        # Check for proper VBA syntax elements
        assert "Dim " in output  # Variable declarations
        assert "As Long" in output  # Type declarations
        assert "As String" in output
        assert "Select Case" in output
        assert "End Select" in output


class TestBackwardCompatibility:
    """Test backward compatibility with deprecated function."""
    
    def test_deprecated_function_exists(self):
        """Test that deprecated function still exists."""
        from scitex.gists import SigMacro_toBlue
        
        assert callable(SigMacro_toBlue)
    
    def test_deprecated_function_warns(self):
        """Test that deprecated function issues warning."""
        from scitex.gists import SigMacro_toBlue
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SigMacro_toBlue()
            
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "SigMacro_toBlue is deprecated" in str(w[0].message)
            assert "use sigmacro_to_blue() instead" in str(w[0].message)
    
    def test_deprecated_function_same_output(self, capsys):
        """Test that deprecated function produces same output."""
        from scitex.gists import sigmacro_to_blue, SigMacro_toBlue
        
        # Get output from new function
        sigmacro_to_blue()
        captured_new = capsys.readouterr()
        
        # Get output from deprecated function
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            SigMacro_toBlue()
        captured_old = capsys.readouterr()
        
        assert captured_new.out == captured_old.out
    
    def test_deprecated_function_stacklevel(self):
        """Test that warning has correct stacklevel."""
        from scitex.gists import SigMacro_toBlue
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Call from this function
            SigMacro_toBlue()
            
            assert len(w) == 1
            # The warning should point to this test function, not internal code
            assert __name__ in w[0].filename or "test_" in w[0].filename


class TestOutputValidation:
    """Test validation of the generated VBA macro."""
    
    def test_output_is_valid_vba_syntax(self, capsys):
        """Test that output follows VBA syntax rules."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for balanced quotes
        assert output.count('"') % 2 == 0
        
        # Check for balanced parentheses
        assert output.count('(') == output.count(')')
        
        # Check indentation exists
        assert "    " in output  # VBA uses 4-space indentation
    
    def test_output_rgb_values(self, capsys):
        """Test that RGB values are valid."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Extract RGB values using simple parsing
        import re
        rgb_pattern = r'RGB\((\d+),\s*(\d+),\s*(\d+)\)'
        matches = re.findall(rgb_pattern, output)
        
        assert len(matches) > 0  # Should find RGB values
        
        for r, g, b in matches:
            # RGB values should be 0-255
            assert 0 <= int(r) <= 255
            assert 0 <= int(g) <= 255
            assert 0 <= int(b) <= 255
    
    def test_output_hex_values(self, capsys):
        """Test that hex values are present and valid."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for hex values (VBA format: &H00000000&)
        import re
        hex_pattern = r'&H[0-9A-Fa-f]+&'
        matches = re.findall(hex_pattern, output)
        
        assert len(matches) > 0  # Should find hex values
        
        # Specific hex values mentioned in code
        assert "&H00000002&" in output  # Color repeat
        assert "&H00000005&" in output  # Thickness
        assert "&H00000020&" in output  # Size
    
    def test_output_comments(self, capsys):
        """Test that helpful comments are included."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check for comments
        assert "'" in output  # VBA comment character
        assert ".12 mm = .047 Inches" in output
        assert ".8 mm = .032 inch" in output
        assert "Default or error handling" in output


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_multiple_calls(self, capsys):
        """Test that function can be called multiple times."""
        from scitex.gists import sigmacro_to_blue
        
        # First call
        sigmacro_to_blue()
        captured1 = capsys.readouterr()
        
        # Second call
        sigmacro_to_blue()
        captured2 = capsys.readouterr()
        
        assert captured1.out == captured2.out
        assert len(captured1.out) > 0
    
    def test_no_side_effects(self):
        """Test that function has no side effects."""
        from scitex.gists import sigmacro_to_blue
        
        # Capture initial state
        import sys
        initial_modules = set(sys.modules.keys())
        
        # Call function
        with redirect_stdout(io.StringIO()):
            sigmacro_to_blue()
        
        # Check no new modules imported
        final_modules = set(sys.modules.keys())
        # Only the gists module itself should be new
        new_modules = final_modules - initial_modules
        assert all("gists" in mod or "SigMacro" in mod for mod in new_modules)
    
    def test_output_to_file(self):
        """Test redirecting output to file."""
        from scitex.gists import sigmacro_to_blue
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            sigmacro_to_blue()
        
        macro_content = output_buffer.getvalue()
        
        assert len(macro_content) > 0
        assert "Option Explicit" in macro_content
        
        # Could write to actual .vba file
        # with open("test_macro.vba", "w") as f:
        #     f.write(macro_content)


class TestDocumentation:
    """Test documentation and docstrings."""
    
    def test_function_has_docstring(self):
        """Test that function has proper docstring."""
        from scitex.gists import sigmacro_to_blue
        
        assert sigmacro_to_blue.__doc__ is not None
        assert "SigmaPlot" in sigmacro_to_blue.__doc__
        assert "macro" in sigmacro_to_blue.__doc__.lower()
    
    def test_deprecated_function_docstring(self):
        """Test that deprecated function has docstring."""
        from scitex.gists import SigMacro_toBlue
        
        assert SigMacro_toBlue.__doc__ is not None
        assert "deprecated" in SigMacro_toBlue.__doc__.lower()


class TestIntegration:
    """Test integration scenarios."""
    
    def test_capture_for_processing(self, capsys):
        """Test capturing output for further processing."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        
        # Process the VBA code
        lines = captured.out.strip().split('\n')
        
        # Count different types of elements
        functions = sum(1 for line in lines if line.strip().startswith("Function"))
        subs = sum(1 for line in lines if line.strip().startswith("Sub"))
        
        assert functions >= 3  # FlagOn, FlagOff, getColor, findObjectType
        assert subs >= 4  # Main, updatePlot, updateScatter, updateSolid
    
    def test_extract_color_mapping(self, capsys):
        """Test extracting color mappings from output."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        
        # Extract color mappings
        import re
        color_pattern = r'Case "(\w+)"\s*\n\s*getColor = RGB\((\d+),\s*(\d+),\s*(\d+)\)'
        matches = re.findall(color_pattern, captured.out)
        
        color_map = {name: (int(r), int(g), int(b)) for name, r, g, b in matches}
        
        # Verify some known colors
        assert color_map.get("Black") == (0, 0, 0)
        assert color_map.get("White") == (255, 255, 255)
        assert color_map.get("Blue") == (0, 128, 192)
        assert color_map.get("Red") == (255, 70, 50)
    
    def test_macro_completeness(self, capsys):
        """Test that macro is complete and self-contained."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that all referenced functions/subs are defined
        referenced = ["FlagOn", "FlagOff", "getColor", "updatePlot", 
                     "updateScatter", "updateSolid", "findObjectType"]
        
        for ref in referenced:
            assert ref in output
            
        # Check Main sub calls other functions
        assert "getColor(" in output
        assert "findObjectType()" in output
        assert "updatePlot " in output or "updatePlot(" in output


class TestUsageScenarios:
    """Test real-world usage scenarios."""
    
    def test_save_macro_to_file(self, tmp_path, capsys):
        """Test saving macro to a VBA file."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        
        # Save to file
        vba_file = tmp_path / "SigmaPlot_ToBlue.vba"
        vba_file.write_text(captured.out)
        
        # Verify file
        assert vba_file.exists()
        content = vba_file.read_text()
        assert "Option Explicit" in content
        assert len(content) > 1000  # Should be substantial
    
    def test_modify_for_different_color(self, capsys):
        """Test modifying output for different default color."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        
        # Modify to use Red instead of Blue
        modified = captured.out.replace('getColor("Blue")', 'getColor("Red")')
        
        assert 'getColor("Red")' in modified
        assert 'getColor("Blue")' not in modified
    
    def test_extract_for_documentation(self, capsys):
        """Test extracting parts for documentation."""
        from scitex.gists import sigmacro_to_blue
        
        sigmacro_to_blue()
        captured = capsys.readouterr()
        
        # Extract just the color function for documentation
        lines = captured.out.split('\n')
        in_color_func = False
        color_func_lines = []
        
        for line in lines:
            if "Function getColor" in line:
                in_color_func = True
            if in_color_func:
                color_func_lines.append(line)
            if in_color_func and "End Function" in line:
                break
        
        color_func = '\n'.join(color_func_lines)
        assert "Function getColor" in color_func
        assert "End Function" in color_func
        assert len(color_func_lines) > 20  # Should have all color cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])