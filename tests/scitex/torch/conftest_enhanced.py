#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 21:24:00"
# File: /tests/scitex/torch/conftest_enhanced.py
# ----------------------------------------
"""
Enhanced fixtures for torch module testing.

This conftest provides comprehensive fixtures for testing PyTorch utilities:
- Various tensor creation patterns
- Device and dtype management
- Gradient checking utilities
- Performance monitoring
- Numerical comparison helpers
- Mock objects for isolation testing
"""

import pytest
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable
import time
from contextlib import contextmanager
import warnings
from unittest.mock import MagicMock


# ============================================================================
# Tensor Creation Fixtures
# ============================================================================

@pytest.fixture
def tensor_factory():
    """Factory for creating various types of tensors."""
    def create_tensor(
        shape: Union[Tuple[int, ...], List[int]],
        dtype: torch.dtype = torch.float32,
        device: str = 'cpu',
        requires_grad: bool = False,
        fill_type: str = 'random'
    ) -> torch.Tensor:
        """Create a tensor with specified properties."""
        
        if fill_type == 'random':
            tensor = torch.randn(shape, dtype=dtype, device=device, requires_grad=requires_grad)
        elif fill_type == 'zeros':
            tensor = torch.zeros(shape, dtype=dtype, device=device, requires_grad=requires_grad)
        elif fill_type == 'ones':
            tensor = torch.ones(shape, dtype=dtype, device=device, requires_grad=requires_grad)
        elif fill_type == 'arange':
            total_elements = 1
            for dim in shape:
                total_elements *= dim
            tensor = torch.arange(total_elements, dtype=dtype, device=device).reshape(shape)
            if requires_grad and dtype.is_floating_point:
                tensor.requires_grad_(True)
        elif fill_type == 'normal':
            tensor = torch.empty(shape, dtype=dtype, device=device)
            tensor.normal_(mean=0, std=1)
            if requires_grad and dtype.is_floating_point:
                tensor.requires_grad_(True)
        elif fill_type == 'uniform':
            tensor = torch.empty(shape, dtype=dtype, device=device)
            tensor.uniform_(-1, 1)
            if requires_grad and dtype.is_floating_point:
                tensor.requires_grad_(True)
        else:
            raise ValueError(f"Unknown fill_type: {fill_type}")
        
        return tensor
    
    return create_tensor


@pytest.fixture
def special_tensors():
    """Provide tensors with special values."""
    return {
        'nan': torch.tensor([float('nan'), 1.0, 2.0]),
        'inf': torch.tensor([float('inf'), 1.0, -float('inf')]),
        'empty': torch.tensor([]),
        'scalar': torch.tensor(3.14),
        'integer': torch.tensor([1, 2, 3], dtype=torch.int64),
        'boolean': torch.tensor([True, False, True]),
        'complex': torch.tensor([1+2j, 3+4j], dtype=torch.complex64),
        'large': torch.randn(10000),
        'tiny': torch.randn(1),
        'high_dim': torch.randn(2, 3, 4, 5, 6),
    }


@pytest.fixture
def edge_case_shapes():
    """Provide edge case tensor shapes."""
    return [
        (),  # Scalar
        (0,),  # Empty 1D
        (0, 5),  # Empty rows
        (5, 0),  # Empty columns
        (1,),  # Single element
        (1, 1, 1),  # All dimensions are 1
        (1000000,),  # Very large 1D
        (1, 1, 1, 1, 1, 1, 1, 1),  # Many dimensions
    ]


# ============================================================================
# Device and Dtype Management
# ============================================================================

@pytest.fixture
def available_devices():
    """Get list of available devices."""
    devices = ['cpu']
    
    if torch.cuda.is_available():
        devices.append('cuda')
        # Add specific GPU devices if multiple available
        for i in range(torch.cuda.device_count()):
            devices.append(f'cuda:{i}')
    
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        devices.append('mps')
    
    return devices


