#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 23:19:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/plt/test__im2grid.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/plt/test__im2grid.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex
import numpy as np
from scitex.plt.utils import im2grid
from PIL import Image
import pytest
from unittest.mock import Mock, patch


def test_grid_image(monkeypatch):
    def dummy_load(path):
        return Image.new("RGB", (2, 3))

    monkeypatch.setattr(scitex.io, "load", dummy_load)
    paths = np.array([["a", None], [None, "b"]], dtype=object)
    # img = im2grid(paths, default_color=(255, 0, 0))
    img = im2grid(paths, default_color=(255, 0, 0))

    # Save the grid image
    from scitex.io import save

    spath = f"./{os.path.basename(__file__).replace('.py', '')}_test_grid_image.jpg"
    save(img, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save grid image to {spath}"

    # Original assertions
    assert isinstance(img, Image.Image)
    # grid width = 2 cols * img width(2), height = 2 rows * img height(3)
    assert img.size == (4, 6)


def test_single_image(monkeypatch):
    def dummy_load(path):
        return Image.new("RGB", (4, 4))

    monkeypatch.setattr(scitex.io, "load", dummy_load)
    paths = np.array([["a"]], dtype=object)
    img = im2grid(paths)

    # Save the image
    from scitex.io import save

    spath = f"./{os.path.basename(__file__).replace('.py', '')}_test_single_image.jpg"
    save(img, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(actual_spath), f"Failed to save single image to {spath}"

    assert isinstance(img, Image.Image)
    assert img.size == (4, 4)


def test_custom_default_color(monkeypatch):
    def dummy_load(path):
        return Image.new("RGB", (3, 3))

    monkeypatch.setattr(scitex.io, "load", dummy_load)
    paths = np.array([["a", None], [None, "b"]], dtype=object)
    custom_color = (0, 255, 0)  # Green
    img = im2grid(paths, default_color=custom_color)

    # Save the image
    from scitex.io import save

    spath = f"./{os.path.basename(__file__).replace('.py', '')}_test_custom_default_color.jpg"
    save(img, spath)

    # Check saved file
    ACTUAL_SAVE_DIR = __file__.replace(".py", "_out")
    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)
    assert os.path.exists(
        actual_spath
    ), f"Failed to save image with custom color to {spath}"

    assert isinstance(img, Image.Image)
    assert img.size == (6, 6)


def test_all_none_paths():
    """Test that ValueError is raised when all paths are None."""
    paths = np.array([[None, None], [None, None]], dtype=object)
    
    with pytest.raises(ValueError, match="All image paths are None"):
        im2grid(paths)


def test_mixed_image_grid(monkeypatch):
    """Test grid with mixed present and None images."""
    def dummy_load(path):
        # Return different sizes based on path to test consistency
        if path == "large":
            return Image.new("RGB", (10, 10))
        else:
            return Image.new("RGB", (5, 5))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    # 3x3 grid with some None values
    paths = np.array([
        ["img1", "img2", None],
        [None, "img3", "img4"],
        ["img5", None, "img6"]
    ], dtype=object)
    
    img = im2grid(paths, default_color=(128, 128, 128))
    
    assert isinstance(img, Image.Image)
    assert img.size == (15, 15)  # 3 cols * 5 width, 3 rows * 5 height


def test_single_column_grid(monkeypatch):
    """Test grid with single column."""
    def dummy_load(path):
        return Image.new("RGB", (8, 6))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["img1"], ["img2"], ["img3"]], dtype=object)
    img = im2grid(paths)
    
    assert isinstance(img, Image.Image)
    assert img.size == (8, 18)  # 1 col * 8 width, 3 rows * 6 height


def test_single_row_grid(monkeypatch):
    """Test grid with single row."""
    def dummy_load(path):
        return Image.new("RGB", (7, 9))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["img1", "img2", "img3", "img4"]], dtype=object)
    img = im2grid(paths)
    
    assert isinstance(img, Image.Image)
    assert img.size == (28, 9)  # 4 cols * 7 width, 1 row * 9 height


def test_default_white_background(monkeypatch):
    """Test default white background color."""
    def dummy_load(path):
        return Image.new("RGB", (2, 2), color=(255, 0, 0))  # Red image
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["img1", None]], dtype=object)
    img = im2grid(paths)  # No default_color specified
    
    assert isinstance(img, Image.Image)
    # Check that a pixel in the None area is white
    pixel = img.getpixel((3, 1))  # Should be in the white area
    assert pixel == (255, 255, 255)


