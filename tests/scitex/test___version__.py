#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./tests/scitex/test___version__.py
"""Comprehensive tests for scitex.__version__ module."""

import pytest
import re
import os
import sys
from unittest.mock import patch, mock_open
import importlib
import tempfile
import shutil


class TestVersionBasics:
    """Basic tests for version module."""
    
    def test_version_exists(self):
        """Test that __version__ attribute exists."""
        from scitex.__version__ import __version__
        
        assert __version__ is not None
        
    def test_version_is_string(self):
        """Test that __version__ is a string."""
        from scitex.__version__ import __version__
        
        assert isinstance(__version__, str)
        
    def test_version_not_empty(self):
        """Test that __version__ is not empty."""
        from scitex.__version__ import __version__
        
        assert len(__version__) > 0
        assert __version__.strip() != ""
        
    def test_file_attribute_exists(self):
        """Test that __FILE__ attribute exists."""
        from scitex.__version__ import __FILE__
        
        assert __FILE__ is not None
        assert isinstance(__FILE__, str)
        
    def test_dir_attribute_exists(self):
        """Test that __DIR__ attribute exists."""
        from scitex.__version__ import __DIR__
        
        assert __DIR__ is not None
        assert isinstance(__DIR__, str)


class TestVersionFormat:
    """Tests for version format validation."""
    
    def test_semantic_versioning(self):
        """Test that __version__ follows semantic versioning format."""
        from scitex.__version__ import __version__
        
        # Test semantic versioning pattern (major.minor.patch)
        semantic_version_pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(semantic_version_pattern, __version__)
        
    def test_version_components(self):
        """Test that version components are valid numbers."""
        from scitex.__version__ import __version__
        
        components = __version__.split('.')
        assert len(components) == 3
        
        # Test each component is a valid integer
        for component in components:
            assert component.isdigit()
            assert int(component) >= 0
            
    def test_version_major_minor_patch(self):
        """Test version major, minor, and patch components separately."""
        from scitex.__version__ import __version__
        
        major, minor, patch = __version__.split('.')
        
        # Convert to integers
        major_int = int(major)
        minor_int = int(minor)
        patch_int = int(patch)
        
        # Major version should be positive
        assert major_int > 0
        
        # Minor and patch can be 0 or positive
        assert minor_int >= 0
        assert patch_int >= 0
        
    def test_no_leading_zeros(self):
        """Test that version components don't have leading zeros."""
        from scitex.__version__ import __version__
        
        components = __version__.split('.')
        for component in components:
            # "0" is valid, but "01", "001" etc. are not
            if component != "0":
                assert not component.startswith("0")
                
    def test_version_comparison(self):
        """Test that version can be compared properly."""
        from scitex.__version__ import __version__
        
        # Should be able to compare with other version strings
        assert __version__ >= "1.0.0"
        assert __version__ > "0.0.0"


class TestVersionValues:
    """Tests for specific version values."""
    
    def test_current_version_value(self):
        """Test that __version__ has the expected current value."""
        from scitex.__version__ import __version__
        
        # Test current version (this may need updating with releases)
        assert __version__ == "1.11.0"
        
    def test_file_attribute_value(self):
        """Test that __FILE__ attribute has correct value."""
        from scitex.__version__ import __FILE__
        
        assert __FILE__ == "./src/scitex/__version__.py"
        
    def test_dir_attribute_value(self):
        """Test that __DIR__ attribute is derived from __FILE__."""
        from scitex.__version__ import __DIR__, __FILE__
        
        expected_dir = os.path.dirname(__FILE__)
        assert __DIR__ == expected_dir


class TestVersionModuleImport:
    """Tests for version module import behavior."""
    
    def test_import_from_package(self):
        """Test importing version from main package."""
        import scitex
        
        assert hasattr(scitex, '__version__')
        assert scitex.__version__ == "1.11.0"
        
    def test_module_attributes(self):
        """Test all expected module attributes."""
        import scitex.__version__ as version_module
        
        expected_attrs = ['__version__', '__FILE__', '__DIR__']
        for attr in expected_attrs:
            assert hasattr(version_module, attr)
            
    def test_no_unexpected_attributes(self):
        """Test that module doesn't have unexpected public attributes."""
        import scitex.__version__ as version_module
        
        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(version_module) 
                       if not attr.startswith('_') or attr in ['__version__', '__FILE__', '__DIR__']]
        
        # Should only have the expected attributes plus Python defaults
        expected = {'__version__', '__FILE__', '__DIR__', 'os'}
        actual = set(public_attrs) - set(dir(object))
        
        # Check that we don't have unexpected exports
        unexpected = actual - expected
        assert len(unexpected) == 0, f"Unexpected attributes: {unexpected}"


class TestVersionModuleFile:
    """Tests for version module file handling."""
    
    def test_file_exists(self):
        """Test that version file actually exists."""
        import scitex
        
        # Get the actual path to the version file
        module_path = scitex.__file__
        package_dir = os.path.dirname(module_path)
        version_file = os.path.join(package_dir, '__version__.py')
        
        assert os.path.exists(version_file)
        assert os.path.isfile(version_file)
        
    def test_file_readable(self):
        """Test that version file is readable."""
        import scitex
        
        module_path = scitex.__file__
        package_dir = os.path.dirname(module_path)
        version_file = os.path.join(package_dir, '__version__.py')
        
        # Should be able to read the file
        with open(version_file, 'r') as f:
            content = f.read()
            assert '__version__' in content
            assert '1.11.0' in content


