#!/usr/bin/env python3
"""
Comprehensive test suite for ResNet1D neural network architecture.

This module tests the ResNet1D class and ResNetBasicBlock including:
- Basic instantiation with different configurations
- Forward pass functionality with various input shapes
- Residual connections and skip connections
- Multi-kernel convolutions (3, 5, 7)
- Gradient flow and vanishing gradient prevention
- Different network depths
- Channel expansion handling
- BatchNorm and activation functions
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, patch
import scitex


class TestResNetBasicBlock:
    """Test suite for ResNetBasicBlock - the fundamental building block of ResNet1D."""
    
    def test_basic_block_instantiation(self):
        """Test ResNetBasicBlock instantiation with various channel configurations."""
        configs = [(32, 64), (64, 64), (19, 76), (128, 32)]
        
        for in_chs, out_chs in configs:
            block = scitex.nn.ResNetBasicBlock(in_chs, out_chs)
            assert isinstance(block, nn.Module)
            assert block.in_chs == in_chs
            assert block.out_chs == out_chs
    
    def test_basic_block_layers_structure(self):
        """Test that ResNetBasicBlock has all required layers."""
        block = scitex.nn.ResNetBasicBlock(32, 64)
        
        # Check convolutional layers
        assert hasattr(block, 'conv7')
        assert hasattr(block, 'conv5')
        assert hasattr(block, 'conv3')
        assert hasattr(block, 'expansion_conv')
        
        # Check batch norm layers
        assert hasattr(block, 'bn7')
        assert hasattr(block, 'bn5')
        assert hasattr(block, 'bn3')
        assert hasattr(block, 'bn')
        
        # Check activation layers
        assert hasattr(block, 'activation7')
        assert hasattr(block, 'activation5')
        assert hasattr(block, 'activation3')
        assert hasattr(block, 'activation')
    
    def test_basic_block_forward_same_channels(self):
        """Test forward pass when input and output channels are the same."""
        batch_size, in_chs, seq_len = 16, 64, 1000
        block = scitex.nn.ResNetBasicBlock(in_chs, in_chs)
        
        x = torch.randn(batch_size, in_chs, seq_len)
        output = block(x)
        
        assert output.shape == (batch_size, in_chs, seq_len)
    
    def test_basic_block_forward_different_channels(self):
        """Test forward pass with channel expansion."""
        batch_size, in_chs, out_chs, seq_len = 16, 32, 128, 500
        block = scitex.nn.ResNetBasicBlock(in_chs, out_chs)
        
        x = torch.randn(batch_size, in_chs, seq_len)
        output = block(x)
        
        assert output.shape == (batch_size, out_chs, seq_len)
    
    def test_basic_block_conv_k_static_method(self):
        """Test the static conv_k method for creating convolution layers."""
        conv = scitex.nn.ResNetBasicBlock.conv_k(32, 64, k=3, s=1, p=1)
        
        assert isinstance(conv, nn.Conv1d)
        assert conv.in_channels == 32
        assert conv.out_channels == 64
        assert conv.kernel_size == (3,)
        assert conv.stride == (1,)
        assert conv.padding == (1,)
        assert conv.bias is None  # Should have no bias
    
    def test_basic_block_residual_connection(self):
        """Test that residual connection is properly applied."""
        block = scitex.nn.ResNetBasicBlock(64, 64)
        x = torch.randn(8, 64, 256, requires_grad=True)
        
        # Forward pass
        output = block(x)
        
        # The output should be different from input due to transformations
        assert not torch.allclose(output, x)
        
        # But gradient should flow through residual connection
        loss = output.sum()
        loss.backward()
        assert x.grad is not None
    
    def test_basic_block_expansion_conv_usage(self):
        """Test expansion convolution is used when channels differ."""
        block = scitex.nn.ResNetBasicBlock(32, 64)
        
        # Mock to track if expansion_conv is called
        original_expansion = block.expansion_conv
        block.expansion_conv = Mock(wraps=original_expansion)
        
        x = torch.randn(4, 32, 128)
        _ = block(x)
        
        # Expansion conv should be called
        block.expansion_conv.assert_called()
    
    def test_basic_block_kernel_sizes(self):
        """Test different kernel sizes in the block."""
        block = scitex.nn.ResNetBasicBlock(32, 64)
        
        # Check kernel sizes
        assert block.conv7.kernel_size == (7,)
        assert block.conv5.kernel_size == (5,)
        assert block.conv3.kernel_size == (3,)
        assert block.expansion_conv.kernel_size == (1,)
    
    def test_basic_block_padding_preservation(self):
        """Test that padding preserves sequence length."""
        seq_lengths = [100, 256, 512, 1000, 2048]
        block = scitex.nn.ResNetBasicBlock(32, 64)
        
        for seq_len in seq_lengths:
            x = torch.randn(2, 32, seq_len)
            output = block(x)
            assert output.shape[-1] == seq_len
    
    def test_basic_block_gradient_flow(self):
        """Test gradient flows properly through the block."""
        block = scitex.nn.ResNetBasicBlock(32, 64)
        x = torch.randn(4, 32, 128, requires_grad=True)
        
        output = block(x)
        loss = output.mean()
        loss.backward()
        
        # Check gradients exist and are not zero
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))
        
        # Check no gradient explosion
        assert not torch.isnan(x.grad).any()
        assert not torch.isinf(x.grad).any()


class TestResNet1D:
    """Test suite for ResNet1D - 1D ResNet for signal classification."""
    
    def test_resnet1d_instantiation_default(self):
        """Test ResNet1D instantiation with default parameters."""
        model = scitex.nn.ResNet1D()
        assert isinstance(model, nn.Module)
        assert hasattr(model, 'res_conv_blk_layers')
    
    def test_resnet1d_instantiation_custom(self):
        """Test ResNet1D instantiation with custom parameters."""
        configs = [
            (19, 10, 5),    # EEG: 19 channels, 10 classes, 5 blocks
            (32, 4, 3),     # 32 channels, 4 classes, 3 blocks
            (64, 2, 10),    # 64 channels, binary, 10 blocks
            (160, 5, 7),    # MEG: 160 channels, 5 classes, 7 blocks
        ]
        
        for n_chs, n_out, n_blks in configs:
            model = scitex.nn.ResNet1D(n_chs=n_chs, n_out=n_out, n_blks=n_blks)
            assert isinstance(model, nn.Module)
    
    def test_resnet1d_blocks_structure(self):
        """Test the structure of residual blocks in ResNet1D."""
        n_blks = 5
        n_chs = 32
        model = scitex.nn.ResNet1D(n_chs=n_chs, n_blks=n_blks)
        
        # Check sequential container
        assert isinstance(model.res_conv_blk_layers, nn.Sequential)
        assert len(model.res_conv_blk_layers) == n_blks
        
        # First block should expand channels
        first_block = model.res_conv_blk_layers[0]
        assert isinstance(first_block, scitex.nn.ResNetBasicBlock)
        assert first_block.in_chs == n_chs
        assert first_block.out_chs == n_chs * 4  # _N_FILTS_PER_CH = 4
        
        # Remaining blocks maintain channels
        for i in range(1, n_blks):
            block = model.res_conv_blk_layers[i]
            assert block.in_chs == n_chs * 4
            assert block.out_chs == n_chs * 4
    
    def test_resnet1d_forward_pass_basic(self):
        """Test basic forward pass through ResNet1D."""
        batch_size, n_chs, seq_len = 16, 32, 1000
        model = scitex.nn.ResNet1D(n_chs=n_chs, n_out=10)
        
        x = torch.randn(batch_size, n_chs, seq_len)
        output = model(x)
        
        # Output should have expanded channels
        expected_out_chs = n_chs * 4  # _N_FILTS_PER_CH = 4
        assert output.shape == (batch_size, expected_out_chs, seq_len)
    
    def test_resnet1d_forward_various_sequence_lengths(self):
        """Test ResNet1D with various sequence lengths."""
        model = scitex.nn.ResNet1D(n_chs=19, n_out=4)
        batch_size = 8
        seq_lengths = [128, 256, 512, 1024, 2048, 4096]
        
        for seq_len in seq_lengths:
            x = torch.randn(batch_size, 19, seq_len)
            output = model(x)
            assert output.shape == (batch_size, 76, seq_len)  # 19 * 4 = 76
    
    def test_resnet1d_forward_various_batch_sizes(self):
        """Test ResNet1D with various batch sizes."""
        model = scitex.nn.ResNet1D(n_chs=32, n_out=10)
        seq_len = 1000
        batch_sizes = [1, 4, 16, 32, 64, 128]
        
        for batch_size in batch_sizes:
            x = torch.randn(batch_size, 32, seq_len)
            output = model(x)
            assert output.shape == (batch_size, 128, seq_len)  # 32 * 4 = 128
    
    def test_resnet1d_different_depths(self):
        """Test ResNet1D with different network depths."""
        depths = [1, 3, 5, 10, 20, 50]
        
        for n_blks in depths:
            model = scitex.nn.ResNet1D(n_chs=16, n_out=10, n_blks=n_blks)
            x = torch.randn(2, 16, 256)
            output = model(x)
            assert output.shape == (2, 64, 256)  # 16 * 4 = 64
    
    def test_resnet1d_gradient_flow_shallow(self):
        """Test gradient flow in shallow ResNet1D."""
        model = scitex.nn.ResNet1D(n_chs=32, n_out=10, n_blks=3)
        x = torch.randn(4, 32, 512, requires_grad=True)
        
        output = model(x)
        loss = output.mean()
        loss.backward()
        
        assert x.grad is not None
        assert not torch.isnan(x.grad).any()
        assert not torch.isinf(x.grad).any()
    
    def test_resnet1d_gradient_flow_deep(self):
        """Test gradient flow in deep ResNet1D (vanishing gradient test)."""
        model = scitex.nn.ResNet1D(n_chs=32, n_out=10, n_blks=20)
        x = torch.randn(2, 32, 256, requires_grad=True)
        
        output = model(x)
        loss = output.mean()
        loss.backward()
        
        # Even in deep network, gradients should flow
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))
        assert not torch.isnan(x.grad).any()
    
    def test_resnet1d_device_compatibility_cpu(self):
        """Test ResNet1D on CPU."""
        model = scitex.nn.ResNet1D(n_chs=19, n_out=4)
        x = torch.randn(8, 19, 1000)
        
        output = model(x)
        assert output.device.type == 'cpu'
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_resnet1d_device_compatibility_gpu(self):
        """Test ResNet1D on GPU if available."""
        model = scitex.nn.ResNet1D(n_chs=19, n_out=4).cuda()
        x = torch.randn(8, 19, 1000).cuda()
        
        output = model(x)
        assert output.device.type == 'cuda'
    
    def test_resnet1d_parameter_count(self):
        """Test parameter count for different configurations."""
        configs = [
            (19, 10, 5),
            (32, 4, 10),
            (64, 2, 20),
        ]
        
        for n_chs, n_out, n_blks in configs:
            model = scitex.nn.ResNet1D(n_chs=n_chs, n_out=n_out, n_blks=n_blks)
            
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            # Should have reasonable parameter count
            assert total_params > 10000  # At least 10k parameters
            assert total_params < 100000000  # Less than 100M parameters
            assert trainable_params == total_params
    
    def test_resnet1d_eval_train_modes(self):
        """Test behavior in training vs evaluation modes."""
        model = scitex.nn.ResNet1D(n_chs=32, n_out=10)
        x = torch.randn(4, 32, 256)
        
        # Training mode
        model.train()
        assert model.training
        output_train = model(x)
        
        # Eval mode
        model.eval()
        assert not model.training
        output_eval = model(x)
        
        # Outputs should have same shape
        assert output_train.shape == output_eval.shape
    
    def test_resnet1d_multiple_forward_consistency(self):
        """Test consistency of multiple forward passes in eval mode."""
        model = scitex.nn.ResNet1D(n_chs=19, n_out=4)
        model.eval()
        
        x = torch.randn(8, 19, 512)
        
        # Multiple forward passes should give same result
        out1 = model(x)
        out2 = model(x)
        
        assert torch.allclose(out1, out2)
    
    def test_resnet1d_channels_per_filter_ratio(self):
        """Test the 4x channel expansion ratio."""
        n_chs_list = [8, 16, 19, 32, 64]
        
        for n_chs in n_chs_list:
            model = scitex.nn.ResNet1D(n_chs=n_chs)
            x = torch.randn(2, n_chs, 128)
            output = model(x)
            
            # Output channels should be 4x input channels
            assert output.shape[1] == n_chs * 4
    
    def test_resnet1d_with_single_channel(self):
        """Test ResNet1D with single channel input."""
        model = scitex.nn.ResNet1D(n_chs=1, n_out=2, n_blks=3)
        x = torch.randn(16, 1, 1000)
        
        output = model(x)
        assert output.shape == (16, 4, 1000)  # 1 * 4 = 4
    
    def test_resnet1d_with_many_channels(self):
        """Test ResNet1D with many input channels."""
        model = scitex.nn.ResNet1D(n_chs=256, n_out=10, n_blks=5)
        x = torch.randn(2, 256, 512)
        
        output = model(x)
        assert output.shape == (2, 1024, 512)  # 256 * 4 = 1024
    
    def test_resnet1d_output_features(self):
        """Test that output maintains spatial resolution."""
        model = scitex.nn.ResNet1D(n_chs=32, n_out=10)
        
        # Test that convolutions preserve spatial dimensions
        x = torch.randn(4, 32, 1000)
        output = model(x)
        
        # Spatial dimension should be preserved
        assert output.shape[-1] == x.shape[-1]
    
    def test_resnet1d_integration_with_classifier(self):
        """Test ResNet1D can be integrated with a classifier head."""
        class ResNet1DClassifier(nn.Module):
            def __init__(self, n_chs, n_out):
                super().__init__()
                self.feature_extractor = scitex.nn.ResNet1D(n_chs, n_out)
                self.classifier = nn.Linear(n_chs * 4, n_out)
            
            def forward(self, x):
                features = self.feature_extractor(x)
                pooled = features.mean(dim=-1)  # Global average pooling
                return self.classifier(pooled)
        
        model = ResNet1DClassifier(n_chs=19, n_out=4)
        x = torch.randn(8, 19, 1000)
        output = model(x)
        
        assert output.shape == (8, 4)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_ResNet1D.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2023-05-15 16:46:54 (ywatanabe)"
#
# import torch
# import torch.nn as nn
# from torchsummary import summary
#
# class ResNet1D(nn.Module):
#     """
#     A representative convolutional neural network for signal classification tasks.
#     """
#
#     def __init__(
#         self,
#             n_chs=19,
#             n_out=10,
#             n_blks=5
#     ):
#         super().__init__()
#
#         # Parameters
#         N_CHS = n_chs
#         _N_FILTS_PER_CH = 4
#         N_FILTS = N_CHS * _N_FILTS_PER_CH
#         N_BLKS = n_blks
#
#         # Convolutional layers
#         self.res_conv_blk_layers = nn.Sequential(
#             ResNetBasicBlock(N_CHS, N_FILTS),
#             *[ResNetBasicBlock(N_FILTS, N_FILTS) for _ in range(N_BLKS - 1)],
#         )
#
#         # ## FC layer
#         # self.fc = nn.Sequential(
#         #     nn.Linear(N_FILTS, 64),
#         #     nn.ReLU(),
#         #     nn.Dropout(p=0.5),
#         #     nn.Linear(64, 32),
#         #     nn.ReLU(),
#         #     nn.Dropout(p=0.5),
#         #     nn.Linear(32, n_out),
#         # )
#
#     def forward(self, x):
#         x = self.res_conv_blk_layers(x)
#         # x = x.mean(axis=-1)
#         # x = self.fc(x)
#         return x
#
#
# class ResNetBasicBlock(nn.Module):
#     """The basic block of the ResNet1D model"""
#
#     def __init__(self, in_chs, out_chs):
#         super(ResNetBasicBlock, self).__init__()
#         self.in_chs = in_chs
#         self.out_chs = out_chs
#
#         self.conv7 = self.conv_k(in_chs, out_chs, k=7, p=3)
#         self.bn7 = nn.BatchNorm1d(out_chs)
#         self.activation7 = nn.ReLU()
#
#         self.conv5 = self.conv_k(out_chs, out_chs, k=5, p=2)
#         self.bn5 = nn.BatchNorm1d(out_chs)
#         self.activation5 = nn.ReLU()
#
#         self.conv3 = self.conv_k(out_chs, out_chs, k=3, p=1)
#         self.bn3 = nn.BatchNorm1d(out_chs)
#         self.activation3 = nn.ReLU()
#
#         self.expansion_conv = self.conv_k(in_chs, out_chs, k=1, p=0)
#
#         self.bn = nn.BatchNorm1d(out_chs)
#         self.activation = nn.ReLU()
#
#     @staticmethod
#     def conv_k(in_chs, out_chs, k=1, s=1, p=1):
#         """Build size k kernel's convolution layer with padding"""
#         return nn.Conv1d(
#             in_chs, out_chs, kernel_size=k, stride=s, padding=p, bias=False
#         )
#
#     def forward(self, x):
#         residual = x
#
#         x = self.conv7(x)
#         x = self.bn7(x)
#         x = self.activation7(x)
#
#         x = self.conv5(x)
#         x = self.bn5(x)
#         x = self.activation5(x)
#
#         x = self.conv3(x)
#         x = self.bn3(x)
#         x = self.activation3(x)
#
#         if self.in_chs != self.out_chs:
#             residual = self.expansion_conv(residual)
#         residual = self.bn(residual)
#
#         x = x + residual
#         x = self.activation(x)
#
#         return x
#
# if __name__ == "__main__":
#     import sys
#
#     sys.path.append("./DEAP/")
#     import utils
#
#     # Demo data
#     bs, n_chs, seq_len = 16, 32, 8064
#     Xb = torch.rand(bs, n_chs, seq_len)
#
#     model = ResNet1D(
#             n_chs=n_chs,
#             n_out=4,
#     )  # utils.load_yaml("./config/global.yaml")["EMOTIONS"]
#     y = model(Xb)  # 16,4
#     summary(model, Xb)

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/nn/_ResNet1D.py
# --------------------------------------------------------------------------------