def test_rgba_images(monkeypatch):
    """Test grid with RGBA images."""
    def dummy_load(path):
        return Image.new("RGBA", (4, 4), color=(255, 0, 0, 128))  # Semi-transparent red
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["img1", "img2"]], dtype=object)
    img = im2grid(paths)
    
    assert isinstance(img, Image.Image)
    assert img.mode == "RGB"  # Should be converted to RGB
    assert img.size == (8, 4)


def test_large_grid(monkeypatch):
    """Test larger grid creation."""
    def dummy_load(path):
        return Image.new("RGB", (10, 10))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    # 5x5 grid
    paths = np.array([
        [f"img_{i}_{j}" if (i + j) % 2 == 0 else None 
         for j in range(5)] 
        for i in range(5)
    ], dtype=object)
    
    img = im2grid(paths)
    
    assert isinstance(img, Image.Image)
    assert img.size == (50, 50)  # 5 * 10 for each dimension


def test_different_color_formats(monkeypatch):
    """Test different color format inputs for default_color."""
    def dummy_load(path):
        return Image.new("RGB", (3, 3))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([[None, "img1"]], dtype=object)
    
    # Test with different color formats
    color_formats = [
        (255, 0, 0),      # Red
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (128, 128, 128),  # Gray
        (255, 255, 0),    # Yellow
    ]
    
    for color in color_formats:
        img = im2grid(paths, default_color=color)
        assert isinstance(img, Image.Image)
        # Check that the None area has the specified color
        pixel = img.getpixel((1, 1))  # Should be in the colored area
        assert pixel == color


def test_image_loading_error_handling(monkeypatch):
    """Test handling of image loading errors."""
    def dummy_load(path):
        if path == "bad_image":
            raise IOError("Cannot load image")
        return Image.new("RGB", (5, 5))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["good_image", "bad_image"]], dtype=object)
    
    # Should raise the IOError from loading
    with pytest.raises(IOError, match="Cannot load image"):
        im2grid(paths)


def test_empty_array():
    """Test behavior with empty array."""
    paths = np.array([], dtype=object).reshape(0, 0)
    
    # Should handle empty array gracefully
    with pytest.raises(ValueError):
        im2grid(paths)


def test_non_uniform_none_pattern(monkeypatch):
    """Test complex pattern of None and images."""
    def dummy_load(path):
        return Image.new("RGB", (4, 3))
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    # Checkerboard pattern
    paths = np.array([
        ["img1", None, "img2", None],
        [None, "img3", None, "img4"],
        ["img5", None, "img6", None],
        [None, "img7", None, "img8"]
    ], dtype=object)
    
    img = im2grid(paths, default_color=(200, 200, 200))
    
    assert isinstance(img, Image.Image)
    assert img.size == (16, 12)  # 4 cols * 4 width, 4 rows * 3 height


def test_grayscale_images(monkeypatch):
    """Test grid with grayscale images."""
    def dummy_load(path):
        return Image.new("L", (5, 5), color=128)  # Grayscale
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    paths = np.array([["img1", "img2"]], dtype=object)
    img = im2grid(paths)
    
    assert isinstance(img, Image.Image)
    assert img.mode == "RGB"  # Should be converted to RGB
    assert img.size == (10, 5)


def test_image_paste_positioning(monkeypatch):
    """Test that images are pasted at correct positions."""
    call_count = 0
    paste_calls = []
    
    def dummy_load(path):
        nonlocal call_count
        call_count += 1
        # Create images with different colors to distinguish them
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        return Image.new("RGB", (2, 2), color=colors[call_count - 1])
    
    monkeypatch.setattr(scitex.io, "load", dummy_load)
    
    # 2x2 grid
    paths = np.array([["r", "g"], ["b", "y"]], dtype=object)
    
    img = im2grid(paths)
    
    # Check specific pixels to verify positioning
    assert img.getpixel((0, 0))[:3] == (255, 0, 0)    # Top-left: red
    assert img.getpixel((2, 0))[:3] == (0, 255, 0)    # Top-right: green
    assert img.getpixel((0, 2))[:3] == (0, 0, 255)    # Bottom-left: blue
    assert img.getpixel((2, 2))[:3] == (255, 255, 0)  # Bottom-right: yellow


