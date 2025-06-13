#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:35:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/reproduce/test__fix_seeds.py

"""Comprehensive tests for random seed fixing functionality."""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from scitex.reproduce import fix_seeds


class TestFixSeedsBasic:
    """Test basic seed fixing functionality."""

    def test_function_exists(self):
        """Test that fix_seeds function is importable."""
        assert callable(fix_seeds)

    def test_no_packages_specified(self):
        """Test fix_seeds with no packages specified."""
        # Should run without errors when no packages are specified
        fix_seeds(verbose=False)

    def test_default_parameters(self):
        """Test fix_seeds with default parameters."""
        # Default should use seed=42, verbose=True
        with patch('builtins.print') as mock_print:
            fix_seeds()
            # Should print verbose output by default
            mock_print.assert_called()

    def test_custom_seed(self):
        """Test fix_seeds with custom seed value."""
        custom_seed = 12345
        with patch('builtins.print') as mock_print:
            fix_seeds(seed=custom_seed, verbose=True)
            # Check that custom seed appears in output
            call_args = str(mock_print.call_args_list)
            assert str(custom_seed) in call_args

    def test_verbose_false(self):
        """Test fix_seeds with verbose=False."""
        with patch('builtins.print') as mock_print:
            fix_seeds(verbose=False)
            # Should not print when verbose=False
            mock_print.assert_not_called()


class TestFixSeedsOsModule:
    """Test OS environment variable seed fixing."""

    def test_os_seed_setting(self):
        """Test that OS environment variable is set correctly."""
        import os as os_module
        
        # Test with os module
        test_seed = 999
        fix_seeds(os=os_module, seed=test_seed, verbose=False)
        
        # Check that PYTHONHASHSEED was set
        assert os.environ.get("PYTHONHASHSEED") == str(test_seed)

    def test_os_seed_string_conversion(self):
        """Test that seed is properly converted to string for OS."""
        import os as os_module
        
        # Test with different seed types
        for seed_val in [42, 0, 999999]:
            fix_seeds(os=os_module, seed=seed_val, verbose=False)
            assert os.environ.get("PYTHONHASHSEED") == str(seed_val)

    def test_os_none_no_action(self):
        """Test that no OS action taken when os=None."""
        original_env = os.environ.get("PYTHONHASHSEED")
        
        fix_seeds(os=None, seed=777, verbose=False)
        
        # Environment should not change
        assert os.environ.get("PYTHONHASHSEED") == original_env


class TestFixSeedsRandomModule:
    """Test random module seed fixing."""

    @patch('random.seed')
    def test_random_seed_called(self, mock_random_seed):
        """Test that random.seed is called with correct value."""
        import random
        
        test_seed = 555
        fix_seeds(random=random, seed=test_seed, verbose=False)
        
        mock_random_seed.assert_called_once_with(test_seed)

    def test_random_none_no_action(self):
        """Test that no random action taken when random=None."""
        with patch('random.seed') as mock_random_seed:
            fix_seeds(random=None, seed=123, verbose=False)
            mock_random_seed.assert_not_called()

    @patch('random.seed')
    def test_random_with_different_seeds(self, mock_random_seed):
        """Test random seed setting with various seed values."""
        import random
        
        for seed_val in [0, 1, 42, 99999]:
            mock_random_seed.reset_mock()
            fix_seeds(random=random, seed=seed_val, verbose=False)
            mock_random_seed.assert_called_once_with(seed_val)


class TestFixSeedsNumpyModule:
    """Test numpy module seed fixing."""

    def test_numpy_seed_setting(self):
        """Test numpy random seed setting."""
        try:
            import numpy as np
            
            # Mock numpy random seed
            with patch.object(np.random, 'seed') as mock_np_seed:
                test_seed = 888
                fix_seeds(np=np, seed=test_seed, verbose=False)
                mock_np_seed.assert_called_once_with(test_seed)
                
        except ImportError:
            pytest.skip("NumPy not available")

    def test_numpy_none_no_action(self):
        """Test that no numpy action taken when np=None."""
        try:
            import numpy as np
            with patch.object(np.random, 'seed') as mock_np_seed:
                fix_seeds(np=None, seed=123, verbose=False)
                mock_np_seed.assert_not_called()
        except ImportError:
            pytest.skip("NumPy not available")

    def test_numpy_without_import(self):
        """Test behavior when numpy is not available."""
        # Create a mock object that acts like numpy
        mock_np = Mock()
        mock_np.random.seed = Mock()
        
        fix_seeds(np=mock_np, seed=456, verbose=False)
        mock_np.random.seed.assert_called_once_with(456)


