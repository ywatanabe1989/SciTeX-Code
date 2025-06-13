#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:20:00 (ywatanabe)"
# File: tests/scitex/dev/test___init__.py

import pytest
from unittest.mock import patch, MagicMock, mock_open
import threading
import time
import sys


class TestDevModule:
    """Test suite for scitex.dev module."""

    def test_code_flow_analyzer_import(self):
        """Test that CodeFlowAnalyzer can be imported from scitex.dev."""
        from scitex.dev import CodeFlowAnalyzer
        
        assert CodeFlowAnalyzer is not None
        assert hasattr(CodeFlowAnalyzer, '__init__')

    def test_reload_import(self):
        """Test that reload function can be imported from scitex.dev."""
        from scitex.dev import reload
        
        assert callable(reload)
        assert hasattr(reload, '__call__')

    def test_reload_auto_import(self):
        """Test that reload_auto function can be imported from scitex.dev."""
        from scitex.dev import reload_auto
        
        assert callable(reload_auto)
        assert hasattr(reload_auto, '__call__')

    def test_module_attributes(self):
        """Test that scitex.dev module has expected attributes."""
        import scitex.dev
        
        assert hasattr(scitex.dev, 'CodeFlowAnalyzer')
        assert hasattr(scitex.dev, 'reload')
        assert hasattr(scitex.dev, 'reload_auto')
        
        # Check that they're the right types
        assert isinstance(scitex.dev.CodeFlowAnalyzer, type)  # It's a class
        assert callable(scitex.dev.reload)
        assert callable(scitex.dev.reload_auto)

    def test_dynamic_import_mechanism(self):
        """Test that the dynamic import mechanism works correctly."""
        import scitex.dev
        
        # Check that functions/classes are available after dynamic import
        assert hasattr(scitex.dev, 'CodeFlowAnalyzer')
        assert hasattr(scitex.dev, 'reload')
        assert hasattr(scitex.dev, 'reload_auto')
        
        # Check that cleanup variables are not present
        assert not hasattr(scitex.dev, 'os')
        assert not hasattr(scitex.dev, 'importlib')
        assert not hasattr(scitex.dev, 'inspect')
        assert not hasattr(scitex.dev, 'current_dir')

    def test_code_flow_analyzer_initialization(self):
        """Test CodeFlowAnalyzer class initialization."""
        from scitex.dev import CodeFlowAnalyzer
        
        test_file_path = "/path/to/test/file.py"
        analyzer = CodeFlowAnalyzer(test_file_path)
        
        assert analyzer.file_path == test_file_path
        assert hasattr(analyzer, 'execution_flow')
        assert hasattr(analyzer, 'sequence')
        assert hasattr(analyzer, 'skip_functions')
        
        # Check initial values
        assert analyzer.execution_flow == []
        assert analyzer.sequence == 1
        assert isinstance(analyzer.skip_functions, (set, list, dict))

    def test_code_flow_analyzer_skip_functions(self):
        """Test that CodeFlowAnalyzer has expected skip functions."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("test.py")
        
        # Check that common built-in functions are in skip list
        skip_functions = analyzer.skip_functions
        expected_skips = ["__init__", "__main__", "print", "len", "str"]
        
        for func in expected_skips:
            assert func in skip_functions, f"Function '{func}' should be in skip_functions"

    def test_reload_basic_functionality(self):
        """Test basic reload functionality with mocked modules."""
        from scitex.dev import reload
        
        # Mock sys.modules to simulate scitex modules
        original_modules = sys.modules.copy()
        
        try:
            # Add fake scitex modules to sys.modules
            fake_scitex = MagicMock()
            fake_scitex_sub = MagicMock()
            sys.modules['scitex'] = fake_scitex
            sys.modules['scitex.fake_submodule'] = fake_scitex_sub
            
            with patch('importlib.reload') as mock_reload:
                # Mock the final scitex reload to return the fake module
                mock_reload.return_value = fake_scitex
                
                result = reload()
                
                # Should have called reload on scitex modules
                assert mock_reload.called
                assert result is not None
                
        finally:
            # Restore original sys.modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_reload_handles_exceptions(self):
        """Test that reload handles exceptions gracefully."""
        from scitex.dev import reload
        
        original_modules = sys.modules.copy()
        
        try:
            # Add fake scitex modules that will raise exceptions
            fake_problematic_module = MagicMock()
            sys.modules['scitex'] = MagicMock()
            sys.modules['scitex.problematic'] = fake_problematic_module
            
            with patch('importlib.reload') as mock_reload:
                # Make some reloads fail
                def side_effect(module):
                    if module == fake_problematic_module:
                        raise ImportError("Test error")
                    return module
                
                mock_reload.side_effect = side_effect
                
                # Should not raise exception despite individual failures
                result = reload()
                assert result is not None
                
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_reload_auto_basic_functionality(self):
        """Test reload_auto basic functionality with mocking."""
        from scitex.dev import reload_auto
        
        with patch('scitex.dev._reload.reload') as mock_reload:
            with patch('threading.Thread') as mock_thread:
                with patch('time.sleep') as mock_sleep:
                    
                    # Create a mock thread
                    mock_thread_instance = MagicMock()
                    mock_thread.return_value = mock_thread_instance
                    
                    # Call reload_auto with short interval
                    reload_auto(interval=1)
                    
                    # Should create a thread
                    mock_thread.assert_called_once()
                    
                    # Should start the thread
                    mock_thread_instance.start.assert_called_once()

    def test_reload_auto_custom_interval(self):
        """Test reload_auto with custom interval."""
        from scitex.dev import reload_auto
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Test with custom interval
            custom_interval = 5
            reload_auto(interval=custom_interval)
            
            # Check that thread was created
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    def test_reload_thread_management(self):
        """Test that reload_auto properly manages threads."""
        from scitex.dev import reload_auto
        import scitex.dev._reload as reload_module
        
        # Reset module state
        reload_module._running = False
        reload_module._reload_thread = None
        
        with patch('threading.Thread') as mock_thread:
            with patch('time.sleep') as mock_sleep:
                mock_thread_instance = MagicMock()
                mock_thread.return_value = mock_thread_instance
                
                # Start auto-reload
                reload_auto(interval=1)
                
                # Should create and start thread
                assert mock_thread.called
                assert mock_thread_instance.start.called

    def test_code_flow_analyzer_methods(self):
        """Test that CodeFlowAnalyzer has expected methods."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("test.py")
        
        # Check for expected methods (these might vary based on implementation)
        methods = dir(analyzer)
        
        # Should have basic Python object methods
        assert '__init__' in methods
        assert '__dict__' in methods or hasattr(analyzer, '__dict__')

    def test_reload_function_signature(self):
        """Test reload function signature."""
        from scitex.dev import reload
        import inspect
        
        sig = inspect.signature(reload)
        params = list(sig.parameters.keys())
        
        # reload() should take no parameters
        assert len(params) == 0

    def test_reload_auto_function_signature(self):
        """Test reload_auto function signature."""
        from scitex.dev import reload_auto
        import inspect
        
        sig = inspect.signature(reload_auto)
        params = list(sig.parameters.keys())
        
        # Should have interval parameter
        assert 'interval' in params
        
        # Check default value
        interval_param = sig.parameters['interval']
        assert interval_param.default == 10

    def test_code_flow_analyzer_with_mock_file(self):
        """Test CodeFlowAnalyzer with mocked file system."""
        from scitex.dev import CodeFlowAnalyzer
        
        fake_file_path = "/fake/path/test.py"
        
        # Should not crash even with non-existent file
        analyzer = CodeFlowAnalyzer(fake_file_path)
        assert analyzer.file_path == fake_file_path

    def test_reload_return_type(self):
        """Test that reload returns something (module-like object)."""
        from scitex.dev import reload
        
        with patch('importlib.reload') as mock_reload:
            # Mock to return a fake module
            fake_scitex = MagicMock()
            mock_reload.return_value = fake_scitex
            
            result = reload()
            
            # Should return the reloaded module
            assert result is not None

    def test_module_docstrings(self):
        """Test that imported classes/functions have docstrings."""
        from scitex.dev import CodeFlowAnalyzer, reload, reload_auto
        
        # Check docstrings exist
        assert hasattr(reload, '__doc__')
        assert reload.__doc__ is not None
        assert 'reload' in reload.__doc__.lower()

    def test_dev_module_integration(self):
        """Test integration between dev module components."""
        from scitex.dev import CodeFlowAnalyzer, reload, reload_auto
        
        # All should be importable and callable/instantiable
        analyzer = CodeFlowAnalyzer("test.py")
        assert analyzer is not None
        
        # Functions should be callable
        assert callable(reload)
        assert callable(reload_auto)

    def test_threading_safety(self):
        """Test that reload functions handle threading safely."""
        from scitex.dev import reload_auto
        import scitex.dev._reload as reload_module
        
        # Reset state
        reload_module._running = False
        reload_module._reload_thread = None
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Should be able to call multiple times safely
            reload_auto(interval=1)
            reload_auto(interval=2)
            
            # Should create threads
            assert mock_thread.called

    def test_code_flow_analyzer_file_path_handling(self):
        """Test CodeFlowAnalyzer handles different file path formats."""
        from scitex.dev import CodeFlowAnalyzer
        
        test_paths = [
            "/absolute/path/file.py",
            "relative/path/file.py",
            "file.py",
            "/path/with spaces/file.py",
            "/path/with-dashes/file_with_underscores.py"
        ]
        
        for path in test_paths:
            analyzer = CodeFlowAnalyzer(path)
            assert analyzer.file_path == path

    def test_reload_module_filtering(self):
        """Test that reload only affects scitex modules."""
        from scitex.dev import reload
        
        original_modules = sys.modules.copy()
        
        try:
            # Add both scitex and non-scitex modules
            sys.modules['scitex'] = MagicMock()
            sys.modules['scitex.test'] = MagicMock()
            sys.modules['numpy'] = MagicMock()  # Non-scitex module
            sys.modules['other_package'] = MagicMock()  # Non-scitex module
            
            with patch('importlib.reload') as mock_reload:
                mock_reload.return_value = MagicMock()
                
                reload()
                
                # Should only reload scitex modules
                reloaded_modules = [call[0][0] for call in mock_reload.call_args_list]
                
                # Check that only scitex modules were reloaded
                for module in reloaded_modules:
                    if hasattr(module, '__name__'):
                        module_name = module.__name__
                    else:
                        # For mock objects, we need to check differently
                        continue
                    
                    # Skip the final scitex reload
                    if module_name and not module_name.startswith('scitex'):
                        pytest.fail(f"Non-scitex module {module_name} was reloaded")
                        
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
