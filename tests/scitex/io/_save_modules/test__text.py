#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:56:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__text.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__text.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for text file saving functionality
"""

import os
import tempfile
import pytest
from pathlib import Path

from scitex.io._save_modules import save_text


class TestSaveText:
    """Test suite for save_text function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_simple_string(self):
        """Test saving simple string"""
        text = "Hello, World!"
        save_text(text, self.test_file)
        
        assert os.path.exists(self.test_file)
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert content == text

    def test_save_multiline_string(self):
        """Test saving multiline string"""
        text = """Line 1
Line 2
Line 3
Line 4"""
        save_text(text, self.test_file)
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert content == text

    def test_save_with_special_characters(self):
        """Test saving text with special characters"""
        text = "Special chars: äöü €¥£ → ← ↑ ↓ 你好世界 😊"
        save_text(text, self.test_file)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == text

    def test_save_empty_string(self):
        """Test saving empty string"""
        save_text("", self.test_file)
        
        assert os.path.exists(self.test_file)
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert content == ""

    def test_save_with_newlines(self):
        """Test saving text with various newline types"""
        text = "Line 1\nLine 2\r\nLine 3\rLine 4"
        save_text(text, self.test_file)
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        # Content should preserve the exact newlines
        assert content == text

    def test_save_large_text(self):
        """Test saving large text content"""
        # Generate large text
        lines = [f"This is line {i} of a large text file." for i in range(10000)]
        text = "\n".join(lines)
        
        save_text(text, self.test_file)
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        assert content == text
        assert content.count('\n') == 9999

    def test_save_with_encoding(self):
        """Test saving with specific encoding"""
        text = "Testing encoding: ñáéíóú"
        save_text(text, self.test_file, encoding='utf-8')
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == text

    def test_save_json_formatted_text(self):
        """Test saving JSON-formatted text"""
        import json
        data = {"name": "test", "value": 42, "nested": {"key": "value"}}
        text = json.dumps(data, indent=2)
        
        save_text(text, self.test_file)
        
        with open(self.test_file, 'r') as f:
            content = f.read()
        
        # Should be valid JSON
        loaded = json.loads(content)
        assert loaded == data

    def test_save_code_snippet(self):
        """Test saving code snippet with proper formatting"""
        code = '''def hello_world():
    """Print hello world."""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_text.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:17:12 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_text.py
# 
# 
# def _save_text(obj, spath):
#     """
#     Save text content to a file.
#     
#     Parameters
#     ----------
#     obj : str
#         The text content to save.
#     spath : str
#         Path where the text file will be saved.
#         
#     Returns
#     -------
#     None
#     """
#     with open(spath, "w") as file:
#         file.write(obj)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_text.py
# --------------------------------------------------------------------------------
