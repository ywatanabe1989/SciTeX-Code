#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-03 08:27:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__markdown.py

"""Tests for Markdown file loading functionality.

This module tests the Markdown loading functionality including the _load_markdown
and load_markdown functions with support for HTML and plain text conversion.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, Mock, mock_open


class TestLoadMarkdown:
    """Test the _load_markdown function."""

    def test_load_markdown_basic_plain_text(self):
        """Test loading basic Markdown file as plain text."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = """# Test Header

This is a paragraph.

- Item 1
- Item 2

## Subheader

More content here."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            loaded_content = _load_markdown(temp_path)
            assert isinstance(loaded_content, str)
            assert "Test Header" in loaded_content
            assert "Item 1" in loaded_content
            assert "More content" in loaded_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_html_output(self):
        """Test loading Markdown file as HTML."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = """# Test Header

This is a **bold** paragraph with *italic* text.

- Item 1
- Item 2"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            loaded_content = _load_markdown(temp_path, style="html")
            assert isinstance(loaded_content, str)
            assert "<h1>" in loaded_content
            assert "<strong>" in loaded_content
            assert "<em>" in loaded_content
            assert "<ul>" in loaded_content
            assert "<li>" in loaded_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_empty_file(self):
        """Test loading empty Markdown file."""
        from scitex.io._load_modules import _load_markdown
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            loaded_content = _load_markdown(temp_path)
            # html2text adds newlines even for empty content
            assert loaded_content == "\n\n"
        finally:
            os.unlink(temp_path)

    def test_load_markdown_invalid_style(self):
        """Test loading Markdown with invalid style option."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid style option"):
                _load_markdown(temp_path, style="invalid")
        finally:
            os.unlink(temp_path)

    def test_load_markdown_nonexistent_file(self):
        """Test loading non-existent Markdown file."""
        from scitex.io._load_modules import _load_markdown
        
        with pytest.raises(FileNotFoundError):
            _load_markdown("nonexistent_file.md")

    def test_load_markdown_complex_content(self):
        """Test loading complex Markdown content."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = """# Main Title

## Section 1

This is a paragraph with **bold** and *italic* text.

### Subsection

Here's a [link](https://example.com) and some `inline code`.

```python
def hello():
    print("Hello, World!")
```

#### Lists

1. Ordered item 1
2. Ordered item 2
   - Nested unordered item
   - Another nested item

> This is a blockquote
> spanning multiple lines

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

---

Final paragraph."""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Test HTML output
            html_content = _load_markdown(temp_path, style="html")
            assert "<h1>" in html_content
            assert "<h2>" in html_content
            assert "<code>" in html_content
            assert "<blockquote>" in html_content
            # Note: Without table extension, markdown renders tables as paragraphs
            assert "Column 1" in html_content
            assert "Cell 1" in html_content
            
            # Test plain text output
            text_content = _load_markdown(temp_path, style="plain_text")
            assert "Main Title" in text_content
            assert "Section 1" in text_content
            assert "hello" in text_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_with_kwargs(self):
        """Test that _load_markdown accepts kwargs parameter."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Should not raise error with additional kwargs
            result = _load_markdown(temp_path, custom_arg=True, another_arg="test")
            assert isinstance(result, str)
        finally:
            os.unlink(temp_path)

    def test_load_markdown_special_characters(self):
        """Test loading Markdown with special characters."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = """# Título con acentos

Contenido con caracteres especiales: ñáéíóú

- Elementos con símbolos: €, ©, ®
- Emojis: 🚀 🎉 ⭐

