#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:15:30 (ywatanabe)"
# File: ./tests/scitex/scholar/test_scholar_init.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/scholar/test_scholar_init.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Tests for scitex scholar module initialization and imports."""

import importlib
import inspect
import sys
from pathlib import Path

import pytest


class TestScholarModuleInitialization:
    """Test suite for scholar module initialization and imports."""

    def test_module_exists(self):
        """Test that the scholar module can be imported."""
        import scitex.scholar
        assert scitex.scholar is not None
        assert hasattr(scitex, 'scholar')

    def test_core_legacy_imports(self):
        """Test that core legacy imports are available."""
        import scitex.scholar
        
        core_functions = [
            'LocalSearchEngine',
            'Paper',
            'PDFDownloader',
            'VectorSearchEngine',
            'build_index',
            'get_scholar_dir',
            'search_sync'
        ]
        
        for func_name in core_functions:
            assert hasattr(scitex.scholar, func_name), f"Core function {func_name} not found"

    def test_enhanced_functionality_graceful_import(self):
        """Test that enhanced functionality imports gracefully handle missing dependencies."""
        import scitex.scholar
        
        # These might be None if dependencies are missing, which is acceptable
        enhanced_functions = [
            'PaperAcquisition',
            'PaperMetadata',
            'search_papers_with_ai',
            'full_literature_review',
            'SemanticScholarClient',
            'S2Paper',
            'search_papers',
            'get_paper_info',
            'JournalMetrics',
            'lookup_journal_impact_factor',
            'enhance_bibliography_with_metrics'
        ]
        
        for func_name in enhanced_functions:
            # Should have the attribute, but it might be None
            assert hasattr(scitex.scholar, func_name), f"Enhanced function {func_name} not found"

    def test_optional_advanced_modules(self):
        """Test that optional advanced modules are handled gracefully."""
        import scitex.scholar
        
        optional_modules = [
            'LiteratureReviewWorkflow',
            'EnhancedVectorSearchEngine',
            'MCPServer'
        ]
        
        for module_name in optional_modules:
            # Should have the attribute, but it might be None
            assert hasattr(scitex.scholar, module_name), f"Optional module {module_name} not found"

    def test_all_exports_present(self):
        """Test that __all__ exports are properly defined."""
        import scitex.scholar
        
        assert hasattr(scitex.scholar, '__all__')
        all_exports = scitex.scholar.__all__
        
        # Check it's a list and contains expected items
        assert isinstance(all_exports, list)
        assert len(all_exports) > 0
        
        # Check core items are in __all__
        core_items = ['Paper', 'build_index', 'search_sync', 'VectorSearchEngine']
        for item in core_items:
            assert item in all_exports, f"Core item {item} not in __all__"

    def test_module_attributes(self):
        """Test module attributes and metadata."""
        import scitex.scholar
        
        # Check standard module attributes
        assert hasattr(scitex.scholar, '__file__')
        assert hasattr(scitex.scholar, '__name__')
        assert scitex.scholar.__name__ == 'scitex.scholar'
        
        module_path = scitex.scholar.__file__
        assert module_path.endswith('__init__.py')
        assert os.path.exists(module_path)

    def test_scitex_header_format(self):
        """Test that the module follows scitex header format."""
        import scitex.scholar
        
        # Check for scitex-style attributes
        assert hasattr(scitex.scholar, '__FILE__')
        assert hasattr(scitex.scholar, '__DIR__')
        
        # These should be strings
        assert isinstance(scitex.scholar.__FILE__, str)
        assert isinstance(scitex.scholar.__DIR__, str)

    def test_no_private_exports(self):
        """Test that private functions are not exposed inappropriately."""
        import scitex.scholar
        
        public_attrs = [attr for attr in dir(scitex.scholar) if not attr.startswith('_')]
        
        # Should not expose common private patterns
        # Note: 'os' might be visible due to __FILE__/__DIR__ setup, but shouldn't be in __all__
        unwanted = ['sys', 'import', 'ImportError']
        for item in unwanted:
            assert item not in public_attrs, f"Module should not export '{item}'"
            
        # Check that os is not in __all__ even if it's in dir()
        if 'os' in public_attrs:
            assert 'os' not in scitex.scholar.__all__, "Module should not export 'os' in __all__"

    def test_reimport_stability(self):
        """Test that reimporting maintains stability."""
        import scitex.scholar
        
        # Get initial function list
        initial_attrs = set(dir(scitex.scholar))
        
        # Reload module
        importlib.reload(scitex.scholar)
        
        # Check attributes are still there
        final_attrs = set(dir(scitex.scholar))
        
        # Core attributes should remain
        core_attrs = {'Paper', 'build_index', 'search_sync', '__all__'}
        for attr in core_attrs:
            assert attr in final_attrs, f"Core attribute {attr} missing after reload"

    def test_lazy_loading_compatibility(self):
        """Test that the module works with scitex's lazy loading."""
        import scitex
        
        # Should be able to access scholar through main scitex module
        assert hasattr(scitex, 'scholar')
        
        # Basic functionality should work
        assert hasattr(scitex.scholar, 'Paper')
        assert hasattr(scitex.scholar, 'search_sync')

    def test_import_error_resilience(self):
        """Test that the module is resilient to import errors in dependencies."""
        import scitex.scholar
        
        # The module should have imported successfully despite potential missing deps
        assert scitex.scholar is not None
        
        # Core functionality should always be available
        assert callable(getattr(scitex.scholar, 'Paper', None))
        assert callable(getattr(scitex.scholar, 'build_index', None))

    def test_module_docstring(self):
        """Test that module has proper documentation."""
        import scitex.scholar
        
        # Due to the way the module is structured, __doc__ might be None
        # but the source file should have a docstring
        import inspect
        try:
            source = inspect.getsource(scitex.scholar)
            assert '"""' in source, "Module source should contain docstring"
            assert 'scholar' in source.lower(), "Module should mention scholar"
        except (OSError, TypeError):
            # Fallback: check if __doc__ exists
            if scitex.scholar.__doc__ is not None:
                assert len(scitex.scholar.__doc__) > 0
                assert 'scholar' in scitex.scholar.__doc__.lower()

    def test_from_import_syntax(self):
        """Test various from-import syntaxes work correctly."""
        # Test specific imports
        from scitex.scholar import Paper, build_index, search_sync
        
        assert Paper is not None
        assert build_index is not None
        assert search_sync is not None
        
        # Test that they're callable or classes
        assert callable(Paper)
        assert callable(build_index)
        assert callable(search_sync)

    def test_namespace_cleanliness(self):
        """Test that the module doesn't pollute namespace unnecessarily."""
        import scitex.scholar
        
        # Get all public attributes
        public_attrs = [attr for attr in dir(scitex.scholar) if not attr.startswith('_')]
        
        # Should not include common library names that might leak
        unwanted_libs = ['asyncio', 'pathlib', 'tempfile', 'shutil', 'aiohttp']
        for lib in unwanted_libs:
            assert lib not in public_attrs, f"Module should not expose library '{lib}'"


