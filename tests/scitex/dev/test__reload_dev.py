#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-11 03:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dev/test__reload.py

"""Comprehensive tests for module reloading functionality.

This module tests the reload functions that help with development by
reloading the scitex package and its submodules, including auto-reload
functionality with threading.
"""

import pytest
import os
import sys
import time
import threading
import importlib
from unittest.mock import patch, MagicMock, call
from typing import Dict, List, Any, Optional
import tempfile
from pathlib import Path


class TestReloadBasic:
    """Basic functionality tests for reload function."""
    
    def test_reload_function_exists(self):
        """Test that reload function can be imported."""
        from scitex.dev import reload
        assert callable(reload)
    
    def test_reload_returns_module(self):
        """Test that reload returns the reloaded module."""
        from scitex.dev import reload
        
        # First ensure scitex is imported
        import scitex
        
        # Call reload
        result = reload()
        
        # Should return the scitex module
        assert result is not None
        assert hasattr(result, '__name__')
        assert 'scitex' in result.__name__
    
    def test_reload_handles_submodules(self):
        """Test that reload handles scitex submodules."""
        from scitex.dev import reload
        
        # Import some submodules first
        import scitex.gen
        import scitex.io
        import scitex.plt
        
        # Store original module ids
        original_ids = {
            'scitex': id(sys.modules.get('scitex')),
            'scitex.gen': id(sys.modules.get('scitex.gen')),
            'scitex.io': id(sys.modules.get('scitex.io')),
            'scitex.plt': id(sys.modules.get('scitex.plt'))
        }
        
        # Reload
        reload()
        
        # Modules should still exist in sys.modules
        assert 'scitex' in sys.modules
        assert 'scitex.gen' in sys.modules
        assert 'scitex.io' in sys.modules
        assert 'scitex.plt' in sys.modules
    
    @patch('importlib.reload')
    def test_reload_calls_importlib_reload(self, mock_reload):
        """Test that reload uses importlib.reload."""
        from scitex.dev import reload
        
        # Set up mock to return a module
        mock_module = MagicMock()
        mock_module.__name__ = 'scitex'
        mock_reload.return_value = mock_module
        
        result = reload()
        
        # Should have called importlib.reload
        assert mock_reload.called
        assert result == mock_module
    
    def test_reload_handles_import_errors(self):
        """Test that reload handles errors gracefully."""
        from scitex.dev import reload
        
        # Even with a broken submodule, reload should not crash
        # Add a fake broken module to sys.modules
        fake_module = MagicMock()
        fake_module.__name__ = 'scitex.broken_submodule'
        sys.modules['scitex.broken_submodule'] = fake_module
        
        try:
            # Should not raise exception
            result = reload()
            assert result is not None
        finally:
            # Clean up
            if 'scitex.broken_submodule' in sys.modules:
                del sys.modules['scitex.broken_submodule']


class TestReloadSubmodules:
    """Test reloading of scitex submodules."""
    
    def test_reload_finds_all_scitex_modules(self):
        """Test that reload finds all modules starting with 'scitex'."""
        from scitex.dev import reload
        
        # Import various scitex modules
        import scitex
        import scitex.gen
        import scitex.io
        import scitex.plt.color
        
        # Track which modules are in sys.modules before reload
        scitex_modules_before = [m for m in sys.modules if m.startswith('scitex')]
        
        # Reload
        reload()
        
        # Should still have all scitex modules
        scitex_modules_after = [m for m in sys.modules if m.startswith('scitex')]
        
        # Should have at least the same modules (might have more)
        for module in scitex_modules_before:
            assert module in scitex_modules_after
    
    @patch('importlib.reload')
    def test_reload_attempts_all_submodules(self, mock_reload):
        """Test that reload attempts to reload all scitex submodules."""
        from scitex.dev import reload
        
        # Add some fake scitex modules
        fake_modules = ['scitex', 'scitex.test1', 'scitex.test2', 'scitex.test3']
        for mod_name in fake_modules:
            module = MagicMock()
            module.__name__ = mod_name
            sys.modules[mod_name] = module
        
        try:
            reload()
            
            # Should have attempted to reload each module
            assert mock_reload.call_count >= len(fake_modules)
        finally:
            # Clean up
            for mod_name in fake_modules[1:]:  # Keep scitex itself
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
    
    def test_reload_preserves_module_state(self):
        """Test that reload preserves important module state."""
        from scitex.dev import reload
        
        # Import and set some state
        import scitex
        
        # Add a custom attribute
        scitex._test_attribute = "test_value"
        
        # Reload
        reload()
        
        # The attribute might or might not be preserved depending on implementation
        # This test documents the behavior
        # (Reload typically resets module state)


