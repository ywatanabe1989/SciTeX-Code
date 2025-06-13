import os
import tempfile
from pathlib import Path
import shutil

import pytest

from scitex.gen import symlink


class TestSymlinkBasic:
    """Test basic symlink functionality."""

    def test_create_simple_symlink(self, tmp_path):
        """Test creating a simple symbolic link."""
        # Create a target file
        target = tmp_path / "target.txt"
        target.write_text("Hello World")

        # Create symlink
        link = tmp_path / "link.txt"

        # Capture output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            symlink(str(target), str(link))
        finally:
            sys.stdout = old_stdout

        # Check symlink exists and points to target
        assert link.is_symlink()
        assert link.resolve() == target.resolve()
        assert link.read_text() == "Hello World"

        # Check output message
        output = buffer.getvalue()
        assert "Symlink was created" in output
        assert str(link) in output

    def test_symlink_to_directory(self, tmp_path):
        """Test creating symlink to a directory."""
        # Create target directory with content
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        (target_dir / "file1.txt").write_text("File 1")
        (target_dir / "file2.txt").write_text("File 2")

        # Create symlink
        link_dir = tmp_path / "link_dir"
        symlink(str(target_dir), str(link_dir))

        # Check symlink works
        assert link_dir.is_symlink()
        assert link_dir.is_dir()
        assert (link_dir / "file1.txt").read_text() == "File 1"
        assert (link_dir / "file2.txt").read_text() == "File 2"

    def test_relative_path_calculation(self, tmp_path):
        """Test that symlinks use relative paths."""
        # Create nested structure
        (tmp_path / "a" / "b").mkdir(parents=True)
        (tmp_path / "x" / "y").mkdir(parents=True)

        # Create target
        target = tmp_path / "a" / "b" / "target.txt"
        target.write_text("Target content")

        # Create symlink in different directory
        link = tmp_path / "x" / "y" / "link.txt"
        symlink(str(target), str(link))

        # Check that relative path is used
        link_target = os.readlink(str(link))
        assert not os.path.isabs(link_target)
        assert link_target == "../../../a/b/target.txt"

    def test_symlink_in_same_directory(self, tmp_path):
        """Test creating symlink in the same directory as target."""
        target = tmp_path / "target.txt"
        target.write_text("Same dir")

        link = tmp_path / "link.txt"
        symlink(str(target), str(link))

        # When in same directory, relative path should be simple
        link_target = os.readlink(str(link))
        assert link_target == "target.txt"


class TestSymlinkForceOption:
    """Test symlink force option functionality."""

    def test_force_removes_existing_file(self, tmp_path):
        """Test that force=True removes existing file."""
        target = tmp_path / "target.txt"
        target.write_text("Target content")

        # Create existing file at link location
        link = tmp_path / "link.txt"
        link.write_text("Existing content")

        # Without force, should raise error
        with pytest.raises(FileExistsError):
            symlink(str(target), str(link), force=False)

        # With force, should succeed
        symlink(str(target), str(link), force=True)

        assert link.is_symlink()
        assert link.read_text() == "Target content"

    def test_force_removes_existing_symlink(self, tmp_path):
        """Test that force=True removes existing symlink."""
        target1 = tmp_path / "target1.txt"
        target1.write_text("Target 1")

        target2 = tmp_path / "target2.txt"
        target2.write_text("Target 2")

        link = tmp_path / "link.txt"

        # Create initial symlink
        symlink(str(target1), str(link))
        assert link.read_text() == "Target 1"

        # Force create new symlink
        symlink(str(target2), str(link), force=True)
        assert link.read_text() == "Target 2"

    def test_force_with_nonexistent_link(self, tmp_path):
        """Test that force=True works when link doesn't exist."""
        target = tmp_path / "target.txt"
        target.write_text("Content")

        link = tmp_path / "link.txt"

        # Should work fine even if file doesn't exist
        symlink(str(target), str(link), force=True)
        assert link.is_symlink()

    def test_force_does_not_remove_directory(self, tmp_path):
        """Test that force=True fails on existing directory."""
        target = tmp_path / "target.txt"
        target.write_text("Content")

        # Create directory at link location
        link_dir = tmp_path / "link_dir"
        link_dir.mkdir()

        # Force should fail on directory (os.remove doesn't work on dirs)
        with pytest.raises(OSError):
            symlink(str(target), str(link_dir), force=True)


class TestSymlinkErrorCases:
    """Test error handling in symlink function."""

    def test_nonexistent_target(self, tmp_path):
        """Test symlink to nonexistent target (should still work)."""
        # Note: Unix allows creating symlinks to nonexistent targets
        target = tmp_path / "nonexistent.txt"
        link = tmp_path / "link.txt"

        # Should create broken symlink
        symlink(str(target), str(link))

        assert link.is_symlink()
        assert not link.exists()  # Broken symlink

    def test_existing_link_without_force(self, tmp_path):
        """Test error when link exists and force=False."""
        target = tmp_path / "target.txt"
        target.write_text("Content")

        link = tmp_path / "link.txt"
        link.write_text("Existing")

        with pytest.raises(FileExistsError):
            symlink(str(target), str(link), force=False)

    def test_invalid_link_path(self, tmp_path):
        """Test error with invalid link path."""
        target = tmp_path / "target.txt"
        target.write_text("Content")

        # Try to create symlink in non-existent directory
        link = tmp_path / "nonexistent_dir" / "link.txt"

        with pytest.raises(FileNotFoundError):
            symlink(str(target), str(link))

    def test_permission_error(self, tmp_path):
        """Test handling of permission errors."""
        if os.name == "nt":
            pytest.skip("Permission test not applicable on Windows")

        target = tmp_path / "target.txt"
        target.write_text("Content")

        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)

        try:
            link = readonly_dir / "link.txt"
            with pytest.raises(PermissionError):
                symlink(str(target), str(link))
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)