class TestScholarCoreFunctionality:
    """Test core functionality of the scholar module."""

    def test_paper_class_available(self):
        """Test that Paper class is available and functional."""
        import scitex.scholar
        
        assert hasattr(scitex.scholar, 'Paper')
        Paper = scitex.scholar.Paper
        
        # Should be a class
        assert inspect.isclass(Paper)
        
        # Should be instantiable with basic parameters
        paper = Paper(
            title="Test Paper",
            authors=["Test Author"],
            abstract="Test abstract",
            source="test"
        )
        assert paper.title == "Test Paper"

    def test_search_functions_available(self):
        """Test that search functions are available."""
        import scitex.scholar
        
        assert hasattr(scitex.scholar, 'search_sync')
        assert hasattr(scitex.scholar, 'build_index')
        assert hasattr(scitex.scholar, 'get_scholar_dir')
        
        # Should be callable
        assert callable(scitex.scholar.search_sync)
        assert callable(scitex.scholar.build_index)
        assert callable(scitex.scholar.get_scholar_dir)

    def test_search_engines_available(self):
        """Test that search engine classes are available."""
        import scitex.scholar
        
        assert hasattr(scitex.scholar, 'LocalSearchEngine')
        assert hasattr(scitex.scholar, 'VectorSearchEngine')
        
        # Should be classes
        assert inspect.isclass(scitex.scholar.LocalSearchEngine)
        assert inspect.isclass(scitex.scholar.VectorSearchEngine)

    def test_enhanced_features_optional(self):
        """Test that enhanced features fail gracefully if dependencies missing."""
        import scitex.scholar
        
        # These might be None if dependencies are missing
        enhanced_attrs = ['PaperAcquisition', 'SemanticScholarClient', 'JournalMetrics']
        
        for attr_name in enhanced_attrs:
            attr = getattr(scitex.scholar, attr_name, None)
            # Should either be None or a valid callable/class
            if attr is not None:
                assert callable(attr) or inspect.isclass(attr)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF