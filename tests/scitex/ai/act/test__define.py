#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:00:00 (ywatanabe)"
# File: ./tests/scitex/ai/act/test__define.py

"""Tests for scitex.ai.act._define module."""

import pytest
import torch
import torch.nn as nn
from scitex.ai.act import define


class TestDefine:
    """Test suite for define function."""

    def test_relu_activation(self):
        """Test ReLU activation creation."""
        act = define("relu")
        assert isinstance(act, nn.ReLU)
        
        # Test functionality
        x = torch.tensor([-1.0, 0.0, 1.0])
        output = act(x)
        expected = torch.tensor([0.0, 0.0, 1.0])
        assert torch.allclose(output, expected)

    def test_swish_activation(self):
        """Test Swish (SiLU) activation creation."""
        act = define("swish")
        assert isinstance(act, nn.SiLU)
        
        # Test functionality
        x = torch.tensor([0.0, 1.0, 2.0])
        output = act(x)
        # Swish(x) = x * sigmoid(x)
        expected = x * torch.sigmoid(x)
        assert torch.allclose(output, expected)

    def test_mish_activation(self):
        """Test Mish activation creation."""
        act = define("mish")
        assert isinstance(act, nn.Mish)
        
        # Test functionality
        x = torch.tensor([0.0, 1.0, -1.0])
        output = act(x)
        # Mish is a smooth activation function
        assert output.shape == x.shape
        assert torch.all(torch.isfinite(output))

    def test_lrelu_activation(self):
        """Test LeakyReLU activation creation."""
        act = define("lrelu")
        assert isinstance(act, nn.LeakyReLU)
        assert act.negative_slope == 0.1
        
        # Test functionality
        x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
        output = act(x)
        # For negative values: output = 0.1 * input
        expected = torch.tensor([-0.2, -0.1, 0.0, 1.0, 2.0])
        assert torch.allclose(output, expected)

    def test_invalid_activation_string(self):
        """Test error handling for invalid activation string."""
        with pytest.raises(KeyError):
            define("invalid_activation")

    def test_activation_gradients(self):
        """Test that activations support gradient computation."""
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act = define(act_str)
            
            x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
            y = act(x).sum()
            y.backward()
            
            assert x.grad is not None
            assert x.grad.shape == x.shape
            assert torch.all(torch.isfinite(x.grad))

    def test_activation_batch_processing(self):
        """Test activations work with batched inputs."""
        batch_size = 4
        features = 10
        
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act = define(act_str)
            
            x = torch.randn(batch_size, features)
            output = act(x)
            
            assert output.shape == (batch_size, features)
            assert torch.all(torch.isfinite(output))

    def test_activation_inplace_operation(self):
        """Test that activations don't modify input tensors."""
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act = define(act_str)
            
            x = torch.tensor([-1.0, 0.0, 1.0])
            x_original = x.clone()
            
            _ = act(x)
            
            # Input should not be modified
            assert torch.equal(x, x_original)

    def test_activation_edge_cases(self):
        """Test activations with edge case inputs."""
        edge_cases = [
            torch.tensor([0.0]),  # Zero
            torch.tensor([1e-8]),  # Very small positive
            torch.tensor([-1e-8]),  # Very small negative
            torch.tensor([1e8]),  # Very large positive
            torch.tensor([-1e8]),  # Very large negative
            torch.tensor([float('inf')]),  # Infinity
            torch.tensor([-float('inf')]),  # Negative infinity
        ]
        
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act = define(act_str)
            
            for x in edge_cases:
                if torch.isfinite(x).all():
                    output = act(x)
                    # ReLU and LeakyReLU handle infinities
                    if act_str in ["relu", "lrelu"]:
                        assert torch.all(torch.isfinite(output) | torch.isinf(x))
                    else:
                        # Swish and Mish should handle finite inputs
                        assert torch.all(torch.isfinite(output))

    def test_activation_consistency(self):
        """Test that same activation string returns equivalent modules."""
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act1 = define(act_str)
            act2 = define(act_str)
            
            # They should be different instances
            assert act1 is not act2
            
            # But produce same results
            x = torch.randn(5, 10)
            output1 = act1(x)
            output2 = act2(x)
            assert torch.allclose(output1, output2)

    @pytest.mark.parametrize("device", [
        "cpu",
        pytest.param("cuda", marks=pytest.mark.skipif(
            not torch.cuda.is_available(), 
            reason="CUDA not available"
        ))
    ])
    def test_activation_device_compatibility(self, device):
        """Test activations work on different devices."""
        for act_str in ["relu", "swish", "mish", "lrelu"]:
            act = define(act_str)
            act = act.to(device)
            
            x = torch.randn(3, 5).to(device)
            output = act(x)
            
            assert output.device == x.device
            assert output.shape == x.shape

    def test_all_supported_activations(self):
        """Test that all documented activations are available."""
        supported = ["relu", "swish", "mish", "lrelu"]
        
        for act_str in supported:
            act = define(act_str)
            assert isinstance(act, nn.Module)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