@pytest.fixture
def all_dtypes():
    """Get all PyTorch dtypes organized by category."""
    return {
        'floating': [
            torch.float32, torch.float64, torch.float16,
            torch.bfloat16 if hasattr(torch, 'bfloat16') else None,
        ],
        'integer': [
            torch.int8, torch.int16, torch.int32, torch.int64,
            torch.uint8,
        ],
        'complex': [
            torch.complex64, torch.complex128,
        ],
        'boolean': [torch.bool],
    }


@pytest.fixture
def dtype_limits():
    """Get numerical limits for each dtype."""
    def get_limits(dtype):
        if dtype in [torch.float32, torch.float64, torch.float16]:
            info = torch.finfo(dtype)
            return {
                'min': info.min,
                'max': info.max,
                'eps': info.eps,
                'tiny': info.tiny
            }
        elif dtype in [torch.int8, torch.int16, torch.int32, torch.int64, torch.uint8]:
            info = torch.iinfo(dtype)
            return {
                'min': info.min,
                'max': info.max,
            }
        elif dtype == torch.bool:
            return {
                'min': False,
                'max': True,
            }
        else:
            return {}
    
    return get_limits


# ============================================================================
# Numerical Testing Utilities
# ============================================================================

@pytest.fixture
def allclose_with_nan():
    """Provide a function for comparing tensors that may contain NaN."""
    def compare(a: torch.Tensor, b: torch.Tensor, 
                rtol: float = 1e-5, atol: float = 1e-8) -> bool:
        """Compare tensors element-wise, treating NaN as equal."""
        if a.shape != b.shape:
            return False
        
        # Create masks for NaN values
        nan_mask_a = torch.isnan(a)
        nan_mask_b = torch.isnan(b)
        
        # NaN masks must match
        if not torch.equal(nan_mask_a, nan_mask_b):
            return False
        
        # Compare non-NaN values
        if nan_mask_a.any():
            valid_mask = ~nan_mask_a
            return torch.allclose(
                a[valid_mask], b[valid_mask], 
                rtol=rtol, atol=atol
            )
        else:
            return torch.allclose(a, b, rtol=rtol, atol=atol)
    
    return compare


@pytest.fixture
def numerical_gradient_check():
    """Provide numerical gradient checking utility."""
    def check_gradient(func: Callable, inputs: torch.Tensor, 
                      eps: float = 1e-4, atol: float = 1e-5) -> bool:
        """Check gradients using finite differences."""
        inputs = inputs.detach().requires_grad_(True)
        output = func(inputs)
        
        # Compute gradients analytically
        grad_analytical = torch.autograd.grad(
            output.sum(), inputs, create_graph=True
        )[0]
        
        # Compute gradients numerically
        grad_numerical = torch.zeros_like(inputs)
        
        for i in range(inputs.numel()):
            inputs_plus = inputs.clone()
            inputs_minus = inputs.clone()
            
            inputs_plus.view(-1)[i] += eps
            inputs_minus.view(-1)[i] -= eps
            
            output_plus = func(inputs_plus)
            output_minus = func(inputs_minus)
            
            grad_numerical.view(-1)[i] = (
                (output_plus.sum() - output_minus.sum()) / (2 * eps)
            )
        
        return torch.allclose(grad_analytical, grad_numerical, atol=atol)
    
    return check_gradient


