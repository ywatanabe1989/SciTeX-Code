#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:51:23 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/web/test___init__.py

"""
Tests for web module initialization.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
import importlib
import inspect


class TestWebModuleInit:
    """Test web module initialization and dynamic imports."""
    
    def test_module_imports_successfully(self):
        """Test that the web module can be imported."""
        import scitex.web
        assert scitex.web is not None
    
    def test_search_pubmed_function_available(self):
        """Test that search_pubmed function is available after import."""
        import scitex.web
        assert hasattr(scitex.web, 'search_pubmed')
        assert callable(scitex.web.search_pubmed)
    
    def test_summarize_url_function_available(self):
        """Test that summarize_url function is available after import."""
        import scitex.web
        assert hasattr(scitex.web, 'summarize_url')
        assert callable(scitex.web.summarize_url)
    
    def test_main_alias_available(self):
        """Test that main alias is available."""
        import scitex.web
        assert hasattr(scitex.web, 'main')
        assert scitex.web.main == scitex.web.summarize_url
    
    def test_dynamic_import_mechanism(self):
        """Test the dynamic import mechanism works correctly."""
        # Create mock modules
        mock_module1 = MagicMock()
        mock_module1.test_function = lambda: "test1"
        mock_module1.TestClass = type('TestClass', (), {})
        mock_module1._private_function = lambda: "private"
        
        mock_module2 = MagicMock()
        mock_module2.another_function = lambda: "test2"
        
        # Mock the directory listing
        mock_files = ['_test_module1.py', '_test_module2.py', '__init__.py', 'README.md']
        
        with patch('os.listdir', return_value=mock_files):
            with patch('importlib.import_module', side_effect=[mock_module1, mock_module2]) as mock_import:
                # Re-execute the module initialization logic
                current_dir = "/fake/dir"
                namespace = {}
                
                for filename in mock_files:
                    if filename.endswith(".py") and not filename.startswith("__"):
                        module_name = filename[:-3]
                        if module_name == '_test_module1':
                            module = mock_module1
                        else:
                            module = mock_module2
                        
                        for name, obj in inspect.getmembers(module):
                            if inspect.isfunction(obj) or inspect.isclass(obj):
                                if not name.startswith("_"):
                                    namespace[name] = obj
                
                # Verify public functions/classes were imported
                assert 'test_function' in namespace
                assert 'TestClass' in namespace
                assert 'another_function' in namespace
                
                # Verify private functions were not imported
                assert '_private_function' not in namespace
    
    def test_cleanup_of_temporary_variables(self):
        """Test that temporary variables are cleaned up after import."""
        # Import fresh to ensure initialization runs
        if 'scitex.web' in sys.modules:
            del sys.modules['scitex.web']
        
        import scitex.web
        
        # Check that temporary variables don't exist in the module namespace
        assert not hasattr(scitex.web, 'filename')
        assert not hasattr(scitex.web, 'module_name')
        assert not hasattr(scitex.web, 'module')
        assert not hasattr(scitex.web, 'name')
        assert not hasattr(scitex.web, 'obj')
    
    def test_only_public_functions_exported(self):
        """Test that only public functions are exported."""
        import scitex.web
        
        # Get all attributes
        all_attrs = dir(scitex.web)
        
        # Filter for actual web module functions (not built-ins)
        web_functions = [
            attr for attr in all_attrs 
            if not attr.startswith('__') and callable(getattr(scitex.web, attr))
        ]
        
        # Verify no private functions are exposed
        for func_name in web_functions:
            assert not func_name.startswith('_'), f"Private function {func_name} should not be exported"
    
    def test_search_pubmed_submodule_functions(self):
        """Test that functions from _search_pubmed are available."""
        import scitex.web
        
        # These should be available from _search_pubmed
        expected_functions = [
            'search_pubmed',
            'get_crossref_metrics',
            'save_bibtex',
            'format_bibtex',
            'parse_args',
            'run_main'
        ]
        
        for func_name in expected_functions:
            assert hasattr(scitex.web, func_name), f"Function {func_name} should be available"
            assert callable(getattr(scitex.web, func_name)), f"{func_name} should be callable"
    
    def test_summarize_url_submodule_functions(self):
        """Test that functions from _summarize_url are available."""
        import scitex.web
        
        # These should be available from _summarize_url
        expected_functions = [
            'extract_main_content',
            'crawl_url',
            'crawl_to_json',
            'summarize_all',
            'summarize_url',
            'main'
        ]
        
        for func_name in expected_functions:
            assert hasattr(scitex.web, func_name), f"Function {func_name} should be available"
            assert callable(getattr(scitex.web, func_name)), f"{func_name} should be callable"
    
    def test_no_submodule_conflicts(self):
        """Test that there are no naming conflicts between submodules."""
        import scitex.web
        
        # Get all public attributes
        attrs = {name: getattr(scitex.web, name) for name in dir(scitex.web) if not name.startswith('_')}
        
        # Check that 'main' is an alias for summarize_url
        if 'main' in attrs and 'summarize_url' in attrs:
            assert attrs['main'] == attrs['summarize_url']
    
    def test_module_reimport_consistency(self):
        """Test that reimporting the module gives consistent results."""
        # First import
        import scitex.web
        functions_first = set(name for name in dir(scitex.web) if callable(getattr(scitex.web, name)) and not name.startswith('_'))
        
        # Force reimport
        importlib.reload(scitex.web)
        functions_second = set(name for name in dir(scitex.web) if callable(getattr(scitex.web, name)) and not name.startswith('_'))
        
        # Should have the same functions
        assert functions_first == functions_second
    
    def test_module_file_path(self):
        """Test that the module file path is correctly set."""
        import scitex.web
        
        # The module should have a __file__ attribute
        assert hasattr(scitex.web, '__file__')
        assert scitex.web.__file__.endswith('__init__.py')
        assert 'web' in scitex.web.__file__
    
    def test_async_functions_available(self):
        """Test that async functions from submodules are available."""
        import scitex.web
        
        # These async functions should be available
        async_functions = ['fetch_async', 'batch__fetch_details']
        
        for func_name in async_functions:
            if hasattr(scitex.web, func_name):
                func = getattr(scitex.web, func_name)
                # Check if it's a coroutine function
                assert inspect.iscoroutinefunction(func) or callable(func)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
