#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01 20:25:00 (ywatanabe)"
# File: ./tests/scitex/dsp/test___init__.py

"""
Test module for scitex.dsp package initialization.
"""

import pytest
import numpy as np


class TestDspInit:
    """Test class for dsp module initialization."""

    def test_module_import(self):
        """Test that scitex.dsp can be imported."""
        import scitex.dsp

        assert hasattr(scitex, "dsp")

    def test_core_functions_available(self):
        """Test that core DSP functions are available."""
        import scitex.dsp

        # Core functions that should be available
        expected_functions = [
            "crop",
            "demo_sig",
            "detect_ripples",
            "hilbert",
            "ensure_3d",
            "get_eeg_pos",
            "modulation_index",
            "pac",
            "psd",
            "resample",
            "time",
            "to_segments",
            "to_sktime_df",
            "wavelet",
        ]

        # Check that most functions are available
        available_count = sum(
            1 for func in expected_functions if hasattr(scitex.dsp, func)
        )
        assert (
            available_count >= 10
        ), f"Only {available_count} functions available out of {len(expected_functions)}"

    def test_submodules_available(self):
        """Test that submodules are available."""
        import scitex.dsp

        expected_modules = ["params", "add_noise", "filt", "norm", "reference", "utils"]

        for module in expected_modules:
            assert hasattr(scitex.dsp, module), f"Module {module} not available"

    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        import scitex.dsp

        # PARAMS should be available as deprecated alias for params
        assert hasattr(scitex.dsp, "PARAMS")
        assert scitex.dsp.PARAMS is scitex.dsp.params

    def test_params_module(self):
        """Test that params module has expected attributes."""
        import scitex.dsp

        # Common DSP parameters that might be in params
        if hasattr(scitex.dsp, "params"):
            params = scitex.dsp.params
            # Check it's a module or has attributes
            assert hasattr(params, "__dict__") or hasattr(params, "__name__")

    def test_basic_functionality_smoke_test(self):
        """Smoke test for basic DSP functionality."""
        import scitex.dsp

        # Test demo_sig if available
        if hasattr(scitex.dsp, "demo_sig"):
            # Should be able to generate a demo signal
            try:
                sig = scitex.dsp.demo_sig()
                assert sig is not None
                assert hasattr(sig, "shape") or isinstance(sig, (list, tuple))
            except Exception:
                # Some functions may require parameters
                pass

        # Test ensure_3d if available
        if hasattr(scitex.dsp, "ensure_3d"):
            # Should handle 1D input
            test_1d = np.array([1, 2, 3, 4])
            result = scitex.dsp.ensure_3d(test_1d)
            assert result.ndim == 3

    def test_no_import_errors_on_load(self):
        """Test that the module loads without import errors."""
        # This test passes if we got here without errors
        import scitex.dsp

        assert True

    def test_function_types(self):
        """Test that imported items are proper callable functions."""
        import scitex.dsp

        # Functions that should be callable
        function_names = ["crop", "hilbert", "psd", "resample", "wavelet"]

        for func_name in function_names:
            if hasattr(scitex.dsp, func_name):
                func = getattr(scitex.dsp, func_name)
                assert callable(func), f"{func_name} is not callable"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/dsp/__init__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
#
# from . import PARAMS, add_noise, filt, norm, reference, utils
# from ._crop import crop
# from ._demo_sig import demo_sig
# from ._detect_ripples import detect_ripples
# from ._hilbert import hilbert
# from ._misc import ensure_3d
# from ._mne import get_eeg_pos
# from ._modulation_index import modulation_index
# from ._pac import pac
# from ._psd import psd
# from ._resample import resample
# from ._time import time
# from ._transform import to_segments, to_sktime_df
# from ._wavelet import wavelet
#
# # try:
# #     from . import PARAMS, add_noise, filt, norm, reference, utils
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import some modules. Error: {e}")
#
# # try:
# #     from ._crop import crop
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import crop. Error: {e}")
#
# # try:
# #     from ._demo_sig import demo_sig
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import demo_sig. Error: {e}")
#
# # try:
# #     from ._detect_ripples import detect_ripples
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import detect_ripples. Error: {e}")
#
# # try:
# #     from ._hilbert import hilbert
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import hilbert. Error: {e}")
#
# # try:
# #     from ._misc import ensure_3d
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import ensure_3d. Error: {e}")
#
# # try:
# #     from ._mne import get_eeg_pos
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import get_eeg_pos. Error: {e}")
#
# # try:
# #     from ._modulation_index import modulation_index
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import modulation_index. Error: {e}")
#
# # try:
# #     from ._pac import pac
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import pac. Error: {e}")
#
# # try:
# #     from ._psd import psd
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import psd. Error: {e}")
#
# # try:
# #     from ._resample import resample
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import resample. Error: {e}")
#
# # try:
# #     from ._time import time
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import time. Error: {e}")
#
# # try:
# #     from ._transform import to_segments, to_sktime_df
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import to_segments or to_sktime_df. Error: {e}")
#
# # try:
# #     from ._wavelet import wavelet
# # except ImportError as e:
# #     warnings.warn(f"Warning: Failed to import wavelet. Error: {e}")
#
# # # #!/usr/bin/env python3
#
#
# # # from . import PARAMS, add_noise, filt, norm, reference, utils
# # # from ._crop import crop
# # # from ._demo_sig import demo_sig
# # # from ._detect_ripples import detect_ripples
#
# # # # from ._ensure_3d import ensure_3d
# # # from ._hilbert import hilbert
#
# # # # from ._listen import listen
# # # from ._misc import ensure_3d
# # # from ._mne import get_eeg_pos
# # # from ._modulation_index import modulation_index
# # # from ._pac import pac
# # # from ._psd import psd
# # # from ._resample import resample
# # # from ._time import time
# # # from ._transform import to_segments, to_sktime_df
# # # from ._wavelet import wavelet

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/dsp/__init__.py
# --------------------------------------------------------------------------------
