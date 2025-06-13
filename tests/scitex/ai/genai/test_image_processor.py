#!/usr/bin/env python3
"""Tests for image_processor module."""

import pytest
import base64
import numpy as np
from unittest.mock import Mock, MagicMock, patch, mock_open
from io import BytesIO
from PIL import Image as PILImage

from scitex.ai.genai.image_processor import ImageProcessor


class TestImageProcessor:
    """Test cases for ImageProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create an ImageProcessor instance."""
        return ImageProcessor()

    @pytest.fixture
    def sample_image(self):
        """Create a sample PIL Image."""
        return PILImage.new("RGB", (100, 100), color="red")

    @pytest.fixture
    def base64_image(self, sample_image):
        """Create a base64 encoded image."""
        buffer = BytesIO()
        sample_image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def test_init(self, processor):
        """Test initialization."""
        assert processor.supported_formats == {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
        }

    def test_process_image_from_pil(self, processor, sample_image):
        """Test processing a PIL Image."""
        result = processor.process_image(sample_image, max_size=50)

        assert isinstance(result, str)
        # Verify it's valid base64
        base64.b64decode(result)

    def test_process_image_from_bytes(self, processor, sample_image):
        """Test processing image from bytes."""
        buffer = BytesIO()
        sample_image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        result = processor.process_image(image_bytes)
        assert isinstance(result, str)
        base64.b64decode(result)

    def test_process_image_from_base64_string(self, processor, base64_image):
        """Test processing image from base64 string."""
        result = processor.process_image(base64_image)
        assert isinstance(result, str)
        base64.b64decode(result)

    def test_process_image_from_data_url(self, processor, base64_image):
        """Test processing image from data URL."""
        data_url = f"data:image/jpeg;base64,{base64_image}"
        result = processor.process_image(data_url)
        assert isinstance(result, str)
        base64.b64decode(result)

    def test_process_image_with_resize(self, processor):
        """Test image resizing during processing."""
        large_image = PILImage.new("RGB", (1000, 1000), color="blue")
        result = processor.process_image(large_image, max_size=100)

        # Decode and check size
        decoded = base64.b64decode(result)
        resized = PILImage.open(BytesIO(decoded))
        assert max(resized.size) <= 100

    def test_resize_image_landscape(self, processor):
        """Test resizing landscape image."""
        image = PILImage.new("RGB", (200, 100), color="green")
        resized = processor.resize_image(image, 100)

        assert resized.width == 100
        assert resized.height == 50

    def test_resize_image_portrait(self, processor):
        """Test resizing portrait image."""
        image = PILImage.new("RGB", (100, 200), color="green")
        resized = processor.resize_image(image, 100)

        assert resized.width == 50
        assert resized.height == 100

    def test_to_base64_jpeg(self, processor, sample_image):
        """Test converting to base64 JPEG."""
        result = processor.to_base64(sample_image, format="JPEG")
        assert isinstance(result, str)

        # Verify it can be decoded
        decoded = base64.b64decode(result)
        img = PILImage.open(BytesIO(decoded))
        assert img.format == "JPEG"

    def test_to_base64_png(self, processor, sample_image):
        """Test converting to base64 PNG."""
        result = processor.to_base64(sample_image, format="PNG")
        assert isinstance(result, str)

        # Verify it can be decoded
        decoded = base64.b64decode(result)
        img = PILImage.open(BytesIO(decoded))
        assert img.format == "PNG"

    def test_to_base64_rgba_to_jpeg(self, processor):
        """Test converting RGBA image to JPEG."""
        rgba_image = PILImage.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        result = processor.to_base64(rgba_image, format="JPEG")

        # Verify conversion worked
        decoded = base64.b64decode(result)
        img = PILImage.open(BytesIO(decoded))
        assert img.mode == "RGB"

    def test_get_image_info(self, processor, sample_image):
        """Test getting image information."""
        info = processor.get_image_info(sample_image)

        assert info["width"] == 100
        assert info["height"] == 100
        assert info["mode"] == "RGB"
        assert "size_mb" in info
        assert isinstance(info["size_mb"], float)

    def test_validate_image_valid_extension(self, processor):
        """Test image validation with valid extension."""
        with patch("PIL.Image.open") as mock_open:
            mock_img = Mock()
            mock_img.verify.return_value = None
            mock_open.return_value = mock_img

            assert processor.validate_image("test.jpg") is True
            assert processor.validate_image("test.PNG") is True

    def test_validate_image_invalid_extension(self, processor):
        """Test image validation with invalid extension."""
        assert processor.validate_image("test.txt") is False
        assert processor.validate_image("test.pdf") is False

    def test_validate_image_corrupted_file(self, processor):
        """Test image validation with corrupted file."""
        with patch("PIL.Image.open", side_effect=Exception("Corrupted")):
            assert processor.validate_image("test.jpg") is False

    def test_validate_image_non_string_input(self, processor):
        """Test image validation with non-string input."""
        assert processor.validate_image(123) is False
        assert processor.validate_image(None) is False
        assert processor.validate_image(["test.jpg"]) is False

    def test_to_pil_image_unsupported_type(self, processor):
        """Test _to_pil_image with unsupported type."""
        with pytest.raises(ValueError, match="Unsupported image type"):
            processor._to_pil_image(12345)

    @patch("PIL.Image.open")
    def test_process_image_from_file_path(self, mock_open, processor, sample_image):
        """Test processing image from file path."""
        mock_open.return_value = sample_image

        result = processor.process_image("/path/to/image.jpg")
        assert isinstance(result, str)
        mock_open.assert_called_once_with("/path/to/image.jpg")

    def test_repr(self, processor):
        """Test string representation."""
        repr_str = repr(processor)
        assert "ImageProcessor" in repr_str
        assert "supported_formats" in repr_str
