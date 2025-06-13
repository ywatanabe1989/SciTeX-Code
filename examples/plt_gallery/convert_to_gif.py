#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert PNG examples to GIF for GitHub display."""

import matplotlib
matplotlib.use('Agg')

from PIL import Image
import os
import glob

# Directory containing the figures
figures_dir = "/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/examples/plt_gallery/figures"

# Find all PNG files
png_files = glob.glob(os.path.join(figures_dir, "*.png"))

print(f"Found {len(png_files)} PNG files to convert")

# Convert each PNG to GIF
for png_path in png_files:
    gif_path = png_path.replace('.png', '.gif')
    
    # Skip if GIF already exists
    if os.path.exists(gif_path):
        print(f"Skipping {os.path.basename(png_path)} - GIF already exists")
        continue
    
    try:
        # Open PNG and save as GIF
        img = Image.open(png_path)
        img.save(gif_path, 'GIF')
        print(f"Converted: {os.path.basename(png_path)} -> {os.path.basename(gif_path)}")
    except Exception as e:
        print(f"Error converting {os.path.basename(png_path)}: {e}")

print("\nConversion complete!")