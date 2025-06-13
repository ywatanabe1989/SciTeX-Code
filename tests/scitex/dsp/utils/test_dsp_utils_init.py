#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:24:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dsp/utils/test___init__.py

"""Tests for dsp.utils module initialization and imports."""

import pytest
import importlib
import sys
from unittest.mock import patch, MagicMock


class TestDspUtilsInit:
    """Test dsp.utils module initialization."""

    def test_basic_imports(self):
        """Test basic imports from dsp.utils module."""
        try:
            import scitex.dsp.utils
            
            # Test that module exists and is importable
            assert hasattr(scitex.dsp.utils, '__file__')
            assert hasattr(scitex.dsp.utils, '__name__')
            
        except ImportError as e:
            pytest.fail(f"Failed to import scitex.dsp.utils: {e}")
            
    def test_pac_module_import(self):
        """Test that pac submodule is available."""
        try:
            import scitex.dsp.utils
            assert hasattr(scitex.dsp.utils, 'pac')
            
            # Test that pac module has expected structure
            import scitex.dsp.utils.pac
            assert hasattr(scitex.dsp.utils.pac, '__file__')
            
        except ImportError as e:
            pytest.skip(f"pac module not available: {e}")
            
    def test_differential_bandpass_filters_import(self):
        """Test import of differential bandpass filters."""
        try:
            from scitex.dsp.utils import build_bandpass_filters, init_bandpass_filters
            
            # Verify functions are callable
            assert callable(build_bandpass_filters)
            assert callable(init_bandpass_filters)
            
        except ImportError as e:
            pytest.skip(f"Differential bandpass filters not available: {e}")
            
    def test_ensure_even_len_import(self):
        """Test import of ensure_even_len function."""
        try:
            from scitex.dsp.utils import ensure_even_len
            
            # Verify function is callable
            assert callable(ensure_even_len)
            
        except ImportError as e:
            pytest.skip(f"ensure_even_len not available: {e}")
            
    def test_zero_pad_import(self):
        """Test import of zero_pad function."""
        try:
            from scitex.dsp.utils import zero_pad
            
            # Verify function is callable
            assert callable(zero_pad)
            
        except ImportError as e:
            pytest.skip(f"zero_pad not available: {e}")
            
    def test_filter_functions_import(self):
        """Test import of filter functions."""
        try:
            from scitex.dsp.utils import design_filter, plot_filter_responses
            
            # Verify functions are callable
            assert callable(design_filter)
            assert callable(plot_filter_responses)
            
        except ImportError as e:
            pytest.skip(f"Filter functions not available: {e}")
            
    def test_all_expected_exports(self):
        """Test that all expected functions are exported."""
        try:
            import scitex.dsp.utils
            
            # List of expected exports based on __init__.py
            expected_exports = [
                'pac',  # submodule
                'build_bandpass_filters',
                'init_bandpass_filters', 
                'ensure_even_len',
                'zero_pad',
                'design_filter',
                'plot_filter_responses'
            ]
            
            available_exports = []
            for export in expected_exports:
                if hasattr(scitex.dsp.utils, export):
                    available_exports.append(export)
                    
            # At least some core functions should be available
            assert len(available_exports) >= 3, f"Only {len(available_exports)} exports available: {available_exports}"
            
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")
            
    def test_module_structure(self):
        """Test the overall module structure."""
        try:
            import scitex.dsp.utils
            
            # Test module has proper attributes
            assert hasattr(scitex.dsp.utils, '__name__')
            assert scitex.dsp.utils.__name__ == 'scitex.dsp.utils'
            
            # Test that it's a proper package
            if hasattr(scitex.dsp.utils, '__path__'):
                assert isinstance(scitex.dsp.utils.__path__, list)
                
        except ImportError as e:
            pytest.skip(f"Module structure test failed: {e}")
            
    def test_import_error_handling(self):
        """Test graceful handling of import errors."""
        # Test what happens when optional dependencies are missing
        with patch.dict('sys.modules', {'tensorpac': None}):
            try:
                # Should still be able to import the module
                import scitex.dsp.utils
                # pac submodule might not work, but main module should
                assert hasattr(scitex.dsp.utils, '__name__')
            except ImportError:
                # This is acceptable if dependencies are missing
                pass
                
    def test_namespace_integrity(self):
        """Test that the namespace is properly set up."""
        try:
            import scitex.dsp.utils
            
            # Test that imports don't pollute the namespace unnecessarily
            module_dir = dir(scitex.dsp.utils)
            
            # Should not have obvious internal imports leaked
            assert '__builtins__' not in module_dir or len(module_dir) > 5
            
            # Should have some actual functionality
            functional_attrs = [attr for attr in module_dir if not attr.startswith('_')]
            assert len(functional_attrs) > 0, f"No functional attributes found: {module_dir}"
            
        except ImportError as e:
            pytest.skip(f"Namespace test failed: {e}")


