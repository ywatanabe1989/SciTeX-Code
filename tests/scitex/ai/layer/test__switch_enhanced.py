#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 22:15:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/layer/test__switch_enhanced.py
# ----------------------------------------
"""Enhanced tests for switch function with advanced testing patterns."""

import os
import sys
import time
import gc
import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from functools import partial

try:
    from hypothesis import given, strategies as st, settings, assume
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

from scitex.ai.layer import switch, Pass

__FILE__ = "./tests/scitex/ai/layer/test__switch_enhanced.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------


class TestSwitchFunctionEnhanced:
    """Enhanced test suite for switch function with advanced testing patterns."""

    @pytest.fixture
    def layer_factory(self):
        """Factory fixture for creating various layer types."""
        def create_layer(layer_type='linear', **kwargs):
            if layer_type == 'linear':
                return nn.Linear(kwargs.get('in_features', 10), 
                               kwargs.get('out_features', 5))
            elif layer_type == 'conv2d':
                return nn.Conv2d(kwargs.get('in_channels', 3),
                               kwargs.get('out_channels', 16),
                               kwargs.get('kernel_size', 3))
            elif layer_type == 'lstm':
                return nn.LSTM(kwargs.get('input_size', 10),
                             kwargs.get('hidden_size', 20),
                             kwargs.get('num_layers', 2))
            elif layer_type == 'transformer':
                return nn.TransformerEncoderLayer(
                    d_model=kwargs.get('d_model', 512),
                    nhead=kwargs.get('nhead', 8)
                )
            elif layer_type == 'custom':
                class CustomLayer(nn.Module):
                    def __init__(self):
                        super().__init__()
                        self.param = nn.Parameter(torch.randn(10, 10))
                    def forward(self, x):
                        return x @ self.param
                return CustomLayer()
            else:
                raise ValueError(f"Unknown layer type: {layer_type}")
        return create_layer

    # Property-based testing
    if HAS_HYPOTHESIS:
        @given(
            layer_type=st.sampled_from(['linear', 'conv2d', 'lstm']),
            is_used=st.booleans(),
            input_shape=st.lists(st.integers(min_value=1, max_value=32), min_size=2, max_size=4)
        )
        @settings(max_examples=30, deadline=2000)
        def test_switch_property_based(self, layer_factory, layer_type, is_used, input_shape):
            """Property test: switch should consistently return layer or Pass."""
            # Adjust input shape based on layer type
            if layer_type == 'linear':
                input_shape = [input_shape[0], 10]  # Match in_features
            elif layer_type == 'conv2d':
                if len(input_shape) < 4:
                    input_shape = [input_shape[0], 3, 32, 32]
            elif layer_type == 'lstm':
                if len(input_shape) < 3:
                    input_shape = [input_shape[0], 5, 10]  # batch, seq, features
            
            layer = layer_factory(layer_type)
            result = switch(layer, is_used)
            
            if is_used:
                assert result is layer
            else:
                assert isinstance(result, Pass)
                assert result is not layer

        @given(
            num_switches=st.integers(min_value=1, max_value=10),
            switch_pattern=st.lists(st.booleans(), min_size=1, max_size=10)
        )
        @settings(max_examples=20, deadline=1000)
        def test_switch_chain_property(self, layer_factory, num_switches, switch_pattern):
            """Test chaining multiple switch operations."""
            layer = layer_factory('linear')
            current = layer
            
            for is_used in switch_pattern[:num_switches]:
                current = switch(current, is_used)
            
            # Final result depends on pattern
            if all(switch_pattern[:num_switches]):
                assert current is layer
            elif not switch_pattern[0]:
                assert isinstance(current, Pass)

    # Performance benchmarks
    def test_switch_performance_overhead(self, layer_factory):
        """Benchmark switch function overhead."""
        layer = layer_factory('linear', in_features=100, out_features=100)
        
        # Baseline: direct conditional
        start = time.perf_counter()
        for _ in range(10000):
            result = layer if True else Pass()
        baseline_time = time.perf_counter() - start
        
        # Switch function
        start = time.perf_counter()
        for _ in range(10000):
            result = switch(layer, True)
        switch_time = time.perf_counter() - start
        
        # Should have minimal overhead
        overhead_ratio = switch_time / baseline_time
        assert overhead_ratio < 1.5, f"Switch overhead too high: {overhead_ratio:.2f}x"

    def test_switch_memory_efficiency(self, layer_factory):
        """Test memory efficiency of switch function."""
        # Create a large layer
        large_layer = layer_factory('linear', in_features=1000, out_features=1000)
        
        # Get initial memory
        if hasattr(torch.cuda, 'memory_allocated'):
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated()
        
        # Create many switched-off layers
        switched_layers = []
        for _ in range(100):
            switched_layers.append(switch(large_layer, False))
        
        # All should be Pass instances, not copies of large_layer
        assert all(isinstance(layer, Pass) for layer in switched_layers)
        
        # Memory should not increase significantly
        if hasattr(torch.cuda, 'memory_allocated'):
            final_memory = torch.cuda.memory_allocated()
            memory_increase = final_memory - initial_memory
            # Should be minimal (just Pass instances)
            assert memory_increase < 1000000  # Less than 1MB

    # Edge cases and robustness
    def test_switch_with_mock_layers(self):
        """Test switch with mocked layer objects."""
        mock_layer = Mock(spec=nn.Module)
        mock_layer.forward = Mock(return_value=torch.randn(10, 5))
        
        # Test with True
        result_true = switch(mock_layer, True)
        assert result_true is mock_layer
        
        # Test with False
        result_false = switch(mock_layer, False)
        assert isinstance(result_false, Pass)

    def test_switch_with_wrapped_layers(self, layer_factory):
        """Test switch with wrapped/decorated layers."""
        base_layer = layer_factory('linear')
        
        # Wrap with DataParallel
        if torch.cuda.device_count() > 1:
            wrapped_layer = nn.DataParallel(base_layer)
            result = switch(wrapped_layer, True)
            assert result is wrapped_layer
        
        # Wrap with custom wrapper
        class LayerWrapper(nn.Module):
            def __init__(self, layer):
                super().__init__()
                self.layer = layer
            def forward(self, x):
                return self.layer(x)
        
        wrapped = LayerWrapper(base_layer)
        result_true = switch(wrapped, True)
        assert result_true is wrapped
        result_false = switch(wrapped, False)
        assert isinstance(result_false, Pass)

    def test_switch_with_quantized_layers(self, layer_factory):
        """Test switch with quantized layers."""
        if hasattr(torch.quantization, 'quantize_dynamic'):
            layer = layer_factory('linear')
            quantized_layer = torch.quantization.quantize_dynamic(
                layer, {nn.Linear}, dtype=torch.qint8
            )
            
            result_true = switch(quantized_layer, True)
            assert result_true is quantized_layer
            
            result_false = switch(quantized_layer, False)
            assert isinstance(result_false, Pass)

    def test_switch_with_pruned_layers(self, layer_factory):
        """Test switch with pruned layers."""
        try:
            import torch.nn.utils.prune as prune
            
            layer = layer_factory('linear')
            # Apply pruning
            prune.l1_unstructured(layer, name='weight', amount=0.3)
            
            result_true = switch(layer, True)
            assert result_true is layer
            assert hasattr(layer, 'weight_mask')  # Pruning applied
            
            result_false = switch(layer, False)
            assert isinstance(result_false, Pass)
        except ImportError:
            pass

    # Integration tests
    def test_switch_in_dynamic_architectures(self, layer_factory):
        """Test switch in dynamically constructed architectures."""
        class DynamicModel(nn.Module):
            def __init__(self, layer_config):
                super().__init__()
                self.layers = nn.ModuleList()
                
                for config in layer_config:
                    layer_type = config['type']
                    is_used = config.get('is_used', True)
                    
                    if layer_type == 'linear':
                        layer = layer_factory('linear', **config.get('params', {}))
                    elif layer_type == 'conv2d':
                        layer = layer_factory('conv2d', **config.get('params', {}))
                    else:
                        layer = nn.Identity()
                    
                    self.layers.append(switch(layer, is_used))
            
            def forward(self, x):
                for layer in self.layers:
                    x = layer(x)
                return x
        
        # Test configuration
        config = [
            {'type': 'linear', 'is_used': True, 'params': {'in_features': 10, 'out_features': 20}},
            {'type': 'linear', 'is_used': False, 'params': {'in_features': 20, 'out_features': 20}},
            {'type': 'linear', 'is_used': True, 'params': {'in_features': 20, 'out_features': 5}},
        ]
        
        model = DynamicModel(config)
        x = torch.randn(32, 10)
        output = model(x)
        
        # Should work despite middle layer being switched off
        assert output.shape == (32, 5)

    def test_switch_with_hooks(self, layer_factory):
        """Test switch with layers that have hooks."""
        layer = layer_factory('linear')
        hook_called = {'forward': False, 'backward': False}
        
        def forward_hook(module, input, output):
            hook_called['forward'] = True
            return output
        
        def backward_hook(module, grad_input, grad_output):
            hook_called['backward'] = True
        
        layer.register_forward_hook(forward_hook)
        layer.register_backward_hook(backward_hook)
        
        # Test with is_used=True
        switched_true = switch(layer, True)
        x = torch.randn(10, 10, requires_grad=True)
        output = switched_true(x)
        output.sum().backward()
        
        assert hook_called['forward']
        assert hook_called['backward']
        
        # Reset
        hook_called = {'forward': False, 'backward': False}
        
        # Test with is_used=False
        switched_false = switch(layer, False)
        x = torch.randn(10, 10, requires_grad=True)
        output = switched_false(x)
        output.sum().backward()
        
        # Hooks should not be called on Pass layer
        assert not hook_called['forward']
        assert not hook_called['backward']

    def test_switch_serialization(self, layer_factory):
        """Test serialization of models with switched layers."""
        import tempfile
        import pickle
        
        class ModelWithSwitch(nn.Module):
            def __init__(self, use_dropout=True):
                super().__init__()
                self.conv = layer_factory('conv2d')
                self.dropout = switch(nn.Dropout2d(0.5), use_dropout)
                self.fc = layer_factory('linear')
            
            def forward(self, x):
                x = self.conv(x)
                x = self.dropout(x)
                x = x.view(x.size(0), -1)
                x = self.fc(x)
                return x
        
        model = ModelWithSwitch(use_dropout=False)
        
        # Serialize
        with tempfile.NamedTemporaryFile(delete=False) as f:
            pickle.dump(model, f)
            temp_path = f.name
        
        # Deserialize
        with open(temp_path, 'rb') as f:
            loaded_model = pickle.load(f)
        
        # Verify structure
        assert isinstance(loaded_model.dropout, Pass)
        
        # Cleanup
        os.unlink(temp_path)

    # Advanced gradient tests
    def test_switch_gradient_routing(self, layer_factory):
        """Test gradient routing through switched layers."""
        # Create a model with switchable paths
        class SwitchablePathModel(nn.Module):
            def __init__(self, use_path_a=True, use_path_b=False):
                super().__init__()
                self.input_layer = nn.Linear(10, 20)
                
                # Path A
                self.path_a = switch(nn.Sequential(
                    nn.Linear(20, 30),
                    nn.ReLU(),
                    nn.Linear(30, 20)
                ), use_path_a)
                
                # Path B
                self.path_b = switch(nn.Sequential(
                    nn.Linear(20, 40),
                    nn.ReLU(),
                    nn.Linear(40, 20)
                ), use_path_b)
                
                self.output_layer = nn.Linear(20, 5)
            
            def forward(self, x):
                x = self.input_layer(x)
                x_a = self.path_a(x)
                x_b = self.path_b(x)
                x = x_a + x_b
                return self.output_layer(x)
        
        # Test different configurations
        configs = [
            (True, True),   # Both paths active
            (True, False),  # Only path A
            (False, True),  # Only path B
            (False, False), # No paths (just pass-through)
        ]
        
        for use_a, use_b in configs:
            model = SwitchablePathModel(use_a, use_b)
            x = torch.randn(5, 10, requires_grad=True)
            output = model(x)
            loss = output.sum()
            loss.backward()
            
            # Check gradients exist
            assert x.grad is not None
            assert model.input_layer.weight.grad is not None
            assert model.output_layer.weight.grad is not None

    def test_switch_with_custom_autograd(self):
        """Test switch with custom autograd functions."""
        class CustomAutogradLayer(nn.Module):
            def forward(self, x):
                return CustomOp.apply(x)
        
        class CustomOp(torch.autograd.Function):
            @staticmethod
            def forward(ctx, x):
                ctx.save_for_backward(x)
                return x * 2
            
            @staticmethod
            def backward(ctx, grad_output):
                x, = ctx.saved_tensors
                return grad_output * 2
        
        layer = CustomAutogradLayer()
        
        # Test enabled
        switched_true = switch(layer, True)
        x = torch.randn(10, requires_grad=True)
        y = switched_true(x)
        y.sum().backward()
        assert torch.allclose(x.grad, torch.ones_like(x) * 2)
        
        # Test disabled
        x.grad = None
        switched_false = switch(layer, False)
        y = switched_false(x)
        y.sum().backward()
        assert torch.allclose(x.grad, torch.ones_like(x))  # Pass gradient

    # Type safety and error handling
    def test_switch_type_validation(self):
        """Test switch with invalid inputs."""
        # Non-module input
        with pytest.raises(AttributeError):
            result = switch("not a layer", True)
        
        # None input with True
        result = switch(None, True)
        assert result is None
        
        # None input with False
        result = switch(None, False)
        assert isinstance(result, Pass)

    def test_switch_with_lazy_modules(self):
        """Test switch with lazy modules."""
        if hasattr(nn, 'LazyLinear'):
            lazy_layer = nn.LazyLinear(10)
            
            # Switch before initialization
            switched_true = switch(lazy_layer, True)
            assert switched_true is lazy_layer
            
            switched_false = switch(lazy_layer, False)
            assert isinstance(switched_false, Pass)
            
            # Initialize lazy layer
            x = torch.randn(5, 20)
            _ = lazy_layer(x)
            
            # Switch after initialization
            switched_after = switch(lazy_layer, True)
            assert switched_after is lazy_layer

    def test_switch_thread_safety(self, layer_factory):
        """Test thread safety of switch function."""
        import threading
        
        layer = layer_factory('linear')
        results = []
        errors = []
        
        def thread_func(layer, is_used, idx):
            try:
                result = switch(layer, is_used)
                results.append((idx, is_used, result))
            except Exception as e:
                errors.append((idx, e))
        
        threads = []
        for i in range(20):
            is_used = i % 2 == 0
            t = threading.Thread(target=thread_func, args=(layer, is_used, i))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 20
        
        # Verify results
        for idx, is_used, result in results:
            if is_used:
                assert result is layer
            else:
                assert isinstance(result, Pass)

    # Performance comparison tests
    def test_switch_vs_conditional_performance(self, layer_factory):
        """Compare switch performance with manual conditionals."""
        layer = layer_factory('linear', in_features=100, out_features=100)
        x = torch.randn(32, 100)
        
        # Method 1: Using switch
        def forward_with_switch(x, is_used):
            layer_to_use = switch(layer, is_used)
            return layer_to_use(x)
        
        # Method 2: Manual conditional
        def forward_with_conditional(x, is_used):
            if is_used:
                return layer(x)
            else:
                return x
        
        # Benchmark
        import timeit
        
        switch_time = timeit.timeit(
            lambda: forward_with_switch(x, True),
            number=1000
        )
        
        conditional_time = timeit.timeit(
            lambda: forward_with_conditional(x, True),
            number=1000
        )
        
        # Switch should be reasonably competitive
        ratio = switch_time / conditional_time
        assert ratio < 2.0, f"Switch is too slow compared to conditional: {ratio:.2f}x"


if __name__ == "__main__":
    pytest.main([__FILE__, "-v"])