`código con tildes: función()`"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            loaded_content = _load_markdown(temp_path)
            assert "Título" in loaded_content
            assert "ñáéíóú" in loaded_content
            assert "función" in loaded_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_function_signature(self):
        """Test that _load_markdown has correct function signature."""
        from scitex.io._load_modules import _load_markdown
        import inspect
        
        sig = inspect.signature(_load_markdown)
        params = list(sig.parameters.keys())
        assert 'lpath_md' in params
        assert 'style' in params
        assert 'kwargs' in params or len([p for p in sig.parameters.values() if p.kind == p.VAR_KEYWORD]) > 0

    def test_load_markdown_docstring(self):
        """Test that _load_markdown has comprehensive docstring."""
        from scitex.io._load_modules import _load_markdown
        
        assert _load_markdown.__doc__ is not None
        assert len(_load_markdown.__doc__.strip()) > 100
        assert 'Markdown' in _load_markdown.__doc__
        assert 'Parameters' in _load_markdown.__doc__
        assert 'Returns' in _load_markdown.__doc__

    def test_load_markdown_default_style(self):
        """Test that default style is plain_text."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = "# Test **bold**"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Call without style parameter
            result_default = _load_markdown(temp_path)
            # Call with explicit plain_text style
            result_explicit = _load_markdown(temp_path, style="plain_text")
            
            # Both should be equivalent
            assert result_default == result_explicit
            # Should not contain HTML tags
            assert "<" not in result_default
        finally:
            os.unlink(temp_path)


class TestLoadMarkdownAlternative:
    """Test the load_markdown function (alternative implementation)."""

    def test_load_markdown_alt_basic(self):
        """Test the alternative load_markdown function."""
        from scitex.io._load_modules import load_markdown
        
        md_content = "# Test Header\n\nParagraph content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            loaded_content = load_markdown(temp_path)
            assert isinstance(loaded_content, str)
            assert "Test Header" in loaded_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_alt_html(self):
        """Test alternative load_markdown function with HTML output."""
        from scitex.io._load_modules import load_markdown
        
        md_content = "# Test **bold**"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            html_content = load_markdown(temp_path, style="html")
            assert "<h1>" in html_content
            assert "<strong>" in html_content
        finally:
            os.unlink(temp_path)

    def test_load_markdown_alt_signature(self):
        """Test alternative load_markdown function signature."""
        from scitex.io._load_modules import load_markdown
        import inspect
        
        sig = inspect.signature(load_markdown)
        params = list(sig.parameters.keys())
        assert 'lpath_md' in params
        assert 'style' in params

    def test_load_markdown_alt_docstring(self):
        """Test that alternative load_markdown has docstring."""
        from scitex.io._load_modules import load_markdown
        
        assert load_markdown.__doc__ is not None
        assert 'Markdown' in load_markdown.__doc__


class TestMarkdownDependencies:
    """Test Markdown processing dependencies and edge cases."""

    @patch('markdown.markdown')
    def test_markdown_conversion_mocked(self, mock_markdown_func):
        """Test Markdown conversion with mocked markdown library."""
        from scitex.io._load_modules import _load_markdown
        
        # Mock the markdown conversion function
        mock_markdown_func.return_value = "<h1>Test</h1>"
        
        md_content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            result = _load_markdown(temp_path, style="html")
            assert result == "<h1>Test</h1>"
            mock_markdown_func.assert_called_once_with(md_content)
        finally:
            os.unlink(temp_path)

    @patch('html2text.HTML2Text')
    @patch('markdown.markdown')
    def test_html2text_conversion_mocked(self, mock_markdown_func, mock_html2text_class):
        """Test HTML to text conversion with mocked html2text library."""
        from scitex.io._load_modules import _load_markdown
        
        # Setup mocks
        mock_markdown_func.return_value = "<h1>Test</h1>"
        mock_converter = Mock()
        mock_converter.handle.return_value = "Test Header\n"
        mock_html2text_class.return_value = mock_converter
        
        md_content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            result = _load_markdown(temp_path, style="plain_text")
            assert result == "Test Header\n"
            mock_markdown_func.assert_called_once_with(md_content)
            mock_html2text_class.assert_called_once()
            mock_converter.handle.assert_called_once()
        finally:
            os.unlink(temp_path)

    def test_file_encoding_handling(self):
        """Test handling of different file encodings."""
        from scitex.io._load_modules import _load_markdown
        
        # Test with UTF-8 content
        md_content = "# Tëst wîth spëcîal chàractërs"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            result = _load_markdown(temp_path)
            assert "Tëst" in result
            assert "spëcîal" in result
        finally:
            os.unlink(temp_path)

    def test_large_file_handling(self):
        """Test handling of large Markdown files."""
        from scitex.io._load_modules import _load_markdown
        
        # Create a large Markdown content
        sections = []
        for i in range(50):
            sections.append(f"## Section {i}")
            sections.append(f"This is content for section {i} with **bold** and *italic* text.")
            sections.append("")
        
        md_content = "\n".join(sections)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            result = _load_markdown(temp_path)
            assert "Section 0" in result
            assert "Section 49" in result
            assert len(result) > 1000  # Should be substantial content
        finally:
            os.unlink(temp_path)


class TestMarkdownErrorHandling:
    """Test error handling and edge cases."""

    def test_file_permission_error(self):
        """Test handling of file permission errors."""
        from scitex.io._load_modules import _load_markdown
        
        # Create a file and remove read permissions (on Unix systems)
        md_content = "# Test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Try to remove read permissions (may not work on all systems)
            try:
                os.chmod(temp_path, 0o000)
                with pytest.raises(PermissionError):
                    _load_markdown(temp_path)
            except (OSError, PermissionError):
                # Permission change failed, skip this test
                pass
        finally:
            # Restore permissions and clean up
            try:
                os.chmod(temp_path, 0o644)
                os.unlink(temp_path)
            except (OSError, FileNotFoundError):
                pass

    @patch('builtins.open')
    def test_io_error_handling(self, mock_open_func):
        """Test handling of IO errors during file reading."""
        from scitex.io._load_modules import _load_markdown
        
        # Mock open to raise an IOError
        mock_open_func.side_effect = IOError("Mocked IO error")
        
        with pytest.raises(IOError):
            _load_markdown("test.md")

    def test_markdown_conversion_edge_cases(self):
        """Test edge cases in Markdown conversion."""
        from scitex.io._load_modules import _load_markdown
        
        edge_cases = [
            "",  # Empty content
            "\n\n\n",  # Only whitespace
            "Plain text without markdown",  # No markdown syntax
            "# \n",  # Empty header
            "[broken link]()",  # Malformed link
            "```\ncode block without language\n```",  # Code block without language
        ]
        
        for md_content in edge_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(md_content)
                temp_path = f.name
            
            try:
                # Should not raise exceptions for any edge case
                result_html = _load_markdown(temp_path, style="html")
                result_text = _load_markdown(temp_path, style="plain_text")
                
                assert isinstance(result_html, str)
                assert isinstance(result_text, str)
            finally:
                os.unlink(temp_path)


class TestMarkdownIntegration:
    """Integration tests for complete Markdown processing workflows."""

    def test_markdown_to_html_to_text_conversion(self):
        """Test complete workflow from Markdown to HTML to text."""
        from scitex.io._load_modules import _load_markdown
        
        md_content = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Section

- List item 1
- List item 2

[Link](https://example.com)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Convert to HTML
            html_result = _load_markdown(temp_path, style="html")
            
            # Convert to plain text
            text_result = _load_markdown(temp_path, style="plain_text")
            
            # Verify HTML contains expected tags
            assert "<h1>" in html_result
            assert "<strong>" in html_result
            assert "<em>" in html_result
            assert "<ul>" in html_result
            assert "<a href=" in html_result
            
            # Verify text contains content but no HTML tags
            assert "Main Title" in text_result
            assert "bold" in text_result
            assert "italic" in text_result
            assert "<" not in text_result
            
        finally:
            os.unlink(temp_path)

    def test_both_function_consistency(self):
        """Test that both load_markdown functions produce consistent results."""
        from scitex.io._load_modules import _load_markdown, load_markdown
        
        md_content = "# Test\n\nContent **bold**"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            # Both functions should produce similar results for basic cases
            result1 = _load_markdown(temp_path, style="plain_text")
            result2 = load_markdown(temp_path, style="plain_text")
            
            # Both should contain the same basic content
            assert "Test" in result1
            assert "Test" in result2
            assert "bold" in result1
            assert "bold" in result2
            
        finally:
            os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_markdown.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:55:42 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_markdown.py
# 
# 
# def _load_markdown(lpath_md, style="plain_text", **kwargs):
#     """
#     Load and convert Markdown content from a file.
# 
#     This function reads a Markdown file and converts it to either HTML or plain text format.
# 
#     Parameters:
#     -----------
#     lpath_md : str
#         The path to the Markdown file to be loaded.
#     style : str, optional
#         The output style of the converted content.
#         Options are "html" or "plain_text" (default).
# 
#     Returns:
#     --------
#     str
#         The converted content of the Markdown file, either as HTML or plain text.
# 
#     Raises:
#     -------
#     FileNotFoundError
#         If the specified file does not exist.
#     IOError
#         If there's an error reading the file.
#     ValueError
#         If an invalid style option is provided.
# 
#     Notes:
#     ------
#     This function uses the 'markdown' library to convert Markdown to HTML,
#     and 'html2text' to convert HTML to plain text when necessary.
#     """
#     import html2text
#     import markdown
# 
#     # Load Markdown content from a file
#     with open(lpath_md, "r") as file:
#         markdown_content = file.read()
# 
#     # Convert Markdown to HTML
#     html_content = markdown.markdown(markdown_content)
#     if style == "html":
#         return html_content
#     elif style == "plain_text":
#         text_maker = html2text.HTML2Text()
#         text_maker.ignore_links = True
#         text_maker.bypass_tables = False
#         plain_text = text_maker.handle(html_content)
#         return plain_text
#     else:
#         raise ValueError("Invalid style option. Choose 'html' or 'plain_text'.")
# 
# 
# def load_markdown(lpath_md, style="plain_text"):
#     """
#     Load and convert a Markdown file to either HTML or plain text.
# 
#     Parameters:
#     -----------
#     lpath_md : str
#         The path to the Markdown file.
#     style : str, optional
#         The output style, either "html" or "plain_text" (default).
# 
#     Returns:
#     --------
#     str
#         The converted content of the Markdown file.
#     """
#     import html2text
#     import markdown
# 
#     # Load Markdown content from a file
#     with open(lpath_md, "r") as file:
#         markdown_content = file.read()
# 
#     # Convert Markdown to HTML
#     html_content = markdown.markdown(markdown_content)
#     if style == "html":
#         return html_content
# 
#     elif style == "plain_text":
#         text_maker = html2text.HTML2Text()
#         text_maker.ignore_links = True
#         text_maker.bypass_tables = False
#         plain_text = text_maker.handle(html_content)
# 
#         return plain_text
# 
# 
# # def _load_markdown(lpath):
# #     md_text = StringIO(lpath.read().decode("utf-8"))
# #     html = markdown.markdown(md_text.read())
# #     return html
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_markdown.py
# --------------------------------------------------------------------------------
