#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 21:50:00 (ywatanabe)"
# File: tests/scitex/nn/test__TransposeLayer.py

"""
Tests for TransposeLayer module.

This module tests:
1. Basic transpose functionality
2. Different axis combinations
3. Various tensor shapes (2D, 3D, 4D, 5D)
4. Error handling and edge cases
5. Integration with PyTorch autograd
6. Device compatibility (CPU/GPU)
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import TransposeLayer


class TestTransposeLayerBasics:
    """Test basic functionality of TransposeLayer."""
    
    def test_instantiation(self):
        """Test that TransposeLayer can be instantiated with valid parameters."""
        layer = TransposeLayer(0, 1)
        assert isinstance(layer, nn.Module)
        assert layer.axis1 == 0
        assert layer.axis2 == 1
        
    def test_forward_2d_tensor(self):
        """Test transpose operation on 2D tensors."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(3, 4)
        output = layer(x)
        
        assert output.shape == (4, 3)
        assert torch.allclose(output, x.transpose(0, 1))
        
    def test_forward_3d_tensor(self):
        """Test transpose operation on 3D tensors."""
        layer = TransposeLayer(1, 2)
        x = torch.randn(2, 3, 4)
        output = layer(x)
        
        assert output.shape == (2, 4, 3)
        assert torch.allclose(output, x.transpose(1, 2))
        
    def test_forward_4d_tensor(self):
        """Test transpose operation on 4D tensors (common in CNNs)."""
        layer = TransposeLayer(2, 3)
        x = torch.randn(8, 16, 32, 64)  # batch, channels, height, width
        output = layer(x)
        
        assert output.shape == (8, 16, 64, 32)
        assert torch.allclose(output, x.transpose(2, 3))
        
    def test_forward_5d_tensor(self):
        """Test transpose operation on 5D tensors."""
        layer = TransposeLayer(3, 4)
        x = torch.randn(2, 3, 4, 5, 6)
        output = layer(x)
        
        assert output.shape == (2, 3, 4, 6, 5)
        assert torch.allclose(output, x.transpose(3, 4))


class TestTransposeLayerAxisCombinations:
    """Test different axis combinations."""
    
    def test_transpose_batch_channel(self):
        """Test transposing batch and channel dimensions."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(10, 3, 28, 28)  # Common image tensor
        output = layer(x)
        
        assert output.shape == (3, 10, 28, 28)
        
    def test_transpose_spatial_dimensions(self):
        """Test transposing spatial dimensions (height and width)."""
        layer = TransposeLayer(2, 3)
        x = torch.randn(1, 3, 224, 224)  # ImageNet-like tensor
        output = layer(x)
        
        assert output.shape == (1, 3, 224, 224)  # Square image remains same
        
        # Non-square image
        x_rect = torch.randn(1, 3, 100, 200)
        output_rect = layer(x_rect)
        assert output_rect.shape == (1, 3, 200, 100)
        
    def test_transpose_non_adjacent_axes(self):
        """Test transposing non-adjacent axes."""
        layer = TransposeLayer(0, 3)
        x = torch.randn(2, 3, 4, 5)
        output = layer(x)
        
        assert output.shape == (5, 3, 4, 2)
        assert torch.allclose(output, x.transpose(0, 3))
        
    def test_transpose_same_axis(self):
        """Test transposing same axis (should return unchanged)."""
        layer = TransposeLayer(1, 1)
        x = torch.randn(2, 3, 4)
        output = layer(x)
        
        assert output.shape == x.shape
        assert torch.allclose(output, x)


class TestTransposeLayerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_element_tensor(self):
        """Test transpose on single element tensor."""
        layer = TransposeLayer(0, 1)
        x = torch.tensor([[5.0]])
        output = layer(x)
        
        assert output.shape == (1, 1)
        assert output.item() == 5.0
        
    def test_empty_tensor(self):
        """Test transpose on empty tensor."""
        layer = TransposeLayer(0, 1)
        x = torch.empty(0, 5)
        output = layer(x)
        
        assert output.shape == (5, 0)
        
    def test_negative_axis_indices(self):
        """Test using negative axis indices."""
        layer = TransposeLayer(-2, -1)
        x = torch.randn(2, 3, 4, 5)
        output = layer(x)
        
        # -2 is axis 2, -1 is axis 3
        assert output.shape == (2, 3, 5, 4)
        assert torch.allclose(output, x.transpose(-2, -1))
        
    def test_invalid_axis_error(self):
        """Test that invalid axis raises appropriate error."""
        layer = TransposeLayer(0, 5)  # axis 5 doesn't exist for most tensors
        x = torch.randn(2, 3, 4)
        
        with pytest.raises((IndexError, RuntimeError)):
            output = layer(x)


class TestTransposeLayerGradients:
    """Test gradient flow through TransposeLayer."""
    
    def test_gradient_flow(self):
        """Test that gradients flow correctly through transpose."""
        layer = TransposeLayer(1, 2)
        x = torch.randn(2, 3, 4, requires_grad=True)
        output = layer(x)
        
        # Create a loss and backpropagate
        loss = output.sum()
        loss.backward()
        
        assert x.grad is not None
        assert x.grad.shape == x.shape
        
    def test_gradient_correctness(self):
        """Test gradient values are correct."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(3, 4, requires_grad=True)
        
        # Forward pass
        output = layer(x)
        
        # Create gradient for output
        grad_output = torch.randn_like(output)
        output.backward(grad_output)
        
        # The gradient should be transposed back
        expected_grad = grad_output.transpose(0, 1)
        assert torch.allclose(x.grad, expected_grad)
        
    def test_multiple_transposes_gradient(self):
        """Test gradient through multiple transpose operations."""
        layer1 = TransposeLayer(0, 1)
        layer2 = TransposeLayer(1, 2)
        x = torch.randn(2, 3, 4, requires_grad=True)
        
        output = layer2(layer1(x))
        loss = output.mean()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()


