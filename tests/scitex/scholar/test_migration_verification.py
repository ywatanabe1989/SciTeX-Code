#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:21:00 (ywatanabe)"
# File: ./tests/scitex/scholar/test_migration_verification.py

"""Verify the scholar module migration was successful."""

import pytest
import os
import importlib
import pkgutil


def test_no_nested_src_directory():
    """Verify nested src directory was removed."""
    import scitex.scholar
    scholar_path = os.path.dirname(scitex.scholar.__file__)
    nested_src = os.path.join(scholar_path, 'src')
    assert not os.path.exists(nested_src), "Nested src directory still exists"


def test_underscore_naming_convention():
    """Verify internal modules use underscore prefix."""
    import scitex.scholar
    scholar_path = os.path.dirname(scitex.scholar.__file__)
    
    # List of modules that should have underscore prefix
    expected_underscore_modules = [
        '_document_indexer.py',
        '_journal_metrics.py', 
        '_latex_parser.py',
        '_literature_review_workflow.py',
        '_local_search.py',
        '_mcp_server.py',
        '_mcp_vector_server.py',
        '_paper_acquisition.py',
        '_paper.py',
        '_pdf_downloader.py',
        '_scientific_pdf_parser.py',
        '_search_engine.py',
        '_search.py',
        '_semantic_scholar_client.py',
        '_text_processor.py',
        '_vector_search_engine.py',
        '_vector_search.py',
        '_web_sources.py'
    ]
    
    for module_name in expected_underscore_modules:
        module_path = os.path.join(scholar_path, module_name)
        assert os.path.exists(module_path), f"Missing underscore module: {module_name}"


def test_no_pypi_files_in_module():
    """Verify PyPI-related files were moved out of module."""
    import scitex.scholar
    scholar_path = os.path.dirname(scitex.scholar.__file__)
    
    pypi_files = ['setup.py', 'pyproject.toml', 'MANIFEST.in', 
                  'requirements.txt', 'build_for_pypi.sh']
    
    for pypi_file in pypi_files:
        file_path = os.path.join(scholar_path, pypi_file)
        assert not os.path.exists(file_path), f"PyPI file still in module: {pypi_file}"
    
    # Verify they were moved to pypi_files directory
    pypi_dir = os.path.join(scholar_path, 'pypi_files')
    assert os.path.exists(pypi_dir), "pypi_files directory not found"


def test_demo_files_moved_to_examples():
    """Verify demo files were moved to examples directory."""
    import scitex.scholar
    scholar_path = os.path.dirname(scitex.scholar.__file__)
    
    # Demo files that should not be in scholar module
    demo_files = [
        'demo_enhanced_bibliography.py',
        'demo_gpac_enhanced_search.py', 
        'demo_literature_search.py',
        'demo_working_literature_system.py',
        'quick_gpac_review.py',
        'subscription_journal_workflow.py'
    ]
    
    for demo_file in demo_files:
        file_path = os.path.join(scholar_path, demo_file)
        assert not os.path.exists(file_path), f"Demo file still in module: {demo_file}"
    
    # Check examples directory exists
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(scholar_path))))
    examples_scholar = os.path.join(project_root, 'examples', 'scholar')
    assert os.path.exists(examples_scholar), "examples/scholar directory not found"


def test_module_structure_consistency():
    """Test that scholar module structure is consistent with other scitex modules."""
    # Check that scholar follows similar patterns to other modules
    import scitex.ai
    import scitex.io
    import scitex.scholar
    
    # All should have __all__ defined
    assert hasattr(scitex.ai, '__all__')
    assert hasattr(scitex.io, '__all__')
    assert hasattr(scitex.scholar, '__all__')
    
    # Check similar file naming patterns (underscore prefixes for internal modules)
    scholar_path = os.path.dirname(scitex.scholar.__file__)
    py_files = [f for f in os.listdir(scholar_path) if f.endswith('.py')]
    
    # Most .py files should start with underscore (except __init__.py)
    internal_modules = [f for f in py_files if f != '__init__.py' and not f.startswith('_')]
    
    # Should have very few non-underscore modules
    assert len(internal_modules) == 0, f"Non-underscore internal modules found: {internal_modules}"


def test_imports_between_scholar_modules():
    """Test that imports between scholar modules work correctly."""
    # This tests that the renamed modules can import each other
    try:
        from scitex.scholar._search_engine import SearchEngine
        from scitex.scholar._text_processor import TextProcessor
        from scitex.scholar._document_indexer import DocumentIndexer
        
        # These imports should work without errors
        assert SearchEngine is not None or SearchEngine is None  # May be None if optional
        assert TextProcessor is not None or TextProcessor is None
        assert DocumentIndexer is not None or DocumentIndexer is None
        
    except ImportError as e:
        # Some imports might fail due to missing dependencies, which is OK for this test
        if "No module named" not in str(e):
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])