# def test_grid_image(monkeypatch):
#     def dummy_load(path):
#         return Image.new("RGB", (2, 3))

#     monkeypatch.setattr(scitex.io, "load", dummy_load)
#     paths = np.array([["a", None], [None, "b"]], dtype=object)
#     img = im2grid(paths, default_color=(255, 0, 0))

#     # Save the grid image
#     out_dir = __file__.replace(".py", "_out")
#     os.makedirs(out_dir, exist_ok=True)

#     filename = (
#         os.path.basename(__file__).replace(".py", "") + "_test_grid_image.jpg"
#     )
#     save_path = os.path.join(out_dir, filename)

#     img.save(save_path)
#     assert os.path.exists(
#         save_path
#     ), f"Failed to save grid image to {save_path}"

#     # Original assertions
#     assert isinstance(img, Image.Image)
#     # grid width = 2 cols * img width(2), height = 2 rows * img height(3)
#     assert img.size == (4, 6)


# def test_single_image(monkeypatch):
#     def dummy_load(path):
#         return Image.new("RGB", (4, 4))

#     monkeypatch.setattr(scitex.io, "load", dummy_load)
#     paths = np.array([["a"]], dtype=object)
#     img = im2grid(paths)

#     # Save the image
#     out_dir = __file__.replace(".py", "_out")
#     os.makedirs(out_dir, exist_ok=True)

#     filename = os.path.basename(__file__).replace('.py', '') + "_test_single_image.jpg"
#     save_path = os.path.join(out_dir, filename)

#     img.save(save_path)
#     assert os.path.exists(save_path), f"Failed to save single image to {save_path}"

#     assert isinstance(img, Image.Image)
#     assert img.size == (4, 4)

# def test_custom_default_color(monkeypatch):
#     def dummy_load(path):
#         return Image.new("RGB", (3, 3))

#     monkeypatch.setattr(scitex.io, "load", dummy_load)
#     paths = np.array([["a", None], [None, "b"]], dtype=object)
#     custom_color = (0, 255, 0)  # Green
#     img = im2grid(paths, default_color=custom_color)

#     # Save the image
#     out_dir = __file__.replace(".py", "_out")
#     os.makedirs(out_dir, exist_ok=True)

#     filename = os.path.basename(__file__).replace('.py', '') + "_test_custom_default_color.jpg"
#     save_path = os.path.join(out_dir, filename)

#     img.save(save_path)
#     assert os.path.exists(save_path), f"Failed to save image with custom color to {save_path}"

#     assert isinstance(img, Image.Image)
#     assert img.size == (6, 6)

#     # To validate the background color, we'd need to check pixel values
#     # This depends on how PIL handles colors and may require more detailed testing

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_im2grid.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 23:21:22 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_im2grid.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/plt/_im2grid.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# from PIL import Image
#
#
# def im2grid(image_paths, default_color=(255, 255, 255)):
#     """
#     Create a grid of images from a 2D NumPy array of image paths.
#     Skips positions where image_paths is None.
#
#     Args:
#     image_paths (2D numpy array of str or None): Array of image file paths or None for empty slots
#     default_color (tuple): RGB color tuple for empty spaces
#
#     Returns:
#     PIL.Image: A new image consisting of the grid of images
#     """
#     from scitex.io import load as scitex_io_load
#
#     nrows, ncols = image_paths.shape
#
#     # Load images, skip None paths
#     images = []
#     for row in image_paths:
#         row_images = []
#         for path in row:
#             if path is not None:
#                 # img = Image.open(path)
#                 img = scitex_io_load(path)
#             else:
#                 img = None
#             row_images.append(img)
#         images.append(row_images)
#
#     # Assuming all images are the same size, use the first non-None image to determine size
#     for row in images:
#         for img in row:
#             if img is not None:
#                 img_width, img_height = img.size
#                 break
#         else:
#             continue
#         break
#     else:
#         raise ValueError("All image paths are None.")
#
#     # Create a new image with the total size
#     grid_width = img_width * ncols
#     grid_height = img_height * nrows
#     grid_image = Image.new("RGB", (grid_width, grid_height), default_color)
#
#     # Paste images into the grid
#     for y, row in enumerate(images):
#         for x, img in enumerate(row):
#             if img is not None:
#                 grid_image.paste(img, (x * img_width, y * img_height))
#
#     return grid_image
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/plt/utils/_im2grid.py
# --------------------------------------------------------------------------------
