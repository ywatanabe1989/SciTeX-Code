#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 23:55:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/custom/test_export_as_csv_utils.py
# ----------------------------------------
"""
Utility functions for CSV export tests
"""

import os
import pandas as pd

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_export_as_csv_out')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def verify_csv_export(fig, save_path):
    """
    Verifies that a CSV is exported alongside the image.
    
    Args:
        fig: matplotlib figure object
        save_path: path to save the figure
        
    Returns:
        DataFrame: the loaded CSV data
        
    Raises:
        AssertionError: if CSV is not created or is empty
    """
    # Import scitex here to avoid circular imports
    import scitex

    # Save the figure - this should also create a CSV
    scitex.io.save(fig, save_path)
    
    # Verify image was created
    assert os.path.exists(save_path), f"PNG file not created: {save_path}"
    
    # Verify CSV was created
    csv_path = save_path.replace(".png", ".csv")
    assert os.path.exists(csv_path), f"CSV file not created: {csv_path}"
    
    # Read CSV and verify it's not empty
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty"
    
    return df