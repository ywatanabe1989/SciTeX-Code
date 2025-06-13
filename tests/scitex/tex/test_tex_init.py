#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:20:00 (ywatanabe)"
# File: tests/scitex/tex/test___init__.py

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestTexModule:
    """Test suite for scitex.tex module."""

    def test_preview_import(self):
        """Test that preview function can be imported from scitex.tex."""
        from scitex.tex import preview
        
        assert callable(preview)
        assert hasattr(preview, '__call__')

    def test_to_vec_import(self):
        """Test that to_vec function can be imported from scitex.tex."""
        from scitex.tex import to_vec
        
        assert callable(to_vec)
        assert hasattr(to_vec, '__call__')

    def test_module_attributes(self):
        """Test that scitex.tex module has expected attributes."""
        import scitex.tex
        
        assert hasattr(scitex.tex, 'preview')
        assert hasattr(scitex.tex, 'to_vec')
        assert callable(scitex.tex.preview)
        assert callable(scitex.tex.to_vec)

    def test_dynamic_import_mechanism(self):
        """Test that the dynamic import mechanism works correctly."""
        import scitex.tex
        
        # Check that functions are available after dynamic import
        assert hasattr(scitex.tex, 'preview')
        assert hasattr(scitex.tex, 'to_vec')
        
        # Check that cleanup variables are not present
        assert not hasattr(scitex.tex, 'os')
        assert not hasattr(scitex.tex, 'importlib')
        assert not hasattr(scitex.tex, 'inspect')
        assert not hasattr(scitex.tex, 'current_dir')

    def test_to_vec_basic_functionality(self):
        """Test basic to_vec functionality."""
        from scitex.tex import to_vec
        
        # Test simple vector
        result = to_vec("AB")
        expected = "\\overrightarrow{\\mathrm{AB}}"
        assert result == expected

    def test_to_vec_single_character(self):
        """Test to_vec with single character."""
        from scitex.tex import to_vec
        
        result = to_vec("v")
        expected = "\\overrightarrow{\\mathrm{v}}"
        assert result == expected

    def test_to_vec_multiple_characters(self):
        """Test to_vec with multiple characters."""
        from scitex.tex import to_vec
        
        result = to_vec("velocity")
        expected = "\\overrightarrow{\\mathrm{velocity}}"
        assert result == expected

    def test_to_vec_with_numbers(self):
        """Test to_vec with numbers in string."""
        from scitex.tex import to_vec
        
        result = to_vec("v1")
        expected = "\\overrightarrow{\\mathrm{v1}}"
        assert result == expected
        
        result2 = to_vec("A123")
        expected2 = "\\overrightarrow{\\mathrm{A123}}"
        assert result2 == expected2

    def test_to_vec_with_special_characters(self):
        """Test to_vec with special characters."""
        from scitex.tex import to_vec
        
        # Test with underscore (common in LaTeX)
        result = to_vec("v_max")
        expected = "\\overrightarrow{\\mathrm{v_max}}"
        assert result == expected

    def test_to_vec_empty_string(self):
        """Test to_vec with empty string."""
        from scitex.tex import to_vec
        
        result = to_vec("")
        expected = "\\overrightarrow{\\mathrm{}}"
        assert result == expected

    def test_to_vec_latex_special_chars(self):
        """Test to_vec with LaTeX special characters."""
        from scitex.tex import to_vec
        
        # Test with characters that might need escaping in LaTeX
        result = to_vec("F_net")
        expected = "\\overrightarrow{\\mathrm{F_net}}"
        assert result == expected

    def test_to_vec_return_type(self):
        """Test that to_vec returns string."""
        from scitex.tex import to_vec
        
        result = to_vec("test")
        assert isinstance(result, str)
        assert result.startswith("\\overrightarrow")
        assert "\\mathrm{test}" in result

    def test_preview_basic_functionality(self):
        """Test basic preview functionality with mocked matplotlib."""
        from scitex.tex import preview
        
        # Mock the matplotlib and subplots dependencies
        with patch('scitex.plt.subplots') as mock_subplots:
            # Mock the return values
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with simple LaTeX strings
            tex_strings = ["x^2", "\\sum_{i=1}^n i"]
            result = preview(tex_strings)
            
            # Check that subplots was called
            mock_subplots.assert_called_once()
            
            # Check that we get a figure-like object back
            assert result is not None

    def test_preview_single_string(self):
        """Test preview with single LaTeX string."""
        from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with single string
            tex_strings = ["\\alpha + \\beta"]
            result = preview(tex_strings)
            
            mock_subplots.assert_called_once()
            assert result is not None

    def test_preview_multiple_strings(self):
        """Test preview with multiple LaTeX strings."""
        from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with multiple strings
            tex_strings = ["x^2", "y=mx+b", "\\int_0^1 x dx", "\\sqrt{2}"]
            result = preview(tex_strings)
            
            mock_subplots.assert_called_once()
            assert result is not None

    def test_preview_empty_list(self):
        """Test preview with empty list."""
        from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with empty list
            tex_strings = []
            result = preview(tex_strings)
            
            # Should still call subplots
            mock_subplots.assert_called_once()
            assert result is not None

    def test_preview_complex_latex(self):
        """Test preview with complex LaTeX expressions."""
        from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with complex LaTeX
            tex_strings = [
                "\\frac{\\partial f}{\\partial x}",
                "\\sum_{i=1}^{\\infty} \\frac{1}{n^2}",
                "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}"
            ]
            result = preview(tex_strings)
            
            mock_subplots.assert_called_once()
            assert result is not None

    def test_preview_with_numpy_dependency(self):
        """Test that preview function can handle numpy arrays if needed."""
        from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            with patch('scitex.tex._preview.np') as mock_np:
                mock_fig = MagicMock()
                mock_axes = MagicMock()
                mock_subplots.return_value = (mock_fig, mock_axes)
                
                tex_strings = ["x^2"]
                result = preview(tex_strings)
                
                # numpy should be available as it's imported
                assert mock_np is not None
                mock_subplots.assert_called_once()

    def test_function_docstrings(self):
        """Test that imported functions have docstrings."""
        from scitex.tex import preview, to_vec
        
        assert hasattr(preview, '__doc__')
        assert hasattr(to_vec, '__doc__')
        
        # Check that docstrings contain useful information
        assert preview.__doc__ is not None
        assert to_vec.__doc__ is not None
        assert 'LaTeX' in preview.__doc__ or 'latex' in preview.__doc__.lower()
        assert 'vector' in to_vec.__doc__.lower()

    def test_function_signatures(self):
        """Test function signatures."""
        from scitex.tex import preview, to_vec
        import inspect
        
        # Test to_vec signature
        to_vec_sig = inspect.signature(to_vec)
        to_vec_params = list(to_vec_sig.parameters.keys())
        assert len(to_vec_params) == 1
        assert 'v_str' in to_vec_params or any('str' in param for param in to_vec_params)
        
        # Test preview signature
        preview_sig = inspect.signature(preview)
        preview_params = list(preview_sig.parameters.keys())
        assert len(preview_params) >= 1
        # Should accept a list parameter
        assert any('list' in param or 'tex' in param for param in preview_params)

    def test_to_vec_latex_validity(self):
        """Test that to_vec produces valid LaTeX syntax."""
        from scitex.tex import to_vec
        
        test_cases = ["x", "AB", "force", "v1", "acceleration"]
        
        for case in test_cases:
            result = to_vec(case)
            
            # Check LaTeX syntax validity
            assert result.startswith("\\overrightarrow{")
            assert result.endswith("}")
            assert "\\mathrm{" in result
            assert case in result
            
            # Check proper nesting
            brace_count = result.count("{") - result.count("}")
            assert brace_count == 0, f"Unbalanced braces in: {result}"

    def test_tex_module_integration(self):
        """Test integration between tex module functions."""
        from scitex.tex import to_vec, preview
        
        # Create vector notation
        vector_latex = to_vec("velocity")
        
        # Use it in preview (mocked)
        with patch('scitex.plt.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_axes = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Should be able to preview the vector LaTeX
            result = preview([vector_latex])
            
            assert result is not None
            mock_subplots.assert_called_once()

    def test_tex_error_handling(self):
        """Test error handling in tex functions."""
        from scitex.tex import to_vec
        
        # to_vec should handle various inputs without crashing
        edge_cases = ["", " ", "123", "!@#", "very_long_vector_name_with_lots_of_characters"]
        
        for case in edge_cases:
            try:
                result = to_vec(case)
                assert isinstance(result, str)
                assert "\\overrightarrow" in result
            except Exception as e:
                pytest.fail(f"to_vec failed on input '{case}': {e}")

    def test_tex_module_mathematical_context(self):
        """Test tex module in mathematical contexts."""
        from scitex.tex import to_vec
        
        # Common physics vectors
        physics_vectors = ["F", "v", "a", "p", "r", "E", "B"]
        
        for vector in physics_vectors:
            result = to_vec(vector)
            
            # Should produce standard LaTeX vector notation
            expected_pattern = f"\\overrightarrow{{\\mathrm{{{vector}}}}}"
            assert result == expected_pattern


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
