#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-01 23:21:22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/plt/_im2grid.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/plt/_im2grid.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from PIL import Image


def im2grid(image_paths, default_color=(255, 255, 255)):
    """
    Create a grid of images from a 2D NumPy array of image paths.
    Skips positions where image_paths is None.

    Args:
    image_paths (2D numpy array of str or None): Array of image file paths or None for empty slots
    default_color (tuple): RGB color tuple for empty spaces

    Returns:
    PIL.Image: A new image consisting of the grid of images
    """
    from scitex.io import load as scitex_io_load

    nrows, ncols = image_paths.shape

    # Load images, skip None paths
    images = []
    for row in image_paths:
        row_images = []
        for path in row:
            if path is not None:
                # img = Image.open(path)
                img = scitex_io_load(path)
            else:
                img = None
            row_images.append(img)
        images.append(row_images)

    # Assuming all images are the same size, use the first non-None image to determine size
    for row in images:
        for img in row:
            if img is not None:
                img_width, img_height = img.size
                break
        else:
            continue
        break
    else:
        raise ValueError("All image paths are None.")

    # Create a new image with the total size
    grid_width = img_width * ncols
    grid_height = img_height * nrows
    grid_image = Image.new("RGB", (grid_width, grid_height), default_color)

    # Paste images into the grid
    for y, row in enumerate(images):
        for x, img in enumerate(row):
            if img is not None:
                grid_image.paste(img, (x * img_width, y * img_height))

    return grid_image


# EOF