class TestFixSeedsTorchModule:
    """Test PyTorch module seed fixing."""

    def test_torch_seed_setting(self):
        """Test PyTorch seed setting with all required functions."""
        # Create comprehensive mock torch module
        mock_torch = Mock()
        mock_torch.manual_seed = Mock()
        mock_torch.cuda.manual_seed = Mock()
        mock_torch.cuda.manual_seed_all = Mock()
        mock_torch.backends.cudnn = Mock()
        
        test_seed = 777
        fix_seeds(torch=mock_torch, seed=test_seed, verbose=False)
        
        # Verify all torch seed functions were called
        mock_torch.manual_seed.assert_called_once_with(test_seed)
        mock_torch.cuda.manual_seed.assert_called_once_with(test_seed)
        mock_torch.cuda.manual_seed_all.assert_called_once_with(test_seed)
        
        # Verify deterministic setting
        assert mock_torch.backends.cudnn.deterministic is True

    def test_torch_none_no_action(self):
        """Test that no torch action taken when torch=None."""
        mock_torch = Mock()
        fix_seeds(torch=None, seed=123, verbose=False)
        
        # Mock should not be called
        mock_torch.manual_seed.assert_not_called()

    def test_torch_deterministic_setting(self):
        """Test that deterministic mode is properly set."""
        mock_torch = Mock()
        mock_torch.backends.cudnn = Mock()
        
        fix_seeds(torch=mock_torch, seed=333, verbose=False)
        
        # Check deterministic was set to True
        assert mock_torch.backends.cudnn.deterministic is True


class TestFixSeedsTensorFlowModule:
    """Test TensorFlow module seed fixing."""

    def test_tensorflow_seed_setting(self):
        """Test TensorFlow random seed setting."""
        mock_tf = Mock()
        mock_tf.random.set_seed = Mock()
        
        test_seed = 999
        fix_seeds(tf=mock_tf, seed=test_seed, verbose=False)
        
        mock_tf.random.set_seed.assert_called_once_with(test_seed)

    def test_tensorflow_none_no_action(self):
        """Test that no tensorflow action taken when tf=None."""
        mock_tf = Mock()
        fix_seeds(tf=None, seed=123, verbose=False)
        
        mock_tf.random.set_seed.assert_not_called()

    def test_tensorflow_different_seeds(self):
        """Test tensorflow with various seed values."""
        mock_tf = Mock()
        mock_tf.random.set_seed = Mock()
        
        for seed_val in [0, 1, 42, 100000]:
            mock_tf.random.set_seed.reset_mock()
            fix_seeds(tf=mock_tf, seed=seed_val, verbose=False)
            mock_tf.random.set_seed.assert_called_once_with(seed_val)


class TestFixSeedsMultiplePackages:
    """Test seed fixing with multiple packages simultaneously."""

    def test_all_packages_together(self):
        """Test fixing seeds for all packages at once."""
        import os as os_module
        import random
        
        # Create mocks for packages that might not be available
        mock_np = Mock()
        mock_np.random.seed = Mock()
        mock_torch = Mock()
        mock_torch.manual_seed = Mock()
        mock_torch.cuda.manual_seed = Mock()
        mock_torch.cuda.manual_seed_all = Mock()
        mock_torch.backends.cudnn = Mock()
        mock_tf = Mock()
        mock_tf.random.set_seed = Mock()
        
        test_seed = 12345
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(
                os=os_module,
                random=random,
                np=mock_np,
                torch=mock_torch,
                tf=mock_tf,
                seed=test_seed,
                verbose=False
            )
            
            # Verify all were called
            assert os.environ.get("PYTHONHASHSEED") == str(test_seed)
            mock_random_seed.assert_called_once_with(test_seed)
            mock_np.random.seed.assert_called_once_with(test_seed)
            mock_torch.manual_seed.assert_called_once_with(test_seed)
            mock_tf.random.set_seed.assert_called_once_with(test_seed)

    def test_partial_packages(self):
        """Test with only some packages specified."""
        import random
        mock_np = Mock()
        mock_np.random.seed = Mock()
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(
                random=random,
                np=mock_np,
                seed=567,
                verbose=False
            )
            
            mock_random_seed.assert_called_once_with(567)
            mock_np.random.seed.assert_called_once_with(567)


