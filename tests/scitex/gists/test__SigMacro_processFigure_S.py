#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for SigMacro_processFigure_S functionality

import pytest
import warnings
from io import StringIO
from unittest.mock import patch
import sys

from scitex.gists import (
    sigmacro_process_figure_s,
    SigMacro_processFigure_S
)


def test_sigmacro_process_figure_s_prints_output():
    """Test that sigmacro_process_figure_s prints output."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check that output is not empty
        assert len(output) > 0
        assert output.strip() != ""


def test_sigmacro_process_figure_s_contains_vba_code():
    """Test that the output contains expected VBA code elements."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for key VBA elements
        assert "Option Explicit" in output
        assert "Sub Main()" in output
        assert "End Sub" in output
        assert "Function FlagOn" in output
        assert "Function FlagOff" in output
        assert "Sub setTitleSize()" in output
        assert "Sub setLabelSize(dimension)" in output
        assert "Sub setTickLabelSize(dimension)" in output
        assert "Sub processTicks(dimension)" in output
        assert "Sub removeAxis(dimension)" in output
        assert "Sub resizeFigure" in output


def test_sigmacro_process_figure_s_contains_constants():
    """Test that the output contains expected constants."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for constants
        assert "Const FLAG_SET_BIT As Long = 1" in output
        assert "Const FLAG_CLEAR_BIT As Long = 0" in output


def test_sigmacro_process_figure_s_contains_comments():
    """Test that the output contains helpful comments."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for comments
        assert "' Constants for FLAG_SET_BIT and FLAG_CLEAR_BIT should be defined" in output
        assert "' Function to set option flag bits on" in output
        assert "' Function to set option flag bits off" in output
        assert "' Procedure to set the title size to 8 points" in output
        assert "' Main procedure" in output


def test_sigmacro_process_figure_s_size_settings():
    """Test that the output contains correct size settings."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for size settings
        assert '"111"' in output  # 8 points for title and labels
        assert '"97"' in output   # 7 points for tick labels
        assert "&H000004F5&" in output  # Width setting
        assert "&H00000378&" in output  # Height setting


def test_sigmacro_process_figure_s_axis_operations():
    """Test that the output contains axis operations."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for axis operations
        assert "setLabelSize(1) ' X-axis" in output
        assert "setLabelSize(2) ' Y-axis" in output
        assert "setTickLabelSize(1) ' X-axis" in output
        assert "setTickLabelSize(2) ' Y-axis" in output
        assert "processTicks(1) ' X-axis" in output
        assert "processTicks(2) ' Y-axis" in output
        assert "removeAxis(1) ' Right axis" in output
        assert "removeAxis(2) ' Top axis" in output


def test_sigmacro_process_figure_s_sigmaplot_specific():
    """Test that the output contains SigmaPlot-specific elements."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for SigmaPlot-specific elements
        assert "ActiveDocument" in output
        assert "CurrentPageItem" in output
        assert "GraphPages" in output
        assert "CurrentPageObject" in output
        assert "GPT_GRAPH" in output
        assert "GPT_AXIS" in output
        assert "SetCurrentObjectAttribute" in output


def test_sigmacro_process_figure_s_returns_none():
    """Test that the function returns None (just prints)."""
    with patch('sys.stdout', new=StringIO()):
        result = sigmacro_process_figure_s()
        assert result is None


def test_deprecated_function_raises_warning():
    """Test that the deprecated function raises a deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with patch('sys.stdout', new=StringIO()):
            SigMacro_processFigure_S()
        
        # Check that a deprecation warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "SigMacro_processFigure_S is deprecated" in str(w[0].message)
        assert "use sigmacro_process_figure_s() instead" in str(w[0].message)


def test_deprecated_function_still_works():
    """Test that the deprecated function still produces output."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            SigMacro_processFigure_S()
            output = fake_stdout.getvalue()
            
            # Should produce the same output
            assert len(output) > 0
            assert "Option Explicit" in output
            assert "Sub Main()" in output


def test_output_is_valid_vba_structure():
    """Test that the output has valid VBA structure."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Count opening and closing statements
        sub_count = output.count("Sub ")
        end_sub_count = output.count("End Sub")
        function_count = output.count("Function ")
        end_function_count = output.count("End Function")
        
        # Should have matching pairs
        assert sub_count == end_sub_count
        assert function_count == end_function_count
        
        # Should have expected number of subroutines
        assert sub_count >= 7  # At least 7 Sub procedures


