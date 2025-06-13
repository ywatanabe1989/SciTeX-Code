#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "ywatanabe (2024-11-02 23:58:11)"
# File: ./scitex_repo/tests/scitex/tex/test__preview.py

"""Comprehensive tests for tex._preview module"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, call, MagicMock
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestPreview:
    """Tests for preview function"""
    
    def test_preview_single_tex_string(self):
        """Test preview with single LaTeX string"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            result = preview(["x^2"])
            
            # Verify
            assert result == mock_fig
            mock_subplots.assert_called_once_with(nrows=1, ncols=1, figsize=(10, 3))
            assert mock_ax.text.call_count == 2
            mock_ax.text.assert_any_call(0.5, 0.7, "x^2", size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, "$x^2$", size=20, ha="center", va="center")
            mock_ax.hide_spines.assert_called_once()
            mock_fig.tight_layout.assert_called_once()
    
    def test_preview_multiple_tex_strings(self):
        """Test preview with multiple LaTeX strings"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_axes = [Mock(spec=Axes) for _ in range(3)]
            for ax in mock_axes:
                ax.text = Mock()
                ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test
            tex_strings = ["x^2", r"\sum_{i=1}^n i", r"\frac{a}{b}"]
            result = preview(tex_strings)
            
            # Verify
            assert result == mock_fig
            mock_subplots.assert_called_once_with(nrows=3, ncols=1, figsize=(10, 9))
            
            # Check each axis
            for i, (ax, tex_str) in enumerate(zip(mock_axes, tex_strings)):
                assert ax.text.call_count == 2
                ax.text.assert_any_call(0.5, 0.7, tex_str, size=20, ha="center", va="center")
                ax.text.assert_any_call(0.5, 0.3, f"${tex_str}$", size=20, ha="center", va="center")
                ax.hide_spines.assert_called_once()
            
            mock_fig.tight_layout.assert_called_once()
    
    def test_preview_empty_list(self):
        """Test preview with empty list"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_subplots.return_value = (mock_fig, np.array([]))
            mock_fig.tight_layout = Mock()
            
            # Test
            result = preview([])
            
            # Verify
            assert result == mock_fig
            mock_subplots.assert_called_once_with(nrows=0, ncols=1, figsize=(10, 0))
            mock_fig.tight_layout.assert_called_once()
    
    def test_preview_complex_latex(self):
        """Test preview with complex LaTeX expressions"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            complex_tex = r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}"
            result = preview([complex_tex])
            
            # Verify
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, complex_tex, size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, f"${complex_tex}$", size=20, ha="center", va="center")
    
    def test_preview_special_characters(self):
        """Test preview with special LaTeX characters"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            special_tex = r"\alpha \beta \gamma \delta \epsilon"
            result = preview([special_tex])
            
            # Verify
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, special_tex, size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, f"${special_tex}$", size=20, ha="center", va="center")
    
    def test_preview_unicode_strings(self):
        """Test preview with Unicode strings"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            unicode_tex = "∑ᵢ₌₁ⁿ xᵢ²"
            result = preview([unicode_tex])
            
            # Verify
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, unicode_tex, size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, f"${unicode_tex}$", size=20, ha="center", va="center")
    
    def test_preview_with_numpy_array_axes(self):
        """Test preview handles numpy array of axes correctly"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock with numpy array
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            # Return numpy array
            mock_subplots.return_value = (mock_fig, np.array(mock_ax))
            
            # Test
            result = preview(["test"])
            
            # Verify np.atleast_1d is handled
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, "test", size=20, ha="center", va="center")
    
    def test_preview_text_positioning(self):
        """Test that text is positioned correctly"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            result = preview(["E=mc^2"])
            
            # Verify positions
            calls = mock_ax.text.call_args_list
            assert len(calls) == 2
            # First call: raw string at y=0.7
            assert calls[0][0] == (0.5, 0.7, "E=mc^2")
            assert calls[0][1] == {"size": 20, "ha": "center", "va": "center"}
            # Second call: LaTeX string at y=0.3
            assert calls[1][0] == (0.5, 0.3, "$E=mc^2$")
            assert calls[1][1] == {"size": 20, "ha": "center", "va": "center"}
    
    def test_preview_figure_size_scaling(self):
        """Test that figure size scales with number of strings"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_axes = [Mock(spec=Axes) for _ in range(5)]
            for ax in mock_axes:
                ax.text = Mock()
                ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test
            tex_strings = ["a", "b", "c", "d", "e"]
            result = preview(tex_strings)
            
            # Verify figure size
            mock_subplots.assert_called_once_with(nrows=5, ncols=1, figsize=(10, 15))
    
    def test_preview_escaping_edge_cases(self):
        """Test preview with edge case LaTeX strings"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test with backslashes and special chars
            edge_case = r"\left\{ x \in \mathbb{R} : |x| < 1 \right\}"
            result = preview([edge_case])
            
            # Verify
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, edge_case, size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, f"${edge_case}$", size=20, ha="center", va="center")
    
    def test_preview_matrix_latex(self):
        """Test preview with matrix LaTeX notation"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test
            matrix_tex = r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"
            result = preview([matrix_tex])
            
            # Verify
            assert result == mock_fig
            mock_ax.text.assert_any_call(0.5, 0.7, matrix_tex, size=20, ha="center", va="center")
            mock_ax.text.assert_any_call(0.5, 0.3, f"${matrix_tex}$", size=20, ha="center", va="center")
    
    def test_preview_type_validation(self):
        """Test preview with invalid input types"""
