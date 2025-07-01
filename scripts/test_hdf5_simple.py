#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:20:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/scripts/test_hdf5_simple.py
# ----------------------------------------
import os
import sys
__FILE__ = "./scripts/test_hdf5_simple.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Simple test to verify HDF5 functionality"""

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy as np
    import h5py
    from src.scitex.io._save_modules._hdf5 import _save_hdf5
    from src.scitex.io._load_modules._hdf5 import _load_hdf5
    
    print("✓ Imports successful")
    
    # Test data
    test_data = {
        'array': np.array([1, 2, 3, 4, 5]),
        'string': 'Hello HDF5',
        'number': 42
    }
    
    # Save and load test
    test_file = '/tmp/test_simple.h5'
    
    print("\nSaving data...")
    _save_hdf5(test_data, test_file)
    print("✓ Save successful")
    
    print("\nLoading data...")
    loaded = _load_hdf5(test_file)
    print("✓ Load successful")
    
    # Verify
    print("\nVerifying data...")
    assert np.array_equal(loaded['array'], test_data['array'])
    assert loaded['string'] == test_data['string']
    assert loaded['number'] == test_data['number']
    print("✓ Data verification successful")
    
    # Cleanup
    if os.path.exists(test_file):
        os.unlink(test_file)
    
    print("\n✅ All tests passed! The simplified HDF5 implementation is working correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# EOF