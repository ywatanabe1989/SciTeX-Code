#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:12:00 (ywatanabe)"
# File: tests/scitex/os/test___init__.py

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import shutil


class TestOsModule:
    """Test suite for scitex.os module."""

    def test_mv_import(self):
        """Test that mv function can be imported from scitex.os."""
        from scitex.os import mv
        
        assert callable(mv)
        assert hasattr(mv, '__call__')

    def test_mv_function_signature(self):
        """Test mv function has correct signature."""
        from scitex.os import mv
        import inspect
        
        sig = inspect.signature(mv)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2
        assert 'src' in params
        assert 'tgt' in params

    def test_module_attributes(self):
        """Test that scitex.os module has expected attributes."""
        import scitex.os
        
        assert hasattr(scitex.os, 'mv')
        assert callable(scitex.os.mv)

    def test_mv_basic_functionality(self):
        """Test basic mv functionality with file moving."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("test content")
            
            # Create target directory
            tgt_dir = Path(temp_dir) / "target"
            
            # Mock print to capture output
            with patch('builtins.print') as mock_print:
                result = mv(str(src_file), str(tgt_dir))
                
                # Check result
                assert result is True
                
                # Check file was moved
                assert not src_file.exists()
                assert (tgt_dir / "source.txt").exists()
                assert (tgt_dir / "source.txt").read_text() == "test content"
                
                # Check print was called
                mock_print.assert_called_once()
                assert "Moved from" in str(mock_print.call_args)

    def test_mv_creates_target_directory(self):
        """Test that mv creates target directory if it doesn't exist."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("test content")
            
            # Target directory that doesn't exist
            tgt_dir = Path(temp_dir) / "new_dir" / "nested_dir"
            assert not tgt_dir.exists()
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                # Check target directory was created
                assert tgt_dir.exists()
                assert tgt_dir.is_dir()
                assert result is True

    def test_mv_file_error_handling(self):
        """Test mv error handling with invalid source."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Non-existent source file
            src_file = Path(temp_dir) / "nonexistent.txt"
            tgt_dir = Path(temp_dir) / "target"
            
            with patch('builtins.print') as mock_print:
                result = mv(str(src_file), str(tgt_dir))
                
                # Should return False on error
                assert result is False
                
                # Should print error message
                mock_print.assert_called()
                error_msg = str(mock_print.call_args)
                assert "Error:" in error_msg

    def test_mv_permission_error(self):
        """Test mv handling of permission errors."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("test content")
            tgt_dir = Path(temp_dir) / "target"
            
            # Mock shutil.move to raise OSError
            with patch('shutil.move', side_effect=OSError("Permission denied")):
                with patch('builtins.print') as mock_print:
                    result = mv(str(src_file), str(tgt_dir))
                    
                    assert result is False
                    mock_print.assert_called()
                    error_msg = str(mock_print.call_args)
                    assert "Error:" in error_msg
                    assert "Permission denied" in error_msg

    def test_mv_with_absolute_paths(self):
        """Test mv with absolute paths."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create source file with absolute path
            src_file = temp_path / "source.txt"
            src_file.write_text("absolute path test")
            
            # Target with absolute path
            tgt_dir = temp_path / "target_abs"
            
            with patch('builtins.print'):
                result = mv(str(src_file.absolute()), str(tgt_dir.absolute()))
                
                assert result is True
                assert not src_file.exists()
                assert (tgt_dir / "source.txt").exists()

    def test_mv_with_relative_paths(self):
        """Test mv with relative paths."""
        from scitex.os import mv
        
        # Change to temporary directory for relative path testing
        original_cwd = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                # Create source file
                src_file = Path("source.txt")
                src_file.write_text("relative path test")
                
                # Target directory
                tgt_dir = "target_rel"
                
                with patch('builtins.print'):
                    result = mv(str(src_file), tgt_dir)
                    
                    assert result is True
                    assert not src_file.exists()
                    assert Path(tgt_dir, "source.txt").exists()
        finally:
            os.chdir(original_cwd)

    def test_mv_overwrites_existing_file(self):
        """Test that mv overwrites existing files in target."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("new content")
            
            # Create target directory with existing file
            tgt_dir = Path(temp_dir) / "target"
            tgt_dir.mkdir()
            existing_file = tgt_dir / "source.txt"
            existing_file.write_text("old content")
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                assert result is True
                assert not src_file.exists()
                assert existing_file.exists()
                # File should be overwritten
                assert existing_file.read_text() == "new content"

    def test_mv_large_file_handling(self):
        """Test mv with large files."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create large-ish file (1MB)
            src_file = Path(temp_dir) / "large.txt"
            large_content = "x" * (1024 * 1024)  # 1MB of 'x'
            src_file.write_text(large_content)
            
            tgt_dir = Path(temp_dir) / "target"
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                assert result is True
                assert not src_file.exists()
                moved_file = tgt_dir / "large.txt"
                assert moved_file.exists()
                assert len(moved_file.read_text()) == len(large_content)

    def test_mv_empty_file(self):
        """Test mv with empty files."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty file
            src_file = Path(temp_dir) / "empty.txt"
            src_file.touch()
            
            tgt_dir = Path(temp_dir) / "target"
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                assert result is True
                assert not src_file.exists()
                moved_file = tgt_dir / "empty.txt"
                assert moved_file.exists()
                assert moved_file.stat().st_size == 0

    def test_mv_special_characters_in_filename(self):
        """Test mv with special characters in filenames."""
        from scitex.os import mv
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file with special characters
            src_file = Path(temp_dir) / "file-with_special.chars[123].txt"
            src_file.write_text("special chars")
            
            tgt_dir = Path(temp_dir) / "target"
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                assert result is True
                assert not src_file.exists()
                moved_file = tgt_dir / "file-with_special.chars[123].txt"
                assert moved_file.exists()
                assert moved_file.read_text() == "special chars"

    def test_mv_preserves_file_content_and_metadata(self):
        """Test that mv preserves file content and basic metadata."""
        from scitex.os import mv
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            src_file = Path(temp_dir) / "test.txt"
            test_content = "content to preserve"
            src_file.write_text(test_content)
            
            # Get original file stats
            original_size = src_file.stat().st_size
            
            tgt_dir = Path(temp_dir) / "target"
            
            with patch('builtins.print'):
                result = mv(str(src_file), str(tgt_dir))
                
                assert result is True
                moved_file = tgt_dir / "test.txt"
                assert moved_file.exists()
                assert moved_file.read_text() == test_content
                assert moved_file.stat().st_size == original_size


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
