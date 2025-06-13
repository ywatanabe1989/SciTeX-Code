#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:25:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/image_processor.py

"""
Handles image processing for multimodal AI inputs.

This module provides image processing functionality including:
- Image resizing to fit token limits
- Base64 encoding for API transmission
- Multiple format support (file path, bytes, PIL Image)
- Format validation
"""

import base64
import io
from typing import Union, Tuple, Optional
from PIL import Image


class ImageProcessor:
    """Processes images for multimodal AI inputs.

    Example
    -------
    >>> processor = ImageProcessor()
    >>> # Process image from file
    >>> base64_str = processor.process_image("path/to/image.jpg", max_size=512)
    >>> print(base64_str[:50])
    /9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBw...

    >>> # Process PIL Image
    >>> from PIL import Image
    >>> img = Image.new('RGB', (100, 100), color='red')
    >>> base64_str = processor.process_image(img)
    """

    def __init__(self):
        """Initialize image processor."""
        self.supported_formats = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def process_image(
        self, image: Union[str, bytes, Image.Image], max_size: int = 512
    ) -> str:
        """Process an image for API transmission.

        Parameters
        ----------
        image : Union[str, bytes, Image.Image]
            Image as file path, bytes, or PIL Image
        max_size : int
            Maximum dimension (width or height) in pixels

        Returns
        -------
        str
            Base64 encoded image string
        """
        # Convert to PIL Image
        pil_image = self._to_pil_image(image)

        # Resize if needed
        if max(pil_image.size) > max_size:
            pil_image = self.resize_image(pil_image, max_size)

        # Convert to base64
        return self.to_base64(pil_image)

    def _to_pil_image(self, image: Union[str, bytes, Image.Image]) -> Image.Image:
        """Convert various image formats to PIL Image.

        Parameters
        ----------
        image : Union[str, bytes, Image.Image]
            Input image in various formats

        Returns
        -------
        Image.Image
            PIL Image object
        """
        if isinstance(image, Image.Image):
            return image

        if isinstance(image, str):
            # Check if it's a base64 string
            if image.startswith("data:image"):
                # Extract base64 data from data URL
                base64_data = image.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            else:
                # Assume it's a file path
                try:
                    return Image.open(image)
                except Exception as e:
                    # Maybe it's already base64 encoded
                    try:
                        image_bytes = base64.b64decode(image)
                        return Image.open(io.BytesIO(image_bytes))
                    except:
                        raise ValueError(f"Could not load image from string: {e}")

        if isinstance(image, bytes):
            return Image.open(io.BytesIO(image))

        raise ValueError(f"Unsupported image type: {type(image)}")

    def resize_image(self, image: Image.Image, max_size: int) -> Image.Image:
        """Resize image to fit within max_size while maintaining aspect ratio.

        Parameters
        ----------
        image : Image.Image
            PIL Image to resize
        max_size : int
            Maximum dimension in pixels

        Returns
        -------
        Image.Image
            Resized PIL Image
        """
        # Calculate new dimensions
        width, height = image.size
        aspect_ratio = width / height

        if width > height:
            new_width = max_size
            new_height = int(max_size / aspect_ratio)
        else:
            new_height = max_size
            new_width = int(max_size * aspect_ratio)

        # Use high-quality resampling
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def to_base64(self, image: Image.Image, format: str = "JPEG") -> str:
        """Convert PIL Image to base64 string.

        Parameters
        ----------
        image : Image.Image
            PIL Image to encode
        format : str
            Output format (JPEG, PNG, etc.)

        Returns
        -------
        str
            Base64 encoded image string
        """
        # Convert RGBA to RGB if saving as JPEG
        if format.upper() == "JPEG" and image.mode in ("RGBA", "LA", "P"):
            # Create a white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode == "RGBA" else None
            )
            image = background

        # Save to bytes buffer
        buffer = io.BytesIO()
        image.save(
            buffer, format=format, quality=95 if format.upper() == "JPEG" else None
        )

        # Encode to base64
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_image_info(self, image: Union[str, bytes, Image.Image]) -> dict:
        """Get information about an image.

        Parameters
        ----------
        image : Union[str, bytes, Image.Image]
            Image to analyze

        Returns
        -------
        dict
            Image information including size, mode, format
        """
        pil_image = self._to_pil_image(image)

        return {
            "width": pil_image.width,
            "height": pil_image.height,
            "mode": pil_image.mode,
            "format": pil_image.format,
            "size_mb": self._estimate_size_mb(pil_image),
        }

    def _estimate_size_mb(self, image: Image.Image) -> float:
        """Estimate image size in megabytes.

        Parameters
        ----------
        image : Image.Image
            PIL Image

        Returns
        -------
        float
            Estimated size in MB
        """
        # Rough estimate based on dimensions and mode
        bytes_per_pixel = len(image.mode)  # Rough estimate
        total_bytes = image.width * image.height * bytes_per_pixel
        return total_bytes / (1024 * 1024)

    def validate_image(self, image_path: str) -> bool:
        """Validate if a file is a supported image format.

        Parameters
        ----------
        image_path : str
            Path to image file

        Returns
        -------
        bool
            True if valid image format
        """
        if not isinstance(image_path, str):
            return False

        # Check file extension
        ext = image_path.lower().split(".")[-1]
        if f".{ext}" not in self.supported_formats:
            return False

        # Try to open the image
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except:
            return False

    def __repr__(self) -> str:
        """String representation of ImageProcessor."""
        return f"ImageProcessor(supported_formats={self.supported_formats})"


# EOF
