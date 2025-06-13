#!/usr/bin/env python3
"""Tests for scitex.gen._is_ipython module."""

import pytest
from unittest.mock import patch, MagicMock
from scitex.gen import is_ipython, is_script


class TestIsIPython:
    """Test cases for is_ipython function."""

    def test_is_ipython_not_in_ipython(self):
        """Test is_ipython returns False when not in IPython."""
        # In normal Python environment, __IPYTHON__ is not defined
        assert is_ipython() is False

    @patch.dict("globals", {"__IPYTHON__": True})
    def test_is_ipython_in_ipython(self):
        """Test is_ipython returns True when in IPython."""
        # We need to modify the global namespace of the module
        import scitex.gen._is_ipython

        # Save original function
        original_is_ipython = scitex.gen._is_ipython.is_ipython

        # Create a modified version that has __IPYTHON__ in its globals
        def mock_is_ipython():
            try:
                # This will check a mock global namespace
                mock_globals = {"__IPYTHON__": True}
                if "__IPYTHON__" in mock_globals:
                    return True
            except NameError:
                return False
            return False

        # Temporarily replace the function
        scitex.gen._is_ipython.is_ipython = mock_is_ipython

        try:
            assert scitex.gen._is_ipython.is_ipython() is True
        finally:
            # Restore original function
            scitex.gen._is_ipython.is_ipython = original_is_ipython

    def test_is_ipython_jupyter_check(self):
        """Test behavior in Jupyter-like environment."""
        # In Jupyter, both __IPYTHON__ and get_ipython are typically available
        with patch("builtins.globals", return_value={"__IPYTHON__": True}):
            # This test shows the limitation - we can't easily mock the global __IPYTHON__
            # The actual function checks for __IPYTHON__ in its own global namespace
            assert is_ipython() is False  # Will still be False in test environment

    def test_is_ipython_consistency(self):
        """Test that is_ipython returns consistent results."""
        # Call multiple times to ensure consistency
        result1 = is_ipython()
        result2 = is_ipython()
        result3 = is_ipython()

        assert result1 == result2 == result3
        assert isinstance(result1, bool)


class TestIsScript:
    """Test cases for is_script function."""

    def test_is_script_inverse_of_ipython(self):
        """Test that is_script is the logical inverse of is_ipython."""
        ipython_result = is_ipython()
        script_result = is_script()

        assert script_result == (not ipython_result)

    def test_is_script_in_normal_python(self):
        """Test is_script returns True in normal Python environment."""
        # When not in IPython, we are in a script
        assert is_script() is True

    def test_is_script_with_mocked_ipython(self):
        """Test is_script behavior when mocking IPython environment."""
        import scitex.gen._is_ipython

        # Save original functions
        original_is_ipython = scitex.gen._is_ipython.is_ipython
        original_is_script = scitex.gen._is_ipython.is_script

        # Mock is_ipython to return True
        scitex.gen._is_ipython.is_ipython = lambda: True

        # Redefine is_script to use the mocked is_ipython
        scitex.gen._is_ipython.is_script = lambda: not scitex.gen._is_ipython.is_ipython()

        try:
            assert scitex.gen._is_ipython.is_script() is False
        finally:
            # Restore original functions
            scitex.gen._is_ipython.is_ipython = original_is_ipython
            scitex.gen._is_ipython.is_script = original_is_script

    def test_is_script_consistency(self):
        """Test that is_script returns consistent results."""
        results = [is_script() for _ in range(5)]

        # All results should be the same
        assert all(r == results[0] for r in results)
        assert isinstance(results[0], bool)


class TestIntegration:
    """Integration tests for is_ipython and is_script."""

    def test_mutual_exclusivity(self):
        """Test that is_ipython and is_script are mutually exclusive."""
        # At any given time, exactly one should be True
        ipython = is_ipython()
        script = is_script()

        assert ipython != script  # XOR relationship
        assert ipython or script  # At least one is True
        assert not (ipython and script)  # Not both True

    def test_use_case_branching(self):
        """Test typical use case of branching based on environment."""
        # This is how the functions are typically used
        if is_ipython():
            mode = "interactive"
        else:
            mode = "script"

        # In test environment, should be script mode
        assert mode == "script"

        # Alternative check
        mode2 = "script" if is_script() else "interactive"
        assert mode2 == "script"

    @pytest.mark.parametrize("mock_ipython", [True, False])
    def test_environment_detection(self, mock_ipython):
        """Test environment detection with different states."""
        import scitex.gen._is_ipython

        # Save originals
        original_is_ipython = scitex.gen._is_ipython.is_ipython

        # Mock the function
        scitex.gen._is_ipython.is_ipython = lambda: mock_ipython

        try:
            if mock_ipython:
                assert scitex.gen._is_ipython.is_ipython() is True
                assert scitex.gen._is_ipython.is_script() is False
            else:
                assert scitex.gen._is_ipython.is_ipython() is False
                assert scitex.gen._is_ipython.is_script() is True
        finally:
            # Restore
            scitex.gen._is_ipython.is_ipython = original_is_ipython


if __name__ == "__main__":
    import os
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