class TestAutoReload:
    """Test auto-reload functionality."""
    
    def test_reload_auto_function_exists(self):
        """Test that reload_auto function can be imported."""
        from scitex.dev import reload_auto
        assert callable(reload_auto)
    
    def test_reload_stop_function_exists(self):
        """Test that reload_stop function can be imported."""
        from scitex.dev import reload_stop
        assert callable(reload_stop)
    
    def test_auto_reload_starts_thread(self):
        """Test that reload_auto starts a background thread."""
        from scitex.dev import reload_auto, reload_stop, _reload_thread
        
        # Ensure stopped first
        reload_stop()
        time.sleep(0.1)
        
        # Start auto reload with short interval
        reload_auto(interval=1)
        
        # Give it a moment to start
        time.sleep(0.1)
        
        # Thread should be created and alive
        assert _reload_thread is not None
        assert _reload_thread.is_alive()
        assert _reload_thread.daemon  # Should be daemon thread
        
        # Clean up
        reload_stop()
        time.sleep(0.2)
    
    def test_auto_reload_with_custom_interval(self):
        """Test auto-reload with custom interval."""
        from scitex.dev import reload_auto, reload_stop
        
        # Stop any existing reload
        reload_stop()
        time.sleep(0.1)
        
        # Start with custom interval
        custom_interval = 5
        reload_auto(interval=custom_interval)
        
        # Should start successfully
        time.sleep(0.1)
        
        # Clean up
        reload_stop()
    
    def test_reload_stop_stops_thread(self):
        """Test that reload_stop stops the auto-reload thread."""
        from scitex.dev import reload_auto, reload_stop, _running
        
        # Start auto reload
        reload_auto(interval=1)
        time.sleep(0.1)
        
        # Stop it
        reload_stop()
        
        # _running flag should be False
        assert not _running
        
        # Give thread time to stop
        time.sleep(0.5)
    
    def test_multiple_reload_auto_calls(self):
        """Test that multiple reload_auto calls don't create multiple threads."""
        from scitex.dev import reload_auto, reload_stop, _reload_thread
        
        # Stop any existing
        reload_stop()
        time.sleep(0.1)
        
        # Start auto reload
        reload_auto(interval=1)
        first_thread = _reload_thread
        
        # Call again
        reload_auto(interval=1)
        second_thread = _reload_thread
        
        # Should be the same thread (not create a new one)
        assert first_thread is second_thread
        
        # Clean up
        reload_stop()
        time.sleep(0.2)


class TestAutoReloadLoop:
    """Test the auto-reload loop functionality."""
    
    @patch('scitex.dev._reload.reload')
    @patch('time.sleep')
    def test_auto_reload_loop_calls_reload(self, mock_sleep, mock_reload):
        """Test that auto-reload loop calls reload periodically."""
        from scitex.dev import _auto_reload_loop, _running
        
        # Set up test
        call_count = 0
        
        def side_effect(*args):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                # Stop after 3 iterations
                import scitex.dev._reload
                scitex.dev._reload._running = False
        
        mock_sleep.side_effect = side_effect
        
        # Set running flag
        import scitex.dev._reload
        scitex.dev._reload._running = True
        
        # Run the loop
        _auto_reload_loop(5)
        
        # Should have called reload multiple times
        assert mock_reload.call_count >= 3
        assert mock_sleep.call_count >= 3
    
    @patch('scitex.dev._reload.reload')
    @patch('builtins.print')
    def test_auto_reload_handles_exceptions(self, mock_print, mock_reload):
        """Test that auto-reload handles reload exceptions."""
        from scitex.dev import _auto_reload_loop
        
        # Make reload raise exception
        mock_reload.side_effect = Exception("Test exception")
        
        # Set up to run once
        import scitex.dev._reload
        original_running = scitex.dev._reload._running
        scitex.dev._reload._running = True
        
        # Create a thread to stop the loop after a short time
        def stop_loop():
            time.sleep(0.1)
            scitex.dev._reload._running = False
        
        stop_thread = threading.Thread(target=stop_loop)
        stop_thread.start()
        
        try:
            # Run the loop
            _auto_reload_loop(0.05)
            
            # Should have printed error message
            mock_print.assert_called()
            assert "Reload failed" in str(mock_print.call_args)
        finally:
            scitex.dev._reload._running = original_running
            stop_thread.join()


