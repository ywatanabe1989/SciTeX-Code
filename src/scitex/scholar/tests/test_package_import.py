#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 15:40:00 (ywatanabe)"
# File: tests/test_package_import.py

"""
Test basic package import functionality.

This test verifies that the SciTeX-Scholar package can be imported correctly
and that basic package metadata is accessible.
"""

import unittest


class TestPackageImport(unittest.TestCase):
    """Test suite for package import functionality."""
    
    def test_package_import(self):
        """Test that the scitex_scholar package can be imported."""
        try:
            import sys
            sys.path.insert(0, './src')
            import scitex_scholar
        except ImportError:
            self.fail("Failed to import scitex_scholar package")

    def test_package_version(self):
        """Test that package version is accessible."""
        import sys
        sys.path.insert(0, './src')
        import scitex_scholar
        
        self.assertTrue(hasattr(scitex_scholar, '__version__'))
        self.assertIsInstance(scitex_scholar.__version__, str)
        self.assertGreater(len(scitex_scholar.__version__), 0)

    def test_package_metadata(self):
        """Test that package metadata is properly set."""
        import sys
        sys.path.insert(0, './src')
        import scitex_scholar
        
        # Test required metadata attributes
        self.assertTrue(hasattr(scitex_scholar, '__author__'))
        self.assertTrue(hasattr(scitex_scholar, '__email__'))
        self.assertEqual(scitex_scholar.__author__, "Yusuke Watanabe")
        self.assertEqual(scitex_scholar.__email__, "ywatanabe@alumni.u-tokyo.ac.jp")


if __name__ == "__main__":
    unittest.main()

# EOF