class TestTransposeLayerDeviceCompatibility:
    """Test TransposeLayer on different devices."""
    
    def test_cpu_operation(self):
        """Test transpose operation on CPU."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(3, 4)
        output = layer(x)
        
        assert output.device == x.device
        assert output.device.type == 'cpu'
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_operation(self):
        """Test transpose operation on CUDA."""
        layer = TransposeLayer(0, 1).cuda()
        x = torch.randn(3, 4).cuda()
        output = layer(x)
        
        assert output.device == x.device
        assert output.device.type == 'cuda'
        assert torch.allclose(output.cpu(), x.cpu().transpose(0, 1))
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cpu_to_cuda_transfer(self):
        """Test moving layer from CPU to CUDA."""
        layer = TransposeLayer(1, 2)
        x_cpu = torch.randn(2, 3, 4)
        
        # Test on CPU first
        output_cpu = layer(x_cpu)
        
        # Move to CUDA
        layer = layer.cuda()
        x_cuda = x_cpu.cuda()
        output_cuda = layer(x_cuda)
        
        assert torch.allclose(output_cpu, output_cuda.cpu())


class TestTransposeLayerIntegration:
    """Test TransposeLayer integration with other PyTorch components."""
    
    def test_sequential_model(self):
        """Test TransposeLayer in Sequential model."""
        model = nn.Sequential(
            nn.Linear(10, 20),
            TransposeLayer(0, 1),
            nn.ReLU()
        )
        
        x = torch.randn(5, 10)
        output = model(x)
        
        # After linear: (5, 20), after transpose: (20, 5)
        assert output.shape == (20, 5)
        
    def test_with_conv_layers(self):
        """Test TransposeLayer with convolutional layers."""
        model = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            TransposeLayer(2, 3),  # Swap height and width
            nn.Conv2d(16, 32, 3, padding=1)
        )
        
        x = torch.randn(1, 3, 28, 32)  # Non-square input
        output = model(x)
        
        # After first conv: (1, 16, 28, 32)
        # After transpose: (1, 16, 32, 28)
        # After second conv: (1, 32, 32, 28)
        assert output.shape == (1, 32, 32, 28)
        
    def test_state_dict_serialization(self):
        """Test that TransposeLayer can be saved and loaded."""
        layer = TransposeLayer(2, 3)
        state_dict = layer.state_dict()
        
        # TransposeLayer has no parameters, so state_dict should be empty
        assert len(state_dict) == 0
        
        # Create new layer and load state dict
        new_layer = TransposeLayer(2, 3)
        new_layer.load_state_dict(state_dict)
        
        # Test they behave the same
        x = torch.randn(1, 2, 3, 4)
        assert torch.allclose(layer(x), new_layer(x))


class TestTransposeLayerSpecialCases:
    """Test special use cases of TransposeLayer."""
    
    def test_batch_first_to_time_first(self):
        """Test converting batch-first to time-first for RNNs."""
        # Common use case: (batch, time, features) -> (time, batch, features)
        layer = TransposeLayer(0, 1)
        x = torch.randn(32, 100, 256)  # batch_size=32, seq_len=100, features=256
        output = layer(x)
        
        assert output.shape == (100, 32, 256)
        
    def test_channel_last_to_channel_first(self):
        """Test converting channel-last to channel-first format."""
        # (batch, height, width, channels) -> (batch, channels, height, width)
        layer1 = TransposeLayer(1, 3)  # Move channels from last to second
        layer2 = TransposeLayer(2, 3)  # Fix the ordering
        
        x = torch.randn(8, 224, 224, 3)  # Channel-last format
        output = layer2(layer1(x))
        
        assert output.shape == (8, 3, 224, 224)  # Channel-first format
        
    def test_preserves_contiguity_when_possible(self):
        """Test memory layout preservation."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(3, 4)
        
        assert x.is_contiguous()
        output = layer(x)
        
        # Transpose generally breaks contiguity
        # This is expected behavior
        assert output.shape == (4, 3)


