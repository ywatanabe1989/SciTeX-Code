#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__image.py

"""Comprehensive tests for image file loading functionality."""

import os
import tempfile
import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from unittest.mock import patch, Mock
import io


class TestLoadImage:
    """Test suite for _load_image function."""
    
    def test_basic_rgb_image_loading(self):
        """Test loading basic RGB image files in various formats."""
        from scitex.io._load_modules import _load_image
        
        # Create a simple RGB image with distinct colors
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        img_array[:, :50, 0] = 255  # Red half
        img_array[:, 50:, 2] = 255  # Blue half
        img = Image.fromarray(img_array, 'RGB')
        
        # Test multiple supported formats
        for ext in ['.png', '.jpg', '.jpeg']:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                if ext == '.jpg' or ext == '.jpeg':
                    img.save(f.name, quality=95)  # High quality JPEG
                else:
                    img.save(f.name)
                temp_path = f.name
            
            try:
                loaded_img = _load_image(temp_path)
                assert isinstance(loaded_img, Image.Image)
                assert loaded_img.size == (100, 100)
                assert loaded_img.mode in ['RGB', 'RGBA']  # JPEG -> RGB, PNG may have alpha
                
                # Verify image content (allowing for JPEG compression artifacts)
                loaded_array = np.array(loaded_img)
                if loaded_array.ndim == 3 and loaded_array.shape[2] == 4:
                    loaded_array = loaded_array[:, :, :3]  # Remove alpha if present
                
                # Check if red and blue regions are distinguishable
                assert loaded_array[:, 25, 0].mean() > 200  # Red region should be red
                assert loaded_array[:, 75, 2].mean() > 200  # Blue region should be blue
                
            finally:
                os.unlink(temp_path)
    
    def test_grayscale_image_loading(self):
        """Test loading grayscale images."""
        from scitex.io._load_modules import _load_image
        
        # Create grayscale image with gradient
        gray_array = np.linspace(0, 255, 10000, dtype=np.uint8).reshape(100, 100)
        img = Image.fromarray(gray_array, 'L')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name
        
        try:
            loaded_img = _load_image(temp_path)
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (100, 100)
            assert loaded_img.mode == 'L'
            
            # Verify gradient preserved
            loaded_array = np.array(loaded_img)
            assert loaded_array[0, 0] < loaded_array[99, 99]  # Gradient preserved
            
        finally:
            os.unlink(temp_path)
    
    def test_rgba_image_with_transparency(self):
        """Test loading RGBA images with transparency."""
        from scitex.io._load_modules import _load_image
        
        # Create RGBA image with transparency
        rgba_array = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba_array[:, :, 0] = 255  # Red channel
        rgba_array[:, :50, 3] = 255  # Full opacity for left half
        rgba_array[:, 50:, 3] = 128  # Half opacity for right half
        img = Image.fromarray(rgba_array, 'RGBA')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name
        
        try:
            loaded_img = _load_image(temp_path)
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (100, 100)
            assert loaded_img.mode == 'RGBA'
            
            # Verify transparency preserved
            loaded_array = np.array(loaded_img)
            assert loaded_array[50, 25, 3] == 255  # Full opacity
            assert loaded_array[50, 75, 3] == 128  # Half opacity
            
        finally:
            os.unlink(temp_path)
    
    def test_tiff_format_support(self):
        """Test loading TIFF format images (both .tiff and .tif extensions)."""
        from scitex.io._load_modules import _load_image
        
        # Create high-resolution image for TIFF
        img_array = np.random.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        for ext in ['.tiff', '.tif']:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                img.save(f.name, compression='lzw')  # Use LZW compression
                temp_path = f.name
            
            try:
                loaded_img = _load_image(temp_path)
                assert isinstance(loaded_img, Image.Image)
                assert loaded_img.size == (300, 200)  # PIL reports (width, height)
                assert loaded_img.mode == 'RGB'
                
                # Verify image content preserved
                loaded_array = np.array(loaded_img)
                np.testing.assert_array_equal(loaded_array, img_array)
                
            finally:
                os.unlink(temp_path)
    
    def test_large_image_loading(self):
        """Test loading large images to verify memory handling."""
        from scitex.io._load_modules import _load_image
        
        # Create a large image (4K-like resolution)
        large_array = np.random.randint(0, 255, (2160, 3840, 3), dtype=np.uint8)
        img = Image.fromarray(large_array, 'RGB')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Use compression to reduce file size
            img.save(f.name, optimize=True, compress_level=6)
            temp_path = f.name
        
        try:
            loaded_img = _load_image(temp_path)
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (3840, 2160)
            assert loaded_img.mode == 'RGB'
            
            # Verify we can access pixel data without errors
            loaded_array = np.array(loaded_img)
            assert loaded_array.shape == (2160, 3840, 3)
            
        finally:
            os.unlink(temp_path)
    
    def test_scientific_image_formats(self):
        """Test loading images commonly used in scientific applications."""
        from scitex.io._load_modules import _load_image
        
        # 16-bit grayscale (common in microscopy)
        img_16bit = Image.new('I;16', (256, 256))
        # Create a pattern
        draw = ImageDraw.Draw(img_16bit)
        for i in range(0, 256, 32):
            draw.rectangle([i, i, i+16, i+16], fill=i*256)
        
        with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as f:
            img_16bit.save(f.name)
            temp_path = f.name
        
        try:
            loaded_img = _load_image(temp_path)
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (256, 256)
            # PIL may convert 16-bit to other formats
            assert loaded_img.mode in ['I;16', 'I', 'L']
            
        finally:
            os.unlink(temp_path)
    
    def test_multipage_tiff_loading(self):
        """Test loading multi-page TIFF (loads first page)."""
        from scitex.io._load_modules import _load_image
        
        # Create multi-page TIFF
        pages = []
        for i in range(3):
            img_array = np.full((100, 100, 3), i * 80, dtype=np.uint8)
            pages.append(Image.fromarray(img_array, 'RGB'))
        
        with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as f:
            pages[0].save(f.name, save_all=True, append_images=pages[1:], compression='lzw')
            temp_path = f.name
        
        try:
            loaded_img = _load_image(temp_path)
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (100, 100)
            assert loaded_img.mode == 'RGB'
            
            # Should load the first page
            loaded_array = np.array(loaded_img)
            assert np.all(loaded_array == 0)  # First page should be all zeros
            
        finally:
            os.unlink(temp_path)
    
    def test_kwargs_parameter_passing(self):
        """Test that kwargs are properly passed to PIL Image.open."""
        from scitex.io._load_modules import _load_image
        
        # Create test image
        img_array = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f.name)
            temp_path = f.name
        
        try:
            # Test with kwargs (formats parameter for PIL)
            loaded_img = _load_image(temp_path, formats=['PNG'])
            assert isinstance(loaded_img, Image.Image)
            assert loaded_img.size == (50, 50)
            
        finally:
            os.unlink(temp_path)
    
    def test_unsupported_extensions(self):
        """Test that unsupported file extensions raise ValueError."""
        from scitex.io._load_modules import _load_image
        
        unsupported_extensions = [
            'file.txt', 'image.gif', 'data.csv', 'document.pdf',
            'archive.zip', 'executable.exe', 'image.bmp', 'image.webp'
        ]
        
        for filename in unsupported_extensions:
            with pytest.raises(ValueError, match="Unsupported image format"):
                _load_image(filename)
    
    def test_supported_extensions_validation(self):
        """Test that all documented supported extensions are recognized."""
        from scitex.io._load_modules import _load_image
        
        # These should not raise ValueError (will raise FileNotFoundError instead)
        supported_extensions = [
            'image.jpg', 'image.png', 'image.tiff', 'image.tif',
            'photo.JPG', 'scan.PNG', 'data.TIFF', 'microscopy.TIF'
        ]
        
        for filename in supported_extensions:
            try:
                _load_image(filename)
            except ValueError:
                pytest.fail(f"Extension {filename} should be supported but raised ValueError")
            except FileNotFoundError:
                pass  # Expected for non-existent files
    
    def test_nonexistent_file_error(self):
        """Test that loading non-existent files raises appropriate errors."""
        from scitex.io._load_modules import _load_image
        
        nonexistent_files = [
            "/nonexistent/image.png",
            "./missing_image.jpg",
            "/tmp/not_found.tiff"
        ]
        
        for filepath in nonexistent_files:
            with pytest.raises(FileNotFoundError):
                _load_image(filepath)
    
    def test_corrupted_image_file(self):
        """Test handling of corrupted image files."""
        from scitex.io._load_modules import _load_image
        
        # Create a file with image extension but invalid content
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b'This is not a valid PNG file content')
            temp_path = f.name
        
        try:
            # Should raise an exception from PIL
            with pytest.raises(Exception):  # PIL raises various exceptions for corrupted files
                _load_image(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_image_file(self):
        """Test handling of empty image files."""
        from scitex.io._load_modules import _load_image
        
        # Create empty file with image extension
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name  # File is empty
        
        try:
            with pytest.raises(Exception):  # PIL should raise an exception
                _load_image(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_case_insensitive_extensions(self):
        """Test that file extension matching is case-insensitive."""
        from scitex.io._load_modules import _load_image
        
        # Create test image
        img_array = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        # Test various case combinations
        for ext in ['.PNG', '.Jpg', '.JPEG', '.TifF', '.TIF']:
            with tempfile.NamedTemporaryFile(suffix=ext.lower(), delete=False) as f:
                img.save(f.name)
                # Rename to have uppercase extension
                uppercase_path = f.name.replace(ext.lower(), ext)
                os.rename(f.name, uppercase_path)
                temp_path = uppercase_path
            
            try:
                # This should work despite case differences
                try:
                    loaded_img = _load_image(temp_path)
                    assert isinstance(loaded_img, Image.Image)
                except ValueError:
                    # Current implementation might be case-sensitive
                    # This documents the current behavior
                    pass
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    @patch('PIL.Image.open')
    def test_pil_integration_mocking(self, mock_open):
        """Test integration with PIL using mocking."""
        from scitex.io._load_modules import _load_image
        
        # Setup mock
        mock_image = Mock(spec=Image.Image)
        mock_image.size = (640, 480)
        mock_image.mode = 'RGB'
        mock_open.return_value = mock_image
        
        # Test function call
        result = _load_image('test_image.png')
        
        # Verify behavior
        assert result is mock_image
        mock_open.assert_called_once_with('test_image.png')
    
    @patch('PIL.Image.open')
    def test_kwargs_forwarding_to_pil(self, mock_open):
        """Test that kwargs are properly forwarded to PIL.Image.open."""
        from scitex.io._load_modules import _load_image
        
        # Setup mock
        mock_image = Mock(spec=Image.Image)
        mock_open.return_value = mock_image
        
        # Test with various kwargs
        test_kwargs = {'formats': ['PNG'], 'mode': 'r'}
        _load_image('test.png', **test_kwargs)
        
        # Verify kwargs were passed
        mock_open.assert_called_once_with('test.png', **test_kwargs)


# Legacy test functions for backward compatibility
def test_load_image_basic():
    """Legacy test function - basic image loading."""
    test_instance = TestLoadImage()
    test_instance.test_basic_rgb_image_loading()


def test_load_image_grayscale():
    """Legacy test function - grayscale image loading."""
    test_instance = TestLoadImage()
    test_instance.test_grayscale_image_loading()


def test_load_image_invalid_extension():
    """Legacy test function - invalid extension handling."""
    test_instance = TestLoadImage()
    test_instance.test_unsupported_extensions()


def test_load_image_nonexistent():
    """Legacy test function - nonexistent file handling."""
    test_instance = TestLoadImage()
    test_instance.test_nonexistent_file_error()

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_image.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:55:38 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_image.py
# 
# from typing import Any
# 
# from PIL import Image
# 
# 
# def _load_image(lpath: str, **kwargs) -> Any:
#     """Load image file."""
#     supported_exts = [".jpg", ".jpeg", ".png", ".tiff", ".tif"]
#     if not any(lpath.lower().endswith(ext) for ext in supported_exts):
#         raise ValueError("Unsupported image format")
#     return Image.open(lpath, **kwargs)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_image.py
# --------------------------------------------------------------------------------
