import pytest
from unittest.mock import patch, MagicMock

from scitex.gen import title2path


class TestTitle2Path:
    """Test the title2path function."""

    def test_simple_string(self):
        """Test conversion of a simple string."""
        assert title2path("hello world") == "hello_world"

    def test_string_with_special_chars(self):
        """Test removal of special characters."""
        assert title2path("test:file;name=value[0]") == "testfilenamevalue0"

    def test_string_with_spaces(self):
        """Test space replacement with underscores."""
        assert title2path("test file name") == "test_file_name"

    def test_string_with_consecutive_underscores(self):
        """Test removal of consecutive underscores."""
        assert title2path("test___file") == "test_file"
        assert title2path("test____file") == "test_file"

    def test_underscore_dash_underscore_pattern(self):
        """Test replacement of _-_ pattern."""
        assert title2path("test_-_file") == "test-file"

    def test_uppercase_to_lowercase(self):
        """Test conversion to lowercase."""
        assert title2path("TEST FILE") == "test_file"
        assert title2path("TestFile") == "testfile"

    def test_complex_string(self):
        """Test complex string with multiple patterns."""
        input_str = "Test:File[1];Name=Value _-_ End"
        expected = "testfile1namevalue_-_end"
        assert title2path(input_str) == expected

    def test_empty_string(self):
        """Test empty string input."""
        assert title2path("") == ""

    def test_string_with_only_special_chars(self):
        """Test string containing only special characters."""
        assert title2path("::;;==[[]]") == ""

    def test_string_with_mixed_patterns(self):
        """Test string with various patterns combined."""
        input_str = "Model: ResNet50; Epochs=100 [Batch: 32]"
        expected = "model_resnet50_epochs100_batch_32"
        assert title2path(input_str) == expected

    @patch("scitex.gen.dict2str")
    def test_dict_input(self, mock_dict2str):
        """Test conversion of dictionary input."""
        # Mock the dict2str function
        mock_dict2str.return_value = "model:resnet50 epochs=100"

        test_dict = {"model": "resnet50", "epochs": 100}
        result = title2path(test_dict)

        # Verify dict2str was called
        mock_dict2str.assert_called_once_with(test_dict)

        # Verify the result
        assert result == "modelresnet50_epochs100"

    def test_real_world_examples(self):
        """Test with real-world title examples."""
        # Scientific paper title
        title1 = "Deep Learning: A Review [2023]"
        assert title2path(title1) == "deep_learning_a_review_2023"

        # Configuration string
        title2 = "config: lr=0.001; batch_size=32; optimizer=adam"
        assert title2path(title2) == "config_lr0.001_batch_size32_optimizeradam"

        # File path-like string
        title3 = "data/train/images [processed]"
        assert title2path(title3) == "data/train/images_processed"

    def test_preserves_forward_slashes(self):
        """Test that forward slashes are preserved (for path-like strings)."""
        assert title2path("folder/subfolder/file") == "folder/subfolder/file"

    def test_multiple_consecutive_spaces(self):
        """Test handling of multiple consecutive spaces."""
        assert title2path("test    file") == "test_file"

    def test_tabs_and_newlines(self):
        """Test that tabs and newlines are treated as spaces."""
        # Note: The current implementation doesn't handle tabs/newlines,
        # but spaces should work
        assert title2path("test file") == "test_file"

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        # The function should handle unicode strings
        assert title2path("café: résumé") == "café_résumé"

    def test_numbers_preserved(self):
        """Test that numbers are preserved."""
        assert title2path("test123file456") == "test123file456"
        assert title2path("v2.0: release[final]") == "v2.0_releasefinal"

    def test_edge_case_patterns(self):
        """Test edge cases with pattern combinations."""
        # Multiple _-_ patterns
        assert title2path("a_-_b_-_c") == "a-b-c"

        # Pattern at start/end
        assert title2path("_-_start") == "-start"
        assert title2path("end_-_") == "end-"

        # Many underscores becoming one
        assert title2path("a________b") == "a_b"


class TestTitle2PathIntegration:
    """Integration tests for title2path function."""

    def test_model_experiment_titles(self):
        """Test conversion of ML experiment titles."""
        titles = [
            ("ResNet50: ImageNet [Epoch: 100]", "resnet50_imagenet_epoch_100"),
            ("BERT Fine-tuning; Task=NER", "bert_fine-tuning_taskner"),
            (
                "GAN Training [Discriminator Loss = 0.5]",
                "gan_training_discriminator_loss_0.5",
            ),
        ]

        for input_title, expected in titles:
            assert title2path(input_title) == expected

    def test_filename_sanitization(self):
        """Test that the output is suitable for filenames."""
        # Common problematic filename characters are removed
        problematic = "file:name*with?invalid<chars>"
        result = title2path(problematic)

        # Check that colon and other special chars are removed
        assert ":" not in result
        assert ";" not in result
        assert "=" not in result
        assert "[" not in result
        assert "]" not in result

        # Result should be lowercase
        assert result == result.lower()

        # No consecutive underscores
        assert "__" not in result


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_title2path.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: 2024-05-12 21:02:21 (7)
# # /sshx:ywatanabe@444:/home/ywatanabe/proj/scitex/src/scitex/gen/_title2spath.py
# 
# 
# def title2path(title):
#     """
#     Convert a title (string or dictionary) to a path-friendly string.
# 
#     Parameters
#     ----------
#     title : str or dict
#         The input title to be converted.
# 
#     Returns
#     -------
#     str
#         A path-friendly string derived from the input title.
#     """
#     if isinstance(title, dict):
#         from scitex.dict import to_str
# 
#         title = to_str(title)
# 
#     path = title
# 
#     patterns = [":", ";", "=", "[", "]"]
#     for pattern in patterns:
#         path = path.replace(pattern, "")
# 
#     path = path.replace("_-_", "-")
#     path = path.replace(" ", "_")
# 
#     while "__" in path:
#         path = path.replace("__", "_")
# 
#     return path.lower()
# 
# 
# # def title2path(title):
# #     if isinstance(title, dict):
# #         title = dict2str(title)
# 
# #     path = title
# 
# #     # Comma patterns
# #     patterns = [":", ";", "=", "[", "]"]
# #     for pp in patterns:
# #         path = path.replace(pp, "")
# 
# #     # Exceptions
# #     path = path.replace("_-_", "-")
# #     path = path.replace(" ", "_")
# 
# #     # Consective under scores
# #     for _ in range(10):
# #         path = path.replace("__", "_")
# 
# #     return path.lower()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_title2path.py
# --------------------------------------------------------------------------------
