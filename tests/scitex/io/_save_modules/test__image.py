#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:57:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__image.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__image.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for image saving wrapper functionality
"""

import os
import tempfile
import pytest
import numpy as np
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from scitex.io._save_modules import save_image


class TestSaveImage:
    """Test suite for save_image wrapper function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_png = os.path.join(self.temp_dir, "test.png")
        self.test_file_jpg = os.path.join(self.temp_dir, "test.jpg")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        # Close any matplotlib figures
        if MATPLOTLIB_AVAILABLE:
            plt.close('all')

    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL/Pillow not installed")
    def test_save_pil_image(self):
        """Test saving PIL Image object"""
        # Create a simple RGB image
        img = Image.new('RGB', (100, 100), color='red')
        save_image(img, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)
        
        # Verify saved image
        loaded = Image.open(self.test_file_png)
        assert loaded.size == (100, 100)
        assert loaded.mode == 'RGB'

    def test_save_numpy_array_rgb(self):
        """Test saving numpy array as image (RGB)"""
        # Create RGB image array (H, W, C)
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:, :, 0] = 255  # Red channel
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)
        
        if PIL_AVAILABLE:
            loaded = Image.open(self.test_file_png)
            assert loaded.size == (100, 100)

    def test_save_numpy_array_grayscale(self):
        """Test saving grayscale numpy array"""
        # Create grayscale image
        arr = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)

    def test_save_numpy_array_float(self):
        """Test saving float numpy array (0-1 range)"""
        # Create float array
        arr = np.random.rand(100, 100, 3)
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_save_matplotlib_figure(self):
        """Test saving matplotlib figure"""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title("Test Plot")
        
        save_image(fig, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)
        plt.close(fig)

    def test_save_different_formats(self):
        """Test saving in different image formats"""
        arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        # PNG
        save_image(arr, self.test_file_png)
        assert os.path.exists(self.test_file_png)
        
        # JPEG
        save_image(arr, self.test_file_jpg)
        assert os.path.exists(self.test_file_jpg)
        
        # BMP
        bmp_file = os.path.join(self.temp_dir, "test.bmp")
        save_image(arr, bmp_file)
        assert os.path.exists(bmp_file)

    def test_save_with_quality(self):
        """Test saving JPEG with quality setting"""
        arr = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        # High quality
        high_quality = os.path.join(self.temp_dir, "high_quality.jpg")
        save_image(arr, high_quality, quality=95)
        
        # Low quality
        low_quality = os.path.join(self.temp_dir, "low_quality.jpg")
        save_image(arr, low_quality, quality=10)
        
        # High quality file should be larger
        assert os.path.getsize(high_quality) > os.path.getsize(low_quality)

    def test_save_rgba_image(self):
        """Test saving image with alpha channel"""
        # Create RGBA image
        arr = np.zeros((100, 100, 4), dtype=np.uint8)
        arr[:, :, 0] = 255  # Red
        arr[:, :, 3] = 128  # Semi-transparent
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)
        
        if PIL_AVAILABLE:
            loaded = Image.open(self.test_file_png)
            assert loaded.mode in ['RGBA', 'LA']

    def test_save_large_image(self):
        """Test saving large image"""
        # Create large image
        arr = np.random.randint(0, 256, (2000, 2000, 3), dtype=np.uint8)
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)

    def test_save_binary_image(self):
        """Test saving binary (black and white) image"""
        # Create binary image
        arr = np.random.choice([0, 255], size=(100, 100), p=[0.5, 0.5]).astype(np.uint8)
        
        save_image(arr, self.test_file_png)
        
        assert os.path.exists(self.test_file_png)

    @pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
    def test_save_matplotlib_with_dpi(self):
        """Test saving matplotlib figure with custom DPI"""
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot([1, 2, 3], [1, 2, 3])
        
        # Save with high DPI
        save_image(fig, self.test_file_png, dpi=300)
        
        assert os.path.exists(self.test_file_png)
        plt.close(fig)

    def test_save_from_file_path(self):
        """Test copying existing image file"""
        # First create an image
        arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        temp_source = os.path.join(self.temp_dir, "source.png")
        
        if PIL_AVAILABLE:
            Image.fromarray(arr).save(temp_source)
            
            # Now use save_image to copy it
            save_image(temp_source, self.test_file_png)
            
            assert os.path.exists(self.test_file_png)

    def test_error_invalid_input(self):
        """Test error handling for invalid input"""
        with pytest.raises(ValueError):
            save_image("not an image", self.test_file_png)
        
        with pytest.raises(ValueError):
            save_image(123, self.test_file_png)

    def test_save_with_metadata(self):
        """Test saving image with metadata (if supported)"""
        if PIL_AVAILABLE:
            img = Image.new('RGB', (100, 100), color='blue')
            
            # PIL images can have info dict
            img.info['description'] = 'Test image'
            img.info['software'] = 'scitex'
            
            save_image(img, self.test_file_png)
            
            loaded = Image.open(self.test_file_png)
            # Note: Not all formats preserve metadata

    def test_save_palette_image(self):
        """Test saving palette/indexed color image"""
        if PIL_AVAILABLE:
            # Create palette image
            img = Image.new('P', (100, 100))
            palette = []
            for i in range(256):
                palette.extend([i, 0, 0])  # Red gradient
            img.putpalette(palette)
            
            save_image(img, self.test_file_png)
            
            assert os.path.exists(self.test_file_png)
            loaded = Image.open(self.test_file_png)
            assert loaded.mode == 'P'


# EOF