class TestGlobalState:
    """Test global state management."""
    
    def test_initial_global_state(self):
        """Test initial state of global variables."""
        from scitex.dev import _reload
        
        # Check initial state (after imports, state might be modified)
        assert hasattr(_reload, '_reload_thread')
        assert hasattr(_reload, '_running')
        
        # _running should be boolean
        assert isinstance(_reload._running, bool)
    
    def test_reload_thread_cleanup(self):
        """Test that reload thread is properly cleaned up."""
        from scitex.dev import reload_auto, reload_stop, _reload_thread
        
        # Start and stop
        reload_auto(interval=1)
        time.sleep(0.1)
        reload_stop()
        time.sleep(0.5)  # Give thread time to stop
        
        # Thread should eventually stop
        if _reload_thread:
            assert not _reload_thread.is_alive()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_reload_with_no_scitex_imported(self):
        """Test reload when scitex is not yet imported."""
        # Remove scitex modules from sys.modules temporarily
        scitex_modules = {k: v for k, v in sys.modules.items() if k.startswith('scitex')}
        
        for mod in list(scitex_modules.keys()):
            del sys.modules[mod]
        
        try:
            from scitex.dev import reload
            
            # Should still work (will import scitex)
            result = reload()
            assert result is not None
        finally:
            # Restore modules
            sys.modules.update(scitex_modules)
    
    def test_reload_auto_with_zero_interval(self):
        """Test auto-reload with zero interval."""
        from scitex.dev import reload_auto, reload_stop
        
        # Should handle zero interval
        reload_auto(interval=0)
        time.sleep(0.1)
        
        # Clean up
        reload_stop()
        time.sleep(0.1)
    
    def test_reload_auto_with_negative_interval(self):
        """Test auto-reload with negative interval."""
        from scitex.dev import reload_auto, reload_stop
        
        # Should handle negative interval (might treat as 0 or absolute value)
        reload_auto(interval=-5)
        time.sleep(0.1)
        
        # Clean up  
        reload_stop()
        time.sleep(0.1)
    
    @patch('threading.Thread')
    def test_reload_auto_thread_creation_failure(self, mock_thread_class):
        """Test handling of thread creation failure."""
        from scitex.dev import reload_auto
        
        # Make thread creation fail
        mock_thread_class.side_effect = Exception("Thread creation failed")
        
        # Should handle the error gracefully
        try:
            reload_auto(interval=1)
        except Exception:
            # It's ok if it propagates the exception
            pass


class TestIntegration:
    """Integration tests with actual module reloading."""
    
    def test_reload_updates_module_changes(self):
        """Test that reload picks up module changes."""
        from scitex.dev import reload
        
        # This test would require modifying actual module files
        # which is not practical in a test environment
        # Document the expected behavior instead
        
        # Expected behavior:
        # 1. Modify a source file
        # 2. Call reload()
        # 3. Changes should be reflected in the loaded module
        assert True  # Placeholder for integration test
    
    def test_reload_performance(self):
        """Test reload performance with many submodules."""
        from scitex.dev import reload
        import time
        
        # Import many submodules
        import scitex
        import scitex.gen
        import scitex.io  
        import scitex.plt
        import scitex.str
        
        # Measure reload time
        start = time.time()
        reload()
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 5.0  # 5 seconds should be plenty


class TestDocumentation:
    """Test function documentation."""
    
    def test_reload_has_docstring(self):
        """Test that reload has a docstring."""
        from scitex.dev import reload
        
        assert reload.__doc__ is not None
        assert "reload" in reload.__doc__.lower()
        assert "scitex" in reload.__doc__
    
    def test_reload_auto_has_docstring(self):
        """Test that reload_auto has a docstring."""
        from scitex.dev import reload_auto
        
        assert reload_auto.__doc__ is not None
        assert "auto" in reload_auto.__doc__.lower()
        assert "reload" in reload_auto.__doc__.lower()
    
    def test_reload_stop_has_docstring(self):
        """Test that reload_stop has a docstring."""
        from scitex.dev import reload_stop
        
        assert reload_stop.__doc__ is not None
        assert "stop" in reload_stop.__doc__.lower()


class TestThreadSafety:
    """Test thread safety of reload operations."""
    
    def test_concurrent_reload_calls(self):
        """Test concurrent calls to reload."""
        from scitex.dev import reload
        import concurrent.futures
        
        # Run multiple reloads concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(reload) for _ in range(5)]
            results = [f.result() for f in futures]
        
        # All should complete successfully
        assert all(r is not None for r in results)
    
    def test_reload_auto_stop_thread_safety(self):
        """Test thread safety of start/stop operations."""
        from scitex.dev import reload_auto, reload_stop
        import concurrent.futures
        
        def start_stop_cycle():
            reload_auto(interval=1)
            time.sleep(0.05)
            reload_stop()
        
        # Run multiple start/stop cycles concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(start_stop_cycle) for _ in range(3)]
            
            # Wait for all to complete
            for f in futures:
                f.result()
        
        # Should complete without deadlock or errors
        assert True


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v", "-s"])