def test_output_multiline_format():
    """Test that the output is properly formatted as multiline."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Should have multiple lines
        lines = output.strip().split('\n')
        assert len(lines) > 50  # Should have many lines of VBA code
        
        # Check indentation exists
        indented_lines = [line for line in lines if line.startswith('    ')]
        assert len(indented_lines) > 0


def test_function_docstring():
    """Test that the function has a proper docstring."""
    assert sigmacro_process_figure_s.__doc__ is not None
    assert "SigmaPlot" in sigmacro_process_figure_s.__doc__
    assert "macro" in sigmacro_process_figure_s.__doc__.lower()


def test_no_side_effects():
    """Test that calling the function has no side effects besides printing."""
    # Store original stdout
    original_stdout = sys.stdout
    
    # Call function
    with patch('sys.stdout', new=StringIO()):
        sigmacro_process_figure_s()
    
    # Verify stdout is restored
    assert sys.stdout is original_stdout


def test_consistent_output():
    """Test that the function produces consistent output."""
    outputs = []
    
    for _ in range(3):
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            sigmacro_process_figure_s()
            outputs.append(fake_stdout.getvalue())
    
    # All outputs should be identical
    assert outputs[0] == outputs[1] == outputs[2]


def test_output_contains_dim_declarations():
    """Test that the output contains variable declarations."""
    with patch('sys.stdout', new=StringIO()) as fake_stdout:
        sigmacro_process_figure_s()
        output = fake_stdout.getvalue()
        
        # Check for Dim statements
        assert "Dim FullPATH As String" in output
        assert "Dim OrigPageName As String" in output
        assert "Dim ObjectType As String" in output
        assert "Dim COLOR As Long" in output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gists/_SigMacro_processFigure_S.py
# --------------------------------------------------------------------------------
# def SigMacro_processFigure_S():
#     """Print a macro for SigmaPlot (v12.0) to format a panel. Please refer to the 'Automating Routine Tasks' section of the official documentation."""
#
#     print(
#         """
# Option Explicit
#
# ' Constants for FLAG_SET_BIT and FLAG_CLEAR_BIT should be defined
# Const FLAG_SET_BIT As Long = 1 ' Assuming value, replace with actual value
# Const FLAG_CLEAR_BIT As Long = 0 ' Assuming value, replace with actual value
#
# ' Function to set option flag bits on
# Function FlagOn(flag As Long) As Long
#     FlagOn = flag Or FLAG_SET_BIT
# End Function
#
# ' Function to set option flag bits off
# Function FlagOff(flag As Long) As Long
#     FlagOff = flag And Not FLAG_CLEAR_BIT
# End Function
#
# ' Procedure to set the title size to 8 points
# Sub setTitleSize()
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "111") ' Size set to 8 points
# End Sub
#
# ' Procedure to set label size for a given dimension to 8 points
# Sub setLabelSize(dimension)
#     ' ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "111") ' Size set to 8 points
# End Sub
#
# ' Procedure to set tick label size for a given dimension to 7 points
# Sub setTickLabelSize(dimension)
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).TickLabelAttributes(SAA_LINE_MAJORTIC).SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETOBJECTATTR, STA_SIZE, "97") ' Size set to 7 points
# End Sub
#
# ' Procedure to process tick settings for a given dimension
# Sub processTicks(dimension)
#     ' Ensure the object is correctly targeted before setting attributes
#     ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_AXIS).NameObject.SetObjectCurrent
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SELECTLINE, 1)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SEA_THICKNESS, &H00000008)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_TICSIZE, &H00000020)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SELECTLINE, 2)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SEA_THICKNESS, &H00000008)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_TICSIZE, &H00000020)
# End Sub
#
# ' Procedure to remove an axis for a given dimension
# Sub removeAxis(dimension)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETPLOTATTR, SLA_SELECTDIM, dimension)
#     ActiveDocument.CurrentPageItem.SetCurrentObjectAttribute(GPM_SETAXISATTR, SAA_SUB2OPTIONS, &H00000000)
# End Sub
#
# Sub resizeFigure
# 	ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH).NameObject.SetObjectCurrent
#     With ActiveDocument.CurrentPageItem.GraphPages(0).CurrentPageObject(GPT_GRAPH)
# 	'.Top = 0
# 	'.Left = 0
# 	.Width = &H000004F5&
# 	.Height = &H00000378&
# 	End With
# End Sub
#
# ' Main procedure
# Sub Main()
#     Dim FullPATH As String
#     Dim OrigPageName As String
#     Dim ObjectType As String
#     Dim COLOR As Long
#
#     ' Saves the original page to jump back
#     FullPATH = ActiveDocument.FullName
#     OrigPageName = ActiveDocument.CurrentPageItem.Name
#     ActiveDocument.NotebookItems(OrigPageName).IsCurrentBrowserEntry = True
#
# 	' Code to set the figure size should be implemented here
#     resizeFigure
#
#     ' Set the title sizes
#     setTitleSize
#
#     ' Set the sizes of X/Y labels
#     setLabelSize(1) ' X-axis
#     setLabelSize(2) ' Y-axis
#
#     ' Set the sizes of X/Y tick labels
#     setTickLabelSize(1) ' X-axis
#     setTickLabelSize(2) ' Y-axis
#
#     ' Set tick length and width
#     processTicks(1) ' X-axis
#     processTicks(2) ' Y-axis
#
#     ' Remove right and top axes
#     removeAxis(1) ' Right axis
#     removeAxis(2) ' Top axis
#
#     ' Go back to the original page
# 	Notebooks(FullPATH).NotebookItems(OrigPageName).Open
#
# End Sub
#     """
#     )

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gists/_SigMacro_processFigure_S.py
# --------------------------------------------------------------------------------