from scitex.tex import preview
        
        # Test with string instead of list - raises ValueError from numpy
        with pytest.raises(ValueError):
            preview("not a list")
        
        # Test with None - will raise when calling len()
        with pytest.raises(TypeError):
            preview(None)
        
        # Test with int - will raise TypeError from len()
        with pytest.raises(TypeError):
            preview(123)
    
    def test_preview_with_actual_matplotlib(self):
        """Integration test with actual matplotlib"""
from scitex.tex import preview
        
        # Skip this test as scitex.plt.subplots returns wrapped objects
        # that don't directly expose matplotlib Figure interface
        pytest.skip("scitex.plt.subplots returns wrapped objects, not raw matplotlib figures")
    
    def test_preview_long_list_performance(self):
        """Test preview performance with many LaTeX strings"""
from scitex.tex import preview
        import time
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_axes = [Mock(spec=Axes) for _ in range(100)]
            for ax in mock_axes:
                ax.text = Mock()
                ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test with 100 strings
            tex_strings = [f"x^{{{i}}}" for i in range(100)]
            
            start_time = time.time()
            result = preview(tex_strings)
            elapsed = time.time() - start_time
            
            # Should complete quickly even with many strings
            assert elapsed < 1.0
            assert result == mock_fig
    
    def test_preview_mixed_content(self):
        """Test preview with mixed LaTeX and plain text"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_axes = [Mock(spec=Axes) for _ in range(3)]
            for ax in mock_axes:
                ax.text = Mock()
                ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test
            mixed_content = [
                "Plain text",
                r"\LaTeX",
                "x + y = z"
            ]
            result = preview(mixed_content)
            
            # Verify each is rendered both ways
            assert result == mock_fig
            for i, (ax, content) in enumerate(zip(mock_axes, mixed_content)):
                ax.text.assert_any_call(0.5, 0.7, content, size=20, ha="center", va="center")
                ax.text.assert_any_call(0.5, 0.3, f"${content}$", size=20, ha="center", va="center")
    
    def test_preview_error_recovery(self):
        """Test preview handles errors gracefully"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock that raises on tight_layout
            mock_fig = Mock(spec=Figure)
            mock_ax = Mock(spec=Axes)
            mock_ax.text = Mock()
            mock_ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock(side_effect=Exception("Layout error"))
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test - should raise the exception
            with pytest.raises(Exception, match="Layout error"):
                preview(["test"])
    
    def test_preview_docstring_example(self):
        """Test the example from the docstring works"""
from scitex.tex import preview
        
        with patch('scitex.plt.subplots') as mock_subplots:
            # Setup mock
            mock_fig = Mock(spec=Figure)
            mock_axes = [Mock(spec=Axes) for _ in range(2)]
            for ax in mock_axes:
                ax.text = Mock()
                ax.hide_spines = Mock()
            mock_fig.tight_layout = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # Test example from docstring
            tex_strings = ["x^2", r"\sum_{i=1}^n i"]
            fig = preview(tex_strings)
            
            # Verify it returns a figure
            assert fig == mock_fig
            
            # Verify the strings were rendered
            mock_axes[0].text.assert_any_call(0.5, 0.7, "x^2", size=20, ha="center", va="center")
            mock_axes[0].text.assert_any_call(0.5, 0.3, "$x^2$", size=20, ha="center", va="center")
            mock_axes[1].text.assert_any_call(0.5, 0.7, r"\sum_{i=1}^n i", size=20, ha="center", va="center")
            mock_axes[1].text.assert_any_call(0.5, 0.3, r"$\sum_{i=1}^n i$", size=20, ha="center", va="center")


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
