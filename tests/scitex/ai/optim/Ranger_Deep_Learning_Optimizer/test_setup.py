#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 06:47:00 (ywatanabe)"
# File: ./tests/scitex/ai/optim/Ranger_Deep_Learning_Optimizer/test_setup.py

import pytest
import os
import sys
from unittest import mock
from pathlib import Path


class TestRangerSetup:
    """Test suite for Ranger Deep Learning Optimizer setup.py functionality."""

    @pytest.fixture
    def setup_dir(self):
        """Get the setup.py directory path."""
        return Path(__file__).parent.parent.parent.parent.parent.parent / "src" / "scitex" / "ai" / "optim" / "Ranger_Deep_Learning_Optimizer"

    @pytest.fixture
    def setup_file(self, setup_dir):
        """Get the setup.py file path."""
        return setup_dir / "setup.py"

    def test_setup_file_exists(self, setup_file):
        """Test that setup.py file exists."""
        assert setup_file.exists(), "setup.py file should exist"

    def test_setup_file_is_readable(self, setup_file):
        """Test that setup.py file is readable."""
        assert setup_file.is_file(), "setup.py should be a file"
        with open(setup_file, 'r') as f:
            content = f.read()
            assert len(content) > 0, "setup.py should not be empty"

    def test_setup_file_contains_required_imports(self, setup_file):
        """Test that setup.py contains necessary imports."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert "from setuptools import" in content, "Should import setuptools"
        assert "setup(" in content, "Should call setup function"

    def test_setup_metadata(self, setup_file):
        """Test that setup.py contains proper metadata."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        # Check for essential metadata
        assert 'name="ranger"' in content, "Should specify package name"
        assert 'version=' in content, "Should specify version"
        assert 'author=' in content, "Should specify author"
        assert 'description=' in content, "Should have description"
        assert 'install_requires=' in content, "Should specify dependencies"

    def test_setup_dependencies(self, setup_file):
        """Test that setup.py specifies torch dependency."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert '"torch"' in content, "Should require torch dependency"

    @mock.patch('setuptools.setup')
    def test_setup_execution(self, mock_setup, setup_dir):
        """Test that setup.py can be executed without errors."""
        setup_file = setup_dir / "setup.py"
        
        # Mock the read function to avoid file dependency issues
        def mock_read(fname):
            if fname == "README.md":
                return "Mock README content"
            return ""
        
        # Add the setup directory to sys.path temporarily
        original_path = sys.path[:]
        try:
            sys.path.insert(0, str(setup_dir))
            
            # Mock the global namespace for execution
            exec_globals = {
                'os': os,
                'read': mock_read,
                '__file__': str(setup_file),
                '__name__': '__main__'
            }
            
            # Execute the setup.py content
            with open(setup_file, 'r') as f:
                setup_code = f.read()
            
            # Replace the read function call to avoid file issues
            setup_code = setup_code.replace('long_description=read("README.md")', 'long_description="Mock README"')
            
            exec(setup_code, exec_globals)
            
            # Verify setup was called
            assert mock_setup.called, "setup() should be called"
            
        finally:
            sys.path[:] = original_path

    def test_package_configuration(self, setup_file):
        """Test that package configuration is correct."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        # Check package exclusions
        assert "exclude=" in content, "Should exclude test packages"
        assert '"tests"' in content, "Should exclude tests directory"
        
        # Check package directory configuration
        assert "package_dir=" in content, "Should specify package directory"

    def test_setup_version_format(self, setup_file):
        """Test that version follows semantic versioning."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        # Extract version string
        import re
        version_match = re.search(r'version=["\']([^"\']+)["\']', content)
        assert version_match, "Should have a version string"
        
        version = version_match.group(1)
        # Check for development version format
        assert "dev" in version or "." in version, "Version should be properly formatted"

    def test_license_specification(self, setup_file):
        """Test that license is specified."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert 'license=' in content, "Should specify license"
        assert 'Apache' in content, "Should use Apache license"

    def test_description_content(self, setup_file):
        """Test that description mentions key components."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        # Check for key algorithm mentions
        assert "RAdam" in content or "Rectified Adam" in content, "Should mention RAdam"
        assert "LookAhead" in content, "Should mention LookAhead"
        assert "optimizer" in content.lower(), "Should mention optimizer"

    def test_find_packages_configuration(self, setup_file):
        """Test that find_packages is configured correctly."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert "find_packages(" in content, "Should use find_packages"
        assert "exclude=" in content, "Should exclude test directories"

    def test_long_description_configuration(self, setup_file):
        """Test that long description is configured for markdown."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert "long_description_content_type" in content, "Should specify content type"
        assert "text/markdown" in content, "Should use markdown content type"

    @pytest.mark.parametrize("required_field", [
        "name=",
        "version=", 
        "packages=",
        "package_dir=",
        "description=",
        "author=",
        "license=",
        "install_requires="
    ])
    def test_required_setup_fields(self, setup_file, required_field):
        """Test that all required setup fields are present."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert required_field in content, f"setup.py should contain {required_field}"

    def test_read_function_exists(self, setup_file):
        """Test that helper read function is defined."""
        with open(setup_file, 'r') as f:
            content = f.read()
        
        assert "def read(" in content, "Should define read helper function"
        assert "open(" in content, "Read function should open files"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/optim/Ranger_Deep_Learning_Optimizer/setup.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python
# 
# import os
# from setuptools import find_packages, setup
# 
# 
# def read(fname):
#     with open(os.path.join(os.path.dirname(__file__), fname)) as f:
#         return f.read()
# 
# 
# setup(
#     name="ranger",
#     version="0.1.dev0",
#     packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
#     package_dir={"ranger": os.path.join(".", "ranger")},
#     description="Ranger - a synergistic optimizer using RAdam "
#     "(Rectified Adam) and LookAhead in one codebase ",
#     long_description=read("README.md"),
#     long_description_content_type="text/markdown",
#     author="Less Wright",
#     license="Apache",
#     install_requires=["torch"],
# )

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/optim/Ranger_Deep_Learning_Optimizer/setup.py
# --------------------------------------------------------------------------------