class TestFixSeedsVerboseOutput:
    """Test verbose output functionality."""

    def test_verbose_output_format(self):
        """Test that verbose output contains expected elements."""
        import random
        
        with patch('builtins.print') as mock_print:
            fix_seeds(random=random, seed=789, verbose=True)
            
            # Check that print was called
            assert mock_print.call_count > 0
            
            # Get all print call arguments
            all_calls = [str(call) for call in mock_print.call_args_list]
            output = ' '.join(all_calls)
            
            # Check for expected content
            assert '789' in output  # Seed value
            assert 'random' in output.lower()  # Package name
            assert 'seed' in output.lower()  # Word "seed"

    def test_verbose_package_names(self):
        """Test that package names appear in verbose output."""
        import random
        mock_np = Mock()
        mock_np.random.seed = Mock()
        
        with patch('builtins.print') as mock_print:
            fix_seeds(
                random=random,
                np=mock_np,
                seed=111,
                verbose=True
            )
            
            output = str(mock_print.call_args_list)
            assert 'random' in output
            assert 'np' in output

    def test_verbose_separator_lines(self):
        """Test that verbose output includes separator lines."""
        with patch('builtins.print') as mock_print:
            fix_seeds(seed=222, verbose=True)
            
            output = str(mock_print.call_args_list)
            # Should contain dashes for separator
            assert '-' in output


class TestFixSeedsEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_seed(self):
        """Test with seed value of 0."""
        import random
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(random=random, seed=0, verbose=False)
            mock_random_seed.assert_called_once_with(0)

    def test_negative_seed(self):
        """Test with negative seed value."""
        import random
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(random=random, seed=-1, verbose=False)
            mock_random_seed.assert_called_once_with(-1)

    def test_large_seed(self):
        """Test with very large seed value."""
        import random
        large_seed = 2**31 - 1
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(random=random, seed=large_seed, verbose=False)
            mock_random_seed.assert_called_once_with(large_seed)

    def test_string_seed_conversion(self):
        """Test that numeric seeds work with string conversion for OS."""
        import os as os_module
        
        # Test various numeric types
        test_cases = [
            (42, "42"),
            (42.0, "42.0"),  # Float converts to "42.0"
            (int(42), "42")
        ]
        
        for seed_val, expected_str in test_cases:
            fix_seeds(os=os_module, seed=seed_val, verbose=False)
            assert os.environ.get("PYTHONHASHSEED") == expected_str


class TestFixSeedsIntegration:
    """Integration tests for complete workflows."""

    def test_reproducible_random_generation(self):
        """Test that fixed seeds produce reproducible results."""
        import random
        
        # Fix seed and generate some random numbers
        fix_seeds(random=random, seed=42, verbose=False)
        first_numbers = [random.random() for _ in range(5)]
        
        # Fix seed again and generate same sequence
        fix_seeds(random=random, seed=42, verbose=False)
        second_numbers = [random.random() for _ in range(5)]
        
        # Should be identical
        assert first_numbers == second_numbers

    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results."""
        import random
        
        # Generate with seed 1
        fix_seeds(random=random, seed=1, verbose=False)
        first_numbers = [random.random() for _ in range(5)]
        
        # Generate with seed 2
        fix_seeds(random=random, seed=2, verbose=False)
        second_numbers = [random.random() for _ in range(5)]
        
        # Should be different
        assert first_numbers != second_numbers

    def test_scientific_workflow_simulation(self):
        """Test simulating a typical scientific workflow."""
        import random
        
        # Simulate fixing seeds for reproducible science
        mock_np = Mock()
        mock_np.random.seed = Mock()
        mock_torch = Mock()
        mock_torch.manual_seed = Mock()
        mock_torch.cuda.manual_seed = Mock()
        mock_torch.cuda.manual_seed_all = Mock()
        mock_torch.backends.cudnn = Mock()
        
        # Fix all seeds for reproducible ML experiment
        experiment_seed = 2024
        
        with patch('random.seed') as mock_random_seed:
            fix_seeds(
                random=random,
                np=mock_np,
                torch=mock_torch,
                seed=experiment_seed,
                verbose=False
            )
            
            # Verify all components were seeded
            mock_random_seed.assert_called_once_with(experiment_seed)
            mock_np.random.seed.assert_called_once_with(experiment_seed)
            mock_torch.manual_seed.assert_called_once_with(experiment_seed)
            assert mock_torch.backends.cudnn.deterministic is True


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
