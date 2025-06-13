#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 (ywatanabe)"
# /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/nn/test__MNet_1000.py

"""Comprehensive test suite for MNet1000 neural network architecture."""

import pytest
import torch
import torch.nn as nn
import numpy as np
from scitex.nn import MNet1000, MNet_1000, SwapLayer, ReshapeLayer, MNet_config


class TestMNet1000Architecture:
    """Test MNet1000 architecture and initialization."""
    
    def test_basic_instantiation(self):
        """Test basic model instantiation with default config."""
        model = MNet1000(MNet_config)
        assert isinstance(model, nn.Module)
        assert hasattr(model, 'config')
        assert hasattr(model, 'backborn')
        assert hasattr(model, 'fc')
        
    def test_backward_compatibility_alias(self):
        """Test that MNet_1000 alias works for backward compatibility."""
        model = MNet_1000(MNet_config)
        assert isinstance(model, MNet1000)
        
    def test_custom_config(self):
        """Test instantiation with custom configuration."""
        custom_config = {
            "classes": ["A", "B", "C"],
            "n_chs": 128,
            "n_fc1": 512,
            "d_ratio1": 0.5,
            "n_fc2": 128,
            "d_ratio2": 0.5,
        }
        model = MNet1000(custom_config)
        assert model.config == custom_config
        # Check output dimension matches number of classes
        assert model.fc[-1].out_features == 3
        
    def test_backbone_structure(self):
        """Test the backbone convolutional structure."""
        model = MNet1000(MNet_config)
        # Check backbone contains expected layers
        backbone_modules = list(model.backborn.modules())
        conv_layers = [m for m in backbone_modules if isinstance(m, nn.Conv2d)]
        assert len(conv_layers) == 4
        # Verify kernel sizes
        assert conv_layers[0].kernel_size == (270, 4)
        assert conv_layers[1].kernel_size == (1, 4)
        assert conv_layers[2].kernel_size == (8, 12)
        assert conv_layers[3].kernel_size == (1, 5)
        
    def test_fc_structure(self):
        """Test the fully connected layer structure."""
        model = MNet1000(MNet_config)
        fc_modules = list(model.fc.modules())
        linear_layers = [m for m in fc_modules if isinstance(m, nn.Linear)]
        assert len(linear_layers) == 2
        assert linear_layers[0].in_features == 1024
        assert linear_layers[0].out_features == 256
        assert linear_layers[1].in_features == 256
        assert linear_layers[1].out_features == 2


class TestMNet1000ForwardPass:
    """Test forward pass functionality."""
    
    def test_forward_pass_basic(self):
        """Test basic forward pass with standard input."""
        model = MNet1000(MNet_config)
        BS, N_CHS, SEQ_LEN = 4, 270, 1000
        x = torch.randn(BS, N_CHS, SEQ_LEN)
        output = model(x)
        assert output.shape == (BS, 2)
        
    def test_forward_pass_different_batch_sizes(self):
        """Test forward pass with various batch sizes."""
        model = MNet1000(MNet_config)
        N_CHS, SEQ_LEN = 270, 1000
        for batch_size in [1, 8, 16, 32]:
            x = torch.randn(batch_size, N_CHS, SEQ_LEN)
            output = model(x)
            assert output.shape == (batch_size, 2)
            
    def test_forward_bb_method(self):
        """Test forward_bb method for backbone features."""
        model = MNet1000(MNet_config)
        BS, N_CHS, SEQ_LEN = 4, 270, 1000
        x = torch.randn(BS, N_CHS, SEQ_LEN)
        features = model.forward_bb(x)
        assert features.shape == (BS, 1024)
        
    def test_reshape_input_static_method(self):
        """Test _reshape_input static method."""
        BS, N_CHS, SEQ_LEN = 4, 270, 1000
        x = torch.randn(BS, N_CHS, SEQ_LEN)
        reshaped = MNet1000._reshape_input(x, N_CHS)
        assert reshaped.shape == (BS, 1, N_CHS, SEQ_LEN, 1)
        
    def test_znorm_static_method(self):
        """Test _znorm_along_the_last_dim static method."""
        x = torch.randn(4, 270, 1000)
        normalized = MNet1000._znorm_along_the_last_dim(x)
        # Check mean is close to 0 and std is close to 1
        assert torch.abs(normalized.mean(dim=-1)).max() < 1e-5
        assert torch.abs(normalized.std(dim=-1) - 1.0).max() < 1e-5


