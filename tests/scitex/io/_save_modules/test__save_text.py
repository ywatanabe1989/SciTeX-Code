#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31"
# File: test__save_text.py

"""Tests for scitex.io._save_text module."""

import os
import tempfile
from pathlib import Path

import pytest


class TestSaveTextBasic:
    """Test basic text saving functionality."""

    def test_save_simple_text(self):
        """Test saving simple text string."""
from scitex.io import _save_text

        test_text = "Hello, World!"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.txt")
            _save_text(test_text, output_path)

            # Verify file exists and content is correct
            assert os.path.exists(output_path)
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text

    def test_save_multiline_text(self):
        """Test saving multiline text."""
from scitex.io import _save_text

        test_text = """Line 1
Line 2
Line 3
Final line"""

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "multiline.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text
            assert content.count("\n") == 3

    def test_save_empty_string(self):
        """Test saving empty string."""
from scitex.io import _save_text

        test_text = ""

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty.txt")
            _save_text(test_text, output_path)

            # Verify file exists but is empty
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) == 0
            with open(output_path, "r") as f:
                content = f.read()
            assert content == ""

    def test_save_text_with_special_characters(self):
        """Test saving text with special characters."""
from scitex.io import _save_text

        test_text = 'Special chars: !@#$%^&*()_+{}[]|\\:";<>?,./~`'

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "special.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text


class TestSaveTextUnicode:
    """Test Unicode text saving functionality."""

    def test_save_unicode_text(self):
        """Test saving Unicode text."""
from scitex.io import _save_text

        test_text = "Unicode: 你好世界 🌍 Café résumé naïve"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "unicode.txt")
            _save_text(test_text, output_path)

            # Verify content (file opened with UTF-8 by default)
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == test_text

    def test_save_emoji_text(self):
        """Test saving text with emojis."""
from scitex.io import _save_text

        test_text = "Emojis: 😀😃😄😁😆😅🤣😂🙂🙃😉😊"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "emoji.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == test_text

    def test_save_mixed_language_text(self):
        """Test saving text with multiple languages."""
from scitex.io import _save_text

        test_text = """English: Hello
Chinese: 你好
Japanese: こんにちは
Korean: 안녕하세요
Arabic: مرحبا
Russian: Привет"""

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "multilang.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == test_text


class TestSaveTextPaths:
    """Test different path formats and directory handling."""

    def test_save_with_nested_directory(self):
        """Test saving to nested directory path."""
from scitex.io import _save_text

        test_text = "Nested directory test"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested path (directories must exist)
            nested_dir = os.path.join(tmpdir, "level1", "level2")
            os.makedirs(nested_dir)
            output_path = os.path.join(nested_dir, "nested.txt")

            _save_text(test_text, output_path)

            # Verify file exists in nested location
            assert os.path.exists(output_path)
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text

    def test_save_with_pathlib_path(self):
        """Test saving with pathlib Path object."""
from scitex.io import _save_text

        test_text = "Pathlib test"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "pathlib_test.txt"
            _save_text(test_text, str(output_path))

            # Verify file exists
            assert output_path.exists()
            content = output_path.read_text()
            assert content == test_text

    def test_overwrite_existing_file(self):
        """Test overwriting an existing file."""
from scitex.io import _save_text

        original_text = "Original content"
        new_text = "New content that replaces the original"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "overwrite.txt")

            # First save
            _save_text(original_text, output_path)

            # Verify original content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == original_text

            # Overwrite with new content
            _save_text(new_text, output_path)

            # Verify new content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == new_text


class TestSaveTextContent:
    """Test various content types and formats."""

    def test_save_long_text(self):
        """Test saving very long text."""
from scitex.io import _save_text

        # Create a long text (1MB)
        test_text = "A" * 1024 * 1024

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "long.txt")
            _save_text(test_text, output_path)

            # Verify file size and content
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) == len(test_text)
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text

    def test_save_json_like_text(self):
        """Test saving JSON-formatted text."""
from scitex.io import _save_text

        test_text = """{
    "name": "test",
    "value": 123,
    "nested": {
        "key": "value"
    }
}"""

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "json_like.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text

    def test_save_csv_like_text(self):
        """Test saving CSV-formatted text."""
from scitex.io import _save_text

        test_text = """header1,header2,header3
value1,value2,value3
data1,data2,data3"""

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "csv_like.txt")
            _save_text(test_text, output_path)

            # Verify content
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text

    def test_save_text_with_tabs(self):
        """Test saving text with tab characters."""
from scitex.io import _save_text

        test_text = "Column1\tColumn2\tColumn3\nData1\tData2\tData3"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "tabs.txt")
            _save_text(test_text, output_path)

            # Verify content preserves tabs
            with open(output_path, "r") as f:
                content = f.read()
            assert content == test_text
            assert "\t" in content


class TestSaveTextErrorHandling:
    """Test error handling scenarios."""

    def test_save_to_nonexistent_directory(self):
        """Test saving to a directory that doesn't exist."""
from scitex.io import _save_text

        test_text = "This should fail"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to save to non-existent directory
            output_path = os.path.join(tmpdir, "does_not_exist", "file.txt")

            # Should raise FileNotFoundError
            with pytest.raises(FileNotFoundError):
                _save_text(test_text, output_path)

    def test_save_non_string_object(self):
        """Test saving non-string objects (should fail)."""
from scitex.io import _save_text

        # Try to save various non-string objects
        non_string_objects = [
            123,  # integer
            45.67,  # float
            [1, 2, 3],  # list
            {"key": "value"},  # dict
            None,  # None
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for obj in non_string_objects:
                output_path = os.path.join(tmpdir, f"test_{type(obj).__name__}.txt")

                # Should raise TypeError when trying to write non-string
                with pytest.raises(TypeError):
                    _save_text(obj, output_path)

    def test_save_to_readonly_file(self):
        """Test saving to a read-only file."""
from scitex.io import _save_text

        test_text = "This should fail"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "readonly.txt")

            # Create a file and make it read-only
            with open(output_path, "w") as f:
                f.write("Original")
            os.chmod(output_path, 0o444)  # Read-only

            # Should raise PermissionError
            with pytest.raises(PermissionError):
                _save_text(test_text, output_path)

            # Cleanup: restore write permission
            os.chmod(output_path, 0o644)


class TestSaveTextIntegration:
    """Test integration scenarios."""

    def test_round_trip_save_load(self):
        """Test saving and loading text maintains integrity."""
from scitex.io import _save_text

        test_texts = [
            "Simple text",
            "Multi\nline\ntext",
            "Unicode: 你好 🌍",
            "Special: <>&\"'",
            "\tTabbed\ttext\t",
            "",  # empty
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for i, text in enumerate(test_texts):
                output_path = os.path.join(tmpdir, f"test_{i}.txt")

                # Save
                _save_text(text, output_path)

                # Load and verify
                with open(output_path, "r", encoding="utf-8") as f:
                    loaded = f.read()
                assert loaded == text

    def test_save_multiple_files_same_directory(self):
        """Test saving multiple files to same directory."""
from scitex.io import _save_text

        files = {
            "file1.txt": "Content of file 1",
            "file2.txt": "Content of file 2",
            "file3.txt": "Content of file 3",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save all files
            for filename, content in files.items():
                output_path = os.path.join(tmpdir, filename)
                _save_text(content, output_path)

            # Verify all files exist with correct content
            for filename, expected_content in files.items():
                file_path = os.path.join(tmpdir, filename)
                assert os.path.exists(file_path)
                with open(file_path, "r") as f:
                    content = f.read()
                assert content == expected_content


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