# ============================================================================
# Performance Monitoring
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics for operations."""
    class PerformanceTracker:
        def __init__(self):
            self.timings = {}
            self.memory_usage = {}
            self.flops = {}
        
        @contextmanager
        def track(self, name: str):
            """Context manager to track operation performance."""
            # Clear GPU cache if available
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                start_memory = torch.cuda.memory_allocated()
            
            start_time = time.perf_counter()
            
            yield
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(elapsed)
            
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                end_memory = torch.cuda.memory_allocated()
                peak_memory = torch.cuda.max_memory_allocated()
                
                if name not in self.memory_usage:
                    self.memory_usage[name] = []
                self.memory_usage[name].append({
                    'allocated': end_memory - start_memory,
                    'peak': peak_memory - start_memory
                })
        
        def get_stats(self, name: str) -> Dict:
            """Get statistics for a tracked operation."""
            if name not in self.timings:
                return {}
            
            timings = self.timings[name]
            stats = {
                'count': len(timings),
                'mean_time': np.mean(timings),
                'std_time': np.std(timings),
                'min_time': np.min(timings),
                'max_time': np.max(timings),
            }
            
            if name in self.memory_usage:
                memory_data = self.memory_usage[name]
                stats['mean_memory'] = np.mean([m['allocated'] for m in memory_data])
                stats['peak_memory'] = np.max([m['peak'] for m in memory_data])
            
            return stats
        
        def print_summary(self):
            """Print performance summary."""
            print("\nPerformance Summary:")
            print("-" * 60)
            for name in self.timings:
                stats = self.get_stats(name)
                print(f"{name}:")
                print(f"  Time: {stats['mean_time']*1000:.2f} ± {stats['std_time']*1000:.2f} ms")
                if 'mean_memory' in stats:
                    print(f"  Memory: {stats['mean_memory']/1024/1024:.2f} MB")
    
    return PerformanceTracker()


# ============================================================================
# Gradient Testing Fixtures
# ============================================================================

@pytest.fixture
def gradient_test_cases():
    """Provide test cases for gradient checking."""
    def make_test_case(shape, func, requires_double=False):
        dtype = torch.float64 if requires_double else torch.float32
        x = torch.randn(shape, dtype=dtype, requires_grad=True)
        return x, func
    
    test_cases = {
        'simple_sum': lambda: make_test_case((3, 4), lambda x: x.sum()),
        'mean': lambda: make_test_case((5, 5), lambda x: x.mean()),
        'max': lambda: make_test_case((3, 4), lambda x: x.max()),
        'complex': lambda: make_test_case(
            (2, 3), 
            lambda x: (x ** 2).sum() + x.mean() * 2
        ),
        'nonlinear': lambda: make_test_case(
            (4, 4),
            lambda x: torch.sigmoid(x).sum()
        ),
    }
    
    return test_cases


@pytest.fixture
def autograd_checker():
    """Check autograd functionality."""
    def check_autograd(func, *inputs, check_backward=True, check_double_backward=False):
        """Comprehensive autograd checking."""
        # Enable gradient computation
        inputs = [x.requires_grad_(True) if x.dtype.is_floating_point else x 
                  for x in inputs]
        
        # Forward pass
        outputs = func(*inputs)
        
        # Check that output requires grad if any input does
        any_requires_grad = any(x.requires_grad for x in inputs if hasattr(x, 'requires_grad'))
        if any_requires_grad and outputs.dtype.is_floating_point:
            assert outputs.requires_grad
        
        if check_backward and outputs.requires_grad:
            # Backward pass
            grad_outputs = torch.ones_like(outputs)
            grads = torch.autograd.grad(
                outputs, inputs, grad_outputs,
                create_graph=check_double_backward,
                allow_unused=True
            )
            
            # Check gradients exist and have correct shape
            for inp, grad in zip(inputs, grads):
                if inp.requires_grad:
                    assert grad is not None
                    assert grad.shape == inp.shape
            
            if check_double_backward:
                # Second backward pass
                grad_grads = [torch.ones_like(g) if g is not None else None 
                              for g in grads]
                second_grads = torch.autograd.grad(
                    grads, inputs, grad_grads,
                    allow_unused=True
                )
                
                # Check second gradients
                for inp, grad in zip(inputs, second_grads):
                    if inp.requires_grad and grad is not None:
                        assert grad.shape == inp.shape
        
        return True
    
    return check_autograd


# ============================================================================
# Mock Objects
# ============================================================================

@pytest.fixture
def mock_tensor():
    """Provide mock tensor for testing."""
    mock = MagicMock(spec=torch.Tensor)
    mock.shape = (10, 20)
    mock.dtype = torch.float32
    mock.device = torch.device('cpu')
    mock.requires_grad = False
    mock.is_cuda = False
    mock.numel.return_value = 200
    mock.dim.return_value = 2
    
    # Add common tensor methods
    mock.size.return_value = torch.Size([10, 20])
    mock.clone.return_value = mock
    mock.detach.return_value = mock
    mock.cpu.return_value = mock
    mock.cuda.return_value = mock
    
    return mock


@pytest.fixture
def mock_module():
    """Provide mock PyTorch module."""
    mock = MagicMock(spec=torch.nn.Module)
    mock.training = True
    mock.parameters.return_value = [
        torch.randn(10, 10),
        torch.randn(10)
    ]
    mock.state_dict.return_value = {
        'weight': torch.randn(10, 10),
        'bias': torch.randn(10)
    }
    
    return mock


# ============================================================================
# Testing Utilities
# ============================================================================

@pytest.fixture
def assert_tensor_properties():
    """Provide utility for asserting tensor properties."""
    def assert_props(tensor: torch.Tensor, 
                    shape: Optional[Tuple] = None,
                    dtype: Optional[torch.dtype] = None,
                    device: Optional[Union[str, torch.device]] = None,
                    requires_grad: Optional[bool] = None,
                    is_leaf: Optional[bool] = None,
                    is_contiguous: Optional[bool] = None):
        """Assert multiple tensor properties at once."""
        if shape is not None:
            assert tensor.shape == shape, f"Expected shape {shape}, got {tensor.shape}"
        
        if dtype is not None:
            assert tensor.dtype == dtype, f"Expected dtype {dtype}, got {tensor.dtype}"
        
        if device is not None:
            expected_device = torch.device(device)
            assert tensor.device.type == expected_device.type
        
        if requires_grad is not None:
            assert tensor.requires_grad == requires_grad
        
        if is_leaf is not None:
            assert tensor.is_leaf == is_leaf
        
        if is_contiguous is not None:
            assert tensor.is_contiguous() == is_contiguous
    
    return assert_props


@pytest.fixture
def random_seed():
    """Set and restore random seeds."""
    def set_seed(seed: int = 42):
        # Save current state
        torch_state = torch.get_rng_state()
        numpy_state = np.random.get_state()
        
        # Set new seed
        torch.manual_seed(seed)
        np.random.seed(seed)
        
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        
        yield
        
        # Restore state
        torch.set_rng_state(torch_state)
        np.random.set_state(numpy_state)
    
    return set_seed


# ============================================================================
# Integration Test Helpers
# ============================================================================

@pytest.fixture
def torch_script_tester():
    """Test TorchScript compatibility."""
    def test_scriptable(module_or_func):
        """Check if module/function can be scripted."""
        try:
            if isinstance(module_or_func, torch.nn.Module):
                scripted = torch.jit.script(module_or_func)
            else:
                scripted = torch.jit.script(module_or_func)
            
            # Test that scripted version works
            if isinstance(module_or_func, torch.nn.Module):
                test_input = torch.randn(1, *module_or_func.input_shape)
                original_output = module_or_func(test_input)
                scripted_output = scripted(test_input)
                assert torch.allclose(original_output, scripted_output)
            
            return True, scripted
        except Exception as e:
            return False, str(e)
    
    return test_scriptable


@pytest.fixture
def distributed_test_helper():
    """Helper for distributed testing."""
    def setup_distributed(rank: int = 0, world_size: int = 1):
        """Setup distributed environment for testing."""
        import os
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        
        if not torch.distributed.is_initialized():
            torch.distributed.init_process_group(
                backend='gloo',  # Use gloo for CPU testing
                rank=rank,
                world_size=world_size
            )
        
        yield
        
        if torch.distributed.is_initialized():
            torch.distributed.destroy_process_group()
    
    return setup_distributed


if __name__ == "__main__":
    # Test fixtures
    pytest.main([__file__])

# EOF