class TestSymlinkSpecialCases:
    """Test special cases and edge scenarios."""

    def test_symlink_to_symlink(self, tmp_path):
        """Test creating symlink to another symlink."""
        # Create chain: target -> link1 -> link2
        target = tmp_path / "target.txt"
        target.write_text("Original")

        link1 = tmp_path / "link1.txt"
        symlink(str(target), str(link1))

        link2 = tmp_path / "link2.txt"
        symlink(str(link1), str(link2))

        # Both should resolve to original target
        assert link2.read_text() == "Original"
        assert link2.resolve() == target.resolve()

    def test_deep_nested_paths(self, tmp_path):
        """Test symlink with deeply nested paths."""
        # Create deep structure
        deep_path = tmp_path
        for i in range(5):
            deep_path = deep_path / f"level{i}"
        deep_path.mkdir(parents=True)

        target = deep_path / "target.txt"
        target.write_text("Deep content")

        link = tmp_path / "shallow_link.txt"
        symlink(str(target), str(link))

        assert link.read_text() == "Deep content"
        # Check relative path goes down many levels
        link_target = os.readlink(str(link))
        assert link_target.count("/") >= 5

    def test_unicode_filenames(self, tmp_path):
        """Test symlink with unicode filenames."""
        target = tmp_path / "target_文件.txt"
        target.write_text("Unicode content")

        link = tmp_path / "link_链接.txt"
        symlink(str(target), str(link))

        assert link.is_symlink()
        assert link.read_text() == "Unicode content"

    def test_spaces_in_paths(self, tmp_path):
        """Test symlink with spaces in paths."""
        target_dir = tmp_path / "dir with spaces"
        target_dir.mkdir()
        target = target_dir / "file with spaces.txt"
        target.write_text("Spaced content")

        link = tmp_path / "link with spaces.txt"
        symlink(str(target), str(link))

        assert link.read_text() == "Spaced content"


class TestSymlinkOutput:
    """Test output messages from symlink function."""

    def test_output_format(self, tmp_path, capsys):
        """Test the format of output messages."""
        target = tmp_path / "target.txt"
        target.write_text("Content")

        link = tmp_path / "link.txt"

        # Clear any previous output
        capsys.readouterr()

        symlink(str(target), str(link))

        captured = capsys.readouterr()
        output = captured.out

        # Check output contains expected elements
        assert "Symlink was created:" in output
        assert str(link) in output
        assert "->" in output
        assert "target.txt" in output

    def test_output_shows_relative_path(self, tmp_path, capsys):
        """Test that output shows the relative path used."""
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()

        target = tmp_path / "a" / "target.txt"
        target.write_text("Content")

        link = tmp_path / "b" / "link.txt"

        capsys.readouterr()  # Clear
        symlink(str(target), str(link))

        output = capsys.readouterr().out
        # Should show relative path
        assert "../a/target.txt" in output


class TestSymlinkCrossPlatform:
    """Test cross-platform compatibility."""

    @pytest.mark.skipif(os.name == "nt", reason="Unix-specific test")
    def test_unix_symlink_properties(self, tmp_path):
        """Test Unix-specific symlink properties."""
        target = tmp_path / "target.txt"
        target.write_text("Unix test")

        link = tmp_path / "link.txt"
        symlink(str(target), str(link))

        # Check it's actually a symlink (not a copy)
        assert os.path.islink(str(link))

        # Modifying through symlink should modify target
        link.write_text("Modified")
        assert target.read_text() == "Modified"

    def test_path_separator_handling(self, tmp_path):
        """Test handling of different path separators."""
        target = tmp_path / "target.txt"
        target.write_text("Sep test")

        # Use forward slashes even on Windows
        link_path = str(tmp_path) + "/link.txt"
        symlink(str(target), link_path)

        link = Path(link_path)
        assert link.is_symlink()
        assert link.read_text() == "Sep test"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_symlink.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 13:29:31 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_symlink.py
#
# import os
# from ..str._color_text import color_text
#
#
# def symlink(tgt, src, force=False):
#     """Create a symbolic link.
#
#     This function creates a symbolic link from the target to the source.
#     If the force parameter is True, it will remove any existing file at
#     the source path before creating the symlink.
#
#     Parameters
#     ----------
#     tgt : str
#         The target path (the file or directory to be linked to).
#     src : str
#         The source path (where the symbolic link will be created).
#     force : bool, optional
#         If True, remove the existing file at the src path before creating
#         the symlink (default is False).
#
#     Returns
#     -------
#     None
#
#     Raises
#     ------
#     OSError
#         If the symlink creation fails.
#
#     Example
#     -------
#     >>> symlink('/path/to/target', '/path/to/link')
#     >>> symlink('/path/to/target', '/path/to/existing_file', force=True)
#     """
#     if force:
#         try:
#             os.remove(src)
#         except FileNotFoundError:
#             pass
#
#     # Calculate the relative path from src to tgt
#     src_dir = os.path.dirname(src)
#     relative_tgt = os.path.relpath(tgt, src_dir)
#
#     os.symlink(relative_tgt, src)
#     print(color_text(f"\nSymlink was created: {src} -> {relative_tgt}\n", c="yellow"))
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_symlink.py
# --------------------------------------------------------------------------------