class TestVersionEdgeCases:
    """Edge case tests for version module."""
    
    def test_version_immutability(self):
        """Test that version string appears immutable."""
        from scitex.__version__ import __version__
        
        original = __version__
        
        # Strings are immutable in Python, but test the reference
        assert __version__ is original
        
    def test_version_type_consistency(self):
        """Test version type consistency across imports."""
        from scitex.__version__ import __version__ as v1
        from scitex.__version__ import __version__ as v2
        
        assert type(v1) is type(v2)
        assert v1 == v2
        
    def test_version_unicode(self):
        """Test that version string is properly encoded."""
        from scitex.__version__ import __version__
        
        # Should be ASCII-only
        assert __version__.isascii()
        
        # Should be encodable as UTF-8
        assert __version__.encode('utf-8')
        
    def test_version_strip_whitespace(self):
        """Test version has no leading/trailing whitespace."""
        from scitex.__version__ import __version__
        
        assert __version__ == __version__.strip()
        assert '\n' not in __version__
        assert '\t' not in __version__
        assert '\r' not in __version__


class TestVersionIntegration:
    """Integration tests for version module."""
    
    def test_version_in_package_metadata(self):
        """Test that package version matches module version."""
        try:
            # Try to get version from package metadata
            import importlib.metadata
            package_version = importlib.metadata.version('scitex')
            
            from scitex.__version__ import __version__
            assert __version__ == package_version
        except ImportError:
            # importlib.metadata not available in older Python
            pytest.skip("importlib.metadata not available")
        except importlib.metadata.PackageNotFoundError:
            # Package not installed, just check module version exists
            from scitex.__version__ import __version__
            assert __version__
            
    def test_version_used_in_setup(self):
        """Test that version is used consistently."""
        from scitex.__version__ import __version__
        
        # Version should be a valid PEP 440 version
        # Basic check - more detailed check would need packaging library
        assert re.match(r'^\d+\.\d+\.\d+', __version__)
        
    def test_dir_relative_to_file(self):
        """Test __DIR__ is correctly relative to __FILE__."""
        from scitex.__version__ import __DIR__, __FILE__
        
        # Reconstruct full path and check consistency
        if __FILE__.startswith('./'):
            # Relative path
            assert __DIR__ == os.path.dirname(__FILE__)
        else:
            # Absolute path
            assert __DIR__ == os.path.dirname(__FILE__)


class TestVersionComparison:
    """Tests for version comparison functionality."""
    
    def test_version_parseable(self):
        """Test that version can be parsed for comparison."""
        from scitex.__version__ import __version__
        
        # Should be able to split into components
        parts = __version__.split('.')
        assert len(parts) == 3
        
        # Each part should be a number
        for part in parts:
            int(part)  # Should not raise
            
    def test_version_ordering(self):
        """Test version ordering logic."""
        from scitex.__version__ import __version__
        
        # Parse current version
        major, minor, patch = map(int, __version__.split('.'))
        
        # Test ordering
        newer = f"{major + 1}.0.0"
        older = f"{major - 1 if major > 0 else 0}.0.0"
        
        # String comparison should work for simple cases
        if major > 0:
            assert __version__ > older
        assert __version__ < newer


class TestVersionPerformance:
    """Performance tests for version module."""
    
    def test_import_speed(self):
        """Test that version module imports quickly."""
        import time
        import importlib
        
        # Clear any cached import
        if 'scitex.__version__' in sys.modules:
            del sys.modules['scitex.__version__']
            
        start = time.time()
        import scitex.__version__
        end = time.time()
        
        # Import should be fast (less than 0.1 seconds)
        assert end - start < 0.1
        
    def test_repeated_access(self):
        """Test repeated access to version is efficient."""
        from scitex.__version__ import __version__
        
        import time
        
        # Access version many times
        start = time.time()
        for _ in range(10000):
            _ = __version__
        end = time.time()
        
        # Should be very fast (less than 0.01 seconds)
        assert end - start < 0.01


class TestVersionDocumentation:
    """Tests for version module documentation."""
    
    def test_module_has_docstring(self):
        """Test that version module could have a docstring."""
        import scitex.__version__ as version_module
        
        # Module docstring is optional but good practice
        # Just test that if it exists, it's a string
        if version_module.__doc__:
            assert isinstance(version_module.__doc__, str)
            
    def test_version_mentioned_in_init(self):
        """Test that version is accessible from main package."""
        import scitex
        
        # Should be able to access version from main package
        assert hasattr(scitex, '__version__')
        
        # Should match the version module version
        from scitex.__version__ import __version__
        assert scitex.__version__ == __version__


class TestVersionMaintenance:
    """Tests to help with version maintenance."""
    
    def test_version_format_for_pip(self):
        """Test version format is compatible with pip."""
        from scitex.__version__ import __version__
        
        # PEP 440 compatible version
        # Basic test - just check it's numeric.numeric.numeric
        assert re.match(r'^\d+\.\d+\.\d+$', __version__)
        
    def test_version_not_dev(self):
        """Test that version doesn't contain dev markers in release."""
        from scitex.__version__ import __version__
        
        # Release versions shouldn't contain dev, alpha, beta, rc
        assert 'dev' not in __version__.lower()
        assert 'alpha' not in __version__.lower()
        assert 'beta' not in __version__.lower()
        assert 'rc' not in __version__.lower()
        
    def test_version_incrementable(self):
        """Test that version components can be incremented."""
        from scitex.__version__ import __version__
        
        major, minor, patch = map(int, __version__.split('.'))
        
        # Test incrementing each component
        next_major = f"{major + 1}.0.0"
        next_minor = f"{major}.{minor + 1}.0"
        next_patch = f"{major}.{minor}.{patch + 1}"
        
        # All should be valid version strings
        for version in [next_major, next_minor, next_patch]:
            assert re.match(r'^\d+\.\d+\.\d+$', version)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__), "-v"])