class TestTransposeLayerDtypes:
    """Test TransposeLayer with different data types."""
    
    def test_float_tensors(self):
        """Test with different float precisions."""
        layer = TransposeLayer(0, 1)
        
        # Float32
        x_f32 = torch.randn(3, 4, dtype=torch.float32)
        output_f32 = layer(x_f32)
        assert output_f32.dtype == torch.float32
        
        # Float64
        x_f64 = torch.randn(3, 4, dtype=torch.float64)
        output_f64 = layer(x_f64)
        assert output_f64.dtype == torch.float64
        
        # Float16
        x_f16 = torch.randn(3, 4, dtype=torch.float16)
        output_f16 = layer(x_f16)
        assert output_f16.dtype == torch.float16
        
    def test_integer_tensors(self):
        """Test with integer tensors."""
        layer = TransposeLayer(0, 1)
        
        # Int32
        x_i32 = torch.randint(0, 10, (3, 4), dtype=torch.int32)
        output_i32 = layer(x_i32)
        assert output_i32.dtype == torch.int32
        
        # Int64
        x_i64 = torch.randint(0, 10, (3, 4), dtype=torch.int64)
        output_i64 = layer(x_i64)
        assert output_i64.dtype == torch.int64
        
    def test_bool_tensors(self):
        """Test with boolean tensors."""
        layer = TransposeLayer(0, 1)
        x = torch.tensor([[True, False], [False, True], [True, True]])
        output = layer(x)
        
        assert output.dtype == torch.bool
        assert output.shape == (2, 3)


class TestTransposeLayerAttributes:
    """Test TransposeLayer attributes and methods."""
    
    def test_repr(self):
        """Test string representation of TransposeLayer."""
        layer = TransposeLayer(1, 2)
        repr_str = repr(layer)
        
        assert 'TransposeLayer' in repr_str
        
    def test_parameters(self):
        """Test that TransposeLayer has no learnable parameters."""
        layer = TransposeLayer(0, 1)
        
        # Should have no parameters
        assert len(list(layer.parameters())) == 0
        
        # Should have no buffers
        assert len(list(layer.buffers())) == 0
        
    def test_training_eval_mode(self):
        """Test behavior in training and eval modes."""
        layer = TransposeLayer(0, 1)
        x = torch.randn(3, 4)
        
        # Training mode
        layer.train()
        output_train = layer(x)
        
        # Eval mode
        layer.eval()
        output_eval = layer(x)
        
        # Should behave the same in both modes
        assert torch.allclose(output_train, output_eval)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_TransposeLayer.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-30 07:26:35 (ywatanabe)"
#
# import torch.nn as nn
#
#
# class TransposeLayer(nn.Module):
#     def __init__(
#         self,
#         axis1,
#         axis2,
#     ):
#         super().__init__()
#         self.axis1 = axis1
#         self.axis2 = axis2
#
#     def forward(self, x):
#         return x.transpose(self.axis1, self.axis2)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_TransposeLayer.py
# --------------------------------------------------------------------------------
