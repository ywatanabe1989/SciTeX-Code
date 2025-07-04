#!/usr/bin/env python3
"""
Test script to verify that the PosixPath fix works correctly.
This script tests both the save and load functions with pathlib.Path objects.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tempfile
import numpy as np
from pathlib import Path
import pandas as pd

# Import scitex after adding to path
import scitex

def test_save_with_posixpath():
    """Test that save function works with PosixPath objects."""
    print("Testing save function with PosixPath objects...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test data
        test_data = np.array([1, 2, 3, 4, 5])
        test_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        
        # Test with PosixPath for numpy array
        posix_path_npy = Path(temp_dir) / "test_data.npy"
        try:
            scitex.io.save(test_data, posix_path_npy, verbose=True)
            print("✓ PosixPath save for .npy file succeeded")
        except AttributeError as e:
            if "'PosixPath' object has no attribute 'startswith'" in str(e):
                print("✗ PosixPath save failed with startswith error")
                return False
            else:
                print(f"✗ PosixPath save failed with unexpected error: {e}")
                return False
        except Exception as e:
            print(f"✗ PosixPath save failed with error: {e}")
            return False
        
        # Test with PosixPath for CSV
        posix_path_csv = Path(temp_dir) / "test_data.csv"
        try:
            scitex.io.save(test_df, posix_path_csv, verbose=True)
            print("✓ PosixPath save for .csv file succeeded")
        except AttributeError as e:
            if "'PosixPath' object has no attribute 'startswith'" in str(e):
                print("✗ PosixPath save failed with startswith error")
                return False
            else:
                print(f"✗ PosixPath save failed with unexpected error: {e}")
                return False
        except Exception as e:
            print(f"✗ PosixPath save failed with error: {e}")
            return False
        
        # Verify files were created
        if posix_path_npy.exists():
            print("✓ .npy file was created successfully")
        else:
            print("✗ .npy file was not created")
            return False
            
        if posix_path_csv.exists():
            print("✓ .csv file was created successfully")
        else:
            print("✗ .csv file was not created")
            return False
    
    return True

def test_load_with_posixpath():
    """Test that load function works with PosixPath objects."""
    print("\nTesting load function with PosixPath objects...")
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test data and save it first
        test_data = np.array([1, 2, 3, 4, 5])
        test_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        
        # Save with string paths first
        npy_path_str = os.path.join(temp_dir, "test_data.npy")
        csv_path_str = os.path.join(temp_dir, "test_data.csv")
        
        scitex.io.save(test_data, npy_path_str, verbose=False)
        scitex.io.save(test_df, csv_path_str, verbose=False)
        
        # Now test loading with PosixPath
        posix_path_npy = Path(npy_path_str)
        posix_path_csv = Path(csv_path_str)
        
        try:
            loaded_npy = scitex.io.load(posix_path_npy)
            print("✓ PosixPath load for .npy file succeeded")
        except Exception as e:
            print(f"✗ PosixPath load failed with error: {e}")
            return False
        
        try:
            loaded_csv = scitex.io.load(posix_path_csv)
            print("✓ PosixPath load for .csv file succeeded")
        except Exception as e:
            print(f"✗ PosixPath load failed with error: {e}")
            return False
        
        # Verify data integrity
        if np.array_equal(test_data, loaded_npy):
            print("✓ Loaded .npy data matches original")
        else:
            print("✗ Loaded .npy data does not match original")
            return False
            
        if test_df.equals(loaded_csv):
            print("✓ Loaded .csv data matches original")
        else:
            print("✗ Loaded .csv data does not match original")
            return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing PosixPath fix for scitex.io module")
    print("=" * 60)
    
    save_success = test_save_with_posixpath()
    load_success = test_load_with_posixpath()
    
    print("\n" + "=" * 60)
    if save_success and load_success:
        print("✓ All tests passed! PosixPath fix is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. PosixPath fix needs more work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())