class TestMNet1000Gradient:
    """Test gradient flow and backpropagation."""
    
    def test_gradient_flow(self):
        """Test that gradients flow through the model."""
        model = MNet1000(MNet_config)
        x = torch.randn(4, 270, 1000, requires_grad=True)
        output = model(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()
        
    def test_parameter_updates(self):
        """Test that parameters can be updated."""
        model = MNet1000(MNet_config)
        optimizer = torch.optim.Adam(model.parameters())
        x = torch.randn(4, 270, 1000)
        target = torch.randint(0, 2, (4,))
        
        # Store initial parameters
        initial_params = {name: param.clone() for name, param in model.named_parameters()}
        
        # Forward pass and update
        output = model(x)
        loss = nn.CrossEntropyLoss()(output, target)
        loss.backward()
        optimizer.step()
        
        # Check parameters were updated
        for name, param in model.named_parameters():
            assert not torch.equal(param, initial_params[name])


class TestMNet1000Device:
    """Test device compatibility."""
    
    def test_cpu_computation(self):
        """Test computation on CPU."""
        model = MNet1000(MNet_config)
        x = torch.randn(2, 270, 1000)
        output = model(x)
        assert output.device.type == 'cpu'
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_cuda_computation(self):
        """Test computation on CUDA."""
        model = MNet1000(MNet_config).cuda()
        x = torch.randn(2, 270, 1000).cuda()
        output = model(x)
        assert output.device.type == 'cuda'
        
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_multi_gpu_compatibility(self):
        """Test DataParallel compatibility."""
        if torch.cuda.device_count() > 1:
            model = nn.DataParallel(MNet1000(MNet_config))
            x = torch.randn(8, 270, 1000).cuda()
            output = model(x)
            assert output.shape == (8, 2)


class TestSwapLayer:
    """Test SwapLayer functionality."""
    
    def test_swap_layer_forward(self):
        """Test SwapLayer forward pass."""
        layer = SwapLayer()
        x = torch.randn(4, 10, 20)
        output = layer(x)
        assert output.shape == (4, 20, 10)
        assert torch.equal(output, x.transpose(1, 2))
        
    def test_swap_layer_gradient(self):
        """Test gradient flow through SwapLayer."""
        layer = SwapLayer()
        x = torch.randn(4, 10, 20, requires_grad=True)
        output = layer(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None


class TestReshapeLayer:
    """Test ReshapeLayer functionality."""
    
    def test_reshape_layer_forward(self):
        """Test ReshapeLayer forward pass."""
        layer = ReshapeLayer()
        x = torch.randn(4, 10, 20, 5)
        output = layer(x)
        assert output.shape == (4, 10 * 20 * 5)
        
    def test_reshape_layer_preserves_data(self):
        """Test that ReshapeLayer preserves data."""
        layer = ReshapeLayer()
        x = torch.randn(4, 10, 20, 5)
        output = layer(x)
        expected = x.reshape(4, -1)
        assert torch.equal(output, expected)


class TestMNet1000Memory:
    """Test memory efficiency."""
    
    def test_memory_efficiency(self):
        """Test model memory footprint."""
        model = MNet1000(MNet_config)
        total_params = sum(p.numel() for p in model.parameters())
        total_size_mb = total_params * 4 / (1024 * 1024)  # 4 bytes per float32
        assert total_size_mb < 100  # Model should be under 100MB
        
    def test_inference_memory(self):
        """Test memory usage during inference."""
        model = MNet1000(MNet_config)
        model.eval()
        x = torch.randn(1, 270, 1000)
        
        with torch.no_grad():
            output = model(x)
        assert output.shape == (1, 2)


class TestMNet1000Integration:
    """Test integration with other components."""
    
    def test_with_different_optimizers(self):
        """Test compatibility with different optimizers."""
        model = MNet1000(MNet_config)
        optimizers = [
            torch.optim.SGD(model.parameters(), lr=0.01),
            torch.optim.Adam(model.parameters()),
            torch.optim.AdamW(model.parameters()),
        ]
        
        x = torch.randn(4, 270, 1000)
        target = torch.randint(0, 2, (4,))
        
        for optimizer in optimizers:
            output = model(x)
            loss = nn.CrossEntropyLoss()(output, target)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            
    def test_with_different_loss_functions(self):
        """Test with different loss functions."""
        model = MNet1000(MNet_config)
        x = torch.randn(4, 270, 1000)
        output = model(x)
        
        # Test with various losses
        ce_loss = nn.CrossEntropyLoss()(output, torch.randint(0, 2, (4,)))
        mse_loss = nn.MSELoss()(output, torch.randn(4, 2))
        
        assert ce_loss.item() > 0
        assert mse_loss.item() > 0
        
    def test_dropout_training_eval_difference(self):
        """Test that dropout behaves differently in train/eval mode."""
        model = MNet1000(MNet_config)
        x = torch.randn(16, 270, 1000)
        
        # Get outputs in training mode
        model.train()
        outputs_train = [model(x) for _ in range(10)]
        
        # Get outputs in eval mode
        model.eval()
        with torch.no_grad():
            outputs_eval = [model(x) for _ in range(10)]
        
        # Training outputs should vary due to dropout
        train_variance = torch.stack(outputs_train).var(dim=0).mean()
        eval_variance = torch.stack(outputs_eval).var(dim=0).mean()
        
        assert train_variance > eval_variance


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_MNet_1000.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-05-04 16:54:55 (ywatanabe)"
#
# #!/usr/bin/env python
#
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchsummary import summary
# import scitex
#
# MNet_config = {
#     "classes": ["class1", "class2"],
#     "n_chs": 270,
#     "n_fc1": 1024,
#     "d_ratio1": 0.85,
#     "n_fc2": 256,
#     "d_ratio2": 0.85,
# }
#
#
# class MNet_1000(nn.Module):
#     def __init__(self, config):
#         super().__init__()
#
#         # basic
#         self.config = config
#         # fc
#         N_FC_IN = 15950
#
#
#         # conv
#         self.backborn = nn.Sequential(*[
#
#             nn.Conv2d(1, 40, kernel_size=(config["n_chs"], 4)),
#             nn.Mish(),
#
#             nn.Conv2d(40, 40, kernel_size=(1, 4)),
#             nn.BatchNorm2d(40),
#             nn.MaxPool2d((1, 5)),
#             nn.Mish(),
#
#             SwapLayer(),
#
#             nn.Conv2d(1, 50, kernel_size=(8, 12)),
#             nn.BatchNorm2d(50),
#             nn.MaxPool2d((3, 3)),
#             nn.Mish(),
#
#             nn.Conv2d(50, 50, kernel_size=(1, 5)),
#             nn.BatchNorm2d(50),
#             nn.MaxPool2d((1, 2)),
#             nn.Mish(),
#
#             ReshapeLayer(),
#             nn.Linear(N_FC_IN, config["n_fc1"]),
#             ])
#
#         # # conv
#         # self.conv1 = nn.Conv2d(1, 40, kernel_size=(config["n_chs"], 4))
#         # self.act1 = nn.Mish()
#
#         # self.conv2 = nn.Conv2d(40, 40, kernel_size=(1, 4))
#         # self.bn2 = nn.BatchNorm2d(40)
#         # self.pool2 = nn.MaxPool2d((1, 5))
#         # self.act2 = nn.Mish()
#
#         # self.swap = SwapLayer()
#
#         # self.conv3 = nn.Conv2d(1, 50, kernel_size=(8, 12))
#         # self.bn3 = nn.BatchNorm2d(50)
#         # self.pool3 = nn.MaxPool2d((3, 3))
#         # self.act3 = nn.Mish()
#
#         # self.conv4 = nn.Conv2d(50, 50, kernel_size=(1, 5))
#         # self.bn4 = nn.BatchNorm2d(50)
#         # self.pool4 = nn.MaxPool2d((1, 2))
#         # self.act4 = nn.Mish()
#
#
#         self.fc = nn.Sequential(
#             # nn.Linear(N_FC_IN, config["n_fc1"]),
#             nn.Mish(),
#             nn.Dropout(config["d_ratio1"]),
#             nn.Linear(config["n_fc1"], config["n_fc2"]),
#             nn.Mish(),
#             nn.Dropout(config["d_ratio2"]),
#             nn.Linear(config["n_fc2"], len(config["classes"])),
#         )
#
#     @staticmethod
#     def _reshape_input(x, n_chs):
#         """
#         (batch, channel, time_length) -> (batch, channel, time_length, new_axis)
#         """
#         if x.ndim == 3:
#             x = x.unsqueeze(-1)
#         if x.shape[2] == n_chs:
#             x = x.transpose(1, 2)
#         x = x.transpose(1, 3).transpose(2, 3)
#         return x
#
#     @staticmethod
#     def _znorm_along_the_last_dim(x):
#         return (x - x.mean(dim=-1, keepdims=True)) / x.std(dim=-1, keepdims=True)
#
#     def forward(self, x):
#         # # time-wise normalization
#         # x = self._znorm_along_the_last_dim(x)
#         # x = self._reshape_input(x, self.config["n_chs"])
#
#         # x = self.backborn(x)
#         x = self.forward_bb(x)
#
#         # x = x.reshape(len(x), -1)
#
#         x = self.fc(x)
#
#         return x
#
#     def forward_bb(self, x):
#         # time-wise normalization
#         x = self._znorm_along_the_last_dim(x)
#         x = self._reshape_input(x, self.config["n_chs"])
#         x = self.backborn(x)
#         return x
#
#
#
#
# class SwapLayer(nn.Module):
#     def __init__(
#         self,
#     ):
#         super().__init__()
#
#     def forward(self, x):
#         return x.transpose(1, 2)
#
# class ReshapeLayer(nn.Module):
#     def __init__(
#         self,
#     ):
#         super().__init__()
#
#     def forward(self, x):
#         return x.reshape(len(x), -1)
#
#
# if __name__ == "__main__":
#     ## Demo data
#     BS, N_CHS, SEQ_LEN = 16, 270, 1000
#     x = torch.rand(BS, N_CHS, SEQ_LEN).cuda()
#
#     ## Config for the model
#     model = MNet_1000(MNet_config).cuda()
#
#     y = model(x)
#     summary(model, x)
#     print(y.shape)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_MNet_1000.py
# --------------------------------------------------------------------------------