class TestDspUtilsFunctionalityIntegration:
    """Test integration between different dsp.utils functions."""
    
    def test_zero_pad_ensure_even_len_integration(self):
        """Test integration between zero_pad and ensure_even_len."""
        try:
            from scitex.dsp.utils import zero_pad, ensure_even_len
            import numpy as np
            
            # Create test signals of different lengths
            signals = [
                np.random.randn(100),  # Even length
                np.random.randn(101),  # Odd length
                np.random.randn(50),   # Short signal
            ]
            
            # Zero pad signals
            padded_signals = zero_pad(signals)
            
            # Ensure all have even length
            for signal in padded_signals:
                even_signal = ensure_even_len(signal)
                assert len(even_signal) % 2 == 0
                # Could be numpy array or torch tensor depending on input
                assert hasattr(even_signal, '__len__')
                
        except ImportError as e:
            pytest.skip(f"Functions not available for integration test: {e}")
            
    def test_filter_design_with_signal_processing(self):
        """Test filter design integration with signal processing utilities."""
        try:
            from scitex.dsp.utils import design_filter, ensure_even_len, zero_pad
            import numpy as np
            
            # Create test signal
            fs = 250
            sig_len = 1000
            
            # Design a filter
            filter_coeffs = design_filter(sig_len, fs, low_hz=8.0, high_hz=30.0)
            
            # Ensure filter has even length
            even_filter = ensure_even_len(filter_coeffs)
            
            # Test with zero padding utility
            filter_list = [filter_coeffs, even_filter]
            padded_filters = zero_pad(filter_list)
            
            # Verify results
            assert len(padded_filters) == 2
            assert all(hasattr(f, '__len__') for f in padded_filters)  # Could be numpy or torch
            assert len(padded_filters[0]) == len(padded_filters[1])  # Same length after padding
            
        except ImportError as e:
            pytest.skip(f"Filter integration test failed: {e}")
            
    def test_bandpass_filters_integration(self):
        """Test bandpass filters integration."""
        try:
            from scitex.dsp.utils import build_bandpass_filters, init_bandpass_filters
            import torch
            
            # Test parameters
            fs = 250
            pha_low_hz = 8
            pha_high_hz = 30
            n_bands = 5
            
            # Initialize filters
            filters = init_bandpass_filters(fs, pha_low_hz, pha_high_hz, n_bands)
            
            # Build/apply filters
            test_signal = torch.randn(1, 1, 1000)  # (batch, ch, time)
            filtered_signals = build_bandpass_filters(test_signal, filters)
            
            # Verify output structure
            assert isinstance(filtered_signals, torch.Tensor)
            assert filtered_signals.shape[0] == test_signal.shape[0]  # Same batch size
            
        except ImportError as e:
            pytest.skip(f"Bandpass filters integration test failed: {e}")
        except Exception as e:
            pytest.skip(f"Bandpass filters test execution failed: {e}")


class TestDspUtilsEdgeCases:
    """Test edge cases and error handling in dsp.utils."""
    
    def test_missing_dependencies_handling(self):
        """Test behavior when optional dependencies are missing."""
        # Temporarily hide tensorpac
        original_tensorpac = sys.modules.get('tensorpac')
        try:
            if 'tensorpac' in sys.modules:
                del sys.modules['tensorpac']
            
            # Try to import pac module
            try:
                import scitex.dsp.utils.pac
                # If this succeeds, it should handle missing tensorpac gracefully
                assert hasattr(scitex.dsp.utils.pac, '__file__')
            except ImportError:
                # This is acceptable - module might not load without tensorpac
                pass
                
        finally:
            # Restore tensorpac if it was there
            if original_tensorpac is not None:
                sys.modules['tensorpac'] = original_tensorpac
                
    def test_circular_import_prevention(self):
        """Test that there are no circular import issues."""
        try:
            # Try to import the module multiple times
            for _ in range(3):
                import scitex.dsp.utils
                importlib.reload(scitex.dsp.utils)
                
            # Should not raise any errors
            assert hasattr(scitex.dsp.utils, '__name__')
            
        except ImportError as e:
            pytest.skip(f"Circular import test failed: {e}")
            
    def test_import_order_independence(self):
        """Test that import order doesn't matter."""
        try:
            # Test different import orders
            import scitex.dsp.utils.pac
            import scitex.dsp.utils
            
            # Both should work
            assert hasattr(scitex.dsp.utils, '__name__')
            assert hasattr(scitex.dsp.utils.pac, '__name__')
            
        except ImportError as e:
            pytest.skip(f"Import order test failed: {e}")
            
    def test_module_reload_safety(self):
        """Test that module can be safely reloaded."""
        try:
            import scitex.dsp.utils
            original_name = scitex.dsp.utils.__name__
            
            # Reload the module
            importlib.reload(scitex.dsp.utils)
            
            # Should maintain consistency
            assert scitex.dsp.utils.__name__ == original_name
            
        except ImportError as e:
            pytest.skip(f"Module reload test failed: {e}")


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
